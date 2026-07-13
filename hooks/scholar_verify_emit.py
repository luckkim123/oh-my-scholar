"""oms PostToolUse hook: when a .tex/.bib file is edited/written, inject a
citation-integrity reminder (stdlib only, fail-open).

This is the citation-SAFE variant of OMC's post-tool-verifier. OMC injects
"fix before continuing" on write — for citation-bound paper work that would
push the model to *auto-fix* (i.e. invent) citations. So this hook only
REMINDS to verify; it never instructs an auto-fix, and explicitly forbids
fabricating citations / editing .bib without human confirmation.

R3 #22: env DISABLE_OMS (1/true/on/yes) is the umbrella kill switch shared by
all 5 registered oms hooks, checked first, before stdin -- never advertised
in the injected reminder."""
import json
import os
import sys

PAPER_EXTS = (".tex", ".bib")
WRITE_TOOLS = ("Edit", "Write", "MultiEdit")


def extract_file_path(tool_input: dict) -> str:
    # Edit/Write use file_path; MultiEdit too. Be liberal, fail-open.
    return tool_input.get("file_path", "") or tool_input.get("path", "")


def build_reminder(file_path: str) -> str:
    return (
        f"[oms citation-integrity reminder] `{file_path}` 수정됨.\n"
        "- 인용(\\cite)·수치·그림 참조가 .bib/표/그림과 정합하는지 scholar-verify 로 확인할 것.\n"
        "- ⚠️ 인용을 자동으로 지어내거나 .bib 를 사람 확인 없이 추가하지 말 것 "
        "(citation hallucination 이 가장 위험). 미검증 인용은 사람에게 flag.\n"
        "- 큰 수정이면 버전 스냅샷이 떠졌는지 확인."
    )


def _disable_oms() -> bool:
    try:
        return os.environ.get("DISABLE_OMS", "").strip().lower() in ("1", "true", "on", "yes")
    except Exception:
        return False  # env-read exception -> proceed as if unset


def main() -> int:
    if _disable_oms():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # fail-open: 입력 파싱 실패해도 세션 막지 않음

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    file_path = extract_file_path(tool_input)

    # .tex/.bib 쓰기 도구일 때만 리마인더. 그 외엔 침묵.
    if tool_name not in WRITE_TOOLS or not file_path.endswith(PAPER_EXTS):
        return 0

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": build_reminder(file_path),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
