"""Tests for the scoped Stop-guard hook (item #8, R2).

핵심 계약: 라이브 revise 마커가 스코프 안에 있고 어떤 예외도 안 걸릴 때만 block.
예외(6종) 중 하나라도 걸리면 침묵·fail-open. cwd 로부터의 ascent 는 nearest-first
(가장 가까운 .oms/state/ 하나만 본다), scope 는 paper_root 포함관계로 판정한다."""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "scholar_stop_guard.py"


def run_hook(payload, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    env.pop("OMS_STOP_GUARD", None) if env_extra is None else None
    proc = subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload) if isinstance(payload, dict) else payload,
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def decision_of(stdout):
    if not stdout.strip():
        return None
    return json.loads(stdout)


def stop_payload(cwd, stop_hook_active=False):
    return {"hook_event_name": "Stop", "cwd": str(cwd), "stop_hook_active": stop_hook_active}


def mk_marker(tmp_path, state_dir=None, slug="s1", **overrides):
    """Writes `.oms/state/revise-<slug>.json` with live defaults, paper_root=str(tmp_path)."""
    state_dir = Path(state_dir) if state_dir else tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": slug,
        "active": True,
        "round": 1,
        "round_id": "round-1",
        "max_rounds": 5,
        "ttl_hours": 6,
        "strikes": {},
        "stop_blocks": 0,
        "paper_root": str(tmp_path),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "live",
    }
    data.update(overrides)
    (state_dir / f"revise-{slug}.json").write_text(json.dumps(data), encoding="utf-8")
    return data


def test_blocks_while_live_marker(tmp_path):
    mk_marker(tmp_path)
    out = decision_of(run_hook(stop_payload(tmp_path)))
    assert out and out["decision"] == "block"
    assert "s1" in out["reason"]
    assert "revise-end" in out["reason"]


def test_silent_without_marker(tmp_path):
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_silent_when_inactive(tmp_path):
    mk_marker(tmp_path, active=False)
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_silent_when_done(tmp_path):
    mk_marker(tmp_path, status="done")
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_third_strike_exempts(tmp_path):
    mk_marker(tmp_path, strikes={"d": 3})
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_max_rounds_exempts(tmp_path):
    mk_marker(tmp_path, round=5, max_rounds=5)
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_ttl_exempts(tmp_path):
    started = (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()
    mk_marker(tmp_path, started_at=started, ttl_hours=6)
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_abort_gate_exempts(tmp_path):
    mk_marker(tmp_path)
    state_dir = tmp_path / ".oms" / "state"
    (state_dir / "pilot-s1.json").write_text(
        json.dumps({"slug": "s1", "gate_status": "abort"}), encoding="utf-8")
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_stop_blocks_cap_scales(tmp_path):
    # cap = max(10, 2*max_rounds) = 16 when max_rounds=8: 10 still blocks, 16 exempts.
    mk_marker(tmp_path, max_rounds=8, stop_blocks=10)
    out = decision_of(run_hook(stop_payload(tmp_path)))
    assert out and out["decision"] == "block"

    mk_marker(tmp_path, max_rounds=8, stop_blocks=16)
    assert run_hook(stop_payload(tmp_path)).strip() == ""

    # defaults (max_rounds=5): cap = max(10, 10) = 10 -> 10 exempts (not a hardcoded 10 that misses this).
    mk_marker(tmp_path, max_rounds=5, stop_blocks=10)
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_ancestor_marker_ignored_when_local_state_exists(tmp_path):
    mk_marker(tmp_path)  # live marker at grandparent .oms/state/
    cwd = tmp_path / "a" / "b"
    (cwd / ".oms" / "state").mkdir(parents=True)  # session cwd has its own EMPTY state dir
    assert run_hook(stop_payload(cwd)).strip() == ""


def test_marker_outside_paper_root_silent(tmp_path):
    mk_marker(tmp_path, paper_root=str(tmp_path / "paperA"))
    cwd = tmp_path / "other"
    cwd.mkdir()
    assert run_hook(stop_payload(cwd)).strip() == ""


def test_marker_missing_paper_root_silent(tmp_path):
    state_dir = tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True)
    data = {
        "slug": "s1", "active": True, "status": "live", "round": 1, "max_rounds": 5,
        "ttl_hours": 6, "strikes": {}, "stop_blocks": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }  # no paper_root — hand-written marker
    (state_dir / "revise-s1.json").write_text(json.dumps(data), encoding="utf-8")
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_future_started_at_exempts(tmp_path):
    started = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    mk_marker(tmp_path, started_at=started)
    assert run_hook(stop_payload(tmp_path)).strip() == ""


def test_block_increments_stop_blocks_durably(tmp_path):
    mk_marker(tmp_path)
    marker_path = tmp_path / ".oms" / "state" / "revise-s1.json"
    run_hook(stop_payload(tmp_path))
    assert json.loads(marker_path.read_text())["stop_blocks"] == 1
    run_hook(stop_payload(tmp_path))
    assert json.loads(marker_path.read_text())["stop_blocks"] == 2


def test_env_escape_hatch(tmp_path):
    mk_marker(tmp_path)
    out = run_hook(stop_payload(tmp_path), env_extra={"OMS_STOP_GUARD": "off"})
    assert out.strip() == ""


def test_reason_never_advertises_env_hatch(tmp_path):
    mk_marker(tmp_path)
    out = decision_of(run_hook(stop_payload(tmp_path)))
    assert "OMS_STOP_GUARD" not in out["reason"]


def test_reason_forbids_citation_looping(tmp_path):
    mk_marker(tmp_path)
    out = decision_of(run_hook(stop_payload(tmp_path)))
    assert "NEVER looped" in out["reason"]
    assert "escalate" in out["reason"]


def test_fail_open_on_bad_input():
    assert run_hook("not json").strip() == ""


def test_fail_open_on_corrupt_marker(tmp_path):
    state_dir = tmp_path / ".oms" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "revise-s1.json").write_text("{broken", encoding="utf-8")
    assert run_hook(stop_payload(tmp_path)).strip() == ""
