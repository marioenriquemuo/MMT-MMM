"""Offline response-curve providers for STORY-301 (Step 1).

Reads Meridian ``reports/metrics.json`` ``response_curves.means`` (or a
synthetic fixture with the same / flattened shape) and answers
``incremental_kpi(channel, spend)`` via linear interpolation.

**Extrapolation policy:** clamp to endpoint KPI values outside the observed
spend range (``numpy.interp`` default — no left/right fill). Flat outside
the grid; do not invent steeper or declining tails.

Assumption: curves are trusted as Meridian reported them. Path-C rank
recovery vs Meridian remains an open Sprint 1 issue — do not treat these
as Path-C ground truth.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping

import numpy as np

# --- Types ---

CurveArrays = dict[str, tuple[np.ndarray, np.ndarray]]  # channel -> (spend, mean_kpi)


# --- Provider interface ---


class CurveProvider(ABC):
    """Spend → incremental KPI per channel (offline or future live)."""

    @abstractmethod
    def channels(self) -> list[str]:
        """Channel names available on this provider."""

    @abstractmethod
    def incremental_kpi(self, channel: str, spend: float) -> float:
        """Interpolated incremental KPI at ``spend`` for ``channel``."""


# --- Load / normalize ---


def load_curve_means(data: Mapping[str, Any]) -> CurveArrays:
    """Normalize Meridian metrics or synthetic fixture into spend/mean arrays.

    Accepted shapes (first match wins):

    1. Meridian metrics: ``{"response_curves": {"means": {ch: {spend, mean}}}}``
    2. Nested means only: ``{"means": {ch: {spend, mean}}}``
    3. Flat channel map: ``{ch: {spend, mean}}``
    """
    raw = _extract_means_map(data)
    out: CurveArrays = {}
    for channel, entry in raw.items():
        if not isinstance(entry, Mapping):
            raise ValueError(f"curve entry for {channel!r} must be a mapping")
        if "spend" not in entry or "mean" not in entry:
            raise ValueError(
                f"curve entry for {channel!r} needs 'spend' and 'mean' arrays"
            )
        spend = np.asarray(entry["spend"], dtype=float).reshape(-1)
        mean = np.asarray(entry["mean"], dtype=float).reshape(-1)
        if spend.size != mean.size:
            raise ValueError(
                f"{channel!r}: spend length {spend.size} != mean length {mean.size}"
            )
        if spend.size < 2:
            raise ValueError(f"{channel!r}: need at least 2 spend/mean points")
        # np.interp requires increasing xp
        order = np.argsort(spend)
        spend, mean = spend[order], mean[order]
        out[str(channel)] = (spend, mean)
    if not out:
        raise ValueError("no response curve channels found")
    return out


def _extract_means_map(data: Mapping[str, Any]) -> Mapping[str, Any]:
    rc = data.get("response_curves")
    if isinstance(rc, Mapping) and "means" in rc:
        means = rc["means"]
        if isinstance(means, Mapping):
            return means
    means = data.get("means")
    if isinstance(means, Mapping):
        return means
    # Flat {channel: {spend, mean}} — every value looks like a curve entry
    if data and all(
        isinstance(v, Mapping) and "spend" in v and "mean" in v for v in data.values()
    ):
        return data
    raise ValueError(
        "expected response_curves.means, means, or flat {channel: {spend, mean}}"
    )


def load_curve_means_json(path: str | Path) -> CurveArrays:
    """Load curve arrays from a JSON file path."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path}: JSON root must be an object")
    return load_curve_means(payload)


# --- Offline JSON provider ---


class MetricsJsonCurveProvider(CurveProvider):
    """Linear-interpolated curves from Meridian metrics or synthetic fixture JSON."""

    def __init__(self, curves: CurveArrays | Mapping[str, Any] | str | Path):
        if isinstance(curves, (str, Path)):
            self._curves = load_curve_means_json(curves)
        elif isinstance(curves, Mapping) and curves and not _looks_like_arrays(curves):
            self._curves = load_curve_means(curves)
        else:
            self._curves = {
                str(ch): (np.asarray(sp, dtype=float), np.asarray(mn, dtype=float))
                for ch, (sp, mn) in curves.items()  # type: ignore[misc]
            }

    def channels(self) -> list[str]:
        return list(self._curves.keys())

    def incremental_kpi(self, channel: str, spend: float) -> float:
        if channel not in self._curves:
            raise KeyError(f"unknown channel: {channel!r}")
        xp, fp = self._curves[channel]
        # Clamp: np.interp returns fp[0] / fp[-1] outside xp range
        return float(np.interp(float(spend), xp, fp))

    def spend_grid(self, channel: str) -> np.ndarray:
        """Observed spend knots for ``channel`` (teaching / tests)."""
        return self._curves[channel][0].copy()

    def mean_grid(self, channel: str) -> np.ndarray:
        """Observed mean incremental KPI knots for ``channel``."""
        return self._curves[channel][1].copy()


def _looks_like_arrays(curves: Mapping[str, Any]) -> bool:
    """True if mapping is already channel -> (spend, mean) array pairs."""
    first = next(iter(curves.values()), None)
    return isinstance(first, tuple) and len(first) == 2


# --- Future live Meridian seam (not implemented) ---
#
# class MeridianLiveCurveProvider(CurveProvider):
#     """ponytail: stub only — wire Analyzer.response_curves when live reload is needed.
#     Would call Meridian Analyzer, then reuse load_curve_means(response_curve_means(...)).
#     """
#
#     def channels(self) -> list[str]:
#         raise NotImplementedError("live Meridian provider not implemented")
#
#     def incremental_kpi(self, channel: str, spend: float) -> float:
#         raise NotImplementedError("live Meridian provider not implemented")
