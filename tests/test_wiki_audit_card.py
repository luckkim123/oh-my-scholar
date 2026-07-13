"""Tests for the wiki-audit procedure card (R4 #23) — references/wiki/audit.md.

The card is the companion to `scripts/oms_wiki_audit.py` (Task 1, mechanical
dimensions). It carries the PROCEDURE: how to run the script, plus the two
JUDGMENT dimensions (SSOT-delegation integrity, strength-tag discipline)
that require reading meaning and cannot be scripted, ported faithfully from
the source workflow (`workspace/.oms/workflows/wiki-audit.js`), including
the strength-tag calibration block and the generalized calibration lesson.

House convention (see test_writing_craft_card.py): plain asserts on file
text, content-token locks. No duplicate-embedding check — the card must
point to the script's docstring/--help and references/wiki/README.md for
the mechanical dimension definitions rather than re-listing them.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CARD = ROOT / "references" / "wiki" / "audit.md"


def _body():
    return CARD.read_text(encoding="utf-8")


def test_card_exists():
    assert CARD.exists(), "references/wiki/audit.md missing — wiki-audit procedure card"


def test_title_line():
    """Line 1 matches house card title convention: `# <Title> — <subtitle>`."""
    lines = _body().splitlines()
    assert lines[0].startswith("# Wiki Audit — "), f"line 1 must match '^# Wiki Audit — ', got: {lines[0]!r}"


def test_consumer_blockquote():
    """Line 2 is a `> ` blockquote stating what the card is and who consumes it."""
    lines = _body().splitlines()
    assert lines[1].startswith("> "), f"line 2 must be a '> ' consumer blockquote, got: {lines[1]!r}"


def test_section1_points_to_the_script_not_a_restatement():
    """§1 gives real run instructions (--root, --write-index, once per level)
    and points to the script rather than re-listing its mechanical dimensions."""
    body = _body()
    assert "oms_wiki_audit.py" in body
    assert "--root" in body
    assert "--write-index" in body
    assert "once per level" in body


def test_section2_ssot_delegation_dimension():
    """§2 — SSOT-delegation integrity: broken + cyclic delegation, ported
    from the source workflow prompt (quote the delegating sentence, verify
    the target owns the topic, never flag healthy one-directional delegation)."""
    body = _body()
    assert "SSOT-delegation" in body
    assert re.search(r"broken delegation", body, re.I)
    assert re.search(r"cyclic delegation", body, re.I)
    assert re.search(r"never flag.*healthy|healthy.*never flag|do not flag.*healthy", body, re.I), \
        "must preserve 'do not flag a healthy one-directional delegation' guidance"


def test_section3_strength_tag_calibration_exact_wording_governs():
    """§3 — strength-tag discipline WITH the calibration block ported
    verbatim in substance: the rule's exact wording governs."""
    body = _body()
    assert "strength-tag" in body
    assert re.search(r"exact wording governs", body, re.I), \
        "calibration rule 'the rule's exact wording governs' must be preserved"
    assert "[N편공통]" in body, "quoted Korean rule text must stay verbatim (quotes the live wiki's own rule)"
    assert "1편에서만 본 걸 공통이라 쓰지 않는다" in body or "1편에서만 본 걸 \"공통\"이라 쓰지 않는다" in body


def test_section3_naming_two_papers_passes_without_inline_quotes():
    """A tag NAMING 2+ distinct papers passes even without inline quotes —
    the naming attests the multi-paper observation."""
    body = _body()
    assert re.search(r"2\+?\s*(distinct )?papers?.{0,40}pass", body, re.I) or \
        re.search(r"names?.{0,20}2\+?\s*(distinct )?papers?.{0,60}(pass|satisf)", body, re.I), \
        "must state a tag naming 2+ distinct papers PASSES (even without inline quotes)"


def test_section3_defect_is_only_count_exceeds_named_sources():
    """A defect is ONLY tagged-count > named-or-quoted distinct sources."""
    body = _body()
    assert re.search(r"tagged.count.{0,40}exceed", body, re.I) or \
        re.search(r"exceed.{0,60}named.or.quoted", body, re.I), \
        "must state the defect condition: tagged count exceeds named-or-quoted distinct sources"


def test_section3_one_reminder_per_file_not_per_tag():
    """At most one independence-cluster reminder per file, not one per tag."""
    body = _body()
    assert re.search(r"one.{0,20}reminder per file", body, re.I)
    assert re.search(r"not (one )?per tag", body, re.I)


def test_section4_calibration_lesson_generalized():
    """§4 — the generalized calibration lesson: when a dimension's findings
    diverge from expectation, audit the criteria first, then the corpus."""
    body = _body()
    assert re.search(r"audit the criteria", body, re.I)
    assert "2026-06-02" in body, "must cite the 2026-06-02 incident as the worked example"


def test_section5_detection_only_discipline():
    """§5 — the audit NEVER edits the wiki; findings ranked high/medium/low
    with file:line evidence."""
    body = _body()
    assert re.search(r"never edits the wiki", body, re.I)
    assert re.search(r"high\s*/\s*medium\s*/\s*low|high/medium/low", body, re.I)
    assert "file:line" in body


def test_no_duplicate_embedding_of_mechanical_dimension_definitions():
    """House discipline: point to the script's docstring/--help and
    references/wiki/README.md instead of re-listing mechanical dimension
    definitions (dangling refs, duplicate section tokens, frontmatter, etc.)."""
    body = _body()
    assert "references/wiki/README.md" in body
    assert re.search(r"--help|docstring", body, re.I)


def test_section_numbers_present_in_order():
    body = _body()
    tokens = re.findall(r"^##\s*§(\d)", body, re.M)
    assert tokens == sorted(tokens), f"§-numbered sections out of order: {tokens}"
    assert set(tokens) >= {"1", "2", "3", "4", "5"}, f"missing §-numbered sections, found: {tokens}"
