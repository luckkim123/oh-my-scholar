"""Tests for the abstract-discipline guard — abstract = 질적 의미만, 정량 수치·수식 금지.

배경(2026-06-01): draft 초안의 abstract 3단락에 `$316\\times$`·`$13\\times$`·`$\\le 0.25$~m`
인라인 수식·배수·임계치가 그대로 들어가 있었다. 규칙은 선배 5편 정독으로 wiki 에 이미
명문화돼 있었으나(abstract=질적 의미만, 수치는 본문 Results 로) — draft 가 그것을 따르지
않았고 verify 게이트도 검출하지 않아 통과했다. 원인: 규칙 부재가 아니라 *강제 시점*의 부재.

처방(범용 배포): latex.md §3 에 SSOT 규칙+검출방법 추가, scholar-drafter 가 생성 시점에 따르고,
scholar-verifier 가 사후 WARN 으로 검출. WARN(FAIL 아님) — 일부 venue 가 abstract 핵심 수치
1개를 허용해 강제 FAIL 은 false-positive 위험. 이 테스트가 그 메커니즘 드리프트와 범용성
위반(특정 논문 고유명사 재유입)을 막는다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
LATEX_CARD = ROOT / "references" / "formats" / "latex.md"
RUBRIC = ROOT / "references" / "rubrics" / "paper-eval.md"
VERIFIER = ROOT / "agents" / "scholar-verifier.md"
DRAFTER = ROOT / "agents" / "scholar-drafter.md"
VERIFY_SKILL = ROOT / "skills" / "scholar-verify" / "SKILL.md"


def test_latex_card_defines_abstract_rule_and_detection():
    """① latex.md §3 = SSOT. abstract 질적 규칙 + verifier 검출 방법(grep 토큰) 명문화."""
    body = LATEX_CARD.read_text(encoding="utf-8")
    assert "abstract" in body.lower(), "latex.md 에 abstract 규율 누락"
    # 질적 의미만 / 본문 Results 로 미룸
    assert "질적" in body or "qualitative" in body, "abstract=질적 의미만 규칙 누락"
    assert "Results" in body, "수치를 본문 Results 로 미룬다는 규약 누락"
    # 검출 토큰 (인라인 수식·배수)
    assert r"\times" in body, "verifier 검출 토큰(\\times) 누락"
    assert "WARN" in body, "abstract 검출이 WARN 임을 명시 누락"
    # 단위 커버리지 — 이 도메인(로보틱스/수중) 흔한 단위가 토큰에 포함 (reviewer IMPORTANT 반영)
    for unit in ("cm", "dB", "kg"):
        assert unit in body, f"검출 토큰에 흔한 단위 '{unit}' 누락 (recall 약화)"
    # 유니코드 부등호 글리프
    assert "≤" in body or "≥" in body, "유니코드 부등호 글리프(≤/≥) 검출 누락"
    # no-anchor fallback — abstract 못 찾으면 전체 grep 금지 (reviewer MEDIUM 반영)
    assert re.search(r"(skip|N/A|건너).*전체 문서 grep 금지|전체 문서 grep 금지|do not grep the whole document", body), \
        "no-anchor fallback(검사 skip, 전체 문서 grep 금지) 명문화 누락"


def test_verifier_checks_abstract_as_warn_not_fail():
    """② scholar-verifier 가 abstract 규율을 WARN 으로 검사(FAIL 아님)."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert "abstract 규율" in body or "abstract discipline" in body, "verifier 검사 항목에 abstract 규율 누락"
    assert "WARN" in body, "verifier 가 abstract 를 WARN 으로 다룸 누락"
    # WARN ≠ FAIL: 전체 PASS 를 막지 않음이 명시돼야
    assert re.search(r"WARN.*FAIL 아님|FAIL 아님.*WARN|전체 PASS|[Nn]ot a FAIL|does not block overall PASS", body), \
        "abstract WARN 이 전체 PASS 를 막지 않음(WARN≠FAIL) 명시 누락"
    # 검출 단계가 Investigation_Protocol 에 있어야
    assert re.search(r"abstract 규율 검사|abstract 영역 추출|abstract discipline check|extract the abstract region", body), \
        "verifier Investigation_Protocol 에 abstract 검출 단계 누락"
    # 토큰 SSOT 참조 — verifier 는 토큰을 재나열하지 않고 latex.md §3 를 가리킨다 (drift 방지)
    assert "latex.md §3" in body, "verifier 가 검출 토큰 SSOT(latex.md §3)를 참조하지 않음"
    # no-anchor fallback — anchor 없으면 전체 grep 금지
    assert "전체 문서 grep 금지" in body or "do not grep the whole document" in body, \
        "verifier 에 no-anchor 전체 grep 금지 규약 누락"


def test_drafter_prevents_abstract_numbers_at_generation():
    """③ scholar-drafter 가 생성 시점에 사전 예방(사후 검출보다 근본)."""
    body = DRAFTER.read_text(encoding="utf-8")
    assert "abstract" in body.lower(), "drafter 가 abstract 규율을 안 따름"
    # 생성 시 정량 수치/수식 금지
    assert re.search(r"abstract = qualitative|no quantitative", body), \
        "drafter 가 abstract=질적만(수치 금지)을 따른다는 규약 누락"


def test_rubric_and_skill_reference_latex_card_ssot():
    """④ 정합성: rubric·verify skill 이 SSOT(latex.md §3)를 가리킨다 (중복 정의 금지)."""
    rubric = RUBRIC.read_text(encoding="utf-8")
    skill = VERIFY_SKILL.read_text(encoding="utf-8")
    assert "abstract 규율" in rubric or "abstract discipline" in rubric, "paper-eval rubric verify 축에 abstract 규율 행 누락"
    assert "latex.md §3" in rubric, "rubric 이 SSOT(latex.md §3)를 참조하지 않음"
    assert "abstract 규율" in skill or "Abstract discipline" in skill or "abstract discipline" in skill, \
        "verify SKILL 위임 항목에 abstract 규율 누락"
    assert "latex.md §3" in skill, "verify SKILL 이 SSOT(latex.md §3)를 참조하지 않음"


def test_no_project_specific_proper_nouns_leaked():
    """⑤ 범용성: 배포물에 특정 논문 고유명사가 새지 않았다 (universal rule only).

    이 abstract 규율은 모든 논문에 적용되는 범용 규율 — 이 논문 고유 수치나
    제목·플랫폼명·지도교수명 등이 배포 카드·agent 에 들어가면 안 된다."""
    leaked_tokens = ["ROOM_X", "ORG_X", "SITE_X", "ADVISOR_X", "PROJ_TITLE_X", "ADVISOR_X_EN", "STUDENT_ID_X"]
    for path in (LATEX_CARD, RUBRIC, VERIFIER, DRAFTER, VERIFY_SKILL):
        body = path.read_text(encoding="utf-8")
        for tok in leaked_tokens:
            assert tok not in body, f"{path.name} 에 특정 논문 고유명사 '{tok}' 누출 (범용성 위반)"
