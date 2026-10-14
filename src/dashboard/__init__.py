"""STORY-401 dashboard view (percent mix + Plotly, no Streamlit)."""

from src.dashboard.view import (
    build_dashboard,
    clamp_percents,
    default_curves_path,
    equal_percents,
    partner_investments,
    slider_bounds,
)

__all__ = [
    "build_dashboard",
    "clamp_percents",
    "default_curves_path",
    "equal_percents",
    "partner_investments",
    "slider_bounds",
]
