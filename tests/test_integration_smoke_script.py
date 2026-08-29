"""Tests for `scripts/integration_smoke.py`'s own pure functions (Tier 1,
CI-safe) — transcript-dispatch parsing, scaffold-assertion, preflight
fail-fast. Never invokes `claude`, never touches network. Same importlib
idiom as `test_oms_doctor.py`/`test_version_sync.py`.

Does NOT re-cover the existing wiring-integrity suite (`test_plugin_integrity.py`,
`test_agent_integrity.py`, `oms_doctor.py`) — `run_preflight` here is a thin
wrapper reusing those checks in-process, not a reimplementation.
"""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "integration_smoke.py"
spec = importlib.util.spec_from_file_location("integration_smoke", SCRIPT)
ism = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ism)

SUBAGENT = "oh-my-scholar:scholar-planner"


def _task_event(subagent_type):
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "dispatching..."},
                {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "Task",
                    "input": {"subagent_type": subagent_type, "description": "run it"},
                },
            ],
        },
    }


def _text_event(text):
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }


# ------------------------------------------------------------ find_task_dispatch
def test_find_task_dispatch_found():
    lines = [
        _text_event("starting scholar-init"),
        _task_event(SUBAGENT),
        _text_event("done"),
    ]
    found = ism.find_task_dispatch(lines, SUBAGENT)
    assert found is not None
    assert found["input"]["subagent_type"] == SUBAGENT


def test_find_task_dispatch_missing():
    lines = [
        _text_event("starting scholar-init"),
        _text_event("done, no dispatch here"),
    ]
    assert ism.find_task_dispatch(lines, SUBAGENT) is None


# ------------------------------------------------------------------ check_scaffold
def _write_scaffold(root, slug, venue):
    slug_dir = root / slug
    (slug_dir / "sections").mkdir(parents=True)
    (slug_dir / "figures").mkdir(parents=True)
    (slug_dir / "refs").mkdir(parents=True)
    (slug_dir / "data").mkdir(parents=True)
    (slug_dir / "meta.md").write_text("# meta\n\nsome content\n", encoding="utf-8")
    (slug_dir / "refs" / "paper.bib").write_text("", encoding="utf-8")
    (slug_dir / "preamble.tex").write_text("", encoding="utf-8")
    (slug_dir / f"{slug}.tex").write_text("", encoding="utf-8")

    venues_dir = root / ".oms" / "venues"
    venues_dir.mkdir(parents=True)
    (venues_dir / f"{venue}.yaml").write_text("key: generic\n", encoding="utf-8")

    (root / ".gitignore").write_text(".oms/\noutputs/*\n", encoding="utf-8")


def test_check_scaffold_pass(tmp_path):
    _write_scaffold(tmp_path, "oms-smoke-test", "generic")
    rows = ism.check_scaffold(tmp_path, "oms-smoke-test", "generic")
    assert not [r for r in rows if r["status"] == "FAIL"]


def test_check_scaffold_missing_file_fails(tmp_path):
    _write_scaffold(tmp_path, "oms-smoke-test", "generic")
    (tmp_path / "oms-smoke-test" / "refs" / "paper.bib").unlink()

    rows = ism.check_scaffold(tmp_path, "oms-smoke-test", "generic")
    fails = [r for r in rows if r["status"] == "FAIL"]
    assert len(fails) == 1
    assert "refs/paper.bib" in fails[0]["message"]


# test_check_scaffold_history_dir_present_fails removed (r7, 2026-08-30): it asserted
# check_scaffold() FAILs when a post-store `history/` category directory was created
# locally. scholar-init no longer scaffolds ANY `.hq/community/posts/` shape — `hq post`
# creates the store lazily on first write — so check_scaffold() dropped the whole
# wiki_dir/REQUIRED_WIKI_CATEGORIES check block it depended on (integration_smoke.py).
# There is no longer a "wrong directory was created" failure mode to test for.


# ------------------------------------------------------------------ run_preflight
def _write_broken_plugin(root):
    (root / ".claude-plugin").mkdir(parents=True)
    plugin = {"name": "fixture", "version": "0.9.0", "skills": [], "hooks": {}}
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(plugin), encoding="utf-8")
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0] - 2026-01-01\n", encoding="utf-8")


def test_preflight_aborts_before_invoking_claude(tmp_path, monkeypatch):
    monkeypatch.setenv("OMHA_ROOT", str(tmp_path / "no-such-omha"))

    real_run = ism.subprocess.run

    def _boom_if_claude(cmd, *args, **kwargs):
        # run_preflight legitimately shells out to `git` (via sync_version's
        # tag lookup) -- only invoking the `claude` binary itself is forbidden
        # here, proving preflight never reaches the actual smoke-test call site.
        if isinstance(cmd, (list, tuple)) and any("claude" == str(c) for c in cmd):
            raise AssertionError("claude must not be invoked during preflight")
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(ism.subprocess, "run", _boom_if_claude)

    root = tmp_path / "broken-repo"
    _write_broken_plugin(root)

    rows = ism.run_preflight(root)
    fails = [r for r in rows if r["status"] == "FAIL"]
    assert fails  # version drift (0.9.0 vs 0.1.0) must surface as FAIL
