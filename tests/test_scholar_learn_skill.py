"""Tests for the wiki -> reference-card anchoring verb in scholar-learn (R4 #26, Task 6).

Background: scholar-learn's <Steps> gains a new Step 6 (after the existing Step 5 commit
step; the old Step 6 "Follow-up guidance" renumbers to Step 7) — a third lane, separate
from both venue-default promotion (Steps 1-5, learned.md -> venues.md) and the
local->global wiki elevation documented in Execution_Policy. The new verb repeats the
2026-06 hand-done pattern (an external survey anchored into 5 oms files) as a repeatable
step: trigger on a mature *global*-wiki cluster (paper-agnostic, harness-relevant,
confidence: high, sightings >= 3, or explicit user request), propose a references/ card
draft or update that anchors (wiki source pointers + file:line anchors into oms surfaces)
rather than copying wholesale, write only under a dev-mode guard (the plugin root's
`.git` must EXIST as file-or-directory, explicitly not `isdir` -- a linked git worktree's
`.git` is a plain gitfile), always pass a mandatory human gate, and permanently exclude
citation/.bib content (same invariant as venue-default promotion, learning-protocol.md
§6.F).

`references/learning-protocol.md` gains one non-restating pointer line in the heavy-channel
section (§1) naming this as a third lane and pointing at scholar-learn's Step 6 for the
procedure -- SSOT stays in the skill body.

House convention (see test_scholar_mock_review_skill.py, test_wiki_spec_docs.py): plain
asserts via `skill_md()` + `.index()`-scoped windows for the skill body, a `section()`
regex helper for learning-protocol.md, and discriminance tests proving the locks are not
vacuous (old Step 6 heading is actually gone / a directory-only regression would actually
fail the guard lock).
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
BODY = skill_md("scholar-learn")
LEARNING = (ROOT / "references" / "learning-protocol.md").read_text(encoding="utf-8")

STEP6_HEADING = "6. **Wiki → reference-card anchoring"
STEP7_HEADING = "7. **Follow-up guidance"
OLD_STEP6_HEADING = "6. **Follow-up guidance"

GIT_GUARD_PHRASE = "existence check (file or directory), explicitly not `isdir`"


def _step6_section() -> str:
    idx = BODY.index(STEP6_HEADING)
    end = BODY.index(STEP7_HEADING)
    return BODY[idx:end]


def _steps_section() -> str:
    idx = BODY.index("<Steps>")
    end = BODY.index("</Steps>")
    return BODY[idx:end]


def _heavy_channel_section() -> str:
    idx = LEARNING.index("### Heavy channel")
    end = LEARNING.index("### Light channel")
    return LEARNING[idx:end]


# --------------------------------------------------------- step renumbering (Step 0/discriminance)
def test_step6_exists_between_step5_and_step7():
    steps = _steps_section()
    i5 = steps.index("5. **Commit approved items")
    i6 = steps.index(STEP6_HEADING)
    i7 = steps.index(STEP7_HEADING)
    assert i5 < i6 < i7


def test_old_step6_heading_actually_renumbered_not_just_coexisting():
    """Discriminance: the OLD '6. **Follow-up guidance' heading must be gone (renumbered
    to 7), not merely co-existing alongside a new step 6."""
    assert OLD_STEP6_HEADING not in BODY
    assert STEP7_HEADING in BODY


def test_followup_guidance_content_preserved_under_new_number():
    """The old Step 6 body content survives verbatim under its new Step 7 number."""
    idx = BODY.index(STEP7_HEADING)
    end = BODY.index("</Steps>")
    sec = BODY[idx:end]
    assert "scholar-outline will lay down the new defaults" in sec
    assert "H10" in sec


# --------------------------------------------------------- Step 6: trigger
def test_step6_trigger_is_global_wiki_cluster():
    sec = _step6_section()
    assert "global" in sec.lower()
    assert "paper-agnostic" in sec
    assert "harness-relevant" in sec


def test_step6_trigger_confidence_and_sightings_bar():
    sec = _step6_section()
    assert "confidence: high" in sec
    assert "sightings ≥ 3" in sec


def test_step6_trigger_user_requested_bypass():
    sec = _step6_section()
    assert re.search(r"user explicitly requests", sec, re.I)


# --------------------------------------------------------- Step 6: verb
def test_step6_verb_targets_references_card():
    sec = _step6_section()
    assert "references/" in sec
    assert "card" in sec


def test_step6_verb_anchors_never_copies_wholesale():
    sec = _step6_section()
    assert "anchors, never copies wholesale" in sec


def test_step6_verb_uses_file_line_anchors():
    sec = _step6_section()
    assert "file:line" in sec


def test_step6_precedent_named():
    sec = _step6_section()
    assert "2026-06" in sec


# --------------------------------------------------------- Step 6: dev-mode guard (+ discriminance)
def test_step6_git_guard_existence_not_isdir():
    sec = _step6_section()
    assert GIT_GUARD_PHRASE in sec


def test_step6_git_guard_covers_worktree_gitfile_form():
    sec = _step6_section()
    assert "worktree" in sec.lower()
    assert "gitfile" in sec.lower()
    assert "gitdir" in sec


def test_step6_git_guard_absent_falls_back_to_text_only():
    sec = _step6_section()
    assert re.search(r"absent in any form", sec)
    assert "emit the proposed card as text only" in sec
    assert "never write" in sec


def test_step6_git_guard_discriminance_directory_only_regression_would_fail_lock():
    """Discriminance: prove the lock actually distinguishes file-or-directory wording
    from a plausible regression (dropping 'file or', leaving directory-only). If the
    body had regressed to directory-only phrasing, GIT_GUARD_PHRASE would no longer be
    found -- simulate that regression and confirm the token disappears."""
    sec = _step6_section()
    assert GIT_GUARD_PHRASE in sec
    regressed = sec.replace("file or directory", "directory")
    assert GIT_GUARD_PHRASE not in regressed


# --------------------------------------------------------- Step 6: human gate
def test_step6_human_gate_mandatory_no_exception():
    sec = _step6_section()
    assert "human gate" in sec
    assert re.search(r"no matter how high confidence", sec, re.I)


# --------------------------------------------------------- Step 6: citation exclusion
def test_step6_citation_bib_permanently_excluded():
    sec = _step6_section()
    assert "Citation/.bib permanently excluded" in sec
    assert "§6.F" in sec


# --------------------------------------------------------- learning-protocol.md: pointer only (heavy channel)
def test_learning_protocol_heavy_channel_points_to_scholar_learn_step6():
    sec = _heavy_channel_section()
    assert "scholar-learn" in sec
    assert "Step 6" in sec
    assert re.search(r"third lane", sec, re.I)


def test_learning_protocol_pointer_distinguishes_from_local_to_global_elevation():
    sec = _heavy_channel_section()
    assert re.search(r"local.{0,5}global", sec, re.I)


def test_learning_protocol_does_not_restate_step6_guard_details():
    """SSOT discipline: the pointer line in learning-protocol.md must not duplicate the
    dev-mode guard mechanics (isdir/gitfile/gitdir) that live only in scholar-learn's
    Step 6 -- point, don't restate."""
    sec = _heavy_channel_section()
    assert "isdir" not in sec
    assert "gitdir" not in sec


# --------------------------------------------------------- frozen surfaces untouched
def test_shim_untouched_frontmatter_description_intact():
    shim = (ROOT / "skills" / "scholar-learn" / "SKILL.md").read_text(encoding="utf-8")
    assert "No automatic promotion" in shim
    assert "anchoring" not in shim
