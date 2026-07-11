"""R1 #5 — researcher output contract: every claim row carries a verbatim
source quote + locator (Elicit/PaperQA2 pattern). Feeds the claim-faithfulness
check (#3) mechanically."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-researcher.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "scholar-research" / "SKILL.md").read_text(encoding="utf-8")


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
