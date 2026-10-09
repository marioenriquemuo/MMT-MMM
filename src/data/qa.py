"""STORY-104 media QA: detect + repair channel-day anomalies (pre-Meridian gate).

Why this exists
---------------
ETL (103) builds a complete date×channel grid. QA asks whether *media ratios*
on active days still look believable vs that channel's recent history.
Bad impressions/clicks poison Meridian; spend and baseline_sales stay immutable.

Pipeline: load → repair → hard-fail if unrepaired → Pandera validate → overwrite
``clean_spend.parquet`` + optional ``qa_repair_log.csv``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.data.etl import SpendPanelSchema

# --- Constants (locked v1 thresholds) ---

WINDOW_DAYS = 14
MIN_ACTIVITY_DAYS = 7  # required in-window activity days to repair
MIN_IMPRESSIONS_CTR = 1000
CTR_COLLAPSE_FACTOR = 0.2  # clicks < factor × median_CTR × impressions
SPEND_NEAR_PCT = 0.20  # |spend − median| / median ≤ 20%
IPS_LO = 0.5  # impressions/spend vs median IPS
IPS_HI = 2.0

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PANEL_PATH = REPO_ROOT / "data" / "processed" / "clean_spend.parquet"
DEFAULT_LOG_PATH = REPO_ROOT / "data" / "processed" / "qa_repair_log.csv"

ANOMALY_COLUMNS = (
    "date",
    "channel",
    "rule",
    "spend",
    "impressions",
    "clicks",
    "median_ctr",
    "ctr_floor_clicks",
    "ips",
    "median_ips",
    "median_spend",
)

LOG_COLUMNS = (
    "date",
    "channel",
    "rule",
    "old_impressions",
    "new_impressions",
    "old_clicks",
    "new_clicks",
)


# --- Load ---


def load_panel(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Load a channel-day panel from a DataFrame, Parquet path, or CSV path."""
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        path = Path(source)
        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["channel"] = df["channel"].astype(str)
    return df.sort_values(["channel", "date"]).reset_index(drop=True)


# --- History helper ---


