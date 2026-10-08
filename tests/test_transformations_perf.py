"""STORY-102 Step 6 — wall-time gate for transforms on ~2y daily data."""

from __future__ import annotations

import time

import numpy as np

from src.models.transformations import (
    geometric_adstock,
    hill_saturation,
    weibull_adstock,
)

N_DAYS = 730
N_CHANNELS = 4
MAX_SECONDS = 1.0


def _panel(rng: np.random.Generator) -> np.ndarray:
    """Non-negative spend panel shaped ``(channels, days)``."""
    return rng.uniform(0.0, 100.0, size=(N_CHANNELS, N_DAYS))


def _run_transforms(x: np.ndarray) -> None:
    geo = geometric_adstock(x, theta=0.5, axis=-1)
    wbl = weibull_adstock(x, shape=2.0, scale=7.0, axis=-1)
    hill_saturation(geo, K=50.0, S=1.5)
    hill_saturation(wbl, K=50.0, S=1.5)


def test_transforms_two_years_daily_under_one_second():
    """DoD: geometric + Weibull + Hill on 730×4 panel finishes in <1s."""
    rng = np.random.default_rng(42)
    x = _panel(rng)

    # Warm-up (import / NumPy dispatch); timed run is cold enough for DoD.
    _run_transforms(x)

    t0 = time.perf_counter()
    _run_transforms(x)
    elapsed = time.perf_counter() - t0

    assert elapsed < MAX_SECONDS, (
        f"transforms on {N_DAYS}d×{N_CHANNELS}ch took {elapsed:.3f}s "
        f"(limit {MAX_SECONDS}s)"
    )
