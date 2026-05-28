"""Tests for the citation-safe PostToolUse hook.

핵심 계약: .tex/.bib 쓰기엔 검증 리마인더를 주입하되, '자동 수정'은
절대 지시하지 않는다 (경고만). 그 외 파일은 침묵. stdlib only, fail-open."""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "scholar_verify_emit.py"


def run_hook(payload: dict) -> str:
    """훅을 서브프로세스로 실행하고 stdout 반환."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def context_of(stdout: str) -> str:
    if not stdout.strip():
        return ""
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]


def test_tex_edit_injects_reminder():
    """① .tex Edit → 인용 검증 리마인더 주입."""
    out = context_of(run_hook(
        {"tool_name": "Edit", "tool_input": {"file_path": "paper/sections/method.tex"}}))
    assert "method.tex" in out
    assert "\\cite" in out or "인용" in out


def test_bib_write_injects_reminder():
    """① .bib Write → 리마인더 주입."""
    out = context_of(run_hook(
        {"tool_name": "Write", "tool_input": {"file_path": "paper/references.bib"}}))
    assert "references.bib" in out
    assert "인용" in out


def test_non_paper_file_is_silent():
    """② .tex/.bib 아닌 파일은 침묵 (예: .py 편집)."""
    out = run_hook({"tool_name": "Edit", "tool_input": {"file_path": "script.py"}})
    assert out.strip() == ""


def test_non_write_tool_is_silent():
    """② 쓰기 도구가 아니면 침묵 (예: Read)."""
    out = run_hook({"tool_name": "Read", "tool_input": {"file_path": "paper/main.tex"}})
    assert out.strip() == ""


def test_reminder_forbids_autofix_not_just_warns():
    """③ 핵심: '자동 수정' 지시가 아니라 자동수정 금지를 명시 (citation-safe).
    OMC 의 'fix before continuing' 과 달리, 인용을 자동으로 고치라고 하지 않는다."""
    out = context_of(run_hook(
        {"tool_name": "Edit", "tool_input": {"file_path": "refs.bib"}}))
    # 자동수정 금지 문구가 있어야
    assert "지어내" in out or "자동" in out
    assert "사람" in out  # 미검증 인용은 사람에게 flag


def test_stdlib_only_no_third_party_imports():
    """④ stdlib only — a2a/외부 의존 없이 import 성공 가능."""
    src = HOOK.read_text()
    # 표준 라이브러리만 import
    assert "import json" in src and "import sys" in src
    assert "import a2a" not in src and "import requests" not in src


def test_fail_open_on_bad_input():
    """⑤ fail-open: 잘못된 입력(JSON 아님)에도 exit 0, 세션 안 막음."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json at all", capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""
