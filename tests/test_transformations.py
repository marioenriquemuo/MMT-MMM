"""Tests for STORY-102 geometric + Weibull adstock + Hill (Steps 2–4)."""

from __future__ import annotations

import numpy as np
import pytest

from src.models.transformations import (
    geometric_adstock,
    hill_saturation,
    weibull_adstock,
)

# --- Fixtures ---


@pytest.fixture
def pulse() -> np.ndarray:
    """Impulse of 100 on day 0, zeros after (hand-checkable decay)."""
    x = np.zeros(8)
    x[0] = 100.0
    return x


@pytest.fixture
def long_pulse() -> np.ndarray:
    """Longer impulse for Weibull tail / peak-timing checks."""
    x = np.zeros(40)
    x[0] = 100.0
    return x


# --- geometric_adstock ---


def test_theta_zero_equals_input():
    x = np.array([3.0, 1.0, 4.0, 2.0])
    np.testing.assert_allclose(geometric_adstock(x, 0.0), x)


def test_pulse_decay_theta_half(pulse: np.ndarray):
    """100 then zeros, theta=0.5 → 100, 50, 25, 12.5, …"""
    y = geometric_adstock(pulse, 0.5)
    expected = np.array([100.0, 50.0, 25.0, 12.5, 6.25, 3.125, 1.5625, 0.78125])
    np.testing.assert_allclose(y, expected, rtol=1e-12, atol=1e-12)


def test_nonnegative_when_x_nonnegative():
    x = np.array([0.0, 10.0, 5.0, 20.0, 0.0])
    y = geometric_adstock(x, 0.4)
    assert np.all(y >= 0.0)


def test_length_preserved():
    x = np.linspace(0.0, 50.0, 37)
    assert geometric_adstock(x, 0.3).shape == x.shape


def test_two_runs_identical(pulse: np.ndarray):
    a = geometric_adstock(pulse, 0.6)
    b = geometric_adstock(pulse, 0.6)
    np.testing.assert_array_equal(a, b)


def test_rejects_bad_theta():
    x = np.ones(5)
    with pytest.raises(ValueError, match="theta"):
        geometric_adstock(x, 1.0)
    with pytest.raises(ValueError, match="theta"):
        geometric_adstock(x, -0.01)


def test_2d_channels_by_time():
    """Shape (channels, T) with axis=-1 adstocks each channel independently."""
    x = np.zeros((2, 5))
    x[0, 0] = 100.0
    x[1, 0] = 40.0
    y = geometric_adstock(x, 0.5, axis=-1)
    np.testing.assert_allclose(
        y[0],
        [100.0, 50.0, 25.0, 12.5, 6.25],
        rtol=1e-12,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        y[1],
        [40.0, 20.0, 10.0, 5.0, 2.5],
        rtol=1e-12,
        atol=1e-12,
    )


def test_matches_recursive_definition():
    rng = np.random.default_rng(0)
    x = rng.uniform(0.0, 50.0, size=200)
    theta = 0.37
    y = geometric_adstock(x, theta)
    prev = 0.0
    for i, xi in enumerate(x):
        prev = float(xi) + theta * prev
        assert y[i] == pytest.approx(prev, rel=1e-12, abs=1e-12)


# --- weibull_adstock ---


def test_weibull_length_preserved(long_pulse: np.ndarray):
    y = weibull_adstock(long_pulse, shape=1.5, scale=5.0)
    assert y.shape == long_pulse.shape


def test_weibull_nonnegative(long_pulse: np.ndarray):
    y = weibull_adstock(long_pulse, shape=0.8, scale=4.0)
    assert np.all(y >= 0.0)


def test_weibull_normalize_unit_mass_on_constant():
    """Normalized weights sum to 1 → constant series stays at that level."""
    x = np.full(50, 10.0)
    y = weibull_adstock(x, shape=1.2, scale=3.0, normalize=True, max_lag=20)
    # After warm-up (lag window), level ≈ 10
    np.testing.assert_allclose(y[20:], 10.0, rtol=1e-10, atol=1e-10)


def test_weibull_raw_mass_not_forced_to_one(long_pulse: np.ndarray):
    """normalize=False keeps raw PDF-style weights (pulse response ≠ pulse)."""
    y_raw = weibull_adstock(
        long_pulse, shape=1.5, scale=5.0, normalize=False, max_lag=20
    )
    y_norm = weibull_adstock(
        long_pulse, shape=1.5, scale=5.0, normalize=True, max_lag=20
    )
    # Raw total response mass differs from normalized (unless weights already sum≈1)
    assert not np.allclose(y_raw, y_norm)
    assert y_raw.sum() != pytest.approx(y_norm.sum())


