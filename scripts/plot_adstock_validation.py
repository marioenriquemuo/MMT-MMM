"""Plotly Express validation for geometric + Weibull adstock (STORY-102).

Pulse of 100 on day 0, zeros after. Writes:

* ``reports/figures/geometric_adstock_pulse.html`` — two geometric thetas
* ``reports/figures/weibull_adstock_pulse.html`` — two Weibull shapes
  (plus optional geometric reference on the same pulse)

Adapted from the Jupyter DoD — plain script, no notebook required.

Usage (from repo root, conda env ``mmt-mmm``)::

    python scripts/plot_adstock_validation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- Paths / constants ---

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import plotly.express as px

from src.models.transformations import geometric_adstock, weibull_adstock

FIG_DIR = REPO_ROOT / "reports" / "figures"
GEOMETRIC_OUT = FIG_DIR / "geometric_adstock_pulse.html"
WEIBULL_OUT = FIG_DIR / "weibull_adstock_pulse.html"
N_DAYS = 30
PULSE = 100.0
THETAS = (0.3, 0.7)
# shape < 1 → peak at lag 0; shape > 1 → delayed peak
WEIBULL_SHAPES = (
    (0.7, 5.0, "Weibull k=0.7, λ=5 (peak @ day 0)"),
    (2.2, 5.0, "Weibull k=2.2, λ=5 (delayed peak)"),
)
GEOMETRIC_REF_THETA = 0.5


def _pulse_frame() -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    x = np.zeros(N_DAYS)
    x[0] = PULSE
    days = np.arange(N_DAYS)
    raw = pd.DataFrame(
        {
            "day": days,
            "value": x,
            "series": "raw pulse (100 @ t=0)",
        }
    )
    return x, days, raw


def build_geometric_figure():
    """Impulse response for two geometric thetas."""
    x, days, raw = _pulse_frame()
    frames: list[pd.DataFrame] = [raw]
    for theta in THETAS:
        y = geometric_adstock(x, theta)
        frames.append(
            pd.DataFrame(
                {
                    "day": days,
                    "value": y,
                    "series": f"geometric θ={theta}",
                }
            )
        )

    df = pd.concat(frames, ignore_index=True)
    fig = px.line(
        df,
        x="day",
        y="value",
        color="series",
        markers=True,
        title="Geometric adstock pulse response (STORY-102)",
        labels={"day": "Day", "value": "Exposure", "series": "Series"},
    )
    fig.update_layout(template="plotly_white", legend_title_text="")
    return fig


def build_weibull_figure():
    """Impulse response for two Weibull shapes + geometric reference."""
    x, days, raw = _pulse_frame()
    frames: list[pd.DataFrame] = [raw]

    y_geo = geometric_adstock(x, GEOMETRIC_REF_THETA)
    frames.append(
        pd.DataFrame(
            {
                "day": days,
                "value": y_geo,
                "series": f"geometric θ={GEOMETRIC_REF_THETA} (reference)",
            }
        )
    )

    for shape, scale, label in WEIBULL_SHAPES:
        y = weibull_adstock(x, shape=shape, scale=scale, normalize=True)
        frames.append(
            pd.DataFrame(
                {
                    "day": days,
                    "value": y,
                    "series": label,
                }
            )
        )

    df = pd.concat(frames, ignore_index=True)
    fig = px.line(
        df,
        x="day",
        y="value",
        color="series",
        markers=True,
        title="Weibull adstock pulse response (STORY-102 Step 3)",
        labels={"day": "Day", "value": "Exposure", "series": "Series"},
    )
    fig.update_layout(template="plotly_white", legend_title_text="")
    return fig


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    geo = build_geometric_figure()
    geo.write_html(str(GEOMETRIC_OUT), include_plotlyjs="cdn")
    print(f"Wrote {GEOMETRIC_OUT}")

    weib = build_weibull_figure()
    weib.write_html(str(WEIBULL_OUT), include_plotlyjs="cdn")
    print(f"Wrote {WEIBULL_OUT}")


if __name__ == "__main__":
    main()
