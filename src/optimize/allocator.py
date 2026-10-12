"""SLSQP budget allocator (STORY-301 Step 2).

Maximizes sum of ``provider.incremental_kpi(ch, x_c)`` subject to
``sum(x) == total_budget`` and per-channel bounds. Target-KPI minimize
mode lands in Step 3.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
from scipy.optimize import minimize

from src.optimize.curves import CurveProvider

# --- Defaults ---

_DEFAULT_TOL = 1e-6


# --- Public API ---


def optimize_budget(
    provider: CurveProvider,
    total_budget: float,
    min_spend: float | Mapping[str, float] = 0.0,
    max_spend: float | Mapping[str, float] | None = None,
    *,
    channels: Sequence[str] | None = None,
    tol: float = _DEFAULT_TOL,
) -> dict:
    """Allocate ``total_budget`` across channels to maximize incremental KPI.

    Parameters
    ----------
    provider :
        Curve lookup (``incremental_kpi`` / ``channels``).
    total_budget :
        Exact spend to allocate (equality constraint).
    min_spend, max_spend :
        Scalar broadcast to every channel, or per-channel dict.
        ``max_spend=None`` → each channel upper bound is ``total_budget``.
    channels :
        Optional subset / order; default = ``provider.channels()``.
    tol :
        Absolute tolerance for post-solve sum and bound checks.

    Returns
    -------
    dict with ``spends``, ``expected_incremental_kpi``, ``success``, ``message``.
    On hard infeasibility (before solve), ``spends`` is empty and ``success`` is False.
    """
    chans = list(channels) if channels is not None else list(provider.channels())
    if not chans:
        return _fail("no channels to allocate", {})

    budget = float(total_budget)
    if budget < 0:
        return _fail(f"total_budget must be >= 0, got {budget}", {})

    lo, hi = _resolve_bounds(chans, min_spend, max_spend, budget)

    # --- Feasibility gates (before SLSQP) ---
    if np.any(lo > hi + tol):
        bad = [c for c, a, b in zip(chans, lo, hi) if a > b + tol]
        return _fail(f"min_spend > max_spend for channels: {bad}", {})
    if float(lo.sum()) > budget + tol:
        return _fail(
            f"infeasible: sum(min_spend)={float(lo.sum()):.6g} > total_budget={budget:.6g}",
            {},
        )
    if float(hi.sum()) < budget - tol:
        return _fail(
            f"infeasible: sum(max_spend)={float(hi.sum()):.6g} < total_budget={budget:.6g}",
            {},
        )

    x0 = _feasible_start(lo, hi, budget)
    bounds = list(zip(lo.tolist(), hi.tolist()))
    cons = {"type": "eq", "fun": lambda x: float(np.sum(x) - budget)}

    def objective(x: np.ndarray) -> float:
        # Maximize sum f_c(x_c) → minimize negative
        return -sum(
            provider.incremental_kpi(ch, float(x[i])) for i, ch in enumerate(chans)
        )

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=cons,
        options={"ftol": tol, "maxiter": 500},
    )

    spends = {ch: float(result.x[i]) for i, ch in enumerate(chans)}
    kpi = sum(provider.incremental_kpi(ch, spends[ch]) for ch in chans)
    ok, msg = _validate_solution(spends, chans, lo, hi, budget, tol, result)

    return {
        "spends": spends,
        "expected_incremental_kpi": float(kpi),
        "success": ok,
        "message": msg,
    }


# --- Bounds / start / validate ---


def _resolve_bounds(
    channels: list[str],
    min_spend: float | Mapping[str, float],
    max_spend: float | Mapping[str, float] | None,
    total_budget: float,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(channels)
    if isinstance(min_spend, Mapping):
        lo = np.array([float(min_spend.get(ch, 0.0)) for ch in channels], dtype=float)
    else:
        lo = np.full(n, float(min_spend), dtype=float)

    if max_spend is None:
        hi = np.full(n, float(total_budget), dtype=float)
    elif isinstance(max_spend, Mapping):
        hi = np.array(
            [float(max_spend.get(ch, total_budget)) for ch in channels], dtype=float
        )
    else:
        hi = np.full(n, float(max_spend), dtype=float)

    return lo, hi


def _feasible_start(lo: np.ndarray, hi: np.ndarray, budget: float) -> np.ndarray:
    """Start at mins, then fill remaining budget proportional to room."""
    remaining = budget - float(lo.sum())
    room = hi - lo
    room_sum = float(room.sum())
    if room_sum <= 0:
        return lo.copy()
    return lo + remaining * (room / room_sum)


def _validate_solution(
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


def _fail(message: str, spends: dict[str, float]) -> dict:
    return {
        "spends": spends,
        "expected_incremental_kpi": 0.0,
        "success": False,
        "message": message,
    }
