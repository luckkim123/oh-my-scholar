# GATE 1 outline view — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render `.oms/<slug>/outline/outline.md` as a self-contained read-only HTML sheet at GATE 1, flagging seven mechanically-detectable structural gaps, so the human approving a paper structure sees the whole section tree at once.

**Architecture:** One new script, `scripts/oms_outline_view.py`, holding three pure functions (`parse_outline`, `flags`, `render_html`) plus a thin `argparse` CLI. `outline.md` remains the SSOT and is never written by this feature; the HTML is a derived view, regenerated rather than edited. The skill calls the script at GATE 1 and publishes the result opportunistically.

**Tech Stack:** Python 3.11, stdlib only (`re`, `html`, `dataclasses`, `argparse`, `pathlib`). pytest for tests. No new dependency.

**Spec:** `docs/2026-08-12-gate1-outline-view-design.md`

## Global Constraints

- **Stdlib only.** No new entry in `pyproject.toml` dependencies. `ruff` config is `E4,E7,E9,F,I`, line-length 100, target py311 — the new file must pass `ruff check`.
- **`outline.md` is the SSOT.** No task writes, edits, or reorders `outline.md`. The script opens it read-only.
- **Content problems never raise.** Every malformed or missing field resolves to a flag. The single raising condition in the whole feature is a missing input file at the CLI layer.
- **Self-contained HTML.** The rendered page makes no external request: no `<script src=`, no `<link rel="stylesheet" href=`, no remote font, no remote image. All CSS is inline in a `<style>` block.
- **`skill-bodies/` is authoritative, `skills/` is a shim.** Every skill-text change lands in `skill-bodies/scholar-outline/SKILL.md`. Never edit `skills/scholar-outline/SKILL.md`.
- **House test style.** pytest with plain `assert`, stdlib only, no fixtures framework. Skill-text locks read through `conftest.skill_md()`. File name pattern `test_<topic>.py`.
- **Version SSOT** is `.claude-plugin/plugin.json`; four surfaces must agree at release (`scripts/sync_version.py`).

## File Structure

| File | Responsibility |
|:---|:---|
| `scripts/oms_outline_view.py` (new) | Parse outline text into a dataclass model; compute flags over the model; render the model to HTML; expose a CLI. Single file, matching the repo's one-file-per-CLI pattern (`oms_state.py`, `oms_doctor.py`). |
| `tests/test_oms_outline_view.py` (new) | One complete fixture as a module constant, mutated per test. Parser tests, flag tests, exemption tests, render tests, CLI test, skill-text lock. |
| `skill-bodies/scholar-outline/SKILL.md` (modify) | `<Steps>` step 6 gains the render call and the present-or-degrade instruction. |
| `references/output-layout.md` (modify) | Line 98 admits the generated `.html` in `outline/`. |
| `CHANGELOG.md` (modify) | `### Added` under `[Unreleased]`. |
| `.claude-plugin/plugin.json` (modify) | Version bump at release only. |

---

### Task 1: Data model and section-tree parsing

**Files:**
- Create: `scripts/oms_outline_view.py`
- Test: `tests/test_oms_outline_view.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `Section`, `ChainLink`, `Outline`, `Flag` dataclasses and `parse_outline(text: str) -> Outline`. Later tasks fill the remaining `Outline` fields and read `outline.sections`.

`Outline` is defined in full here so later tasks do not redefine it. Tasks 2 and 3 populate and read fields that this task leaves at their empty defaults.

- [ ] **Step 1: Write the fixture and the first failing test**

Create `tests/test_oms_outline_view.py`:

```python
"""Tests for the GATE 1 outline view (scripts/oms_outline_view.py).

House convention: plain asserts, stdlib only. COMPLETE below is a healthy
outline that must produce zero flags; every defect test is COMPLETE with one
targeted mutation, so the delta under test is visible in the test body.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import oms_outline_view as ov  # noqa: E402

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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'oms_outline_view'`

- [ ] **Step 3: Write the model and the section parser**

Create `scripts/oms_outline_view.py`:

```python
"""GATE 1 outline view — render .oms/<slug>/outline/outline.md as a read-only sheet.

The outline is the SSOT and is opened read-only. Content problems never raise:
a malformed or missing field becomes a flag, because a parser that throws on a
bad outline hides exactly the outline that most needs looking at.

Spec: docs/2026-08-12-gate1-outline-view-design.md
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Section:
    number: str
    name: str
    word_budget: int | None = None
    purpose: str | None = None
    core_message: str | None = None
    proposition: str | None = None
    citations: list[str] = field(default_factory=list)
    recheck: str | None = None


