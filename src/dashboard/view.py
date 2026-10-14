"""Dashboard math for STORY-401.

Loads offline curves, turns min/max percents into spend bounds, and runs
``optimize_budget``. Builds the fact pack, offline brief, and Plotly figures.
Does not call Claude.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import plotly.express as px

from src.optimize.allocator import optimize_budget
from src.optimize.curves import MetricsJsonCurveProvider
from src.report.brief import format_brief, render_offline
from src.report.facts import build_fact_pack

# --- Thresholds ---

# Same cutoff as src.report.facts._saturation_flag (near_ceiling).
_NEAR_CEILING_PCT = 90.0


# --- Public API ---


def format_units(value: float) -> str:
    """Thousands separators and 2 decimals. No currency symbol."""
    return f"{float(value):,.2f}"


def default_curves_path(root: str | Path | None = None) -> Path:
    """``reports/metrics.json`` when it exists, else the synthetic fixture."""
    base = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    metrics = base / "reports" / "metrics.json"
    if metrics.is_file():
        return metrics
    return base / "tests" / "fixtures" / "synthetic_response_curves.json"


def slider_bounds(curves_path: str | Path) -> dict[str, Any]:
    """Spend-knot ranges and a feasible default budget.

    Channel min/max default to that channel's lowest and highest spend knot.
    ``budget_default`` is the midpoint of the sum of those mins and maxes.
    """
    provider = MetricsJsonCurveProvider(curves_path)
    channels: dict[str, dict[str, float]] = {}
    for channel in provider.channels():
        grid = provider.spend_grid(channel)
        lo = float(grid.min())
        hi = float(grid.max())
        channels[channel] = {"min": lo, "max": hi, "step": _slider_step(lo, hi)}
    budget_min = float(sum(row["min"] for row in channels.values()))
    budget_max = float(sum(row["max"] for row in channels.values()))
    return {
        "channels": channels,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "budget_default": (budget_min + budget_max) / 2.0,
        "budget_step": _slider_step(budget_min, budget_max),
    }


def clamp_percent(requested: float, others: float) -> float:
    """Keep one percent inside the room still left (``100 - others``)."""
    room = 100.0 - float(others)
    if room < 0.0:
        room = 0.0
    value = float(requested)
    if value < 0.0:
        value = 0.0
    if value > room:
        value = room
    return value


def clamp_min_percent(requested: float, others: float, this_max: float) -> float:
    """Min percent: room left by the other mins, and not above this partner's max."""
    value = clamp_percent(requested, others)
    cap = float(this_max)
    if cap < 0.0:
        cap = 0.0
    if cap > 100.0:
        cap = 100.0
    if value > cap:
        value = cap
    return value


def clamp_max_percent(requested: float, this_min: float) -> float:
    """Max percent stays in 0–100 and cannot fall below this partner's min."""
    value = float(requested)
    if value < 0.0:
        value = 0.0
    if value > 100.0:
        value = 100.0
    floor = float(this_min)
    if floor < 0.0:
        floor = 0.0
    if value < floor:
        value = floor
    return value


def clamp_percents(percents: Mapping[str, float]) -> dict[str, float]:
    """Walk mins in order. Each one keeps only the room earlier ones left."""
    out: dict[str, float] = {}
    used = 0.0
    for name, requested in percents.items():
        value = clamp_percent(requested, used)
        out[str(name)] = value
        used += value
    return out


def partner_investments(budget: float, percents: Mapping[str, float]) -> dict[str, float]:
    """Spend units: ``(percent / 100) × budget``. Not a currency."""
    scale = float(budget) / 100.0
    return {str(name): scale * float(pct) for name, pct in percents.items()}


def build_dashboard(
    curves_path: str | Path,
    total_budget: float,
    min_pct: Mapping[str, float],
    max_pct: Mapping[str, float],
) -> dict[str, Any]:
    """Maximize KPI inside min/max percents of the budget.

    Recommended spend is the optimizer result. Before-the-move spend is the
    equal-room baseline. Mins that add up past 100 are clamped in channel
    order, and a min cannot sit above its max. Does not call Claude.
    """
    provider = MetricsJsonCurveProvider(curves_path)
    names = provider.channels()
    if not names:
        return _failed("curve file has no channels")
    maxes = {
        name: clamp_max_percent(float(max_pct.get(name, 100.0)), 0.0) for name in names
    }
    mins: dict[str, float] = {}
    used = 0.0
    for name in names:
        value = clamp_min_percent(float(min_pct.get(name, 0.0)), used, maxes[name])
        mins[name] = value
        used += value
    budget = float(total_budget)
    min_spend = partner_investments(budget, mins)
    max_spend = partner_investments(budget, maxes)
    allocation = optimize_budget(
        provider,
        total_budget=budget,
        min_spend=min_spend,
        max_spend=max_spend,
        curve_source=str(curves_path),
    )
    if not allocation.get("success"):
        message = str(allocation.get("message") or "allocator failed")
        return _failed(message, mins=mins, maxes=maxes)
    try:
        fact_pack = build_fact_pack(allocation)
        offline_brief = format_brief(render_offline(fact_pack))
    except (ValueError, RuntimeError) as exc:
        return _failed(str(exc), mins=mins, maxes=maxes)

    spends = {
        name: float(row["recommended_spend"]) for name, row in fact_pack["channels"].items()
    }
    rows = [
        {
            "channel": name,
            "min_percent": mins[name],
            "max_percent": maxes[name],
            "recommended_spend": spends[name],
            "saturation_flag": fact_pack["channels"][name]["saturation_flag"],
            "incremental_kpi": provider.incremental_kpi(name, spends[name]),
        }
        for name in names
    ]
    return {
        "min_percent": mins,
        "max_percent": maxes,
        "fact_pack": fact_pack,
        "offline_brief": offline_brief,
        "response_figure": _response_figure(provider, spends),
        "saturation_figure": _saturation_figure(spends, max_spend),
        "spend_move_figure": _spend_move_figure(fact_pack),
        "kpi_move_figure": _kpi_move_figure(provider, fact_pack),
        "error": None,
        "rows": rows,
        "expected_incremental_kpi": fact_pack.get("expected_incremental_kpi"),
        "lift_vs_baseline": fact_pack.get("incremental_kpi_delta_vs_baseline"),
    }


