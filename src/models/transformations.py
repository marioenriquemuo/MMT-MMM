"""STORY-102 media transforms (Step 2: geometric adstock only).

Pure NumPy helpers for the modeling pipeline. Weibull adstock and Hill
saturation land in later teaching steps; the STORY-101 generator still owns
its inline DGP math until the shared module is complete.
"""

from __future__ import annotations

import numpy as np

# --- Geometric adstock ---


def geometric_adstock(
    x: np.ndarray,
    theta: float,
    *,
    axis: int = -1,
) -> np.ndarray:
    """Apply one-parameter geometric adstock along ``axis``.

    Recurrence (carryover of prior adstocked exposure)::

        x'_t = x_t + θ · x'_{t-1}

    with ``x'_{-1} = 0``. Equivalent closed form::

        x'_t = Σ_{ℓ=0}^{t} θ^ℓ · x_{t-ℓ}

    Parameters
    ----------
    x :
        Media series (spend, impressions, …). 1D ``(T,)`` or 2D
        ``(channels, T)`` / ``(T, channels)`` depending on ``axis``.
    theta :
        Carryover in ``[0, 1)``. ``theta = 0`` is identity (no memory);
        values near 1 retain long decay tails.
    axis :
        Time axis to accumulate along. Default ``-1`` (last axis).

    Returns
    -------
    np.ndarray
        Adstocked array, same shape as ``x``. Non-negative when ``x`` is.

    Notes
    -----
    Implementation moves the time axis last, then applies the recurrence
    with NumPy broadcasting over leading dimensions (fast for typical MMM
    shapes: a few channels × hundreds of days).
    """
    arr = np.asarray(x, dtype=float)
    if not (0.0 <= float(theta) < 1.0):
        raise ValueError(f"theta must be in [0, 1), got {theta!r}")
    if arr.ndim == 0:
        raise ValueError("x must be at least 1-D")

    # Move time to the last axis: out[..., t] = x[..., t] + θ · out[..., t-1]
    moved = np.moveaxis(arr, axis, -1)
    n = moved.shape[-1]
    out = np.empty_like(moved, dtype=float)
    if n == 0:
        return np.moveaxis(out, -1, axis)

    out[..., 0] = moved[..., 0]
    for t in range(1, n):
        out[..., t] = moved[..., t] + theta * out[..., t - 1]

    return np.moveaxis(out, -1, axis)
