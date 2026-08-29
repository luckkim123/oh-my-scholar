"""Tests for the post-store contract standardized across the three spec surfaces
(R4 #25 originally; rewired r7 2026-08-30) — `references/knowledge/README.md`,
`references/output-layout.md`, `references/learning-protocol.md`.

Background: this file originally tested the wiki page-tree form's thin frontmatter
syntax (parsed by the now-deleted `scripts/oms_wiki_audit.py`) and its `INDEX.md`
`--write-index` contract. The wiki form is retired (r7, user decision: "wiki 는 아예
없애는 걸로. Wiki 폴더 안만들게") — the store is now `.hq/community/posts/`, `hq` owns
the frontmatter shape (store-spec §4) directly, and `.hq/community/INDEX.md`
regenerates automatically inside `hq post`/`hq edit`. The frontmatter-syntax tests
have no successor (that schema is hq's, not this plugin's, to define) and are
dropped; the INDEX.md tests are rewired to the new automatic-regeneration contract;
the citation_lookup() contract tests are untouched in substance (that abstract
function was never wiki-specific) and only need the README's new path.

House convention (see test_consensus_layout.py, test_wiki_audit_card.py): plain asserts
on file text and content tokens; a `section()` helper to scope assertions to the right
heading block.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
README = ROOT / "references" / "knowledge" / "README.md"
LAYOUT = ROOT / "references" / "output-layout.md"
LEARNING = ROOT / "references" / "learning-protocol.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, start_pattern: str, end_pattern: str) -> str:
    """Extract text between a heading and the next given heading (exclusive of both)."""
    start_m = re.search(start_pattern, text, re.MULTILINE)
    assert start_m, f"heading not found: {start_pattern}"
    rest = text[start_m.end():]
    end_m = re.search(end_pattern, rest, re.MULTILINE)
    return rest[: end_m.start()] if end_m else rest


# --------------------------------------------------------- README: old location gone
def test_old_wiki_readme_location_gone():
    assert not (ROOT / "references" / "wiki").exists(), \
        "references/wiki/ must be gone — git mv'd to references/knowledge/ (r7)"


# --------------------------------------------------------- README: frontmatter ownership moved to hq
def test_readme_states_hq_owns_frontmatter_shape():
    """The retired form's local 'Frontmatter standard' section (parsed by the deleted
    oms_wiki_audit.py) has no successor in this plugin — hq owns the post schema
    (store-spec §4) directly. The README must say so rather than re-defining a syntax."""
    body = _read(README)
    assert re.search(r"`?hq`?\s+owns\s+the\s+frontmatter\s+shape", body, re.I)
    assert "store-spec" in body


def test_readme_no_leftover_frontmatter_standard_section():
    body = _read(README)
    assert "## Frontmatter standard" not in body, \
        "the thin-frontmatter syntax section described the retired wiki form and has no successor"


# --------------------------------------------------------- README: INDEX.md contract (now automatic)
def test_readme_index_contract_present():
    body = _read(README)
    sec = section(body, r"^## Reading it", r"^## `citation_lookup")
    assert "INDEX.md" in sec
    assert "never hand-edited" in sec
    assert re.search(r"automatic", sec, re.I)


def test_readme_index_is_not_a_query_surface():
    body = _read(README)
    sec = section(body, r"^## Reading it", r"^## `citation_lookup")
    assert re.search(r"not a query surface", sec, re.I)
    assert re.search(r"hq query", sec, re.I), "must still point recall at hq query over the posts"


def test_readme_ascend_omission_warning_present():
    """The single most likely way to lose the global level by accident: forgetting
    --ascend. This warning survived the form change unchanged in spirit."""
    body = _read(README)
    sec = section(body, r"^## Reading it", r"^## `citation_lookup")
    assert "--ascend" in sec
    assert re.search(r"nearest anchor only", sec, re.I)


# --------------------------------------------------------- README: citation_lookup() contract (R6 U1 #35, untouched in substance)
def test_readme_citation_lookup_contract_section_exists():
    body = _read(README)
    assert "## `citation_lookup(doi_or_title)` abstract function contract" in body
    assert "citation_lookup(" in body


def test_readme_citation_lookup_swap_points_named():
    body = _read(README)
    sec = section(body, r"^## `citation_lookup", r"^## Data this store collects")
    assert "Semantic Scholar MCP" in sec
    assert "arXiv MCP" in sec
    assert "Zotero MCP" in sec


def test_readme_citation_lookup_zotero_human_gate_adjacent():
    body = _read(README)
    sec = section(body, r"^## `citation_lookup", r"^## Data this store collects")
    assert re.search(r"Zotero.{0,200}human gate", sec, re.I | re.S), \
        "Zotero row must be adjacent to a human-gate statement"


def test_readme_citation_lookup_empirical_validation_rule():
    body = _read(README)
    sec = section(body, r"^## `citation_lookup", r"^## Data this store collects")
    assert re.search(r"empirical", sec, re.I)
    assert re.search(r"probe call", sec, re.I)


def test_readme_citation_lookup_fallback_chain():
    body = _read(README)
    sec = section(body, r"^## `citation_lookup", r"^## Data this store collects")
    assert "WebSearch" in sec and "WebFetch" in sec
    assert re.search(r"fallback chain", sec, re.I)


def test_readme_citation_lookup_mcp_absence_changes_nothing():
    body = _read(README)
    sec = section(body, r"^## `citation_lookup", r"^## Data this store collects")
    assert re.search(r"[Aa]bsence of every MCP.{0,80}nothing", sec, re.S)


# --------------------------------------------------------- output-layout.md: posts/ block
def test_output_layout_posts_block_has_all_five_topics():
    body = _read(LAYOUT)
    sec = section(body, r"^\.hq/community/posts/", r"^\.hq/community/INDEX\.md")
    for topic in ("convention", "pattern", "decision", "reference", "history"):
        assert topic in sec, f"topic {topic!r} missing from .hq/community/posts/ block"


def test_output_layout_posts_block_notes_history_is_global_only():
    body = _read(LAYOUT)
    sec = section(body, r"^\.hq/community/posts/", r"^\.hq/community/INDEX\.md")
    assert re.search(r"history.{0,60}global", sec, re.I) or re.search(r"global.{0,60}history", sec, re.I), \
        "history must be annotated as global-level only"


def test_output_layout_index_line_documents_automatic_regeneration():
    body = _read(LAYOUT)
    idx = body.index(".hq/community/INDEX.md")
    line = body[idx: idx + 200]
    assert re.search(r"generated by", line, re.I)
    assert "never hand-edited" in line


# --------------------------------------------------------- output-layout.md: §6 checklist row
def test_output_layout_checklist_has_index_regeneration_row():
    body = _read(LAYOUT)
    sec = section(body, r"^## 6\. Implementation checklist", r"\Z")
    assert re.search(r"INDEX\.md", sec)
    assert re.search(r"never hand-edited", sec, re.I)
    assert "--write-index" not in sec, \
        "the retired script's --write-index flag has no successor — regeneration is automatic now"


# --------------------------------------------------------- output-layout.md: Task 5 territory untouched
def test_output_layout_per_slug_tree_and_cleanup_table_untouched():
    """This task must not touch the per-slug tree or §5 cleanup table — that's Task 5's
    territory. Sanity check: the consensus/ entry (owned by an earlier task) is still intact
    and §5's row count for known targets is unchanged in shape (still has the consensus row)."""
    body = _read(LAYOUT)
    sec5 = section(body, r"^## 5\. Terminal cleanup", r"^## 6\.")
    assert "consensus/" in sec5


# --------------------------------------------------------- learning-protocol.md: confidence-on-posts section
def test_learning_protocol_confidence_section_points_to_hq_ownership():
    """The pointer now names hq/store-spec as the frontmatter-shape owner instead of a
    local 'Frontmatter standard' section that no longer exists."""
    body = _read(LEARNING)
    sec = section(body, r"^### ⭐ confidence on posts", r"^\*\*Posts are immutable")
    assert re.search(r"`?hq`?\s+owns", sec, re.I)
    assert "store-spec" in sec


def test_learning_protocol_does_not_restate_frontmatter_syntax():
    """SSOT discipline: the pointer line must not duplicate syntax details (flat key:value,
    no nesting/no lists) that belong to hq's own schema, not this plugin's cards."""
    body = _read(LEARNING)
    sec = section(body, r"^### ⭐ confidence on posts", r"^\*\*Posts are immutable")
    assert "no nesting" not in sec
    assert "no lists" not in sec
