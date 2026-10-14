"""STORY-401 dashboard view (min/max bounds + optimizer, no Streamlit)."""

from src.dashboard.view import (
    build_dashboard,
    clamp_max_percent,
    clamp_min_percent,
    clamp_percents,
    default_curves_path,
    partner_investments,
    slider_bounds,
)

__all__ = [
    "build_dashboard",
    "clamp_max_percent",
    "clamp_min_percent",
    "clamp_percents",
    "default_curves_path",
    "partner_investments",
    "slider_bounds",
]
