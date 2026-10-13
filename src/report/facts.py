"""Fact pack for a C-suite brief (STORY-302 Step 1).

Reads an allocation plan (``optimize_budget`` / ``allocation.json``) and
recomputes the equal-room baseline. Does not call a model and does not
recompute KPI — those two fields are copied from the plan.
"""

from __future__ import annotations

import math
import re
from typing import Any, Mapping

import numpy as np

# --- Thresholds (match the teaching charts) ---

_NEAR_CEILING = 0.90
_FLOOR_TOL = 1e-6
_CONCENTRATION = 0.70
_NUMBER_TOL = 1e-6
_PROSE_TOL = 1e-4
_NUMBER_TOKEN = re.compile(r"[+-]?(?:\d+\.\d+|\d+)%?")


# --- Public API ---


def build_fact_pack(allocation: Mapping[str, Any]) -> dict[str, Any]:
    """Channel shifts, saturation flags, and copied KPI fields.

    Raises ``ValueError`` when ``solver.success`` is false or ``channels``
    is empty — callers get no partial pack.
    """
    solver = allocation.get("solver") or {}
    channels = allocation.get("channels") or {}
    message = str(solver.get("message") or "")
    if not solver.get("success") or not channels:
        raise ValueError(
            "no fact pack: solver.success is false or channels is empty"
            + (f" ({message})" if message else "")
        )
    if not isinstance(channels, Mapping):
        raise ValueError("no fact pack: channels must be a mapping of spend")

    constraints = allocation.get("constraints") or {}
    order = list(constraints.get("channels") or channels.keys())
    missing = [ch for ch in order if ch not in channels]
    if missing:
        raise ValueError(f"no fact pack: constraints.channels missing spends for {missing}")

    budget = constraints.get("total_budget")
    if budget is None:
        budget = allocation.get("total_spend")
    if budget is None:
        raise ValueError("no fact pack: need constraints.total_budget or total_spend")
    budget_f = float(budget)

    min_spend = constraints.get("min_spend", 0.0)
    max_spend = constraints.get("max_spend")
    if max_spend is None:
        raise ValueError("no fact pack: constraints.max_spend is required")

    lo = np.array([_bound(min_spend, ch) for ch in order], dtype=float)
    hi = np.array([_bound(max_spend, ch) for ch in order], dtype=float)
    baseline = _equal_room(lo, hi, budget_f)

    total_spend = allocation.get("total_spend")
    total_spend_f = float(total_spend) if total_spend is not None else float(
        sum(float(channels[ch]) for ch in order)
    )
    recommended = {ch: float(channels[ch]) for ch in order}

    rows: dict[str, dict[str, Any]] = {}
    for i, ch in enumerate(order):
        rec = recommended[ch]
        base = float(baseline[i])
        rows[ch] = {
            "recommended_spend": rec,
            "baseline_spend": base,
            "spend_delta": rec - base,
            "share_of_budget": (rec / budget_f) if budget_f else 0.0,
            "saturation_flag": _saturation_flag(rec, float(lo[i]), float(hi[i])),
        }

    return {
        "channels": rows,
        "concentration_note": _concentration_note(recommended, total_spend_f),
        "expected_incremental_kpi": allocation.get("expected_incremental_kpi"),
        "incremental_kpi_delta_vs_baseline": allocation.get(
            "incremental_kpi_delta_vs_baseline"
        ),
    }


def numbers_match(fact_pack: Mapping[str, Any], brief: Any) -> bool:
    """True when the brief matches the fact pack.

    Structured fields use absolute tolerance ``1e-6`` (``None`` matches only
    ``None``). Headline and bullet numbers use absolute tolerance ``1e-4``
    and must each be a fact-pack spend, delta, share (fraction or percent),
    or KPI. ``saturation_flag`` must match exactly. A token with no allowed
    value returns False. Text with no numbers is skipped.
    """
    payload = brief.model_dump() if hasattr(brief, "model_dump") else brief
    if not _same(
        payload.get("predicted_incremental_kpi"),
        fact_pack.get("expected_incremental_kpi"),
    ):
        return False
    if not _same(
        payload.get("incremental_kpi_delta_vs_baseline"),
        fact_pack.get("incremental_kpi_delta_vs_baseline"),
    ):
        return False

    shifts = payload.get("shifts") or []
    by_channel = {row["channel"]: row for row in shifts}
    facts = fact_pack["channels"]
    if set(by_channel) != set(facts):
        return False
    for ch, fact in facts.items():
        shift = by_channel[ch]
        if not _same(shift.get("baseline_spend"), fact["baseline_spend"]):
            return False
        if not _same(shift.get("recommended_spend"), fact["recommended_spend"]):
            return False
        if not _same(shift.get("spend_delta"), fact["spend_delta"]):
            return False
        if shift.get("saturation_flag") != fact["saturation_flag"]:
            return False
    return _prose_numbers_ok(payload, fact_pack)


# --- Equal-room / flags ---


def _equal_room(lo: np.ndarray, hi: np.ndarray, budget: float) -> np.ndarray:
    """Copy of allocator._feasible_start: mins, then leftover proportional to room."""
    remaining = budget - float(lo.sum())
    room = hi - lo
    room_sum = float(room.sum())
    if room_sum <= 0:
        return lo.copy()
    return lo + remaining * (room / room_sum)


def _bound(spec: Any, channel: str) -> float:
    if isinstance(spec, Mapping):
        if channel not in spec:
            raise ValueError(f"no fact pack: missing bound for {channel}")
        return float(spec[channel])
    return float(spec)


def _saturation_flag(spend: float, min_spend: float, max_spend: float) -> str:
    if spend >= _NEAR_CEILING * max_spend:
        return "near_ceiling"
    if spend <= min_spend + _FLOOR_TOL:
        return "at_floor"
    return "ok"


def _concentration_note(spends: Mapping[str, float], total_spend: float) -> str | None:
    if total_spend <= 0:
        return None
    channel, spend = max(spends.items(), key=lambda item: item[1])
    share = spend / total_spend
    if share < _CONCENTRATION:
        return None
    # Percent form of share_of_budget so the note survives the prose number lock.
    return f"{channel} holds {share * 100:.6g}% of total spend"


def _allowed_numbers(fact_pack: Mapping[str, Any]) -> list[float]:
    allowed: list[float] = []
    for fact in fact_pack["channels"].values():
        allowed.append(float(fact["baseline_spend"]))
        allowed.append(float(fact["recommended_spend"]))
        allowed.append(float(fact["spend_delta"]))
        share = float(fact["share_of_budget"])
        allowed.append(share)
        allowed.append(share * 100.0)
    kpi = fact_pack.get("expected_incremental_kpi")
    if kpi is not None:
        allowed.append(float(kpi))
    delta = fact_pack.get("incremental_kpi_delta_vs_baseline")
    if delta is not None:
        allowed.append(float(delta))
    return allowed


def _prose_numbers_ok(payload: Mapping[str, Any], fact_pack: Mapping[str, Any]) -> bool:
    texts = [str(payload.get("headline") or "")]
    texts.extend(str(item) for item in (payload.get("bullets") or []))
    allowed = _allowed_numbers(fact_pack)
    for text in texts:
        for match in _NUMBER_TOKEN.finditer(text):
            token = match.group(0)
            value = float(token[:-1] if token.endswith("%") else token)
            if not any(
                math.isclose(value, item, rel_tol=0.0, abs_tol=_PROSE_TOL) for item in allowed
            ):
                return False
    return True


def _same(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is None and right is None
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=_NUMBER_TOL)
