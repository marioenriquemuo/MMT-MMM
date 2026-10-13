#!/usr/bin/env python3
"""STORY-302 Step 2 — offline C-suite brief from an allocation JSON.

Live model calls are Step 3. This script only renders offline.

Examples::

    conda activate mmt-mmm
    python scripts/04_csuite_brief.py --offline
    python scripts/04_csuite_brief.py \\
        --allocation tests/fixtures/story_302_allocation.json --offline
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.report.brief import format_brief, render_offline  # noqa: E402
from src.report.facts import build_fact_pack  # noqa: E402

# --- Paths ---

DEFAULT_ALLOCATION = REPO_ROOT / "tests" / "fixtures" / "story_302_allocation.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "csuite_brief.json"


# --- CLI ---


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="STORY-302 offline C-suite brief")
    parser.add_argument(
        "--allocation",
        type=Path,
        default=DEFAULT_ALLOCATION,
        help="Allocation JSON (default: tests/fixtures/story_302_allocation.json)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Required. Render from the fact pack with no model call.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.offline:
        print("Live mode is Step 3. Re-run with --offline.", file=sys.stderr)
        return 2

    path = args.allocation
    if not path.is_file():
        print(f"allocation file not found: {path}", file=sys.stderr)
        return 1
    try:
        allocation = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(allocation, dict):
            raise ValueError("allocation JSON root must be an object")
        brief = render_offline(build_fact_pack(allocation))
    except (ValueError, RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(format_brief(brief), flush=True)
    DEFAULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUT.write_text(
        json.dumps(brief.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {DEFAULT_OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
