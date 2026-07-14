"""Tests for the GROBID intake reference card (R6 U2 #36) — references/grobid-intake.md.

Same genre as `references/wiki/audit.md` (E2): a standalone reference card
documenting an optional accelerator's contract. House convention (see
test_wiki_audit_card.py): plain asserts on file text, content-token locks.

GROBID proposes, never commits — every proposed entry still passes the same
human-confirm gate + `verify_bib_entry.py` mechanical check + cite-guard
before any `.bib` write; absence degrades to today's manual path, unchanged.
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
CARD = ROOT / "references" / "grobid-intake.md"


def _body():
    return CARD.read_text(encoding="utf-8")


def test_card_exists():
    assert CARD.exists(), "references/grobid-intake.md missing — GROBID intake reference card"


def test_title_line():
    """Line 1 matches house card title convention: `# <Title> — <subtitle>`."""
    lines = _body().splitlines()
    assert lines[0].startswith("# GROBID Intake — "), f"line 1 must match '^# GROBID Intake — ', got: {lines[0]!r}"


def test_consumer_blockquote():
    """Line 2 is a `> ` blockquote stating what the card is and who consumes it."""
    lines = _body().splitlines()
    assert lines[1].startswith("> "), f"line 2 must be a '> ' consumer blockquote, got: {lines[1]!r}"


def test_section1_what_and_when_optional_self_hosted():
    body = _body()
    assert re.search(r"self-hosted", body, re.I)
    assert re.search(r"optional", body, re.I)
    assert "scholar-read" in body
    assert "scholar-research" in body


def test_section2_flow_pdf_to_tei_to_proposed_to_human_to_verify_to_bib():
    """§2 — the intake flow: PDF → TEI → proposed entries → human confirms
    every entry → verify_bib_entry.py → only then .bib."""
    body = _body()
    assert re.search(r"TEI", body)
    assert re.search(r"proposed", body, re.I)
    assert re.search(r"verify_bib_entry\.py", body)
    assert re.search(r"human confirms\s+every\s+entry|human-confirm", body, re.I), \
        "must state a human confirms EVERY proposed entry"


def test_section3_accuracy_hedged_as_reported():
    """§3 — F1 figure cited as an external report, hedged, never asserted as
    settled fact; failure modes hedged the same way."""
    body = _body()
    assert re.search(r"F1\s*[≈~]?\s*0\.8", body), "reported F1 figure missing"
    assert re.search(r"commonly reported", body, re.I), \
        "failure modes must be hedged as 'commonly reported — verify against GROBID's own documentation'"
    assert re.search(r"two.column", body, re.I)
    assert re.search(r"non-English", body, re.I)
    assert re.search(r"DOI", body)


def test_section4_degrade_path_unchanged():
    body = _body()
    assert re.search(r"degrade", body, re.I)
    assert re.search(r"unchanged", body, re.I)
    assert re.search(r"manual", body, re.I)


def test_section5_boundary_proposes_never_commits():
    body = _body()
    assert re.search(r"proposes,?\s*never commits", body, re.I), \
        "must state 'GROBID proposes, never commits'"
    assert re.search(r"cite-guard", body)
    assert re.search(r"not a citation authority", body, re.I)


def test_section_numbers_present_in_order():
    body = _body()
    tokens = re.findall(r"^##\s*§(\d)", body, re.M)
    assert tokens == sorted(tokens), f"§-numbered sections out of order: {tokens}"
    assert set(tokens) >= {"1", "2", "3", "4", "5"}, f"missing §-numbered sections, found: {tokens}"


# ---------------------------------------------------------- skill-body pointer lines (wiring)

def test_scholar_read_points_at_card():
    body = skill_md("scholar-read")
    assert "references/grobid-intake.md" in body, \
        "scholar-read SKILL.md must point at references/grobid-intake.md (no behavior change)"


def test_scholar_research_points_at_card():
    body = skill_md("scholar-research")
    assert "references/grobid-intake.md" in body, \
        "scholar-research SKILL.md must point at references/grobid-intake.md (no behavior change)"
