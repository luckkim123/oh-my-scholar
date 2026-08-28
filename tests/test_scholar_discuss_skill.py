"""Tests for scholar-discuss (R5 T3 / #29): standing Socratic discussion partner.

Background: a 14th skill — an on-demand devil's-advocate partner over ideas, zero `.tex`
surface. Interactive in the main session (invariant 1 untouched: no content is generated
here, so there is nothing to parallelize and no subagent dispatch at all — unlike
scholar-read's single dispatch to scholar-researcher). Three self-contained personas
(Contrarian / Simplifier / Ontologist, D3) restate — but do not import or modify —
scholar-deepen's Round 4/6/8 originals (scholar-deepen/SKILL.md stays on the do-not-touch
list). A Co-STORM-style moderator move surfaces retrieved-but-unused evidence. Outline
deltas surfaced during discussion are proposed at a human gate, never auto-applied (D9 —
deliberately more conservative than the roadmap's "appends to the living outline", because
auto-mutating a GATE1-approved artifact would breach invariant 5).

House convention (see test_scholar_read_skill.py / test_scholar_pilot_skill.py): plain
asserts via `skill_md()` + `.index()`-scoped windows, discriminance tests proving the
boundaries actually hold (no subagent dispatch, no `.tex`/`.bib` write, deltas proposed
not applied) rather than merely being named in passing.
"""
import json
import re
from pathlib import Path

from conftest import skill_md

ROOT = Path(__file__).parent.parent
SHIM = (ROOT / "skills" / "scholar-discuss" / "SKILL.md").read_text(encoding="utf-8")
BODY = skill_md("scholar-discuss")
DEEPEN_BODY = skill_md("scholar-deepen")


# --------------------------------------------------------- shim contract
def test_shim_is_compact_and_points_at_body():
    assert len(SHIM.encode("utf-8")) <= 4096
    assert "skill-bodies/scholar-discuss/SKILL.md" in SHIM
    assert "oms-full-body: ../../skill-bodies/scholar-discuss/SKILL.md" in SHIM


def test_shim_has_triggers():
    assert "Triggers:" in SHIM
    for trigger in ("토론하자", "discuss this idea", "devil's advocate", "argue with me"):
        assert trigger in SHIM, f"missing trigger phrase: {trigger}"


def test_plugin_json_registers_scholar_discuss():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert any(Path(s).name == "scholar-discuss" for s in plugin["skills"])
    assert (ROOT / "skills" / "scholar-discuss" / "SKILL.md").is_file()


# --------------------------------------------------------- invariant 1: no subagent dispatch
def test_body_dispatches_no_subagent():
    """Discriminance: unlike scholar-read (single dispatch), discuss has no actual
    `Task(subagent_type=...)` invocation anywhere — the one prose mention of `Task(...)`
    is in the negation sentence saying there is none (same negation-context idiom as
    test_scholar_read_skill.py's `--record` check)."""
    assert "subagent_type" not in BODY
    hits = list(re.finditer(r"Task\(", BODY))
    for m in hits:
        window = BODY[max(0, m.start() - 20): m.start()]
        assert re.search(r"no|without", window, re.I), \
            f"'Task(' appears without a negation nearby: ...{window!r}"


def test_body_states_no_dispatch_explicitly():
    assert re.search(r"no subagent dispatch", BODY, re.I)
    assert "invariant 1" in BODY


# --------------------------------------------------------- personas (D3)
def test_body_names_all_three_personas():
    for persona in ("Contrarian", "Simplifier", "Ontologist"):
        assert persona in BODY, f"missing persona: {persona}"


def test_body_persona_prompts_are_present_verbatim():
    idx = BODY.index("2. **Stance rounds**")
    end = BODY.index("3. **Moderator move")
    sub = BODY[idx:end]
    assert "What if the opposite" in sub
    assert "kept only 1 of 3 contributions" in sub
    assert "What *is* this thing" in sub


