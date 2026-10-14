"""STORY-401 Streamlit layout.

Sliders and number boxes set the percent mix and the charts. **Update
insights** is the only control that calls Claude. Run with ``streamlit run app.py``.
"""

from __future__ import annotations

import html
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
    clamp_percent,
    default_curves_path,
    equal_percents,
    format_units,
    slider_bounds,
)
from src.report.brief import format_brief, load_api_key, render_live  # noqa: E402

_SECRET_RE = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
_NUMBER_RE = re.compile(r"[+-]?\d+(?:\.\d+)?")


# --- Redaction ---


def _redact(text: str, secret: str | None) -> str:
    if secret:
        text = text.replace(secret, "[redacted]")
    return _SECRET_RE.sub("[redacted]", text)


def _synced_number(
    label: str,
    lo: float,
    hi: float,
    default: float,
    step: float,
    key: str,
    fmt: str,
    clamp=None,
) -> float:
    """Slider and number box on one session value. ``clamp`` runs on each edit."""
    slider_key = f"{key}::s"
    number_key = f"{key}::n"
    if slider_key not in st.session_state:
        st.session_state[slider_key] = float(default)
        st.session_state[number_key] = float(default)

    def _store(raw: float) -> None:
        value = float(raw)
        if clamp is not None:
            value = float(clamp(value))
        st.session_state[slider_key] = value
        st.session_state[number_key] = value

    def _from_slider() -> None:
        _store(st.session_state[slider_key])

    def _from_number() -> None:
        _store(st.session_state[number_key])

    st.sidebar.slider(
        label,
        min_value=float(lo),
        max_value=float(hi),
        step=float(step),
        format=fmt,
        key=slider_key,
        on_change=_from_slider,
    )
    # number_input uses Python %, which rejects a thousands-separator flag.
    number_fmt = "%.2f" if "," in fmt else fmt
    st.sidebar.number_input(
        label,
        min_value=float(lo),
        max_value=float(hi),
        step=float(step),
        format=number_fmt,
        key=number_key,
        on_change=_from_number,
    )
    return float(st.session_state[number_key])


# --- Pure CSS (CDN from the Pure start page; widgets stay Streamlit) ---

_PURE_CSS = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/pure-min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/grids-responsive-min.css">
<style>
.stApp, [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
  background: #fff;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
[data-testid="stSidebar"] { border-right: 1px solid #ddd; }
[data-testid="stSlider"],
.pure-menu-heading,
.pure-menu + p { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
button[data-testid="stBaseButton-secondary"] {
  background: #1f8dd6;
  color: #fff;
  border: 1px solid #1f8dd6;
  border-radius: 2px;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
.brief-card {
  padding: .5em 1em;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: inset 0 1px 3px #ddd;
  background: #fff;
}
.brief-card pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
</style>
<div class="pure-menu pure-menu-horizontal">
<span class="pure-menu-heading">Budget dashboard</span>
</div>
<p>Numbers are incremental KPI, not revenue. Meridian channel rank vs Path-C is still an open issue.</p>
"""


def _commentary(text: str) -> None:
    shown = _NUMBER_RE.sub(lambda match: format_units(float(match.group(0))), text)
    st.markdown(
        '<div class="pure-g"><div class="pure-u-1"><div class="brief-card"><pre>'
        + html.escape(shown)
        + "</pre></div></div></div>",
        unsafe_allow_html=True,
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
    st.markdown(_PURE_CSS, unsafe_allow_html=True)
    st.sidebar.caption(
        "Percents set the mix. Update insights calls Claude."
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

    budget = _synced_number(
        "Total budget",
        spec["budget_min"],
        spec["budget_max"],
        spec["budget_default"],
        0.01,
        key=f"budget::{curves_path}",
        fmt="%,.2f",
    )
    partners = list(spec["channels"])
    defaults = equal_percents(partners)
    for channel in partners:
        slider_key = f"pct::{curves_path}::{channel}::s"
        if slider_key not in st.session_state:
            st.session_state[slider_key] = float(defaults[channel])
            st.session_state[f"pct::{curves_path}::{channel}::n"] = float(defaults[channel])

    percents: dict[str, float] = {}
    for channel in partners:
        def _room(requested: float, channel: str = channel) -> float:
            others = sum(
                float(st.session_state[f"pct::{curves_path}::{other}::n"])
                for other in partners
                if other != channel
            )
            return clamp_percent(requested, others)

        percents[channel] = _synced_number(
            f"{channel} %",
            0.0,
            100.0,
            defaults[channel],
            0.01,
            key=f"pct::{curves_path}::{channel}",
            fmt="%.2f",
            clamp=_room,
        )
        st.sidebar.caption(
            f"{channel} investment {format_units(budget * percents[channel] / 100.0)}"
        )
    st.sidebar.caption(f"Unallocated {100.0 - sum(percents.values()):.2f}%")

    signature = (
        str(path),
        float(budget),
        tuple((channel, percents[channel]) for channel in partners),
    )
    if st.session_state.get("slider_sig") != signature:
        st.session_state["live_brief"] = None
        st.session_state["live_error"] = None
        st.session_state["slider_sig"] = signature

    try:
        result = build_dashboard(path, budget, percents)
    except (OSError, ValueError) as exc:
        st.error(str(exc))
        return

    if result["error"]:
        st.error(result["error"])
        return

    st.subheader("Allocation")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "channel": row["channel"],
                    "percent": f"{row['percent']:.2f}",
                    "investment": format_units(row["recommended_spend"]),
                    "saturation_flag": row["saturation_flag"],
                    "incremental_kpi": format_units(row["incremental_kpi"]),
                }
                for row in result["rows"]
            ]
        ),
        hide_index=True,
    )
    lift = result["lift_vs_baseline"]
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "expected_incremental_kpi": format_units(
                        result["expected_incremental_kpi"]
                    ),
                    "lift_vs_baseline": "" if lift is None else format_units(lift),
                }
            ]
        ),
        hide_index=True,
    )
    st.caption(
        "Incremental KPI is units, not dollars, euros, or revenue. "
        "Spend is the curve file’s spend units, not a currency."
    )
    st.plotly_chart(result["response_figure"], width="stretch")
    st.plotly_chart(result["saturation_figure"], width="stretch")
    st.plotly_chart(result["spend_move_figure"], width="stretch")
    st.plotly_chart(result["kpi_move_figure"], width="stretch")
    st.caption("The Update insights button does not change these numbers.")

    st.subheader("Commentary")
    _commentary(result["offline_brief"])
    if st.button("Update insights"):
        _update_insights(result["fact_pack"])
    if st.session_state.get("live_brief"):
        st.subheader("Live insights")
        _commentary(st.session_state["live_brief"])
    if st.session_state.get("live_error"):
        st.error(st.session_state["live_error"])


if __name__ == "__main__":
    main()
