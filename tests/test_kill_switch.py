"""Tests for the DISABLE_OMS umbrella kill switch across all 5 registered oms hooks
(R3 #22). 핵심 계약: env DISABLE_OMS in {1,true,on,yes} (case-insensitive,
whitespace-tolerant) makes every registered hook a silent no-op BEFORE it even
reads stdin — the umbrella switch that sits above each hook's own scalpel hatch
(OMS_CITE_GUARD, OMS_STOP_GUARD). Never advertised in any injected/deny/block
text (same convention those two hatches already follow)."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parent.parent / "hooks"


def run_hook(hook_path: Path, payload, disable=None) -> str:
    """훅을 서브프로세스로 실행. disable=None → env 에서 DISABLE_OMS 제거(unset).
    disable="1" 등 → 그 값으로 설정."""
    env = dict(os.environ)
    env.pop("DISABLE_OMS", None)
    if disable is not None:
        env["DISABLE_OMS"] = disable
    proc = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload) if isinstance(payload, dict) else payload,
        capture_output=True, text=True, env=env,
    )
    assert proc.returncode == 0, f"{hook_path.name} exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def route_payload(tmp_path):
    return {"prompt": "이 논문 introduction 초안 써줘"}


def cite_guard_payload(tmp_path):
    bib = tmp_path / "refs.bib"
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": str(bib), "content": "@article{smith2024,\n title={X}\n}"},
        "cwd": str(tmp_path),
    }


def verify_emit_payload(tmp_path):
    return {"tool_name": "Edit", "tool_input": {"file_path": "paper/sections/method.tex"}}


def stop_guard_payload(tmp_path):
    state_dir = tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": "s1", "active": True, "round": 1, "round_id": "round-1",
        "max_rounds": 5, "ttl_hours": 6, "strikes": {}, "stop_blocks": 0,
        "paper_root": str(tmp_path),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "live",
    }
    (state_dir / "revise-s1.json").write_text(json.dumps(data), encoding="utf-8")
    return {"hook_event_name": "Stop", "cwd": str(tmp_path), "stop_hook_active": False}


def resume_emit_payload(tmp_path):
    state_dir = tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": "s1", "stage": "draft", "gate_status": "pending",
        "open_fail_ids": [], "paper_root": str(tmp_path),
        "updated_at": "2026-07-13T00:00:00+00:00",
    }
    (state_dir / "pilot-s1.json").write_text(json.dumps(data), encoding="utf-8")
    return {"hook_event_name": "SessionStart", "source": "startup", "cwd": str(tmp_path)}


HOOKS = [
    ("scholar_route_emit.py", route_payload),
    ("scholar_cite_guard.py", cite_guard_payload),
    ("scholar_verify_emit.py", verify_emit_payload),
    ("scholar_stop_guard.py", stop_guard_payload),
    ("scholar_resume_emit.py", resume_emit_payload),
]


@pytest.mark.parametrize("hook_name,payload_builder", HOOKS)
def test_disable_oms_silences_every_hook(tmp_path, hook_name, payload_builder):
    """DISABLE_OMS=1 → every registered hook is a silent no-op, even on a
    fixture that would otherwise emit/deny/block."""
    payload = payload_builder(tmp_path)
    out = run_hook(HOOKS_DIR / hook_name, payload, disable="1")
    assert out.strip() == ""


@pytest.mark.parametrize("hook_name,payload_builder", HOOKS)
def test_disable_oms_unset_leaves_hooks_live(tmp_path, hook_name, payload_builder):
    """Same fixtures, DISABLE_OMS unset → hooks are still live (spot-check per
    family; depth is covered by each hook's own test file)."""
    payload = payload_builder(tmp_path)
    out = run_hook(HOOKS_DIR / hook_name, payload, disable=None)
    assert out.strip() != ""


@pytest.mark.parametrize("hook_name,payload_builder", HOOKS)
def test_hatch_never_advertised(tmp_path, hook_name, payload_builder):
    """DISABLE_OMS must never appear in any hook's produced stdout (injected
    additionalContext / deny reason / block reason) — same silent-hatch
    convention as OMS_CITE_GUARD / OMS_STOP_GUARD. Run WITHOUT the switch, on
    the live fixture, so there is real output to inspect."""
    payload = payload_builder(tmp_path)
    out = run_hook(HOOKS_DIR / hook_name, payload, disable=None)
    assert "DISABLE_OMS" not in out


@pytest.mark.parametrize("value", ["1", "true", "on", "yes", "TRUE", "On", " 1 ", "YES"])
def test_disable_oms_case_and_whitespace_insensitive(tmp_path, value):
    """Value matching is case-insensitive and tolerant of surrounding whitespace."""
    out = run_hook(HOOKS_DIR / "scholar_route_emit.py", route_payload(tmp_path), disable=value)
    assert out.strip() == ""


@pytest.mark.parametrize("value", ["0", "false", "no", "off", ""])
def test_disable_oms_non_matching_values_do_not_disable(tmp_path, value):
    """Only the exact allowed tokens disable — everything else leaves hooks live."""
    out = run_hook(HOOKS_DIR / "scholar_route_emit.py", route_payload(tmp_path), disable=value)
    assert out.strip() != ""
