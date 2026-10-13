"""STORY-302 Step 2 — offline brief, number lock, CLI exits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.report.brief import CAVEAT_KPI, CAVEAT_RANK, build_messages, render_offline
from src.report.facts import build_fact_pack, numbers_match
from src.report.schema import CsuiteBrief

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "story_302_allocation.json"
SCRIPT = REPO / "scripts" / "04_csuite_brief.py"
OUT = REPO / "reports" / "csuite_brief.json"


def _allocation() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )


# --- Offline brief ---


def test_offline_brief_validates_and_locks_numbers():
    pack = build_fact_pack(_allocation())
    brief = render_offline(pack)
    again = CsuiteBrief.model_validate(brief.model_dump())
    assert again == brief
    assert numbers_match(pack, brief)
    assert 3 <= len(brief.bullets) <= 6

    text = " ".join(brief.bullets)
    assert "Budget shift" in text
    assert "near_ceiling" in text
    assert "ok" in text
    assert "lift vs baseline" in text
    assert CAVEAT_KPI in brief.caveats
    assert CAVEAT_RANK in brief.caveats

    messages = build_messages(pack)
    assert "alpha" in messages["user"]
    assert "27" in messages["user"]
    assert ".csv" not in messages["user"]
    assert "incremental KPI" in messages["system"]
    assert "Path-C" in messages["system"]


def test_null_delta_does_not_invent_lift():
    allocation = _allocation()
    allocation["incremental_kpi_delta_vs_baseline"] = None
    pack = build_fact_pack(allocation)
    brief = render_offline(pack)
    assert brief.incremental_kpi_delta_vs_baseline is None
    assert numbers_match(pack, brief)
    lift = next(b for b in brief.bullets if "Lift vs baseline" in b)
    assert "not computed" in lift
    assert "+" not in lift


def test_lock_failure_refuses_the_brief(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("src.report.brief.numbers_match", lambda *_args, **_kwargs: False)
    pack = build_fact_pack(_allocation())
    with pytest.raises(RuntimeError, match="do not match"):
        render_offline(pack)


# --- CLI ---


def test_cli_prints_offline_brief_and_writes_json():
    proc = _run(
        "--allocation",
        str(FIXTURE),
        "--offline",
    )
    assert proc.returncode == 0, proc.stderr
    assert "Move alpha up" in proc.stdout
    assert "near_ceiling" in proc.stdout
    assert CAVEAT_KPI in proc.stdout
    assert CAVEAT_RANK in proc.stdout

    saved = json.loads(OUT.read_text(encoding="utf-8"))
    brief = CsuiteBrief.model_validate(saved)
    assert numbers_match(build_fact_pack(_allocation()), brief)
    assert saved["predicted_incremental_kpi"] == 33.45


def test_cli_failed_allocation_exits_nonzero(tmp_path: Path):
    bad = tmp_path / "failed.json"
    bad.write_text(
        json.dumps(
            {
                "channels": {},
                "solver": {"success": False, "message": "infeasible"},
            }
        ),
        encoding="utf-8",
    )
    proc = _run("--allocation", str(bad), "--offline")
    assert proc.returncode != 0
    assert proc.returncode != 2
    assert "no fact pack" in proc.stderr


def test_cli_without_offline_exits_2():
    proc = _run("--allocation", str(FIXTURE))
    assert proc.returncode == 2
    assert "Step 3" in proc.stderr
