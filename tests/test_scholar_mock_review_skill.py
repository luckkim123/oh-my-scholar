"""Tests for scholar-mock-review verdict-history + meta-review mining (R4 #27, Task 5).

Background: scholar-mock-review's read-only rule (skill-bodies/scholar-mock-review/SKILL.md:47)
gains one carve-out — after the AC verdict (Step 3), the orchestrating SKILL flow (the calling
session, never the dispatched read-only scholar-reviewer agent) appends one dated entry to
`.oms/<slug>/reviews-log.md` (create-if-absent, append-only, never touches .tex/.bib). A gated
meta-review sub-step (>= 3 log entries or explicit user request) mines recurring weakness types
and flags "always-moderate" score drift, proposing lens-prompt tweaks at a human gate only —
never auto-applied.

Two other surfaces also say "read-only" about mock-review and are deliberately left untouched
this task (frontmatter frozen; both mean read-only w.r.t. the reviewed draft, which a metadata
log append does not violate): the shim frontmatter (`skills/scholar-mock-review/SKILL.md`) and
`references/rubrics/paper-eval.md:68`. Locked here only as absence-of-change, not new content.

House convention (see test_scholar_pilot_skill.py): plain asserts via `skill_md()` +
`.index()`-scoped windows, one discriminance test proving the original .tex/.bib prohibition
sentence survives verbatim inside the carved-out Execution_Policy bullet (not merely
co-existing nearby text — the exact substring must still be there)."""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
BODY = skill_md("scholar-mock-review")
LAYOUT = (ROOT / "references" / "output-layout.md").read_text(encoding="utf-8")

# The pre-existing Execution_Policy prohibition sentence (must survive verbatim after the edit).
ORIGINAL_READONLY_SENTENCE = (
    "the reviewer does not modify .tex/.bib. Adjudication only. Edits go to scholar-revise."
)


def _execution_policy_section() -> str:
    idx = BODY.index("<Execution_Policy>")
    end = BODY.index("</Execution_Policy>")
    return BODY[idx:end]


def _step4_section() -> str:
    idx = BODY.index("4. **Verdict-history append")
    end = BODY.index("5. **Output the synthesis report")
    return BODY[idx:end]


def _output_section() -> str:
    idx = BODY.index("<Output>")
    end = BODY.index("</Output>")
    return BODY[idx:end]


def _layout_section(start_pattern: str, end_pattern: str) -> str:
    """Extract text between a heading and the next given heading (exclusive of both)."""
    start_m = re.search(start_pattern, LAYOUT, re.MULTILINE)
    assert start_m, f"heading not found: {start_pattern}"
    rest = LAYOUT[start_m.end():]
    end_m = re.search(end_pattern, rest, re.MULTILINE)
    return rest[: end_m.start()] if end_m else rest


# --------------------------------------------------------- Execution_Policy carve-out (:47)
def test_execution_policy_readonly_prohibition_survives_verbatim():
    """Discriminance: the original .tex/.bib prohibition sentence must still be present
    VERBATIM inside the carved-out bullet — the carve-out only adds a clause, it does not
    rewrite the existing prohibition."""
    sec = _execution_policy_section()
    assert ORIGINAL_READONLY_SENTENCE in sec


def test_execution_policy_carve_out_names_reviews_log():
    sec = _execution_policy_section()
    assert "reviews-log.md" in sec
    assert "append-only" in sec
    assert "create-if-absent" in sec


def test_execution_policy_carve_out_writer_identity():
    """The append is performed by the calling session, never the dispatched agent."""
    sec = _execution_policy_section()
    assert "calling session" in sec
    assert "scholar-reviewer" in sec
    assert "disallowedTools" in sec


def test_execution_policy_carve_out_scopes_read_only_to_the_paper():
    sec = _execution_policy_section()
    assert "read-only w.r.t. the paper" in sec
    assert "workbench metadata" in sec


# --------------------------------------------------------- Step 4: verdict-history append
def test_step4_exists_between_step3_and_output_step():
    assert "4. **Verdict-history append" in BODY
    i3 = BODY.index("3. **Area Chair synthesis")
    i4 = BODY.index("4. **Verdict-history append")
    i5 = BODY.index("5. **Output the synthesis report")
    assert i3 < i4 < i5


def test_step4_reviews_log_fields():
    sec = _step4_section()
    for field in ("date", "venue", "lens set", "final verdict", "rebuttal flag"):
        assert field in sec, f"missing field: {field}"
    assert "reviews-log.md" in sec
    assert "append-only" in sec
    assert "create-if-absent" in sec
    assert ".tex" in sec and ".bib" in sec


def test_step4_writer_identity_not_dispatched_agent():
    sec = _step4_section()
    assert "calling session" in sec
    assert "scholar-reviewer" in sec  # names the dispatched agent it is NOT


# --------------------------------------------------------- meta-review sub-step gate
def test_meta_review_gate_at_least_3_entries_or_explicit_request():
    sec = _step4_section()
    assert "at least 3" in sec
    assert "explicitly asks for" in sec


def test_meta_review_always_moderate_drift_flag():
    sec = _step4_section()
    assert "always-moderate" in sec
    assert "borderline" in sec
    assert "calibration" in sec


def test_meta_review_output_is_proposed_and_human_gated_never_auto_applied():
    sec = _step4_section()
    assert "human gate" in sec
    assert "never auto-applied" in sec
    assert "proposed" in sec.lower()


# --------------------------------------------------------- Output section rows
def test_output_section_has_log_confirmation_row():
    sec = _output_section()
    assert "reviews-log.md" in sec
    assert "appended" in sec


def test_output_section_has_meta_review_report_row():
    sec = _output_section()
    assert "Meta-review report" in sec
    assert "at least 3" in sec
    assert "human gate" in sec


# --------------------------------------------------------- frozen surfaces untouched
def test_shim_frontmatter_untouched():
    shim = (ROOT / "skills" / "scholar-mock-review" / "SKILL.md").read_text(encoding="utf-8")
    assert "Read-only." in shim


def test_paper_eval_rubric_line_68_untouched():
    paper_eval = (ROOT / "references" / "rubrics" / "paper-eval.md").read_text(encoding="utf-8")
    assert (
        "**No self-approval**: inspect, verify, and mock-review all cannot evaluate a draft "
        "they themselves wrote. A different lane from the drafter (different agent, read-only)."
    ) in paper_eval


# --------------------------------------------------------- output-layout.md
def test_layout_tree_has_reviews_log_entry():
    sec2 = _layout_section(r"^## 2\. Fixed directory structure", r"^## 3\.")
    assert "reviews-log.md" in sec2
    assert "append-only" in sec2


def test_layout_cleanup_table_has_keep_fate_row():
    sec5 = _layout_section(r"^## 5\. Terminal cleanup", r"^## 6\.")
    reviews_log_lines = [ln for ln in sec5.splitlines() if "reviews-log.md" in ln]
    assert reviews_log_lines, "§5 cleanup table missing reviews-log.md row"
    assert any("KEEP" in ln for ln in reviews_log_lines)


def test_layout_checklist_has_mock_review_row():
    sec6 = _layout_section(r"^## 6\. Implementation checklist", r"\Z")
    assert "scholar-mock-review" in sec6
    assert "reviews-log.md" in sec6
    assert "calling session" in sec6


def test_layout_wiki_block_untouched_by_this_task():
    """Task 3's territory — this task must not touch the .oms/wiki/ tree block."""
    idx = LAYOUT.index(".oms/wiki/")
    wiki_block = LAYOUT[idx: idx + 400]
    assert "reviews-log.md" not in wiki_block
