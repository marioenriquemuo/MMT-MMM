"""STORY-201: map QA'd ``clean_spend.parquet`` → Meridian national ``InputData``.

Long channel-day panel → wide national time series. KPI is site-wide
``baseline_sales`` (groupby date first — never sum across channels). Media
exposure uses impressions; spend is the ROI denominator. ``revenue_per_kpi``
is fixed at 1.0 so incremental outcome equals incremental units (iROAS ≈ units
per dollar).

Weekly aggregation is the default grain for Meridian spikes (faster MCMC;
closer to common MMM practice). Pass ``freq="D"`` to keep daily periods.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from meridian.data import data_frame_input_data_builder as data_builder
from meridian.data.input_data import InputData

DEFAULT_PARQUET = (
    Path(__file__).resolve().parents[2] / "data" / "processed" / "clean_spend.parquet"
)

CHANNEL_ORDER = ("meta", "google", "tiktok", "tv")


def load_clean_panel(path: Path | str = DEFAULT_PARQUET) -> pd.DataFrame:
    """Load post-QA parquet; require expected columns."""
    df = pd.read_parquet(path)
    need = {"date", "channel", "spend", "impressions", "clicks", "baseline_sales"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"clean panel missing columns: {sorted(missing)}")
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    return out


def panel_to_national_wide(
    panel: pd.DataFrame,
    *,
    freq: str = "W",
    channel_order: tuple[str, ...] = CHANNEL_ORDER,
) -> pd.DataFrame:
    """Pivot long channel-day panel to Meridian-friendly wide national frame.

    Columns: ``time``, ``kpi``, ``revenue_per_kpi``, plus
    ``{channel}_impression`` / ``{channel}_spend`` for each channel.

    ``freq``: ``"W"`` (week ending Sunday) or ``"D"`` (daily).
    """
    if freq not in {"W", "D"}:
        raise ValueError("freq must be 'W' or 'D'")

    channels = [c for c in channel_order if c in set(panel["channel"].unique())]
    extra = sorted(set(panel["channel"].unique()) - set(channels))
    channels = channels + extra
    if not channels:
        raise ValueError("panel has no channels")

    # Site-wide daily KPI (repeated on each channel row).
    daily_kpi = (
        panel.groupby("date", as_index=False)["baseline_sales"]
        .first()
        .rename(columns={"baseline_sales": "kpi"})
    )
    # Build one spend / impressions series per channel (long → wide).
    frames = [daily_kpi.set_index("date")]
    for ch in channels:
        sub = panel.loc[panel["channel"] == ch, ["date", "spend", "impressions"]].copy()
        sub = sub.set_index("date").sort_index()
        sub = sub.rename(
            columns={"spend": f"{ch}_spend", "impressions": f"{ch}_impression"}
        )
        frames.append(sub[[f"{ch}_spend", f"{ch}_impression"]])
    daily = pd.concat(frames, axis=1).sort_index()
    daily["revenue_per_kpi"] = 1.0
    daily = daily.fillna(0)

    if freq == "D":
        wide = daily.reset_index().rename(columns={"date": "time"})
    else:
        agg = {"kpi": "sum", "revenue_per_kpi": "mean"}
        for ch in channels:
            agg[f"{ch}_spend"] = "sum"
            agg[f"{ch}_impression"] = "sum"
        wide = daily.resample("W-SUN").agg(agg).dropna(subset=["kpi"]).reset_index()
        wide = wide.rename(columns={"date": "time"})

    wide["time"] = pd.to_datetime(wide["time"]).dt.strftime("%Y-%m-%d")
    cols = ["time", "kpi", "revenue_per_kpi"]
    for ch in channels:
        cols.extend([f"{ch}_impression", f"{ch}_spend"])
    return wide[cols].reset_index(drop=True)


def wide_to_input_data(wide: pd.DataFrame) -> InputData:
    """Build Meridian ``InputData`` from a national wide DataFrame."""
    channels = []
    for col in wide.columns:
        if col.endswith("_impression"):
            channels.append(col[: -len("_impression")])
    if not channels:
        raise ValueError("wide frame has no *_impression media columns")

    builder = data_builder.DataFrameInputDataBuilder(
        kpi_type="non_revenue",
        default_kpi_column="kpi",
        default_revenue_per_kpi_column="revenue_per_kpi",
        default_time_column="time",
    )
    builder.currency_code = "USD"
    builder = builder.with_kpi(wide).with_revenue_per_kpi(wide)
    builder = builder.with_media(
        wide,
        media_cols=[f"{ch}_impression" for ch in channels],
        media_spend_cols=[f"{ch}_spend" for ch in channels],
        media_channels=channels,
    )
    return builder.build()


def load_meridian_input(
    path: Path | str = DEFAULT_PARQUET,
    *,
    freq: str = "W",
) -> InputData:
    """Load parquet → national Meridian ``InputData`` (default weekly)."""
    panel = load_clean_panel(path)
    wide = panel_to_national_wide(panel, freq=freq)
    return wide_to_input_data(wide)
