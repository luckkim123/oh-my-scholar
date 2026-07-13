"""R2 #6/#11/#12 — the state schema and notepad tiers are documented in the
layout SSOT and wired into scholar-pilot (literal locks, repo idiom).

R2 #11+#12 (Task 6): abort/interrupt spec on the pilot SKILL + the notepad
3-tier convention on the layout SSOT."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
LAYOUT = (ROOT / "references" / "output-layout.md").read_text(encoding="utf-8")
PILOT = (ROOT / "skills" / "scholar-pilot" / "SKILL.md").read_text(encoding="utf-8")


def test_layout_documents_pilot_state():
    assert "pilot-<slug>.json" in LAYOUT
    assert re.search(r"gate_status", LAYOUT) and re.search(r"open_fail_ids", LAYOUT)
    assert re.search(r"oms_state\.py", LAYOUT), "state files are written only via the CLI"


def test_layout_documents_revise_marker():
    assert "revise-<slug>.json" in LAYOUT  # written by T2; documented together in §2.2


def test_pilot_writes_state_at_boundaries():
    assert "oms_state.py" in PILOT
    assert re.search(r"(every|each) stage boundary", PILOT, re.I)


def test_pilot_from_reads_state():
    idx = PILOT.index("--from")
    assert re.search(r"oms_state\.py read|pilot-<slug>\.json", PILOT[idx:idx + 600]), \
        "--from must read the recorded state, not just advertise"


def test_pilot_has_interruption_and_resume_section():
    assert "Interruption_And_Resume" in PILOT
    idx = PILOT.index("Interruption_And_Resume")
    section = PILOT[idx:idx + 2500]
    assert re.search(r"resume", section, re.I) and re.search(r"discard", section, re.I), \
        "must offer a resume/discard choice, not just describe state"
    assert re.search(r"\babort\b", section) and re.search(r"terminal", section, re.I), \
        "abort must be documented as terminal"
    assert re.search(r"\bstale\b", section, re.I)
    assert "14 days" in section


def test_layout_documents_notepad_tiers():
    assert ".oms/notepad.md" in LAYOUT
    idx = LAYOUT.index("notepad tiers")
    section = LAYOUT[idx:idx + 2000]
    for tier in ("Priority Context", "Working Notes", "Manual"):
        assert tier in section, f"missing tier: {tier}"
    assert "replace-on-write" in section
    assert re.search(r"7[\s-]?day", section, re.I)
    assert re.search(r"\bnever\b", section, re.I), "Manual must be documented as never auto-written/pruned"


def test_pilot_execution_policy_points_to_layout_tiers():
    idx = PILOT.index("Priority Context")
    assert re.search(r"references/output-layout\.md §2\.3", PILOT[idx:idx + 600])
    # Task 6: assert that pilot SKILL explicitly instructs the prune duty
    assert re.search(r"prune.{0,120}Working Notes|Working Notes.{0,120}prune", PILOT, re.I | re.S), \
        "pilot SKILL must contain an imperative to prune Working Notes (not just a citation)"
    assert re.search(r"7[\s-]?day", PILOT, re.I), \
        "pilot SKILL must mention the 7-day TTL (not only in the layout file)"
