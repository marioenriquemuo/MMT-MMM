"""STORY-302 Step 2 — offline brief, number lock, CLI exits."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.report.brief import (
    CAVEAT_KPI,
    CAVEAT_RANK,
    DEFAULT_MODEL,
    MissingApiKey,
    build_messages,
    load_api_key,
    render_live,
    render_offline,
)
from src.report.facts import build_fact_pack, numbers_match
from src.report.schema import CsuiteBrief, emit_brief_json_schema

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


def _cli():
    name = "csuite_brief_cli"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _fake_client(payload: dict, captured: dict | None = None) -> MagicMock:
    client = MagicMock()

    def create(**kwargs):
        if captured is not None:
            captured.update(kwargs)
        block = SimpleNamespace(type="tool_use", name="emit_brief", input=payload)
        return SimpleNamespace(content=[block])

    client.messages.create.side_effect = create
    return client


def _matching_payload() -> tuple[dict, dict]:
    pack = build_fact_pack(_allocation())
    return pack, render_offline(pack).model_dump()


# --- Live path (mocked client, no network) ---


def test_live_accepts_matching_tool_payload():
    pack, payload = _matching_payload()
    captured: dict = {}
    brief = render_live(pack, client=_fake_client(payload, captured), model=DEFAULT_MODEL)
    assert numbers_match(pack, brief)
    assert captured["model"] == DEFAULT_MODEL
    assert captured["tool_choice"] == {"type": "tool", "name": "emit_brief"}
    assert captured["tools"][0]["name"] == "emit_brief"
    assert captured["tools"][0]["input_schema"] == emit_brief_json_schema()


def test_live_rejects_drifted_spend_or_kpi():
    pack, payload = _matching_payload()
    drifted_spend = json.loads(json.dumps(payload))
    drifted_spend["shifts"][0]["recommended_spend"] += 1
    with pytest.raises(RuntimeError, match="do not match"):
        render_live(pack, client=_fake_client(drifted_spend))

    drifted_kpi = json.loads(json.dumps(payload))
    drifted_kpi["predicted_incremental_kpi"] += 1
    with pytest.raises(RuntimeError, match="do not match"):
        render_live(pack, client=_fake_client(drifted_kpi))

    before = OUT.read_bytes()
    code = _cli().main(
        ["--allocation", str(FIXTURE)],
        client=_fake_client(drifted_spend),
    )
    assert code != 0
    assert OUT.read_bytes() == before


def test_missing_key_names_env_and_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(MissingApiKey) as exc:
        load_api_key(tmp_path / "anthropic_api_key")
    text = str(exc.value)
    assert "ANTHROPIC_API_KEY" in text
    assert "anthropic_api_key" in text
    assert "sk-" not in text


def test_env_key_used_before_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-env-key")
    path = tmp_path / "anthropic_api_key"
    path.write_text("test-file-key\n", encoding="utf-8")
    assert load_api_key(path) == "test-env-key"


def test_failed_allocation_does_not_call_model(tmp_path: Path):
    bad = tmp_path / "failed.json"
    bad.write_text(
        json.dumps({"channels": {}, "solver": {"success": False, "message": "infeasible"}}),
        encoding="utf-8",
    )
    client = MagicMock()
    code = _cli().main(["--allocation", str(bad)], client=client)
    assert code != 0
    client.messages.create.assert_not_called()
