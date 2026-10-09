#!/usr/bin/env python3
"""STORY-201 Meridian national MMM spike (smoke + fuller MCMC).

Examples::

    conda activate mmt-mmm
    python -m src.data.etl && python -m src.data.qa
    python scripts/02_model_spike.py --mode smoke
    python scripts/02_model_spike.py --mode full

Fuller mode writes ``reports/metrics.json``,
``reports/figures/posterior_predictive.png``, and
``reports/parameter_recovery.md``. Exits non-zero if max R-hat on core
params ≥ 1.05.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from meridian.analysis import analyzer  # noqa: E402
from meridian.model import model, prior_distribution, spec  # noqa: E402

from src.models.meridian_data import DEFAULT_PARQUET, load_meridian_input  # noqa: E402

REPORTS = REPO_ROOT / "reports"
FIGURES = REPORTS / "figures"
METRICS_PATH = REPORTS / "metrics.json"
PPC_PATH = FIGURES / "posterior_predictive.png"
RECOVERY_PATH = REPORTS / "parameter_recovery.md"
GROUND_TRUTH = REPO_ROOT / "data" / "raw" / "ground_truth.json"

# Smallest configs that still exercise Meridian MCMC on CPU.
SMOKE = dict(n_chains=2, n_adapt=50, n_burnin=20, n_keep=20, n_prior=50)
# Lean fuller: aim R-hat < 1.05 without multi-hour runtime on laptop CPU.
FULL = dict(n_chains=4, n_adapt=500, n_burnin=200, n_keep=400, n_prior=200)

CORE_RHAT_PREFIXES = (
    "media_channel",
    "roi_m",
    "alpha_m",
    "ec_m",
    "slope_m",
    "beta_m",
    "beta_gm",
    "mu_t",
    "knot",
    "tau_g",
    "gamma",
    "sigma",
)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--mode",
        choices=("smoke", "full"),
        default="smoke",
        help="smoke = short chains; full = DoD MCMC + artifacts",
    )
    p.add_argument("--parquet", type=Path, default=DEFAULT_PARQUET)
    p.add_argument(
        "--freq",
        choices=("W", "D"),
        default="W",
        help="time grain for Meridian InputData (default weekly)",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--rhat-threshold",
        type=float,
        default=1.05,
        help="fail full mode if max core R-hat ≥ this (default 1.05)",
    )
    p.add_argument("--n-chains", type=int, default=None)
    p.add_argument("--n-adapt", type=int, default=None)
    p.add_argument("--n-burnin", type=int, default=None)
    p.add_argument("--n-keep", type=int, default=None)
    return p.parse_args()


def _mcmc_cfg(args: argparse.Namespace) -> dict:
    base = dict(SMOKE if args.mode == "smoke" else FULL)
    for key, attr in (
        ("n_chains", "n_chains"),
        ("n_adapt", "n_adapt"),
        ("n_burnin", "n_burnin"),
        ("n_keep", "n_keep"),
    ):
        val = getattr(args, attr)
        if val is not None:
            base[key] = val
    return base


def _build_mmm(input_data, *, max_lag: int = 8):
    model_spec = spec.ModelSpec(
        prior=prior_distribution.PriorDistribution(),
        media_effects_dist="log_normal",
        hill_before_adstock=False,
        max_lag=max_lag,
        unique_sigma_for_each_geo=False,
        media_prior_type="roi",
        adstock_decay_spec="geometric",
        enable_aks=False,
    )
    return model.Meridian(input_data=input_data, model_spec=model_spec)


def _core_rhat_rows(rhat_df: pd.DataFrame) -> pd.DataFrame:
    if rhat_df is None or rhat_df.empty:
        return pd.DataFrame()
    name_col = "parameter" if "parameter" in rhat_df.columns else rhat_df.columns[0]
    mask = rhat_df[name_col].astype(str).apply(
        lambda n: any(n.startswith(p) or p in n for p in CORE_RHAT_PREFIXES)
    )
    return rhat_df.loc[mask].copy()


def _rhat_peek(mmm, threshold: float) -> dict:
    an = analyzer.Analyzer(mmm)
    summary = an.rhat_summary(bad_rhat_threshold=threshold)
    core = _core_rhat_rows(summary)
    max_col = "max_r_hat" if "max_r_hat" in summary.columns else summary.columns[-1]
    max_all = float(summary[max_col].max()) if len(summary) else float("nan")
    max_core = float(core[max_col].max()) if len(core) else max_all
    print("\n=== R-hat summary (peek) ===")
    print(summary.to_string(index=False))
    print(f"max R-hat (all)={max_all:.4f}  max R-hat (core)={max_core:.4f}")
    return {
        "rhat_summary": summary.to_dict(orient="records"),
        "max_rhat_all": max_all,
        "max_rhat_core": max_core,
        "rhat_pass": bool(max_core < threshold),
        "rhat_threshold": threshold,
    }


def _roi_by_channel(mmm) -> dict[str, float]:
    an = analyzer.Analyzer(mmm)
    channels = list(mmm.input_data.media.coords["media_channel"].values)
    # use_kpi=True → incremental units / spend (iROAS-like for non_revenue KPI)
    roi = np.asarray(an.roi(use_posterior=True, use_kpi=True))
    # Expected shape: (n_chains, n_draws, n_channels) or similar — take mean.
    while roi.ndim > 1:
        roi = roi.mean(axis=0)
    return {ch: float(v) for ch, v in zip(channels, roi)}


def _response_curve_summary(mmm) -> dict:
    an = analyzer.Analyzer(mmm)
    curves = an.response_curves(use_posterior=True, use_kpi=True)
    out: dict = {"coords": {}, "means": {}}
    for name, coord in curves.coords.items():
        out["coords"][name] = [str(x) for x in coord.values]
    # Store mean incremental outcome across posterior for each spend multiplier.
    data_vars = {}
    for var in curves.data_vars:
        arr = np.asarray(curves[var])
        data_vars[var] = {
            "shape": list(arr.shape),
            "mean": float(np.nanmean(arr)),
            "std": float(np.nanstd(arr)),
        }
    out["data_vars"] = data_vars
    return out


def _posterior_summaries(mmm) -> dict:
    an = analyzer.Analyzer(mmm)
    try:
        sm = an.summary_metrics(use_kpi=True, aggregate_geos=True, aggregate_times=True)
        summary = {}
        for var in sm.data_vars:
            arr = np.asarray(sm[var])
            summary[var] = {
                "mean": float(np.nanmean(arr)),
                "std": float(np.nanstd(arr)),
                "shape": list(arr.shape),
            }
        return summary
    except Exception as exc:  # pragma: no cover - defensive for Meridian API drift
        return {"error": str(exc)}


def _write_ppc(mmm, path: Path) -> None:
    an = analyzer.Analyzer(mmm)
    eva = an.expected_vs_actual_data(
        aggregate_geos=True, aggregate_times=False, use_kpi=True
    )
    # Common var names across Meridian versions.
    actual_name = next(
        (v for v in ("actual", "kpi", "outcome") if v in eva), list(eva.data_vars)[0]
    )
    expected_name = next(
        (
            v
            for v in ("expected", "expected_outcome", "mean", "prediction")
            if v in eva
        ),
        [v for v in eva.data_vars if v != actual_name][0],
    )
    actual = np.asarray(eva[actual_name]).reshape(-1)
    expected = np.asarray(eva[expected_name]).reshape(-1)
    # If expected still has chain/draw dims collapsed poorly, take nanmean trailing.
    if expected.shape != actual.shape:
        # Broadcast / reduce trailing dims.
        while expected.ndim > 1 and expected.shape[-1] == actual.shape[0]:
            expected = expected.mean(axis=tuple(range(expected.ndim - 1)))
        expected = expected.reshape(-1)[: actual.shape[0]]

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(actual, label="actual KPI", color="#333333", linewidth=1.2)
    ax.plot(expected, label="posterior expected", color="#1f77b4", linewidth=1.2)
    ax.set_title("Meridian posterior predictive (national, weekly)")
    ax.set_xlabel("time index")
    ax.set_ylabel("KPI (units)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f"wrote {path}")


def _parameter_recovery(iroas: dict[str, float]) -> str:
    truth = json.loads(GROUND_TRUTH.read_text()) if GROUND_TRUTH.is_file() else {}
    contrib = truth.get("sales_meta", {}).get("channel_contribution_means", {})
    beta = truth.get("media_beta", {})
    decay = truth.get("adstock_decay", {})

    est_rank = sorted(iroas, key=iroas.get, reverse=True)
    truth_rank = sorted(contrib, key=contrib.get, reverse=True) if contrib else []

    lines = [
        "# Parameter recovery note (STORY-201)",
        "",
        "Directional check only — Meridian ROI / Hill parameterization ≠ Path-C",
        "`media_beta` × geometric adstock × Hill saturation. Compare ranks, not",
        "point estimates.",
        "",
        "## Estimated iROAS (posterior mean, units per $)",
        "",
    ]
    for ch, v in sorted(iroas.items(), key=lambda kv: -kv[1]):
        lines.append(f"- `{ch}`: {v:.4f}")
    lines.extend(["", "## Path-C planted signals", ""])
    if contrib:
        lines.append("Channel contribution means (units):")
        for ch, v in sorted(contrib.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{ch}`: {v:.2f}")
    if beta:
        lines.append("")
        lines.append("media_beta (DGP scale):")
        for ch, v in sorted(beta.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{ch}`: {v}")
    if decay:
        lines.append("")
        lines.append("adstock_decay (higher = longer memory):")
        for ch, v in sorted(decay.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{ch}`: {v}")

    lines.extend(
        [
            "",
            "## Rank comparison",
            "",
            f"- Meridian iROAS rank: {est_rank}",
            f"- Path-C contribution rank: {truth_rank}",
        ]
    )
    if est_rank and truth_rank:
        # Spearmans on overlapping channels.
        common = [c for c in truth_rank if c in est_rank]
        if len(common) >= 2:
            t_ranks = {c: i for i, c in enumerate(truth_rank)}
            e_ranks = {c: i for i, c in enumerate(est_rank)}
            n = len(common)
            d2 = sum((t_ranks[c] - e_ranks[c]) ** 2 for c in common)
            spearman = 1 - 6 * d2 / (n * (n * n - 1))
            lines.append(f"- Spearman rank correlation (iROAS vs contribution): {spearman:.3f}")
            if spearman > 0:
                lines.append(
                    "- Verdict: **directional match** (positive rank correlation)."
                )
            else:
                lines.append(
                    "- Verdict: **directional mismatch** — investigate media scaling / priors."
                )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = _parse_args()
    cfg = _mcmc_cfg(args)
    print(f"mode={args.mode} freq={args.freq} parquet={args.parquet}")
    print(f"mcmc={cfg}")

    if not args.parquet.is_file():
        print(
            f"missing {args.parquet}; run: python -m src.data.etl && python -m src.data.qa",
            file=sys.stderr,
        )
        return 2

    input_data = load_meridian_input(args.parquet, freq=args.freq)
    print(
        f"InputData: times={input_data.kpi.shape[1]} "
        f"channels={list(input_data.media.coords['media_channel'].values)}"
    )

    max_lag = 8 if args.freq == "W" else 28
    mmm = _build_mmm(input_data, max_lag=max_lag)
    mmm.sample_prior(cfg["n_prior"], seed=args.seed)
    print("sampling posterior…")
    mmm.sample_posterior(
        n_chains=cfg["n_chains"],
        n_adapt=cfg["n_adapt"],
        n_burnin=cfg["n_burnin"],
        n_keep=cfg["n_keep"],
        seed=args.seed,
    )

    rhat_info = _rhat_peek(mmm, args.rhat_threshold)

    if args.mode == "smoke":
        print("smoke OK — R-hat peek printed above")
        return 0

    # --- Fuller DoD artifacts ---
    REPORTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    iroas = _roi_by_channel(mmm)
    print("iROAS (posterior mean):", iroas)
    response = _response_curve_summary(mmm)
    post_sum = _posterior_summaries(mmm)
    _write_ppc(mmm, PPC_PATH)

    recovery_md = _parameter_recovery(iroas)
    RECOVERY_PATH.write_text(recovery_md)
    print(f"wrote {RECOVERY_PATH}")

    metrics = {
        "story": "STORY-201",
        "mode": args.mode,
        "freq": args.freq,
        "mcmc": cfg,
        "seed": args.seed,
        "n_times": int(input_data.kpi.shape[1]),
        "channels": list(input_data.media.coords["media_channel"].values),
        "rhat": rhat_info,
        "iroas_units_per_dollar": iroas,
        "posterior_summaries": post_sum,
        "response_curves": response,
        "artifacts": {
            "metrics": str(METRICS_PATH.relative_to(REPO_ROOT)),
            "posterior_predictive": str(PPC_PATH.relative_to(REPO_ROOT)),
            "parameter_recovery": str(RECOVERY_PATH.relative_to(REPO_ROOT)),
        },
        "dod": {
            "rhat_lt_1_05": rhat_info["rhat_pass"],
            "metrics_json": True,
            "ppc_png": PPC_PATH.is_file(),
            "parameter_recovery": RECOVERY_PATH.is_file(),
        },
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"wrote {METRICS_PATH}")

    if not rhat_info["rhat_pass"]:
        print(
            f"FAIL: max core R-hat {rhat_info['max_rhat_core']:.4f} "
            f">= {args.rhat_threshold}",
            file=sys.stderr,
        )
        return 1
    print("full DoD: R-hat PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
