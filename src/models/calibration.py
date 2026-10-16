"""STORY-503: tighten the national ROI prior from geo-experiment bounds.

Reads a JSON experiment list and replaces ``roi_m`` only for channels that
match this client's channel list and region label. Does not sample a posterior
and does not build a city model. Bounds are not Path-C ground truth.
``GAP-201-RANK`` stays open.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from scipy.stats import norm

from src.data.tenants import load_client, resolve_client_path
from src.models.meridian_data import CHANNEL_ORDER

# Relative slack so a float round-trip still counts as inside the experiment.
_INSIDE_TOL = 1e-6


# --- Interval ---


def loc_scale(low: float, high: float, confidence: float) -> tuple[float, float]:
    """Log-normal ``loc``/``scale`` whose central interval is ``[low, high]``."""
    z = float(norm.ppf((1.0 + confidence) / 2.0))
    log_low = math.log(low)
    log_high = math.log(high)
    return (log_low + log_high) / 2.0, (log_high - log_low) / (2.0 * z)


def central_bounds(loc: float, scale: float, confidence: float) -> tuple[float, float]:
    """Endpoints of the log-normal central interval at ``confidence``."""
    z = float(norm.ppf((1.0 + confidence) / 2.0))
    return math.exp(loc - z * scale), math.exp(loc + z * scale)


def _inside(got_low: float, got_high: float, low: float, high: float) -> bool:
    return got_low >= low - _INSIDE_TOL * max(low, 1.0) and got_high <= high + _INSIDE_TOL * max(
        high, 1.0
    )


# --- Rows ---


def ordered_channels(names: list[str]) -> list[str]:
    """Client channels in ``CHANNEL_ORDER``, then any name that order does not list."""
    chosen = [channel for channel in CHANNEL_ORDER if channel in names]
    return chosen + [channel for channel in names if channel not in chosen]


def region_label(client: dict[str, Any]) -> str:
    """The single region label on this client (``national`` for pathc and wellness)."""
    regions = [str(region) for region in client["regions"]]
    if len(regions) != 1:
        raise ValueError(f"{client['client_id']} has {len(regions)} region labels")
    return regions[0]


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _usable(row: dict[str, Any], channels: set[str], region: str) -> bool:
    if row.get("metric") != "roi":
        return False
    if row.get("channel") not in channels or row.get("region") != region:
        return False
    low, high, confidence = _number(row.get("low")), _number(row.get("high")), _number(
        row.get("confidence")
    )
    if low is None or high is None or confidence is None:
        return False
    return low > 0 and low < high and 0 < confidence < 1


def matched_experiments(
    rows: list[dict[str, Any]], channels: list[str], region: str
) -> dict[str, dict[str, float]]:
    """First usable ROI row per channel. Other rows, including ``bogota``, are ignored."""
    allowed = set(channels)
    found: dict[str, dict[str, float]] = {}
    for row in rows:
        if not isinstance(row, dict) or not _usable(row, allowed, region):
            continue
        channel = str(row["channel"])
        if channel in found:
            continue
        low, high = float(row["low"]), float(row["high"])
        confidence = float(row["confidence"])
        loc, scale = loc_scale(low, high, confidence)
        found[channel] = {
            "low": low,
            "high": high,
            "confidence": confidence,
            "loc": loc,
            "scale": scale,
        }
    return found


def load_experiments(path: Path) -> list[dict[str, Any]]:
    """Load the ``experiments`` list. A missing file is the caller's choice."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("experiments"), list):
        raise ValueError(f"{path} needs an experiments list")
    return payload["experiments"]


# --- Prior ---


def default_roi_params() -> tuple[float, float]:
    """Uncalibrated ``roi_m`` loc and scale from Meridian's default prior."""
    import numpy as np
    from meridian.model.prior_distribution import PriorDistribution

    roi = PriorDistribution().roi_m
    loc = np.asarray(roi.loc)
    scale = np.asarray(roi.scale)
    if loc.shape != () or scale.shape != ():
        raise ValueError("expected a scalar default roi_m prior")
    return float(loc), float(scale)


