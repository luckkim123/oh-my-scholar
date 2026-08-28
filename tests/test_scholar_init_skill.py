"""Tests for scholar-init/SKILL.md — 새 논문 0단계 부트스트랩 스킬의 구조 계약.

scholar-init 은 omp-init 의 검증된 부트스트랩 패턴(GATE 0 멱등성 → read-only
진단 → 사람 게이트 → write)을 논문 도메인으로 이식한다. 이 테스트는 그 계약이
SKILL 본문에 박혀 있는지(드리프트 방지)와, oms 고유 불변(절대경로 0·citation
안전·scaffold만)이 지켜지는지 검사한다. design.md §3.2-3.5 / plan.md A2 의 검증 기준."""
import re
from pathlib import Path

from conftest import skill_md

SKILL = Path(__file__).parent.parent / "skills" / "scholar-init" / "SKILL.md"


def read() -> str:
    return skill_md("scholar-init")


def test_skill_file_exists():
    """① scholar-init/SKILL.md 가 실재한다 (shim — full body lives at skill-bodies/)."""
    assert SKILL.is_file(), f"missing {SKILL}"


def test_frontmatter_has_required_keys():
    """② frontmatter 에 name·description·Triggers 가 있다."""
    body = read()
    assert body.startswith("---"), "YAML frontmatter 로 시작해야"
    fm = body.split("---", 2)[1]
    assert "name: scholar-init" in fm
    assert "description:" in fm
    assert "Triggers:" in fm


def test_has_gate_zero_idempotency():
    """③ GATE 0 멱등성 — 이미 .oms/<slug>/ 있으면 멈춤 (재초기화 손실 경고)."""
    body = read()
    assert "게이트 0" in body or "GATE 0" in body or "gate 0" in body
    assert ".hq/work/scholar/<slug>/" in body
    assert "재초기화" in body or "re-initializ" in body  # 손실 경고


def test_has_human_gate_one():
    """④ GATE 1 사람 승인 — proceed/revise/abort, 자동 통과 없음."""
    body = read()
    assert "GATE 1" in body
    assert "proceed" in body and "revise" in body and "abort" in body
    assert "자동 통과 없음" in body or "No automatic pass" in body


def test_read_only_before_write_gate():
    """⑤ dispatch 는 read-only, 쓰기는 게이트 후에만 (self-approval 금지)."""
    body = read()
    assert "read-only" in body
    assert "게이트 통과 후" in body or "GATE 1 통과 후" in body or "after passing GATE 1" in body
    assert "self-approval 금지" in body or "self-approve 금지" in body or "No self-approval" in body or "No self-approve" in body


def test_scaffold_matches_design_3_3():
    """⑥ scaffold 디렉토리가 design §3.3 과 1:1 (sections/figures/refs/data/preamble/meta)."""
    body = read()
    for item in ("sections/", "figures/", "refs/", "data/",
                 "preamble.tex", "meta.md"):
        assert item in body, f"scaffold 항목 '{item}' 누락"
    # .hq 작업장 + 논문별 wiki 4-카테고리
    assert ".hq/work/scholar/<slug>/" in body
    assert "convention/" in body and "pattern/" in body


def test_global_wiki_is_ascent_not_absolute():
    """⑦ 전역 wiki = 상위 폴더 .oms/ ascent (절대경로·환경변수 아님)."""
    body = read()
    assert "ascent" in body
    assert "상위 폴더" in body or "상위 `.oms/`" in body or "부모" in body or "parent folder" in body or "parent `.oms/`" in body
    assert "wiki_query" in body  # 추상 함수로 조회


def test_no_absolute_path_hardcode():
    """⑧ 배포물 오염 방지 — 절대경로·홈 하드코딩 0.

    SKILL 본문에 머신 특정 절대경로(/Users/... 또는 명령형 ~/ 경로)가 없어야.
    (설명 문맥의 `Path.cwd()`·상대경로 지침은 허용.)"""
    body = read()
    assert "/Users/" not in body, "머신 특정 절대경로 누출"
    # '~/' 로 시작하는 하드코딩 경로 패턴 (코드/예시에서) 금지
    assert not re.search(r"[`'\"]~/", body), "홈(~/) 하드코딩 경로 누출"
    assert ("절대경로" in body and "하드코딩 금지" in body) or \
        ("absolute path" in body.lower() and "hardcod" in body.lower())  # 원칙 명시


def test_citation_safety_scaffold_only():
    """⑨ citation 안전 — init 은 scaffold 만, 인용 생성·날조 0, 임베딩 금지."""
    body = read()
    assert "scaffold" in body
    assert "citation" in body or "인용" in body
    assert "날조" in body or "생성하지 않" in body or "생성 0" in body or "fabricat" in body.lower() or "does not generate" in body or "not generated" in body
    assert "임베딩" in body or "embedding" in body.lower()  # 임베딩 검색 영구 금지 언급


def test_min_questions_progressive_disclosure():
    """⑩ 질문 최소화 — 첫 세션 ≤3개, 방법론·세부는 후속 단계 위임."""
    body = read()
    assert "≤3" in body or "3개" in body
    assert "progressive disclosure" in body


def test_venue_config_written_atomically():
    """⑫ venue-config 는 atomic_write_text 로 쓰인다 — "yaml 은 plain write" 예외 폐기 (R3 #16)."""
    body = read()
    assert "atomic_write_text" in body
    assert "for yaml use a plain write" not in body


def test_pilot_absorb_and_history_category():
    """⑪ 확정 미해결값 반영 — pilot 흡수(권유) + history 카테고리 + Q7 부모 안내."""
    body = read()
    assert "pilot" in body  # pilot 흡수 진입
    assert "history" in body  # history 카테고리 (Q4 신설)
    # Q7: 부모 .oms/ 없으면 임의 생성 안 함 + 안내
    assert "부모 폴더" in body or "임의로 만들지 않" in body or "홈 오염" in body or \
        "parent folder" in body or "does not arbitrarily create" in body or "home pollution" in body
