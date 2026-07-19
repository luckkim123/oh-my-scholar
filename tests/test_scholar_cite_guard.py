"""Tests for the PreToolUse citation-write interlock (item #1, R1).

핵심 계약: 미검증 새 .bib entry / dangling \cite 는 deny-with-feedback 으로
구조적으로 차단하되, 절대 auto-fix 를 지시하지 않는다. 그 외엔 침묵·fail-open."""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "scholar_cite_guard.py"


def run_hook(payload, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    env.pop("OMS_CITE_GUARD", None) if env_extra is None else None
    proc = subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload) if isinstance(payload, dict) else payload,
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def decision_of(stdout):
    if not stdout.strip():
        return None
    return json.loads(stdout)["hookSpecificOutput"]


def bib_payload(path, content, tool="Write", old="", cwd=None):
    ti = {"file_path": str(path)}
    if tool == "Write":
        ti["content"] = content
    else:
        ti.update({"old_string": old, "new_string": content})
    p = {"tool_name": tool, "tool_input": ti}
    if cwd:
        p["cwd"] = str(cwd)
    return p


def test_new_unverified_bib_entry_denied(tmp_path):
    bib = tmp_path / "refs.bib"
    out = decision_of(run_hook(bib_payload(bib, "@article{smith2024,\n title={X}\n}", cwd=tmp_path)))
    assert out and out["permissionDecision"] == "deny"
    assert "smith2024" in out["permissionDecisionReason"]
    assert "verify_bib_entry" in out["permissionDecisionReason"]


def test_allowlisted_key_passes(tmp_path):
    state = tmp_path / ".oms" / "state"
    state.mkdir(parents=True)
    (state / "verified-citations.json").write_text(json.dumps({"keys": {"smith2024": {"doi": "10.1/x"}}}))
    bib = tmp_path / "refs.bib"
    out = run_hook(bib_payload(bib, "@article{smith2024,\n title={X}\n}", cwd=tmp_path))
    assert out.strip() == ""


def test_editing_existing_entry_allowed(tmp_path):
    bib = tmp_path / "refs.bib"
    bib.write_text("@article{kim2023,\n title={Old}\n}")
    out = run_hook(bib_payload(bib, "@article{kim2023,\n title={New}\n}", tool="Edit",
                               old="@article{kim2023,\n title={Old}\n}", cwd=tmp_path))
    assert out.strip() == ""


def test_dangling_cite_in_tex_denied(tmp_path):
    (tmp_path / "refs.bib").write_text("@article{real2020,\n title={R}\n}")
    tex = tmp_path / "main.tex"
    out = decision_of(run_hook(bib_payload(tex, r"as shown \cite{ghost2025}", cwd=tmp_path)))
    assert out and out["permissionDecision"] == "deny"
    assert "ghost2025" in out["permissionDecisionReason"]


def test_cite_of_existing_key_allowed(tmp_path):
    (tmp_path / "refs.bib").write_text("@article{real2020,\n title={R}\n}")
    tex = tmp_path / "sections" / "intro.tex"
    tex.parent.mkdir()
    out = run_hook(bib_payload(tex, r"\cite{real2020}", cwd=tmp_path))  # parent-dir .bib
    assert out.strip() == ""


def test_tex_without_any_bib_fails_open(tmp_path):
    out = run_hook(bib_payload(tmp_path / "main.tex", r"\cite{x2020}", cwd=tmp_path))
    assert out.strip() == ""


def test_non_paper_and_non_write_are_silent(tmp_path):
    assert run_hook({"tool_name": "Edit", "tool_input": {"file_path": "a.py", "new_string": "@x{y,}"}}).strip() == ""
    assert run_hook({"tool_name": "Read", "tool_input": {"file_path": "refs.bib"}}).strip() == ""


def test_fail_open_on_bad_input():
    assert run_hook("not json").strip() == ""


def test_env_escape_hatch(tmp_path):
    out = run_hook(bib_payload(tmp_path / "refs.bib", "@article{new2025,\n t={x}\n}", cwd=tmp_path),
                   env_extra={"OMS_CITE_GUARD": "off"})
    assert out.strip() == ""


def test_deny_reason_never_instructs_autofix(tmp_path):
    out = decision_of(run_hook(bib_payload(tmp_path / "refs.bib", "@misc{k2025,\n t={x}\n}", cwd=tmp_path)))
    reason = out["permissionDecisionReason"]
    assert "fabricat" in reason or "지어내" in reason or "invent" in reason  # forbids invention
    assert "OMS_CITE_GUARD" not in reason  # never advertises the bypass to the model


def test_stdlib_only():
    src = HOOK.read_text()
    assert "import requests" not in src and "import a2a" not in src
