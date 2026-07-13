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
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from oms_atomic import atomic_write_json  # noqa: E402

STAGES = (
    "research", "deepen", "ideate", "outline", "draft",
    "inspect", "verify", "revise", "submission", "terminal",
)
GATE_STATUSES = ("pending", "approved", "revise", "abort")
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


def _err(message) -> int:
    """Print an error to stderr and return exit code 2 (never raises SystemExit —
    a session-facing CLI must let the caller inspect the return code)."""
    print(f"error: {message}", file=sys.stderr)
    return 2


def _valid_slug(slug) -> bool:
    return bool(SLUG_RE.match(slug))


def _cmd_write(args) -> int:
    if not _valid_slug(args.slug):
        return _err(f"--slug {args.slug!r} must match {SLUG_RE.pattern} (no path separators)")
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
            return _err(f"--slug {args.slug!r} must match {SLUG_RE.pattern} (no path separators)")
        print(json.dumps(load(args.state_dir, f"pilot-{args.slug}")))
        return 0
    results = []
    if state_dir.is_dir():
        for f in sorted(state_dir.glob("pilot-*.json")):
            results.append(load(args.state_dir, f.stem))
    print(json.dumps(results))
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
    p_write.add_argument("--state-dir", default="./.oms/state")

    p_read = sub.add_parser("read")
    p_read.add_argument("--slug", default=None)
    p_read.add_argument("--state-dir", default="./.oms/state")

    args = parser.parse_args(argv)

    if args.verb == "write":
        return _cmd_write(args)
    return _cmd_read(args)


if __name__ == "__main__":
    sys.exit(main())
