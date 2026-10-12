"""STORY-301 Step 4 — Plotly Express teaching plots for budget allocation.

Writes under ``reports/figures/``:

* ``story_301_response_curves.html`` — response curves (fixture or ``--curves``)
* ``story_301_allocation_vs_baseline.html`` — baseline vs optimized spend + KPI bars

Usage (from repo root, conda env ``mmt-mmm``)::

    python scripts/plot_allocation_teaching.py
    python scripts/plot_allocation_teaching.py --curves reports/metrics.json \\
        --budget 100000 --min-spend 0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.optimize.allocator import optimize_budget  # noqa: E402
from src.optimize.curves import MetricsJsonCurveProvider  # noqa: E402

# --- Paths / defaults ---

FIG_DIR = REPO_ROOT / "reports" / "figures"
CURVES_OUT = FIG_DIR / "story_301_response_curves.html"
BARS_OUT = FIG_DIR / "story_301_allocation_vs_baseline.html"
DEFAULT_CURVES = REPO_ROOT / "tests" / "fixtures" / "synthetic_response_curves.json"
DEFAULT_BUDGET = 60.0
DEFAULT_MIN = 5.0
DEFAULT_MAX = 30.0


# --- Helpers ---


def _equal_room_baseline(
    channels: list[str],
    budget: float,
    min_spend: float,
    max_spend: float,
) -> dict[str, float]:
    """Equal-room fill from mins (matches allocator maximize baseline)."""
    n = len(channels)
    lo = np.full(n, float(min_spend))
    hi = np.full(n, float(max_spend))
    remaining = budget - float(lo.sum())
    room = hi - lo
    room_sum = float(room.sum())
    x = lo.copy() if room_sum <= 0 else lo + remaining * (room / room_sum)
    return {ch: float(x[i]) for i, ch in enumerate(channels)}


def _curve_frame(provider: MetricsJsonCurveProvider) -> pd.DataFrame:
    rows = [
        {
            "channel": ch,
            "spend": float(spend),
            "incremental_kpi": float(kpi),
        }
        for ch in provider.channels()
        for spend, kpi in zip(provider.spend_grid(ch), provider.mean_grid(ch))
    ]
    return pd.DataFrame(rows)


def _bar_frame(
    provider: MetricsJsonCurveProvider,
    baseline: dict[str, float],
    optimized: dict[str, float],
) -> pd.DataFrame:
    rows: list[dict] = []
    for ch in baseline:
        for label, spends in (("baseline", baseline), ("optimized", optimized)):
            sp = float(spends[ch])
            rows.append(
                {
                    "channel": ch,
                    "allocation": label,
                    "spend": sp,
                    "incremental_kpi": float(provider.incremental_kpi(ch, sp)),
                }
            )
    return pd.DataFrame(rows)


# --- Figures ---


def build_curves_figure(provider: MetricsJsonCurveProvider, title: str):
    return px.line(
        _curve_frame(provider),
        x="spend",
        y="incremental_kpi",
        color="channel",
        markers=True,
        title=title,
        labels={"spend": "Spend", "incremental_kpi": "Incremental KPI"},
    )


def write_allocation_bars(bar_df: pd.DataFrame, title: str, out: Path) -> None:
    spend_fig = px.bar(
        bar_df,
        x="channel",
        y="spend",
        color="allocation",
        barmode="group",
        labels={"spend": "Spend", "channel": "Channel"},
    )
    kpi_fig = px.bar(
        bar_df,
        x="channel",
        y="incremental_kpi",
        color="allocation",
        barmode="group",
        labels={"incremental_kpi": "Incremental KPI", "channel": "Channel"},
    )
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Spend: baseline vs optimized", "KPI contribution by channel"),
        vertical_spacing=0.12,
    )
    for tr in spend_fig.data:
        fig.add_trace(tr, row=1, col=1)
    for tr in kpi_fig.data:
        fig.add_trace(tr.update(showlegend=False), row=2, col=1)
    fig.update_layout(
        title_text=title,
        barmode="group",
        height=720,
        legend_title_text="allocation",
    )
    fig.update_yaxes(title_text="Spend", row=1, col=1)
    fig.update_yaxes(title_text="Incremental KPI", row=2, col=1)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(out, include_plotlyjs="cdn")


# --- CLI ---


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="STORY-301 allocation teaching plots")
    p.add_argument("--curves", type=Path, default=DEFAULT_CURVES)
    p.add_argument("--budget", type=float, default=DEFAULT_BUDGET)
    p.add_argument("--min-spend", type=float, default=DEFAULT_MIN)
    p.add_argument("--max-spend", type=float, default=DEFAULT_MAX)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    provider = MetricsJsonCurveProvider(args.curves)
    channels = list(provider.channels())

    result = optimize_budget(
        provider,
        total_budget=args.budget,
        min_spend=args.min_spend,
        max_spend=args.max_spend,
        curve_source=str(args.curves),
    )
    if not result["solver"]["success"]:
        print(result["solver"]["message"], file=sys.stderr)
        return 1

    optimized = {ch: float(result["channels"][ch]) for ch in channels}
    baseline = _equal_room_baseline(
        channels, args.budget, args.min_spend, args.max_spend
    )

    src = args.curves.name
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    curves_fig = build_curves_figure(
        provider,
        f"STORY-301 response curves ({src})",
    )
    curves_fig.write_html(CURVES_OUT, include_plotlyjs="cdn")
    print(f"Wrote {CURVES_OUT}")

    write_allocation_bars(
        _bar_frame(provider, baseline, optimized),
        f"STORY-301 allocation vs baseline ({src}, budget={args.budget:g})",
        BARS_OUT,
    )
    print(f"Wrote {BARS_OUT}")

    delta = result.get("incremental_kpi_delta_vs_baseline")
    print(
        f"optimized KPI={result['expected_incremental_kpi']:.6g} "
        f"delta_vs_baseline={delta}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
