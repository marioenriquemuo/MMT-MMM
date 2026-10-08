"""Tests for STORY-101 synthetic data generator."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.data.generator import (
    CHANNELS,
    COLUMNS,
    INTEGER_COLUMNS,
    N_DAYS,
    SEED,
    assert_valid,
    generate,
    write_outputs,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_CSV = REPO_ROOT / "data" / "raw" / "synthetic_ad_spend.csv"
COMMITTED_GT = REPO_ROOT / "data" / "raw" / "ground_truth.json"


def test_seed_stability():
    df1, gt1 = generate(seed=SEED)
    df2, gt2 = generate(seed=SEED)
    pd.testing.assert_frame_equal(df1, df2)
    assert gt1["seed_used"] == gt2["seed_used"] == SEED
    assert gt1["adstock_decay"] == gt2["adstock_decay"]


def test_schema_and_shape():
    df, _ = generate(seed=SEED)
    assert list(df.columns) == list(COLUMNS)
    assert len(df) == N_DAYS * len(CHANNELS)
    assert df["date"].nunique() == N_DAYS
    assert set(df["channel"].unique()) == set(CHANNELS)
    assert_valid(df)


def test_bounds_non_negative_no_nulls():
    df, _ = generate(seed=SEED)
    assert int(df.isna().sum().sum()) == 0
    numeric = df[["spend", "impressions", "clicks", "baseline_sales"]]
    assert bool((numeric >= 0).all().all())


def test_integer_count_columns():
    df, _ = generate(seed=SEED)
    for col in INTEGER_COLUMNS:
        assert pd.api.types.is_integer_dtype(df[col]), col
        assert bool((df[col] >= 0).all())
    # spend remains float currency
    assert pd.api.types.is_float_dtype(df["spend"])


def test_baseline_sales_repeated_per_date():
    df, _ = generate(seed=SEED)
    grouped = df.groupby("date")["baseline_sales"]
    assert bool((grouped.nunique() == 1).all())


def test_ground_truth_documents_integer_postprocess():
    _, gt = generate(seed=SEED)
    assert gt["baseline_sales_unit"] == "orders_units"
    assert gt["integer_postprocess"]["columns"] == list(INTEGER_COLUMNS)
    assert "seed=42" in gt["integer_postprocess"]["note"]


def test_different_seed_changes_output():
    df_a, _ = generate(seed=SEED)
    df_b, _ = generate(seed=99)
    assert not df_a["spend"].equals(df_b["spend"])


def test_write_outputs_roundtrip(tmp_path: Path):
    df, gt = generate(seed=SEED)
    csv_path = tmp_path / "synthetic_ad_spend.csv"
    gt_path = tmp_path / "ground_truth.json"
    write_outputs(df, gt, csv_path=csv_path, gt_path=gt_path)
    loaded = pd.read_csv(csv_path)
    assert_valid(loaded)
    meta = json.loads(gt_path.read_text())
    assert meta["seed"] == SEED
    assert meta["n_days"] == N_DAYS
    assert set(meta["channels"]) == set(CHANNELS)


@pytest.mark.skipif(not COMMITTED_CSV.exists(), reason="committed CSV not generated yet")
def test_committed_csv_matches_generator():
    df, _ = generate(seed=SEED)
    committed = pd.read_csv(COMMITTED_CSV)
    pd.testing.assert_frame_equal(df, committed, check_dtype=False)


@pytest.mark.skipif(not COMMITTED_GT.exists(), reason="committed ground_truth not generated yet")
def test_committed_ground_truth_has_planted_params():
    meta = json.loads(COMMITTED_GT.read_text())
    for key in ("adstock_decay", "hill_half", "hill_slope", "media_beta", "cpm_usd", "ctr"):
        assert key in meta
        assert set(meta[key]) == set(CHANNELS)
