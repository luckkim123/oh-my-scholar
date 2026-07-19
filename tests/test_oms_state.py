"""R2 #6 — .oms/state/ schema: pilot-<slug>.json written atomically (oms_atomic),
merge semantics, strict enums, read never fails. The substrate for #7–#11/#13."""
import importlib.util, json, sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "oms_state.py"
spec = importlib.util.spec_from_file_location("oms_state", SCRIPT)
oms_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oms_state)


def run(argv, tmp_path):
    return oms_state.main([*argv, "--state-dir", str(tmp_path)])


def read_file(tmp_path, slug):
    return json.loads((tmp_path / f"pilot-{slug}.json").read_text(encoding="utf-8"))


def test_write_creates_schema(tmp_path):
    assert run(["write", "--slug", "s1", "--stage", "draft"], tmp_path) == 0
    d = read_file(tmp_path, "s1")
    assert d["slug"] == "s1" and d["stage"] == "draft"
    assert "updated_at" in d and "T" in d["updated_at"]  # ISO-8601
    # create initializes the full key set — consumers read stable keys
    assert d["gate_status"] is None and d["open_fail_ids"] == []
    assert d["paper_root"]  # recorded cwd (or --paper-root)


def test_write_merges_not_overwrites(tmp_path):
    run(["write", "--slug", "s1", "--stage", "verify", "--open-fail-ids", "d1,d2"], tmp_path)
    run(["write", "--slug", "s1", "--gate-status", "pending"], tmp_path)
    d = read_file(tmp_path, "s1")
    assert d["stage"] == "verify" and d["open_fail_ids"] == ["d1", "d2"]
    assert d["gate_status"] == "pending"


def test_invalid_stage_rejected(tmp_path, capsys):
    assert run(["write", "--slug", "s1", "--stage", "vibing"], tmp_path) == 2
    assert not (tmp_path / "pilot-s1.json").exists()


def test_invalid_gate_status_rejected(tmp_path):
    assert run(["write", "--slug", "s1", "--stage", "draft", "--gate-status", "yolo"], tmp_path) == 2


def test_slug_path_traversal_rejected(tmp_path):
    assert run(["write", "--slug", "../evil", "--stage", "draft"], tmp_path) == 2
    assert run(["write", "--slug", "a/b", "--stage", "draft"], tmp_path) == 2


def test_read_missing_is_empty_not_error(tmp_path, capsys):
    assert run(["read", "--slug", "ghost"], tmp_path) == 0
    assert json.loads(capsys.readouterr().out) == {}


def test_read_all_lists_pilots(tmp_path, capsys):
    run(["write", "--slug", "a", "--stage", "draft"], tmp_path)
    run(["write", "--slug", "b", "--stage", "verify"], tmp_path)
    capsys.readouterr()
    assert run(["read"], tmp_path) == 0
    slugs = {d["slug"] for d in json.loads(capsys.readouterr().out)}
    assert slugs == {"a", "b"}


def test_write_goes_through_oms_atomic():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "atomic_write_json" in src
    assert "import requests" not in src  # stdlib only


# R2 #7 — revise marker + strike/round ledger


def test_revise_start_creates_marker(tmp_path, capsys):
    assert run(["revise-start", "--slug", "s1", "--max-rounds", "3"], tmp_path) == 0
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["active"] is True and d["round"] == 0 and d["strikes"] == {}
    assert d["max_rounds"] == 3 and d["status"] == "live" and d["stop_blocks"] == 0


def test_revise_round_increments_and_mints_round_id(tmp_path, capsys):
    run(["revise-start", "--slug", "s1"], tmp_path)
    capsys.readouterr()
    run(["revise-round", "--slug", "s1"], tmp_path)
    r1 = json.loads(capsys.readouterr().out)
    run(["revise-round", "--slug", "s1"], tmp_path)
    r2 = json.loads(capsys.readouterr().out)
    assert (r1["round"], r2["round"]) == (1, 2)
    assert r1["round_id"] != r2["round_id"] and len(r1["round_id"]) >= 32


