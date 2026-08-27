"""R2 #6 — .oms/state/ pipeline mechanism state.

This CLI is the ONLY writer of `.oms/state/pilot-*.json` / `revise-*.json`
(the verified-citations allowlist stays owned by `verify_bib_entry.py`).
All writes go through `atomic_write_json` (crash-safe, same-volume rename).
It never touches `.tex`/`.bib`/notepad — those stay outside this file's
responsibility. Schema documented in `references/output-layout.md` §2.2.
"""
import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from oms_atomic import atomic_write_json  # noqa: E402
from oms_paths import state_dir_default_str  # noqa: E402

STAGES = (
    "research", "deepen", "ideate", "outline", "draft",
    "inspect", "verify", "revise", "submission", "terminal",
)
GATE_STATUSES = ("pending", "approved", "revise", "abort")
REVISE_STATUSES = ("done", "stopped", "abort")
MAX_ROUNDS_RANGE = (1, 20)
TTL_HOURS_RANGE = (1, 168)
SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def load(state_dir, name) -> dict:
    """Read `<name>.json` from `state_dir`. Missing/unparseable → {} (read never fails)."""
    target = Path(state_dir) / f"{name}.json"
    if not target.is_file():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_pilot(state_dir, slug, **fields) -> dict:
    """Merge-write `pilot-<slug>.json`: existing fields not passed are preserved.
    On create, initializes the full key set so downstream consumers read stable keys."""
    target = Path(state_dir) / f"pilot-{slug}.json"
    data = load(state_dir, f"pilot-{slug}")
    if not data:
        data = {
            "slug": slug,
            "stage": None,
            "gate_status": None,
            "open_fail_ids": [],
            "paper_root": None,
            "updated_at": None,
        }
    data.update({k: v for k, v in fields.items() if v is not None})
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write_json(target, data)
    return data


def _revise_target(state_dir, slug) -> Path:
    return Path(state_dir) / f"revise-{slug}.json"


def _err(message) -> int:
    """Print an error to stderr and return exit code 2 (never raises SystemExit —
    a session-facing CLI must let the caller inspect the return code)."""
    print(f"error: {message}", file=sys.stderr)
    return 2


def _valid_slug(slug) -> bool:
    return bool(SLUG_RE.match(slug))


def _slug_error(value, flag="--slug") -> str:
    """Shared error string for any {slug} arg failing to match `SLUG_RE`."""
    return f"{flag} {value!r} must match {SLUG_RE.pattern} (no path separators)"


def _cmd_write(args) -> int:
    if not _valid_slug(args.slug):
        return _err(_slug_error(args.slug))
    existing = load(args.state_dir, f"pilot-{args.slug}")
    if not existing and args.stage is None:
        return _err("--stage is required when creating a new state (no existing pilot file)")
    if args.stage is not None and args.stage not in STAGES:
        return _err(f"--stage must be one of {STAGES}")
    if args.gate_status is not None and args.gate_status not in GATE_STATUSES:
        return _err(f"--gate-status must be one of {GATE_STATUSES}")

    fields = {}
    if args.stage is not None:
        fields["stage"] = args.stage
    if args.gate_status is not None:
        fields["gate_status"] = args.gate_status
    if args.open_fail_ids is not None:
        fields["open_fail_ids"] = [x for x in args.open_fail_ids.split(",") if x]
    # paper_root: preserved on merge unless explicitly overridden; resolved cwd on create.
    if args.paper_root is not None:
        fields["paper_root"] = args.paper_root
    elif not existing:
        fields["paper_root"] = str(Path.cwd())

    data = write_pilot(args.state_dir, args.slug, **fields)
    print(json.dumps(data))
    return 0


def _cmd_read(args) -> int:
    state_dir = Path(args.state_dir)
    if args.slug is not None:
        if not _valid_slug(args.slug):
            return _err(_slug_error(args.slug))
        print(json.dumps(load(args.state_dir, f"pilot-{args.slug}")))
        return 0
    results = []
    if state_dir.is_dir():
        for f in sorted(state_dir.glob("pilot-*.json")):
            results.append(load(args.state_dir, f.stem))
    print(json.dumps(results))
    return 0


