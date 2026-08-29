"""Store cutover acceptance — the four-state gate and anchor-gated resolution
(om* store-unification, oms's `.oms` -> `.hq` cutover; mirrors oh-my-project's
tests/test_omp_store_cutover.py).

store-spec.md section 6 requires a fixture for all four gate rows, and it is
worth saying why each of the three "not normal" rows is here rather than
folded into one "not on the new store" case:

  off      the harness must be genuinely inert in a folder that is not an oms
           project at all — the one row where silence is correct
  legacy   the most dangerous state of the whole migration, and the one a
           three-state design would send into `off` where a stopped hook
           looks exactly like a correctly-quiet one
  corrupt  the row that reverses a blanket fail-open: a store that will not
           parse is not an absent store

P4 (stage 1) gave reads a per-file existence fallback and writes a
three-branch gate protecting the anchored-but-not-yet-copied window. Stage 2
(store-spec §7) collapses both into one anchor-only `_resolve`: anchored ->
`.hq/`, unanchored -> `.oms/`, unconditionally, for reads and writes alike.
The tests that used to pin the old per-file/window behavior are gone;
`test_read_resolves_to_new_store_even_when_only_legacy_exists_once_anchored`
and `test_read_stays_legacy_for_an_unanchored_project_with_a_legacy_file`
below are their stage-2 replacements.

`.oms/state/` fanning out across two layers (config/scholar for
verified-citations.json, runtime/scholar for everything else) is oms-specific
and has no omp analogue — it gets its own dedicated tests below rather than
being folded into the generic anchor-resolution case, since it is the one
place in this repo's mapping table where a single legacy directory splits.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))
from oms_paths import (  # noqa: E402
    GATE_CORRUPT, GATE_LEGACY, GATE_NORMAL, GATE_OFF, AnchorError,
    gate_state, learned_md, notepad_md, parse_anchor_id, posts_dir, state_dir,
    state_dir_write, venue_yaml, verified_citations_json,
    verified_citations_json_write,
)


def _load_script(name: str):
    """Import `scripts/<name>.py` fresh by file path (idiom shared with
    tests/test_verify_bib_entry.py and tests/test_oms_state.py) — the script
    itself inserts `hooks/` onto sys.path on exec, so nothing extra is needed
    here."""
    path = Path(__file__).parent.parent / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_cutover_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vbe = _load_script("verify_bib_entry")
oms_state_mod = _load_script("oms_state")


def _seed_anchor(base, text="id: fixture\n"):
    (base / ".hq").mkdir(parents=True, exist_ok=True)
    (base / ".hq" / ".anchor").write_text(text, encoding="utf-8")


def _seed_legacy(base):
    (base / ".oms" / "state").mkdir(parents=True, exist_ok=True)
    (base / ".oms" / "notepad.md").write_text("# notepad\n", encoding="utf-8")


def _seed_migrated(base):
    """A fully cut-over anchor: anchor + every layer populated."""
    _seed_anchor(base)
    cfg = base / ".hq" / "config" / "scholar"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "learned.md").write_text("# l\n", encoding="utf-8")
    (cfg / "notepad.md").write_text("# n\n", encoding="utf-8")
    (cfg / "verified-citations.json").write_text('{"keys": {}}', encoding="utf-8")
    venues = cfg / "venues"
    venues.mkdir(parents=True, exist_ok=True)
    (venues / "generic.yaml").write_text("key: x\n", encoding="utf-8")
    (base / ".hq" / "community" / "posts").mkdir(parents=True, exist_ok=True)
    rt = base / ".hq" / "runtime" / "scholar"
    rt.mkdir(parents=True, exist_ok=True)
    (rt / "pilot-demo.json").write_text("{}", encoding="utf-8")


# --- the four gate states ---------------------------------------------------

def test_gate_off(tmp_path):
    assert gate_state(tmp_path) == GATE_OFF


def test_gate_legacy(tmp_path):
    _seed_legacy(tmp_path)
    assert gate_state(tmp_path) == GATE_LEGACY


def test_gate_normal(tmp_path):
    _seed_anchor(tmp_path)
    assert gate_state(tmp_path) == GATE_NORMAL


@pytest.mark.parametrize("bad", [
    "id: a\nid: b\n",          # two lines
    "vault\n",                 # missing the id: prefix
    "id:   \n",                # empty value
    "",                        # empty file
])
def test_gate_corrupt(tmp_path, bad):
    _seed_anchor(tmp_path, bad)
    assert gate_state(tmp_path) == GATE_CORRUPT


def test_gate_corrupt_beats_legacy(tmp_path):
    """A broken anchor next to a populated legacy store is corrupt, not
    legacy — the pair is read anchor-first, or a typo would silently look
    like 'not yet migrated' and keep writing to the old store forever."""
    _seed_legacy(tmp_path)
    _seed_anchor(tmp_path, "id: a\nid: b\n")
    assert gate_state(tmp_path) == GATE_CORRUPT


def test_parse_anchor_id_roundtrip(tmp_path):
    _seed_anchor(tmp_path, "id: oh-my-scholar\n")
    assert parse_anchor_id(tmp_path / ".hq" / ".anchor") == "oh-my-scholar"
    with pytest.raises(AnchorError):
        parse_anchor_id(tmp_path / ".hq" / "nope")


# --- read resolution: new path when migrated, legacy when not ---------------

def test_every_helper_resolves_to_the_new_store_when_migrated(tmp_path):
    _seed_migrated(tmp_path)
    hq = tmp_path / ".hq"
    assert learned_md(tmp_path) == hq / "config/scholar/learned.md"
    assert notepad_md(tmp_path) == hq / "config/scholar/notepad.md"
    assert verified_citations_json(tmp_path) == hq / "config/scholar/verified-citations.json"
    assert venue_yaml(tmp_path, "generic") == hq / "config/scholar/venues/generic.yaml"
    assert posts_dir(tmp_path) == hq / "community/posts"
    assert state_dir(tmp_path) == hq / "runtime/scholar"


def test_every_helper_falls_back_when_only_the_legacy_store_exists(tmp_path):
    """posts_dir() is deliberately absent from this batch — r7 (2026-08-30) gave it
    no legacy fallback at all (spec: "wiki_dir() 게터를 posts_dir() 로 교체 (legacy
    fallback 없음)"), unlike every other helper here. Its own behavior is covered by
    test_posts_dir_has_no_legacy_fallback below."""
    _seed_legacy(tmp_path)
    (tmp_path / ".oms" / "learned.md").write_text("# l\n", encoding="utf-8")
    (tmp_path / ".oms" / "venues").mkdir()
    (tmp_path / ".oms" / "venues" / "generic.yaml").write_text("key: x\n", encoding="utf-8")
    (tmp_path / ".oms" / "state" / "verified-citations.json").write_text(
        '{"keys": {}}', encoding="utf-8")
    legacy = tmp_path / ".oms"
    assert learned_md(tmp_path) == legacy / "learned.md"
    assert notepad_md(tmp_path) == legacy / "notepad.md"
    assert verified_citations_json(tmp_path) == legacy / "state/verified-citations.json"
    assert venue_yaml(tmp_path, "generic") == legacy / "venues/generic.yaml"
    assert state_dir(tmp_path) == legacy / "state"


def test_posts_dir_has_no_legacy_fallback(tmp_path):
    """r7 (2026-08-30): posts_dir() always resolves to `.hq/community/posts` — anchored
    or not, migrated or not. A store still holding wiki pages under `.oms/wiki/` (or
    `.hq/community/wiki/`) converts once with omo's convert-wiki-form.py rather than
    being read in place; posts_dir() itself never looks at either legacy location."""
    hq_posts = tmp_path / ".hq" / "community" / "posts"

    # no anchor, no legacy store at all
    assert posts_dir(tmp_path) == hq_posts

    # legacy store present, unanchored — still resolves to .hq/, unlike every
    # other helper's fallback-to-legacy behavior
    _seed_legacy(tmp_path)
    (tmp_path / ".oms" / "wiki").mkdir()
    assert posts_dir(tmp_path) == hq_posts

    # anchored — same answer, now for the ordinary reason
    _seed_anchor(tmp_path)
    assert posts_dir(tmp_path) == hq_posts


def test_read_resolves_to_new_store_even_when_only_legacy_exists_once_anchored(tmp_path):
    """Stage 2 (store-spec §7): the anchor alone decides, in both
    directions. An anchored project whose file has not yet been copied to
    `.hq/` resolves to the (non-existent) new path anyway -- the per-file
    existence fallback stage 1 used is gone."""
    _seed_anchor(tmp_path)
    (tmp_path / ".oms").mkdir()
    (tmp_path / ".oms" / "learned.md").write_text("# l\n", encoding="utf-8")
    assert learned_md(tmp_path) == tmp_path / ".hq/config/scholar/learned.md"


def test_read_stays_legacy_for_an_unanchored_project_with_a_legacy_file(tmp_path):
    """No anchor at all: the helper still resolves to the legacy store,
    unconditionally -- a machine that never migrated keeps working exactly
    as before."""
    _seed_legacy(tmp_path)
    (tmp_path / ".oms" / "learned.md").write_text("# l\n", encoding="utf-8")
    assert learned_md(tmp_path) == tmp_path / ".oms/learned.md"


# --- state/ splits across two layers (oms-specific: no omp analogue) --------

def test_legacy_state_dir_splits_across_two_layers_once_migrated(tmp_path):
    """`.oms/state/` fans out: verified-citations.json is config/scholar
    (③, ⑤(b) fails -- losing it costs a re-verification pass), while
    everything else in state/ (pilot-*.json, revise-*.json) is
    runtime/scholar (⑤ -- session state, loss harmless). A helper keyed on
    the whole directory would put both in the same layer; store-spec
    section 3 requires per-file resolution instead."""
    _seed_migrated(tmp_path)
    hq = tmp_path / ".hq"
    assert verified_citations_json(tmp_path) == hq / "config/scholar/verified-citations.json"
    assert state_dir(tmp_path) == hq / "runtime/scholar"
    assert verified_citations_json(tmp_path).parent != state_dir(tmp_path)


def test_legacy_state_dir_two_layers_also_holds_under_fallback(tmp_path):
    """Same split, unmigrated: both still resolve out of the ONE legacy
    `.oms/state/` directory, but as two independent helper calls -- proof the
    split is a read-time decision, not something baked into disk layout."""
    _seed_legacy(tmp_path)
    (tmp_path / ".oms" / "state" / "verified-citations.json").write_text(
        '{"keys": {}}', encoding="utf-8")
    legacy_state = tmp_path / ".oms" / "state"
    assert verified_citations_json(tmp_path) == legacy_state / "verified-citations.json"
    assert state_dir(tmp_path) == legacy_state


# --- write gating: the anchor decides, and a half-migrated root stays put ----

def test_write_goes_legacy_without_an_anchor(tmp_path):
    _seed_legacy(tmp_path)
    assert verified_citations_json_write(tmp_path) == tmp_path / ".oms/state/verified-citations.json"
    assert state_dir_write(tmp_path) == tmp_path / ".oms/state"


def test_write_goes_new_when_migrated(tmp_path):
    _seed_migrated(tmp_path)
    assert verified_citations_json_write(tmp_path) == \
        tmp_path / ".hq/config/scholar/verified-citations.json"
    assert state_dir_write(tmp_path) == tmp_path / ".hq/runtime/scholar"


def test_write_goes_new_even_when_anchored_but_not_yet_copied(tmp_path):
    """Stage 2 closes the pilot's old window. Seeding the anchor used to
    leave writes pinned to a populated legacy store until the copy caught
    up; now the anchor alone decides, so a write lands in `.hq/` the moment
    the anchor exists, regardless of what `.oms/` still holds."""
    _seed_legacy(tmp_path)
    (tmp_path / ".oms" / "state" / "verified-citations.json").write_text(
        '{"keys": {}}', encoding="utf-8")
    (tmp_path / ".oms" / "state" / "pilot-demo.json").write_text("{}", encoding="utf-8")
    _seed_anchor(tmp_path)
    assert verified_citations_json_write(tmp_path) == \
        tmp_path / ".hq/config/scholar/verified-citations.json"
    assert state_dir_write(tmp_path) == tmp_path / ".hq/runtime/scholar"


def test_write_goes_new_for_a_project_anchored_from_scratch(tmp_path):
    """Neither path holds the artifact and there is no legacy store to
    orphan — this is the only case where the new path wins by default."""
    _seed_anchor(tmp_path)
    assert verified_citations_json_write(tmp_path) == \
        tmp_path / ".hq/config/scholar/verified-citations.json"
    assert state_dir_write(tmp_path) == tmp_path / ".hq/runtime/scholar"


# --- the CLI gap: verify_bib_entry.py / oms_state.py without --state-dir ----
# Both scripts used to default `--state-dir` to the LITERAL legacy string
# `state_dir_default_str()`. In an anchored+copied project that silently
# writes to the shadowed legacy path forever while every read
# (`verified_citations_json()`/`state_dir()`) already prefers the new one —
# a citation gets verified, recorded, and then invisible to cite-guard. The
# round trip below (write via the CLI's own default, read back via the
# oms_paths helper) is this defect's exact shape; a directory existence
# check alone would not have caught it.

def test_verify_bib_entry_record_default_writes_new_and_round_trips(tmp_path, monkeypatch):
    _seed_migrated(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        vbe, "verify",
        lambda *a, **kw: vbe.Verdict("VERIFIED", "crossref", "ok", doi="10.1/x", title="T"),
    )
    assert vbe.main(["--key", "smith2024", "--doi", "10.1/x", "--record"]) == 0
    target = verified_citations_json(tmp_path)
    assert target == tmp_path / ".hq/config/scholar/verified-citations.json"
    assert json.loads(target.read_text(encoding="utf-8"))["keys"]["smith2024"]["doi"] == "10.1/x"


def test_verify_bib_entry_record_default_writes_legacy_without_anchor(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        vbe, "verify",
        lambda *a, **kw: vbe.Verdict("VERIFIED", "crossref", "ok", doi="10.1/x", title="T"),
    )
    assert vbe.main(["--key", "smith2024", "--doi", "10.1/x", "--record"]) == 0
    target = verified_citations_json(tmp_path)
    assert target == tmp_path / ".oms/state/verified-citations.json"
    assert target.is_file()


def test_oms_state_write_default_writes_new_and_round_trips(tmp_path, monkeypatch):
    _seed_migrated(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert oms_state_mod.main(["write", "--slug", "demo", "--stage", "draft"]) == 0
    target = state_dir(tmp_path) / "pilot-demo.json"
    assert target == tmp_path / ".hq/runtime/scholar/pilot-demo.json"
    assert json.loads(target.read_text(encoding="utf-8"))["stage"] == "draft"


def test_oms_state_write_default_writes_legacy_without_anchor(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert oms_state_mod.main(["write", "--slug", "demo", "--stage", "draft"]) == 0
    target = state_dir(tmp_path) / "pilot-demo.json"
    assert target == tmp_path / ".oms/state/pilot-demo.json"
    assert target.is_file()


def test_verify_bib_entry_explicit_state_dir_still_respected(tmp_path, monkeypatch):
    """An explicit --state-dir must never be overridden by the gate-aware
    default, migrated or not."""
    _seed_migrated(tmp_path)
    monkeypatch.chdir(tmp_path)
    custom = tmp_path / "elsewhere"
    monkeypatch.setattr(
        vbe, "verify",
        lambda *a, **kw: vbe.Verdict("VERIFIED", "crossref", "ok", doi="10.1/x", title="T"),
    )
    assert vbe.main(
        ["--key", "smith2024", "--doi", "10.1/x", "--record", "--state-dir", str(custom)]
    ) == 0
    assert (custom / "verified-citations.json").is_file()
    untouched = tmp_path / ".hq/config/scholar/verified-citations.json"
    assert json.loads(untouched.read_text(encoding="utf-8")) == {"keys": {}}


# test_oms_wiki_audit_default_root_resolves_new_when_migrated and
# test_oms_wiki_audit_default_root_resolves_legacy_without_anchor removed (r7,
# 2026-08-30): both exercised `scripts/oms_wiki_audit.py`'s own `--root` default
# against `wiki_dir()`'s gate-aware resolution -- the exact "a script's own CLI
# default silently diverges from the shared helper" defect class the section above
# this one guards against. The script is `git rm`'d with the retired wiki form, and
# `posts_dir()` has no gate-aware resolution left to diverge from (see
# test_posts_dir_has_no_legacy_fallback above) -- nothing in this repo still owns a
# `--root`/`--state-dir`-style flag whose default could drift from `posts_dir()`, so
# this defect class has no successor to test for.