def test_revise_round_flags_exceeded(tmp_path, capsys):
    run(["revise-start", "--slug", "s1", "--max-rounds", "1"], tmp_path)
    run(["revise-round", "--slug", "s1"], tmp_path)
    capsys.readouterr()
    run(["revise-round", "--slug", "s1"], tmp_path)
    assert json.loads(capsys.readouterr().out).get("exceeded") is True


def test_strike_counts_to_three(tmp_path, capsys):
    run(["revise-start", "--slug", "s1"], tmp_path)
    capsys.readouterr()
    for expected in (False, False, True):
        run(["strike", "--slug", "s1", "--defect-id", "dangling-ref"], tmp_path)
        assert json.loads(capsys.readouterr().out)["third_strike"] is expected


def test_revise_end_deactivates(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    run(["revise-end", "--slug", "s1", "--status", "stopped"], tmp_path)
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["active"] is False and d["status"] == "stopped"


def test_ledger_verbs_require_started_loop(tmp_path):
    assert run(["strike", "--slug", "ghost", "--defect-id", "d"], tmp_path) == 2
    assert run(["revise-round", "--slug", "ghost"], tmp_path) == 2


def test_revise_start_idempotent_on_live_marker(tmp_path, capsys):
    run(["revise-start", "--slug", "s1"], tmp_path)
    run(["revise-round", "--slug", "s1"], tmp_path)
    run(["strike", "--slug", "s1", "--defect-id", "d"], tmp_path)
    capsys.readouterr()
    assert run(["revise-start", "--slug", "s1"], tmp_path) == 0
    assert json.loads(capsys.readouterr().out).get("resumed") is True
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["round"] == 1 and d["strikes"] == {"d": 1}  # never-wedge counters preserved


def test_revise_start_force_restart_resets(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    run(["revise-round", "--slug", "s1"], tmp_path)
    run(["revise-start", "--slug", "s1", "--force-restart"], tmp_path)
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["round"] == 0 and d["strikes"] == {}


def test_revise_start_rejects_insane_bounds(tmp_path):
    assert run(["revise-start", "--slug", "s1", "--max-rounds", "999"], tmp_path) == 2
    assert run(["revise-start", "--slug", "s1", "--ttl-hours", "0"], tmp_path) == 2
    assert not (tmp_path / "revise-s1.json").exists()


def test_strike_defect_id_rejects_path_chars(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    before = (tmp_path / "revise-s1.json").read_text()
    assert run(["strike", "--slug", "s1", "--defect-id", "../x"], tmp_path) == 2
    assert run(["strike", "--slug", "s1", "--defect-id", "a/b"], tmp_path) == 2
    assert (tmp_path / "revise-s1.json").read_text() == before  # no marker mutation


# --- slug validation guard, exercised for every remaining verb (only `write`'s
# own slug check was covered before) — a malformed slug must be refused and no
# state file may be written anywhere, including the tmp_path's parent.


@pytest.mark.parametrize(
    "argv",
    [
        ["read", "--slug", "../evil"],
        ["revise-start", "--slug", "../evil"],
        ["revise-round", "--slug", "../evil"],
        ["strike", "--slug", "../evil", "--defect-id", "d"],
        ["revise-end", "--slug", "../evil"],
    ],
)
def test_slug_path_traversal_rejected_for_every_verb(argv, tmp_path, capsys):
    rc = run(argv, tmp_path)
    err = capsys.readouterr().err
    assert rc == 2 and "must match" in err
    assert not list(tmp_path.glob("*.json"))
    assert not list(tmp_path.parent.glob("*evil*"))


def test_write_requires_stage_on_first_creation(tmp_path):
    assert run(["write", "--slug", "s1"], tmp_path) == 2
    assert not (tmp_path / "pilot-s1.json").exists()


def test_revise_end_invalid_status_rejected(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    before = (tmp_path / "revise-s1.json").read_text()
    assert run(["revise-end", "--slug", "s1", "--status", "vibing"], tmp_path) == 2
    assert (tmp_path / "revise-s1.json").read_text() == before  # no mutation


def test_revise_end_requires_started_loop(tmp_path):
    assert run(["revise-end", "--slug", "ghost"], tmp_path) == 2
