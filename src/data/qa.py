"""STORY-104 media QA: detect channel-day anomalies (detect-only in Step 1).

Why this exists
---------------
ETL (103) builds a complete date×channel grid. QA asks whether *media ratios*
on active days still look believable vs that channel's recent history.
Bad impressions/clicks poison Meridian; spend and baseline_sales stay immutable.

Step 1 ships ``detect_anomalies`` only — no repair, no parquet overwrite, no CLI gate.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# --- Constants (locked v1 thresholds) ---

WINDOW_DAYS = 14
MIN_IMPRESSIONS_CTR = 1000
CTR_COLLAPSE_FACTOR = 0.2  # clicks < factor × median_CTR × impressions
SPEND_NEAR_PCT = 0.20  # |spend − median| / median ≤ 20%
IPS_LO = 0.5  # impressions/spend vs median IPS
IPS_HI = 2.0

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PANEL_PATH = REPO_ROOT / "data" / "processed" / "clean_spend.parquet"

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
