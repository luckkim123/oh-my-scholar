"""R1 #3 — "citation exists" ≠ "citation supports this claim". verify gains a
claim-faithfulness sub-check (stance: supports/contrasts/mentions) sourced from
the researcher's quote anchors. WARN + human list, never auto-fix, never guess
without an anchor."""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-verifier.md").read_text(encoding="utf-8")
SKILL = skill_md("scholar-verify")


def test_agent_has_citation_misuse_check():
    assert "citation-misuse" in AGENT
    assert re.search(r"supports.*contrasts.*mentions", AGENT, re.S), "3-stance 라벨 누락"


def test_agent_check_is_warn_and_human_flagged():
    block = AGENT[AGENT.index("citation-misuse"):]
    assert re.search(r"WARN", block), "citation-misuse 는 WARN 급이어야"
    assert re.search(r"human", block, re.I), "human-confirmation 연결 누락"


def test_agent_no_anchor_means_not_run_not_guessed():
    assert re.search(r"(no|without).{0,40}anchor.{0,120}(not run|manual|never guess)", AGENT, re.I | re.S), \
        "앵커 부재 시 '미실행/사람 확인' 처리 누락 (추측 금지)"


def test_agent_output_table_has_row():
    assert re.search(r"claim-faithfulness", AGENT), "Output_Format 표에 행 누락"


def test_skill_step_names_the_check():
    assert "citation-misuse" in SKILL or "claim-faithfulness" in SKILL
    assert re.search(r"quote anchor", SKILL, re.I), "research 노트 앵커 소스 명시 누락"
