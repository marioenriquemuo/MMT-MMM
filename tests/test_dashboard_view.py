"""STORY-401 — dashboard view figures, bounds, and infeasible inputs."""

from __future__ import annotations

from pathlib import Path

import pytest

import src.dashboard.view as dashboard_view
from src.dashboard.view import build_dashboard, default_curves_path, slider_bounds

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic_response_curves.json"
TOL = 1e-5

_MINS = {"alpha": 5.0, "beta": 5.0, "gamma": 5.0}
_MAXS = {"alpha": 30.0, "beta": 30.0, "gamma": 30.0}
_BUDGET = 60.0


def _forbid_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*_args, **_kwargs):
        raise AssertionError("Claude was called")

    monkeypatch.setattr("src.report.brief.render_live", _boom)
    monkeypatch.setattr("src.report.brief.load_api_key", _boom)


def test_figures_and_spends_respect_bounds(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)
    out = build_dashboard(FIXTURE, _BUDGET, _MINS, _MAXS)
    assert out["error"] is None
    assert out["response_figure"] is not None
    assert out["saturation_figure"] is not None
    assert len(out["response_figure"].data) > 0
    assert len(out["saturation_figure"].data) > 0
    assert any(
        abs(float(shape.y0) - 90.0) < 1e-6
        for shape in out["saturation_figure"].layout.shapes
    )

    spends = out["allocation"]["channels"]
    assert spends
    assert out["allocation"]["total_spend"] == pytest.approx(_BUDGET, abs=TOL)
    assert sum(spends.values()) == pytest.approx(_BUDGET, abs=TOL)
    xs = [float(x) for trace in out["response_figure"].data for x in trace.x]
    for channel, spend in spends.items():
        assert spend >= _MINS[channel] - TOL
        assert spend <= _MAXS[channel] + TOL
        assert any(abs(x - spend) <= 1e-4 for x in xs)

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
    out = build_dashboard(FIXTURE, budget, mins, maxs)
    assert out["error"] is None
    assert out["allocation"]["success"] is True
    assert out["response_figure"] is not None


def test_infeasible_returns_error_without_claude(monkeypatch: pytest.MonkeyPatch):
    _forbid_claude(monkeypatch)
    out = build_dashboard(
        FIXTURE,
        10.0,
        {"alpha": 30.0, "beta": 30.0, "gamma": 30.0},
        {"alpha": 40.0, "beta": 40.0, "gamma": 30.0},
    )
    assert out["allocation"]["success"] is False
    assert out["allocation"]["channels"] == {}
    assert out["error"]
    assert "infeasible" in out["error"].lower()
    assert out["fact_pack"] is None
    assert out["offline_brief"] is None
    assert out["response_figure"] is None
    assert out["saturation_figure"] is None


def test_default_curves_path_prefers_metrics(tmp_path: Path):
    fallback = tmp_path / "tests" / "fixtures" / "synthetic_response_curves.json"
    assert default_curves_path(tmp_path) == fallback
    metrics = tmp_path / "reports" / "metrics.json"
    metrics.parent.mkdir(parents=True)
    metrics.write_text("{}", encoding="utf-8")
    assert default_curves_path(tmp_path) == metrics
