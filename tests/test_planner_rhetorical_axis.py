"""Tests for the planner rhetorical-structure axis — CARS·OCAR·모래시계 (v0.4.0 직교).

배경(2026-06-01): planner v0.4.0 구조 모델은 *섹션 순서/규모*(flat·system·thesis)만 다뤘다.
수사 구조 축(CARS 3-move·OCAR 아크·모래시계)이 통째로 비어 있어 Intro 가 territory 만 말하고
gap(Move-2)을 못 파는 게 #1 논리 실패. 처방: planner 에 수사 구조 축을 *직교*로 추가
(v0.4.0 섹션-순서 모델을 덮지 않음). writing-craft.md §4 를 SSOT 로 참조.

⚠️ v0.4.0 회귀 0: flat/system/thesis·기술 백서 안티패턴 가드 잔존. 설계: design.md §3.3.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLANNER = ROOT / "agents" / "scholar-planner.md"


def test_planner_has_cars_three_move():
    """① CARS 3-move 가 planner 에 있고 Move-2(gap)가 강제된다."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "CARS" in body, "planner 에 CARS 3-move 누락"
    assert re.search(r"Move\s*2", body), "planner 에 CARS Move-2 누락"
    # Move-2 = 틈/gap, 그리고 강제(건너뛰지 마라 / reject 사유)
    assert re.search(r"틈|gap|niche", body), "Move-2 틈/gap 개념 누락"
    assert re.search(r"건너.{0,3}(뛰지|마)|reject|필수", body), \
        "Move-2 gap 강제(건너뛰지 마라/reject 1순위) 누락"


def test_planner_has_ocar_and_hourglass():
    """② OCAR 아크 + 모래시계 폭 일치."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "OCAR" in body, "planner 에 OCAR 아크 누락"
    # 모래시계: Opening 폭 = Resolution 폭
    assert re.search(r"모래시계|hourglass", body), "모래시계 개념 누락"
    assert re.search(r"독자 인내심|audience patience|인내심", body), \
        "아크를 독자 인내심으로 선택(OCAR↔LD) 누락"


def test_planner_section_brief_has_must_argue():
    """③ per-section brief 에 '논증할 명제 1개' 필드 추가."""
    body = PLANNER.read_text(encoding="utf-8")
    assert re.search(r"논증할 명제|논증.{0,4}명제|must argue|논증해야", body), \
        "섹션 brief 에 '이 섹션이 논증할 명제 1개' 필드 누락"


def test_planner_references_writing_craft_ssot():
    """④ 수사 구조 규칙은 writing-craft.md §4 를 참조(재나열 금지)."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "writing-craft.md" in body, \
        "planner 가 수사 구조 SSOT(writing-craft.md §4)를 참조 안 함"


def test_planner_rhetorical_axis_orthogonal_to_v040():
    """⑤ 수사 축이 v0.4.0 섹션-순서 모델과 *직교*임이 명시된다."""
    body = PLANNER.read_text(encoding="utf-8")
    assert re.search(r"직교|orthogonal|덮(지|어쓰지)\s*않|섹션-순서.{0,6}(축|별도)", body), \
        "수사 구조 축이 v0.4.0 모델과 직교(덮지 않음)임이 명시 안 됨"


def test_v040_structure_model_regression():
    """⑥ 회귀: v0.4.0 섹션-순서 모델(flat/system/thesis + 공통 골격)이 그대로다."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "<Structure_Types>" in body, "회귀: <Structure_Types> 섹션 사라짐"
    assert "공통 골격" in body, "회귀: '공통 골격' 개념 사라짐"
    for variant in ("flat", "system", "thesis"):
        assert re.search(rf"`{variant}`", body), f"회귀: 규모 변주 '{variant}' 사라짐"
    # 기술 백서 안티패턴 가드 잔존
    assert "기술 백서" in body, "회귀: 기술 백서 안티패턴 경고 사라짐"
    assert re.search(r"실험.*(몰지|끝.*한)", body), "회귀: 실험 끝-몰이 금지 규약 사라짐"
    # 폐기 용어 재유입 차단
    assert "thesis-by-contribution" not in body, "폐기 용어 'thesis-by-contribution' 재유입"


def test_planner_has_no_project_specific_proper_nouns():
    """⑦ 범용성 가드 — planner(배포 파일)에 프로젝트 고유명사 없음."""
    body = PLANNER.read_text(encoding="utf-8")
    bad = re.compile(r"유선철|POSTECH|kimseungmin|ASV-ROV|형산강|hyeongsan|KHNP|KIRO", re.I)
    hits = [
        f"  scholar-planner.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(body.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "배포 파일에 프로젝트 고유명사 잔존(범용성 위반):\n" + "\n".join(hits)
