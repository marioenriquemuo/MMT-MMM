"""Unit tests for STORY-201 spike helpers (no Meridian MCMC)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

REPO_ROOT = Path(__file__).resolve().parents[1]
SPIKE_PATH = REPO_ROOT / "scripts" / "02_model_spike.py"


def _load_spike():
    """Import scripts/02_model_spike.py without running main (no Meridian import)."""
    name = "model_spike_helpers_under_test"
    spec = importlib.util.spec_from_file_location(name, SPIKE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def spike():
    return _load_spike()


def test_response_curve_means_structure(spike):
    channels = ["meta", "google"]
    multipliers = [0.0, 1.0, 2.0]
    # (spend_multiplier, channel, metric=mean/ci_lo/ci_hi)
    outcome = np.zeros((3, 2, 3), dtype=float)
    outcome[:, 0, 0] = [0.0, 10.0, 18.0]  # meta mean
    outcome[:, 0, 1] = [0.0, 8.0, 14.0]
    outcome[:, 0, 2] = [0.0, 12.0, 22.0]
    outcome[:, 1, 0] = [0.0, 5.0, 9.0]  # google mean
    outcome[:, 1, 1] = [0.0, 4.0, 7.0]
    outcome[:, 1, 2] = [0.0, 6.0, 11.0]
    spend = np.array([[0.0, 0.0], [100.0, 50.0], [200.0, 100.0]])
    curves = xr.Dataset(
        data_vars={
            "incremental_outcome": (("spend_multiplier", "channel", "metric"), outcome),
            "spend": (("spend_multiplier", "channel"), spend),
        },
        coords={
            "channel": channels,
            "metric": ["mean", "ci_lo", "ci_hi"],
            "spend_multiplier": multipliers,
        },
    )
    means = spike.response_curve_means(curves)
    assert set(means) == {"meta", "google"}
    assert means["meta"]["spend_multiplier"] == multipliers
    assert means["meta"]["mean"] == [0.0, 10.0, 18.0]
    assert means["meta"]["ci_lo"] == [0.0, 8.0, 14.0]
    assert means["meta"]["ci_hi"] == [0.0, 12.0, 22.0]
    assert means["meta"]["spend"] == [0.0, 100.0, 200.0]
    assert means["google"]["mean"] == [0.0, 5.0, 9.0]


def test_response_curve_means_empty_without_outcome(spike):
    assert spike.response_curve_means(None) == {}
    empty = xr.Dataset(data_vars={"spend": (("x",), [1.0])})
    assert spike.response_curve_means(empty) == {}


def test_recovery_rank_stats_directional_false(spike):
    # Opposite ranks → negative Spearman → not directional recovery.
    iroas = {"meta": 1.0, "google": 0.8, "tiktok": 0.6, "tv": 0.4}
    contrib = {"tv": 4.0, "google": 3.0, "meta": 2.0, "tiktok": 1.0}
    stats = spike.recovery_rank_stats(iroas, contrib)
    assert stats["recovery_spearman"] is not None
    assert stats["recovery_spearman"] < 0
    assert stats["directional_recovery"] is False


def test_recovery_rank_stats_directional_true(spike):
    iroas = {"tv": 1.0, "google": 0.8, "meta": 0.6, "tiktok": 0.4}
    contrib = {"tv": 4.0, "google": 3.0, "meta": 2.0, "tiktok": 1.0}
    stats = spike.recovery_rank_stats(iroas, contrib)
    assert stats["recovery_spearman"] == pytest.approx(1.0)
    assert stats["directional_recovery"] is True
