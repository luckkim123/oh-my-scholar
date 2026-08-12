"""Tests for the GATE 1 outline view (scripts/oms_outline_view.py).

House convention: plain asserts, stdlib only, and the importlib
spec_from_file_location idiom for loading a script under test (matching
test_oms_doctor.py and test_version_sync.py) rather than sys.path surgery.

COMPLETE below is a healthy outline that must produce zero flags; every defect
test is COMPLETE with one targeted mutation, so the delta under test is visible
in the test body.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "oms_outline_view.py"
_spec = importlib.util.spec_from_file_location("oms_outline_view", SCRIPT)
ov = importlib.util.module_from_spec(_spec)
# dataclasses resolves string-form annotations (from __future__ import
# annotations) by looking up cls.__module__ in sys.modules; register before
# exec so that lookup doesn't AttributeError on Python 3.12.
sys.modules["oms_outline_view"] = ov
_spec.loader.exec_module(ov)

COMPLETE = """## Outline — Entropy-Map Seabed Scanning

### Venue constraints
- venue: IROS  page_limit: 6 pages → word budget total: 3000 words
- required sections: Introduction, Related Work, Method, Experiments, Conclusion

### Section tree

#### §1. Introduction — [word budget: 600 words]
- **Purpose**: Frame the seabed-coverage problem and state the gap.
- **Core message**: Uniform lawnmower scanning wastes time on low-information seabed.
- **Proposition to argue**: Information-guided scanning beats uniform coverage under a fixed time budget.
- **Dependent citations**: `galceran2013survey`, `bourgault2002information`

#### §2. Related Work — [word budget: 500 words]
- **Purpose**: Position against coverage planning and active perception.
- **Core message**: Neither line covers entropy-driven seabed scanning with imaging sonar.
- **Proposition to argue**: The two adjacent literatures leave the sonar-specific case open.
- **Dependent citations**: `galceran2013survey`, `stachniss2005information`

#### §3. Method — [word budget: 1100 words]
- **Purpose**: Define the entropy map and the scan policy over it.
- **Core message**: The entropy map turns sonar returns into a scan-priority field.
- **Proposition to argue**: Entropy over the occupancy posterior is the right scan-priority signal.
- **Dependent citations**: `bourgault2002information`

#### §4. Experiments — [word budget: 600 words]
- **Purpose**: Show coverage-per-time against the lawnmower baseline.
- **Core message**: Entropy-guided scanning reaches the same map quality in less time.
- **Proposition to argue**: The gain holds across three seabed textures, not one tuned case.
- **Dependent citations**: `galceran2013survey`

#### §5. Conclusion — [word budget: 200 words]
- **Purpose**: State what was shown and the remaining limit.
- **Core message**: Entropy guidance pays off; the sonar noise model is the open limit.
- **Proposition to argue**: The result generalizes to any range sensor with an occupancy posterior.
- **Dependent citations**: `bourgault2002information`

### Story Arc — necessity chain
§1 Introduction
  → establishes: the coverage-time problem and the gap
  → why this is needed: §2 must show the gap is not already closed
§2 Related Work
  → establishes: neither adjacent literature covers this case
  → why this is needed: §3 can only claim novelty once the gap stands
§3 Method
  → establishes: the entropy map and the policy over it
  → why this is needed: §4 needs a defined method to measure
§4 Experiments
  → establishes: the time gain across three textures
  → why this is needed: §5 can only conclude from measured gain
§5 Conclusion
  → establishes: the generalization claim and its limit
  → paper contribution complete

### Word Budget summary
| Section | Word Budget | Ratio |
| §1 | 600 | 20% |
| §2 | 500 | 17% |
| §3 | 1100 | 37% |
| §4 | 600 | 20% |
| §5 | 200 | 7% |

### Full citation-dependency mapping
| Section | Citation keys |
| §1 | `galceran2013survey`, `bourgault2002information` |
| §2 | `galceran2013survey`, `stachniss2005information` |
| §3 | `bourgault2002information` |
| §4 | `galceran2013survey` |
| §5 | `bourgault2002information` |

