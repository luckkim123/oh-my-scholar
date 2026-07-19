"""oms Stop hook: scoped revise-loop guard (R2 #8, stdlib, fail-open).

Blocks a stop attempt ONLY while a revise-<slug>.json marker (T2) is live,
in scope of the session cwd, and no exemption fires — the blunt "never let
the model stop" loop is deliberately out of scope (advancement-plan §6).

Scope: ascend from the payload `cwd` to the NEAREST ancestor (inclusive)
containing `.oms/state/` (first hit only — never look past it). A marker in
that dir is in scope only when it carries `paper_root` and `cwd` equals or
is a descendant of it (hand-written markers missing `paper_root` are out of
scope, never guessed into scope).

Six exemptions (ANY one → that marker never blocks):
  1. not (`active` is True and `status == "live"`)
  2. any strike count >= 3
  3. `round >= max_rounds`
  4. TTL: age_hours = (now_utc - started_at) / 3600 >= `ttl_hours`, OR a
     negative age (clock skew) — skew must never extend the guard
  5. sibling `pilot-<slug>.json` in the same state dir has `gate_status == "abort"`
  6. `stop_blocks >= max(10, 2 * max_rounds)` — durable, cross-turn cap; the
     platform itself force-ends the turn after 8 consecutive blocks per
     stopping cycle, this counter is the secondary safeguard across turns

On block: increments the marker's `stop_blocks` via `atomic_write_json`
FIRST (durable); only on a successful write is the block JSON printed — a
failed increment allows the stop silently (never trade a wedge for a count).

Escape hatch for humans: env OMS_STOP_GUARD in {off,0,false} (never
mentioned in the reason). The revise-end escape IS advertised in the reason
— unlike cite-guard's hidden env hatch, ending the loop and reporting to the
human is the desired behavior here.

R3 #22: env DISABLE_OMS (1/true/on/yes) is the umbrella kill switch shared by
all 5 registered oms hooks, checked first, before OMS_STOP_GUARD and before
stdin -- never mentioned in the block reason.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from oms_atomic import atomic_write_json
from oms_paths import nearest_ancestor


def script_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "scripts" / "oms_state.py")


def nearest_state_dir(cwd: Path):
    """First ancestor of cwd (inclusive) containing `.oms/state/`, or None."""
    root = nearest_ancestor(cwd, lambda c: (c / ".oms" / "state").is_dir())
    return (root / ".oms" / "state") if root is not None else None


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def in_scope(marker: dict, cwd: Path) -> bool:
    root = marker.get("paper_root")
    if not root:
        return False
    root_path = Path(root).resolve()
    return cwd == root_path or root_path in cwd.parents


def is_exempt(marker: dict, state_dir: Path, slug: str) -> bool:
    if marker.get("active") is not True or marker.get("status") != "live":
        return True
    strikes = marker.get("strikes") or {}
    if any(v >= 3 for v in strikes.values()):
        return True
    max_rounds = marker.get("max_rounds", 5)
    if marker.get("round", 0) >= max_rounds:
        return True
    try:
        started = datetime.fromisoformat(marker.get("started_at", ""))
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - started).total_seconds() / 3600
    except (TypeError, ValueError):
        return True  # unparseable started_at -> fail-open (exempt)
    if age_hours >= marker.get("ttl_hours", 6) or age_hours < 0:
        return True
    pilot = load_json(state_dir / f"pilot-{slug}.json")
    if isinstance(pilot, dict) and pilot.get("gate_status") == "abort":
        return True
    cap = max(10, 2 * max_rounds)
    if marker.get("stop_blocks", 0) >= cap:
        return True
    return False


def reason_for(marker: dict, slug: str) -> str:
    strikes = marker.get("strikes") or {}
    strikes_str = ", ".join(f"{k}:{v}" for k, v in strikes.items()) if strikes else "none"
    return (
        f"[oms stop-guard] revise loop for '{slug}' is live "
        f"(round {marker.get('round', 0)}/{marker.get('max_rounds', 5)}, "
        f"open strikes: {strikes_str}): continue the revise-verify loop until PASS or a stop "
        f"condition, or end it explicitly with `python3 {script_path()} revise-end --slug {slug} "
        f"--status stopped` and report to the human. Citation/content defects are NEVER looped — "
        f"escalate those to the human instead."
    )


def block(marker: dict, target: Path, slug: str) -> int:
    try:
        marker["stop_blocks"] = marker.get("stop_blocks", 0) + 1
        atomic_write_json(target, marker)
    except Exception:
        return 0  # never trade a wedge for a count
    print(json.dumps({"decision": "block", "reason": reason_for(marker, slug)}, ensure_ascii=False))
    return 0


def _disable_oms() -> bool:
    try:
        return os.environ.get("DISABLE_OMS", "").strip().lower() in ("1", "true", "on", "yes")
    except Exception:
        return False  # env-read exception -> proceed as if unset


def main() -> int:
    if _disable_oms():
        return 0
    try:
        if os.environ.get("OMS_STOP_GUARD", "").lower() in ("off", "0", "false"):
            return 0
        payload = json.load(sys.stdin)
        cwd_raw = payload.get("cwd")
        if not cwd_raw:
            return 0  # cannot scope -- never guess
        cwd = Path(cwd_raw).resolve()
        state_dir = nearest_state_dir(cwd)
        if state_dir is None:
            return 0
        for path in sorted(state_dir.glob("revise-*.json")):
            try:
                marker = load_json(path)
                if not isinstance(marker, dict):
                    continue  # corrupt/unparseable marker: skip (fail-open per marker)
                if not in_scope(marker, cwd):
                    continue
                # slug from the filename (the `revise-<slug>.json` naming contract, §2.2) is
                # authoritative -- never trust an untrusted/omitted JSON `slug` field for the
                # write target.
                slug = path.stem[len("revise-"):]
                if is_exempt(marker, state_dir, slug):
                    continue
                return block(marker, path, slug)
            except Exception:
                continue  # fail-open per marker
        return 0
    except Exception:
        return 0  # fail-open: 세션을 절대 막지 않음


if __name__ == "__main__":
    sys.exit(main())
