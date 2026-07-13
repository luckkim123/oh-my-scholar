"""R2 #10 — verifier round-id echo. T2's `revise-round` mints a fresh round_id
per round; this task completes the other half: the verifier echoes it back so
the revise loop can detect and discard a stale/crossed verdict. Pure prompt
contract — no code changes."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-verifier.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "scholar-revise" / "SKILL.md").read_text(encoding="utf-8")

VOID_RE = re.compile(
    r"(void|discard|stale).{0,120}(round[- _]?id)|round[- _]?id.{0,120}(void|discard|stale)",
    re.I | re.S,
)


def test_agent_constraints_has_echo_instruction():
    block = AGENT[AGENT.index("<Constraints>"):AGENT.index("</Constraints>")]
    assert re.search(r"round-id", block, re.I), "Constraints 스냅샷 토큰 불릿에 round-id 지시 누락"
    assert re.search(r"echo it verbatim", block, re.I), "verbatim echo 지시 누락"


def test_agent_output_format_has_round_id_line_under_target_snapshot():
    out = AGENT[AGENT.index("<Output_Format>"):AGENT.index("</Output_Format>")]
    m = re.search(r"\*\*Target snapshot\*\*:.*\n\*\*Round ID\*\*:", out)
    assert m, "Round ID 라인이 Target snapshot 라인 바로 아래에 없음"
    assert re.search(r"echo the round-id", out, re.I), "echo 지시 문구 누락"
    assert '"none given"' in out or "none given" in out, "round-id 없을 때의 표기 누락"


def test_agent_final_checklist_has_round_id_entry():
    block = AGENT[AGENT.index("<Final_Checklist>"):AGENT.index("</Final_Checklist>")]
    assert re.search(r"round-id", block, re.I), "Final_Checklist에 round-id 항목 누락"
    assert re.search(r"verbatim", block, re.I), "verbatim 언급 누락"


def test_agent_void_if_mismatch_semantics_present():
    assert VOID_RE.search(AGENT), "verifier 파일에 void-if-mismatch 시맨틱스 누락"


def test_skill_step3b_passes_round_id_into_verifier_prompt():
    assert re.search(r"round_id.{0,200}verifier", SKILL, re.I | re.S) or \
        re.search(r"verifier.{0,200}round_id", SKILL, re.I | re.S), \
        "Step 3b가 round_id를 verifier Task 프롬프트에 넘긴다는 명시 누락"


def test_skill_void_if_mismatch_semantics_present():
    assert VOID_RE.search(SKILL), "revise SKILL에 void-if-mismatch 시맨틱스 누락"


def test_skill_discards_mismatched_or_missing_echo():
    assert re.search(r"(mismatch|missing).{0,120}echo|echo.{0,120}(mismatch|missing)", SKILL, re.I | re.S), \
        "mismatch/missing echo 시 폐기 지시 누락"
