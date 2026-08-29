"""Tests for the light-channel evidence signal at scholar-pilot Step 10 (R4 #24, Task 4;
rewired r7 2026-08-30 for the wiki -> post-store form change).

Background: scholar-pilot Step 10 is the ONE place post-capture happens (formerly "wiki
capture" — the wiki page-tree form is retired, user decision: "wiki 는 아예 없애는 걸로.
Wiki 폴더 안만들게"). This task's original evidence-discipline bullet survives the form
change unchanged in spirit — a posted entry with no internal pointer (`<slug> §…`) or
verbatim quote is still posted, but at `--confidence low` with an `evidence: none`
marker, and evidence-less re-observation never raises confidence. What changed
mechanically: `hq` now owns the post frontmatter shape directly (no manual schema to
compose, so the old "points at Frontmatter standard" pointer has no target — that
section was retired with the page-tree form), and the write verb is `hq post` rather
than an in-place file append.
`references/knowledge/README.md`'s evidence-recommendation block gains a short,
cross-referencing addition — SSOT for the append-time procedure stays with the pilot
skill, not restated there.

House convention (see test_state_schema_docs.py, test_wiki_spec_docs.py): plain asserts
via `skill_md("scholar-pilot")` + `.index()`-scoped windows, one discriminance test
proving the old `:61` sentence is actually gone (not just co-existing with new wording).
"""
import re
from pathlib import Path

from conftest import layout_section, skill_md

ROOT = Path(__file__).parent.parent
README = (ROOT / "references" / "knowledge" / "README.md").read_text(encoding="utf-8")
LAYOUT = (ROOT / "references" / "output-layout.md").read_text(encoding="utf-8")
PILOT = skill_md("scholar-pilot")

OLD_APPEND_SENTENCE = "A new category file is free-form .md (no machine schema)."


def _step10_section() -> str:
    idx = PILOT.index("10. **post capture")
    end = PILOT.index("11. **terminal cleanup")
    return PILOT[idx:end]


def _readme_evidence_section() -> str:
    idx = README.index("### ⭐ A post holds *conclusion + evidence* together")
    end = README.index("Example (conclusion + evidence together")
    return README[idx:end]


# --------------------------------------------------------- pilot Step 10: :61 replacement (discriminance)
def test_step10_old_sentence_replaced():
    """Discriminance lock: the OLD unscoped sentence must be gone verbatim, and the
    '(no machine schema)' token must not survive anywhere in the skill body."""
    assert OLD_APPEND_SENTENCE not in PILOT, "old :61 sentence must be replaced"
    assert "(no machine schema)" not in PILOT, "old token must be fully gone"


def test_step10_new_post_gets_hq_owned_frontmatter():
    """r7: hq owns the post frontmatter shape directly — there is no more local
    'Frontmatter standard' section to point at (retired with the page-tree form)."""
    sec = _step10_section()
    assert re.search(r"`?hq`?\s+owns the frontmatter shape", sec, re.I), \
        "new posts must be created through hq, which owns the frontmatter shape"
    assert "references/knowledge/README.md" in sec
    assert "Frontmatter standard" not in sec


# --------------------------------------------------------- pilot Step 10: new evidence-signal bullet
def test_step10_evidence_signal_bullet_exists():
    sec = _step10_section()
    assert re.search(r"internal pointer", sec, re.I)
    assert re.search(r"verbatim quote", sec, re.I)


def test_step10_pointerless_entry_still_posted_not_gated():
    sec = _step10_section()
    assert re.search(r"still posted", sec, re.I)
    assert re.search(r"no reject gate|not a reject gate", sec, re.I)


def test_step10_forces_confidence_low_with_evidence_none_marker():
    sec = _step10_section()
    assert "--confidence low" in sec
    assert "(evidence: none — add a pointer before confidence can rise)" in sec


def test_step10_evidence_less_reobservation_never_raises_confidence():
    sec = _step10_section()
    assert re.search(r"evidence-less re-observation never raises confidence", sec, re.I)


# --------------------------------------------------------- README: cross-reference addition
def test_readme_evidence_block_cross_references_pilot_step10():
    sec = _readme_evidence_section()
    assert "scholar-pilot/SKILL.md" in sec and "Step 10" in sec
    assert "--confidence low" in sec
    assert "evidence: none" in sec


def test_readme_evidence_block_stays_consistent_not_a_reject_gate():
    sec = _readme_evidence_section()
    assert re.search(r"not a reject gate|no reject gate", sec, re.I)
    assert re.search(r"still posted", sec, re.I)


def test_readme_evidence_block_does_not_restate_full_pilot_procedure():
    """SSOT discipline: README cross-references but doesn't restate the pilot's full
    marker sentence — that prose lives at scholar-pilot Step 10."""
    sec = _readme_evidence_section()
    assert "add a pointer before confidence can rise" not in sec


def test_readme_no_automated_compliance_check_claim():
    sec = _readme_evidence_section()
    assert re.search(r"no automated compliance check|prompt-contract", sec, re.I)


