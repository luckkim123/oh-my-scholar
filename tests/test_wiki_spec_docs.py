"""Tests for the wiki frontmatter + INDEX.md contract standardized across the three
spec surfaces (R4 #25, Task 3) — `references/wiki/README.md`, `references/output-layout.md`,
`references/learning-protocol.md`.

Background: Task 1 (`scripts/oms_wiki_audit.py`) already parses a thin, stdlib-only
frontmatter (`confidence`/`sightings`) and can generate a deterministic `INDEX.md` via
`--write-index`, but no spec card formalized the frontmatter SYNTAX (as opposed to what
`confidence` *means*, already covered) or the INDEX.md contract, and output-layout.md's
`.oms/wiki/` block still listed only three of the five wiki categories. This task adds a
`## Frontmatter standard (thin, stdlib-parsable)` section to the README (syntax SSOT),
re-scopes README.md's old unscoped "no machine-parsing schema" sentence to a body-scoped
one (the frontmatter fence is now machine-parsable), fixes output-layout.md's category
list + adds the INDEX.md line + a §6 checklist row, and adds a one-line non-restating
pointer from learning-protocol.md's confidence section to the new syntax SSOT.

House convention (see test_consensus_layout.py, test_wiki_audit_card.py): plain asserts
on file text and content tokens; a `section()` helper to scope assertions to the right
heading block; one discriminance test proving the `:38` sentence replacement actually
happened (old verbatim string gone, new one present) rather than just co-existing.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
README = ROOT / "references" / "wiki" / "README.md"
LAYOUT = ROOT / "references" / "output-layout.md"
LEARNING = ROOT / "references" / "learning-protocol.md"

OLD_SENTENCE = "No machine-parsing schema (grep only)."


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, start_pattern: str, end_pattern: str) -> str:
    """Extract text between a heading and the next given heading (exclusive of both)."""
    start_m = re.search(start_pattern, text, re.MULTILINE)
    assert start_m, f"heading not found: {start_pattern}"
    rest = text[start_m.end():]
    end_m = re.search(end_pattern, rest, re.MULTILINE)
    return rest[: end_m.start()] if end_m else rest


# --------------------------------------------------------- README: :38 re-scope (discriminance)
def test_readme_old_unscoped_sentence_replaced():
    """Discriminance lock: the OLD unscoped sentence ("the whole file has no machine-parsing
    schema") must be gone verbatim, while a NEW body-scoped sentence (frontmatter IS now
    machine-parsable; only the body stays grep-only) takes its place."""
    body = _read(README)
    assert OLD_SENTENCE not in body, f"old unscoped sentence must be replaced: {OLD_SENTENCE!r}"
    assert re.search(r"body.{0,80}no machine-parsing schema", body, re.I | re.S), \
        "new sentence must scope 'no machine-parsing schema' to the note BODY, not the whole file"
    assert re.search(r"frontmatter.{0,80}machine-parsable", body, re.I | re.S), \
        "new sentence must state the frontmatter fence IS machine-parsable"


# --------------------------------------------------------- README: Frontmatter standard section
def test_readme_frontmatter_standard_section_exists():
    body = _read(README)
    assert "## Frontmatter standard (thin, stdlib-parsable)" in body


def test_readme_frontmatter_standard_syntax_contract():
    body = _read(README)
    sec = section(body, r"^## Frontmatter standard", r"^## `wiki_query")
    assert "confidence: high | med | low" in sec
    assert "sightings: <int>" in sec
    assert "keywords" in sec and "comma-separated" in sec
    assert re.search(r"flat.{0,20}`?key: value`?.{0,20}only", sec, re.I), \
        "must state flat key:value only"
    assert re.search(r"no nesting.{0,10}no lists", sec, re.I)
    assert re.search(r"body.{0,20}free-form", sec, re.I)


def test_readme_frontmatter_standard_cross_references_confidence_semantics_not_restated():
    """SSOT discipline: the new section must point at the existing confidence-semantics
    subsection rather than re-explaining what confidence MEANS or how it climbs."""
    body = _read(README)
    sec = section(body, r"^## Frontmatter standard", r"^## `wiki_query")
    assert re.search(r"confidence frontmatter|above", sec, re.I), \
        "must cross-reference the existing confidence subsection"
    assert "low → med → high" not in sec, \
        "must not restate the confidence-climb mechanic (that prose lives in the confidence subsection)"


# --------------------------------------------------------- README: INDEX.md contract
def test_readme_index_contract_present():
    body = _read(README)
    sec = section(body, r"^## Frontmatter standard", r"^## `wiki_query")
    assert "INDEX.md" in sec
    assert "never hand-edited" in sec
    assert "--write-index" in sec
    assert re.search(r"each wiki root", sec, re.I)
    assert re.search(r"\bWARN\b", sec), "drift must be documented as WARN (non-blocking)"


def test_readme_index_is_not_a_query_surface():
    body = _read(README)
    sec = section(body, r"^## Frontmatter standard", r"^## `wiki_query")
    assert re.search(r"not a query surface", sec, re.I)
    assert re.search(r"grep", sec, re.I), "must still point recall at grep over the notes"


# --------------------------------------------------------- output-layout.md: five categories
def test_output_layout_wiki_block_has_all_five_categories():
    body = _read(LAYOUT)
    sec = section(body, r"^\.oms/wiki/", r"^\.oms/notepad\.md")
    for cat in ("convention/", "pattern/", "decision/", "reference/", "history/"):
        assert cat in sec, f"{cat} missing from .oms/wiki/ block"


def test_output_layout_wiki_block_notes_history_is_global_only():
    body = _read(LAYOUT)
    sec = section(body, r"^\.oms/wiki/", r"^\.oms/notepad\.md")
    assert re.search(r"history/.{0,60}global", sec, re.I) or re.search(r"global.{0,60}history/", sec, re.I), \
        "history/ must be annotated as global-level only"


def test_output_layout_wiki_block_has_index_line():
    body = _read(LAYOUT)
    sec = section(body, r"^\.oms/wiki/", r"^\.oms/notepad\.md")
    assert "INDEX.md" in sec
    assert "scripts/oms_wiki_audit.py --write-index" in sec
    assert "never hand-edited" in sec


# --------------------------------------------------------- output-layout.md: §6 checklist row
def test_output_layout_checklist_has_index_regeneration_row():
    body = _read(LAYOUT)
    sec = section(body, r"^## 6\. Implementation checklist", r"\Z")
    assert re.search(r"INDEX\.md", sec)
    assert re.search(r"--write-index", sec)
    assert re.search(r"never hand-edited", sec, re.I)


# --------------------------------------------------------- output-layout.md: Task 5 territory untouched
def test_output_layout_per_slug_tree_and_cleanup_table_untouched():
    """This task must not touch the per-slug tree or §5 cleanup table — that's Task 5's
    territory. Sanity check: the consensus/ entry (owned by an earlier task) is still intact
    and §5's row count for known targets is unchanged in shape (still has the consensus row)."""
    body = _read(LAYOUT)
    sec5 = section(body, r"^## 5\. Terminal cleanup", r"^## 6\.")
    assert "consensus/" in sec5


# --------------------------------------------------------- learning-protocol.md: pointer only
def test_learning_protocol_confidence_section_points_to_frontmatter_standard():
    body = _read(LEARNING)
    sec = section(body, r"^### ⭐ confidence on wiki notes", r"^\*\*Wiki notes are append-only")
    assert "references/wiki/README.md" in sec
    assert re.search(r"Frontmatter standard", sec)


def test_learning_protocol_does_not_restate_frontmatter_syntax():
    """SSOT discipline: the pointer line must not duplicate the syntax details (flat key:value,
    no nesting/no lists) that now live in README.md's Frontmatter standard section."""
    body = _read(LEARNING)
    sec = section(body, r"^### ⭐ confidence on wiki notes", r"^\*\*Wiki notes are append-only")
    assert "no nesting" not in sec
    assert "no lists" not in sec
