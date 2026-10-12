"""STORY-301 Step 0 — toy diminishing-returns curve (not Meridian, not optimizer).

Usage (from repo root, conda env ``mmt-mmm``)::

    python scripts/plot_budget_opt_toy.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px

# --- Paths / synthetic curve ---

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "reports" / "figures" / "story_301_toy_diminishing_returns.html"

spend = np.linspace(0, 100, 51)
# Classic concave response: lift grows fast then flattens (toy only)
kpi = 80.0 * (1.0 - np.exp(-spend / 35.0))
df = pd.DataFrame({"spend": spend, "incremental_kpi": kpi})

fig = px.line(
    df,
    x="spend",
    y="incremental_kpi",
    title="Toy diminishing returns (synthetic — not Meridian fit)",
    labels={"spend": "Spend ($)", "incremental_kpi": "Incremental KPI"},
)
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(OUT, include_plotlyjs="cdn")
print(f"Wrote {OUT}")
