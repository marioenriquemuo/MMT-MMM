"""STORY-301 Step 2 — SLSQP allocator bounds + budget sum."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.optimize.allocator import optimize_budget
from src.optimize.curves import MetricsJsonCurveProvider

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic_response_curves.json"
TOL = 1e-5


@pytest.fixture
def fixture_provider() -> MetricsJsonCurveProvider:
    return MetricsJsonCurveProvider(FIXTURE)


# --- Happy path: bounds + sum ---


def test_optimized_spends_respect_scalar_bounds(fixture_provider: MetricsJsonCurveProvider):
    total = 60.0
    lo, hi = 5.0, 30.0
    out = optimize_budget(
        fixture_provider, total_budget=total, min_spend=lo, max_spend=hi, tol=TOL
    )
    assert out["success"] is True
    for ch, spend in out["spends"].items():
        assert spend >= lo - TOL, f"{ch} below min"
        assert spend <= hi + TOL, f"{ch} above max"
    assert sum(out["spends"].values()) == pytest.approx(total, abs=TOL)
    assert out["expected_incremental_kpi"] > 0


def test_optimized_spends_respect_per_channel_bounds(
    fixture_provider: MetricsJsonCurveProvider,
):
    total = 50.0
    mins = {"alpha": 10.0, "beta": 5.0, "gamma": 0.0}
    maxs = {"alpha": 25.0, "beta": 20.0, "gamma": 15.0}
    out = optimize_budget(
        fixture_provider,
        total_budget=total,
        min_spend=mins,
        max_spend=maxs,
        tol=TOL,
    )
    assert out["success"] is True
    for ch, spend in out["spends"].items():
        assert spend >= mins[ch] - TOL
        assert spend <= maxs[ch] + TOL
    assert sum(out["spends"].values()) == pytest.approx(total, abs=TOL)


def test_sum_equals_total_budget(fixture_provider: MetricsJsonCurveProvider):
    total = 45.0
    out = optimize_budget(
        fixture_provider, total_budget=total, min_spend=0.0, max_spend=40.0, tol=TOL
    )
    assert out["success"] is True
    assert sum(out["spends"].values()) == pytest.approx(total, abs=TOL)


# --- Infeasible ---


def test_infeasible_mins_exceed_budget(fixture_provider: MetricsJsonCurveProvider):
    # 3 channels × min 30 = 90 > budget 50
    out = optimize_budget(
        fixture_provider, total_budget=50.0, min_spend=30.0, max_spend=40.0, tol=TOL
    )
    assert out["success"] is False
    assert "infeasible" in out["message"].lower()
    assert out["spends"] == {}


def test_infeasible_maxes_below_budget(fixture_provider: MetricsJsonCurveProvider):
    out = optimize_budget(
        fixture_provider, total_budget=100.0, min_spend=0.0, max_spend=10.0, tol=TOL
    )
    assert out["success"] is False
    assert "infeasible" in out["message"].lower()
    assert out["spends"] == {}
