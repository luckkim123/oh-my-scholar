"""R2 #6 — .oms/state/ schema: pilot-<slug>.json written atomically (oms_atomic),
merge semantics, strict enums, read never fails. The substrate for #7–#11/#13."""
import importlib.util, json, sys
from pathlib import Path

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
