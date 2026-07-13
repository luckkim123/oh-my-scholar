"""Tests for the light-channel evidence signal at scholar-pilot Step 10 (R4 #24, Task 4).

Background: scholar-pilot Step 10 is the ONE place wiki appends happen. This task adds
an additive evidence-discipline bullet — an appended entry with no internal pointer
(`<slug> §…`) or verbatim quote is still appended, but the note's frontmatter is
created/kept at `confidence: low` with an `evidence: none` marker, and evidence-less
re-observation never raises confidence. It also replaces Step 10's old "(no machine
schema)" sentence with a pointer to `references/wiki/README.md`'s Frontmatter standard
(Task 3), since new note files now carry the standard thin frontmatter.
`references/wiki/README.md`'s evidence-recommendation block gains a short,
cross-referencing addition — SSOT for the append-time procedure stays with the pilot
skill, not restated there.

House convention (see test_state_schema_docs.py, test_wiki_spec_docs.py): plain asserts
via `skill_md("scholar-pilot")` + `.index()`-scoped windows, one discriminance test
proving the old `:61` sentence is actually gone (not just co-existing with new wording).
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
README = (ROOT / "references" / "wiki" / "README.md").read_text(encoding="utf-8")
PILOT = skill_md("scholar-pilot")

OLD_APPEND_SENTENCE = "A new category file is free-form .md (no machine schema)."


def _step10_section() -> str:
    idx = PILOT.index("10. **wiki capture")
    end = PILOT.index("11. **terminal cleanup")
    return PILOT[idx:end]


def _readme_evidence_section() -> str:
    idx = README.index("### ⭐ A note holds *conclusion + evidence* together")
    end = README.index("Example (conclusion + evidence together)")
    return README[idx:end]


# --------------------------------------------------------- pilot Step 10: :61 replacement (discriminance)
def test_step10_old_sentence_replaced():
    """Discriminance lock: the OLD unscoped sentence must be gone verbatim, and the
    '(no machine schema)' token must not survive anywhere in the skill body."""
    assert OLD_APPEND_SENTENCE not in PILOT, "old :61 sentence must be replaced"
    assert "(no machine schema)" not in PILOT, "old token must be fully gone"


def test_step10_new_note_gets_standard_frontmatter():
    sec = _step10_section()
    assert re.search(r"free-form body.{0,20}standard thin frontmatter", sec, re.I), \
        "new category/note files must be created with the standard frontmatter"
    assert "references/wiki/README.md" in sec and "Frontmatter standard" in sec


# --------------------------------------------------------- pilot Step 10: new evidence-signal bullet
def test_step10_evidence_signal_bullet_exists():
    sec = _step10_section()
    assert re.search(r"internal pointer", sec, re.I)
    assert re.search(r"verbatim quote", sec, re.I)


def test_step10_pointerless_entry_still_appended_not_gated():
    sec = _step10_section()
    assert re.search(r"still appended", sec, re.I)
    assert re.search(r"no reject gate|not a reject gate", sec, re.I)


def test_step10_forces_confidence_low_with_evidence_none_marker():
    sec = _step10_section()
    assert "confidence: low" in sec
    assert "(evidence: none — add a pointer before confidence can rise)" in sec


def test_step10_evidence_less_reobservation_never_raises_confidence():
    sec = _step10_section()
    assert re.search(r"evidence-less re-observation never raises confidence", sec, re.I)


# --------------------------------------------------------- README: cross-reference addition
def test_readme_evidence_block_cross_references_pilot_step10():
    sec = _readme_evidence_section()
    assert "scholar-pilot/SKILL.md" in sec and "Step 10" in sec
    assert "confidence: low" in sec
    assert "evidence: none" in sec


def test_readme_evidence_block_stays_consistent_not_a_reject_gate():
    sec = _readme_evidence_section()
    assert re.search(r"not a reject gate|no reject gate", sec, re.I)
    assert re.search(r"still appended", sec, re.I)


def test_readme_evidence_block_does_not_restate_full_pilot_procedure():
    """SSOT discipline: README cross-references but doesn't restate the pilot's full
    marker sentence — that prose lives at scholar-pilot Step 10."""
    sec = _readme_evidence_section()
    assert "add a pointer before confidence can rise" not in sec


def test_readme_no_automated_compliance_check_claim():
    sec = _readme_evidence_section()
    assert re.search(r"no automated compliance check|prompt-contract", sec, re.I)
