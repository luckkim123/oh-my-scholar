"""Tests for the writing-craft card — 4차원(FLOW·TONE·LOGIC·STRUCTURE) 글쓰기 규칙 SSOT.

배경(2026-06-01): oms drafter 산출물이 flow·tone·logic·structure 네 차원에서 어색했다.
gap 분석 결과 — 아키텍처(inspect⊥verify⊥mock-review, 심각도 분류, abstract-WARN 선례,
human-gated learn)는 우수하나 *글쓰기 규칙 내용*이 거의 비어 있었다. 글쓰기 어휘가 repo 에
단 한 곳(scholar-inspector prose lens)만, 그나마 사후 비평 레인이라 생성 시점에 흐름·어투를
빚을 수단이 0. 처방: references/writing-craft.md 를 4차원 규칙 단일 SSOT 로 신설(latex.md=조판
⊥ writing-craft=논증·서술), drafter·inspector·verifier 가 *참조*(재나열 금지)한다.

이 테스트가 카드의 7섹션 구조·각 차원 핵심 규칙·§7 토큰·venue 변주 명시·범용성(고유명사 누출
차단)을 강제한다. 출처 anchor 와 비목표(embedding·Manchester bulk-copy·auto-FAIL) 회피도 검증.
설계: docs/specs/2026-06-01-writing-craft-injection/design.md §3.1.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CARD = ROOT / "references" / "writing-craft.md"


def test_card_exists():
    """① writing-craft.md 가 references/ 에 존재한다."""
    assert CARD.exists(), "references/writing-craft.md 누락 — 4차원 규칙 SSOT"


def test_card_has_seven_sections():
    """② 7개 섹션(§1 FLOW … §7 mechanical-check tokens)이 모두 있다."""
    body = CARD.read_text(encoding="utf-8")
    # §N 헤더 + 차원 이름이 같은 줄에 (순서 무관, 존재만)
    for marker in ("FLOW", "TONE", "LOGIC", "STRUCTURE", "VOICE", "EXEMPLAR"):
        assert marker in body, f"writing-craft.md 에 §섹션 '{marker}' 누락"
    # §7 = 기계 체크 토큰 섹션
    assert re.search(r"§\s*7", body) or "mechanical" in body.lower() or "토큰" in body, \
        "§7 mechanical-check token 섹션 누락"


def test_flow_anchor_rules_present():
    """③ FLOW — Gopen-Swan old→new(stress position)·banana rule 핵심 규칙."""
    body = CARD.read_text(encoding="utf-8")
    assert re.search(r"old\s*[→\-]+\s*new|구정보.*신정보|stress position", body), \
        "FLOW 최상위 규칙(old→new / stress position) 누락"
    assert "banana" in body.lower(), "FLOW banana rule(정확한 키워드 반복) 누락"
    assert "Gopen" in body or "Swan" in body, "FLOW 출처 anchor(Gopen-Swan) 누락"


def test_tone_anchor_rules_present():
    """④ TONE — 장식어 금지 원리 + em-dash 캡."""
    body = CARD.read_text(encoding="utf-8")
    # 장식 동사/형용사 ban (원리 + 씨앗 단어)
    assert re.search(r"장식|ornamental|decorative", body), "TONE 장식 동사·형용사 금지 원리 누락"
    for seed in ("delve", "underscore", "showcase"):
        assert seed in body, f"TONE 장식어 씨앗 토큰 '{seed}' 누락"
    # em-dash 캡 — 유니코드 글리프 명시 (멀티바이트)
    assert "em-dash" in body.lower() or "em dash" in body.lower() or "—" in body, \
        "TONE em-dash 캡 누락"


def test_logic_anchor_rules_present():
    """⑤ LOGIC — one-ping + 과대일반화 경고."""
    body = CARD.read_text(encoding="utf-8")
    assert "one ping" in body.lower() or "one-ping" in body.lower(), \
        "LOGIC one-ping 규칙 누락"
    assert re.search(r"과대일반화|overgeneraliz", body), \
        "LOGIC 과대일반화(최대 실패모드) 경고 누락"
    assert "TEEL" in body, "LOGIC TEEL 문단 모델 누락"


def test_structure_anchor_rules_present():
    """⑥ STRUCTURE — CARS Move-2(gap) + OCAR."""
    body = CARD.read_text(encoding="utf-8")
    assert "CARS" in body, "STRUCTURE CARS 3-move 누락"
    assert re.search(r"Move\s*2|틈|gap|niche", body), \
        "STRUCTURE CARS Move-2(틈/gap) 누락"
    assert "OCAR" in body, "STRUCTURE OCAR 아크 누락"


def test_section7_tokens_parseable_with_multibyte_caveat():
    """⑦ §7 토큰 목록이 파싱 가능 + 멀티바이트 grep 거짓음성 경고.

    verifier 가 이 토큰을 읽어 WARN 검출. abstract-WARN 선례처럼 Python re 만 신뢰."""
    body = CARD.read_text(encoding="utf-8")
    # 멀티바이트 grep false-clean 경고 (메모리: 확인된 함정)
    assert re.search(r"멀티바이트|multibyte", body) and re.search(r"Python\s*`?re|re\s*모듈", body), \
        "§7 에 멀티바이트 grep 거짓음성 경고(Python re 만 신뢰) 누락"
    # 토큰이 검출 대상으로 명시됐는가 (장식어/em-dash/rule-of-three 중 검출 토큰)
    assert re.search(r"rule.of.three|rule-of-three", body), \
        "§7 검출 토큰에 rule-of-three 누락"


def test_venue_variance_not_hardcoded():
    """⑧ venue 변주 명시 — related-work 위치·아크 선택은 하드코딩 금지."""
    body = CARD.read_text(encoding="utf-8")
    assert re.search(r"하드코딩 (금지|하지)|not hardcoded|no hardcoding|do not hardcode|venue.{0,4}(변주|파라미터|parameter)|venue variation", body), \
        "venue 변주(related-work 위치/아크 선택 하드코딩 금지) 명시 누락"


def test_voice_precedence_present():
    """⑨ VOICE — discipline > journal > personal 우선순위."""
    body = CARD.read_text(encoding="utf-8")
    assert re.search(r"discipline.*journal.*personal|분야.*저널.*개인", body), \
        "VOICE 우선순위(discipline>journal>personal) 누락"


def test_exemplar_anti_curation_present():
    """⑩ EXEMPLAR — ~5개 무작위 대표(유사도-curated 금지, embedding 비목표)."""
    body = CARD.read_text(encoding="utf-8")
    assert re.search(r"무작위|random", body), "EXEMPLAR 무작위 대표 표본 규칙 누락"
    # 비목표: 유사도-curated / embedding 금지
    assert re.search(r"유사도|similarity|curat|embedding|임베딩", body), \
        "EXEMPLAR 유사도-curated/embedding 금지(비목표) 명시 누락"


def test_no_project_specific_proper_nouns():
    """⑪ 범용성 — 배포 카드에 특정 사용자/논문/교수 고유명사가 없다.

    writing-craft.md 는 모든 사용자에게 배포되므로 이 논문 고유명사 박히면 오염."""
    body = CARD.read_text(encoding="utf-8")
    bad = re.compile(r"ADVISOR_X|kimseungmin|PROJ_TITLE_X|SITE_X|ORG_X|ROOM_X", re.I)
    hits = [
        f"  writing-craft.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(body.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "배포 카드에 프로젝트 고유명사 잔존(범용성 위반):\n" + "\n".join(hits)