# --- Figures ---


def _response_figure(provider: MetricsJsonCurveProvider, spends: Mapping[str, float]):
    rows = [
        {
            "channel": channel,
            "spend": float(spend),
            "incremental_kpi": float(kpi),
        }
        for channel in spends
        for spend, kpi in zip(
            provider.spend_grid(channel), provider.mean_grid(channel), strict=True
        )
    ]
    fig = px.line(
        pd.DataFrame(rows),
        x="spend",
        y="incremental_kpi",
        color="channel",
        markers=True,
        title="Response curves",
        labels={"spend": "Spend", "incremental_kpi": "Incremental KPI"},
    )
    for channel, spend in spends.items():
        fig.add_scatter(
            x=[float(spend)],
            y=[provider.incremental_kpi(channel, float(spend))],
            mode="markers",
            name=f"{channel} recommended",
            marker={"size": 14, "symbol": "diamond"},
        )
    return _show_units(fig, numeric_x=True)


def _saturation_figure(spends: Mapping[str, float], max_spend: Mapping[str, float]):
    percents: list[float] = []
    rows: list[dict[str, Any]] = []
    for channel, spend in spends.items():
        hi = float(max_spend[channel])
        pct = 0.0 if hi <= 0 else 100.0 * float(spend) / hi
        percents.append(pct)
        rows.append({"channel": channel, "pct_of_max": pct})
    fig = px.bar(
        pd.DataFrame(rows),
        x="channel",
        y="pct_of_max",
        title="Spend as % of channel max",
        labels={"pct_of_max": "Percent of channel max", "channel": "Channel"},
    )
    fig.add_hline(
        y=_NEAR_CEILING_PCT,
        line_dash="dash",
        annotation_text="90% near-ceiling",
    )
    top = max(100.0, max(percents) if percents else 100.0)
    fig.update_yaxes(range=[0, top])
    return _show_units(fig)


def _spend_move_figure(fact_pack: Mapping[str, Any]):
    rows = []
    for channel, fact in fact_pack["channels"].items():
        rows.append(
            {
                "channel": channel,
                "when": "Before the move",
                "spend": float(fact["baseline_spend"]),
            }
        )
        rows.append(
            {
                "channel": channel,
                "when": "After the move",
                "spend": float(fact["recommended_spend"]),
            }
        )
    fig = px.bar(
        pd.DataFrame(rows),
        x="channel",
        y="spend",
        color="when",
        barmode="group",
        title="Spend before the move vs after the move",
        labels={"spend": "Spend", "channel": "Channel", "when": ""},
        category_orders={"when": ["Before the move", "After the move"]},
    )
    return _show_units(fig)


def _kpi_move_figure(provider: MetricsJsonCurveProvider, fact_pack: Mapping[str, Any]):
    rows = []
    for channel, fact in fact_pack["channels"].items():
        rows.append(
            {
                "channel": channel,
                "when": "Before the move",
                "incremental_kpi": provider.incremental_kpi(
                    channel, float(fact["baseline_spend"])
                ),
            }
        )
        rows.append(
            {
                "channel": channel,
                "when": "After the move",
                "incremental_kpi": provider.incremental_kpi(
                    channel, float(fact["recommended_spend"])
                ),
            }
        )
    fig = px.bar(
        pd.DataFrame(rows),
        x="channel",
        y="incremental_kpi",
        color="when",
        barmode="group",
        title="KPI before the move vs after the move",
        labels={
            "incremental_kpi": "Incremental KPI",
            "channel": "Channel",
            "when": "",
        },
        category_orders={"when": ["Before the move", "After the move"]},
    )
    return _show_units(fig)


def _show_units(fig, *, numeric_x: bool = False):
    """Tick and hover text only. Trace values stay full precision."""
    fig.update_yaxes(tickformat=",.2f")
    if numeric_x:
        fig.update_xaxes(tickformat=",.2f")
        hover = "%{x:,.2f}<br>%{y:,.2f}<extra>%{fullData.name}</extra>"
    else:
        hover = "%{x}<br>%{y:,.2f}<extra>%{fullData.name}</extra>"
    fig.update_traces(hovertemplate=hover)
    return fig


# --- Helpers ---


def _slider_step(lo: float, hi: float) -> float:
    span = hi - lo
    if span <= 0:
        return 1.0
    exp = math.floor(math.log10(span / 100.0))
    return float(10**exp)


def _failed(
    message: str,
    mins: Mapping[str, float] | None = None,
    maxes: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    return {
        "min_percent": dict(mins or {}),
        "max_percent": dict(maxes or {}),
        "fact_pack": None,
        "offline_brief": None,
        "response_figure": None,
        "saturation_figure": None,
        "spend_move_figure": None,
        "kpi_move_figure": None,
        "error": message,
        "rows": [],
        "expected_incremental_kpi": None,
        "lift_vs_baseline": None,
    }
