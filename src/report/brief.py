"""C-suite brief (STORY-302 Steps 2–3).

Builds a system+user prompt from the fact pack only (allocation JSON, not
CSVs). ``render_offline`` fills the brief locally. ``render_live`` asks
Anthropic to call ``emit_brief`` and then locks the numbers to the fact pack.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError

from src.report.facts import numbers_match
from src.report.schema import CsuiteBrief, emit_brief_json_schema

# --- Live call defaults ---

DEFAULT_MODEL = "claude-sonnet-4-5"
_TOOL_NAME = "emit_brief"
_SECRET = Path(__file__).resolve().parents[2] / "Secret" / "anthropic_api_key"
_MISSING_KEY = "Set ANTHROPIC_API_KEY or put one line in Secret/anthropic_api_key"

# --- Caveats (always on the brief) ---

CAVEAT_KPI = "Numbers are incremental KPI, not revenue dollars."
CAVEAT_RANK = (
    "Meridian channel rank vs Path-C is still an open issue — "
    "do not treat this as Path-C ground truth."
)

_SYSTEM = f"""You write a short C-suite budget brief from a fact pack.

Use only the fact pack in the user message. Do not read media CSVs or invent spends or KPI.
Fill: headline, 3 to 6 bullets, shifts (one per channel), predicted_incremental_kpi, incremental_kpi_delta_vs_baseline, caveats.
Bullets must cover budget shifts, saturation flags (near_ceiling, at_floor, or ok), and predicted KPI lift.
If incremental_kpi_delta_vs_baseline is null, say the lift vs baseline was not computed. Do not invent a lift.
Caveats must include: {CAVEAT_KPI}
Caveats must include: {CAVEAT_RANK}
"""


# --- Prompt ---


def build_messages(fact_pack: Mapping[str, Any]) -> dict[str, str]:
    """System and user prompt. The user turn is the fact pack JSON only."""
    user = (
        "Write the brief from this fact pack only.\n"
        + json.dumps(fact_pack, indent=2)
    )
    return {"system": _SYSTEM, "user": user}


# --- Offline renderer ---


def render_offline(fact_pack: Mapping[str, Any]) -> CsuiteBrief:
    """Fill the brief from the fact pack and refuse it if numbers drift."""
    channels = fact_pack.get("channels") or {}
    if not channels:
        raise ValueError("no brief: channels is empty")

    kpi = fact_pack.get("expected_incremental_kpi")
    if kpi is None:
        raise ValueError("no brief: expected_incremental_kpi is null")
    delta = fact_pack.get("incremental_kpi_delta_vs_baseline")

    shifts = [
        {
            "channel": ch,
            "baseline_spend": row["baseline_spend"],
            "recommended_spend": row["recommended_spend"],
            "spend_delta": row["spend_delta"],
            "saturation_flag": row["saturation_flag"],
        }
        for ch, row in channels.items()
    ]
    bullets = [
        _shift_bullet(channels),
        _saturation_bullet(channels),
        _lift_bullet(float(kpi), delta),
    ]
    note = fact_pack.get("concentration_note")
    if note:
        bullets.append(str(note))

    brief = CsuiteBrief(
        headline=_headline(channels),
        bullets=bullets,
        shifts=shifts,
        predicted_incremental_kpi=float(kpi),
        incremental_kpi_delta_vs_baseline=None if delta is None else float(delta),
        caveats=[CAVEAT_KPI, CAVEAT_RANK],
    )
    if not numbers_match(fact_pack, brief):
        raise RuntimeError("brief numbers do not match the fact pack")
    return brief


def format_brief(brief: CsuiteBrief) -> str:
    """Plain-text brief for the terminal."""
    lines = [brief.headline, ""]
    lines.extend(f"- {bullet}" for bullet in brief.bullets)
    lines.append("")
    lines.append("Shifts:")
    for shift in brief.shifts:
        lines.append(
            f"  {shift.channel}  baseline {shift.baseline_spend:g}  "
            f"recommended {shift.recommended_spend:g}  "
            f"delta {shift.spend_delta:+g}  {shift.saturation_flag}"
        )
    delta = brief.incremental_kpi_delta_vs_baseline
    delta_txt = "not computed" if delta is None else f"{delta:+.6g}"
    lines.extend(
        [
            "",
            f"Predicted incremental KPI: {brief.predicted_incremental_kpi}",
            f"Lift vs baseline: {delta_txt}",
            "",
            "Caveats:",
            *(f"- {caveat}" for caveat in brief.caveats),
        ]
    )
    return "\n".join(lines)


# --- Sentence builders ---


def _headline(channels: Mapping[str, Mapping[str, Any]]) -> str:
    channel, row = max(
        channels.items(),
        key=lambda item: abs(float(item[1]["spend_delta"])),
    )
    delta = float(row["spend_delta"])
    if delta > 0:
        direction = "up"
    elif delta < 0:
        direction = "down"
    else:
        direction = "unchanged"
    return (
        f"Move {channel} {direction}: {float(row['recommended_spend']):g} "
        f"vs baseline {float(row['baseline_spend']):g}."
    )


def _shift_bullet(channels: Mapping[str, Mapping[str, Any]]) -> str:
    parts = [
        (
            f"{ch} {float(row['baseline_spend']):g} → "
            f"{float(row['recommended_spend']):g} ({float(row['spend_delta']):+g})"
        )
        for ch, row in channels.items()
    ]
    return "Budget shift: " + "; ".join(parts) + "."


def _saturation_bullet(channels: Mapping[str, Mapping[str, Any]]) -> str:
    parts = [f"{ch} {row['saturation_flag']}" for ch, row in channels.items()]
    return "Saturation: " + ", ".join(parts) + "."


def _lift_bullet(kpi: float, delta: Any) -> str:
    if delta is None:
        return (
            f"Expected incremental KPI is {kpi:g}. "
            "Lift vs baseline was not computed."
        )
    return f"Predicted incremental KPI is {kpi:g}, lift vs baseline {float(delta):+.6g}."


# --- Live Anthropic path ---


class MissingApiKey(RuntimeError):
    """Raised when neither the env var nor the secret file has a key."""


def load_api_key(secret_path: Path | None = None) -> str:
    """Env ``ANTHROPIC_API_KEY``, else the first line of the secret file.

    The returned string is the key. Callers must not print it.
    """
    env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env:
        return env
    path = secret_path if secret_path is not None else _SECRET
    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        line = text.splitlines()[0].strip() if text else ""
        if line:
            return line
    raise MissingApiKey(_MISSING_KEY)


def render_live(
    fact_pack: Mapping[str, Any],
    *,
    client: Any,
    model: str = DEFAULT_MODEL,
) -> CsuiteBrief:
    """Force the ``emit_brief`` tool, validate, then lock numbers.

    Raises ``ValueError`` on a missing tool call or schema failure, and
    ``RuntimeError`` when ``numbers_match`` fails. Does not write a file.
    """
    messages = build_messages(fact_pack)
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=messages["system"],
        messages=[{"role": "user", "content": messages["user"]}],
        tools=[
            {
                "name": _TOOL_NAME,
                "description": "Emit the C-suite brief using only fact-pack numbers.",
                "input_schema": emit_brief_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": _TOOL_NAME},
    )
    payload = _tool_input(response)
    try:
        brief = CsuiteBrief.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"emit_brief schema failed: {exc}") from exc
    if not numbers_match(fact_pack, brief):
        raise RuntimeError("brief numbers do not match the fact pack")
    return brief


def _tool_input(response: Any) -> Mapping[str, Any]:
    for block in getattr(response, "content", None) or []:
        if _field(block, "type") != "tool_use" or _field(block, "name") != _TOOL_NAME:
            continue
        raw = _field(block, "input")
        if isinstance(raw, str):
            raw = json.loads(raw)
        if isinstance(raw, Mapping):
            return raw
    raise ValueError("emit_brief tool call missing")


def _field(block: Any, name: str) -> Any:
    if isinstance(block, Mapping):
        return block.get(name)
    return getattr(block, name, None)