def test_body_has_persona_provenance_note_pointing_at_deepen():
    """D3: personas are self-contained restatements with a one-line provenance note
    pointing at scholar-deepen Round 4/6/8 — not a shared personas card, not an edit
    to scholar-deepen itself."""
    assert re.search(r"Round 4/6/8", BODY)
    assert "scholar-deepen" in BODY
    assert re.search(r"does not (import|extract)", BODY, re.I) or re.search(r"not import", BODY, re.I)


def test_scholar_deepen_body_is_untouched_by_this_task():
    """Discriminance: scholar-deepen still carries its OWN Round 4/6/8 prompts verbatim —
    proves T3 restated the personas rather than moving/deleting them from deepen
    (do-not-touch list, plan §Sequencing)."""
    assert "Round 4 Contrarian" in DEEPEN_BODY
    assert "Round 6 Simplifier" in DEEPEN_BODY
    assert "Round 8 Ontologist" in DEEPEN_BODY


# --------------------------------------------------------- moderator move (Co-STORM)
def test_body_has_moderator_move_step():
    idx = BODY.index("3. **Moderator move")
    end = BODY.index("4. **Exit**")
    sub = BODY[idx:end]
    assert "Co-STORM" in sub
    assert re.search(r"gap list", sub, re.I)
    assert re.search(r"highest-information-gain", sub, re.I)


def test_moderator_move_scans_research_and_reading_notes():
    idx = BODY.index("3. **Moderator move")
    end = BODY.index("4. **Exit**")
    sub = BODY[idx:end]
    assert "research/*.md" in sub
    assert "reading/*.md" in sub


# --------------------------------------------------------- exit: wiki decision/ + research-log
def test_body_writes_wiki_decision_note():
    assert ".hq/community/wiki/decision/" in BODY
    assert "create-if-absent" in BODY


def test_body_wiki_write_has_confidence_frontmatter_and_low_rule():
    """#24 append-time rule: a pointerless/quote-less summary is still appended, but at
    confidence: low with an evidence:none marker — never a reject gate."""
    assert "confidence" in BODY
    assert "sightings" in BODY
    assert re.search(r"confidence:\s*low", BODY)
    assert re.search(r"evidence:\s*none", BODY)


def test_body_appends_research_log_context_discuss():
    assert "research-log.md" in BODY
    assert re.search(r"context\s*`?discuss`?", BODY, re.I)
    assert "create-if-absent" in BODY


def test_body_no_embeddings_mentioned_as_recall_mechanism():
    """Invariant 3: no embeddings anywhere in oms's own recall — this skill's wiki write
    must not introduce one."""
    assert "embedding" not in BODY.lower() or "no embeddings" in BODY.lower() or "deterministic grep" in BODY


# --------------------------------------------------------- outline deltas: proposed, never applied (D9)
def test_body_outline_deltas_proposed_not_applied():
    assert re.search(r"never (auto-)?applied", BODY, re.I)
    assert re.search(r"human gate", BODY, re.I)
    assert "D9" in BODY


def test_body_outline_delta_is_explicit_list_at_gate():
    idx = BODY.index("4. **Exit**")
    end = BODY.index("</Steps>")
    sub = BODY[idx:end]
    assert re.search(r"proposed", sub, re.I)
    assert re.search(r"never auto-applied", sub, re.I)


# --------------------------------------------------------- zero .tex/.bib surface boundary
def test_body_states_zero_tex_bib_surface():
    assert re.search(r"[Zz]ero `?\.tex`?/`?\.bib`? surface", BODY)


def test_body_claims_unverified_unless_anchored():
    assert re.search(r"unverified", BODY, re.I)
    assert re.search(r"anchored", BODY, re.I)


def test_output_section_names_no_tex_bib_or_dispatch():
    idx = BODY.index("<Output>")
    end = BODY.index("</Output>")
    sub = BODY[idx:end]
    assert re.search(r"No `?\.tex`?", sub)
    assert re.search(r"`?\.bib`?", sub)
    assert re.search(r"no subagent dispatch", sub, re.I)
