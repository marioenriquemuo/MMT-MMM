#!/usr/bin/env python3
"""STORY-302 — C-suite brief from an allocation JSON.

``--offline`` fills the brief locally. Without it, Anthropic must call
``emit_brief``. A drifted or invalid tool payload exits non-zero and
does not write the brief.

Examples::

    conda activate mmt-mmm
    python scripts/04_csuite_brief.py --offline
    python scripts/04_csuite_brief.py \\
        --allocation tests/fixtures/story_302_allocation.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.report.brief import (  # noqa: E402
    DEFAULT_MODEL,
    MissingApiKey,
    format_brief,
    load_api_key,
    render_live,
    render_offline,
)
from src.report.facts import build_fact_pack  # noqa: E402

# --- Paths ---

DEFAULT_ALLOCATION = REPO_ROOT / "tests" / "fixtures" / "story_302_allocation.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "csuite_brief.json"


# --- CLI ---


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="STORY-302 C-suite brief")
    parser.add_argument(
        "--allocation",
        type=Path,
        default=DEFAULT_ALLOCATION,
        help="Allocation JSON (default: tests/fixtures/story_302_allocation.json)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Deterministic brief from the fact pack. No model call.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Anthropic model id for the live path (default: {DEFAULT_MODEL})",
    )
    return parser


def _redact(text: str, secret: str | None) -> str:
    if secret:
        text = text.replace(secret, "[redacted]")
    return re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[redacted]", text)


def _fail(exc: BaseException, secret: str | None) -> int:
    print(_redact(f"{type(exc).__name__}: {exc}", secret), file=sys.stderr)
    return 1


def main(argv: list[str] | None = None, *, client: Any = None) -> int:
    args = build_parser().parse_args(argv)
    path = args.allocation
    if not path.is_file():
        print(f"allocation file not found: {path}", file=sys.stderr)
        return 1

    secret: str | None = None
    try:
        allocation = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(allocation, dict):
            raise ValueError("allocation JSON root must be an object")
        pack = build_fact_pack(allocation)
        if args.offline:
            brief = render_offline(pack)
        else:
            if client is None:
                secret = load_api_key()
                import anthropic

                client = anthropic.Anthropic(api_key=secret)
            brief = render_live(pack, client=client, model=args.model)
    except MissingApiKey as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ValueError, RuntimeError, json.JSONDecodeError, OSError) as exc:
        return _fail(exc, secret)
    except Exception as exc:
        return _fail(exc, secret)

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
