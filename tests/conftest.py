"""Shared test helpers for oms's test suite.

`skill_md` centralizes reading a skill's full instruction body. After the
R3 #21 shim + skill-bodies/ split, `skills/<name>/SKILL.md` is a compact
pointer shim (routing surface only) and the full text lives at
`skill-bodies/<name>/SKILL.md`. Tests that lock skill *content* read through
this one helper instead of hand-building `skills/...` paths, so a future
reshuffle of the split only has to change this file."""
from pathlib import Path

SKILL_BODIES = Path(__file__).parent.parent / "skill-bodies"


def skill_md(name: str) -> str:
    """Full SKILL.md body text for skill `name` (from skill-bodies/, not skills/)."""
    path = SKILL_BODIES / name / "SKILL.md"
    if not path.is_file():
        raise FileNotFoundError(
            f"skill body not found: {path} (expected skill-bodies/{name}/SKILL.md — "
            "has the R3 #21 shim split run yet?)"
        )
    return path.read_text(encoding="utf-8")
