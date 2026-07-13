"""Tests for the SessionStart resume-advisory + post-compaction Priority-Context
re-injection hook (items #9 + #13, R2).

핵심 계약: (a) cwd 로부터 nearest-first ascent 로 찾은 `.oms/`(state/ 또는
notepad.md 존재) 아래, paper_root 포함관계로 스코프에 든 non-terminal pilot
state + 그 slug 의 live revise 마커만 advisory 로 요약한다 (Stop guard 와 동일
스코핑 idiom). (b) source == "compact" 일 때만 notepad `## Priority Context`
섹션을 그대로(최대 2000자) 재주입한다 — non-terminal pilot state 유무와 무관.
(c) 아무 것도 없으면 완전 침묵(exit 0, stdout 비어있음) — 일반 세션의 injection
tax 를 0으로 유지한다."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "scholar_resume_emit.py"


def run_hook(payload, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    proc = subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload) if isinstance(payload, dict) else payload,
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def session_payload(cwd, source="startup"):
    return {"hook_event_name": "SessionStart", "source": source, "cwd": str(cwd)}


def mk_pilot(tmp_path, state_dir=None, slug="s1", **overrides):
    """Writes `.oms/state/pilot-<slug>.json`, paper_root=str(tmp_path) by default."""
    state_dir = Path(state_dir) if state_dir else tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": slug,
        "stage": "draft",
        "gate_status": "pending",
        "open_fail_ids": [],
        "paper_root": str(tmp_path),
        "updated_at": "2026-07-13T00:00:00+00:00",
    }
    data.update(overrides)
    (state_dir / f"pilot-{slug}.json").write_text(json.dumps(data), encoding="utf-8")
    return data


def mk_revise(tmp_path, state_dir=None, slug="s1", **overrides):
    """Writes `.oms/state/revise-<slug>.json`, live by default, paper_root=str(tmp_path)."""
    state_dir = Path(state_dir) if state_dir else tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": slug,
        "active": True,
        "round": 2,
        "max_rounds": 5,
        "strikes": {},
        "paper_root": str(tmp_path),
        "status": "live",
    }
    data.update(overrides)
    (state_dir / f"revise-{slug}.json").write_text(json.dumps(data), encoding="utf-8")
    return data


def mk_notepad(tmp_path, body, oms_dir=None):
    """Writes `.oms/notepad.md` with `## Priority Context` followed by another
    heading (so section extraction is bounded even without an explicit test)."""
    oms_dir = Path(oms_dir) if oms_dir else tmp_path / ".oms"
    oms_dir.mkdir(parents=True, exist_ok=True)
    content = f"## Priority Context\n{body}\n## Working Notes\nolder stuff here\n"
    (oms_dir / "notepad.md").write_text(content, encoding="utf-8")
    return content


PRIORITY_BODY = (
    "No citation fabrication. No parallel drafts. Confirm with the human before editing .bib.\n"
    "GATE 2/3\n"
    "unverified citations: kim2024, lee2025\n"
)


def test_silent_when_no_state(tmp_path):
    assert run_hook(session_payload(tmp_path)).strip() == ""


def test_advisory_names_stage_and_gate(tmp_path):
    mk_pilot(tmp_path, stage="draft", gate_status="pending")
    out = run_hook(session_payload(tmp_path))
    assert "<oms-resume>" in out
    assert "s1" in out
    assert "draft" in out
    assert "pending" in out
    assert "Advisory only" in out


def test_terminal_and_abort_states_are_silent(tmp_path):
    mk_pilot(tmp_path, slug="t1", stage="terminal", gate_status="pending")
    mk_pilot(tmp_path, slug="t2", stage="draft", gate_status="abort")
    assert run_hook(session_payload(tmp_path)).strip() == ""


def test_live_revise_marker_reported(tmp_path):
    mk_pilot(tmp_path, stage="revise", gate_status="pending")
    mk_revise(tmp_path, round=2, max_rounds=5)
    out = run_hook(session_payload(tmp_path))
    assert "2/5" in out or "round 2" in out


def test_compact_reinjects_priority_context(tmp_path):
    mk_notepad(tmp_path, PRIORITY_BODY)  # no pilot state at all
    out = run_hook(session_payload(tmp_path, source="compact"))
    assert "<oms-resume>" in out
    assert "No citation fabrication" in out
    assert "GATE 2/3" in out
    assert "unverified citations: kim2024, lee2025" in out


def test_startup_does_not_inject_priority_context_without_state(tmp_path):
    mk_notepad(tmp_path, PRIORITY_BODY)  # same fixture, no pilot state
    assert run_hook(session_payload(tmp_path, source="startup")).strip() == ""


def test_compact_bounds_priority_context(tmp_path):
    mk_notepad(tmp_path, "a" * 10000)
    out = run_hook(session_payload(tmp_path, source="compact"))
    data = json.loads(out)
    ctx = data["hookSpecificOutput"]["additionalContext"]
    run_len = len(re.search(r"a+", ctx).group(0))
    assert 1 <= run_len <= 2100


def test_sibling_cwd_not_under_paper_root_silent(tmp_path):
    mk_pilot(tmp_path, paper_root=str(tmp_path / "paperA"))
    mk_revise(tmp_path, paper_root=str(tmp_path / "paperA"))
    cwd = tmp_path / "other"
    cwd.mkdir()
    assert run_hook(session_payload(cwd)).strip() == ""


def test_output_is_wellformed_hookspecificoutput(tmp_path):
    mk_pilot(tmp_path)
    out = run_hook(session_payload(tmp_path))
    data = json.loads(out)
    assert data["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "additionalContext" in data["hookSpecificOutput"]


def test_fail_open_on_bad_input():
    assert run_hook("not json").strip() == ""


def test_fail_open_on_corrupt_notepad(tmp_path):
    dir_case = tmp_path / "dir_case"
    (dir_case / ".oms").mkdir(parents=True)
    (dir_case / ".oms" / "notepad.md").mkdir()  # notepad-is-a-directory
    assert run_hook(session_payload(dir_case, source="compact")).strip() == ""

    bytes_case = tmp_path / "bytes_case"
    (bytes_case / ".oms").mkdir(parents=True)
    (bytes_case / ".oms" / "notepad.md").write_bytes(b"## Priority Context\n\xff\xfe\x00bad")
    assert run_hook(session_payload(bytes_case, source="compact")).strip() == ""


def test_hook_is_read_only():
    src = HOOK.read_text(encoding="utf-8")
    assert "atomic_write_json" not in src
    assert "write_text(" not in src
    assert re.search(r"open\([^)]*[\"']w", src) is None
