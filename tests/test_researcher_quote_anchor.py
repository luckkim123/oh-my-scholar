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
    assert "references/knowledge/README.md" in SKILL, "knowledge README 경로 포인터 누락"


# =========================================================== R6 U3 (#37): Steps rework — 4-field
# delegation template, fan-out sizing/cap, interleaved gap-check, stopping heuristic, clustering.
# The load-bearing Execution_Policy sentence (parallel citation generation is prohibited) must
# survive the Steps rework byte-unchanged (D10-adjacent freeze — U1/U2 also edit this region).

def test_execution_policy_parallel_citation_prohibition_untouched():
    idx = SKILL.index("<Execution_Policy>")
    end = SKILL.index("</Execution_Policy>")
    sec = SKILL[idx:end]
    assert "parallel citation generation is prohibited" in sec


def test_step2_has_4field_delegation_template():
    assert "4-field delegation template" in SKILL
    assert re.search(r"\*\*Objective\*\*", SKILL)
    assert re.search(r"\*\*Output format\*\*", SKILL)
    assert re.search(r"\*\*Tool guidance\*\*", SKILL)
    assert re.search(r"\*\*Boundaries\*\*", SKILL)


def test_single_dispatch_not_authorized_as_parallel_fanout():
    """Acceptance sub-check (U3): the fan-out text cannot be read as authorizing
    parallel Task(mode=gap-research) dispatches — exactly one dispatch call in the body."""
    hits = re.findall(r'Task\(subagent_type="oh-my-scholar:scholar-researcher"', SKILL)
    assert len(hits) == 1
    assert "never a second parallel `mode=gap-research` dispatch" in SKILL


def test_fanout_cap_anchored_to_mock_review_precedent():
    assert "3 concurrent read batches" in SKILL
    assert "mock-review" in SKILL


def test_interleaved_gap_check():
    assert re.search(r"re-derive the gap list", SKILL)


def test_stopping_heuristic_marginal_returns():
    assert "2 consecutive batches" in SKILL
    assert "no new method family" in SKILL
    assert "no new gap" in SKILL
    assert '"until exhausted"' in SKILL
    assert "Undermind" in SKILL


def test_clustering_step_optional_and_advisory():
    assert "scripts/bib_coupling.py" in SKILL
    assert re.search(r"\boptional\b", SKILL, re.I)
    assert re.search(r"\badvisory\b", SKILL, re.I)
