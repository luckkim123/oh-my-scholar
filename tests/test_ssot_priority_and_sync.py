r"""Tests for two harness-mechanism fixes — SSOT reading priority + .tex↔.oms sync.

배경(2026-06-02): 특정 석사논문 §2.3.3 사실검증 중 두 결함이 드러났다.

결함 A — SSOT 우선순위 미강제. 사실검증(scholar-inspect 맥락)이 1차 SSOT
(`.oms/<slug>/outline/outline.md` + `methodology/*.md`)가 아니라 2차 자료
(`research_summary/code_survey/*`)부터 읽혀, 구조 재설계로 stale된 노트의 "Chapter 3 =
mapping" 매핑을 현행 §3(=ROV control)에 갖다 대 챕터축·스코프를 오판했다. 원인: inspect
SKILL Steps 가 .tex 만 읽으라 하고 outline·methodology 를 먼저 보라는 강제가 없었음.

결함 B — `.tex`↔`.oms` 동기화 미강제. .tex 구조 변경(절 이동·제목 변경·수식 교체·\cite
추가)을 해도 같은 작업 안에서 outline·methodology·결정기록을 갱신하라는 완료조건이 없어
.oms 가 stale 로 남는 drift 발생. omp 의 "organize 후 인덱스 sync 완료조건 명문화"와 동형.

처방(범용 배포): learning-protocol.md §8(SSOT 읽기 순서) 신설 + scholar-inspect Steps §1 에
SSOT 먼저 읽기 강제(결함 A); scholar-draft·scholar-revise <Output> 에 .tex↔.oms 동기화
완료조건 + output-layout.md §6 체크리스트 항목(결함 B). 이 테스트가 그 메커니즘 드리프트를
막는다. (verify 재실행 강제는 의도적으로 제외 — 매 구조변경마다 강제는 과중.)
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
LEARNING_PROTOCOL = ROOT / "references" / "learning-protocol.md"
OUTPUT_LAYOUT = ROOT / "references" / "output-layout.md"
INSPECT_SKILL = "scholar-inspect"
DRAFT_SKILL = "scholar-draft"
REVISE_SKILL = "scholar-revise"


# ----- 결함 A: SSOT 읽기 순서 -----

def test_learning_protocol_defines_ssot_reading_order():
    """learning-protocol.md §8 = SSOT 읽기 순서 SSOT. outline·methodology(1차) > research·code_survey(2차)."""
    body = LEARNING_PROTOCOL.read_text(encoding="utf-8")
    assert "## 8." in body and "SSOT reading order" in body, \
        "learning-protocol.md 에 §8 SSOT reading order 섹션 부재"
    # 1차 SSOT 두 경로 명시
    assert "outline/outline.md" in body, "1차 SSOT outline 경로 누락"
    assert "methodology/" in body, "1차 SSOT methodology 경로 누락"
    # 2차가 권위 아님 명시
    assert "code_survey" in body, "2차 code_survey 노트 언급 누락"
    # 1차가 2차보다 먼저 (순서 자체가 load-bearing)
    idx_outline = body.find("outline/outline.md")
    idx_codesurvey = body.find("code_survey")
    assert idx_outline < idx_codesurvey, \
        "§8 에서 outline(1차)이 code_survey(2차)보다 먼저 나와야 함 (읽기 순서)"
    # 두 따름 규칙: 부재≠스코프밖, outline이 챕터축 권위
    assert "out of scope" in body, "'부재를 스코프밖으로 단정 금지' 규칙 누락"
    assert "chapter-axis authority" in body or "chapter axis" in body, \
        "'outline = 챕터축 권위' 규칙 누락"


def test_inspect_skill_enforces_ssot_first():
    """scholar-inspect Steps §1 = SSOT(outline·methodology) 먼저 읽기 강제 + §8 참조."""
    body = skill_md(INSPECT_SKILL)
    steps = re.search(r"<Steps>.*?</Steps>", body, re.DOTALL)
    assert steps, "scholar-inspect 에 <Steps> 없음"
    text = steps.group(0)
    # Step 1 이 .tex 가 아니라 SSOT 먼저
    assert "outline/outline.md" in text, "inspect Steps 에 outline SSOT 먼저읽기 누락"
    assert "methodology/" in text, "inspect Steps 에 methodology SSOT 먼저읽기 누락"
    assert "learning-protocol.md" in text or "§8" in text, \
        "inspect Steps 가 learning-protocol §8 을 참조하지 않음"
    # 2차 노트가 권위 아님 경고
    assert "code_survey" in text or "research_summary" in text, \
        "inspect Steps 에 2차 노트 권위 아님 경고 누락"


# ----- 결함 B: .tex↔.oms 동기화 완료조건 -----

def _output_block(skill_name):
    body = skill_md(skill_name)
    m = re.search(r"<Output>.*?</Output>", body, re.DOTALL)
    assert m, f"{skill_name} 에 <Output> 섹션 없음"
    return m.group(0)


def test_draft_output_requires_oms_sync():
    """scholar-draft <Output> = 구조변경 시 outline·methodology 갱신 완료조건."""
    text = _output_block(DRAFT_SKILL)
    assert "동기화" in text or "sync" in text.lower(), "draft <Output> 에 동기화 완료조건 누락"
    assert "outline" in text and "methodology" in text, \
        "draft <Output> 에 outline·methodology 갱신 대상 누락"
    assert "구조" in text or "structure" in text.lower(), \
        "draft <Output> 에 '구조 변경 시' 조건 누락(단순 교정은 제외돼야)"


def test_revise_output_requires_oms_sync():
    """scholar-revise <Output> = 구조변경 시 outline·methodology·결정기록 갱신이 PASS 완료조건."""
    text = _output_block(REVISE_SKILL)
    assert "동기화" in text or "sync" in text.lower(), "revise <Output> 에 동기화 완료조건 누락"
    assert "outline" in text and "methodology" in text, \
        "revise <Output> 에 outline·methodology 갱신 대상 누락"
    # revise 는 결정기록(SECTION_REVIEW_DECISIONS류)도 대상
    assert "SECTION_REVIEW" in text or "결정기록" in text, \
        "revise <Output> 에 결정기록 갱신 언급 누락"
    assert "drift" in text.lower(), "revise <Output> 에 drift 금지 경고 누락"


def test_output_layout_checklist_has_sync_item():
    """output-layout.md §6 Implementation checklist 에 .tex↔.oms 동기화 항목."""
    body = OUTPUT_LAYOUT.read_text(encoding="utf-8")
    checklist = re.search(r"## 6\. Implementation checklist.*", body, re.DOTALL)
    assert checklist, "output-layout.md §6 Implementation checklist 없음"
    text = checklist.group(0)
    assert ".tex" in text and ".hq" in text, "checklist 에 .tex↔.hq 동기화 항목 부재"
    assert "outline" in text and "methodology" in text, \
        "checklist 동기화 항목에 outline·methodology 대상 누락"
    assert "learning-protocol.md" in text or "§8" in text, \
        "checklist 항목이 learning-protocol §8 을 참조하지 않음"
