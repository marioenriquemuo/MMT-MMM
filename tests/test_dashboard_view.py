"""STORY-401 — dashboard view figures and percent investments."""

from __future__ import annotations

from pathlib import Path

import pytest

import src.dashboard.view as dashboard_view
from src.dashboard.view import (
    build_dashboard,
    clamp_percents,
    default_curves_path,
    equal_percents,
    format_units,
    partner_investments,
    slider_bounds,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic_response_curves.json"
TOL = 1e-5

_PERCENTS = {"alpha": 50.0, "beta": 30.0, "gamma": 20.0}
_BUDGET = 60.0


def _forbid_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*_args, **_kwargs):
        raise AssertionError("Claude was called")

    monkeypatch.setattr("src.report.brief.render_live", _boom)
    monkeypatch.setattr("src.report.brief.load_api_key", _boom)


def test_figures_follow_percent_mix(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)

    def _boom(*_args, **_kwargs):
        raise AssertionError("optimizer was called")

    monkeypatch.setattr("src.optimize.allocator.optimize_budget", _boom)
    out = build_dashboard(FIXTURE, _BUDGET, _PERCENTS)
    assert out["error"] is None
    assert out["response_figure"] is not None
    assert out["saturation_figure"] is not None
    assert out["spend_move_figure"] is not None
    assert out["kpi_move_figure"] is not None
    assert len(out["response_figure"].data) > 0
    assert len(out["saturation_figure"].data) > 0
    assert len(out["spend_move_figure"].data) > 0
    assert len(out["kpi_move_figure"].data) > 0
    assert "before the move" in out["spend_move_figure"].layout.title.text
    assert "before the move" in out["kpi_move_figure"].layout.title.text
    assert format_units(2860810.3805) == "2,860,810.38"
    assert "$" not in format_units(2860810.3805)
    assert any(
        abs(float(shape.y0) - 90.0) < 1e-6
        for shape in out["saturation_figure"].layout.shapes
    )

    spends = {row["channel"]: row["recommended_spend"] for row in out["rows"]}
    assert spends == pytest.approx(partner_investments(_BUDGET, _PERCENTS))
    assert sum(spends.values()) == pytest.approx(_BUDGET, abs=TOL)
    invested = sum(spends.values())
    baseline = invested / len(spends)
    ys = [float(y) for trace in out["spend_move_figure"].data for y in trace.y]
    for channel, spend in spends.items():
        assert any(abs(y - spend) <= 1e-4 for y in ys)
        assert out["fact_pack"]["channels"][channel]["baseline_spend"] == pytest.approx(
            baseline
        )
        assert any(abs(y - baseline) <= 1e-4 for y in ys)

    assert out["fact_pack"] is not None
    assert out["offline_brief"]
    assert "incremental KPI" in out["offline_brief"]
    assert "not revenue" in out["offline_brief"]
    assert "Path-C" in out["offline_brief"]
    assert not hasattr(dashboard_view, "render_live")
    assert not hasattr(dashboard_view, "load_api_key")


def test_slider_defaults_are_feasible():
    spec = slider_bounds(FIXTURE)
    mins = {channel: row["min"] for channel, row in spec["channels"].items()}
    maxs = {channel: row["max"] for channel, row in spec["channels"].items()}
    budget = spec["budget_default"]
    assert spec["budget_min"] <= budget <= spec["budget_max"]
    assert sum(mins.values()) == pytest.approx(spec["budget_min"], abs=TOL)
    assert sum(maxs.values()) == pytest.approx(spec["budget_max"], abs=TOL)
    percents = equal_percents(list(spec["channels"]))
    assert sum(percents.values()) == pytest.approx(100.0, abs=TOL)
    out = build_dashboard(FIXTURE, budget, percents)
    assert out["error"] is None
    assert out["response_figure"] is not None
    assert sum(out["percents"].values()) == pytest.approx(100.0, abs=1e-6)


def test_second_percent_clamps_so_total_cannot_pass_100(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)
    percents = clamp_percents({"alpha": 40.0, "beta": 70.0})
    assert percents["alpha"] == pytest.approx(40.0)
    assert percents["beta"] == pytest.approx(60.0)
    assert sum(percents.values()) <= 100.0
    spend = partner_investments(100.0, percents)
    assert spend["alpha"] == pytest.approx(40.0)
    assert spend["beta"] == pytest.approx(60.0)
    assert format_units(spend["alpha"]) == "40.00"
    assert "$" not in format_units(spend["beta"])

    out = build_dashboard(FIXTURE, 100.0, {"alpha": 40.0, "beta": 70.0, "gamma": 50.0})
    assert out["error"] is None
    assert out["percents"]["alpha"] == pytest.approx(40.0)
    assert out["percents"]["beta"] == pytest.approx(60.0)
    assert out["percents"]["gamma"] == pytest.approx(0.0)
    assert sum(out["percents"].values()) <= 100.0
    by_channel = {row["channel"]: row["recommended_spend"] for row in out["rows"]}
    assert by_channel["alpha"] == pytest.approx(40.0)
    assert by_channel["beta"] == pytest.approx(60.0)
    assert by_channel["gamma"] == pytest.approx(0.0)


def test_default_curves_path_prefers_metrics(tmp_path: Path):
    fallback = tmp_path / "tests" / "fixtures" / "synthetic_response_curves.json"
    assert default_curves_path(tmp_path) == fallback
    metrics = tmp_path / "reports" / "metrics.json"
    metrics.parent.mkdir(parents=True)
    metrics.write_text("{}", encoding="utf-8")
    assert default_curves_path(tmp_path) == metrics
