"""R3 #18 — `oms doctor`: read-only packaging self-diagnosis.

Paperpal-style fixed categories, each reporting PASS/WARN/FAIL rows with
evidence: [version] [hooks] [agents] [skills] and, only with `--paper-root`,
[state]. Never writes anything — this is a report, not a fixer.

Direct causal motivation: the 4-way version drift fixed by R3 #15
(`sync_version.py`) accumulated silently across 3 untagged releases because
nothing checked cross-surface agreement. `sync_version` is this doctor's
[version] section (imported sibling-style, same idiom `oms_state.py` uses
for `hooks/oms_atomic.py`); doctor generalizes the same "nothing checks
surface agreement" failure mode to hooks/agents/skills registration and,
optionally, stale `.oms/<slug>/` pilot state.

Card routing (plan-mandated): the omha card at `<OMHA_ROOT>/cards/oms.json`
is a foreign repo surface whose version bump rides a separate
oh-my-heroacademia PR. Both card-absent and card-mismatched map to WARN,
never FAIL — every other version-drift surface maps to FAIL.

Exit 1 iff any FAIL row anywhere; 0 otherwise.
"""
import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_version  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from oms_paths import legacy_root as oms_root  # noqa: E402

VALID_MODELS = {"haiku", "sonnet", "opus"}
LIBRARY_HOOK_MODULES = {"oms_atomic.py"}
STATE_EXCLUDE_DIRS = {"state", "wiki", "venues"}


def _row(status, message) -> dict:
    return {"status": status, "message": message}


# ---------------------------------------------------------------- [version]
def check_version(repo_root) -> list:
    """Reuse sync_version's gather/check. Card surface (absent or `card:`
    -prefixed drift) routes to WARN; every other drift string routes to FAIL."""
    repo_root = Path(repo_root)
    s = sync_version.gather(repo_root)
    drift = sync_version.check(
        s["plugin"], s["changelog_top"], s["changelog_prev"], s["latest_tag"], s["card"]
    )
    rows = [
        _row("WARN" if d.startswith("card:") else "FAIL", d)
        for d in drift
    ]
    if s["card"] is None:
        rows.append(_row("WARN", "omha card not found at OMHA_ROOT/cards/oms.json (foreign surface)"))
    if not rows:
        rows.append(_row("PASS", f"plugin.json {s['plugin']} in sync across all surfaces"))
    return rows


