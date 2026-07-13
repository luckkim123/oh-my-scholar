"""Tests for the R5 T6 (#33) pre-GATE1 moderator pass.

scholar-pilot Step 4 (outline) gains an unnumbered read-only sub-step (D10 — no
renumbering; the literal `4. **outline` / `━━━ **GATE 1**` lines stay byte-identical)
between the existing mode-branching bullet and the GATE 1 line: dispatch
`scholar-inspector` in its new `mode="moderator"` — a Co-STORM-style anti-groupthink
scan of the proposed outline against the project's research/reading notes, surfacing
retrieved-but-unused evidence + 1-2 pointed questions at the human GATE 1 decision
point. `--skip-moderator` opts out; a dispatch failure fails open (GATE 1 is never
blocked by the moderator — acceptance: GATE 1 semantics stay human-only).

`agents/scholar-inspector.md` gains a matching `mode=moderator` branch alongside the
existing (now-named) `mode=draft-critique` default — Role/Constraints/
Investigation_Protocol/Output_Format/Final_Checklist all gain a moderator slice,
while the pre-existing draft-critique contract text survives verbatim (checked here
as a discriminance lock). Per plan T6, the frontmatter `description:` is updated to
mention both modes but that string is deliberately NOT locked by a test (same
precedent as scholar-researcher/scholar-reviewer's mode-split frontmatter).

House convention (see test_scholar_pilot_skill.py / test_scholar_mock_review_skill.py):
plain asserts via `skill_md()` + `.index()`-scoped windows.
"""
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
PILOT = skill_md("scholar-pilot")
INSPECTOR = (ROOT / "agents" / "scholar-inspector.md").read_text(encoding="utf-8")

GATE1_LINE = (
    "**GATE 1**: outline approval (human) — proceed/revise/abort. "
    "If consensus, present both plan.md+outline"
)


def _step4_section() -> str:
    idx = PILOT.index("4. **outline")
    end = PILOT.index(GATE1_LINE)
    return PILOT[idx:end]


# --------------------------------------------------------- pilot Step 4: GATE 1 untouched
def test_gate1_line_byte_unchanged():
    """Acceptance: GATE 1 semantics/line are untouched by this task (D10)."""
    assert GATE1_LINE in PILOT


def test_step4_top_level_heading_unchanged():
    """D10: no renumbering — step 4/5 headings stay byte-identical."""
    assert "4. **outline**: scholar-outline → section structure·story arc" in PILOT
    assert "5. **draft**: scholar-draft → .tex (drafter single·careful)" in PILOT


# --------------------------------------------------------- pilot Step 4: moderator sub-bullet
def test_moderator_sits_between_outline_mode_branching_and_gate1():
    sec = _step4_section()
    assert "scholar-inspector" in sec
    assert 'mode="moderator"' in sec


def test_moderator_dispatch_inputs():
    sec = _step4_section()
    assert "proposed outline" in sec
    assert ".oms/<slug>/research/*.md" in sec
    assert ".oms/reading/" in sec


def test_moderator_output_shape():
    sec = _step4_section()
    assert re.search(r"retrieved-but-unused evidence", sec, re.I)
    assert re.search(r"1-2 pointed questions", sec, re.I)


def test_moderator_printed_at_gate1_human_decides_no_verdict():
    sec = _step4_section()
    assert "the human decides" in sec
    assert re.search(r"issues no verdict", sec, re.I)


def test_skip_moderator_opt_out_flag():
    sec = _step4_section()
    assert "--skip-moderator" in sec


def test_fail_open_on_dispatch_failure_never_blocks_gate():
    sec = _step4_section()
    assert re.search(r"dispatch failure", sec, re.I)
    assert re.search(r"fail-open", sec, re.I)
    assert re.search(r"never blocks the gate", sec, re.I)


