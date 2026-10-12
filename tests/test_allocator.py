"""STORY-301 Steps 2–3 — SLSQP allocator bounds, budget sum, target KPI."""

from __future__ import annotations

import json
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


# --- Step 2: maximize — bounds + sum ---


def test_optimized_spends_respect_scalar_bounds(fixture_provider: MetricsJsonCurveProvider):
    total = 60.0
    lo, hi = 5.0, 30.0
    out = optimize_budget(
        fixture_provider, total_budget=total, min_spend=lo, max_spend=hi, tol=TOL
    )
    assert out["success"] is True
    assert out["solver"]["success"] is True
    for ch, spend in out["channels"].items():
        assert spend >= lo - TOL, f"{ch} below min"
        assert spend <= hi + TOL, f"{ch} above max"
    assert out["total_spend"] == pytest.approx(total, abs=TOL)
    assert out["expected_incremental_kpi"] > 0
    assert out["incremental_kpi_delta_vs_baseline"] is not None


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
    for ch, spend in out["channels"].items():
        assert spend >= mins[ch] - TOL
        assert spend <= maxs[ch] + TOL
    assert out["total_spend"] == pytest.approx(total, abs=TOL)


def test_sum_equals_total_budget(fixture_provider: MetricsJsonCurveProvider):
    total = 45.0
    out = optimize_budget(
        fixture_provider, total_budget=total, min_spend=0.0, max_spend=40.0, tol=TOL
    )
    assert out["success"] is True
    assert out["total_spend"] == pytest.approx(total, abs=TOL)


def test_infeasible_mins_exceed_budget(fixture_provider: MetricsJsonCurveProvider):
    out = optimize_budget(
        fixture_provider, total_budget=50.0, min_spend=30.0, max_spend=40.0, tol=TOL
    )
    assert out["success"] is False
    assert "infeasible" in out["message"].lower()
    assert out["channels"] == {}


def test_infeasible_maxes_below_budget(fixture_provider: MetricsJsonCurveProvider):
    out = optimize_budget(
        fixture_provider, total_budget=100.0, min_spend=0.0, max_spend=10.0, tol=TOL
    )
    assert out["success"] is False
    assert "infeasible" in out["message"].lower()
    assert out["channels"] == {}


# --- Step 3: target KPI ---


def test_target_mode_hits_kpi_when_feasible(fixture_provider: MetricsJsonCurveProvider):
    # Fixture max KPI ≈ 38.5; T=20 is reachable under curve max spends
    target = 20.0
    out = optimize_budget(
        fixture_provider,
        target_kpi=target,
        min_spend=0.0,
        max_spend=None,
        tol=TOL,
    )
    assert out["solver"]["success"] is True
    assert out["expected_incremental_kpi"] >= target - TOL
    assert out["total_spend"] > 0
    assert out["incremental_kpi_delta_vs_baseline"] is None
    assert out["constraints"]["mode"] == "target"
    for ch, spend in out["channels"].items():
        assert spend >= -TOL


def test_target_mode_fails_when_impossible(fixture_provider: MetricsJsonCurveProvider):
    # Max KPI on fixture ≈ 18+12.5+8 = 38.5
    out = optimize_budget(
        fixture_provider,
        target_kpi=1000.0,
        min_spend=0.0,
        max_spend=None,
        tol=TOL,
    )
    assert out["solver"]["success"] is False
    assert "infeasible" in out["message"].lower()
    assert out["channels"] == {}


def test_target_mode_respects_bounds(fixture_provider: MetricsJsonCurveProvider):
    lo, hi = 2.0, 25.0
    out = optimize_budget(
        fixture_provider,
        target_kpi=15.0,
        min_spend=lo,
        max_spend=hi,
        tol=TOL,
    )
    assert out["solver"]["success"] is True
    for spend in out["channels"].values():
        assert spend >= lo - TOL
        assert spend <= hi + TOL


def test_require_exactly_one_mode(fixture_provider: MetricsJsonCurveProvider):
    both = optimize_budget(
        fixture_provider, total_budget=50.0, target_kpi=10.0, tol=TOL
    )
    assert both["success"] is False
    neither = optimize_budget(fixture_provider, tol=TOL)
    assert neither["success"] is False


# --- CLI entrypoint smoke ---


def test_cli_run_allocate_writes_json(tmp_path: Path):
    import importlib.util

    path = REPO / "scripts" / "03_allocate_budget.py"
    spec = importlib.util.spec_from_file_location("allocate_budget_cli", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    out_path = tmp_path / "allocation.json"
    result = mod.run_allocate(
        FIXTURE,
        budget=60.0,
        min_spend=5.0,
        max_spend=30.0,
        out=out_path,
    )
    assert result["solver"]["success"] is True
    assert out_path.is_file()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert "channels" in payload
    assert "solver" in payload
    assert "spends" not in payload  # on-disk = plan shape only
    assert payload["curve_source"] == str(FIXTURE)
