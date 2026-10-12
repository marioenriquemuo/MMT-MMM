#!/usr/bin/env python3
"""STORY-301 Step 3 — allocate budget from offline response curves.

Examples::

    conda activate mmt-mmm
    python scripts/03_allocate_budget.py \\
        --curves tests/fixtures/synthetic_response_curves.json \\
        --budget 60 --min-spend 5 --max-spend 30

    python scripts/03_allocate_budget.py \\
        --curves reports/metrics.json \\
        --target-kpi 1000 --min-spend 0 --max-spend 50000 \\
        --out reports/allocation.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.optimize.allocator import optimize_budget  # noqa: E402
from src.optimize.curves import MetricsJsonCurveProvider  # noqa: E402

DEFAULT_CURVES = REPO_ROOT / "tests" / "fixtures" / "synthetic_response_curves.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "allocation.json"


# --- CLI parsing helpers ---


def _parse_spend_arg(raw: str | None) -> float | dict[str, float] | None:
    """Scalar float, JSON object string, or ``@path`` / path to JSON file."""
    if raw is None:
        return None
    text = raw.strip()
    if text.startswith("@"):
        text = Path(text[1:]).read_text(encoding="utf-8")
    else:
        path = Path(text)
        if path.is_file() and text.endswith(".json"):
            text = path.read_text(encoding="utf-8")
    try:
        return float(text)
    except ValueError:
        pass
    data = json.loads(text)
    if isinstance(data, (int, float)):
        return float(data)
    if isinstance(data, dict):
        return {str(k): float(v) for k, v in data.items()}
    raise argparse.ArgumentTypeError(
        f"spend bound must be a number or JSON object, got {type(data).__name__}"
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="STORY-301: allocate budget (maximize KPI) or hit a KPI target."
    )
    p.add_argument(
        "--curves",
        type=Path,
        default=DEFAULT_CURVES,
        help=f"Response-curve JSON (default: {DEFAULT_CURVES.relative_to(REPO_ROOT)})",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Maximize mode: exact total spend to allocate",
    )
    mode.add_argument(
        "--target-kpi",
        type=float,
        default=None,
        dest="target_kpi",
        help="Target mode: minimize spend subject to KPI >= T",
    )
    p.add_argument(
        "--min-spend",
        type=str,
        default="0",
        help="Scalar, JSON object string, .json path, or @path (default: 0)",
    )
    p.add_argument(
        "--max-spend",
        type=str,
        default=None,
        help="Scalar / JSON / path; default = budget (maximize) or curve max (target)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output allocation JSON (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})",
    )
    return p


def run_allocate(
    curves: Path,
    *,
    budget: float | None = None,
    target_kpi: float | None = None,
    min_spend: float | dict[str, float] = 0.0,
    max_spend: float | dict[str, float] | None = None,
    out: Path | None = None,
) -> dict[str, Any]:
    """Library entrypoint (also used by tests). Writes JSON when ``out`` is set."""
    provider = MetricsJsonCurveProvider(curves)
    result = optimize_budget(
        provider,
        total_budget=budget,
        min_spend=min_spend,
        max_spend=max_spend,
        target_kpi=target_kpi,
        curve_source=str(curves),
    )
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        # Drop Step-2 aliases from on-disk JSON (plan shape only)
        payload = {
            k: result[k]
            for k in (
                "channels",
                "total_spend",
                "expected_incremental_kpi",
                "incremental_kpi_delta_vs_baseline",
                "constraints",
                "solver",
                "curve_source",
            )
        }
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    min_spend = _parse_spend_arg(args.min_spend)
    max_spend = _parse_spend_arg(args.max_spend)
    if min_spend is None:
        min_spend = 0.0

    result = run_allocate(
        args.curves,
        budget=args.budget,
        target_kpi=args.target_kpi,
        min_spend=min_spend,
        max_spend=max_spend,
        out=args.out,
    )
    ok = bool(result["solver"]["success"])
    print(json.dumps(result["solver"], indent=2))
    print(f"wrote {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
