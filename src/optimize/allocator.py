"""SLSQP budget allocator (STORY-301 Steps 2–3).

**Maximize mode:** fixed ``total_budget``, maximize ∑ incremental KPI under
per-channel min/max.

**Target mode:** minimize ∑ spend s.t. ∑ incremental KPI ≥ ``target_kpi``
and the same bounds. Infeasible targets return ``solver.success=False``.

Baseline (maximize only): equal-room fill from mins within bounds
(``_feasible_start``); ``incremental_kpi_delta_vs_baseline`` = optimum − baseline.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize

from src.optimize.curves import CurveProvider

# --- Defaults ---

_DEFAULT_TOL = 1e-6


# --- Public API ---


def optimize_budget(
    provider: CurveProvider,
    total_budget: float | None = None,
    min_spend: float | Mapping[str, float] = 0.0,
    max_spend: float | Mapping[str, float] | None = None,
    *,
    target_kpi: float | None = None,
    channels: Sequence[str] | None = None,
    tol: float = _DEFAULT_TOL,
    curve_source: str | None = None,
) -> dict[str, Any]:
    """Allocate spend across channels (maximize KPI or hit a KPI target).

    Exactly one of ``total_budget`` or ``target_kpi`` must be set.

    Returns plan-shaped allocation dict (channels, totals, constraints, solver).
    """
    chans = list(channels) if channels is not None else list(provider.channels())
    if not chans:
        return _fail_result("no channels to allocate", curve_source=curve_source)

    has_budget = total_budget is not None
    has_target = target_kpi is not None
    if has_budget == has_target:
        return _fail_result(
            "set exactly one of total_budget (maximize) or target_kpi (minimize spend)",
            curve_source=curve_source,
        )

    if has_budget:
        return _maximize(
            provider,
            chans,
            float(total_budget),
            min_spend,
            max_spend,
            tol=tol,
            curve_source=curve_source,
        )
    return _minimize_for_target(
        provider,
        chans,
        float(target_kpi),
        min_spend,
        max_spend,
        tol=tol,
        curve_source=curve_source,
    )


# --- Maximize mode ---


def _maximize(
    provider: CurveProvider,
    chans: list[str],
    budget: float,
    min_spend: float | Mapping[str, float],
    max_spend: float | Mapping[str, float] | None,
    *,
    tol: float,
    curve_source: str | None,
) -> dict[str, Any]:
    if budget < 0:
        return _fail_result(
            f"total_budget must be >= 0, got {budget}",
            curve_source=curve_source,
            constraints=_constraints("maximize", budget, None, min_spend, max_spend, chans),
        )

    lo, hi = _resolve_bounds(chans, min_spend, max_spend, default_hi=budget)
    cons_meta = _constraints(
        "maximize", budget, None, _bounds_dict(chans, lo), _bounds_dict(chans, hi), chans
    )

    gate = _bounds_gate(chans, lo, hi, tol, curve_source, cons_meta)
    if gate is not None:
        return gate
    if float(lo.sum()) > budget + tol:
        return _fail_result(
            f"infeasible: sum(min_spend)={float(lo.sum()):.6g} > total_budget={budget:.6g}",
            curve_source=curve_source,
            constraints=cons_meta,
        )
    if float(hi.sum()) < budget - tol:
        return _fail_result(
            f"infeasible: sum(max_spend)={float(hi.sum()):.6g} < total_budget={budget:.6g}",
            curve_source=curve_source,
            constraints=cons_meta,
        )

    baseline = _feasible_start(lo, hi, budget)
    baseline_kpi = _total_kpi(provider, chans, baseline)

    x0 = baseline.copy()
    bounds = list(zip(lo.tolist(), hi.tolist()))
    eq = {"type": "eq", "fun": lambda x: float(np.sum(x) - budget)}

    def objective(x: np.ndarray) -> float:
        return -_total_kpi(provider, chans, x)

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=eq,
        options={"ftol": tol, "maxiter": 500},
    )

    spends = {ch: float(result.x[i]) for i, ch in enumerate(chans)}
    kpi = _total_kpi(provider, chans, result.x)
    ok, msg = _validate_maximize(spends, chans, lo, hi, budget, tol, result)
    if not ok:
        return _fail_result(msg, curve_source=curve_source, constraints=cons_meta)

    return _ok_result(
        spends,
        kpi,
        float(kpi - baseline_kpi),
        cons_meta,
        True,
        msg,
        curve_source,
    )


# --- Target-KPI mode ---


def _minimize_for_target(
    provider: CurveProvider,
    chans: list[str],
    target: float,
    min_spend: float | Mapping[str, float],
    max_spend: float | Mapping[str, float] | None,
    *,
    tol: float,
    curve_source: str | None,
) -> dict[str, Any]:
    if target < 0:
        return _fail_result(
            f"target_kpi must be >= 0, got {target}",
            curve_source=curve_source,
        )

    default_hi = _curve_max_spends(provider, chans)
    lo, hi = _resolve_bounds(chans, min_spend, max_spend, default_hi=default_hi)
    cons_meta = _constraints(
        "target", None, target, _bounds_dict(chans, lo), _bounds_dict(chans, hi), chans
    )

    gate = _bounds_gate(chans, lo, hi, tol, curve_source, cons_meta)
    if gate is not None:
        return gate

    kpi_at_lo = _total_kpi(provider, chans, lo)
    kpi_at_hi = _total_kpi(provider, chans, hi)
    if kpi_at_hi + tol < target:
        return _fail_result(
            f"infeasible: max achievable KPI={kpi_at_hi:.6g} < target_kpi={target:.6g}",
            curve_source=curve_source,
            constraints=cons_meta,
        )

    # Already at/above T at mins → minimal feasible spend is lo
    if kpi_at_lo + tol >= target:
        spends = {ch: float(lo[i]) for i, ch in enumerate(chans)}
        return _ok_result(
            spends,
            kpi_at_lo,
            None,
            cons_meta,
            True,
            "target met at min_spend (no further reduction possible)",
            curve_source,
        )

    bounds = list(zip(lo.tolist(), hi.tolist()))
    # Start at hi (feasible by gate above)
    x0 = hi.copy()
    ineq = {
        "type": "ineq",
        "fun": lambda x: _total_kpi(provider, chans, x) - target,
    }

    def objective(x: np.ndarray) -> float:
        return float(np.sum(x))

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=ineq,
        options={"ftol": tol, "maxiter": 500},
    )

    spends = {ch: float(result.x[i]) for i, ch in enumerate(chans)}
    kpi = _total_kpi(provider, chans, result.x)
    ok, msg = _validate_target(spends, chans, lo, hi, target, kpi, tol, result)
    if not ok:
        return _fail_result(msg, curve_source=curve_source, constraints=cons_meta)

    return _ok_result(spends, kpi, None, cons_meta, True, msg, curve_source)


# --- Bounds / KPI / start / validate ---


def _resolve_bounds(
    channels: list[str],
    min_spend: float | Mapping[str, float],
    max_spend: float | Mapping[str, float] | None,
    *,
    default_hi: float | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(channels)
    if isinstance(min_spend, Mapping):
        lo = np.array([float(min_spend.get(ch, 0.0)) for ch in channels], dtype=float)
    else:
        lo = np.full(n, float(min_spend), dtype=float)

    if max_spend is None:
        if isinstance(default_hi, np.ndarray):
            hi = np.asarray(default_hi, dtype=float).copy()
        else:
            hi = np.full(n, float(default_hi), dtype=float)
    elif isinstance(max_spend, Mapping):
        fallback = (
            float(np.max(default_hi))
            if isinstance(default_hi, np.ndarray)
            else float(default_hi)
        )
        hi = np.array(
            [float(max_spend.get(ch, fallback)) for ch in channels], dtype=float
        )
    else:
        hi = np.full(n, float(max_spend), dtype=float)

    return lo, hi


def _curve_max_spends(provider: CurveProvider, channels: list[str]) -> np.ndarray:
    """Per-channel upper default = max observed spend knot (flat beyond)."""
    if not hasattr(provider, "spend_grid"):
        raise ValueError(
            "target mode needs max_spend when provider has no spend_grid()"
        )
    return np.array(
        [float(np.max(provider.spend_grid(ch))) for ch in channels], dtype=float
    )


def _feasible_start(lo: np.ndarray, hi: np.ndarray, budget: float) -> np.ndarray:
    """Start at mins, then fill remaining budget proportional to room (equal-room)."""
    remaining = budget - float(lo.sum())
    room = hi - lo
    room_sum = float(room.sum())
    if room_sum <= 0:
        return lo.copy()
    return lo + remaining * (room / room_sum)


def _total_kpi(provider: CurveProvider, channels: list[str], x: np.ndarray) -> float:
    return float(
        sum(provider.incremental_kpi(ch, float(x[i])) for i, ch in enumerate(channels))
    )


def _bounds_gate(
    chans: list[str],
    lo: np.ndarray,
    hi: np.ndarray,
    tol: float,
    curve_source: str | None,
    constraints: dict[str, Any],
) -> dict[str, Any] | None:
    if np.any(lo > hi + tol):
        bad = [c for c, a, b in zip(chans, lo, hi) if a > b + tol]
        return _fail_result(
            f"min_spend > max_spend for channels: {bad}",
            curve_source=curve_source,
            constraints=constraints,
        )
    return None


def _validate_maximize(
    spends: dict[str, float],
    channels: list[str],
    lo: np.ndarray,
    hi: np.ndarray,
    budget: float,
    tol: float,
    result,
) -> tuple[bool, str]:
    x = np.array([spends[ch] for ch in channels], dtype=float)
    if not bool(result.success):
        return False, f"SLSQP failed: {result.message}"
    if np.any(x < lo - tol) or np.any(x > hi + tol):
        return False, "solution violates channel min/max bounds"
    if abs(float(x.sum()) - budget) > tol:
        return False, (
            f"solution sum {float(x.sum()):.6g} != total_budget {budget:.6g} (tol={tol})"
        )
    return True, str(result.message)


def _validate_target(
    spends: dict[str, float],
    channels: list[str],
    lo: np.ndarray,
    hi: np.ndarray,
    target: float,
    kpi: float,
    tol: float,
    result,
) -> tuple[bool, str]:
    x = np.array([spends[ch] for ch in channels], dtype=float)
    if not bool(result.success):
        return False, f"SLSQP failed: {result.message}"
    if np.any(x < lo - tol) or np.any(x > hi + tol):
        return False, "solution violates channel min/max bounds"
    if kpi + tol < target:
        return False, (
            f"solution KPI {kpi:.6g} < target_kpi {target:.6g} (tol={tol})"
        )
    return True, str(result.message)


# --- Result builders ---


def _bounds_dict(channels: list[str], arr: np.ndarray) -> dict[str, float]:
    return {ch: float(arr[i]) for i, ch in enumerate(channels)}


def _constraints(
    mode: str,
    total_budget: float | None,
    target_kpi: float | None,
    min_spend: Any,
    max_spend: Any,
    channels: list[str],
) -> dict[str, Any]:
    return {
        "mode": mode,
        "total_budget": total_budget,
        "target_kpi": target_kpi,
        "min_spend": min_spend,
        "max_spend": max_spend,
        "channels": list(channels),
    }


def _ok_result(
    spends: dict[str, float],
    kpi: float,
    delta: float | None,
    constraints: dict[str, Any],
    success: bool,
    message: str,
    curve_source: str | None,
) -> dict[str, Any]:
    return {
        "channels": spends,
        "total_spend": float(sum(spends.values())),
        "expected_incremental_kpi": float(kpi),
        "incremental_kpi_delta_vs_baseline": delta,
        "constraints": constraints,
        "solver": {"success": success, "message": message},
        "curve_source": curve_source,
        # Step-2 aliases (tests / callers that used the old shape)
        "spends": spends,
        "success": success,
        "message": message,
    }


def _fail_result(
    message: str,
    *,
    curve_source: str | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "channels": {},
        "total_spend": 0.0,
        "expected_incremental_kpi": 0.0,
        "incremental_kpi_delta_vs_baseline": None,
        "constraints": constraints or {},
        "solver": {"success": False, "message": message},
        "curve_source": curve_source,
        "spends": {},
        "success": False,
        "message": message,
    }
