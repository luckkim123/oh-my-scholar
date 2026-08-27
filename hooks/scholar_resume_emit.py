"""oms SessionStart hook: resume advisory (#9) + post-compaction Priority-Context
re-injection (#13) — stdlib, read-only, fail-open.

#9: on any SessionStart (startup/resume/clear/compact), ascend from the payload
`cwd` to the nearest ancestor `.oms/` (a `.oms/state/` dir or an
`.oms/notepad.md` — whichever exists first counts as "the root", first hit
only, never look past it) and summarize any IN-SCOPE non-terminal pilot stage
(`pilot-<slug>.json`, `stage != "terminal"` and `gate_status != "abort"`) plus
its live revise-loop marker (`revise-<slug>.json`, `active is True` and
`status == "live"`), if any — same `paper_root`-containment scoping as the
Stop guard (hooks/scholar_stop_guard.py): a record whose `paper_root` does not
equal-or-contain the session `cwd`, or that omits `paper_root` altogether, is
never guessed into scope.

#13: additionally, ONLY when `source == "compact"`, re-inject the notepad's
`## Priority Context` section (scholar-pilot writes the 3 citation-safety
principles + current GATE position + open unverified-citation list there on
every GATE transition — see skills/scholar-pilot/SKILL.md) verbatim, bounded
to the first 2,000 characters, even when no non-terminal pilot state exists
(a mid-stage session outside pilot still relies on it, if the section exists).
This is implemented as SessionStart(compact), NOT PreCompact: verified
against https://code.claude.com/docs/en/hooks.md (fetched 2026-07-13) —
PreCompact's JSON-output contract has no context-injection channel at all
(only Stop/SubagentStop get `hookSpecificOutput.additionalContext` outside
SessionStart), while SessionStart's documented `source` values include
`compact` and DO support `additionalContext` into the fresh post-compaction
context. One hook file therefore serves both #9 and #13.

Output: `{"hookSpecificOutput": {"hookEventName": "SessionStart",
"additionalContext": "<oms-resume>...</oms-resume>"}}` on stdout, exit 0.
Silence + exit 0 = nothing to advise — the common case (a plain non-paper
session) pays zero injection tax, deliberately unlike the route hook.

Read-only: this hook never writes anything (no atomic-write helper import, no
file writes) — it only reads `.oms/state/*.json` and `.oms/notepad.md`.
Fail-open everywhere: missing cwd, unreadable/corrupt state or notepad
(including notepad-is-a-directory or undecodable bytes) contribute nothing.

R3 #22: env DISABLE_OMS (1/true/on/yes) is the umbrella kill switch shared by
all 5 registered oms hooks, checked first, before stdin -- never advertised
in the injected advisory.
"""
import json
import os
import re
import sys
from pathlib import Path

from oms_paths import nearest_ancestor, notepad_md, state_dir
from oms_paths import root as oms_root

SECTION_RE = re.compile(r"^## Priority Context\s*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
PRIORITY_CONTEXT_CHAR_LIMIT = 2000


def nearest_oms_root(cwd: Path):
    """First ancestor of cwd (inclusive) whose `.oms/` has a `state/` dir or a
    `notepad.md` (existence only — a corrupt/mistyped notepad still counts as
    "found"; it just fails open later when actually read), or None."""
    root = nearest_ancestor(
        cwd,
        lambda c: state_dir(c).is_dir() or notepad_md(c).exists(),
    )
    return oms_root(root) if root is not None else None


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def in_scope(record: dict, cwd: Path) -> bool:
    root = record.get("paper_root")
    if not root:
        return False
    root_path = Path(root).resolve()
    return cwd == root_path or root_path in cwd.parents


def format_pilot_line(slug: str, pilot: dict, revise_marker) -> str:
    stage = pilot.get("stage")
    gate_status = pilot.get("gate_status")
    fail_ids = pilot.get("open_fail_ids") or []
    line = (
        f"{slug} · stage={stage} · gate_status={gate_status} · "
        f"open_fail_ids ({len(fail_ids)}): {', '.join(fail_ids) if fail_ids else 'none'}"
    )
    if revise_marker is not None:
        strikes = revise_marker.get("strikes") or {}
        strikes_str = ", ".join(f"{k}:{v}" for k, v in strikes.items()) if strikes else "none"
        line += (
            f" · round {revise_marker.get('round', 0)}/{revise_marker.get('max_rounds', 5)}, "
            f"strikes: {strikes_str}"
        )
    return line


def collect_pilot_lines(state_dir: Path, cwd: Path):
    lines = []
    if not state_dir.is_dir():
        return lines
    for path in sorted(state_dir.glob("pilot-*.json")):
        try:
            pilot = load_json(path)
            if not isinstance(pilot, dict):
                continue  # corrupt/unparseable: skip (fail-open per record)
            if not in_scope(pilot, cwd):
                continue
            if pilot.get("stage") == "terminal" or pilot.get("gate_status") == "abort":
                continue
            # slug from the filename (the `pilot-<slug>.json` naming contract) is
            # authoritative -- never trust an untrusted/omitted JSON `slug` field.
            slug = path.stem[len("pilot-"):]
            revise = load_json(state_dir / f"revise-{slug}.json")
            revise_marker = None
            if (
                isinstance(revise, dict)
                and in_scope(revise, cwd)
                and revise.get("active") is True
                and revise.get("status") == "live"
            ):
                revise_marker = revise
            lines.append(format_pilot_line(slug, pilot, revise_marker))
        except Exception:
            continue  # fail-open per record
    return lines


def read_notepad(oms_dir: Path):
    path = oms_dir / "notepad.md"
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def priority_context_body(notepad_text):
    if not notepad_text:
        return None
    m = SECTION_RE.search(notepad_text)
    if not m:
        return None
    return m.group(1)[:PRIORITY_CONTEXT_CHAR_LIMIT]


def compose_context(pilot_lines, priority_body):
    parts = []
    if pilot_lines:
        parts.extend(pilot_lines)
        parts.append(
            "Advisory only — GATEs stay human. Resume with scholar-pilot --from <stage>; "
            "discard with oms_state.py write --slug <slug> --gate-status abort."
        )
    if priority_body:
        parts.append("## Priority Context (re-injected after compaction)")
        parts.append(priority_body)
    if not parts:
        return None
    return "<oms-resume>\n" + "\n".join(parts) + "\n</oms-resume>"


def _disable_oms() -> bool:
    try:
        return os.environ.get("DISABLE_OMS", "").strip().lower() in ("1", "true", "on", "yes")
    except Exception:
        return False  # env-read exception -> proceed as if unset


def main() -> int:
    if _disable_oms():
        return 0
    try:
        payload = json.load(sys.stdin)
        cwd_raw = payload.get("cwd")
        if not cwd_raw:
            return 0  # cannot scope -- never guess
        cwd = Path(cwd_raw).resolve()
        oms_dir = nearest_oms_root(cwd)
        if oms_dir is None:
            return 0

        pilot_lines = collect_pilot_lines(oms_dir / "state", cwd)

        priority_body = None
        if payload.get("source") == "compact":
            priority_body = priority_context_body(read_notepad(oms_dir))

        context = compose_context(pilot_lines, priority_body)
        if context is None:
            return 0
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }}, ensure_ascii=False))
        return 0
    except Exception:
        return 0  # fail-open: 세션을 절대 막지 않음


if __name__ == "__main__":
    sys.exit(main())
