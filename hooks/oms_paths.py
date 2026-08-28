"""Single declaration point for this repo's on-disk root literals — the
unified store `.hq` and the legacy store `.oms` — plus the shared
directory-ascent helper `nearest_ancestor` (R2/R-debt unification; om*
store-unification P2/P4, store-spec.md §9.5).

Every derived path hooks/scripts compute (learned.md, notepad.md, state/,
wiki/, venues/*.yaml, ...) is named here once. Callers never join a root
literal themselves; a re-entry lint (tests/test_oms_paths_lint.py) fails the
build if either literal appears anywhere outside this file.

Reference: ~/oh-my-orchestrator/skills/harness/references/store-spec.md
  §3 the four layers · §6 the four-state gate · §7 fallback · §9.3 oms's
  per-file layer assignment (harness slot `scholar`) · §9.5 the six
  declaration sites.

P2 (2026-08-28, 3a80b02) moved every existing inline `.oms` computation
behind named helpers — a pure move, legacy-only, no `.hq`, no file moves.

P4 (2026-08-28) switches this module from "legacy only" to the cutover
shape, mirroring oh-my-project's hooks/omp_paths.py (P3). Three rules govern
every helper below, and they are not interchangeable:

**1. The anchor is the switch, not the release.** A write goes to `.hq/`
when — and only when — the project root carries a parseable `.hq/.anchor`.
Without one it goes to `.oms/`, exactly where it went before. Making the
write unconditional at release time would split-brain every project that
has a `.oms/` and no anchor yet: reads would still resolve to the legacy
store (the only one with content) while writes landed in a new one nobody
reads.

**2. Reads resolve per file, new first, legacy second.** Not per directory:
a machine that pulled the anchor commit gets the tracked layers (`config/`,
`community/`) but never the ignored ones (`work/`, `runtime/`), so its own
`.oms/state/` markers must still be readable while
`.hq/config/scholar/learned.md` is already live. Existence of the specific
path is the only test; absence of the new one is not evidence of anything.

**3. The layer is per file, never per directory** (§3). `.oms/state/` fans
out across two layers: `verified-citations.json` alone is `config/scholar/`
(⑤(b) fails — losing it costs a re-verification pass); everything else in
`state/` (`pilot-*.json`, `revise-*.json`) is `runtime/scholar/` (⑤ —
session state, loss harmless). A helper keyed on the whole directory would
put both in the same layer, so `verified_citations_json` resolves the single
file while `state_dir` resolves the remaining directory as its own unit —
two helpers, not one, for the same `.oms/state/` origin.
"""
from __future__ import annotations

import re
from pathlib import Path

HQ_ROOT = ".hq"
LEGACY_ROOT = ".oms"

# Substring form used where code checks membership inside prose/file content
# (e.g. a .gitignore body) rather than building a Path. Derived from the root
# literals so each is still declared exactly once.
GITIGNORE_ENTRY = f"{LEGACY_ROOT}/"
HQ_GITIGNORE_ENTRY = f"{HQ_ROOT}/"

# --- layer roots (store-spec section 3; harness slot "scholar") ------------

ANCHOR_REL = f"{HQ_ROOT}/.anchor"
_CONFIG_REL = f"{HQ_ROOT}/config/scholar"
_COMMUNITY_REL = f"{HQ_ROOT}/community"
_RUNTIME_REL = f"{HQ_ROOT}/runtime/scholar"
_WORK_REL = f"{HQ_ROOT}/work/scholar"

_ANCHOR_ID_RE = re.compile(r"^id:\s*(\S.*)$")


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


def legacy_root(base: Path) -> Path:
    """The legacy `.oms/` dir directly under `base`."""
    return Path(base) / LEGACY_ROOT


def anchor_file(base: Path) -> Path:
    return Path(base) / ANCHOR_REL


def config_dir(base: Path) -> Path:
    return Path(base) / _CONFIG_REL


def community_dir(base: Path) -> Path:
    return Path(base) / _COMMUNITY_REL


def runtime_dir(base: Path) -> Path:
    return Path(base) / _RUNTIME_REL


