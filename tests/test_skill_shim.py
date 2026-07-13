"""Tests for the R3 #21 skill shim + `skill-bodies/` split.

Background: OMC's 64 KiB always-loaded skill-corpus budget (every skill's
frontmatter+body is loaded up front for routing) was being pushed by oms's
12 SKILL.md files (~92 KiB combined). The fix mirrors OMC §16's own shim
pattern: `skills/<name>/SKILL.md` shrinks to a compact routing shim (original
frontmatter byte-identical + one additive `oms-full-body:` key, plus a short
pointer body); the full instructions move to `skill-bodies/<name>/SKILL.md`
(git mv, so history follows). `plugin.json` still lists `./skills/<name>/` —
untouched by construction, still 1:1 (test_plugin_integrity.py).

This file locks: the split stays 1:1 both directions, every shim points at
its own (existing, non-empty) body, shim/body `name:` frontmatter can't
drift apart, each shim is small, the live `skills/` corpus stays well under
budget, bodies really carry the full content, and oms_doctor's post-split
[skills] FAIL branch (shim/body mismatch) actually fires — mirrors the
fixture rigor of test_oms_doctor.py's test_missing_registered_hook_fails.
"""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
BODIES_DIR = ROOT / "skill-bodies"

SCRIPT = ROOT / "scripts" / "oms_doctor.py"
_spec = importlib.util.spec_from_file_location("oms_doctor", SCRIPT)
od = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(od)


def _skill_names() -> set:
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}


def _body_names() -> set:
    return {d.name for d in BODIES_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}


def _frontmatter_name(text: str) -> str:
    """Extract the `name:` value from the YAML frontmatter block only (not
    the body) — first `---`...`---` fence."""
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert m, "no YAML frontmatter fence found"
    fm_match = re.search(r"^name:\s*(\S+)\s*$", m.group(1), re.MULTILINE)
    assert fm_match, "no 'name:' key in frontmatter"
    return fm_match.group(1)


def test_shim_body_one_to_one():
    """skills/ dirs == skill-bodies/ dirs, both directions."""
    shims = _skill_names()
    bodies = _body_names()
    assert shims, "no skills/*/SKILL.md found"
    missing_body = shims - bodies
    missing_shim = bodies - shims
    assert not missing_body, f"skills/ with no matching skill-bodies/: {missing_body}"
    assert not missing_shim, f"skill-bodies/ with no matching skills/: {missing_shim}"


def test_every_shim_points_to_its_own_body():
    """Each shim literally references skill-bodies/<its-name>/SKILL.md, and
    that target exists and is non-empty."""
    for name in sorted(_skill_names()):
        shim_text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
        expected_ref = f"skill-bodies/{name}/SKILL.md"
        assert expected_ref in shim_text, f"{name}: shim does not reference {expected_ref}"
        body_path = BODIES_DIR / name / "SKILL.md"
        assert body_path.is_file(), f"{name}: body path missing at {body_path}"
        assert body_path.stat().st_size > 0, f"{name}: body file is empty"


def test_shim_frontmatter_name_matches_body():
    """shim `name:` == body `name:` — drift lock."""
    for name in sorted(_skill_names()):
        shim_name = _frontmatter_name((SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8"))
        body_name = _frontmatter_name((BODIES_DIR / name / "SKILL.md").read_text(encoding="utf-8"))
        assert shim_name == body_name == name, \
            f"{name}: frontmatter name mismatch (shim={shim_name!r}, body={body_name!r}, dir={name!r})"


def test_shim_is_compact():
    """Every shim <= 4,096 B."""
    for name in sorted(_skill_names()):
        size = (SKILLS_DIR / name / "SKILL.md").stat().st_size
        assert size <= 4096, f"{name}: shim is {size} B, exceeds 4,096 B compact cap"


def test_corpus_under_omc_budget():
    """sum(skills/*/SKILL.md) <= 48 KiB headroom (the OMC hard cliff is 64
    KiB — a test that only proves we're under the cliff itself is a time
    bomb, so this asserts real headroom)."""
    total = sum((SKILLS_DIR / name / "SKILL.md").stat().st_size for name in _skill_names())
    assert total <= 48 * 1024, f"always-loaded shim corpus is {total} B, exceeds the 48 KiB headroom budget"


def test_bodies_kept_full():
    """Every body >= its shim's size — the moved content really lives there,
    not truncated in transit."""
    for name in sorted(_skill_names()):
        shim_size = (SKILLS_DIR / name / "SKILL.md").stat().st_size
        body_size = (BODIES_DIR / name / "SKILL.md").stat().st_size
        assert body_size >= shim_size, f"{name}: body ({body_size} B) is smaller than its shim ({shim_size} B)"


def test_doctor_fails_on_shim_body_mismatch(tmp_path):
    """Discriminance for oms_doctor's post-split [skills] branch: a shim
    that does NOT reference its own skill-bodies/ path must FAIL.

    Fixture: skills/foo/ and skill-bodies/foo/ both exist (1:1 at the
    directory level, so the count-mismatch branches stay quiet), but foo's
    shim references skill-bodies/bar (wrong name) instead of skill-bodies/foo
    — isolating the "shim references its own body path" check specifically."""
    root = tmp_path / "repo"
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "fixture", "version": "0.1.0", "skills": ["./skills/foo/"], "hooks": {}}),
        encoding="utf-8",
    )
    (root / "skills" / "foo").mkdir(parents=True)
    (root / "skills" / "foo" / "SKILL.md").write_text(
        "---\nname: foo\ndescription: fixture\n---\n\n"
        "points at the wrong body: skill-bodies/bar/SKILL.md\n",
        encoding="utf-8",
    )
    (root / "skill-bodies" / "foo").mkdir(parents=True)
    (root / "skill-bodies" / "foo" / "SKILL.md").write_text("full body content\n", encoding="utf-8")

    rows = od.check_skills(root)
    fails = [r for r in rows if r["status"] == "FAIL"]
    assert any("foo" in r["message"] and "skill-bodies/foo" in r["message"] for r in fails), fails