@dataclass
class ChainLink:
    number: str
    establishes: str | None = None
    why_needed: str | None = None
    terminal: bool = False


@dataclass
class Outline:
    title: str | None = None
    venue: str | None = None
    page_limit: int | None = None
    budget_total: int | None = None
    sections: list[Section] = field(default_factory=list)
    chain: list[ChainLink] = field(default_factory=list)
    mapping: dict[str, list[str]] | None = None


@dataclass
class Flag:
    code: str
    section: str | None
    detail: str


_TITLE_RE = re.compile(r"^##\s+Outline\s*[—-]\s*(.+?)\s*$", re.M)
_SECTION_RE = re.compile(r"^####\s*§\s*([0-9A-Za-z.]+?)\.?\s+(.*?)\s*$", re.M)
_BUDGET_RE = re.compile(r"word budget:\s*([\d,]+)")
_FIELD_RE = re.compile(r"^-\s*\*\*(.+?)\*\*\s*:\s*(.*)$", re.M)
_KEY_RE = re.compile(r"`([^`]+)`")

_FIELD_ATTR = {
    "purpose": "purpose",
    "core message": "core_message",
    "proposition to argue": "proposition",
    "researcher recheck needed": "recheck",
}


def _clean(value: str) -> str | None:
    """Empty, whitespace-only, or unfilled-template values read as absent."""
    value = value.strip()
    if not value or value in {"[]", "-", "—"}:
        return None
    return value


def _citekeys(value: str) -> list[str]:
    keys = _KEY_RE.findall(value)
    if keys:
        return [k.strip() for k in keys if k.strip()]
    return [p.strip() for p in value.split(",") if p.strip() and p.strip() != "…"]


def _parse_sections(text: str) -> list[Section]:
    matches = list(_SECTION_RE.finditer(text))
    sections: list[Section] = []
    for i, m in enumerate(matches):
        heading = m.group(2)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end() : end]

        budget_m = _BUDGET_RE.search(heading)
        name = _BUDGET_RE.sub("", heading)
        name = re.sub(r"[—-]\s*\[?\s*\]?\s*$", "", name).strip(" -—[]")

        sec = Section(number=m.group(1), name=name)
        if budget_m:
            sec.word_budget = int(budget_m.group(1).replace(",", ""))

        for f in _FIELD_RE.finditer(body):
            label = f.group(1).strip().lower()
            attr = _FIELD_ATTR.get(label)
            if attr:
                setattr(sec, attr, _clean(f.group(2)))
            elif label == "dependent citations":
                sec.citations = _citekeys(f.group(2))
        sections.append(sec)
    return sections


def parse_outline(text: str) -> Outline:
    outline = Outline()
    title_m = _TITLE_RE.search(text)
    if title_m:
        outline.title = title_m.group(1).strip()
    outline.sections = _parse_sections(text)
    return outline
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: PASS, 2 tests

- [ ] **Step 5: Lint and commit**

```bash
cd ~/oh-my-scholar
ruff check scripts/oms_outline_view.py
git add scripts/oms_outline_view.py tests/test_oms_outline_view.py
git commit -m "feat(outline-view): parse the outline section tree

Dataclass model plus the section parser. A missing field parses to None
rather than raising — absence is the signal the gate needs, not an error.

Confidence: high
Scope-risk: narrow"
```

---

### Task 2: Venue constraints, necessity chain, and citation mapping

**Files:**
- Modify: `scripts/oms_outline_view.py`
- Test: `tests/test_oms_outline_view.py`

**Interfaces:**
- Consumes: `Outline`, `ChainLink`, `parse_outline` from Task 1.
- Produces: `parse_outline` now fills `venue`, `page_limit`, `budget_total`, `chain`, and `mapping`. `mapping` is `None` when the block is absent and a `dict[str, list[str]]` when present — Task 3 distinguishes these two.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_oms_outline_view.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: FAIL — the 5 new tests fail with `AssertionError` (fields are still at their defaults)

- [ ] **Step 3: Write the three parsers**

Add to `scripts/oms_outline_view.py`, above `parse_outline`:

