"""STORY-302 Step 0 — Plotly Express teaching plots for a C-suite brief.

Three ideas, three HTML files under ``reports/figures/``:

* ``story_302_budget_shifts.html`` — equal-room baseline spend vs a recommended mix
* ``story_302_saturation.html`` — spend as % of max, with a 90% near-ceiling line
* ``story_302_kpi_lift.html`` — baseline vs recommended incremental KPI (lift = difference)

The recommended mix is hardcoded. On this fixture SLSQP stays on the equal-room
point (a kink in the piecewise-linear curves), so a fixed shift is what makes
the move visible. Spends stay inside budget 60 and bounds [5, 30].

KPI uses ``MetricsJsonCurveProvider.incremental_kpi`` (linear interpolation).

Usage (repo root, conda env ``mmt-mmm``)::

    python scripts/plot_story_302_concepts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.optimize.curves import MetricsJsonCurveProvider  # noqa: E402

# --- Paths / teaching constants ---

FIG_DIR = REPO_ROOT / "reports" / "figures"
SHIFTS_OUT = FIG_DIR / "story_302_budget_shifts.html"
SATURATION_OUT = FIG_DIR / "story_302_saturation.html"
KPI_OUT = FIG_DIR / "story_302_kpi_lift.html"
CURVES = REPO_ROOT / "tests" / "fixtures" / "synthetic_response_curves.json"

BUDGET = 60.0
MIN_SPEND = 5.0
MAX_SPEND = 30.0
# Differs from equal-room (20/20/20). Alpha sits on the 90% ceiling line.
RECOMMENDED = {"alpha": 27.0, "beta": 18.0, "gamma": 15.0}
NEAR_CEILING_PCT = 90.0


# --- Baseline + frames ---


def _equal_room_baseline(channels: list[str]) -> dict[str, float]:
    """Same fill as allocator._feasible_start: mins, then leftover proportional to room."""
    n = len(channels)
    lo = MIN_SPEND
    hi = MAX_SPEND
    remaining = BUDGET - lo * n
    room = hi - lo
    each = lo + remaining * (room / (room * n))
    return {ch: float(each) for ch in channels}


def _kpi(provider: MetricsJsonCurveProvider, spends: dict[str, float]) -> float:
    return float(sum(provider.incremental_kpi(ch, sp) for ch, sp in spends.items()))


def _long_frame(
    baseline: dict[str, float],
    recommended: dict[str, float],
) -> pd.DataFrame:
    rows = []
    for plan, spends in (("baseline", baseline), ("recommended", recommended)):
        for ch, spend in spends.items():
            rows.append(
                {
                    "channel": ch,
                    "plan": plan,
                    "spend": spend,
                    "pct_of_max": 100.0 * spend / MAX_SPEND,
                }
            )
    return pd.DataFrame(rows)


# --- Figures ---


def _write(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn")
    print(f"Wrote {path}")
    print(f"  xdg-open {path}")


def main() -> int:
    provider = MetricsJsonCurveProvider(CURVES)
    channels = [ch for ch in ("alpha", "beta", "gamma") if ch in provider.channels()]
    if channels != ["alpha", "beta", "gamma"]:
        print(f"fixture channels {provider.channels()} != alpha/beta/gamma", file=sys.stderr)
        return 1

    baseline = _equal_room_baseline(channels)
    recommended = {ch: float(RECOMMENDED[ch]) for ch in channels}
    if abs(sum(recommended.values()) - BUDGET) > 1e-6:
        print("recommended mix does not sum to budget", file=sys.stderr)
        return 1
    if baseline == recommended:
        print("baseline equals recommended; teaching shift is invisible", file=sys.stderr)
        return 1

    frame = _long_frame(baseline, recommended)
    base_kpi = _kpi(provider, baseline)
    rec_kpi = _kpi(provider, recommended)
    delta = rec_kpi - base_kpi

    shifts = px.bar(
        frame,
        x="channel",
        y="spend",
        color="plan",
        barmode="group",
        title="Budget shift: equal-room baseline vs recommended spend",
        labels={"spend": "Spend", "channel": "Channel"},
    )
    _write(shifts, SHIFTS_OUT)

    saturation = px.bar(
        frame,
        x="channel",
        y="pct_of_max",
        color="plan",
        barmode="group",
        title="Saturation: spend as % of max (30). Line = near-ceiling flag (90%)",
        labels={"pct_of_max": "% of max spend", "channel": "Channel"},
    )
    saturation.add_hline(
        y=NEAR_CEILING_PCT,
        line_dash="dash",
        annotation_text="near ceiling 90%",
    )
    _write(saturation, SATURATION_OUT)

    kpi_frame = pd.DataFrame(
        [
            {"plan": "baseline", "incremental_kpi": base_kpi},
            {"plan": "recommended", "incremental_kpi": rec_kpi},
        ]
    )
    kpi = px.bar(
        kpi_frame,
        x="plan",
        y="incremental_kpi",
        text="incremental_kpi",
        title=f"Predicted lift = recommended − baseline ({delta:+.6g})",
        labels={"incremental_kpi": "Incremental KPI", "plan": "Plan"},
    )
    kpi.update_traces(texttemplate="%{text:.4g}", textposition="outside")
    _write(kpi, KPI_OUT)

    print(
        f"baseline_spends={baseline} recommended_spends={recommended} "
        f"baseline_kpi={base_kpi:.6g} recommended_kpi={rec_kpi:.6g} kpi_delta={delta:.6g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
