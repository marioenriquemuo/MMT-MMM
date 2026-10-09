"""Tests for STORY-104 QA detect + repair + run_qa gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from src.data.etl import DEFAULT_OUT_PATH
from src.data.qa import (
    ANOMALY_COLUMNS,
    LOG_COLUMNS,
    UnrepairedAnomaliesError,
    detect_anomalies,
    load_panel,
    main,
    repair_panel,
    run_qa,
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


# --- run_qa / CLI (Step 3) ---


def test_run_qa_success_on_clean_parquet(tmp_path: Path):
    assert DEFAULT_OUT_PATH.is_file(), "run python -m src.data.etl first"
    out = tmp_path / "clean_spend.parquet"
    log = tmp_path / "qa_repair_log.csv"
    original = load_panel(DEFAULT_OUT_PATH)

    panel = run_qa(DEFAULT_OUT_PATH, out, log)

    assert out.is_file()
    assert not log.exists()  # nothing repaired → skip log file
    loaded = load_panel(out)
    pd.testing.assert_series_equal(
        loaded["spend"].reset_index(drop=True),
        original["spend"].reset_index(drop=True),
    )
    pd.testing.assert_series_equal(
        loaded["baseline_sales"].reset_index(drop=True),
        original["baseline_sales"].reset_index(drop=True),
    )
    assert len(panel) == len(original)


def test_run_qa_hard_fail_does_not_overwrite(tmp_path: Path):
    out = tmp_path / "clean_spend.parquet"
    log = tmp_path / "qa_repair_log.csv"
    out.write_text("sentinel-do-not-clobber", encoding="utf-8")

    with pytest.raises(UnrepairedAnomaliesError) as excinfo:
        run_qa(ANOMALOUS_FIXTURE, out, log)

    assert len(excinfo.value.unrepaired) >= 1
    assert out.read_text(encoding="utf-8") == "sentinel-do-not-clobber"
    assert not log.exists()


def test_run_qa_repairs_and_overwrites_when_fully_fixable(tmp_path: Path):
    """Drop tiktok (insufficient history) so meta CTR+IPS repairs can succeed."""
    src = load_panel(ANOMALOUS_FIXTURE)
    src = src.loc[src["channel"] != "tiktok"].reset_index(drop=True)
    in_path = tmp_path / "meta_google.csv"
    src.to_csv(in_path, index=False)

    out = tmp_path / "clean_spend.parquet"
    log = tmp_path / "qa_repair_log.csv"
    panel = run_qa(in_path, out, log)

    assert out.is_file()
    assert log.is_file()
    loaded_log = pd.read_csv(log)
    assert set(loaded_log["rule"]) == {"ctr_collapse", "ips_outlier"}

    # Compare on keys (run_qa re-sorts to date × channel like ETL).
    left = panel.sort_values(["date", "channel"]).reset_index(drop=True)
    right = src.sort_values(["date", "channel"]).reset_index(drop=True)
    pd.testing.assert_series_equal(left["spend"], right["spend"])
    pd.testing.assert_series_equal(left["baseline_sales"], right["baseline_sales"])


def test_main_exit_0_on_clean(tmp_path: Path):
    assert DEFAULT_OUT_PATH.is_file(), "run python -m src.data.etl first"
    code = main(
        in_path=DEFAULT_OUT_PATH,
        out_path=tmp_path / "clean_spend.parquet",
        log_path=tmp_path / "qa_repair_log.csv",
    )
    assert code == 0


def test_main_exit_nonzero_when_unrepaired(tmp_path: Path):
    out = tmp_path / "clean_spend.parquet"
    out.write_bytes(b"keep")
    code = main(
        in_path=ANOMALOUS_FIXTURE,
        out_path=out,
        log_path=tmp_path / "qa_repair_log.csv",
    )
    assert code != 0
    assert out.read_bytes() == b"keep"


def test_cli_module_exit_0_on_clean(tmp_path: Path):
    """``python -m src.data.qa`` entry exits 0 on clean panel (tmp out — no clobber)."""
    assert DEFAULT_OUT_PATH.is_file(), "run python -m src.data.etl first"
    out = tmp_path / "clean_spend.parquet"
    log = tmp_path / "qa_repair_log.csv"
    script = (
        "from pathlib import Path; "
        "from src.data.etl import DEFAULT_OUT_PATH; "
        "from src.data.qa import main; "
        f"raise SystemExit(main(DEFAULT_OUT_PATH, Path({str(out)!r}), Path({str(log)!r})))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert out.is_file()