# =========================================================== R5 T1 (#30): research-log substrate
#
# scholar-pilot Step 10 gains an additional unnumbered sub-bullet (D10 — no renumbering, both
# `_step10_section()` anchors above stay byte-identical) appending a dated run summary to
# `.oms/<slug>/research-log.md`. Contract lives in `references/output-layout.md` §2.4 (new
# subsection, mirrors §2.2/§2.3), plus footprint in §2 tree, §2.1 invariance bullet, §5 KEEP-fate
# table row, and §6 checklist. Secondary-memo discipline (invariant 2): never a `.bib` source.

def test_step10_research_log_entry_exists():
    sec = _step10_section()
    assert "research-log.md" in sec
    assert "create-if-absent" in sec
    assert re.search(r"##\s*YYYY-MM-DD\s*—\s*pilot", sec)
    assert re.search(r"tried\s*/\s*decided\s*/\s*dropped", sec)


def test_step10_research_log_no_log_opt_out_mirrors_no_post():
    sec = _step10_section()
    assert "--no-log" in sec
    assert "--no-post" in sec  # both opt-outs coexist in the same step


def test_step10_research_log_writer_identity_calling_session():
    sec = _step10_section()
    assert "calling session" in sec
    assert re.search(r"never a dispatched agent", sec, re.I)


def test_step10_research_log_secondary_memo_never_bib_source():
    sec = _step10_section()
    assert re.search(r"never a `?\.bib` source", sec)
    assert re.search(r"citation authority", sec, re.I)
    assert "invariant 2" in sec


# --------------------------------------------------------- output-layout.md §2 tree
def test_layout_tree_has_research_log_entry():
    sec2 = layout_section(LAYOUT, r"^## 2\. Fixed directory structure", r"^## 3\.")
    assert "research-log.md" in sec2
    assert "append-only" in sec2
    assert "create-if-absent" in sec2


# --------------------------------------------------------- output-layout.md §2.1 invariance
def test_layout_invariance_mentions_research_log_alongside_reviews_log():
    sec2 = layout_section(LAYOUT, r"^## 2\. Fixed directory structure", r"^## 3\.")
    inv = layout_section(sec2, r"### 2\.1 Invariance rules", r"### 2\.2")
    assert "research-log.md" in inv
    assert "reviews-log.md" in inv
    assert "KEEP" in inv


# --------------------------------------------------------- output-layout.md §2.4 (new subsection)
def test_layout_has_research_log_entry_format_subsection():
    sec2 = layout_section(LAYOUT, r"^## 2\. Fixed directory structure", r"^## 3\.")
    idx = sec2.index("### 2.4 research-log entry format")
    sub = sec2[idx:]
    assert re.search(r"##\s*YYYY-MM-DD\s*—\s*<context:\s*pilot\|discuss\|read\|manual>", sub)
    assert "scholar-pilot" in sub
    assert re.search(r"never a `?\.bib` source", sub)


# --------------------------------------------------------- output-layout.md §5 KEEP fate
def test_layout_cleanup_table_has_research_log_keep_row():
    sec5 = layout_section(LAYOUT, r"^## 5\. Terminal cleanup", r"^## 6\.")
    research_log_lines = [ln for ln in sec5.splitlines() if "research-log.md" in ln]
    assert research_log_lines, "§5 cleanup table missing research-log.md row"
    assert any("KEEP" in ln for ln in research_log_lines)


# --------------------------------------------------------- output-layout.md §6 checklist
def test_layout_checklist_has_research_log_row():
    sec6 = layout_section(LAYOUT, r"^## 6\. Implementation checklist", r"\Z")
    assert "scholar-pilot" in sec6
    assert "research-log.md" in sec6
    assert "calling session" in sec6
    assert "--no-log" in sec6


# --------------------------------------------------------- footprint discriminance (plan Acceptance)
def test_research_log_footprint_limited_to_output_layout_pilot_and_tests():
    """Acceptance: `git grep research-log` hits output-layout, pilot body, tests only."""
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        parts = rel.parts
        if parts[0] in (".git", "node_modules", ".claude"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        if "research-log" in text:
            hits.append(str(rel))
    allowed_prefixes = (
        "references/output-layout.md",
        "skill-bodies/scholar-pilot/SKILL.md",
        "skill-bodies/scholar-read/SKILL.md",  # R5 T2 (#28): research-log append, context `read`
        "skill-bodies/scholar-discuss/SKILL.md",  # R5 T3 (#29): research-log append, context `discuss`
        "tests/",
        "docs/",  # planning docs (roadmap, execution plan) — not shipped plugin surface
        "CHANGELOG.md",  # R5 T9: release notes document the shipped feature
        "README.md",  # R5 T9: Status paragraph names the research-log.md substrate
    )
    stray = [h for h in hits if not h.startswith(allowed_prefixes)]
    assert not stray, f"research-log leaked outside its allowed footprint: {stray}"
