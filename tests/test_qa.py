"""Tests for STORY-104 QA detectors (detect-only; no repair)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.etl import DEFAULT_OUT_PATH
from src.data.qa import ANOMALY_COLUMNS, detect_anomalies, load_panel

REPO_ROOT = Path(__file__).resolve().parents[1]
ANOMALOUS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "anomalous_spend.csv"


# --- Fixture plant ---


def test_fixture_plants_ctr_collapse_and_ips_spike():
    anomalies = detect_anomalies(ANOMALOUS_FIXTURE)
    rules = set(anomalies["rule"])
    assert "ctr_collapse" in rules
    assert "ips_outlier" in rules

    ctr = anomalies[anomalies["rule"] == "ctr_collapse"]
    assert len(ctr) == 1
    assert ctr.iloc[0]["channel"] == "meta"
    assert ctr.iloc[0]["date"] == pd.Timestamp("2023-01-20")
    assert ctr.iloc[0]["clicks"] == 0
    assert ctr.iloc[0]["impressions"] >= 1000

    ips = anomalies[anomalies["rule"] == "ips_outlier"]
    assert len(ips) == 1
    assert ips.iloc[0]["channel"] == "meta"
    assert ips.iloc[0]["date"] == pd.Timestamp("2023-01-21")
    assert ips.iloc[0]["ips"] > 2.0 * ips.iloc[0]["median_ips"]


def test_fixture_google_channel_stays_clean():
    anomalies = detect_anomalies(ANOMALOUS_FIXTURE)
    assert not (anomalies["channel"] == "google").any()


# --- Clean path ---


def test_clean_synthetic_parquet_has_zero_anomalies():
    assert DEFAULT_OUT_PATH.is_file(), "run python -m src.data.etl first"
    anomalies = detect_anomalies(DEFAULT_OUT_PATH)
    assert len(anomalies) == 0
    assert list(anomalies.columns) == list(ANOMALY_COLUMNS)


def test_load_panel_accepts_dataframe():
    df = load_panel(ANOMALOUS_FIXTURE)
    again = detect_anomalies(df)
    assert len(again) == 2
