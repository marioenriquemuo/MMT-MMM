"""STORY-102 media transforms (Step 3: geometric + Weibull adstock).

Pure NumPy helpers for the modeling pipeline. Hill saturation lands in a
later teaching step; the STORY-101 generator still owns its inline DGP math
until the shared module is complete.
"""

from __future__ import annotations

import numpy as np

# Cap on discrete lag support for Weibull (daily MMM safety).
_WEIBULL_MAX_LAG_CAP = 200


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


# --- Weibull adstock ---


def _weibull_n_lags(n_time: int, scale: float, max_lag: int | None) -> int:
    """Choose discrete lag support ``L`` for Weibull PDF weights.

    Default: ``min(n_time, ceil(scale * 5) + 1, 200)``. Five scales covers
    nearly all Weibull mass for typical shapes; the hard cap keeps daily
    series from allocating absurd kernels. Pass ``max_lag`` to override.
    """
    if max_lag is not None:
        if max_lag < 1:
            raise ValueError(f"max_lag must be >= 1, got {max_lag!r}")
        return min(n_time, int(max_lag))
    suggested = int(np.ceil(float(scale) * 5.0)) + 1
    return max(1, min(n_time, suggested, _WEIBULL_MAX_LAG_CAP))


def _weibull_pdf_weights(n_lags: int, shape: float, scale: float) -> np.ndarray:
    """Discrete Weibull PDF-style weights on lags ``0 .. L-1``.

    Evaluated at positive points ``1, 2, …, L`` so ``shape < 1`` stays
    finite at lag 0 (the continuous PDF blows up at 0 when ``k < 1``).
    """
    # lag ℓ maps to evaluation point (ℓ + 1)
    t = np.arange(1, n_lags + 1, dtype=float)
    t_over_lambda = t / scale
    return (
        (shape / scale)
        * np.power(t_over_lambda, shape - 1.0)
        * np.exp(-np.power(t_over_lambda, shape))
    )


def weibull_adstock(
    x: np.ndarray,
    shape: float,
    scale: float,
    *,
    axis: int = -1,
    normalize: bool = True,
    max_lag: int | None = None,
) -> np.ndarray:
    """Apply two-parameter Weibull adstock along ``axis``.

    Builds discrete Weibull **PDF-style** lag weights ``w_0 … w_{L-1}``,
    optionally normalizes them to sum to 1, then applies a causal
    convolution::

        x'_t = Σ_{ℓ=0}^{L-1} w_ℓ · x_{t-ℓ}

    (missing past values treated as 0).

    Parameters
    ----------
    x :
        Media series. 1D ``(T,)`` or 2D ``(channels, T)`` /
        ``(T, channels)`` depending on ``axis``.
    shape :
        Weibull shape ``k > 0``.

        * ``k < 1`` — peak weight at lag 0 (immediate impact, fast early
          drop, then a longish tail).
        * ``k = 1`` — exponential-like decay from lag 0.
        * ``k > 1`` — peak **after** day 0 (delayed / humped response).
    scale :
        Weibull scale ``λ > 0``. Larger ``λ`` stretches the lag kernel
        (longer carryover / heavier late tail).
    axis :
        Time axis. Default ``-1`` (last axis), same spirit as
        :func:`geometric_adstock`.
    normalize :
        If ``True`` (default), divide weights by their sum so a constant
        input is preserved in level. If ``False``, use raw PDF-style
        weights (mass generally ≠ 1).
    max_lag :
        Optional hard length ``L`` of the lag kernel. Default chooses
        ``min(T, ceil(scale * 5) + 1, 200)`` — see module docstring on
        :func:`_weibull_n_lags`.

    Returns
    -------
    np.ndarray
        Adstocked array, same shape as ``x``. Non-negative when ``x`` is.

    Notes
    -----
    Geometric adstock is a fixed-fraction decay (always peaks at lag 0).
    Weibull adds a flexible lag *shape* so media effects can crest days
    after the spend pulse — useful for TV / brand channels.
    """
    arr = np.asarray(x, dtype=float)
    shape_f = float(shape)
    scale_f = float(scale)
    if not (shape_f > 0.0):
        raise ValueError(f"shape must be > 0, got {shape!r}")
    if not (scale_f > 0.0):
        raise ValueError(f"scale must be > 0, got {scale!r}")
    if arr.ndim == 0:
        raise ValueError("x must be at least 1-D")

    moved = np.moveaxis(arr, axis, -1)
    n = moved.shape[-1]
    if n == 0:
        return np.moveaxis(np.empty_like(moved, dtype=float), -1, axis)

    n_lags = _weibull_n_lags(n, scale_f, max_lag)
    weights = _weibull_pdf_weights(n_lags, shape_f, scale_f)
    if normalize:
        mass = float(weights.sum())
        if mass <= 0.0:
            raise ValueError("Weibull weights have non-positive mass")
        weights = weights / mass

    # Causal convolution along the last axis for every leading slice.
    flat = moved.reshape(-1, n)
    out_flat = np.empty_like(flat, dtype=float)
    for i in range(flat.shape[0]):
        # mode='full' then truncate → y[t] = Σ_ℓ w[ℓ] x[t-ℓ]
        out_flat[i] = np.convolve(flat[i], weights, mode="full")[:n]
    out = out_flat.reshape(moved.shape)
    return np.moveaxis(out, -1, axis)
