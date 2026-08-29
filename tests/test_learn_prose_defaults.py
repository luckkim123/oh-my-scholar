"""Tests for the learn bifurcation — venue.prose_defaults 승격 + light 채널 이원화.

배경(2026-06-01): writing-style 규칙(flow/tone)을 venue 기본값으로 승격할 길이 없었다 —
candidate_default.target enum 이 구조·포맷(required_sections·section_order·self_citation_max_ratio)
만 허용. 처방(사용자 결정 "강제기본값+light 이원화"): enum 에 venue.prose_defaults 추가(보편
명제를 venue-강제 승격) + user/venue 특이 표현은 light 채널 topic:convention post(advisory).
둘 다 사람 게이트. (r7 2026-08-30: light 채널 저장 형태가 wiki 페이지트리에서 post 스토어로
전환됐다 — 이 파일의 검증 대상은 이원화 로직 자체라 영향 없음.)

⚠️ 회귀: citation/.bib 는 영구 비승격(§6.F). 설계: design.md §3.6.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROTOCOL = ROOT / "references" / "learning-protocol.md"
VENUES = ROOT / "references" / "venues.md"


def test_enum_includes_prose_defaults():
    """① candidate_default.target enum 에 venue.prose_defaults 추가."""
    body = PROTOCOL.read_text(encoding="utf-8")
    assert "venue.prose_defaults" in body, \
        "learning-protocol enum 에 venue.prose_defaults 누락 (보편 글쓰기 명제 승격 경로)"


def test_venues_schema_has_prose_defaults_and_voice():
    """② venues.md 스키마에 prose_defaults·voice 필드 문서화."""
    body = VENUES.read_text(encoding="utf-8")
    assert "prose_defaults:" in body, "venues.md 스키마에 prose_defaults 필드 누락"
    assert "voice:" in body, "venues.md 스키마에 voice 필드 누락"


def test_light_channel_for_user_specific_phrasing():
    """③ light 채널(topic: convention post) — user/venue 특이 표현은 advisory."""
    body = PROTOCOL.read_text(encoding="utf-8")
    # 이원화: 보편 명제 = 강제 default / 특이 표현 = light 채널
    assert re.search(r"prose_defaults.{0,200}(보편|universal)", body, re.S) or \
        re.search(r"(보편|universal).{0,200}prose_defaults", body, re.S), \
        "prose_defaults 가 *보편 명제* 강제용임이 명시 안 됨"
    assert re.search(r"특이.{0,30}표현|표현 선호|phrasing", body), \
        "user/venue 특이 표현이 light 채널(advisory)로 간다는 이원화 명시 누락"


def test_prose_defaults_human_gated():
    """④ prose_defaults 승격도 사람 게이트(자동 승격 없음)."""
    body = PROTOCOL.read_text(encoding="utf-8")
    # heavy 채널 = 사람 게이트 (기존 규약이 prose_defaults 에도 적용됨이 보여야)
    assert re.search(r"prose_defaults.{0,400}(사람 게이트|human gate|승인)", body, re.S) or \
        re.search(r"(heavy|기본값).{0,400}사람 게이트", body, re.S), \
        "prose_defaults 가 heavy 채널(사람 게이트)임이 명시 안 됨"


def test_citation_permanently_non_promotable_regression():
    """⑤ 회귀: citation/.bib 는 영구 비승격(§6.F) — prose_defaults 추가가 이를 흔들지 않음."""
    body = PROTOCOL.read_text(encoding="utf-8")
    assert "§6.F" in body, "회귀: §6.F citation 영구금지 invariant 사라짐"
    assert re.search(r"permanently forbidden|영구.{0,4}(금지|forbidden)|never promoted", body), \
        "회귀: citation 영구 비승격 규약 사라짐"
    # citation 을 target 으로 명명하면 거부하는 가드 잔존
    assert re.search(r"target.{0,40}citation.{0,40}(거부|reject|forbidden)|citation.*bib.*거부", body, re.S | re.I) or \
        "citations never enter the post store" in body, \
        "회귀: citation target 거부 가드 사라짐"


def test_venues_prose_defaults_not_relisting_rules():
    """⑥ venues.md prose_defaults 는 값만 — 규칙 본문은 writing-craft.md 참조(SSOT 분리)."""
    body = VENUES.read_text(encoding="utf-8")
    # prose_defaults 필드 설명이 writing-craft.md 를 SSOT 로 가리켜야 (규칙 재나열 금지)
    assert "writing-craft.md" in body, \
        "venues.md 가 prose 규칙 SSOT(writing-craft.md)를 참조 안 함 (규칙 재나열 위험)"


def test_no_project_specific_proper_nouns():
    """⑦ 범용성 가드 — 두 배포 파일."""
    bad = re.compile(r"ADVISOR_X|kimseungmin|PROJ_TITLE_X|SITE_X|ORG_X|ROOM_X", re.I)
    for path in (PROTOCOL, VENUES):
        body = path.read_text(encoding="utf-8")
        hits = [
            f"  {path.name}:{i}: {ln.strip()[:80]}"
            for i, ln in enumerate(body.splitlines(), 1)
            if bad.search(ln)
        ]
        assert not hits, f"{path.name} 에 프로젝트 고유명사 잔존:\n" + "\n".join(hits)
