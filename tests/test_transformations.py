"""Tests for STORY-102 geometric adstock (Step 2 only)."""

from __future__ import annotations

import numpy as np
import pytest

from src.models.transformations import geometric_adstock

# --- Fixtures ---


@pytest.fixture
def pulse() -> np.ndarray:
    """Impulse of 100 on day 0, zeros after (hand-checkable decay)."""
    x = np.zeros(8)
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
