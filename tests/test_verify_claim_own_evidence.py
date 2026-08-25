"""verify 의 claim↔자기근거 WARN 축이 세 층에 배선돼 있는지 (2026-08-25 신설).

카드에 규칙만 쓰고 verifier·rubric 에 안 배선하면 아무도 안 돌린다 — 이 저장소가
전에 밟은 함정이다(규칙 있음 ≠ 발동됨). 그리고 계측 안 된 게이트는 초록불이
아무 의미가 없으므로 NOT_CALIBRATED 라벨이 붙어 있어야 한다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
VERIFIER = ROOT / "agents" / "scholar-verifier.md"
RUBRIC = ROOT / "references" / "rubrics" / "paper-eval.md"


def test_verifier_declares_the_axis():
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"[Cc]laim ↔ own evidence", body), "verifier 체크 목록에 축 누락"
    assert "7.6" in body, "verifier 절차에 7.6 단계 누락"
    assert re.search(r"\|\s*claim ↔ own evidence\s*\|", body), "verifier 요약표에 행 누락"


def test_axis_is_warn_not_fail():
    """정적 탐지를 hard-FAIL 로 걸면 문맥상 정당한 문장이 게이트를 막는다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"claim ↔ own evidence.*WARN", body, re.S | re.I)
    assert re.search(r"claim ↔ own evidence, uncited claims", body), \
        "WARN 요약 문장에 새 축이 안 실렸다 — 요약이 본문보다 오래 산다"


def test_axis_is_labelled_uncalibrated():
    """계측하지 않은 검사기의 초록불을 근거로 쓰지 못하게 라벨이 필요하다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert "NOT_CALIBRATED" in body, \
        "계측 전 축에 calibration_status 라벨 누락 — 초록불이 증거로 오독된다"


def test_axis_does_not_overlap_citation_faithfulness():
    """두 축이 왜 다른지가 본문에 있어야 한다. 없으면 다음 사람이 중복으로 보고 지운다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"no.{0,4}\*{0,2}\\\\cite|carry \*\*no\*\* `\\cite`|without one", body), \
        "claim-faithfulness 와의 차이(=\\cite 없는 문장) 설명 누락"


def test_rubric_registers_the_axis():
    body = RUBRIC.read_text(encoding="utf-8")
    assert re.search(r"claim ↔ own evidence \(WARN\)", body), "paper-eval verify 축 표에 미등재"
    assert "writing-craft.md §3" in body, "rubric 이 규칙 SSOT 를 안 가리킨다"
