"""Tests for STORY-103 ETL (schema, alignment, imputation, parquet)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.errors
import pytest

from src.data.etl import (
    DEFAULT_OUT_PATH,
    DEFAULT_RAW_PATH,
    SpendPanelSchema,
    align_date_channel_grid,
    impute_panel,
    load_raw,
    run_etl,
)
from src.data.generator import CHANNELS, N_DAYS

REPO_ROOT = Path(__file__).resolve().parents[1]
DIRTY_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "dirty_ad_spend.csv"


# --- Schema ---


def _valid_mini() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2023-01-02", "2023-01-02"]),
            "channel": ["meta", "google"],
            "spend": [1.0, 2.0],
            "impressions": [10, 20],
            "clicks": [1, 2],
            "baseline_sales": [100, 100],
        }
    )


def test_schema_accepts_valid_frame():
    out = SpendPanelSchema.validate(_valid_mini())
    assert len(out) == 2


def test_schema_rejects_negative_spend():
    bad = _valid_mini()
    bad.loc[0, "spend"] = -1.0
    with pytest.raises(pandera.errors.SchemaError):
        SpendPanelSchema.validate(bad)


def test_schema_rejects_unknown_channel():
    bad = _valid_mini()
    bad.loc[0, "channel"] = "radio"
    with pytest.raises(pandera.errors.SchemaError):
        SpendPanelSchema.validate(bad)


# --- Load + align ---


def test_load_raw_synthetic_shape():
    df = load_raw(DEFAULT_RAW_PATH)
    assert len(df) == N_DAYS * len(CHANNELS)
    assert set(df["channel"].unique()) == set(CHANNELS)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_align_inserts_missing_channel_days():
    dirty = load_raw(DIRTY_FIXTURE)
    # google omitted on 2023-01-03 and 2023-01-04 in the fixture
    assert not (
        (dirty["date"] == "2023-01-03") & (dirty["channel"] == "google")
    ).any()

    aligned = align_date_channel_grid(dirty)
    assert len(aligned) == 6 * len(CHANNELS)  # Jan 2–7 inclusive
    google_gap = aligned[
        (aligned["date"] == "2023-01-03") & (aligned["channel"] == "google")
    ]
    assert len(google_gap) == 1
    assert pd.isna(google_gap["spend"].iloc[0])


# --- Impute ---


def test_impute_zero_fills_media_and_ffills_kpi():
    dirty = load_raw(DIRTY_FIXTURE)
    clean = impute_panel(align_date_channel_grid(dirty))

    for day in ("2023-01-03", "2023-01-04"):
        row = clean[(clean["date"] == day) & (clean["channel"] == "google")].iloc[0]
        assert row["spend"] == 0.0
        assert row["impressions"] == 0
        assert row["clicks"] == 0

    # Jan 6 had blank baseline_sales in the fixture → ffill from Jan 5 (530)
    jan6 = clean[clean["date"] == "2023-01-06"]
    assert set(jan6["baseline_sales"].unique()) == {530}
    # Google gap days still get the site KPI for that calendar day
    g3 = clean[(clean["date"] == "2023-01-03") & (clean["channel"] == "google")].iloc[0]
    assert g3["baseline_sales"] == 510


# --- run_etl / parquet ---


def test_run_etl_synthetic_happy_path(tmp_path: Path):
    out = tmp_path / "clean_spend.parquet"
    df = run_etl(DEFAULT_RAW_PATH, out)
    assert out.is_file()
    assert len(df) == N_DAYS * len(CHANNELS)
    assert int(df.isna().sum().sum()) == 0
    roundtrip = pd.read_parquet(out)
    assert len(roundtrip) == len(df)
    SpendPanelSchema.validate(roundtrip)


def test_run_etl_dirty_fixture(tmp_path: Path):
    out = tmp_path / "dirty_clean.parquet"
    df = run_etl(DIRTY_FIXTURE, out)
    assert len(df) == 6 * len(CHANNELS)
    google_pause = df[
        df["date"].isin(pd.to_datetime(["2023-01-03", "2023-01-04"]))
        & (df["channel"] == "google")
    ]
    assert (google_pause["spend"] == 0).all()
    assert (df.loc[df["date"] == "2023-01-06", "baseline_sales"] == 530).all()


def test_committed_clean_parquet_matches_etl_if_present(tmp_path: Path):
    """If we commit the processed artifact, it must match a fresh ETL run."""
    if not DEFAULT_OUT_PATH.is_file():
        pytest.skip("clean_spend.parquet not committed yet")
    fresh = run_etl(DEFAULT_RAW_PATH, tmp_path / "fresh.parquet")
    committed = pd.read_parquet(DEFAULT_OUT_PATH)
    pd.testing.assert_frame_equal(
        committed.reset_index(drop=True),
        fresh.reset_index(drop=True),
        check_dtype=False,
    )
