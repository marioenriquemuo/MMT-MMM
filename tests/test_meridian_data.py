"""Fast unit tests for STORY-201 Meridian adapter (no MCMC)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.models.meridian_data import (
    CHANNEL_ORDER,
    load_clean_panel,
    load_meridian_input,
    panel_to_national_wide,
    wide_to_input_data,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PARQUET = REPO_ROOT / "data" / "processed" / "clean_spend.parquet"


def _mini_panel() -> pd.DataFrame:
    rows = []
    for i, day in enumerate(pd.date_range("2023-01-02", periods=14, freq="D")):
        kpi = 1000 + i
        for ch in CHANNEL_ORDER:
            rows.append(
                {
                    "date": day,
                    "channel": ch,
                    "spend": 10.0 + i,
                    "impressions": 100 + i,
                    "clicks": 1 + i,
                    "baseline_sales": kpi,
                }
            )
    return pd.DataFrame(rows)


def test_panel_to_national_wide_daily_kpi_not_summed_across_channels():
    wide = panel_to_national_wide(_mini_panel(), freq="D")
    assert len(wide) == 14
    # KPI must match one channel-row per day, not 4×.
    assert wide["kpi"].iloc[0] == 1000
    assert set(wide.columns) >= {
        "time",
        "kpi",
        "revenue_per_kpi",
        "meta_impression",
        "meta_spend",
        "google_impression",
        "google_spend",
    }


def test_panel_to_national_wide_weekly_aggregates():
    wide = panel_to_national_wide(_mini_panel(), freq="W")
    assert len(wide) >= 2
    assert wide["kpi"].iloc[0] > 1000  # sum of daily KPIs in the week
    assert (wide["revenue_per_kpi"] == 1.0).all()


def test_wide_to_input_data_shapes():
    wide = panel_to_national_wide(_mini_panel(), freq="W")
    data = wide_to_input_data(wide)
    n_t = len(wide)
    assert data.kpi.shape == (1, n_t)
    assert data.media.shape == (1, n_t, 4)
    assert data.media_spend.shape == (1, n_t, 4)
    assert data.kpi_type == "non_revenue"
    assert list(data.media.coords["media_channel"].values) == list(CHANNEL_ORDER)


def test_load_clean_panel_missing_columns():
    bad = Path("/tmp/bad_clean_spend.parquet")
    pd.DataFrame({"date": ["2023-01-01"], "spend": [1.0]}).to_parquet(bad)
    with pytest.raises(ValueError, match="missing columns"):
        load_clean_panel(bad)


@pytest.mark.skipif(not PARQUET.is_file(), reason="clean_spend.parquet not present")
def test_load_meridian_input_from_committed_parquet():
    data = load_meridian_input(PARQUET, freq="W")
    assert data.kpi.shape[0] == 1
    assert data.kpi.shape[1] >= 50  # ~104 weeks for 728 days
    assert data.media.shape[-1] == 4