def test_weibull_larger_scale_longer_tail(long_pulse: np.ndarray):
    """Larger scale stretches carryover — more mass in the late tail."""
    y_short = weibull_adstock(
        long_pulse, shape=1.5, scale=2.0, normalize=True, max_lag=35
    )
    y_long = weibull_adstock(
        long_pulse, shape=1.5, scale=8.0, normalize=True, max_lag=35
    )
    # Days 15+ should hold more of the response when scale is larger
    assert y_long[15:].sum() > y_short[15:].sum()


def test_weibull_shape_controls_peak_timing(long_pulse: np.ndarray):
    """shape < 1 peaks at lag 0; shape > 1 can peak after day 0."""
    y_early = weibull_adstock(
        long_pulse, shape=0.6, scale=5.0, normalize=True, max_lag=30
    )
    y_delayed = weibull_adstock(
        long_pulse, shape=2.5, scale=6.0, normalize=True, max_lag=30
    )
    assert int(np.argmax(y_early)) == 0
    assert int(np.argmax(y_delayed)) > 0


def test_weibull_rejects_bad_params():
    x = np.ones(5)
    with pytest.raises(ValueError, match="shape"):
        weibull_adstock(x, shape=0.0, scale=2.0)
    with pytest.raises(ValueError, match="shape"):
        weibull_adstock(x, shape=-1.0, scale=2.0)
    with pytest.raises(ValueError, match="scale"):
        weibull_adstock(x, shape=1.0, scale=0.0)
    with pytest.raises(ValueError, match="scale"):
        weibull_adstock(x, shape=1.0, scale=-3.0)


def test_weibull_2d_channels_by_time():
    x = np.zeros((2, 20))
    x[0, 0] = 100.0
    x[1, 0] = 40.0
    y = weibull_adstock(x, shape=1.5, scale=4.0, axis=-1, normalize=True)
    assert y.shape == x.shape
    # Independent channels: ratio of responses ≈ ratio of pulses after normalize
    np.testing.assert_allclose(y[0] * 0.4, y[1], rtol=1e-10, atol=1e-10)


def test_weibull_two_runs_identical(long_pulse: np.ndarray):
    a = weibull_adstock(long_pulse, shape=1.1, scale=3.5)
    b = weibull_adstock(long_pulse, shape=1.1, scale=3.5)
    np.testing.assert_array_equal(a, b)


# --- hill_saturation ---


def test_hill_bounds_in_unit_interval():
    x = np.linspace(0.0, 500.0, 101)
    y = hill_saturation(x, K=50.0, S=1.5)
    assert np.all(y >= 0.0)
    assert np.all(y < 1.0)
    assert y[0] == pytest.approx(0.0)


def test_hill_half_saturation_at_K():
    """At x = K, y ≈ 0.5 for any valid S."""
    for K, S in ((10.0, 0.8), (50.0, 1.0), (100.0, 2.5)):
        y = hill_saturation(np.array([K]), K=K, S=S)
        assert y[0] == pytest.approx(0.5, rel=1e-12, abs=1e-12)


def test_hill_monotonic_in_x():
    x = np.linspace(0.0, 200.0, 50)
    y = hill_saturation(x, K=40.0, S=1.2)
    assert np.all(np.diff(y) >= -1e-15)


def test_hill_larger_S_steeper_around_K():
    """Larger S → steeper slope near K (higher |dy/dx| at half-sat)."""
    K = 50.0
    # Finite difference around K
    eps = 0.5
    x = np.array([K - eps, K + eps])
    slope_lo = np.diff(hill_saturation(x, K=K, S=1.0))[0] / (2 * eps)
    slope_hi = np.diff(hill_saturation(x, K=K, S=3.0))[0] / (2 * eps)
    assert slope_hi > slope_lo


def test_hill_shape_preserved():
    x = np.linspace(0.0, 80.0, 21).reshape(3, 7)
    y = hill_saturation(x, K=20.0, S=1.5)
    assert y.shape == x.shape


def test_hill_clips_negative_x():
    """Negative spend clipped to 0 → response 0 (documented)."""
    y = hill_saturation(np.array([-10.0, 0.0, 25.0]), K=25.0, S=1.0)
    assert y[0] == pytest.approx(0.0)
    assert y[1] == pytest.approx(0.0)
    assert y[2] == pytest.approx(0.5)


def test_hill_rejects_bad_params():
    x = np.ones(3)
    with pytest.raises(ValueError, match="K"):
        hill_saturation(x, K=0.0, S=1.0)
    with pytest.raises(ValueError, match="K"):
        hill_saturation(x, K=-5.0, S=1.0)
    with pytest.raises(ValueError, match="S"):
        hill_saturation(x, K=10.0, S=0.0)
    with pytest.raises(ValueError, match="S"):
        hill_saturation(x, K=10.0, S=-1.0)
