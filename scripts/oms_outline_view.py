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
# Matches the whole trailing "— [word budget: 600 words]" clause, not just the
# number, so the name left behind has no bracket/unit debris to clean up.
_BUDGET_RE = re.compile(r"\s*[—-]*\s*\[word budget:\s*([\d,]+)\s*words?\]\s*$")
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
        name = _BUDGET_RE.sub("", heading).strip()

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
