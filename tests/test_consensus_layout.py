"""Tests for the `consensus/` per-run workspace entry in output-layout.md (oms R3 #17).

Background: scholar-outline's `--consensus` mode already writes structured handoff
artifacts to `.oms/<slug>/consensus/<stage>-<role>.md` (see
skills/scholar-outline/SKILL.md's Consensus_Handoff section, e.g. `consensus/planner-adr.md`),
but output-layout.md — the layout SSOT for "where does each file go" — never mentioned
`consensus/` at all (0 grep hits). This pins the layout to match the existing writer's
contract: §2 tree gets the entry, §5 cleanup scope gets its fate.

Kept as its own file rather than folding into test_md_stage_layout.py: that file's shape
(a fixed MD_STAGE skill->folder dict + a single anti-misdirection regex) is purpose-built
for the research/methodology/outline `.md`-stage layer bug and doesn't fit a cross-cutting,
`--consensus`-mode-only entry with no source-folder-misdirection failure mode to guard."""
import re
from pathlib import Path

LAYOUT = Path(__file__).parent.parent / "references" / "output-layout.md"


def read() -> str:
    return LAYOUT.read_text(encoding="utf-8")


def section(text: str, start_pattern: str, end_pattern: str) -> str:
    """Extract text between a heading and the next given heading (exclusive of both)."""
    start_m = re.search(start_pattern, text, re.MULTILINE)
    assert start_m, f"heading not found: {start_pattern}"
    rest = text[start_m.end():]
    end_m = re.search(end_pattern, rest, re.MULTILINE)
    return rest[: end_m.start()] if end_m else rest


def test_layout_documents_consensus_dir():
    """§2 tree carries a `consensus/` entry annotated with `--consensus` mode;
    §5 cleanup scope carries a `consensus/` row marked as a cleanup target.

    Discriminance: neither `consensus/` nor a §5 mention exists today (grep-verified 0 hits)."""
    text = read()

    sec2 = section(text, r"^## 2\. Fixed directory structure", r"^## 3\.")
    assert "consensus/" in sec2, "§2 tree missing consensus/ entry"
    assert "--consensus" in sec2, "§2 consensus/ entry missing --consensus mode annotation"

    sec5 = section(text, r"^## 5\. Terminal cleanup", r"^## 6\.")
    consensus_lines = [ln for ln in sec5.splitlines() if "consensus/" in ln]
    assert consensus_lines, "§5 cleanup scope missing consensus/ row"
    assert any(re.search(r"✅|clean|T18", ln, re.IGNORECASE) for ln in consensus_lines), \
        "§5 consensus/ row missing a cleanup-fate keyword"
