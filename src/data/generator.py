"""STORY-101 Path-C synthetic multi-channel marketing data generator.

Channels (stable IDs → display names):
  meta → Meta, google → Google, tiktok → TikTok, tv → TV

US-DTC-like CPM/CTR constants are hard-coded below (no network calls).
Geometric adstock and Hill saturation live inline here only — STORY-102
owns the shared transformations module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# --- Constants ---

SEED = 42
N_WEEKS = 104
N_DAYS = N_WEEKS * 7  # 728
CHANNELS = ("meta", "google", "tiktok", "tv")
CHANNEL_DISPLAY = {
    "meta": "Meta",
    "google": "Google",
    "tiktok": "TikTok",
    "tv": "TV",
}
COLUMNS = ("date", "channel", "spend", "impressions", "clicks", "baseline_sales")
# Count columns: round → clip ≥0 → int64 after the continuous DGP (spend stays float USD).
INTEGER_COLUMNS = ("impressions", "clicks", "baseline_sales")
START_DATE = "2023-01-02"  # Monday-aligned start for clean weekly structure

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV_PATH = REPO_ROOT / "data" / "raw" / "synthetic_ad_spend.csv"
DEFAULT_GT_PATH = REPO_ROOT / "data" / "raw" / "ground_truth.json"

# Daily spend base levels (USD) — mid-market US DTC scale.
SPEND_BASE = {
    "meta": 4200.0,
    "google": 5100.0,
    "tiktok": 2800.0,
    "tv": 9500.0,
}

# Fixed US-DTC-like delivery scalars (documented; offline only).
# CPM = cost per 1000 impressions; CTR = clicks / impressions.
CPM_USD = {
    "meta": 10.0,
    "google": 18.0,
    "tiktok": 8.0,
    "tv": 28.0,
}
CTR = {
    "meta": 0.010,
    "google": 0.028,
    "tiktok": 0.014,
    "tv": 0.0012,
}

# Planted geometric adstock decay α ∈ (0, 1): adstock_t = spend_t + α * adstock_{t-1}.
ADSTOCK_DECAY = {
    "meta": 0.35,
    "google": 0.45,
    "tiktok": 0.25,
    "tv": 0.70,
}

# Hill saturation: sat = spend^k / (spend^k + half^k); contribution = beta * sat.
HILL_HALF = {
    "meta": 5500.0,
    "google": 6500.0,
    "tiktok": 4000.0,
    "tv": 12000.0,
}
HILL_SLOPE = {
    "meta": 1.4,
    "google": 1.2,
    "tiktok": 1.6,
    "tv": 1.1,
}
# Incremental sales scale per fully saturated channel-day (planted ROAS-ish beta).
MEDIA_BETA = {
    "meta": 1800.0,
    "google": 2200.0,
    "tiktok": 1400.0,
    "tv": 2600.0,
}

BASELINE_LEVEL = 45_000.0
BASELINE_SEASON_AMP = 6_000.0
BASELINE_TREND_PER_DAY = 4.0


# --- Inline media transforms (generator-only; not STORY-102) ---


def geometric_adstock(spend: np.ndarray, decay: float) -> np.ndarray:
    """One-parameter geometric adstock: y_t = x_t + decay * y_{t-1}."""
    out = np.empty_like(spend, dtype=float)
    prev = 0.0
    for i, x in enumerate(spend):
        prev = float(x) + decay * prev
        out[i] = prev
    return out


def hill_saturation(x: np.ndarray, half: float, slope: float) -> np.ndarray:
    """Hill / Michaelis–Menten style saturation in [0, 1)."""
    x = np.asarray(x, dtype=float)
    x_safe = np.maximum(x, 0.0)
    num = np.power(x_safe, slope)
    den = num + half**slope
    return np.divide(num, den, out=np.zeros_like(num), where=den > 0)


# --- Spend / KPI construction ---


def _spend_series(channel: str, n: int, rng: np.random.Generator) -> np.ndarray:
    """Base + weekly seasonality + trend + flighting + correlated noise."""
    t = np.arange(n, dtype=float)
    dow = t % 7
    base = SPEND_BASE[channel]
    weekly = {
        "meta": 0.18,
        "google": 0.12,
        "tiktok": 0.22,
        "tv": 0.08,
    }[channel]
    # Weekday lift: mid-week digital; weekend TV mild bump.
    if channel == "tv":
        season = 1.0 + weekly * np.cos(2 * np.pi * (dow - 5) / 7)
    else:
        season = 1.0 + weekly * np.sin(2 * np.pi * (dow - 1) / 7)

    trend = 1.0 + 0.12 * (t / max(n - 1, 1))

    # Occasional flighting pulses (~every 6–10 weeks for 5–12 days).
    flight = np.ones(n)
    pulse_starts = {
        "meta": [40, 120, 250, 400, 560],
        "google": [55, 180, 310, 470, 620],
        "tiktok": [70, 200, 340, 500, 650],
        "tv": [90, 220, 380, 540],
    }[channel]
    for start in pulse_starts:
        length = 7 + int(rng.integers(0, 6))
        end = min(n, start + length)
        boost = 1.35 + float(rng.uniform(0.0, 0.45))
        flight[start:end] *= boost

    # Correlated AR(1) noise shared structure per channel.
    eps = np.zeros(n)
    shock = rng.normal(0.0, 0.08, size=n)
    rho = 0.55
    for i in range(n):
        eps[i] = rho * (eps[i - 1] if i else 0.0) + shock[i]

    spend = base * season * trend * flight * (1.0 + eps)
    return np.maximum(spend, 0.0)


def _impressions_clicks(spend: np.ndarray, channel: str) -> tuple[np.ndarray, np.ndarray]:
    cpm = CPM_USD[channel]
    impressions = spend / cpm * 1000.0
    clicks = impressions * CTR[channel]
    return impressions, clicks


def _baseline_sales(
    spend_by_channel: dict[str, np.ndarray],
    n: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """National baseline + media contribution after adstock/Hill."""
    t = np.arange(n, dtype=float)
    yearly = BASELINE_SEASON_AMP * np.sin(2 * np.pi * t / 365.25 - 0.4)
    baseline = BASELINE_LEVEL + yearly + BASELINE_TREND_PER_DAY * t

    media_contrib = np.zeros(n)
    channel_contrib: dict[str, list[float]] = {}
    for ch in CHANNELS:
        adstocked = geometric_adstock(spend_by_channel[ch], ADSTOCK_DECAY[ch])
        sat = hill_saturation(adstocked, HILL_HALF[ch], HILL_SLOPE[ch])
        contrib = MEDIA_BETA[ch] * sat
        channel_contrib[ch] = contrib.tolist()
        media_contrib += contrib

    sales = np.maximum(baseline + media_contrib, 0.0)
    meta = {
        "baseline_level": BASELINE_LEVEL,
        "baseline_season_amp": BASELINE_SEASON_AMP,
        "baseline_trend_per_day": BASELINE_TREND_PER_DAY,
        "channel_contribution_means": {
            ch: float(np.mean(channel_contrib[ch])) for ch in CHANNELS
        },
    }
    return sales, meta


def planted_ground_truth() -> dict[str, Any]:
    """Serializable planted Path-C parameters for later recovery tests."""
    return {
        "seed": SEED,
        "n_days": N_DAYS,
        "n_weeks": N_WEEKS,
        "start_date": START_DATE,
        "channels": list(CHANNELS),
        "channel_display": CHANNEL_DISPLAY,
        "spend_base": SPEND_BASE,
        "cpm_usd": CPM_USD,
        "ctr": CTR,
        "adstock_decay": ADSTOCK_DECAY,
        "hill_half": HILL_HALF,
        "hill_slope": HILL_SLOPE,
        "media_beta": MEDIA_BETA,
        "baseline_level": BASELINE_LEVEL,
        "baseline_season_amp": BASELINE_SEASON_AMP,
        "baseline_trend_per_day": BASELINE_TREND_PER_DAY,
        "transforms": {
            "adstock": "geometric: y_t = x_t + decay * y_{t-1}",
            "saturation": "hill: x^k / (x^k + half^k)",
            "note": "Inline in generator only; STORY-102 owns shared transforms.",
        },
        "baseline_sales_semantics": (
            "Same site-wide daily KPI (integer order/unit counts) repeated on "
            "each channel row for that date; groupby(date).first() recovers the "
            "series — do not sum across channels."
        ),
        "baseline_sales_unit": "orders_units",
        "integer_postprocess": {
            "columns": list(INTEGER_COLUMNS),
            "rule": "round then clip >= 0 to int64",
            "spend": "float USD (unchanged)",
            "note": (
                "Committed synthetic_ad_spend.csv is locked to seed=42 after "
                "this integer post-processing."
            ),
        },
    }


# --- Public API ---


def generate(seed: int = SEED) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build the long-format synthetic panel and planted ground-truth dict."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, periods=N_DAYS, freq="D")

    spend_by_channel: dict[str, np.ndarray] = {}
    # Shared shock so channel noise is mildly correlated across media.
    shared = rng.normal(0.0, 0.03, size=N_DAYS)
    # Fixed per-channel offset (avoid PYTHONHASHSEED-unstable hash()).
    channel_seed_offset = {ch: (i + 1) * 97 for i, ch in enumerate(CHANNELS)}
    for ch in CHANNELS:
        ch_rng = np.random.default_rng(seed + channel_seed_offset[ch])
        spend = _spend_series(ch, N_DAYS, ch_rng)
        spend = np.maximum(spend * (1.0 + shared), 0.0)
        spend_by_channel[ch] = spend

    sales, sales_meta = _baseline_sales(spend_by_channel, N_DAYS)

    rows: list[dict[str, Any]] = []
    for i, day in enumerate(dates):
        for ch in CHANNELS:
            spend = float(spend_by_channel[ch][i])
            impressions, clicks = _impressions_clicks(
                np.array([spend]), ch
            )
            rows.append(
                {
                    "date": day.strftime("%Y-%m-%d"),
                    "channel": ch,
                    "spend": spend,
                    "impressions": float(impressions[0]),
                    "clicks": float(clicks[0]),
                    "baseline_sales": float(sales[i]),
                }
            )

    df = pd.DataFrame(rows, columns=list(COLUMNS))
    df = coerce_integer_columns(df)
    assert_valid(df)

    ground_truth = planted_ground_truth()
    ground_truth["sales_meta"] = sales_meta
    ground_truth["seed_used"] = seed
    return df, ground_truth


def coerce_integer_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Round → clip ≥0 → int64 for impressions, clicks, baseline_sales."""
    out = df.copy()
    for col in INTEGER_COLUMNS:
        out[col] = (
            np.rint(out[col].to_numpy(dtype=float))
            .clip(min=0)
            .astype(np.int64)
        )
    return out