def roi_prior(channels: list[str], rows: list[dict[str, Any]], region: str):
    """``PriorDistribution`` with ``roi_m`` replaced only for matched channels."""
    import numpy as np
    from meridian import backend
    from meridian.model.prior_distribution import PriorDistribution

    base = PriorDistribution()
    loc0, scale0 = default_roi_params()
    matched = matched_experiments(rows, channels, region)
    if not matched:
        return base
    locs = [matched[channel]["loc"] if channel in matched else loc0 for channel in channels]
    scales = [matched[channel]["scale"] if channel in matched else scale0 for channel in channels]
    roi_m = backend.tfd.LogNormal(
        np.asarray(locs, dtype=backend.np_float_dtype),
        np.asarray(scales, dtype=backend.np_float_dtype),
        name=base.roi_m.name,
    )
    return PriorDistribution(roi_m=roi_m)


def model_spec(channels: list[str], rows: list[dict[str, Any]], *, max_lag: int, region: str):
    """Spike ``ModelSpec`` with the calibrated ``roi_m`` prior."""
    from meridian.model import spec

    return spec.ModelSpec(
        prior=roi_prior(channels, rows, region),
        media_effects_dist="log_normal",
        hill_before_adstock=False,
        max_lag=max_lag,
        unique_sigma_for_each_geo=False,
        media_prior_type="roi",
        adstock_decay_spec="geometric",
        enable_aks=False,
    )


# --- Report ---


def build_report(client: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[dict[str, Any], bool]:
    """Per-channel before/after prior. The bool is false when a calibrated row fails the gate."""
    region = region_label(client)
    channels = ordered_channels([str(channel) for channel in client["channels"]])
    loc0, scale0 = default_roi_params()
    matched = matched_experiments(rows, channels, region)
    records: list[dict[str, Any]] = []
    ok = True
    for channel in channels:
        if channel not in matched:
            records.append(
                {
                    "channel": channel,
                    "calibrated": False,
                    "experiment_interval": None,
                    "before": {"loc": loc0, "scale": scale0},
                    "after": {"loc": loc0, "scale": scale0},
                    "inside_experiment_interval": None,
                    "scale_tightened": False,
                }
            )
            continue
        item = matched[channel]
        got_low, got_high = central_bounds(item["loc"], item["scale"], item["confidence"])
        inside = _inside(got_low, got_high, item["low"], item["high"])
        tightened = item["scale"] < scale0
        if not inside or not tightened:
            ok = False
        records.append(
            {
                "channel": channel,
                "calibrated": True,
                "experiment_interval": {
                    "low": item["low"],
                    "high": item["high"],
                    "confidence": item["confidence"],
                },
                "before": {"loc": loc0, "scale": scale0},
                "after": {"loc": item["loc"], "scale": item["scale"]},
                "inside_experiment_interval": inside,
                "scale_tightened": tightened,
            }
        )
    report = {"client_id": client["client_id"], "region": region, "channels": records}
    return report, ok


def gate_reasons(report: dict[str, Any]) -> list[str]:
    """Why ``build_report`` rejected a calibrated channel. Empty when the gate passes."""
    reasons: list[str] = []
    for row in report["channels"]:
        if not row["calibrated"]:
            continue
        channel = row["channel"]
        if row["inside_experiment_interval"] is not True:
            reasons.append(f"{channel}: central interval misses the experiment bounds")
        if not row["scale_tightened"]:
            reasons.append(f"{channel}: scale is not tighter than the default prior")
    return reasons


def run(client_id: str, experiments: str | Path, out: str | Path) -> int:
    """Resolve both paths, write the delta report, and return 0 or 1."""
    client = load_client(client_id)
    src = resolve_client_path(client_id, experiments)
    dest = resolve_client_path(client_id, out)
    rows = load_experiments(src) if src.is_file() else []
    report, ok = build_report(client, rows)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    """CLI: ``python -m src.models.calibration``."""
    parser = argparse.ArgumentParser(description="STORY-503 geo-experiment ROI prior")
    parser.add_argument("--client_id", default="pathc")
    parser.add_argument(
        "--experiments",
        type=Path,
        default=None,
        help="Experiment JSON (default: this client's raw/calibration/geo_experiment.json)",
    )
    args = parser.parse_args(argv)
    client = load_client(args.client_id)
    experiments = args.experiments or (
        client["roots"]["raw"] / "calibration" / "geo_experiment.json"
    )
    out = client["roots"]["reports"] / "calibration_delta.json"
    code = run(args.client_id, experiments, out)
    print(f"wrote {resolve_client_path(args.client_id, out)}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
