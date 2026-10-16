"""STORY-503: geo-experiment bounds tighten the national ROI prior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from src.data.tenants import REPO_ROOT, TenantError, load_client
from src.models.calibration import (
    build_report,
    central_bounds,
    loc_scale,
    model_spec,
    run,
)
from src.models.meridian_data import CHANNEL_ORDER

FIXTURE = REPO_ROOT / "data" / "raw" / "calibration" / "geo_experiment.json"


def _rows(*items: dict) -> list[dict]:
    return list(items)


def _roi(channel: str, region: str, low: float, high: float, confidence: float, metric: str = "roi"):
    return {
        "channel": channel,
        "region": region,
        "metric": metric,
        "low": low,
        "high": high,
        "confidence": confidence,
    }


def test_interval_matches_experiment_bounds():
    low, high, confidence = 0.5, 1.5, 0.9
    loc, scale = loc_scale(low, high, confidence)
    got_low, got_high = central_bounds(loc, scale, confidence)
    assert got_low == pytest.approx(low)
    assert got_high == pytest.approx(high)


def test_channel_order_keeps_meta_before_google():
    rows = _rows(
        _roi("google", "national", 0.4, 1.0, 0.9),
        _roi("meta", "national", 0.5, 1.5, 0.9),
    )
    channels = list(CHANNEL_ORDER)
    spec = model_spec(channels, rows, max_lag=8, region="national")
    locs = [float(value) for value in spec.prior.roi_m.loc]
    meta_loc, _ = loc_scale(0.5, 1.5, 0.9)
    google_loc, _ = loc_scale(0.4, 1.0, 0.9)
    assert locs[0] == pytest.approx(meta_loc)
    assert locs[1] == pytest.approx(google_loc)
    assert channels.index("meta") < channels.index("google")


def test_rejects_non_roi_and_non_positive_bounds():
    rows = _rows(
        _roi("meta", "national", 0.5, 1.5, 0.9, metric="cpa"),
        _roi("meta", "national", 0.0, 1.5, 0.9),
        _roi("meta", "national", -1.0, 1.5, 0.9),
        _roi("meta", "national", 2.0, 1.0, 0.9),
        _roi("meta", "national", 0.5, 1.5, 0.0),
        _roi("meta", "national", 0.5, 1.5, 1.0),
    )
    client = load_client("pathc")
    report, ok = build_report(client, rows)
    meta = report["channels"][0]
    assert meta["channel"] == "meta"
    assert meta["calibrated"] is False
    assert ok is True


def test_bogota_row_does_not_move_national_prior():
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))["experiments"]
    client = load_client("pathc")
    report, ok = build_report(client, rows)
    by_name = {row["channel"]: row for row in report["channels"]}
    meta_loc, meta_scale = loc_scale(0.5, 1.5, 0.9)
    assert by_name["meta"]["calibrated"] is True
    assert by_name["meta"]["after"]["loc"] == pytest.approx(meta_loc)
    assert by_name["meta"]["after"]["scale"] == pytest.approx(meta_scale)
    assert by_name["meta"]["experiment_interval"]["low"] == 0.5
    assert ok is True


def test_path_inside_other_client_raises(tmp_path: Path):
    pathc_json = FIXTURE
    with pytest.raises(TenantError):
        run("wellness", pathc_json, tmp_path / "calibration_delta.json")


def test_report_tightens_meta_and_google_only(tmp_path: Path):
    out = tmp_path / "calibration_delta.json"
    assert run("pathc", FIXTURE, out) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    by_name = {row["channel"]: row for row in report["channels"]}
    assert [row["channel"] for row in report["channels"]] == ["meta", "google", "tiktok", "tv"]
    for channel in ("meta", "google"):
        row = by_name[channel]
        assert row["calibrated"] is True
        assert row["inside_experiment_interval"] is True
        assert row["scale_tightened"] is True
        assert row["after"]["scale"] < row["before"]["scale"]
    for channel in ("tiktok", "tv"):
        row = by_name[channel]
        assert row["calibrated"] is False
        assert row["after"] == row["before"]
        assert row["scale_tightened"] is False


def test_wellness_without_file_stays_uncalibrated(tmp_path: Path):
    missing = load_client("wellness")["roots"]["raw"] / "calibration" / "geo_experiment.json"
    assert not missing.is_file()
    out = tmp_path / "calibration_delta.json"
    assert run("wellness", missing, out) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert [row["channel"] for row in report["channels"]] == ["meta", "google"]
    assert all(row["calibrated"] is False for row in report["channels"])


def test_exit_1_when_scale_does_not_shrink(tmp_path: Path):
    src = tmp_path / "wide.json"
    src.write_text(
        json.dumps(
            {"experiments": [_roi("meta", "national", 0.01, 100.0, 0.5)]}
        ),
        encoding="utf-8",
    )
    out = tmp_path / "calibration_delta.json"
    assert run("pathc", src, out) == 1
    meta = json.loads(out.read_text(encoding="utf-8"))["channels"][0]
    assert meta["scale_tightened"] is False


def test_spike_refuses_wide_experiment_before_sampling(tmp_path: Path, monkeypatch, capsys):
    src = tmp_path / "wide.json"
    src.write_text(
        json.dumps({"experiments": [_roi("meta", "national", 0.01, 100.0, 0.5)]}),
        encoding="utf-8",
    )
    from tests.test_model_spike_helpers import _load_spike

    spike = _load_spike()

    def _no_model(*_args, **_kwargs):
        raise AssertionError("Meridian model was constructed")

    monkeypatch.setattr(spike, "_build_mmm", _no_model)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "02_model_spike.py",
            "--mode",
            "smoke",
            "--client_id",
            "pathc",
            "--calibration",
            str(src),
        ],
    )
    assert spike.main() == 1
    err = capsys.readouterr().err
    assert "meta: scale is not tighter than the default prior" in err
