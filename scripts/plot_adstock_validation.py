"""Plotly Express validation for geometric adstock (STORY-102 Step 2).

Pulse of 100 on day 0, zeros after; overlay two theta curves.
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

from src.models.transformations import geometric_adstock

OUT_PATH = REPO_ROOT / "reports" / "figures" / "geometric_adstock_pulse.html"
N_DAYS = 30
PULSE = 100.0
THETAS = (0.3, 0.7)


def build_figure():
    """Impulse response for two geometric thetas."""
    x = np.zeros(N_DAYS)
    x[0] = PULSE
    days = np.arange(N_DAYS)

    frames: list[pd.DataFrame] = [
        pd.DataFrame(
            {
                "day": days,
                "value": x,
                "series": "raw pulse (100 @ t=0)",
            }
        )
    ]
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


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    fig.write_html(str(OUT_PATH), include_plotlyjs="cdn")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
