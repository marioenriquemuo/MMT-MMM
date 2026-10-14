"""STORY-401 — dashboard view: min/max percents become optimizer bounds."""

from __future__ import annotations

from pathlib import Path

import pytest

import src.dashboard.view as dashboard_view
from src.dashboard.view import (
    build_dashboard,
    clamp_min_percent,
    default_curves_path,
    format_units,
    partner_investments,
    slider_bounds,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic_response_curves.json"
TOL = 1e-5

_MINS = {"alpha": 10.0, "beta": 10.0, "gamma": 10.0}
_MAXES = {"alpha": 50.0, "beta": 50.0, "gamma": 50.0}
_BUDGET = 60.0


def _forbid_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*_args, **_kwargs):
        raise AssertionError("Claude was called")

    monkeypatch.setattr("src.report.brief.render_live", _boom)
    monkeypatch.setattr("src.report.brief.load_api_key", _boom)


def test_optimizer_respects_min_max_spends(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)
    out = build_dashboard(FIXTURE, _BUDGET, _MINS, _MAXES)
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

    min_spend = partner_investments(_BUDGET, _MINS)
    max_spend = partner_investments(_BUDGET, _MAXES)
    spends = {row["channel"]: row["recommended_spend"] for row in out["rows"]}
    assert sum(spends.values()) == pytest.approx(_BUDGET, abs=TOL)
    assert sum(spends.values()) != pytest.approx(sum(min_spend.values()), abs=0.5)
    for channel, spend in spends.items():
        assert min_spend[channel] - TOL <= spend <= max_spend[channel] + TOL
        assert out["fact_pack"]["channels"][channel]["baseline_spend"] == pytest.approx(20.0)

    ys = [float(y) for trace in out["spend_move_figure"].data for y in trace.y]
    for spend in spends.values():
        assert any(abs(y - spend) <= 1e-4 for y in ys)
        assert any(abs(y - 20.0) <= 1e-4 for y in ys)

    assert out["fact_pack"] is not None
    assert out["offline_brief"]
    assert "incremental KPI" in out["offline_brief"]
    assert "not revenue" in out["offline_brief"]
    assert "Path-C" in out["offline_brief"]
    assert not hasattr(dashboard_view, "render_live")
    assert not hasattr(dashboard_view, "load_api_key")


def test_slider_defaults_are_feasible():
    spec = slider_bounds(FIXTURE)
    knot_mins = {channel: row["min"] for channel, row in spec["channels"].items()}
    knot_maxs = {channel: row["max"] for channel, row in spec["channels"].items()}
    budget = spec["budget_default"]
    assert spec["budget_min"] <= budget <= spec["budget_max"]
    assert sum(knot_mins.values()) == pytest.approx(spec["budget_min"], abs=TOL)
    assert sum(knot_maxs.values()) == pytest.approx(spec["budget_max"], abs=TOL)
    out = build_dashboard(FIXTURE, budget, {}, {})
    assert out["error"] is None
    assert out["response_figure"] is not None
    assert set(out["min_percent"]) == set(spec["channels"])
    assert all(value == pytest.approx(0.0) for value in out["min_percent"].values())
    assert all(value == pytest.approx(100.0) for value in out["max_percent"].values())
    spends = {row["channel"]: row["recommended_spend"] for row in out["rows"]}
    assert sum(spends.values()) == pytest.approx(budget, abs=TOL)
    for channel, spend in spends.items():
        assert 0.0 - TOL <= spend <= budget + TOL
        assert out["fact_pack"]["channels"][channel]["baseline_spend"] == pytest.approx(
            budget / len(spends)
        )


def test_second_min_clamps_so_mins_cannot_pass_100(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)
    assert clamp_min_percent(70.0, 40.0, 100.0) == pytest.approx(60.0)
    assert clamp_min_percent(80.0, 0.0, 50.0) == pytest.approx(50.0)

    out = build_dashboard(
        FIXTURE,
        100.0,
        {"alpha": 40.0, "beta": 70.0, "gamma": 50.0},
        {"alpha": 100.0, "beta": 100.0, "gamma": 100.0},
    )
    assert out["error"] is None
    assert out["min_percent"]["alpha"] == pytest.approx(40.0)
    assert out["min_percent"]["beta"] == pytest.approx(60.0)
    assert out["min_percent"]["gamma"] == pytest.approx(0.0)
    assert sum(out["min_percent"].values()) <= 100.0
    assert all(value == pytest.approx(100.0) for value in out["max_percent"].values())
    spend = partner_investments(100.0, out["min_percent"])
    assert spend["alpha"] == pytest.approx(40.0)
    assert spend["beta"] == pytest.approx(60.0)
    by_channel = {row["channel"]: row["recommended_spend"] for row in out["rows"]}
    assert by_channel["alpha"] == pytest.approx(40.0)
    assert by_channel["beta"] == pytest.approx(60.0)
    assert by_channel["gamma"] == pytest.approx(0.0)
    assert format_units(by_channel["alpha"]) == "40.00"
    assert "$" not in format_units(by_channel["beta"])


def test_infeasible_maxes_show_allocator_error(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)
    out = build_dashboard(
        FIXTURE,
        100.0,
        {"alpha": 0.0, "beta": 0.0, "gamma": 0.0},
        {"alpha": 10.0, "beta": 10.0, "gamma": 10.0},
    )
    assert out["error"] is not None
    assert "infeasible" in out["error"]
    assert out["fact_pack"] is None
    assert out["offline_brief"] is None
    assert out["spend_move_figure"] is None
    assert out["rows"] == []


def test_default_curves_path_prefers_metrics(tmp_path: Path):
    fallback = tmp_path / "tests" / "fixtures" / "synthetic_response_curves.json"
    assert default_curves_path(tmp_path) == fallback
    metrics = tmp_path / "reports" / "metrics.json"
    metrics.parent.mkdir(parents=True)
    metrics.write_text("{}", encoding="utf-8")
    assert default_curves_path(tmp_path) == metrics
