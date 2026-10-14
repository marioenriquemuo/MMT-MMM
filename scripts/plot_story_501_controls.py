"""STORY-501 teaching figure: one month of date-level controls.

Writes ``reports/figures/story_501_control_flags.html``.

Usage (from repo root, conda env ``mmt-mmm``)::

    python scripts/plot_story_501_controls.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import plotly.express as px

from src.data.controls import DEFAULT_PANEL_PATH, build_controls

FIG_PATH = REPO_ROOT / "reports" / "figures" / "story_501_control_flags.html"
MONTH_START = "2023-07-01"
MONTH_END = "2023-07-31"
SERIES = ("quincena_flag", "holiday_flag", "organic_seo_clicks")


def build_figure():
    """July 2023: quincena, holiday, and organic clicks on the same dates."""
    controls = build_controls(DEFAULT_PANEL_PATH)
    month = controls.loc[
        pd.to_datetime(controls["date"]).between(MONTH_START, MONTH_END)
    ].copy()
    if len(month) != 31:
        raise AssertionError(f"expected 31 days in July 2023, got {len(month)}")
    long = month.melt(
        id_vars="date",
        value_vars=list(SERIES),
        var_name="series",
        value_name="value",
    )
    long["series"] = pd.Categorical(long["series"], categories=SERIES, ordered=True)
    fig = px.line(
        long,
        x="date",
        y="value",
        facet_row="series",
        markers=True,
        title="These are date-level controls, not channel spend",
        labels={"date": "Date", "value": "Value", "series": "Control"},
    )
    fig.update_yaxes(matches=None)
    fig.update_layout(template="plotly_white", height=720)
    fig.for_each_annotation(lambda ann: ann.update(text=ann.text.split("=")[-1]))
    return fig


def main() -> None:
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    build_figure().write_html(str(FIG_PATH), include_plotlyjs="cdn")
    print(f"Wrote {FIG_PATH}")


if __name__ == "__main__":
    main()