def work_dir(base: Path) -> Path:
    return Path(base) / _WORK_REL


def migrated_jsonl(base: Path) -> Path:
    """The anchor-wide migration ledger — `config/`, not `config/scholar/`:
    it is shared across harnesses (store-spec section 2)."""
    return Path(base) / HQ_ROOT / "config" / "migrated.jsonl"


# --- anchor parse and the four-state gate (store-spec sections 2 and 6) ----

class AnchorError(Exception):
    """The anchor file exists but does not parse — a corrupt store, never an
    absent one."""


def parse_anchor_id(path: Path) -> str:
    """Exactly one non-empty line `id: <value>` after stripping one trailing
    newline. Anything else raises. Deliberately a 10-line reimplementation of
    omo's `hq.anchor.parse_anchor` rather than a cross-plugin import: oms
    cannot assume oh-my-orchestrator is installed, and an ImportError in a
    hook is a worse failure than a duplicated regex."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise AnchorError(f"{path}: cannot read anchor file: {e}") from e
    text = raw[:-1] if raw.endswith("\n") else raw
    non_empty = [ln for ln in text.split("\n") if ln.strip() != ""]
    if len(non_empty) != 1:
        raise AnchorError(
            f"{path}: expected exactly one non-empty line, found {len(non_empty)}")
    m = _ANCHOR_ID_RE.match(non_empty[0])
    if not m:
        raise AnchorError(
            f"{path}: line does not match 'id: <value>': {non_empty[0]!r}")
    value = m.group(1).strip()
    if not value:
        raise AnchorError(f"{path}: empty id value")
    return value


def has_anchor(base: Path) -> bool:
    """True when `base` carries a *parseable* anchor. An unparseable one is
    False here and `corrupt` in `gate_state` — the write switch must not flip
    on a broken file."""
    f = anchor_file(base)
    if not f.is_file():
        return False
    try:
        parse_anchor_id(f)
        return True
    except AnchorError:
        return False


def has_legacy_store(base: Path) -> bool:
    return legacy_root(base).is_dir()


def has_store(base: Path) -> bool:
    """True when `base` is an oms project under either store."""
    return anchor_file(base).is_file() or has_legacy_store(base)


GATE_OFF = "off"
GATE_LEGACY = "legacy"
GATE_NORMAL = "normal"
GATE_CORRUPT = "corrupt"


def gate_state(base: Path) -> str:
    """store-spec section 6, the pair (legacy store, anchor) — never a single
    marker.

    off      no legacy store, no anchor   — not an oms project; hooks exit 0
    legacy   legacy store, no anchor      — warn, read via fallback
    normal   anchor present and parseable
    corrupt  anchor present, unparseable  — loud, never silent
    """
    f = anchor_file(base)
    if f.is_file():
        try:
            parse_anchor_id(f)
            return GATE_NORMAL
        except AnchorError:
            return GATE_CORRUPT
    return GATE_LEGACY if has_legacy_store(base) else GATE_OFF


# --- resolution: read new-then-legacy, write anchor-gated -------------------

def _read(new: Path, legacy: Path) -> Path:
    """Rule 2. Existence of the specific new path is the whole test."""
    return new if new.exists() else legacy


def _write(base: Path, new: Path, legacy: Path) -> Path:
    """Rule 1. The anchor, not the release, decides — and an anchored root
    whose files have not been copied yet keeps writing where the content
    still is.

    The middle branch is the one that matters: seeding an anchor is a
    separate step from copying the store (store-spec section 7 stage 1 is
    copy *then* switch), so between the two an anchored root has a populated
    legacy path and an empty new one. Writing to the new path there would
    orphan every write from a reader that still resolves to the legacy path.
    Only when neither path holds this artifact — a project anchored from
    scratch — does the new path win by default.
    """
    if not has_anchor(base):
        return legacy
    if new.exists():
        return new
    return legacy if legacy.exists() else new


# --- config/scholar/ layer ---------------------------------------------------

def learned_md(base: Path) -> Path:
    return _read(config_dir(base) / "learned.md", legacy_root(base) / "learned.md")


def notepad_md(base: Path) -> Path:
    """`notepad.md` fails ⑤(a) — scholar-pilot rewrites `## Priority Context`
    only on GATE transitions, not every turn — so it lands in `config/`
    rather than `runtime/` (store-spec §9.3)."""
    return _read(config_dir(base) / "notepad.md", legacy_root(base) / "notepad.md")


def venue_yaml(base: Path, venue: str) -> Path:
    return _read(config_dir(base) / "venues" / f"{venue}.yaml",
                 legacy_root(base) / "venues" / f"{venue}.yaml")


def workflows_dir(base: Path) -> Path:
    return _read(config_dir(base) / "workflows", legacy_root(base) / "workflows")


def verified_citations_json(base: Path) -> Path:
    """The cite-guard allowlist. `state/verified-citations.json` under the
    legacy store, `config/scholar/verified-citations.json` once migrated —
    NOT `runtime/scholar/`, see the module docstring's rule 3."""
    return _read(config_dir(base) / "verified-citations.json",
                 legacy_root(base) / "state" / "verified-citations.json")


