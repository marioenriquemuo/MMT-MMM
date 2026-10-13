"""STORY-401 Streamlit layout.

Sliders rerun the local allocator and charts. **Update insights** is the
only control that calls Claude. Run with ``streamlit run app.py``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.dashboard.view import (  # noqa: E402
    build_dashboard,
    default_curves_path,
    slider_bounds,
)
from src.report.brief import format_brief, load_api_key, render_live  # noqa: E402

_SECRET_RE = re.compile(r"sk-[A-Za-z0-9_-]{8,}")


# --- Redaction ---


def _redact(text: str, secret: str | None) -> str:
    if secret:
        text = text.replace(secret, "[redacted]")
    return _SECRET_RE.sub("[redacted]", text)


def _slider(label: str, lo: float, hi: float, default: float, step: float, key: str) -> float:
    lo_f, hi_f = float(lo), float(hi)
    if hi_f <= lo_f:
        st.sidebar.caption(f"{label}: {lo_f:g}")
        return lo_f
    step_f = float(step) if step and step > 0 else (hi_f - lo_f) / 100.0
    value = min(max(float(default), lo_f), hi_f)
    return float(
        st.sidebar.slider(
            label,
            min_value=lo_f,
            max_value=hi_f,
            value=value,
            step=step_f,
            key=key,
        )
    )


# --- Layout ---


def _update_insights(fact_pack: dict) -> None:
    secret: str | None = None
    try:
        secret = load_api_key()
        import anthropic

        client = anthropic.Anthropic(api_key=secret)
        brief = render_live(fact_pack, client=client)
        st.session_state["live_brief"] = format_brief(brief)
        st.session_state["live_error"] = None
    except Exception as exc:
        # Broad catch: an API error can echo the key. Show only the redacted text.
        st.session_state["live_brief"] = None
        st.session_state["live_error"] = _redact(f"{type(exc).__name__}: {exc}", secret)


def main() -> None:
    st.set_page_config(page_title="Budget dashboard", layout="wide")
    st.title("Budget dashboard")
    st.caption(
        "Numbers are incremental KPI, not revenue. "
        "Meridian channel rank vs Path-C is still an open issue."
    )
    st.sidebar.caption(
        "Sliders rerun the local allocator. Update insights calls Claude."
    )

    curves_path = st.sidebar.text_input(
        "Curve file",
        value=str(default_curves_path(REPO_ROOT)),
    )
    path = Path(curves_path)
    if not path.is_file():
        st.error(f"Curve file not found: {path}")
        return
    try:
        spec = slider_bounds(path)
    except (OSError, ValueError) as exc:
        st.error(str(exc))
        return

    budget = _slider(
        "Total budget",
        spec["budget_min"],
        spec["budget_max"],
        spec["budget_default"],
        spec["budget_step"],
        key=f"budget::{curves_path}",
    )
    mins: dict[str, float] = {}
    maxes: dict[str, float] = {}
    for channel, bounds in spec["channels"].items():
        mins[channel] = _slider(
            f"{channel} min",
            bounds["min"],
            bounds["max"],
            bounds["min"],
            bounds["step"],
            key=f"min::{curves_path}::{channel}",
        )
        maxes[channel] = _slider(
            f"{channel} max",
            bounds["min"],
            bounds["max"],
            bounds["max"],
            bounds["step"],
            key=f"max::{curves_path}::{channel}",
        )

    signature = (
        str(path),
        float(budget),
        tuple((channel, mins[channel], maxes[channel]) for channel in spec["channels"]),
    )
    if st.session_state.get("slider_sig") != signature:
        st.session_state["live_brief"] = None
        st.session_state["live_error"] = None
        st.session_state["slider_sig"] = signature

    try:
        result = build_dashboard(path, budget, mins, maxes)
    except (OSError, ValueError) as exc:
        st.error(str(exc))
        return

    if result["error"]:
        st.error(result["error"])
        return

    st.subheader("Allocation")
    st.dataframe(pd.DataFrame(result["rows"]), hide_index=True)
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "expected_incremental_kpi": result["expected_incremental_kpi"],
                    "lift_vs_baseline": result["lift_vs_baseline"],
                }
            ]
        ),
        hide_index=True,
    )
    st.plotly_chart(result["response_figure"], width="stretch")
    st.plotly_chart(result["saturation_figure"], width="stretch")

    st.subheader("Commentary")
    st.text(result["offline_brief"])
    if st.button("Update insights"):
        _update_insights(result["fact_pack"])
    if st.session_state.get("live_brief"):
        st.subheader("Live insights")
        st.text(st.session_state["live_brief"])
    if st.session_state.get("live_error"):
        st.error(st.session_state["live_error"])


if __name__ == "__main__":
    main()
