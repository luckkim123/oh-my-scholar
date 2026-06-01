"""Tests for the verify writing-WARN row — 기계 체크(장식어·em-dash·rule-of-three) = WARN.

배경(2026-06-01): writing-craft.md §7 토큰(장식어·em-dash·rule-of-three·부정병렬)을 verifier 가
기계적으로 검출하되 **WARN(FAIL 아님)**으로 — abstract-WARN(bce59f4) 선례 그대로. 정적 blocklist
부패·멀티바이트 거짓음성 위험으로 강제 FAIL 은 false-positive. 처방: verifier 에 writing 규율 WARN
행 + paper-eval verify 축 행 추가. 토큰은 writing-craft.md §7 SSOT 참조(재나열 금지).

⚠️ 멀티바이트(em-dash —) 검출은 Python re 만 신뢰. 설계: design.md §3.4.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
VERIFIER = ROOT / "agents" / "scholar-verifier.md"
RUBRIC = ROOT / "references" / "rubrics" / "paper-eval.md"


def test_verifier_has_writing_warn_check():
    """① verifier 가 writing 규율(장식어·em-dash·rule-of-three)을 검사한다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"writing 규율|글쓰기 규율|writing-craft", body), \
        "verifier 에 writing 규율 검사 항목 누락"


def test_writing_check_is_warn_not_fail():
    """② writing 검사가 WARN(FAIL 아님) — 전체 PASS 막지 않음."""
    body = VERIFIER.read_text(encoding="utf-8")
    # writing 규율 근처에 WARN + FAIL 아님 명시
    assert re.search(r"writing[^\n]*WARN|글쓰기[^\n]*WARN", body), \
        "writing 검사가 WARN 으로 분류 안 됨"
    # WARN≠FAIL 규약 (전체 PASS 막지 않음) — abstract WARN 과 같은 처리
    assert re.search(r"WARN.*FAIL 아님|FAIL 아님.*WARN|전체 PASS", body), \
        "writing WARN 이 전체 PASS 를 막지 않음(WARN≠FAIL) 명시 누락"


def test_writing_tokens_reference_ssot_not_relisted():
    """③ 토큰 SSOT = writing-craft.md §7 참조(verifier 가 재나열하지 않음)."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert "writing-craft.md §7" in body, \
        "verifier 가 writing 토큰 SSOT(writing-craft.md §7)를 참조 안 함"


def test_multibyte_detection_via_python_re():
    """④ 멀티바이트(em-dash) 검출은 Python re — LC_ALL=C grep 단독 신뢰 금지."""
    body = VERIFIER.read_text(encoding="utf-8")
    # writing WARN 검출도 abstract WARN 과 같은 멀티바이트 caveat 적용
    assert re.search(r"멀티바이트|multibyte", body), \
        "verifier 에 멀티바이트 grep 거짓음성 caveat 누락"
    assert re.search(r"Python\s*`?re|`?re`?\s*(로|모듈|만)", body), \
        "잔여 0건 확정을 Python re 로 한다는 규약 누락"


def test_rubric_verify_axis_has_writing_row():
    """⑤ paper-eval verify 축에 writing 규율 행 추가 + SSOT 참조."""
    body = RUBRIC.read_text(encoding="utf-8")
    assert re.search(r"writing 규율|글쓰기 규율", body), \
        "paper-eval verify 축에 writing 규율 행 누락"
    assert "writing-craft.md" in body, \
        "paper-eval 이 writing SSOT(writing-craft.md)를 참조 안 함"
    # WARN 임을 명시
    assert re.search(r"writing 규율[^\n|]*\(?WARN", body) or re.search(r"글쓰기 규율[^\n|]*WARN", body), \
        "paper-eval writing 행이 WARN 으로 표기 안 됨"


def test_abstract_warn_regression_intact():
    """⑥ 회귀: 기존 abstract 규율 WARN 이 그대로다 (새 writing WARN 과 별개)."""
    vbody = VERIFIER.read_text(encoding="utf-8")
    rbody = RUBRIC.read_text(encoding="utf-8")
    assert "abstract 규율" in vbody, "회귀: verifier abstract 규율 WARN 사라짐"
    assert "abstract 규율" in rbody, "회귀: paper-eval abstract 규율 행 사라짐"
    assert "latex.md §3" in vbody, "회귀: verifier 의 latex.md §3 SSOT 참조 사라짐"


def test_verifier_has_no_project_specific_proper_nouns():
    """⑦ 범용성 가드."""
    body = VERIFIER.read_text(encoding="utf-8")
    bad = re.compile(r"유선철|POSTECH|kimseungmin|ASV-ROV|형산강|316|PKRC", re.I)
    hits = [
        f"  scholar-verifier.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(body.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "배포 파일에 프로젝트 고유명사 잔존:\n" + "\n".join(hits)