# --------------------------------------------------------- footprint discriminance
def test_moderator_footprint_limited_to_pilot_agent_and_tests():
    """Acceptance-adjacent: `mode="moderator"` / `mode=moderator` only appear where T6
    actually touches — pilot body, inspector agent, this test, and planning docs."""
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        parts = rel.parts
        if parts[0] in (".git", "node_modules"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        if "mode=moderator" in text or 'mode="moderator"' in text:
            hits.append(str(rel))
    allowed_prefixes = (
        "agents/scholar-inspector.md",
        "skill-bodies/scholar-pilot/SKILL.md",
        "tests/",
        "docs/",  # planning docs — not shipped plugin surface
        "CHANGELOG.md",  # R5 T9: release notes document the shipped feature
        "README.md",  # R5 T9: agents table + Status paragraph name mode=moderator
    )
    stray = [h for h in hits if not h.startswith(allowed_prefixes)]
    assert not stray, f"mode=moderator leaked outside its allowed footprint: {stray}"


# =========================================================== agents/scholar-inspector.md: mode split


def test_inspector_role_names_two_modes():
    idx = INSPECTOR.index("<Role>")
    end = INSPECTOR.index("</Role>")
    sec = INSPECTOR[idx:end]
    assert "mode=draft-critique" in sec
    assert "mode=moderator" in sec
    assert re.search(r"invoked in one of two modes", sec, re.I)


def test_draft_critique_mode_default_contract_survives_verbatim():
    """Discriminance: the pre-existing default-mode lens descriptions were not reworded
    when the mode split was introduced (plan T6: 'current contract verbatim')."""
    assert (
        "**logic lens**: contribution-evidence correspondence, structural logic, "
        "baseline comparison, devil's advocate" in INSPECTOR
    )
    assert (
        "**prose lens**: academic prose (differs by Korean/English), overclaiming "
        "discipline, repetition, transitions, sentence length" in INSPECTOR
    )
    # step 0-9 of the default protocol are untouched, just wrapped under a mode heading
    assert "0) **Pre-commitment (*before* reading the body)**" in INSPECTOR
    assert "9) **Tally into the Output Format**" in INSPECTOR


def test_moderator_mode_constraint_no_verdict_no_severity_taxonomy():
    idx = INSPECTOR.index("**mode=moderator scope**")
    window = INSPECTOR[idx: idx + 500]
    assert re.search(r"no verdict", window, re.I)
    assert re.search(r"no severity taxonomy", window, re.I)


def test_moderator_investigation_protocol_subsection_exists():
    assert "### mode=draft-critique (default)" in INSPECTOR
    assert "### mode=moderator" in INSPECTOR
    idx = INSPECTOR.index("### mode=moderator")
    end = INSPECTOR.index("</Investigation_Protocol>")
    sec = INSPECTOR[idx:end]
    assert re.search(r"retrieved-but-unused evidence", sec, re.I)
    assert re.search(r"1-2 pointed questions", sec, re.I)
    assert re.search(r"do not approve or reject it", sec, re.I)


def test_moderator_output_format_subsection_exists():
    idx = INSPECTOR.index("<Output_Format>")
    end = INSPECTOR.index("</Output_Format>")
    sec = INSPECTOR[idx:end]
    assert "### mode=moderator output" in sec
    assert re.search(r"Retrieved-but-unused evidence", sec)
    assert re.search(r"Pointed questions \(1-2\)", sec)
    assert re.search(r"No verdict", sec, re.I)


def test_final_checklist_has_moderator_line():
    idx = INSPECTOR.index("<Final_Checklist>")
    end = INSPECTOR.index("</Final_Checklist>")
    sec = INSPECTOR[idx:end]
    assert re.search(r"mode=moderator", sec)
    assert re.search(r"avoid issuing any verdict", sec, re.I)


def test_inspector_no_project_specific_proper_nouns():
    """Regression guard mirroring test_inspector_writing_lenses.py's ⑥ — new moderator
    content must not leak project-specific placeholders into the distributed agent file."""
    bad = re.compile(r"ADVISOR_X|kimseungmin|PROJ_TITLE_X|SITE_X|ORG_X|ROOM_X", re.I)
    hits = [
        f"  scholar-inspector.md:{i}: {ln.strip()[:80]}"
        for i, ln in enumerate(INSPECTOR.splitlines(), 1)
        if bad.search(ln)
    ]
    assert not hits, "distributed file leaks project-specific proper nouns:\n" + "\n".join(hits)
