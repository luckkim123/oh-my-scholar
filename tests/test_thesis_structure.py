"""Tests for the paper structure model — scholar-planner가 '공통 골격 + 규모 변주'를 안다.

배경(2026-05-31): 학위논문을 outline 시켰더니 "기술 백서"(방법을 여러 섹션에 나열 +
실험을 끝 한 곳에 몰아넣음)로 짜였다. 원인: planner에 구조 모델이 flat(단편) 하나뿐.
문헌조사(IROS/RA-L/T-RO author guide·Milford·Brown H2R·York/Oxbridge thesis guide) 결과:
모든 논문은 공통 골격(Intro→[Method 단위 1..N: Overview→Proposed→그 단위 실험]→Conclusion)을
공유하고, structure_type(flat | system | thesis)은 그 골격을 몇 번 반복·얼마나 펼치는가
(규모)만 가른다. 처방: planner <Structure_Types> 재작성 + venues.md structure_type 필드.
이 테스트가 그 드리프트와 범용성 위반·폐기용어 재유입을 막는다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLANNER = ROOT / "agents" / "scholar-planner.md"
VENUES = ROOT / "references" / "venues.md"


def test_planner_defines_common_skeleton_and_scale_variants():
    """① planner가 공통 골격 + 세 규모 변주(flat·system·thesis)를 정의한다."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "<Structure_Types>" in body, "planner에 <Structure_Types> 섹션 누락"
    assert "공통 골격" in body, "planner에 '공통 골격' 개념 누락"
    for variant in ("flat", "system", "thesis"):
        assert re.search(rf"`{variant}`", body), f"planner에 규모 변주 '{variant}' 누락"


def test_planner_forbids_technical_report_antipattern():
    """② planner가 '실험을 끝 한 곳에 몰지 마라'(기술 백서 안티패턴)를 규정한다.

    이번 버그의 핵심 — 어느 규모에서도 실험은 그 방법이 제안된 단위 안에."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "기술 백서" in body, "기술 백서 안티패턴 경고 누락"
    assert re.search(r"실험.*(몰지|끝.*한)", body), "실험을 끝에 몰지 말라는 규약 누락"
    # 각 method/기여 단위가 자체 실험을 갖는다는 공통 골격 규약
    assert re.search(r"Overview.*Proposed.*(실험|Experiment)", body), \
        "공통 골격(Overview→Proposed→그 단위 실험) 규약 누락"


def test_planner_distinguishes_monograph_vs_by_papers():
    """③ thesis 하위형(thesis-by-papers vs monograph)을 구분한다.

    문헌조사 핵심 정정 — 자체완결은 by-papers, 축적은 monograph."""
    body = PLANNER.read_text(encoding="utf-8")
    assert "thesis-by-papers" in body, "thesis-by-papers 하위형 누락"
    assert "monograph" in body, "monograph 하위형 누락"


def test_venues_schema_has_structure_type():
    """④ venues.md 스키마에 structure_type 필드가 있고 세 값을 문서화한다."""
    body = VENUES.read_text(encoding="utf-8")
    assert "structure_type:" in body, "venues.md 스키마에 structure_type 필드 누락"
    for variant in ("flat", "system", "thesis"):
        assert variant in body, f"venues.md에 structure_type 값 '{variant}' 문서화 누락"


def test_no_deprecated_structure_term():
    """⑤ 폐기 용어 'thesis-by-contribution'이 어디에도 안 남았다(drift 방지).

    초기 설계에서 썼다가 문헌조사 후 'thesis'(+하위형)로 대체한 용어."""
    for f in (PLANNER, VENUES):
        body = f.read_text(encoding="utf-8")
        assert "thesis-by-contribution" not in body, \
            f"{f.name}에 폐기 용어 'thesis-by-contribution' 잔존"


def test_planner_has_no_project_specific_proper_nouns():
    """⑥ 범용성 가드 — planner(배포 파일)에 특정 사용자/논문/교수 고유명사가 없다.

    배포 repo는 모든 사용자에게 가므로 이 논문 고유명사가 박히면 오염
    (한때 특정 지도교수 랩명을 박았다가 제거 — 이 테스트가 재발 방지)."""
    body = PLANNER.read_text(encoding="utf-8")
    bad = re.compile(r"ADVISOR_X|kimseungmin|PROJ_TITLE_X|SITE_X|ORG_X", re.I)
    hits = [
        f"  scholar-planner.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(body.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "배포 파일에 프로젝트 고유명사 잔존(범용성 위반):\n" + "\n".join(hits)
