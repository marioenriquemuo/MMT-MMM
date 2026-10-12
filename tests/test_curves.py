"""STORY-301 Step 1 — response curve provider (interpolation + loaders)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.optimize.curves import (
    MetricsJsonCurveProvider,
    load_curve_means,
    load_curve_means_json,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic_response_curves.json"
METRICS = REPO / "reports" / "metrics.json"

# --- load_curve_means shapes ---


def test_load_fixture_nested_means():
    curves = load_curve_means_json(FIXTURE)
    assert set(curves) == {"alpha", "beta", "gamma"}
    spend, mean = curves["alpha"]
    np.testing.assert_allclose(spend, [0.0, 10.0, 20.0, 40.0])
    np.testing.assert_allclose(mean, [0.0, 10.0, 15.0, 18.0])


def test_load_flat_channel_map():
    flat = {
        "x": {"spend": [0, 1, 2], "mean": [0, 3, 4]},
        "y": {"spend": [0, 5, 10], "mean": [0, 1, 1.5]},
    }
    curves = load_curve_means(flat)
    assert set(curves) == {"x", "y"}
    np.testing.assert_allclose(curves["x"][1], [0, 3, 4])


def test_load_means_only_wrapper():
    payload = {"means": {"z": {"spend": [0, 2, 4], "mean": [0, 1, 1.5]}}}
    curves = load_curve_means(payload)
    assert list(curves) == ["z"]


# --- interpolation on fixture ---


@pytest.fixture
def fixture_provider() -> MetricsJsonCurveProvider:
    return MetricsJsonCurveProvider(FIXTURE)


def test_exact_knots(fixture_provider: MetricsJsonCurveProvider):
    p = fixture_provider
    assert p.incremental_kpi("alpha", 0.0) == pytest.approx(0.0)
    assert p.incremental_kpi("alpha", 10.0) == pytest.approx(10.0)
    assert p.incremental_kpi("alpha", 20.0) == pytest.approx(15.0)
    assert p.incremental_kpi("alpha", 40.0) == pytest.approx(18.0)


def test_midpoint_interpolation(fixture_provider: MetricsJsonCurveProvider):
    # alpha: spend 10→20, mean 10→15 → at 15: 12.5
    assert fixture_provider.incremental_kpi("alpha", 15.0) == pytest.approx(12.5)


def test_clamp_outside_range(fixture_provider: MetricsJsonCurveProvider):
    p = fixture_provider
    assert p.incremental_kpi("alpha", -5.0) == pytest.approx(0.0)
    assert p.incremental_kpi("alpha", 100.0) == pytest.approx(18.0)
    assert p.incremental_kpi("beta", -1.0) == pytest.approx(0.0)
    assert p.incremental_kpi("beta", 999.0) == pytest.approx(12.5)


def test_diminishing_nondecreasing(fixture_provider: MetricsJsonCurveProvider):
    """Fixture curves are concave / non-decreasing in spend."""
    for ch in fixture_provider.channels():
        spends = np.linspace(0.0, 40.0, 21)
        kpis = [fixture_provider.incremental_kpi(ch, float(s)) for s in spends]
        assert all(kpis[i] <= kpis[i + 1] + 1e-12 for i in range(len(kpis) - 1))


def test_unknown_channel_raises(fixture_provider: MetricsJsonCurveProvider):
    with pytest.raises(KeyError, match="unknown channel"):
        fixture_provider.incremental_kpi("nope", 1.0)


# --- committed Meridian metrics (if present) ---


@pytest.mark.skipif(not METRICS.is_file(), reason="reports/metrics.json not present")
def test_load_committed_metrics_json():
    p = MetricsJsonCurveProvider(METRICS)
    assert len(p.channels()) >= 1
    ch = p.channels()[0]
    spend = p.spend_grid(ch)
    mean = p.mean_grid(ch)
    assert spend.size == mean.size >= 2
    # Knots match; clamp below min spend
    assert p.incremental_kpi(ch, float(spend[0])) == pytest.approx(float(mean[0]))
    assert p.incremental_kpi(ch, float(spend[-1])) == pytest.approx(float(mean[-1]))
    mid = 0.5 * (float(spend[0]) + float(spend[1]))
    expected = float(np.interp(mid, spend, mean))
    assert p.incremental_kpi(ch, mid) == pytest.approx(expected)
    below = float(spend[0]) - abs(float(spend[-1] - spend[0])) - 1.0
    assert p.incremental_kpi(ch, below) == pytest.approx(float(mean[0]))