def _cmd_revise_start(args) -> int:
    if not _valid_slug(args.slug):
        return _err(_slug_error(args.slug))
    if not (MAX_ROUNDS_RANGE[0] <= args.max_rounds <= MAX_ROUNDS_RANGE[1]):
        return _err(f"--max-rounds must be between {MAX_ROUNDS_RANGE[0]} and {MAX_ROUNDS_RANGE[1]}")
    if not (TTL_HOURS_RANGE[0] <= args.ttl_hours <= TTL_HOURS_RANGE[1]):
        return _err(f"--ttl-hours must be between {TTL_HOURS_RANGE[0]} and {TTL_HOURS_RANGE[1]}")

    existing = load(args.state_dir, f"revise-{args.slug}")
    # Idempotent resume: a crash/compaction resume must never zero the never-wedge
    # counters (round/strikes/stop_blocks) or extend the TTL clock (started_at).
    if existing and existing.get("active") and existing.get("status") == "live" and not args.force_restart:
        print(json.dumps({**existing, "resumed": True}))
        return 0

    data = {
        "slug": args.slug,
        "active": True,
        "round": 0,
        "round_id": None,
        "max_rounds": args.max_rounds,
        "ttl_hours": args.ttl_hours,
        "strikes": {},
        "stop_blocks": 0,
        "paper_root": str(Path.cwd()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "live",
    }
    atomic_write_json(_revise_target(args.state_dir, args.slug), data)
    print(json.dumps(data))
    return 0


def _cmd_revise_round(args) -> int:
    if not _valid_slug(args.slug):
        return _err(_slug_error(args.slug))
    data = load(args.state_dir, f"revise-{args.slug}")
    if not data:
        return _err(f"no revise marker for slug {args.slug!r} — run revise-start first")

    data["round"] += 1
    data["round_id"] = str(uuid.uuid4())
    atomic_write_json(_revise_target(args.state_dir, args.slug), data)

    out = {"round": data["round"], "max_rounds": data["max_rounds"], "round_id": data["round_id"]}
    if data["round"] > data["max_rounds"]:
        out["exceeded"] = True  # the CLI never blocks; the SKILL decides to stop
    print(json.dumps(out))
    return 0


def _cmd_strike(args) -> int:
    if not _valid_slug(args.slug):
        return _err(_slug_error(args.slug))
    if not _valid_slug(args.defect_id):
        return _err(_slug_error(args.defect_id, flag="--defect-id"))
    data = load(args.state_dir, f"revise-{args.slug}")
    if not data:
        return _err(f"no revise marker for slug {args.slug!r} — run revise-start first")

    count = data["strikes"].get(args.defect_id, 0) + 1
    data["strikes"][args.defect_id] = count
    atomic_write_json(_revise_target(args.state_dir, args.slug), data)
    print(json.dumps({"defect_id": args.defect_id, "count": count, "third_strike": count >= 3}))
    return 0


def _cmd_revise_end(args) -> int:
    if not _valid_slug(args.slug):
        return _err(_slug_error(args.slug))
    if args.status not in REVISE_STATUSES:
        return _err(f"--status must be one of {REVISE_STATUSES}")
    data = load(args.state_dir, f"revise-{args.slug}")
    if not data:
        return _err(f"no revise marker for slug {args.slug!r} — run revise-start first")

    data["active"] = False
    data["status"] = args.status
    atomic_write_json(_revise_target(args.state_dir, args.slug), data)
    print(json.dumps(data))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="oms .oms/state/ pipeline mechanism state CLI.")
    sub = parser.add_subparsers(dest="verb", required=True)

    p_write = sub.add_parser("write")
    p_write.add_argument("--slug", required=True)
    p_write.add_argument("--stage", default=None)
    p_write.add_argument("--gate-status", default=None)
    p_write.add_argument("--open-fail-ids", default=None)
    p_write.add_argument("--paper-root", default=None)
    p_write.add_argument("--state-dir", default=state_dir_default_str())

    p_read = sub.add_parser("read")
    p_read.add_argument("--slug", default=None)
    p_read.add_argument("--state-dir", default=state_dir_default_str())

    p_revise_start = sub.add_parser("revise-start")
    p_revise_start.add_argument("--slug", required=True)
    p_revise_start.add_argument("--max-rounds", type=int, default=5)
    p_revise_start.add_argument("--ttl-hours", type=int, default=6)
    p_revise_start.add_argument("--force-restart", action="store_true")
    p_revise_start.add_argument("--state-dir", default=state_dir_default_str())

    p_revise_round = sub.add_parser("revise-round")
    p_revise_round.add_argument("--slug", required=True)
    p_revise_round.add_argument("--state-dir", default=state_dir_default_str())

    p_strike = sub.add_parser("strike")
    p_strike.add_argument("--slug", required=True)
    p_strike.add_argument("--defect-id", required=True)
    p_strike.add_argument("--state-dir", default=state_dir_default_str())

    p_revise_end = sub.add_parser("revise-end")
    p_revise_end.add_argument("--slug", required=True)
    p_revise_end.add_argument("--status", default="done")
    p_revise_end.add_argument("--state-dir", default=state_dir_default_str())

    args = parser.parse_args(argv)

    if args.verb == "write":
        return _cmd_write(args)
    if args.verb == "read":
        return _cmd_read(args)
    if args.verb == "revise-start":
        return _cmd_revise_start(args)
    if args.verb == "revise-round":
        return _cmd_revise_round(args)
    if args.verb == "strike":
        return _cmd_strike(args)
    return _cmd_revise_end(args)


if __name__ == "__main__":
    sys.exit(main())
