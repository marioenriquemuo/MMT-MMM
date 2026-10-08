"""STORY-103 ETL: raw channel-day spend panel → validated clean Parquet.

Why this exists
---------------
Ad-platform exports often *omit* idle channel-days (a pause looks like "no row").
Bayesian MMM needs a regular **date × channel** grid. After we align that grid:

- Missing **spend / impressions / clicks** → **0** (real zero activity / not in export).
- Missing **baseline_sales** (site KPI) → **forward-fill** (measurement continuity).
  We never invent fake ad spend when a partner was off.

Pipeline: load → align → impute → Pandera validate → Parquet (``pyarrow``).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from src.data.generator import CHANNELS, COLUMNS

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_PATH = REPO_ROOT / "data" / "raw" / "synthetic_ad_spend.csv"
DEFAULT_OUT_PATH = REPO_ROOT / "data" / "processed" / "clean_spend.parquet"

MEDIA_COLUMNS = ("spend", "impressions", "clicks")
KPI_COLUMN = "baseline_sales"

# --- Schema (Pandera) ---
# Teach-note: this is a DataFrame contract — types, non-negativity, allowed channels.
# We validate the *clean* panel (after impute), not the dirty export holes.

SpendPanelSchema = pa.DataFrameSchema(
    {
        "date": pa.Column(pa.DateTime, nullable=False),
        "channel": pa.Column(
            str,
            checks=pa.Check.isin(list(CHANNELS)),
            nullable=False,
        ),
        "spend": pa.Column(float, checks=pa.Check.ge(0), nullable=False),
        "impressions": pa.Column(int, checks=pa.Check.ge(0), nullable=False),
        "clicks": pa.Column(int, checks=pa.Check.ge(0), nullable=False),
        "baseline_sales": pa.Column(int, checks=pa.Check.ge(0), nullable=False),
    },
    strict=True,
    coerce=True,
)


# --- Load ---


def load_raw(path: str | Path) -> pd.DataFrame:
    """Read a channel-day CSV and normalize dtypes (no fill yet).

    Returns columns in ``COLUMNS`` order with ``date`` as datetime64.
    """
    path = Path(path)
    df = pd.read_csv(path)
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"raw CSV missing columns: {sorted(missing)}")
    df = df.loc[:, list(COLUMNS)].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["channel"] = df["channel"].astype(str)
    return df


# --- Align ---


def align_date_channel_grid(
    df: pd.DataFrame,
    channels: tuple[str, ...] = CHANNELS,
) -> pd.DataFrame:
    """Expand to every calendar day × every modeled channel.

    Gaps become explicit NaN rows so imputation has something to fill.
    Date span is ``[min(date), max(date)]`` inclusive (daily frequency).
    """
    start = df["date"].min()
    end = df["date"].max()
    all_dates = pd.date_range(start, end, freq="D")
    grid = pd.MultiIndex.from_product(
        [all_dates, list(channels)],
        names=["date", "channel"],
    )
    keyed = df.set_index(["date", "channel"]).sort_index()
    # Drop duplicate keys if any — keep last (export quirk); rare on clean synthetic.
    keyed = keyed[~keyed.index.duplicated(keep="last")]
    aligned = keyed.reindex(grid).reset_index()
    return aligned.loc[:, list(COLUMNS)]


# --- Impute ---


def impute_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Apply locked STORY-103 fill rules on an aligned panel.

    * Media (``spend``, ``impressions``, ``clicks``): NaN → 0
      (= pause / absent from partner export that day).
    * ``baseline_sales``: build a site-wide daily series, forward-fill, broadcast
      back to every channel row for that date.
    """
    out = df.copy()
    for col in MEDIA_COLUMNS:
        out[col] = out[col].fillna(0)

    # Site-wide KPI per date (ignore NaNs from missing channel-days), then ffill.
    daily_kpi = out.groupby("date", sort=True)[KPI_COLUMN].max()
    daily_kpi = daily_kpi.ffill()
    out[KPI_COLUMN] = out["date"].map(daily_kpi)

    out["spend"] = out["spend"].astype(float)
    out["impressions"] = out["impressions"].astype(int)
    out["clicks"] = out["clicks"].astype(int)
    out[KPI_COLUMN] = out[KPI_COLUMN].astype(int)
    return out


# --- Orchestrate ---


def run_etl(
    raw_path: str | Path = DEFAULT_RAW_PATH,
    out_path: str | Path = DEFAULT_OUT_PATH,
) -> pd.DataFrame:
    """Load → align → impute → validate → write Parquet; return the clean frame."""
    raw_path = Path(raw_path)
    out_path = Path(out_path)

    df = load_raw(raw_path)
    df = align_date_channel_grid(df)
    df = impute_panel(df)
    df = SpendPanelSchema.validate(df)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, engine="pyarrow", index=False)
    return df


def main() -> None:
    """CLI entry: ``python -m src.data.etl``."""
    df = run_etl()
    print(
        f"Wrote {DEFAULT_OUT_PATH} "
        f"({len(df)} rows, {df['date'].nunique()} days × {df['channel'].nunique()} channels)"
    )


if __name__ == "__main__":
    main()
