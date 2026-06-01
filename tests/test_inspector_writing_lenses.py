"""Tests for the inspector lens upgrade — prose lens(FLOW/TONE) + reverse-outline + 과대일반화.

배경(2026-06-01): inspector prose lens 가 vague 목록("과장 규율, 반복, 전환, 문장 길이")만.
logic lens 에 과대일반화(최대 실패모드 51%) 커버리지 0. 처방: prose lens 를 writing-craft.md
§1(FLOW)·§2(TONE) actionable 체크로 업그레이드 + reverse-outline audit(skeleton 재사용) +
logic lens 에 과대일반화 flag(formative-only, citation-safe 경계). 설계: design.md §3.5.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
INSPECTOR = ROOT / "agents" / "scholar-inspector.md"


def test_prose_lens_references_writing_craft():
    """① prose lens 가 writing-craft.md §1(FLOW)/§2(TONE)을 참조(vague 목록 탈피)."""
    body = INSPECTOR.read_text(encoding="utf-8")
    assert "writing-craft.md" in body, \
        "inspector prose lens 가 writing-craft.md SSOT 를 참조 안 함"
    # FLOW actionable 체크 (old→new / banana)
    assert re.search(r"old\s*[→\-]+\s*new|구정보.*신정보|banana|stress position", body), \
        "prose lens 에 actionable FLOW 체크(old→new/banana) 누락"


def test_reverse_outline_audit_present():
    """② reverse-outline audit 절차 — topic sentence 추출→논지 연결 체크."""
    body = INSPECTOR.read_text(encoding="utf-8")
    assert re.search(r"reverse.outline|역.?아웃라인|reverse outline", body, re.I), \
        "inspector 에 reverse-outline audit 누락"
    # topic sentence 추출 → 논지 연결 체크
    assert re.search(r"topic sentence", body, re.I), \
        "reverse-outline 의 topic sentence 추출 단계 누락"
    # skeleton 재사용 (drafter Step A 산출물)
    assert re.search(r"skeleton|골격", body), \
        "reverse-outline 이 drafter skeleton 재사용을 언급 안 함"


def test_overgeneralization_flag_present():
    """③ logic lens 에 과대일반화 flag — #1 우선·formative-only."""
    body = INSPECTOR.read_text(encoding="utf-8")
    assert re.search(r"과대일반화|overgeneraliz", body), \
        "logic lens 에 과대일반화 flag 누락"
    # 최대 실패모드 / #1 우선
    assert re.search(r"최대 실패|#1|1순위|가장 흔한", body), \
        "과대일반화가 최대 실패모드(우선순위)임이 명시 안 됨"


def test_overgeneralization_is_formative_only():
    """④ 과대일반화는 formative flag 만 — citation-safe 경계(자동 FAIL 아님)."""
    body = INSPECTOR.read_text(encoding="utf-8")
    # 인용 근거보다 넓은 주장 = formative flag, FAIL 아님 (verifier 영역 아님)
    assert re.search(r"근거보다 넓|broader than|인용 근거", body), \
        "과대일반화 정의(인용 근거보다 넓은 주장) 누락"
    # formative — assumption FRAGILE 의 형제, 자동 FAIL 금지
    assert re.search(r"FRAGILE|formative|판정 아님|FAIL 아님", body), \
        "과대일반화가 formative-only(자동 FAIL 아님)임이 명시 안 됨"


def test_inspector_two_lens_regression():
    """⑤ 회귀: logic⊥prose 2-lens 구조·formative(PASS/FAIL 금지)·evidence 날조 금지 유지."""
    body = INSPECTOR.read_text(encoding="utf-8")
    assert "logic 렌즈" in body and "prose 렌즈" in body, "회귀: 2-lens 구조 사라짐"
    # formative — PASS/FAIL 판정 금지
    assert re.search(r"pass/fail이 아니|PASS.{0,3}FAIL.{0,6}(아니|금지)", body), \
        "회귀: formative(pass/fail 아님) 규약 사라짐"
    # evidence 날조 금지
    assert re.search(r"evidence 날조 금지|날조하지", body), "회귀: evidence 날조 금지 규약 사라짐"
    # assumption FRAGILE 라벨 유지
    assert "FRAGILE" in body, "회귀: assumption FRAGILE 라벨 사라짐"


def test_inspector_has_no_project_specific_proper_nouns():
    """⑥ 범용성 가드."""
    body = INSPECTOR.read_text(encoding="utf-8")
    bad = re.compile(r"유선철|POSTECH|kimseungmin|ASV-ROV|형산강|316|PKRC", re.I)
    hits = [
        f"  scholar-inspector.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(body.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "배포 파일에 프로젝트 고유명사 잔존:\n" + "\n".join(hits)