def assert_valid(df: pd.DataFrame) -> None:
    """Pandas assertions required by STORY-101 DoD."""
    if list(df.columns) != list(COLUMNS):
        raise AssertionError(f"columns must be {COLUMNS}, got {list(df.columns)}")
    if int(df.isna().sum().sum()) != 0:
        raise AssertionError("nulls present in generated frame")
    numeric = df[["spend", "impressions", "clicks", "baseline_sales"]]
    if not bool((numeric >= 0).all().all()):
        raise AssertionError("negative values in numeric columns")
    for col in INTEGER_COLUMNS:
        values = df[col].to_numpy(dtype=float)
        if not np.allclose(values, np.rint(values), equal_nan=False):
            raise AssertionError(f"{col} must be integral (no fractional part)")
    if df["channel"].nunique() != 4:
        raise AssertionError("expected 4 channels")
    if df["date"].nunique() != N_DAYS:
        raise AssertionError(f"expected {N_DAYS} unique dates")
    if len(df) != N_DAYS * len(CHANNELS):
        raise AssertionError(f"expected {N_DAYS * len(CHANNELS)} rows")


def write_outputs(
    df: pd.DataFrame,
    ground_truth: dict[str, Any],
    csv_path: Path = DEFAULT_CSV_PATH,
    gt_path: Path = DEFAULT_GT_PATH,
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    gt_path.write_text(json.dumps(ground_truth, indent=2, sort_keys=True) + "\n")


def main() -> None:
    df, ground_truth = generate(seed=SEED)
    write_outputs(df, ground_truth)
    print(f"Wrote {DEFAULT_CSV_PATH} ({len(df)} rows)")
    print(f"Wrote {DEFAULT_GT_PATH}")


if __name__ == "__main__":
    main()
