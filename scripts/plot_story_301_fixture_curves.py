"""STORY-301 Step 1 — Plotly Express of synthetic fixture response curves.

Usage (from repo root, conda env ``mmt-mmm``)::

    python scripts/plot_story_301_fixture_curves.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import plotly.express as px

from src.optimize.curves import MetricsJsonCurveProvider

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "synthetic_response_curves.json"
OUT = REPO_ROOT / "reports" / "figures" / "story_301_fixture_curves.html"


def main() -> None:
    provider = MetricsJsonCurveProvider(FIXTURE)
    rows: list[dict] = []
    for ch in provider.channels():
        for spend, kpi in zip(provider.spend_grid(ch), provider.mean_grid(ch)):
            rows.append(
                {
                    "channel": ch,
                    "spend": float(spend),
                    "incremental_kpi": float(kpi),
                }
            )
    df = pd.DataFrame(rows)
    fig = px.line(
        df,
        x="spend",
        y="incremental_kpi",
        color="channel",
        markers=True,
        title="STORY-301 fixture response curves (synthetic — not Meridian)",
        labels={"spend": "Spend", "incremental_kpi": "Incremental KPI"},
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(OUT, include_plotlyjs="cdn")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
