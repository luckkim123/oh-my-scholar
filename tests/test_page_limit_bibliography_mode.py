"""page_limit 이 참고문헌 제외형 한도를 표현할 수 있는지 (2026-08-25 신설).

기존 검사는 항상 전체 PDF 페이지를 셌다. 참고문헌을 한도에서 빼는 venue 에서는
과다 계상이고, 그 오판이 불필요한 조판 재작업을 부른다. 기법은 LaTeX 에게 직접
묻는 것 — thebibliography 시작 지점에 label 을 심고 .aux 에서 그 페이지를 읽는다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
VENUES = ROOT / "references" / "venues.md"
LATEX = ROOT / "references" / "formats" / "latex.md"
VERIFIER = ROOT / "agents" / "scholar-verifier.md"


def test_venue_schema_can_express_bibliography_exclusion():
    body = VENUES.read_text(encoding="utf-8")
    assert "page_limit_excludes_bibliography" in body, "venue 스키마에 필드 누락"
    assert re.search(r"default false|기본.*false", body, re.I), \
        "기본값 미명시 — 명시 안 하면 기존 venue 카드의 해석이 바뀐다"


def test_venue_schema_warns_against_guessing():
    """false 를 true 로 잘못 두면 진짜 초과가 숨는다. 기본값 유지가 더 안전하다."""
    body = VENUES.read_text(encoding="utf-8")
    assert re.search(r"author guide|guessing it wrong", body, re.I), \
        "venue 가이드 확인 요구 누락"


def test_latex_card_carries_the_referencesstart_procedure():
    body = LATEX.read_text(encoding="utf-8")
    assert r"\AddToHook{env/thebibliography/begin}" in body, "템플릿 훅 한 줄 누락"
    assert "ReferencesStart" in body, "label 이름 누락"
    assert "main.aux" in body, ".aux 파싱 대상 누락"
    # 중첩 중괄호 — 정규식 하나로 파싱하면 조용히 틀린다
    assert re.search(r"depth counter|nested", body, re.I), \
        "중첩 중괄호 경고 누락 — 단일 정규식 파싱이 조용히 틀린 답을 낸다"


def test_missing_label_does_not_fall_back_to_total():
    """빈 결과를 다른 질문의 답으로 대체하면 안 된다 — silent-success 계열 결함."""
    for f in (LATEX, VERIFIER):
        body = f.read_text(encoding="utf-8")
        assert re.search(r"not available", body, re.I), \
            f"{f.name}: label 부재 시 총 페이지로 폴백 금지 규칙 누락"


def test_page_check_row_mentions_both_modes():
    body = LATEX.read_text(encoding="utf-8")
    row = [l for l in body.splitlines() if l.startswith("| page count")]
    assert row, "page count 검사 행 소실"
    assert "page_limit_excludes_bibliography" in row[0], "검사 행이 두 모드를 안 가른다"
