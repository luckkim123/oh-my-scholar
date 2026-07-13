"""Tests for scholar-read (R5 T2 / #28): external-paper deep-read → structured reading note.

Background: a 13th skill turning "read this paper for me" into a structured, citation-safe
reading note at `.oms/reading/<citekey>.md` (D1) — a personal reading corpus that outlives any
one paper project, sibling of `.oms/wiki/`, strictly separate from this project's own citation
pipeline (invariant 2: reading notes are NEVER a `.bib` source; the only door into the
bibliography stays scholar-research → human-confirmed `.bib`). Single dispatch only (invariant 1)
to `scholar-researcher` `mode="deep-read"` — a new mode alongside the existing default
`mode="gap-research"` (agents/scholar-researcher.md), whose original output contract is not
reworded.

House convention (see test_scholar_pilot_skill.py / test_scholar_mock_review_skill.py): plain
asserts via `skill_md()` + `.index()`-scoped windows, discriminance tests proving the original
gap-research contract text survives verbatim and that the new dispatch is genuinely singular
(not accidentally doubled into a parallel-looking pattern).
"""
import json
import re
from pathlib import Path

from conftest import layout_section, skill_md

ROOT = Path(__file__).parent.parent
SHIM = (ROOT / "skills" / "scholar-read" / "SKILL.md").read_text(encoding="utf-8")
BODY = skill_md("scholar-read")
LAYOUT = (ROOT / "references" / "output-layout.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "scholar-researcher.md").read_text(encoding="utf-8")

NOT_CITABLE_HEADER = (
    "> NOT CITABLE — secondary memo. A .bib entry may only be created via scholar-research verification."
)

DISPATCH_RE = re.compile(r'Task\(subagent_type="oh-my-scholar:scholar-researcher"')


# --------------------------------------------------------- shim contract
def test_shim_is_compact_and_points_at_body():
    assert len(SHIM.encode("utf-8")) <= 4096
    assert "skill-bodies/scholar-read/SKILL.md" in SHIM
    assert "oms-full-body: ../../skill-bodies/scholar-read/SKILL.md" in SHIM


def test_shim_has_triggers():
    assert "Triggers:" in SHIM
    for trigger in ("read this paper", "deep read", "reading note"):
        assert trigger in SHIM, f"missing trigger phrase: {trigger}"


def test_plugin_json_registers_scholar_read():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert any(Path(s).name == "scholar-read" for s in plugin["skills"])
    assert (ROOT / "skills" / "scholar-read" / "SKILL.md").is_file()


# --------------------------------------------------------- body: single dispatch (invariant 1)
def test_body_dispatches_scholar_researcher_exactly_once():
    """Discriminance: singular dispatch, not accidentally doubled into a parallel-looking call."""
    hits = DISPATCH_RE.findall(BODY)
    assert len(hits) == 1, f"expected exactly one literal dispatch call, found {len(hits)}"


def test_body_dispatch_uses_deep_read_mode():
    idx = BODY.index('Task(subagent_type="oh-my-scholar:scholar-researcher"')
    window = BODY[idx: idx + 120]
    assert 'mode="deep-read"' in window


def test_body_names_single_dispatch_not_parallel():
    assert re.search(r"single careful dispatch, not parallel", BODY, re.I)
    assert "invariant 1" in BODY


# --------------------------------------------------------- NOT CITABLE + no .bib write (invariant 2)
def test_body_names_not_citable_header_verbatim():
    assert NOT_CITABLE_HEADER in BODY


def test_shim_has_no_record_flag():
    assert "--record" not in SHIM


def test_body_record_flag_only_appears_in_negation_context():
    """Discriminance: `--record` is only ever named to say NOT to use it (no `--record` /
    invoked WITHOUT `--record`) — never as an instruction the skill actually issues."""
    hits = list(re.finditer(r"--record", BODY))
    assert hits, "expected the skill to name --record at least once, to forbid it"
    for m in hits:
        window = BODY[max(0, m.start() - 20): m.start()]
        assert re.search(r"no|without", window, re.I), \
            f"'--record' appears without a negation nearby: ...{window!r}"


def test_body_states_no_bib_write():
    assert re.search(r"[Nn]o `?\.bib`? is written", BODY)
    assert re.search(r"human confirmation", BODY, re.I)


def test_body_citekey_is_filename_convention_not_bibtex_key():
    assert "NOT a BibTeX key" in BODY


# --------------------------------------------------------- RETRACTED handling
def test_body_retracted_handling_is_loud():
    assert re.search(r"RETRACTED is loud", BODY)


def test_body_surfaces_retracted_at_digest_step():
    idx = BODY.index("6. **Surface**")
    end = BODY.index("</Steps>")
    sub = BODY[idx:end]
    assert re.search(r"RETRACTED", sub)
    assert re.search(r"loudly", sub, re.I)


# --------------------------------------------------------- identity pre-check step (no --record)
def test_body_identity_precheck_invocation_command_has_no_record_flag():
    """The actual backtick-quoted invocation command (not the surrounding prose) never
    passes --record — the negation prose is allowed to name the flag, the command must not."""
    m = re.search(r"`python3 scripts/verify_bib_entry\.py[^`]*`", BODY)
    assert m, "identity pre-check invocation command not found"
    assert "--record" not in m.group(0)


def test_body_identity_verdict_enum_named():
    assert "VERIFIED | MISMATCH | RETRACTED | NOT_FOUND | NETWORK_ERROR" in BODY


# --------------------------------------------------------- research-log wiring (T1 integration)
def test_body_appends_research_log_context_read():
    assert "research-log.md" in BODY
    assert re.search(r"context\s*`?read`?", BODY, re.I)
    assert "create-if-absent" in BODY


# =========================================================== output-layout.md §2 / §2.1 / §2.5 / §5 / §6
def test_layout_tree_has_reading_entry():
    sec2 = layout_section(LAYOUT, r"^## 2\. Fixed directory structure", r"^## 3\.")
    assert ".oms/reading/" in sec2
    assert "<citekey>.md" in sec2


def test_layout_invariance_mentions_reading_sibling_of_wiki():
    sec2 = layout_section(LAYOUT, r"^## 2\. Fixed directory structure", r"^## 3\.")
    inv = layout_section(sec2, r"### 2\.1 Invariance rules", r"### 2\.2")
    assert ".oms/reading/" in inv
    assert "sibling of" in inv


def test_layout_has_reading_note_format_subsection():
    sec2 = layout_section(LAYOUT, r"^## 2\. Fixed directory structure", r"^## 3\.")
    idx = sec2.index("### 2.5 reading note format")
    sub = sec2[idx:]
    assert NOT_CITABLE_HEADER in sub
    assert "scholar-read" in sub
    assert re.search(r"never a[\s*]*`\.bib`[\s*]*source", sub)
    assert "Paper identity" in sub


def test_layout_cleanup_table_has_reading_keep_row():
    sec5 = layout_section(LAYOUT, r"^## 5\. Terminal cleanup", r"^## 6\.")
    reading_lines = [ln for ln in sec5.splitlines() if ".oms/reading" in ln]
    assert reading_lines, "§5 cleanup table missing .oms/reading/ row"
    assert any("KEEP" in ln for ln in reading_lines)


def test_layout_checklist_has_reading_row():
    sec6 = layout_section(LAYOUT, r"^## 6\. Implementation checklist", r"\Z")
    assert "scholar-read" in sec6
    assert ".oms/reading" in sec6
    assert "calling session" in sec6


# =========================================================== agents/scholar-researcher.md mode locks
def test_agent_description_mentions_both_modes():
    assert "mode=gap-research" in AGENT
    assert "mode=deep-read" in AGENT


def test_agent_investigation_protocol_has_both_mode_headers_in_order():
    assert "### mode=gap-research" in AGENT
    assert "### mode=deep-read" in AGENT
    idx_gap = AGENT.index("### mode=gap-research")
    idx_deep = AGENT.index("### mode=deep-read")
    assert idx_gap < idx_deep


def test_agent_gap_research_output_contract_survives_verbatim():
    """Discriminance: the ORIGINAL mode=gap-research output contract text is not reworded."""
    assert "[one sentence + necessity chain: existing X fails at Y → this paper does Z]" in AGENT
    assert "## Citation Verification" in AGENT
    assert "## Inferences (not evidence)" in AGENT
    assert "- Verified: N | Unverified (needs human check): M [list]" in AGENT


def test_agent_deep_read_output_sections_present():
    idx = AGENT.index("### mode=deep-read output")
    end = AGENT.index("</Output_Format>")
    sub = AGENT[idx:end]
    for header in (
        "## Paper identity", "## Claims", "## Method", "## Evidence",
        "## Limitations", "## Relation to my work", "## Open questions",
    ):
        assert header in sub, f"missing {header} in deep-read output contract"


def test_agent_retracted_marker_is_loud_and_verbatim():
    assert "⚠️ RETRACTED" in AGENT
    idx = AGENT.index("### mode=deep-read output")
    end = AGENT.index("</Output_Format>")
    sub = AGENT[idx:end]
    assert re.search(r"restated verbatim", sub, re.I)


def test_agent_deep_read_has_injection_hygiene_step():
    idx = AGENT.index("### mode=deep-read")
    end = AGENT.index("</Investigation_Protocol>")
    sub = AGENT[idx:end]
    assert re.search(r"injection", sub, re.I)


def test_agent_relation_to_my_work_is_conditional_not_guessed():
    idx = AGENT.index("## Relation to my work")
    window = AGENT[idx: idx + 200]
    assert re.search(r"only when|omitted", window, re.I)


def test_agent_deep_read_reuses_quote_anchor_contract():
    idx = AGENT.index("### mode=deep-read")
    end = AGENT.index("</Investigation_Protocol>")
    sub = AGENT[idx:end]
    assert re.search(r"verbatim quote", sub, re.I)
    assert re.search(r"locator", sub, re.I)
    assert re.search(r"never reconstructed from memory", sub, re.I)
