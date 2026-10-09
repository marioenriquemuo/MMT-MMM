"""Tests for STORY-104 QA detect + repair (no CLI / parquet overwrite yet)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.etl import DEFAULT_OUT_PATH
from src.data.qa import (
    ANOMALY_COLUMNS,
    LOG_COLUMNS,
    detect_anomalies,
    load_panel,
    repair_panel,
    write_repair_log,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ANOMALOUS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "anomalous_spend.csv"


# --- Fixture plant (detect) ---


def test_fixture_plants_ctr_collapse_and_ips_spike():
    anomalies = detect_anomalies(ANOMALOUS_FIXTURE)
    rules = set(anomalies["rule"])
    assert "ctr_collapse" in rules
    assert "ips_outlier" in rules

    ctr = anomalies[
        (anomalies["rule"] == "ctr_collapse") & (anomalies["channel"] == "meta")
    ]
    assert len(ctr) == 1
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


def test_fixture_tiktok_insufficient_history_still_detected():
    anomalies = detect_anomalies(ANOMALOUS_FIXTURE)
    tik = anomalies[
        (anomalies["channel"] == "tiktok") & (anomalies["rule"] == "ctr_collapse")
    ]
    assert len(tik) == 1
    assert tik.iloc[0]["date"] == pd.Timestamp("2023-01-05")
    assert tik.iloc[0]["clicks"] == 0


# --- Clean path ---


def test_clean_synthetic_parquet_has_zero_anomalies():
    assert DEFAULT_OUT_PATH.is_file(), "run python -m src.data.etl first"
    anomalies = detect_anomalies(DEFAULT_OUT_PATH)
    assert len(anomalies) == 0
    assert list(anomalies.columns) == list(ANOMALY_COLUMNS)


def test_load_panel_accepts_dataframe():
    df = load_panel(ANOMALOUS_FIXTURE)
    again = detect_anomalies(df)
    assert len(again) == 3  # meta CTR + meta IPS + tiktok CTR


# --- Repair ---


def test_repair_fixes_meta_ctr_and_ips_leaves_spend_kpi():
    original = load_panel(ANOMALOUS_FIXTURE)
    panel, log_df, unrepaired = repair_panel(ANOMALOUS_FIXTURE)

    # spend / baseline_sales immutable
    pd.testing.assert_series_equal(
        panel["spend"].reset_index(drop=True),
        original["spend"].reset_index(drop=True),
    )
    pd.testing.assert_series_equal(
        panel["baseline_sales"].reset_index(drop=True),
        original["baseline_sales"].reset_index(drop=True),
    )

    meta_ctr_day = panel[
        (panel["channel"] == "meta") & (panel["date"] == "2023-01-20")
    ].iloc[0]
    assert meta_ctr_day["impressions"] == 100000
    assert meta_ctr_day["clicks"] == 1000  # round(0.01 * 100000)

    meta_ips_day = panel[
        (panel["channel"] == "meta") & (panel["date"] == "2023-01-21")
    ].iloc[0]
    assert meta_ips_day["impressions"] == 100000  # round(100 * 1000)
    assert meta_ips_day["clicks"] == 5000  # unchanged (not a CTR collapse after repair)

    assert set(log_df["rule"]) == {"ctr_collapse", "ips_outlier"}
    assert set(log_df["channel"]) == {"meta"}
    assert list(log_df.columns) == list(LOG_COLUMNS)

    ips_log = log_df[log_df["rule"] == "ips_outlier"].iloc[0]
    assert ips_log["old_impressions"] == 500000
    assert ips_log["new_impressions"] == 100000
    assert ips_log["old_clicks"] == ips_log["new_clicks"] == 5000

    ctr_log = log_df[log_df["rule"] == "ctr_collapse"].iloc[0]
    assert ctr_log["old_clicks"] == 0
    assert ctr_log["new_clicks"] == 1000
    assert ctr_log["old_impressions"] == ctr_log["new_impressions"] == 100000


def test_repair_insufficient_history_left_unrepaired():
    panel, log_df, unrepaired = repair_panel(ANOMALOUS_FIXTURE)

    tik = unrepaired[unrepaired["channel"] == "tiktok"]
    assert len(tik) == 1
    assert tik.iloc[0]["rule"] == "ctr_collapse"
    assert tik.iloc[0]["date"] == pd.Timestamp("2023-01-05")

    # panel still has the bad clicks
    row = panel[
        (panel["channel"] == "tiktok") & (panel["date"] == "2023-01-05")
    ].iloc[0]
    assert row["clicks"] == 0
    assert row["impressions"] == 50000

    # insufficient-history day never appears in the repair log
    assert not (log_df["channel"] == "tiktok").any()


def test_write_repair_log_to_tmp(tmp_path: Path):
    _, log_df, _ = repair_panel(ANOMALOUS_FIXTURE)
    out = tmp_path / "qa_repair_log.csv"
    written = write_repair_log(log_df, out)
    assert written == out
    assert out.is_file()
    loaded = pd.read_csv(out)
    assert list(loaded.columns) == list(LOG_COLUMNS)
    assert len(loaded) == len(log_df)


def test_write_repair_log_skips_empty(tmp_path: Path):
    empty = pd.DataFrame(columns=list(LOG_COLUMNS))
    out = tmp_path / "qa_repair_log.csv"
    assert write_repair_log(empty, out) is None
    assert not out.exists()


def test_repair_clean_panel_noop():
    assert DEFAULT_OUT_PATH.is_file(), "run python -m src.data.etl first"
    original = load_panel(DEFAULT_OUT_PATH)
    panel, log_df, unrepaired = repair_panel(DEFAULT_OUT_PATH)
    assert len(log_df) == 0
    assert len(unrepaired) == 0
    pd.testing.assert_frame_equal(
        panel.reset_index(drop=True),
        original.reset_index(drop=True),
        check_dtype=False,
    )
