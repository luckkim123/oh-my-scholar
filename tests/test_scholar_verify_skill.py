"""Tests for R5 #34 — preflight-style categorized verify report.

scholar-verifier's Output_Format is regrouped so the same per-item PASS/FAIL/WARN
rows read as a submission checklist under 5 fixed category headers: language /
citations / formatting-metadata / tables-figures / declarations. Each header
carries a worst-severity roll-up. This is a presentation-only regrouping — no
pre-existing check is added, removed, or reweighted — except one genuinely new
check: blind-review anonymization (WARN, double-blind venues only, never
auto-edits), which lands under `declarations`.

House convention (see test_scholar_mock_review_skill.py): plain asserts against
the raw agent/skill text, with `.index()`-scoped windows where a check needs to
be pinned to a specific section rather than merely present anywhere in the file.
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-verifier.md").read_text(encoding="utf-8")
SKILL = skill_md("scholar-verify")

CATEGORIES = ("language", "citations", "formatting-metadata", "tables-figures", "declarations")

# The 15 pre-existing Output_Format item names (verbatim substrings), locked so
# the regrouping can't silently drop a check while moving rows into categories.
PRE_EXISTING_ITEMS = (
    "Compilation (latexmk exit 0)",
    "undefined references",
    "undefined citations",
    "leftover placeholders",
    "figure/table reference consistency (\\ref↔\\label)",
    "numerical consistency (body↔table/figure)",
    "terminology/abbreviation consistency",
    "citation consistency (\\cite↔.bib)",
    "claim-faithfulness (citation-misuse)",
    "DOI existence verification",
    "page count (venue limit)",
    "minimum citation count (venue min)",
    "abstract discipline",
    "writing discipline",
    "uncited claims",
)


def _output_format_section() -> str:
    return AGENT[AGENT.index("<Output_Format>"):AGENT.index("</Output_Format>")]


def _per_item_section() -> str:
    sec = _output_format_section()
    idx = sec.index("## Per-Item Results")
    end = sec.index("## FAIL Item Evidence")
    return sec[idx:end]


# --------------------------------------------------------- 5 fixed category headers
def test_agent_has_5_category_headers():
    sec = _per_item_section()
    for cat in CATEGORIES:
        assert f"### {cat}" in sec, f"missing category header: {cat}"


def test_category_headers_appear_in_declared_order():
    sec = _per_item_section()
    positions = [sec.index(f"### {cat}") for cat in CATEGORIES]
    assert positions == sorted(positions)


def test_category_header_shows_worst_severity_rollup():
    sec = _per_item_section()
    # Each category header line names a roll-up placeholder covering FAIL/WARN/PASS.
    for cat in CATEGORIES:
        idx = sec.index(f"### {cat}")
        header_line = sec[idx: sec.index("\n", idx)]
        assert re.search(r"PASS.*WARN.*FAIL|roll-up", header_line, re.I), \
            f"category header for {cat!r} missing a worst-severity roll-up marker"
    assert re.search(r"worst severity", sec, re.I), "no explicit worst-severity roll-up rule stated"
    assert "FAIL > WARN > PASS" in sec


# --------------------------------------------------------- no check added/removed/reweighted
def test_no_check_added_removed_or_reweighted_language_locked():
    sec = _per_item_section()
    assert re.search(r"no check is added, removed, or reweighted", sec, re.I)


def test_all_pre_existing_items_still_present():
    """Acceptance: every pre-existing defect class is still named in the agent —
    the regrouping is complete, nothing silently dropped."""
    sec = _per_item_section()
    missing = [item for item in PRE_EXISTING_ITEMS if item not in sec]
    assert not missing, f"pre-existing item(s) dropped from Output_Format: {missing}"


# --------------------------------------------------------- category → item mapping
def _category_block(name: str) -> str:
    sec = _per_item_section()
    start = sec.index(f"### {name}")
    idx = CATEGORIES.index(name)
    if idx + 1 < len(CATEGORIES):
        end = sec.index(f"### {CATEGORIES[idx + 1]}")
    else:
        end = len(sec)
    return sec[start:end]


def test_language_category_has_its_three_items():
    block = _category_block("language")
    for item in ("terminology/abbreviation consistency", "abstract discipline", "writing discipline"):
        assert item in block


def test_citations_category_has_its_items():
    block = _category_block("citations")
    for item in (
        "citation consistency (\\cite↔.bib)",
        "undefined citations",
        "claim-faithfulness (citation-misuse)",
        "DOI existence verification",
        "uncited claims",
    ):
        assert item in block


def test_formatting_metadata_category_has_its_items():
    block = _category_block("formatting-metadata")
    for item in ("Compilation (latexmk exit 0)", "page count (venue limit)", "minimum citation count (venue min)"):
        assert item in block
    # venue-meta is named here (spec text) but is a calling-skill-level check, not a
    # new row this agent computes itself — documented, not silently omitted.
    assert "venue-meta consistency" in block
    assert "calling-skill-level" in block


def test_tables_figures_category_has_its_items():
    block = _category_block("tables-figures")
    for item in (
        "undefined references",
        "figure/table reference consistency (\\ref↔\\label)",
        "numerical consistency (body↔table/figure)",
    ):
        assert item in block


def test_declarations_category_has_placeholders_and_anonymization():
    block = _category_block("declarations")
    assert "leftover placeholders" in block
    assert "blind-review anonymization" in block
    assert "WARN" in block


# --------------------------------------------------------- new check: blind-review anonymization
def test_anonymization_check_is_warn_not_fail():
    assert re.search(r"[Bb]lind-review anonymization.{0,400}WARN", AGENT, re.S)


def test_anonymization_check_gated_on_double_blind_indication():
    idx = AGENT.index("Blind-review anonymization")
    block = AGENT[idx: idx + 600]
    assert re.search(r"double-blind", block, re.I)
    assert re.search(r"N/A|skip", block, re.I), "no explicit N/A/skip when venue isn't double-blind"
    assert re.search(r"never assume|do not assume", block, re.I)


def test_anonymization_check_never_auto_edits():
    idx = AGENT.index("Blind-review anonymization")
    block = AGENT[idx: idx + 600]
    assert re.search(r"never auto-edit", block, re.I)


def test_anonymization_investigation_protocol_step_present():
    proto = AGENT[AGENT.index("<Investigation_Protocol>"):AGENT.index("</Investigation_Protocol>")]
    assert "Blind-review anonymization check" in proto
    assert re.search(r"\\author|\\\\thanks", proto)
    assert "acknowledg" in proto.lower()


def test_role_bullet_list_mentions_anonymization():
    role = AGENT[AGENT.index("<Role>"):AGENT.index("</Role>")]
    assert "Blind-review anonymization" in role


# --------------------------------------------------------- round-id adjacency regression (T3/R2 lock)
def test_round_id_still_directly_under_target_snapshot():
    """Regression: the categorized-report edit must not disturb the pre-existing
    Target snapshot / Round ID adjacency locked by test_round_id_contract.py."""
    out = _output_format_section()
    assert re.search(r"\*\*Target snapshot\*\*:.*\n\*\*Round ID\*\*:", out)


# --------------------------------------------------------- verify skill body lock
def test_skill_body_names_categorized_report():
    assert re.search(r"[Cc]ategorized report", SKILL)
    for cat in CATEGORIES:
        assert cat in SKILL, f"skill body missing category name: {cat}"


def test_skill_body_names_anonymization_check():
    assert "anonymization" in SKILL.lower()
    assert "WARN" in SKILL
    assert re.search(r"double-blind", SKILL, re.I)
    assert "never auto-edits" in SKILL


def test_skill_body_delegated_item_list_gains_anonymization():
    """Step 2's delegated-instruction item list (the 'defect-class list' handed
    to scholar-verifier) now names the anonymization check alongside the other
    delegated WARN items."""
    idx = SKILL.index("Instruction: output PASS/FAIL")
    block = SKILL[idx: idx + 2500]
    assert "Blind-review anonymization" in block
    assert "Uncited-claim scan" in block, "regression: pre-existing delegated item dropped"


# --------------------------------------------------------- universality guard
def test_no_project_specific_proper_nouns_leaked():
    bad = re.compile(r"ADVISOR_X|kimseungmin|PROJ_TITLE_X|SITE_X|ORG_X|ROOM_X", re.I)
    for path, body in (("scholar-verifier.md", AGENT), ("scholar-verify SKILL.md", SKILL)):
        hits = [ln.strip()[:80] for ln in body.splitlines() if bad.search(ln)]
        assert not hits, f"{path}: project-specific proper noun(s) leaked: {hits}"