def verified_citations_json_write(base: Path) -> Path:
    return _write(base, config_dir(base) / "verified-citations.json",
                  legacy_root(base) / "state" / "verified-citations.json")


# --- runtime/scholar/ layer --------------------------------------------------

def state_dir(base: Path) -> Path:
    """The directory holding `pilot-<slug>.json` / `revise-<slug>.json` —
    session-mechanism state (⑤: rewritten every session, loss harmless).
    Resolved as a directory, unlike `verified_citations_json` which used to
    live in this same `.oms/state/` directory but fails ⑤(b) and stays in
    `config/scholar/` instead (module docstring rule 3)."""
    return _read(runtime_dir(base), legacy_root(base) / "state")


def state_dir_write(base: Path) -> Path:
    return _write(base, runtime_dir(base), legacy_root(base) / "state")


# --- community/ layer ---------------------------------------------------------

def wiki_dir(base: Path) -> Path:
    return _read(community_dir(base) / "wiki", legacy_root(base) / "wiki")


def reading_dir(base: Path) -> Path:
    return _read(community_dir(base) / "reading", legacy_root(base) / "reading")


def backport_design_dir(base: Path) -> Path:
    return _read(community_dir(base) / "_backport-design",
                 legacy_root(base) / "_backport-design")


# --- work/scholar/<slug>/ layer -----------------------------------------------

def slug_dir(base: Path, slug: str) -> Path:
    """A paper workspace `<slug>/` — versions/renders/research/outline/tmp/
    per-run scaffolding (④, store-spec §9.3)."""
    return _read(work_dir(base) / slug, legacy_root(base) / slug)


# --- relative-string forms ----------------------------------------------------
# For CLI argparse defaults that must stay literal strings (a leading `./`
# normalizes away through Path operations, which would silently change the
# CLI's documented default). Deliberately NOT gate-aware.

def state_dir_default_str() -> str:
    """The legacy `--state-dir` default string, `'./.oms/state'`.

    Built as a string, not via Path — `Path(".") / LEGACY_ROOT` normalizes
    away the leading `./`, which would silently change a CLI's documented
    default.

    P4 fixed a real cite-guard gap this caused: `.oms/state/` splits into two
    layers once migrated (`verified-citations.json` -> `config/scholar/`,
    everything else -> `runtime/scholar/`), so one literal default can never
    name the right directory for both. `verify_bib_entry.py` and
    `oms_state.py` no longer call this function — their `--state-dir` now
    defaults to `None` and resolves at call time via
    `verified_citations_json_write(Path.cwd())` / `state_dir_write(Path.cwd())`
    respectively. This function is KEPT (not deleted) only because its exact
    string is pinned by existing tests.
    """
    return f"./{LEGACY_ROOT}/state"


def wiki_dir_default_str() -> str:
    """argparse `--root` default (oms_wiki_audit.py), exactly as today: `'./.oms/wiki'`."""
    return f"./{LEGACY_ROOT}/wiki"
