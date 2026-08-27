"""Shared directory-ascent helper + path SSOT for oms hooks/scripts (R2/R-debt
unification; om* store-unification P2, store-spec.md §9.5).

Three call sites each walked `start`/`cwd` up its ancestor chain looking for a
different marker (`.oms/state` dir, `.oms/state` dir OR `.oms/notepad.md`, a
specific `.oms/state/verified-citations.json` file) with slightly different
stop conditions (inclusive-of-start vs exclusive). `nearest_ancestor` is the
one walk, parameterized by a per-call-site predicate — each call site keeps
its own exact marker check and its own return value, only the ascent loop is
shared.

P2 addition: `LEGACY_ROOT` + the derived-path helpers below are the ONLY
place in this repo allowed to declare the `.oms` root string literal
(guarded by tests/test_oms_paths_lint.py). P2 is a pure move — every helper
returns exactly the path today's inline call sites already computed; no
path changes, no file moves, no `.hq` migration (that's P3+).
"""
from pathlib import Path


def nearest_ancestor(start: Path, predicate, include_start: bool = True):
    """Return the first ancestor directory of `start` for which
    `predicate(candidate)` is truthy, else None.

    `include_start=True` checks `start` itself first (then parents);
    `include_start=False` starts the walk at `start`'s parent. Stops at the
    first hit — never looks past it.
    """
    candidates = (start, *start.parents) if include_start else start.parents
    for candidate in candidates:
        if predicate(candidate):
            return candidate
    return None


LEGACY_ROOT = ".oms"

# Substring form used where code checks membership inside prose/file content
# (e.g. a .gitignore body) rather than building a Path. Derived from
# LEGACY_ROOT so the literal is still declared exactly once.
GITIGNORE_ENTRY = f"{LEGACY_ROOT}/"


def root(base: Path) -> Path:
    """The `.oms/` dir directly under `base`."""
    return base / LEGACY_ROOT


def state_dir(base: Path) -> Path:
    """`.oms/state/` under `base`."""
    return root(base) / "state"


def notepad_md(base: Path) -> Path:
    """`.oms/notepad.md` under `base`."""
    return root(base) / "notepad.md"


def verified_citations_json(base: Path) -> Path:
    """`.oms/state/verified-citations.json` under `base` (cite-guard allowlist)."""
    return state_dir(base) / "verified-citations.json"


def wiki_dir(base: Path) -> Path:
    """`.oms/wiki/` under `base`."""
    return root(base) / "wiki"


def venue_yaml(base: Path, venue: str) -> Path:
    """`.oms/venues/<venue>.yaml` under `base`."""
    return root(base) / "venues" / f"{venue}.yaml"


def state_dir_default_str() -> str:
    """argparse `--state-dir` default, exactly as today: `'./.oms/state'`.

    Built as a string, not via Path — `Path(".") / LEGACY_ROOT` normalizes
    away the leading `./`, which would silently change the CLI's documented
    default. This is the one call site that must reproduce the literal string.
    """
    return f"./{LEGACY_ROOT}/state"


def wiki_dir_default_str() -> str:
    """argparse `--root` default (oms_wiki_audit.py), exactly as today: `'./.oms/wiki'`."""
    return f"./{LEGACY_ROOT}/wiki"