**Unverified citation requests**: none
"""


def test_parses_every_section_with_every_field():
    outline = ov.parse_outline(COMPLETE)
    assert [s.number for s in outline.sections] == ["1", "2", "3", "4", "5"]
    third = outline.sections[2]
    assert third.name == "Method"
    assert third.word_budget == 1100
    assert third.purpose == "Define the entropy map and the scan policy over it."
    assert third.core_message == "The entropy map turns sonar returns into a scan-priority field."
    assert third.proposition.startswith("Entropy over the occupancy posterior")
    assert third.citations == ["bourgault2002information"]
    assert third.recheck is None


def test_missing_field_parses_as_none_not_an_error():
    text = COMPLETE.replace(
        "- **Core message**: The entropy map turns sonar returns into a scan-priority field.\n", ""
    )
    outline = ov.parse_outline(text)
    third = outline.sections[2]
    assert third.core_message is None
    assert third.purpose is not None


def test_parses_venue_constraints():
    outline = ov.parse_outline(COMPLETE)
    assert outline.venue == "IROS"
    assert outline.page_limit == 6
    assert outline.budget_total == 3000


def test_parses_the_necessity_chain_and_marks_the_terminal_link():
    outline = ov.parse_outline(COMPLETE)
    assert [c.number for c in outline.chain] == ["1", "2", "3", "4", "5"]
    first = outline.chain[0]
    assert first.establishes == "the coverage-time problem and the gap"
    assert first.why_needed == "§2 must show the gap is not already closed"
    assert first.terminal is False
    last = outline.chain[-1]
    assert last.terminal is True
    assert last.why_needed is None


def test_parses_the_citation_mapping_table():
    outline = ov.parse_outline(COMPLETE)
    assert outline.mapping == {
        "1": ["galceran2013survey", "bourgault2002information"],
        "2": ["galceran2013survey", "stachniss2005information"],
        "3": ["bourgault2002information"],
        "4": ["galceran2013survey"],
        "5": ["bourgault2002information"],
    }


def test_absent_mapping_block_parses_as_none_not_empty():
    text = COMPLETE.split("### Full citation-dependency mapping")[0]
    outline = ov.parse_outline(text)
    assert outline.mapping is None


def test_null_page_limit_parses_as_none():
    text = COMPLETE.replace(
        "- venue: IROS  page_limit: 6 pages → word budget total: 3000 words",
        "- venue: PhD Thesis  page_limit: null → word budget total: null",
    )
    outline = ov.parse_outline(text)
    assert outline.page_limit is None
    assert outline.budget_total is None
    assert outline.venue == "PhD Thesis"


def codes(text):
    return sorted({f.code for f in ov.flags(ov.parse_outline(text))})


def test_healthy_outline_produces_zero_flags():
    assert ov.flags(ov.parse_outline(COMPLETE)) == []


def test_missing_field_flag():
    text = COMPLETE.replace(
        "- **Core message**: The entropy map turns sonar returns into a scan-priority field.\n", ""
    )
    assert codes(text) == ["missing-field"]
    hit = [f for f in ov.flags(ov.parse_outline(text)) if f.code == "missing-field"]
    assert len(hit) == 1
    assert hit[0].section == "3"
    assert "core message" in hit[0].detail.lower()


def test_section_off_chain_flag():
    text = COMPLETE.replace(
        "§4 Experiments\n"
        "  → establishes: the time gain across three textures\n"
        "  → why this is needed: §5 can only conclude from measured gain\n",
        "",
    )
    assert codes(text) == ["section-off-chain"]


def test_blank_link_flag():
    text = COMPLETE.replace(
        "  → why this is needed: §2 must show the gap is not already closed",
        "  → why this is needed:",
    )
    assert codes(text) == ["blank-link"]


def test_recheck_flag():
    text = COMPLETE.replace(
        "- **Proposition to argue**: The result generalizes to any range sensor "
        "with an occupancy posterior.",
        "- **Proposition to argue**: The result generalizes to any range sensor "
        "with an occupancy posterior.\n"
        "- **researcher recheck needed**: sonar noise models",
    )
    assert codes(text) == ["recheck"]


def test_over_budget_flag():
    text = COMPLETE.replace(
        "#### §3. Method — [word budget: 1100 words]",
        "#### §3. Method — [word budget: 1600 words]",
    )
    assert codes(text) == ["over-budget"]


def test_citation_mismatch_flag():
    text = COMPLETE.replace(
        "| §4 | `galceran2013survey` |",
        "| §4 | `galceran2013survey`, `stachniss2005information` |",
    )
    assert codes(text) == ["citation-mismatch"]


def test_chain_off_tree_flag_when_a_heading_loses_its_section_sign():
    text = COMPLETE.replace(
        "#### §1. Introduction — [word budget: 600 words]",
        "#### 1. Introduction — [word budget: 600 words]",
    )
    outline = ov.parse_outline(text)
    assert [s.number for s in outline.sections] == ["2", "3", "4", "5"]
    assert codes(text) == ["chain-off-tree"]
    hit = [f for f in ov.flags(outline) if f.code == "chain-off-tree"]
    assert len(hit) == 1
    assert hit[0].section == "1"


def test_duplicate_section_flag():
    text = COMPLETE.replace(
        "#### §3. Method — [word budget: 1100 words]\n"
        "- **Purpose**: Define the entropy map and the scan policy over it.\n"
        "- **Core message**: The entropy map turns sonar returns into a scan-priority field.\n"
        "- **Proposition to argue**: Entropy over the occupancy posterior is the right "
        "scan-priority signal.\n"
        "- **Dependent citations**: `bourgault2002information`\n",
        "#### §3. Method — [word budget: 1100 words]\n"
        "- **Purpose**: Define the entropy map and the scan policy over it.\n"
        "- **Core message**: The entropy map turns sonar returns into a scan-priority field.\n"
        "- **Proposition to argue**: Entropy over the occupancy posterior is the right "
        "scan-priority signal.\n"
        "- **Dependent citations**: `bourgault2002information`\n\n"
        "#### §3. Method — [word budget: 1100 words]\n"
        "- **Purpose**: Define the entropy map and the scan policy over it.\n"
        "- **Core message**: The entropy map turns sonar returns into a scan-priority field.\n"
        "- **Proposition to argue**: Entropy over the occupancy posterior is the right "
        "scan-priority signal.\n"
        "- **Dependent citations**: `bourgault2002information`\n",
    )
    # The duplicated section also duplicates its word budget into the total, so
    # over-budget is a correct second flag here, not a leak from this mutation.
    assert codes(text) == ["duplicate-section", "over-budget"]


def test_chain_written_with_trailing_periods_produces_no_false_section_off_chain():
    text = COMPLETE
    for n, name in (
        (1, "Introduction"),
        (2, "Related Work"),
        (3, "Method"),
        (4, "Experiments"),
        (5, "Conclusion"),
    ):
        text = text.replace(f"§{n} {name}\n", f"§{n}. {name}\n")
    assert codes(text) == []


def test_over_budget_detail_is_visible_in_the_rendered_html():
    text = COMPLETE.replace(
        "#### §3. Method — [word budget: 1100 words]",
        "#### §3. Method — [word budget: 1600 words]",
    )
    outline = ov.parse_outline(text)
    html = ov.render_html(outline, ov.flags(outline))
    assert "section budgets sum to 3500 words against a stated total of 3000" in html


def test_no_sections_flag_on_garbage_input():
    result = ov.flags(ov.parse_outline("완전히 관계없는 텍스트\n\n# nope\n"))
    assert [f.code for f in result] == ["no-sections"]


def test_terminal_chain_entry_does_not_trip_blank_link():
    outline = ov.parse_outline(COMPLETE)
    assert outline.chain[-1].why_needed is None
    assert not [f for f in ov.flags(outline) if f.code == "blank-link"]


def test_null_page_limit_skips_the_budget_check():
    text = COMPLETE.replace(
        "- venue: IROS  page_limit: 6 pages → word budget total: 3000 words",
        "- venue: PhD Thesis  page_limit: null → word budget total: null",
    ).replace(
        "#### §3. Method — [word budget: 1100 words]",
        "#### §3. Method — [word budget: 9900 words]",
    )
    assert codes(text) == []


def test_absent_mapping_block_skips_the_citation_check():
    text = COMPLETE.split("### Full citation-dependency mapping")[0]
    assert codes(text) == []


def test_render_is_self_contained():
    html = ov.render_html(ov.parse_outline(COMPLETE), [])
    assert "<script src=" not in html
    assert "http://" not in html
    assert "https://" not in html
    assert "@import" not in html


def test_render_shows_every_section_and_the_chain_text():
    html = ov.render_html(ov.parse_outline(COMPLETE), [])
    for name in ("Introduction", "Related Work", "Method", "Experiments", "Conclusion"):
        assert name in html
    assert "§2 must show the gap is not already closed" in html


def test_render_escapes_content():
    text = COMPLETE.replace("#### §3. Method —", "#### §3. <script>alert(1)</script> —")
    html = ov.render_html(ov.parse_outline(text), [])
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_render_reports_the_flag_count_and_each_code():
    text = COMPLETE.replace(
        "- **Core message**: The entropy map turns sonar returns into a scan-priority field.\n", ""
    )
    outline = ov.parse_outline(text)
    html = ov.render_html(outline, ov.flags(outline))
    assert "missing-field" in html
    assert "structural gap" in html


def test_render_defines_all_three_theme_states():
    html = ov.render_html(ov.parse_outline(COMPLETE), [])
    assert "prefers-color-scheme: dark" in html or "prefers-color-scheme:dark" in html
    assert ':root:not([data-theme="light"])' in html
    assert ':root[data-theme="dark"]' in html


def test_cli_writes_the_sheet_beside_the_input(tmp_path, capsys):
    src = tmp_path / "outline.md"
    src.write_text(COMPLETE, encoding="utf-8")
    rc = ov.main([str(src)])
    out = tmp_path / "gate1.html"
    assert rc == 0
    assert out.exists()
    assert "Entropy-Map Seabed Scanning" in out.read_text(encoding="utf-8")
    assert "GAPS=0" in capsys.readouterr().out


def test_cli_honours_an_explicit_output_path(tmp_path):
    src = tmp_path / "outline.md"
    src.write_text(COMPLETE, encoding="utf-8")
    dest = tmp_path / "sub" / "sheet.html"
    assert ov.main([str(src), "-o", str(dest)]) == 0
    assert dest.exists()


def test_cli_returns_nonzero_when_gaps_are_found(tmp_path):
    src = tmp_path / "outline.md"
    src.write_text(
        COMPLETE.replace(
            "- **Core message**: The entropy map turns sonar returns into a "
            "scan-priority field.\n",
            "",
        ),
        encoding="utf-8",
    )
    assert ov.main([str(src)]) == 1
    assert (tmp_path / "gate1.html").exists()


def test_cli_raises_only_on_a_missing_input_file(tmp_path):
    import pytest

    with pytest.raises(SystemExit):
        ov.main([str(tmp_path / "nope.md")])


def test_skill_wires_the_view_into_gate_1():
    from conftest import skill_md

    text = skill_md("scholar-outline")
    gate = text.index("GATE 1 — request human approval")
    window = text[gate : gate + 1800]
    assert "oms_outline_view.py" in window
    assert "gate1.html" in window
    assert "proceed" in window and "revise" in window and "abort" in window


def test_output_layout_admits_the_generated_sheet():
    layout = (ROOT / "references" / "output-layout.md").read_text(encoding="utf-8")
    outline_block = layout[layout.index("  outline/") :][:500]
    assert "gate1.html" in outline_block
