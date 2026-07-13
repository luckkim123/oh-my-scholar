"""R2 #6/#11/#12 — the state schema and notepad tiers are documented in the
layout SSOT and wired into scholar-pilot (literal locks, repo idiom)."""
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
