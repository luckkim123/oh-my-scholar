"""Tests for the `.md` stage-output layout rule — research/ideate/outline 중간산출물 위치.

배경(2026-05-31): research/ideate/outline 의 `.md` 중간산출물(연구맵·개념노트·
outline)을 source 폴더(`paper/…`)에 두는 사고가 있었다. 원인 둘:
  ① output-layout.md 가 `.tex`/`.bib`/PDF 위치만 규정 → `.md` 레이어 "공백".
  ② scholar-research/ideate 본문이 `paper/research`·`paper/methodology` 를
     *예시로 유도* → output-layout.md(source ≠ intermediate)와 자기모순.
처방: output-layout.md §2 에 `.md` 레이어(research/methodology/outline)를 `.oms/<slug>/`
하위 고정 경로로 명시 + 스킬 본문을 `.oms/<slug>/…` 로 정정. 이 테스트가 그 드리프트를 막는다.
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
LAYOUT = ROOT / "references" / "output-layout.md"

# `.md` 스테이지 스킬과 각자가 SSOT 로 가리켜야 하는 작업장 하위 폴더
MD_STAGE = {
    "scholar-research": "research",
    "scholar-ideate": "methodology",
    "scholar-outline": "outline",
}

# 이번 버그의 정확한 패턴: source 폴더(paper/) 안에 스테이지 폴더를 두라는 오유도
BAD_PATTERN = re.compile(r"paper/(?:research|methodology|outline|ideate)")


def test_output_layout_defines_md_stage_layer():
    """① output-layout.md 가 `.md` 레이어 3폴더를 `.oms/<slug>/` SSOT 로 명시한다.

    규칙의 *존재* 검증 — 공백(이번 버그의 근본 원인)이 다시 생기지 않게."""
    text = LAYOUT.read_text(encoding="utf-8")
    for folder in ("research", "methodology", "outline"):
        # .oms/<slug>/<folder>/ 형태가 카드에 등장해야 한다
        assert re.search(rf"\.oms/<slug>/.*\b{folder}\b", text) or \
            re.search(rf"^\s*{folder}/", text, re.MULTILINE), \
            f"output-layout.md 에 `.md` 레이어 '{folder}/' 규정 누락"


def test_md_stage_skills_have_no_source_folder_misdirection():
    """② `.md`-stage 스킬 본문에 source 폴더 오유도(`paper/research` 등)가 없다.

    자기모순(이번 버그의 직접 원인)의 *부재* 검증."""
    for skill in MD_STAGE:
        body = skill_md(skill)
        hits = [
            f"  {skill}/SKILL.md:{i}: {ln.strip()[:80]}"
            for i, ln in enumerate(body.splitlines(), 1)
            if BAD_PATTERN.search(ln)
        ]
        assert not hits, "source 폴더 오유도 잔존:\n" + "\n".join(hits)


def test_md_stage_skills_point_to_work_area():
    """③ 각 `.md`-stage 스킬이 자기 산출물의 작업장 경로(`.hq/work/scholar/<slug>/<folder>`)를 가리킨다.

    올바른 경로의 *존재* 검증 — ②(나쁜 패턴 부재)와 짝."""
    for skill, folder in MD_STAGE.items():
        body = skill_md(skill)
        assert re.search(rf"\.hq/work/scholar/<slug>/{folder}", body), \
            f"{skill} 이 작업장 경로 `.hq/work/scholar/<slug>/{folder}` 를 가리키지 않음"