def _prior_activity(ch: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Prior calendar days in ``[as_of − 14d, as_of)`` with ``spend > 0``."""
    start = as_of - pd.Timedelta(days=WINDOW_DAYS)
    mask = (ch["date"] >= start) & (ch["date"] < as_of) & (ch["spend"] > 0)
    return ch.loc[mask]


def _row_index(panel: pd.DataFrame, date: pd.Timestamp, channel: str) -> int:
    hit = panel.index[(panel["date"] == date) & (panel["channel"] == channel)]
    if len(hit) != 1:
        raise KeyError(f"expected one row for {channel!r} on {date.date()}, got {len(hit)}")
    return int(hit[0])


# --- Detect ---


def detect_anomalies(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Flag CTR-collapse and impression-vs-spend (IPS) anomalies per channel-day.

    Returns a frame with ``ANOMALY_COLUMNS`` (one row per fired rule). Empty if clean.
    Does not mutate the panel.
    """
    df = load_panel(source)
    rows: list[dict] = []

    for channel, ch in df.groupby("channel", sort=False):
        ch = ch.sort_values("date")
        for _, row in ch.iterrows():
            hist = _prior_activity(ch, row["date"])
            if hist.empty:
                continue

            spend = float(row["spend"])
            impressions = int(row["impressions"])
            clicks = int(row["clicks"])
            base = {
                "date": row["date"],
                "channel": channel,
                "spend": spend,
                "impressions": impressions,
                "clicks": clicks,
                "median_ctr": float("nan"),
                "ctr_floor_clicks": float("nan"),
                "ips": float("nan"),
                "median_ips": float("nan"),
                "median_spend": float("nan"),
            }

            # --- CTR collapse ---
            with_imps = hist.loc[hist["impressions"] > 0]
            if (
                spend > 0
                and impressions >= MIN_IMPRESSIONS_CTR
                and not with_imps.empty
            ):
                median_ctr = float((with_imps["clicks"] / with_imps["impressions"]).median())
                if median_ctr > 0:
                    floor = CTR_COLLAPSE_FACTOR * median_ctr * impressions
                    if clicks < floor:
                        rows.append(
                            {
                                **base,
                                "rule": "ctr_collapse",
                                "median_ctr": median_ctr,
                                "ctr_floor_clicks": floor,
                            }
                        )

            # --- Impression vs spend (IPS) ---
            if spend > 0:
                median_spend = float(hist["spend"].median())
                median_ips = float((hist["impressions"] / hist["spend"]).median())
                if median_spend > 0 and median_ips > 0:
                    near = abs(spend - median_spend) / median_spend <= SPEND_NEAR_PCT
                    ips = impressions / spend
                    out_of_band = ips < IPS_LO * median_ips or ips > IPS_HI * median_ips
                    if near and out_of_band:
                        rows.append(
                            {
                                **base,
                                "rule": "ips_outlier",
                                "ips": ips,
                                "median_ips": median_ips,
                                "median_spend": median_spend,
                            }
                        )

    if not rows:
        return pd.DataFrame(columns=list(ANOMALY_COLUMNS))
    out = pd.DataFrame(rows)
    out["date"] = pd.to_datetime(out["date"])
    return out.loc[:, list(ANOMALY_COLUMNS)].reset_index(drop=True)


# --- Repair ---


def repair_panel(
    source: str | Path | pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Detect anomalies, repair impressions then clicks when history is enough.

    Returns ``(panel, repair_log, unrepaired)``.

    - Never mutates ``spend`` or ``baseline_sales``.
    - ``ips_outlier`` first: ``impressions = round(median_IPS * spend)`` if
      ≥ ``MIN_ACTIVITY_DAYS`` prior activity days; else unrepaired.
    - Then re-check CTR on the updated panel: ``clicks = round(median_CTR *
      impressions)`` with the same history gate.
    - Does not write files or set exit codes (Step 3).
    """
    panel = load_panel(source)
    log_rows: list[dict] = []
    unrepaired_rows: list[dict] = []

    anomalies = detect_anomalies(panel)

    # --- IPS first ---
    for _, anom in anomalies.loc[anomalies["rule"] == "ips_outlier"].iterrows():
        ch = panel.loc[panel["channel"] == anom["channel"]]
        hist = _prior_activity(ch, anom["date"])
        if len(hist) < MIN_ACTIVITY_DAYS:
            unrepaired_rows.append(anom.to_dict())
            continue
        idx = _row_index(panel, anom["date"], anom["channel"])
        old_imps = int(panel.at[idx, "impressions"])
        old_clicks = int(panel.at[idx, "clicks"])
        new_imps = int(round(float(anom["median_ips"]) * float(anom["spend"])))
        panel.at[idx, "impressions"] = new_imps
        log_rows.append(
            {
                "date": anom["date"],
                "channel": anom["channel"],
                "rule": "ips_outlier",
                "old_impressions": old_imps,
                "new_impressions": new_imps,
                "old_clicks": old_clicks,
                "new_clicks": old_clicks,
            }
        )

    # --- CTR after IPS (re-detect on repaired panel) ---
    ctr_flags = detect_anomalies(panel)
    ctr_flags = ctr_flags.loc[ctr_flags["rule"] == "ctr_collapse"]
    for _, anom in ctr_flags.iterrows():
        ch = panel.loc[panel["channel"] == anom["channel"]]
        hist = _prior_activity(ch, anom["date"])
        if len(hist) < MIN_ACTIVITY_DAYS:
            unrepaired_rows.append(anom.to_dict())
            continue
        idx = _row_index(panel, anom["date"], anom["channel"])
        old_imps = int(panel.at[idx, "impressions"])
        old_clicks = int(panel.at[idx, "clicks"])
        new_clicks = int(round(float(anom["median_ctr"]) * old_imps))
        panel.at[idx, "clicks"] = new_clicks
        log_rows.append(
            {
                "date": anom["date"],
                "channel": anom["channel"],
                "rule": "ctr_collapse",
                "old_impressions": old_imps,
                "new_impressions": old_imps,
                "old_clicks": old_clicks,
                "new_clicks": new_clicks,
            }
        )

    if log_rows:
        log_df = pd.DataFrame(log_rows)
        log_df["date"] = pd.to_datetime(log_df["date"])
        log_df = log_df.loc[:, list(LOG_COLUMNS)].reset_index(drop=True)
    else:
        log_df = pd.DataFrame(columns=list(LOG_COLUMNS))

    if unrepaired_rows:
        unrepaired = pd.DataFrame(unrepaired_rows)
        unrepaired["date"] = pd.to_datetime(unrepaired["date"])
        unrepaired = unrepaired.loc[:, list(ANOMALY_COLUMNS)].reset_index(drop=True)
    else:
        unrepaired = pd.DataFrame(columns=list(ANOMALY_COLUMNS))

    return panel, log_df, unrepaired


def write_repair_log(log_df: pd.DataFrame, path: str | Path | None = None) -> Path | None:
    """Write repair audit CSV. Skips write (returns None) when ``log_df`` is empty."""
    if log_df is None or len(log_df) == 0:
        return None
    out_path = Path(path) if path is not None else DEFAULT_LOG_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frame = log_df.loc[:, list(LOG_COLUMNS)].copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
    frame.to_csv(out_path, index=False)
    return out_path


# --- Orchestrate (Step 3) ---


class UnrepairedAnomaliesError(RuntimeError):
    """Raised when anomalies remain after repair; training parquet must not be overwritten."""

    def __init__(self, unrepaired: pd.DataFrame) -> None:
        self.unrepaired = unrepaired
        n = len(unrepaired)
        super().__init__(
            f"{n} unrepaired anomal{'y' if n == 1 else 'ies'}; "
            "refusing to overwrite training parquet"
        )


def run_qa(
    in_path: str | Path = DEFAULT_PANEL_PATH,
    out_path: str | Path = DEFAULT_PANEL_PATH,
    log_path: str | Path = DEFAULT_LOG_PATH,
) -> pd.DataFrame:
    """Load → repair → validate → overwrite parquet (C1) + repair log.

    On unrepaired anomalies: raises ``UnrepairedAnomaliesError`` and does **not**
    write ``out_path`` (training panel stays untouched).
    """
    in_path = Path(in_path)
    out_path = Path(out_path)
    log_path = Path(log_path)

    panel, log_df, unrepaired = repair_panel(in_path)
    if len(unrepaired) > 0:
        raise UnrepairedAnomaliesError(unrepaired)

    # Match ETL grain order (date × channel) before validate/write.
    panel = panel.sort_values(["date", "channel"]).reset_index(drop=True)
    panel = SpendPanelSchema.validate(panel)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(out_path, engine="pyarrow", index=False)
    write_repair_log(log_df, log_path)
    return panel


def main(
    in_path: str | Path = DEFAULT_PANEL_PATH,
    out_path: str | Path = DEFAULT_PANEL_PATH,
    log_path: str | Path = DEFAULT_LOG_PATH,
) -> int:
    """CLI entry: exit 0 on success; exit 1 when unrepaired anomalies remain."""
    try:
        panel = run_qa(in_path=in_path, out_path=out_path, log_path=log_path)
    except UnrepairedAnomaliesError as exc:
        print(exc, file=sys.stderr)
        print(exc.unrepaired.to_string(index=False), file=sys.stderr)
        return 1

    print(
        f"QA ok → wrote {out_path} "
        f"({len(panel)} rows, {panel['date'].nunique()} days × "
        f"{panel['channel'].nunique()} channels)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
