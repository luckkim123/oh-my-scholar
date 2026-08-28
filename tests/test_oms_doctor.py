"""Tests for `oms doctor` (R3 #18) — read-only packaging self-diagnosis.

Section functions are exercised directly against tmp_path fixture repos
(importlib idiom, matching test_version_sync.py) rather than through one
giant main(); `test_live_repo_is_healthy` is the "would have caught the
4-way drift" lock over the real repo.
"""
import importlib.util
import json
import re
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "oms_doctor.py"
spec = importlib.util.spec_from_file_location("oms_doctor", SCRIPT)
od = importlib.util.module_from_spec(spec)
spec.loader.exec_module(od)

ROOT = Path(__file__).parent.parent


def _rows(rows, status):
    return [r for r in rows if r["status"] == status]


def _write_plugin(root, version="0.1.0", skills=None, hooks=None):
    (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    plugin = {
        "name": "fixture", "version": version,
        "skills": skills or [], "hooks": hooks or {},
    }
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(plugin), encoding="utf-8")


def test_live_repo_is_healthy():
    """Zero FAIL rows over the real repo — WARNs allowed (the omha card surface,
    absent or mismatched, routes to WARN by design, so this stays green while
    cards/oms.json sits at 0.1.0 pending its own PR)."""
    for rows in (
        od.check_version(ROOT),
        od.check_hooks(ROOT),
        od.check_agents(ROOT),
        od.check_skills(ROOT),
    ):
        fails = _rows(rows, "FAIL")
        assert not fails, fails


def test_version_drift_becomes_fail(tmp_path, monkeypatch):
    monkeypatch.setenv("OMHA_ROOT", str(tmp_path / "no-such-omha"))
    root = tmp_path / "repo"
    _write_plugin(root, version="0.8.0")
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.7.0] — 2026-01-01\n", encoding="utf-8")

    fails = _rows(od.check_version(root), "FAIL")
    assert any("0.8.0" in r["message"] and "0.7.0" in r["message"] for r in fails)


def test_unregistered_hook_file_warns(tmp_path):
    root = tmp_path / "repo"
    _write_plugin(root)
    (root / "hooks").mkdir()
    (root / "hooks" / "extra_hook.py").write_text("x = 1\n", encoding="utf-8")
    (root / "hooks" / "oms_atomic.py").write_text("y = 2\n", encoding="utf-8")

    rows = od.check_hooks(root)
    assert not _rows(rows, "FAIL")
    warns = _rows(rows, "WARN")
    assert any("extra_hook.py" in r["message"] for r in warns)
    assert not any("oms_atomic.py" in r["message"] for r in warns)


def test_missing_registered_hook_fails(tmp_path):
    root = tmp_path / "repo"
    (root / "hooks").mkdir(parents=True)
    _write_plugin(root, hooks={
        "Stop": [{"hooks": [{
            "type": "command", "command": "python3",
            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/missing_hook.py"],
        }]}],
    })

    fails = _rows(od.check_hooks(root), "FAIL")
    assert any("missing_hook.py" in r["message"] for r in fails)


def test_bad_agent_model_fails(tmp_path):
    root = tmp_path / "repo"
    (root / "agents").mkdir(parents=True)
    (root / "agents" / "bad-agent.md").write_text(
        '---\nname: bad-agent\ndescription: "does a thing"\nmodel: gpt4\n---\n\nbody\n',
        encoding="utf-8",
    )

    fails = _rows(od.check_agents(root), "FAIL")
    assert any("bad-agent.md" in r["message"] and "gpt4" in r["message"] for r in fails)


def test_skills_mismatch_fails(tmp_path):
    root = tmp_path / "repo"
    _write_plugin(root)  # skills: [] — nothing registered
    (root / "skills" / "orphan-skill").mkdir(parents=True)
    (root / "skills" / "orphan-skill" / "SKILL.md").write_text("x", encoding="utf-8")

    fails = _rows(od.check_skills(root), "FAIL")
    assert any("orphan-skill" in r["message"] for r in fails)


def test_state_scan_warns_on_terminal_slug(tmp_path):
    oms = tmp_path / ".oms"
    (oms / "state").mkdir(parents=True)
    (oms / "terminal-slug").mkdir()
    (oms / "live-slug").mkdir()
    (oms / "state" / "pilot-terminal-slug.json").write_text(
        json.dumps({"stage": "terminal", "gate_status": "approved"}), encoding="utf-8",
    )
    (oms / "state" / "pilot-live-slug.json").write_text(
        json.dumps({"stage": "draft", "gate_status": "pending"}), encoding="utf-8",
    )

    rows = od.check_state(tmp_path)
    warns = _rows(rows, "WARN")
    assert any("terminal-slug" in r["message"] for r in warns)
    assert not any("live-slug" in r["message"] for r in warns)
    assert not _rows(rows, "FAIL")


def test_state_scan_uses_hq_layers_once_anchored(tmp_path):
    """store-spec §7 stage 2: an anchored paper root has no reason to hold
    `.oms/` content at all, so `check_state` must scan `.hq/work/scholar/`
    and `.hq/runtime/scholar/` — not the legacy tree — once anchored."""
    (tmp_path / ".hq").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".hq" / ".anchor").write_text("id: fixture\n", encoding="utf-8")
    work = tmp_path / ".hq" / "work" / "scholar"
    runtime = tmp_path / ".hq" / "runtime" / "scholar"
    (work / "terminal-slug").mkdir(parents=True)
    (work / "live-slug").mkdir(parents=True)
    runtime.mkdir(parents=True)
    (runtime / "pilot-terminal-slug.json").write_text(
        json.dumps({"stage": "terminal", "gate_status": "approved"}), encoding="utf-8",
    )
    (runtime / "pilot-live-slug.json").write_text(
        json.dumps({"stage": "draft", "gate_status": "pending"}), encoding="utf-8",
    )

    rows = od.check_state(tmp_path)
    warns = _rows(rows, "WARN")
    assert any("terminal-slug" in r["message"] for r in warns)
    assert not any("live-slug" in r["message"] for r in warns)
    assert not _rows(rows, "FAIL")


def test_doctor_read_only():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "atomic_write_json" not in src
    assert "atomic_write_text" not in src
    assert not re.search(r'open\([^)]*["\']w', src)
    assert "write_text(" not in src


def test_exit_codes(tmp_path, monkeypatch):
    monkeypatch.setenv("OMHA_ROOT", str(tmp_path / "no-such-omha"))

    healthy = tmp_path / "healthy"
    _write_plugin(healthy, version="0.1.0")
    (healthy / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0] — 2026-01-01\n", encoding="utf-8")
    assert od.main(["--repo-root", str(healthy)]) == 0

    unhealthy = tmp_path / "unhealthy"
    _write_plugin(unhealthy, version="0.9.0")
    (unhealthy / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0] — 2026-01-01\n", encoding="utf-8")
    assert od.main(["--repo-root", str(unhealthy)]) == 1
