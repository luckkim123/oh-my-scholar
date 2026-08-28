"""Tests for the drafter generation-flow upgrade — skeleton 단계 + silent self-audit.

배경(2026-06-01): drafter Investigation_Protocol 이 outline+notes→바로 .tex prose 로
reasoning·composition 을 단일 패스에 융합 — 흐름이 깨지는 구조적 원인. 처방(WriteHERE +
장문 일관성 문헌): prose 전 reasoning-skeleton(문단별 claim+인용 골격) 단계 + 반환 전 silent
self-audit(장식어·em-dash·old→new). 규칙 준수를 *생성 시점*에 구조적으로 강제.

⚠️ citation-safety 코어 불변: skeleton cite-key 도 검증된 .bib 키만, 인라인 날조 금지,
self-audit 은 위생이지 게이트 아님(자기승인 금지 유지). 설계: design.md §3.2.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DRAFTER = ROOT / "agents" / "scholar-drafter.md"


def test_drafter_has_skeleton_step_before_prose():
    """① reasoning skeleton 단계 — prose 전, 문단별 claim+인용 골격."""
    body = DRAFTER.read_text(encoding="utf-8")
    assert re.search(r"skeleton|골격", body), "drafter 에 reasoning skeleton 단계 누락"
    # 문단별 claim + 인용(cite-key) 골격
    assert re.search(r"claim", body), "skeleton 의 claim 요소 누락"
    assert re.search(r"prose 전|before prose|prose 작성 전", body), \
        "skeleton 이 prose *전* 단계임이 명시 안 됨"


def test_skeleton_output_path_in_workspace():
    """② skeleton 산출물은 .hq/work/scholar/<slug>/ 작업장(소스 폴더 오염 금지)."""
    body = DRAFTER.read_text(encoding="utf-8")
    # skeleton 산출물이 .hq/work/scholar/<slug>/ 에 — output-layout 준수
    assert re.search(r"\.hq/work/scholar/<slug>/", body), \
        "skeleton 산출물 경로(.hq/work/scholar/<slug>/) 명시 누락"


def test_drafter_has_silent_self_audit_step():
    """③ 반환 전 silent self-audit — writing-craft.md §2/§7 기준."""
    body = DRAFTER.read_text(encoding="utf-8")
    assert re.search(r"self-audit|self audit|자가 점검|자가점검", body), \
        "drafter 에 silent self-audit 단계 누락"
    # writing-craft.md 를 참조 (SSOT, 토큰 재나열 금지)
    assert "writing-craft.md" in body, "drafter 가 writing-craft.md SSOT 를 참조 안 함"
    # silent — 출력하지 않음
    assert re.search(r"silent|조용히|출력(하지|\s*안)", body), \
        "self-audit 이 silent(출력 안 함)임이 명시 안 됨"


def test_self_audit_is_hygiene_not_gate():
    """④ self-audit 은 위생이지 게이트 아님 — 자기승인 금지 유지(회귀)."""
    body = DRAFTER.read_text(encoding="utf-8")
    # self-audit 이 inspector/verifier 별도 패스를 대체하지 않음
    assert re.search(r"위생|hygiene|게이트 아님|not a gate|대체.{0,4}(아님|않)", body), \
        "self-audit 이 게이트가 아니라 위생임(별도 패스 유지) 명시 누락"
    # 기존 자기승인 금지 텍스트 잔존 (회귀 가드)
    assert re.search(r"self-approv|자기.{0,2}승인|self-review|self-verif", body, re.I), \
        "회귀: '자기승인 금지' 규약이 사라짐"
    assert re.search(r"hand off|핸드오프|넘긴|verifier", body), \
        "회귀: verifier/inspector 별도 패스로 핸드오프 규약이 사라짐"


def test_citation_safety_invariant_intact():
    """⑤ 회귀: citation 인라인 날조 금지·단일 신중 생성 유지."""
    body = DRAFTER.read_text(encoding="utf-8")
    assert re.search(r"NEVER invent a citation|인용.{0,4}(날조|창작|만들지)", body), \
        "회귀: 인라인 citation 날조 금지 규약이 사라짐"
    assert re.search(r"single-thread|단일|never parallel|병렬.{0,4}(아님|금지)", body), \
        "회귀: 단일 신중(병렬 금지) 생성 규약이 사라짐"
    # skeleton 의 cite-key 도 검증된 .bib 키만 (날조 확장 차단)
    assert re.search(r"skeleton.{0,40}(verified|검증|\.bib)", body, re.S | re.I), \
        "skeleton cite-key 가 검증된 .bib 키만이라는 규약 누락"


def test_drafter_loads_writing_craft_card():
    """⑥ drafter 가 writing-craft.md 를 로드 카드 목록에 포함 (latex.md 와 나란히)."""
    body = DRAFTER.read_text(encoding="utf-8")
    # 기존 latex.md 참조 잔존 + 새 writing-craft.md 참조
    assert "latex.md" in body, "회귀: latex.md 참조가 사라짐"
    assert "writing-craft.md" in body, "drafter 가 writing-craft.md 를 안 읽음"


def test_drafter_has_no_project_specific_proper_nouns():
    """⑦ 범용성 가드 — drafter(배포 파일)에 프로젝트 고유명사 없음."""
    body = DRAFTER.read_text(encoding="utf-8")
    bad = re.compile(r"ADVISOR_X|kimseungmin|PROJ_TITLE_X|SITE_X|ORG_X|ROOM_X", re.I)
    hits = [
        f"  scholar-drafter.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(body.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "배포 파일에 프로젝트 고유명사 잔존(범용성 위반):\n" + "\n".join(hits)
