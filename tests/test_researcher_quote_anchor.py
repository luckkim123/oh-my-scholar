"""R1 #5 — researcher output contract: every claim row carries a verbatim
source quote + locator (Elicit/PaperQA2 pattern). Feeds the claim-faithfulness
check (#3) mechanically."""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-researcher.md").read_text(encoding="utf-8")
SKILL = skill_md("scholar-research")


def test_agent_output_format_has_quote_anchor():
    assert re.search(r"Quote:", AGENT), "Output_Format 에 Quote 앵커 행 누락"
    assert re.search(r"verbatim", AGENT, re.I), "verbatim(원문 그대로) 계약 누락"
    assert re.search(r"locator|page|section", AGENT, re.I), "locator 계약 누락"


def test_agent_forbids_reconstructed_quotes():
    assert re.search(r"never.*(reconstruct|from memory)|reconstruct.*never", AGENT, re.I | re.S), \
        "기억 재구성 인용 금지 문구 누락"


def test_agent_quote_missing_degrade():
    assert re.search(r"quote-missing|abstract-only", AGENT, re.I), "전문 접근 불가 시 degrade 표기 누락"


def test_skill_mentions_anchoring_and_faithfulness_feed():
    assert re.search(r"quote", SKILL, re.I), "SKILL 에 quote 앵커 지시 누락"
    assert re.search(r"claim-faithfulness|faithfulness", SKILL, re.I), "verify 연계(#3 feed) 언급 누락"


# =========================================================== R5 T2 (#28): mode=deep-read addition
#
# scholar-researcher gains a second mode (mode=deep-read, for scholar-read) alongside the
# existing default mode=gap-research. These tests lock the mode split itself; the fuller
# deep-read output-contract/RETRACTED/injection-hygiene locks live in test_scholar_read_skill.py
# (which owns the new skill), so this file stays scoped to what it already owned: the quote-anchor
# contract still holding for BOTH modes after the split.

def test_agent_has_two_named_modes():
    assert "mode=gap-research" in AGENT
    assert "mode=deep-read" in AGENT
    assert re.search(r"invoked in one of two modes", AGENT, re.I)


def test_quote_anchor_contract_still_applies_to_gap_research_after_split():
    """Discriminance: the original R1 #5 Success_Criteria sentence (mode=gap-research's contract)
    was not deleted or reworded when the mode split was introduced."""
    idx = AGENT.index("<Success_Criteria>")
    end = AGENT.index("</Success_Criteria>")
    sec = AGENT[idx:end]
    assert "never reconstructed from memory" in sec
    assert "quote-missing (abstract-only)" in sec


def test_deep_read_mode_has_its_own_quote_anchor_reuse_note():
    idx = AGENT.index("### mode=deep-read")
    end = AGENT.index("</Investigation_Protocol>")
    sec = AGENT[idx:end]
    assert re.search(r"same quote-anchor contract as mode=gap-research", sec, re.I)


# =========================================================== R6 U1 (#35): citation_lookup() pointer
def test_skill_points_to_citation_lookup_contract():
    assert re.search(r"citation_lookup\(", SKILL), "citation_lookup() 계약 포인터 누락"
    assert "references/wiki/README.md" in SKILL, "wiki README 경로 포인터 누락"