```python
_VENUE_RE = re.compile(r"venue:\s*(.+?)(?:\s{2,}|\s*\|\s*|$)", re.M)
_PAGE_LIMIT_RE = re.compile(r"page_limit:\s*(\d+)")
_BUDGET_TOTAL_RE = re.compile(r"word budget total:\s*([\d,]+)")
_CHAIN_HEAD_RE = re.compile(r"^§\s*([0-9A-Za-z.]+)\s*(.*)$")
_ARROW_RE = re.compile(r"^\s*→\s*(.+?)\s*:\s*(.*)$")
_TERMINAL_RE = re.compile(r"→\s*paper contribution complete", re.I)
_MAP_ROW_RE = re.compile(r"^\|\s*§\s*([0-9A-Za-z.]+)\s*\|\s*(.*?)\s*\|\s*$", re.M)


def _section_block(text: str, heading: str) -> str | None:
    """Return the text under a `### <heading>` up to the next `###`, or None."""
    start = re.search(rf"^###\s*{re.escape(heading)}.*$", text, re.M)
    if not start:
        return None
    rest = text[start.end() :]
    nxt = re.search(r"^###\s", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def _parse_venue(text: str, outline: Outline) -> None:
    block = _section_block(text, "Venue constraints")
    if block is None:
        return
    venue_m = _VENUE_RE.search(block)
    if venue_m:
        outline.venue = _clean(venue_m.group(1))
    limit_m = _PAGE_LIMIT_RE.search(block)
    if limit_m:
        outline.page_limit = int(limit_m.group(1))
    total_m = _BUDGET_TOTAL_RE.search(block)
    if total_m:
        outline.budget_total = int(total_m.group(1).replace(",", ""))


def _parse_chain(text: str) -> list[ChainLink]:
    block = _section_block(text, "Story Arc")
    if block is None:
        return []
    links: list[ChainLink] = []
    for line in block.splitlines():
        stripped = line.strip()
        head = _CHAIN_HEAD_RE.match(stripped) if stripped.startswith("§") else None
        if head:
            links.append(ChainLink(number=head.group(1)))
            continue
        if not links:
            continue
        if _TERMINAL_RE.search(line):
            links[-1].terminal = True
            continue
        arrow = _ARROW_RE.match(line)
        if arrow:
            label = arrow.group(1).strip().lower()
            if label == "establishes":
                links[-1].establishes = _clean(arrow.group(2))
            elif label == "why this is needed":
                links[-1].why_needed = _clean(arrow.group(2))
    if links:
        links[-1].terminal = True
    return links


def _parse_mapping(text: str) -> dict[str, list[str]] | None:
    block = _section_block(text, "Full citation-dependency mapping")
    if block is None:
        return None
    mapping: dict[str, list[str]] = {}
    for row in _MAP_ROW_RE.finditer(block):
        mapping[row.group(1)] = _citekeys(row.group(2))
    return mapping
```

Then extend `parse_outline`:

```python
def parse_outline(text: str) -> Outline:
    outline = Outline()
    title_m = _TITLE_RE.search(text)
    if title_m:
        outline.title = title_m.group(1).strip()
    _parse_venue(text, outline)
    outline.sections = _parse_sections(text)
    outline.chain = _parse_chain(text)
    outline.mapping = _parse_mapping(text)
    return outline
```

Note on `links[-1].terminal = True`: the last chain entry is terminal whether or not it carries the completion marker. Both conditions set the same flag, so an outline that omits the marker still exempts its final section from the blank-link check.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: PASS, 7 tests

- [ ] **Step 5: Lint and commit**

```bash
cd ~/oh-my-scholar
ruff check scripts/oms_outline_view.py
git add scripts/oms_outline_view.py tests/test_oms_outline_view.py
git commit -m "feat(outline-view): parse venue constraints, necessity chain, citation map

An absent mapping block parses to None rather than {} so the flag layer can
tell 'no summary table' from 'a table that disagrees'.

Confidence: high
Scope-risk: narrow"
```

---

### Task 3: Flag computation

**Files:**
- Modify: `scripts/oms_outline_view.py`
- Test: `tests/test_oms_outline_view.py`

**Interfaces:**
- Consumes: `Outline`, `Flag`, `parse_outline` from Tasks 1-2.
- Produces: `flags(outline: Outline) -> list[Flag]`. Flag codes are exactly: `no-sections`, `missing-field`, `section-off-chain`, `blank-link`, `recheck`, `over-budget`, `citation-mismatch`. Task 4 renders `Flag.code`, `Flag.section`, `Flag.detail`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_oms_outline_view.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: FAIL — `AttributeError: module 'oms_outline_view' has no attribute 'flags'`

- [ ] **Step 3: Write the flag layer**

Add to `scripts/oms_outline_view.py`:

```python
_REQUIRED = (
    ("purpose", "Purpose"),
    ("core_message", "Core message"),
    ("proposition", "Proposition to argue"),
    ("word_budget", "word budget"),
)


def flags(outline: Outline) -> list[Flag]:
    """Report absence, never quality. Judgment stays with the inspector and the human."""
    out: list[Flag] = []

    if not outline.sections:
        return [
            Flag(
                "no-sections",
                None,
                "No section tree was parsed — the outline is not in a shape a human can approve.",
            )
        ]

    for sec in outline.sections:
        missing = [label for attr, label in _REQUIRED if getattr(sec, attr) is None]
        if missing:
            out.append(Flag("missing-field", sec.number, "missing: " + ", ".join(missing)))
        if sec.recheck is not None:
            out.append(Flag("recheck", sec.number, f"researcher recheck needed: {sec.recheck}"))

    on_chain = {link.number for link in outline.chain}
    for sec in outline.sections:
        if sec.number not in on_chain:
            out.append(
                Flag(
                    "section-off-chain",
                    sec.number,
                    "present in the section tree but absent from the necessity chain",
                )
            )

    for link in outline.chain:
        if not link.terminal and link.why_needed is None:
            out.append(
                Flag("blank-link", link.number, "the chain link states no reason it is needed")
            )

    if outline.budget_total is not None:
        total = sum(s.word_budget for s in outline.sections if s.word_budget is not None)
        if total > outline.budget_total:
            out.append(
                Flag(
                    "over-budget",
                    None,
                    f"section budgets sum to {total} words against a stated total of "
                    f"{outline.budget_total}",
                )
            )

    if outline.mapping is not None:
        for sec in outline.sections:
            mapped = set(outline.mapping.get(sec.number, []))
            declared = set(sec.citations)
            if mapped != declared:
                only_map = sorted(mapped - declared)
                only_sec = sorted(declared - mapped)
                parts = []
                if only_map:
                    parts.append("in the mapping table only: " + ", ".join(only_map))
                if only_sec:
                    parts.append("in the section only: " + ", ".join(only_sec))
                out.append(Flag("citation-mismatch", sec.number, "; ".join(parts)))

    return out
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: PASS, 18 tests

- [ ] **Step 5: Lint and commit**

```bash
cd ~/oh-my-scholar
ruff check scripts/oms_outline_view.py
git add scripts/oms_outline_view.py tests/test_oms_outline_view.py
git commit -m "feat(outline-view): seven mechanical flags over the parsed outline

Absence only, never quality. Each defect test asserts the exact flag set, so a
flag that fires on a healthy outline fails the suite rather than becoming noise
the reader learns to ignore.

Constraint: terminal chain entry, absent recheck marker, null page limit, and
  absent mapping block are exemptions with their own tests
Rejected: near-duplicate detection | judgment in a renderer nobody reviews
Confidence: high
Scope-risk: narrow"
```

---

### Task 4: HTML rendering

**Files:**
- Modify: `scripts/oms_outline_view.py`
- Test: `tests/test_oms_outline_view.py`

**Interfaces:**
- Consumes: `Outline`, `Flag`, `parse_outline`, `flags` from Tasks 1-3.
- Produces: `render_html(outline: Outline, defects: list[Flag]) -> str`. Task 5's CLI calls it with `flags(outline)`.

Theme handling follows the three-state rule: the bare `:root` carries the full light palette, `@media (prefers-color-scheme: dark)` is guarded with `:root:not([data-theme="light"])`, and `:root[data-theme="dark"]` repeats the dark tokens. Without all three the page renders one theme's text on the other theme's ground when it is published as an artifact.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_oms_outline_view.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: FAIL — `AttributeError: module 'oms_outline_view' has no attribute 'render_html'`

- [ ] **Step 3: Write the renderer**

Add `import html as _html` to the imports, then append:

```python
_CSS = """
:root{--ground:#EDF0F0;--sheet:#F9FAFA;--card:#FFF;--ink:#141D1C;--muted:#5B6A67;
--rule:#C8D1CF;--soft:#DEE5E4;--accent:#23628F;--accent-bg:#D8EAF6;--ok:#35674F;--crit:#9C3826;
--crit-bg:#F6DED8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#0E1514;
--sheet:#151E1D;--card:#1A2423;--ink:#E3EAE8;--muted:#91A39F;--rule:#2E3B39;--soft:#232F2E;
--accent:#74BAE4;--accent-bg:#17384B;--ok:#74C398;--crit:#E5836A;--crit-bg:#3D211B}}
:root[data-theme="dark"]{--ground:#0E1514;--sheet:#151E1D;--card:#1A2423;--ink:#E3EAE8;
--muted:#91A39F;--rule:#2E3B39;--soft:#232F2E;--accent:#74BAE4;--accent-bg:#17384B;
--ok:#74C398;--crit:#E5836A;--crit-bg:#3D211B}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-size:15px;line-height:1.55;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo","Noto Sans KR",
sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:28px 20px 64px}
.head{background:var(--sheet);border:1px solid var(--rule);border-radius:3px;padding:16px 20px;
margin-bottom:8px}
.head h1{margin:0 0 6px;font-size:19px;text-wrap:balance}
.meta{color:var(--muted);font-size:13px;font-variant-numeric:tabular-nums}
.verdict{margin-top:10px;font-size:13.5px}
.verdict.clean{color:var(--ok)}
.verdict.dirty{color:var(--crit)}
.card{background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--rule);
border-radius:3px;padding:12px 14px;margin-top:8px}
.card.flagged{border-left-color:var(--crit)}
.card h2{margin:0 0 8px;font-size:15px}
.num{color:var(--muted);font-variant-numeric:tabular-nums}
dl{margin:0;display:grid;grid-template-columns:max-content 1fr;gap:4px 14px}
dt{color:var(--muted);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
padding-top:3px}
dd{margin:0}
dd.absent{color:var(--crit)}
.bar{height:5px;background:var(--soft);border-radius:2px;margin-top:8px;overflow:hidden}
.bar>i{display:block;height:100%;background:var(--accent)}
.keys{margin-top:8px;display:flex;flex-wrap:wrap;gap:5px}
.key{font-size:11px;padding:2px 7px;border-radius:2px;background:var(--accent-bg);
color:var(--accent)}
.chip{display:inline-block;font-size:10.5px;padding:2px 7px;border-radius:2px;
background:var(--crit-bg);color:var(--crit);margin:0 4px 4px 0}
.link{padding:8px 14px 0 17px;color:var(--muted);font-size:12.5px}
.link.blank{color:var(--crit)}
.foot{margin-top:26px;padding-top:14px;border-top:1px solid var(--rule);color:var(--muted);
font-size:12.5px}
""".strip()


def _esc(value) -> str:
    return _html.escape(str(value), quote=True)


def _field_row(label: str, value: str | None) -> str:
    if value is None:
        return f"<dt>{_esc(label)}</dt><dd class='absent'>absent</dd>"
    return f"<dt>{_esc(label)}</dt><dd>{_esc(value)}</dd>"


def render_html(outline: Outline, defects: list[Flag]) -> str:
    by_section: dict[str | None, list[Flag]] = {}
    for f in defects:
        by_section.setdefault(f.section, []).append(f)

    budgets = [s.word_budget or 0 for s in outline.sections]
    widest = max(budgets) if budgets else 0
    chain = {c.number: c for c in outline.chain}

    parts: list[str] = []
    title = outline.title or "Outline"
    parts.append(f"<div class='head'><h1>{_esc(title)}</h1>")
    meta = [f"venue: {outline.venue or 'unstated'}", f"sections: {len(outline.sections)}"]
    if outline.budget_total is not None:
        meta.append(f"word budget: {sum(budgets)} / {outline.budget_total}")
    parts.append(f"<div class='meta'>{_esc(' · '.join(meta))}</div>")

    if defects:
        listed = "".join(
            f"<span class='chip'>{_esc(f.code)}"
            f"{' §' + _esc(f.section) if f.section else ''}</span>"
            for f in defects
        )
        parts.append(
            f"<div class='verdict dirty'><b>{len(defects)}</b> structural gap(s) — "
            f"nothing has been drafted yet.</div><div>{listed}</div>"
        )
    else:
        parts.append(
            "<div class='verdict clean'>No mechanical gap found. "
            "Whether the argument holds is still yours to judge.</div>"
        )
    parts.append("</div>")

    for sec in outline.sections:
        hits = by_section.get(sec.number, [])
        parts.append(f"<div class='card{' flagged' if hits else ''}'>")
        parts.append(f"<h2><span class='num'>§{_esc(sec.number)}</span> {_esc(sec.name)}</h2>")
        if hits:
            parts.append(
                "".join(f"<span class='chip'>{_esc(h.code)}: {_esc(h.detail)}</span>" for h in hits)
            )
        parts.append("<dl>")
        parts.append(_field_row("Purpose", sec.purpose))
        parts.append(_field_row("Core message", sec.core_message))
        parts.append(_field_row("Proposition", sec.proposition))
        parts.append("</dl>")
        if sec.word_budget is not None and widest:
            pct = round(100 * sec.word_budget / widest)
            parts.append(
                f"<div class='bar'><i style='width:{pct}%'></i></div>"
                f"<div class='meta'>{sec.word_budget} words</div>"
            )
        else:
            parts.append("<div class='meta'>word budget absent</div>")
        if sec.citations:
            keys = "".join(f"<span class='key'>{_esc(k)}</span>" for k in sec.citations)
            parts.append(f"<div class='keys'>{keys}</div>")
        parts.append("</div>")

        link = chain.get(sec.number)
        if link and link.terminal:
            parts.append("<div class='link'>■ paper contribution complete</div>")
        elif link and link.why_needed:
            parts.append(f"<div class='link'>→ {_esc(link.why_needed)}</div>")
        else:
            parts.append(
                "<div class='link blank'>→ no stated reason the next section is needed</div>"
            )

    parts.append(
        "<div class='foot'>Derived read-only view of <code>outline.md</code>, which is the "
        "single source of truth. Approve or revise there; this sheet is regenerated, never "
        "edited.</div>"
    )

    body = "\n".join(parts)
    return (
        "<!doctype html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>\n"
        f"<title>{_esc(title)} — GATE 1</title>\n<style>{_CSS}</style>\n</head>\n"
        f"<body>\n<div class='wrap'>\n{body}\n</div>\n</body>\n</html>\n"
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: PASS, 23 tests

- [ ] **Step 5: Look at the real render and settle the deferred decision**

The spec (§9) leaves one choice to first render: whether `Proposition to argue` stays open or collapses behind a disclosure control. Generate and open the page:

```bash
cd ~/oh-my-scholar
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
sys.path.insert(0, "tests")
import oms_outline_view as ov
from test_oms_outline_view import COMPLETE
o = ov.parse_outline(COMPLETE)
Path("/tmp/gate1-preview.html").write_text(ov.render_html(o, ov.flags(o)), encoding="utf-8")
print("wrote /tmp/gate1-preview.html")
PY
open /tmp/gate1-preview.html
```

Judge one thing only: can you see enough sections at once for the sheet to beat scrolling the markdown? If yes, keep all three fields open. If no, wrap the `Proposition` row in `<details><summary>` and re-run the tests. Record the choice and what the first render actually looked like in the commit message either way.

- [ ] **Step 6: Lint and commit**

```bash
cd ~/oh-my-scholar
ruff check scripts/oms_outline_view.py
rm -f /tmp/gate1-preview.html
git add scripts/oms_outline_view.py tests/test_oms_outline_view.py
git commit -m "feat(outline-view): self-contained HTML renderer

Section cards with the chain link drawn between them, because the link is a
property of the transition rather than of either section. All three theme
states defined at token level so the page holds up published as an artifact.

Constraint: no external request of any kind — locked by test
Decision: <record the §9 Proposition-density choice and what the first render
  actually looked like>
Confidence: high
Scope-risk: narrow"
```

---

### Task 5: CLI

**Files:**
- Modify: `scripts/oms_outline_view.py`
- Test: `tests/test_oms_outline_view.py`

**Interfaces:**
- Consumes: `parse_outline`, `flags`, `render_html`.
- Produces: `main(argv: list[str] | None = None) -> int` and the `if __name__ == "__main__"` entry point. Task 6's skill text calls `python3 <plugin>/scripts/oms_outline_view.py <outline.md>`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_oms_outline_view.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: FAIL — `AttributeError: module 'oms_outline_view' has no attribute 'main'`

- [ ] **Step 3: Write the CLI**

Add `import argparse`, `import sys`, and `from pathlib import Path` to the imports, then append:

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an oms outline.md as a read-only GATE 1 sheet."
    )
    parser.add_argument("outline", help="path to .oms/<slug>/outline/outline.md")
    parser.add_argument("-o", "--output", default=None, help="output .html path")
    args = parser.parse_args(argv)

    src = Path(args.outline)
    if not src.is_file():
        parser.error(f"no such outline file: {src}")

    outline = parse_outline(src.read_text(encoding="utf-8"))
    defects = flags(outline)

    dest = Path(args.output) if args.output else src.with_name("gate1.html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_html(outline, defects), encoding="utf-8")

    print(dest)
    for f in defects:
        where = f"§{f.section}" if f.section else "outline"
        print(f"  {f.code}  {where}  {f.detail}")
    print(f"GAPS={len(defects)}")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
```

The nonzero exit on gaps is a signal, not a block — the skill reads it to decide what to say, and the sheet is written either way. `parser.error` exits with status 2, which is why the missing-file test asserts `SystemExit` rather than a custom exception.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: PASS, 27 tests

- [ ] **Step 5: Lint and commit**

```bash
cd ~/oh-my-scholar
ruff check scripts/oms_outline_view.py
git add scripts/oms_outline_view.py tests/test_oms_outline_view.py
git commit -m "feat(outline-view): CLI with a GAPS= line and a signalling exit code

Writes the sheet whether or not gaps exist; the exit code only tells the caller
what to say. A missing input file is the one raising condition in the feature.

Confidence: high
Scope-risk: narrow"
```

---

### Task 6: Wire the skill and amend the path contract

**Files:**
- Modify: `skill-bodies/scholar-outline/SKILL.md`
- Modify: `references/output-layout.md:98`
- Test: `tests/test_oms_outline_view.py`

**Interfaces:**
- Consumes: the CLI from Task 5.
- Produces: nothing consumed by later tasks.

Do **not** edit `skills/scholar-outline/SKILL.md` — it is a 13-line dispatch shim and content added there is never surfaced.

- [ ] **Step 1: Write the failing skill-text lock**

Append to `tests/test_oms_outline_view.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -k "skill_wires or output_layout" -v`
Expected: FAIL — `AssertionError` on both

- [ ] **Step 3: Amend the path contract**

In `references/output-layout.md`, replace line 98:

```
    *.md                              # outline stage: section tree, story arc, figure plan
```

with:

```
    *.md                              # outline stage: section tree, story arc, figure plan
    gate1.html                        # derived read-only GATE 1 sheet — regenerated from
                                      # outline.md by scripts/oms_outline_view.py, never edited
```

- [ ] **Step 4: Wire the skill**

In `skill-bodies/scholar-outline/SKILL.md`, inside `<Steps>` under `### Common — GATE 1`, the current step 6 opens with:

```
6. **GATE 1 — request human approval**:
   - Present the full outline (for consensus, both plan.md+outline) and specify the following three options:
```

Replace those two lines with:

```
6. **GATE 1 — request human approval**:
   - **Render the sheet first**: run `python3 <plugin>/scripts/oms_outline_view.py .oms/<slug>/outline/outline.md`. It writes `.oms/<slug>/outline/gate1.html` and prints one line per structural gap plus a final `GAPS=<n>`. The sheet is a *derived read-only view* — `outline.md` stays the SSOT, so never edit the HTML; revisions go to `outline.md` and the sheet is regenerated.
   - **Surface it**: when the running harness can publish an artifact, publish `gate1.html` and give the human the link; when it cannot, report the file path so they can open it in a browser. Its absence is a graceful degrade, not an error — the gate still functions on the text outline alone.
   - **Report the gaps verbatim, do not paper over them**: the script detects *absence* only (missing field, section off the necessity chain, blank chain link, researcher-recheck marker, over-budget total, citation-mapping mismatch, no section tree at all). `GAPS=0` means nothing mechanical is missing — it is **not** a judgment that the structure is good, and must never be presented as one.
   - Present the full outline (for consensus, both plan.md+outline) and specify the following three options:
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd ~/oh-my-scholar && python3 -m pytest tests/test_oms_outline_view.py -v`
Expected: PASS, 29 tests

- [ ] **Step 6: Commit**

```bash
cd ~/oh-my-scholar
git add skill-bodies/scholar-outline/SKILL.md references/output-layout.md \
        tests/test_oms_outline_view.py
git commit -m "feat(scholar-outline): render the GATE 1 sheet before asking for approval

GATE 1 is where a human approves and, unlike the consensus handoff, it had no
mechanical floor at all. The sheet supplies one: gaps are surfaced before the
question is asked, and GAPS=0 is explicitly not a verdict on quality.

Constraint: skill-bodies/ is authoritative — skills/ shim untouched
Constraint: artifact publishing is opportunistic; absent it, degrade to a path
Confidence: high
Scope-risk: moderate — output-layout.md is read by four consumers
Not-tested: artifact publishing itself (harness-dependent, not scriptable)"
```

---

### Task 7: Release 0.14.0

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `README.md` (Status section version and test count)

**Interfaces:**
- Consumes: everything above.
- Produces: a release branch and a PR.

- [ ] **Step 1: Run the full suite and the linter**

```bash
cd ~/oh-my-scholar
python3 -m pytest -q
ruff check .
```
Expected: all tests pass (599 pre-existing plus the new ones), ruff clean. Record the exact test count from pytest's summary — it goes into the README in step 3.

- [ ] **Step 2: Write the CHANGELOG entry**

In `CHANGELOG.md`, insert a new released section below `## [Unreleased]`. The three existing `### Fixed` bullets move under the new version heading; `[Unreleased]` is left empty.

```markdown
## [Unreleased]

## [0.14.0] - 2026-08-12

### Added

- **GATE 1 outline view** — `scholar-outline` now renders `.oms/<slug>/outline/outline.md`
  as a self-contained read-only sheet at `.oms/<slug>/outline/gate1.html` before asking for
  approval, and reports seven mechanically-detectable structural gaps: a section missing
  Purpose / Core message / Proposition to argue / word budget, a section absent from the
  necessity chain, a chain link with no stated reason, a `researcher recheck needed` marker,
  a word-budget total over the venue's, a disagreement between a section's citations and the
  mapping table, and an outline with no section tree at all. The renderer detects *absence*
  only — never quality — so `GAPS=0` is not a verdict that the structure is good. New:
  `scripts/oms_outline_view.py`, `tests/test_oms_outline_view.py`.

### Fixed

  [move the three existing Unreleased bullets here verbatim]
```

- [ ] **Step 3: Bump the version and update the README**

`.claude-plugin/plugin.json`: `"version": "0.13.1"` becomes `"version": "0.14.0"`.

`README.md` Status section: update the version and the pytest count to the number recorded in step 1.

- [ ] **Step 4: Verify version consistency across the four surfaces**

```bash
cd ~/oh-my-scholar
python3 scripts/sync_version.py
```
Expected: no drift between `plugin.json`, the CHANGELOG's top released entry, the latest `v*` tag, and the omha card. The tag does not exist yet, so a tag-behind report at this point is expected and is resolved after the PR is approved.

- [ ] **Step 5: Commit and push a branch**

```bash
cd ~/oh-my-scholar
git add CHANGELOG.md .claude-plugin/plugin.json README.md
git commit -m "chore(release): 0.14.0 — GATE 1 outline view

Confidence: high
Scope-risk: narrow"
git checkout -b feat/gate1-outline-view
git push -u origin feat/gate1-outline-view
```

Do not tag and do not merge without explicit approval. Tagging happens after the PR is approved.

- [ ] **Step 6: Open the PR**

```bash
cd ~/oh-my-scholar
gh pr create --title "GATE 1 outline view" --body "$(cat <<'EOF'
## Summary

`scholar-outline` renders the outline as a self-contained read-only sheet before asking
for GATE 1 approval, and reports seven mechanically-detectable structural gaps.

GATE 1 is where a human approves a paper structure, and it had no mechanical floor —
the `--consensus` path already refuses to proceed without the previous role's `.md` on
disk, but the human gate surfaced nothing before "proceed". This adds the floor without
adding judgment: the renderer detects absence only, so `GAPS=0` never claims the
structure is good.

`outline.md` stays the SSOT. The sheet is derived and regenerated, never edited.

Spec: `docs/2026-08-12-gate1-outline-view-design.md`
Plan: `docs/2026-08-12-gate1-outline-view-execution.md`

## Test plan

- [ ] `python3 -m pytest -q` — full suite green
- [ ] `ruff check .` — clean
- [ ] `python3 scripts/sync_version.py` — four surfaces agree
- [ ] Healthy fixture renders with zero flags
- [ ] Each of the seven flags fires on exactly its own mutation and no other
- [ ] Terminal chain entry, absent recheck marker, null page limit, and absent mapping
      block each skip their check
- [ ] Garbage input raises nothing and reports only `no-sections`
- [ ] Rendered HTML makes no external request and escapes content
- [ ] Sheet opened in a browser is legible in both light and dark

## Not covered

Artifact publishing itself is harness-dependent and not scriptable, so it is exercised
by hand rather than by test. omd's equivalent change is deferred to its own spec — omd
has no persisted outline file, and adding one touches a path SSOT with four consumers.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_012NFrC7Au8QqYLrc8xzVfCR
EOF
)"
```

---

## Self-Review

**Spec coverage.** §4.1 artifact and path → Tasks 4-5. §4.2 card contents → Task 4. §4.3 all seven flags plus the three exemptions → Task 3, one test each. §4.4 components and signatures → Tasks 1-5. §4.5 SSOT rule → carried in the skill text (Task 6) and the rendered footer (Task 4). §4.6 error handling → Task 3's garbage test and Task 5's missing-file test. §4.7 publish-or-degrade → Task 6. §5 files touched → all six appear across the tasks. §6 testing → Tasks 1-6. §8 release → Task 7. §9 deferred decision → Task 4 step 5, with a forced record in the commit message. No gaps.

**Placeholder scan.** Two intentional fill-ins remain, both transcriptions of something that exists at execution time rather than deferred design: Task 4's commit message records the §9 density decision, and Task 7 step 2 moves three existing CHANGELOG bullets verbatim.

**Type consistency.** `Section`, `ChainLink`, `Outline`, `Flag` are defined once in Task 1 and only populated afterwards. `parse_outline(text) -> Outline` is used identically in Tasks 2-5. `flags(outline) -> list[Flag]` and `render_html(outline, defects) -> str` match every call site including Task 5's CLI. The seven flag-code strings in Task 3's implementation match those asserted in Task 3's tests and listed in the CHANGELOG in Task 7. The helper is named `_field_row` throughout, avoiding a collision with `dataclasses.field` imported in Task 1.
