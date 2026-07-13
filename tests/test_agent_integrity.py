"""Tests for agent frontmatter integrity + cross-reference resolution (R3 #19+#20).

#19: every agents/*.md frontmatter is well-formed (live keys, valid model tier),
and the author/reviewer asymmetry — scholar-drafter is the ONLY agent allowed to
write .tex/.bib, the other 5 are read-only critics/gates — is locked from BOTH
sides (reviewers carry `disallowedTools` ⊇ {Write, Edit}; drafter carries no
`disallowedTools` key at all). Also: every `subagent_type="oh-my-scholar:<X>"`
reference in skills/**/SKILL.md (+ skill-bodies/**/SKILL.md, empty until T5
splits skill bodies out) resolves to a real agents/<X>.md, and every agent is
reachable from at least one skill (catches dead agents).

#20: scholar-verifier's tier is pinned to sonnet. Routing-economics rationale
(the audit's, not the agent file's): scholar-verify is a mechanical PASS/FAIL
gate — compile/numbers/refs/citations checked against objective evidence, not
adjudicated judgment — so it doesn't need opus the way scholar-inspector
(formative critique) or scholar-reviewer (venue-scale adjudication) do. This
test exists so a future edit can't silently regress the tier back to opus.

Frontmatter parsing reuses scripts/oms_doctor.py's `_parse_frontmatter` (same
importlib idiom as test_oms_doctor.py) instead of re-implementing a YAML-ish
reader — one stdlib-only parser, one place to fix if the format changes.
"""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENTS_DIR = ROOT / "agents"
WRITER_AGENT = "scholar-drafter"

_spec = importlib.util.spec_from_file_location("oms_doctor", ROOT / "scripts" / "oms_doctor.py")
od = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(od)

# Verified live form (grepped across skills/*/SKILL.md at plan time).
SUBAGENT_TYPE_RE = re.compile(r'subagent_type="oh-my-scholar:([a-z-]+)"')
# Looser net for a prose/unquoted reference inside a Task( call — global regex
# above already covers every real occurrence today, this just guards the form drifting.
TASK_LINE_RE = re.compile(r'oh-my-scholar:([a-z-]+)')


def _agent_paths():
    return sorted(AGENTS_DIR.glob("*.md"))


def _frontmatter(path):
    fm = od._parse_frontmatter(path.read_text(encoding="utf-8"))
    assert fm is not None, f"{path.name}: frontmatter missing or malformed"
    return fm


def _skill_files():
    # skill-bodies/ doesn't exist yet (Task 5 creates it) — glob returns [], which is fine.
    return sorted(ROOT.glob("skills/**/SKILL.md")) + sorted(ROOT.glob("skill-bodies/**/SKILL.md"))


def _referenced_agent_names():
    names = set()
    for path in _skill_files():
        text = path.read_text(encoding="utf-8")
        names.update(SUBAGENT_TYPE_RE.findall(text))
        for line in text.splitlines():
            if "Task(" in line:
                names.update(TASK_LINE_RE.findall(line))
    return names


def test_all_agents_have_live_keys():
    """① every agents/*.md frontmatter has name/description/model."""
    for path in _agent_paths():
        fm = _frontmatter(path)
        missing = [k for k in ("name", "description", "model") if k not in fm]
        assert not missing, f"{path.name}: missing frontmatter key(s) {missing}"


def test_model_values_are_valid_tiers():
    """② model ∈ {haiku, sonnet, opus}."""
    for path in _agent_paths():
        fm = _frontmatter(path)
        assert fm["model"] in od.VALID_MODELS, f"{path.name}: model {fm['model']!r} not a valid tier"


def test_reviewer_agents_block_writes():
    """③ every agent except scholar-drafter carries disallowedTools ⊇ {Write, Edit}
    (locks the asymmetry from the reviewer side)."""
    reviewers = [p for p in _agent_paths() if p.stem != WRITER_AGENT]
    assert len(reviewers) == 5, f"expected 5 reviewer agents, found {len(reviewers)}"
    for path in reviewers:
        fm = _frontmatter(path)
        assert "disallowedTools" in fm, f"{path.name}: missing disallowedTools"
        tools = {t.strip() for t in fm["disallowedTools"].split(",")}
        assert {"Write", "Edit"} <= tools, f"{path.name}: disallowedTools {tools} doesn't block Write+Edit"


def test_drafter_is_the_only_writer():
    """④ scholar-drafter has NO disallowedTools key at all (locks the asymmetry
    from the author side — same both-sides idiom as the triple self-approval ban)."""
    fm = _frontmatter(AGENTS_DIR / f"{WRITER_AGENT}.md")
    assert "disallowedTools" not in fm, "scholar-drafter is the single writer; it must not carry disallowedTools"


def test_skill_agent_references_resolve():
    """⑤ every subagent_type="oh-my-scholar:<X>" reference across skills/**/SKILL.md
    (+ skill-bodies/**/SKILL.md) resolves to a real agents/<X>.md.

    Discriminance proof (pitfall 1, recorded in task-4-report.md): with a
    subagent_type typo'd locally to a nonexistent agent name, this test FAILs;
    reverting makes it pass again — proves this assert isn't vacuously green."""
    agent_names = {p.stem for p in _agent_paths()}
    for path in _skill_files():
        text = path.read_text(encoding="utf-8")
        for name in SUBAGENT_TYPE_RE.findall(text):
            assert name in agent_names, f"{path}: dangling reference oh-my-scholar:{name}"


def test_every_agent_is_reachable():
    """⑥ every agents/*.md is referenced by at least one skill (catches dead
    agents). All 6 current agents are referenced as of this task — if a
    legitimately unreferenced agent shows up later, name it in a skip comment
    here rather than forcing this assert to pass."""
    agent_names = {p.stem for p in _agent_paths()}
    referenced = _referenced_agent_names()
    unreferenced = agent_names - referenced
    assert not unreferenced, f"agent(s) with no skill reference (dead?): {unreferenced}"


def test_verifier_is_sonnet():
    """⑦ #20 tier lock: scholar-verifier is sonnet, description ends with
    '(Sonnet)', and '(Opus)' is gone."""
    fm = _frontmatter(AGENTS_DIR / "scholar-verifier.md")
    assert fm["model"] == "sonnet", f"scholar-verifier model is {fm['model']!r}, expected 'sonnet'"
    assert "(Sonnet)" in fm["description"], "scholar-verifier description missing '(Sonnet)' tag"
    assert "(Opus)" not in fm["description"], "scholar-verifier description still says '(Opus)'"