# ------------------------------------------------------------------ [hooks]
def _load_plugin(repo_root) -> dict:
    return json.loads((Path(repo_root) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


def check_hooks(repo_root) -> list:
    """Every registered hook command resolves to a file under hooks/ and
    parses (ast.parse) -> FAIL if not. Any hooks/*.py neither registered nor
    a known library module (oms_atomic.py) -> WARN (orphan)."""
    repo_root = Path(repo_root)
    hooks_dir = repo_root / "hooks"
    plugin = _load_plugin(repo_root)
    rows = []
    registered = set()

    for entries in plugin.get("hooks", {}).values():
        for entry in entries:
            for h in entry.get("hooks", []):
                for arg in h.get("args", []):
                    if not arg.endswith(".py"):
                        continue
                    name = Path(arg).name
                    registered.add(name)
                    path = hooks_dir / name
                    if not path.is_file():
                        rows.append(_row("FAIL", f"registered hook {name} missing at hooks/{name}"))
                        continue
                    try:
                        ast.parse(path.read_text(encoding="utf-8"))
                    except SyntaxError as e:
                        rows.append(_row("FAIL", f"hooks/{name} fails to parse: {e}"))

    if hooks_dir.is_dir():
        for path in sorted(hooks_dir.glob("*.py")):
            if path.name in registered or path.name in LIBRARY_HOOK_MODULES:
                continue
            rows.append(_row("WARN", f"orphan hooks/{path.name} (neither registered nor a known library module)"))

    if not rows:
        rows.append(_row("PASS", f"{len(registered)} registered hooks resolve and parse"))
    return rows


# ----------------------------------------------------------------- [agents]
def _parse_frontmatter(text: str):
    """Minimal `key: value` frontmatter reader (stdlib only, no YAML dep) —
    every agents/*.md frontmatter block here is flat single-line values."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fm[key.strip()] = value
    return fm


def check_agents(repo_root) -> list:
    """Every agents/*.md frontmatter parses with name/description/model
    present; model must be in {haiku, sonnet, opus} -> FAIL on violation."""
    agents_dir = Path(repo_root) / "agents"
    rows = []
    if not agents_dir.is_dir():
        return rows

    paths = sorted(agents_dir.glob("*.md"))
    for path in paths:
        fm = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            rows.append(_row("FAIL", f"{path.name}: frontmatter missing or malformed"))
            continue
        missing = [k for k in ("name", "description", "model") if k not in fm]
        if missing:
            rows.append(_row("FAIL", f"{path.name}: missing frontmatter key(s) {missing}"))
            continue
        if fm["model"] not in VALID_MODELS:
            rows.append(_row("FAIL", f"{path.name}: model {fm['model']!r} not in {sorted(VALID_MODELS)}"))

    if not rows:
        rows.append(_row("PASS", f"{len(paths)} agent files parse with a valid model"))
    return rows


# ----------------------------------------------------------------- [skills]
def check_skills(repo_root) -> list:
    """plugin.json skills <-> skills/ dirs 1:1 (same rule as
    test_plugin_integrity.py). If skill-bodies/ exists (post-T5): skills/ <->
    skill-bodies/ 1:1 and every shim references its own body path. Checks
    only what exists -- green both before and after that split lands."""
    repo_root = Path(repo_root)
    plugin = _load_plugin(repo_root)
    skills_dir = repo_root / "skills"
    rows = []

    registered = {Path(s).name for s in plugin.get("skills", [])}
    actual = (
        {d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}
        if skills_dir.is_dir() else set()
    )

    for name in sorted(actual - registered):
        rows.append(_row("FAIL", f"{name}: skills/ dir exists but not registered in plugin.json"))
    for name in sorted(registered - actual):
        rows.append(_row("FAIL", f"{name}: registered in plugin.json but no skills/ directory"))

    body_dir = repo_root / "skill-bodies"
    if body_dir.is_dir():
        bodies = {d.name for d in body_dir.iterdir() if d.is_dir()}
        for name in sorted(actual - bodies):
            rows.append(_row("FAIL", f"{name}: skills/ dir has no matching skill-bodies/ dir"))
        for name in sorted(bodies - actual):
            rows.append(_row("FAIL", f"{name}: skill-bodies/ dir has no matching skills/ dir"))
        for name in sorted(actual & bodies):
            shim_path = skills_dir / name / "SKILL.md"
            body_ref = f"skill-bodies/{name}"
            if body_ref not in shim_path.read_text(encoding="utf-8"):
                rows.append(_row("FAIL", f"{name}: shim does not reference its own body path {body_ref}"))

    if not rows:
        rows.append(_row("PASS", f"{len(actual)} skills registered 1:1 with skills/"))
    return rows


# ------------------------------------------------------------------ [state]
def check_state(paper_root) -> list:
    """Optional, only with --paper-root D: scan D/.oms/<slug>/ dirs (excluding
    state/wiki/venues) against D/.oms/state/pilot-<slug>.json. A slug with a
    terminal/abort pilot state, or with no pilot state at all, is a WARN
    cleanup candidate -- advisory only, never FAIL, doctor never deletes."""
    oms_dir = oms_root(Path(paper_root))
    rows = []
    if not oms_dir.is_dir():
        return rows

    state_dir = oms_dir / "state"
    slugs = sorted(
        d.name for d in oms_dir.iterdir()
        if d.is_dir() and d.name not in STATE_EXCLUDE_DIRS
    )
    for slug in slugs:
        pilot_path = state_dir / f"pilot-{slug}.json"
        if not pilot_path.is_file():
            rows.append(_row("WARN", f"{slug}: no pilot state — cleanup candidate"))
            continue
        try:
            pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            rows.append(_row("WARN", f"{slug}: pilot state unreadable — cleanup candidate"))
            continue
        if pilot.get("stage") == "terminal" or pilot.get("gate_status") == "abort":
            rows.append(_row(
                "WARN",
                f"{slug}: stage={pilot.get('stage')} gate_status={pilot.get('gate_status')} — cleanup candidate",
            ))
    return rows


# -------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read-only categorized packaging self-diagnosis (never writes).")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--paper-root", default=None, help="optional: also scan D/.oms/<slug>/ for cleanup candidates")
    args = ap.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    sections = [
        ("version", check_version(repo_root)),
        ("hooks", check_hooks(repo_root)),
        ("agents", check_agents(repo_root)),
        ("skills", check_skills(repo_root)),
    ]
    if args.paper_root:
        sections.append(("state", check_state(Path(args.paper_root).resolve())))

    any_fail = False
    for name, rows in sections:
        print(f"[{name}]")
        if not rows:
            print("  (nothing to check)")
        for row in rows:
            print(f"  {row['status']}: {row['message']}")
            if row["status"] == "FAIL":
                any_fail = True

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
