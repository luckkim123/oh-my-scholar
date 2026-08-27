"""Manual, developer-run plugin-reload integration smoke test (Tier 2).

Closes the one edge the 537-function structural pytest suite never
exercises: skill invocation -> `Task(subagent_type=...)` dispatch -> real
subagent turn -> `.oms/<slug>/` disk artifact. `scholar-init` is the target
stage — the cheapest stage that still crosses every hop of that edge
(one skill, one `Task` dispatch, one gated disk write), needs no network
(`--venue generic` per scholar-init Step 4's own no-network fallback).

Never invoked by CI, a git hook, or any other automated trigger — this
script calls a real `claude -p` and spends real API budget (one sonnet-tier
orchestrating turn + one opus-tier `scholar-planner` dispatch, a few cents
per run). Requires either an interactively-logged-in `claude` CLI session
or `ANTHROPIC_API_KEY` in the environment.

The prompt this script sends auto-approves GATE 0/GATE 1 ("no human
present, do not pause to ask") — a deliberate, narrowly-scoped override of
the real GATE-1 human-approval UX, used only by this script, never a
general "auto mode" for real paper work. A PASS here means the
dispatch->artifact *mechanism* is real, not that the human-approval gate
itself was exercised.

`--deep` additionally chains a `scholar-research` call in the same
workspace after `scholar-init` passes (heavier, network-dependent citation
lookups) — off by default.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oms_doctor  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from oms_paths import GITIGNORE_ENTRY, venue_yaml  # noqa: E402
from oms_paths import wiki_dir as oms_wiki_dir

REQUIRED_WIKI_CATEGORIES = ("convention", "pattern", "decision", "reference")


# ------------------------------------------------------------ transcript parsing
def find_task_dispatch(transcript_lines, subagent_name):
    """Scan parsed `stream-json` transcript events for a `Task` tool_use
    block whose `input.subagent_type` matches `subagent_name`. Returns the
    matching tool_use block dict, or None if never found."""
    for line in transcript_lines:
        content = line.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Task"
                and block.get("input", {}).get("subagent_type") == subagent_name
            ):
                return block
    return None


# ------------------------------------------------------------------ check_scaffold
def check_scaffold(workspace_root, slug, venue) -> list:
    """Assert the exact artifact set scholar-init Step 6 promises landed on
    disk (references/output-layout.md §2). Same {"status", "message"} row
    shape as oms_doctor._row for a consistent PASS/FAIL reading experience."""
    root = Path(workspace_root)
    slug_dir = root / slug
    rows = []

    meta = slug_dir / "meta.md"
    if not meta.is_file() or not meta.read_text(encoding="utf-8").strip():
        rows.append(oms_doctor._row("FAIL", f"{slug}/meta.md missing or empty"))

    required_paths = [
        slug_dir / "sections",
        slug_dir / "figures",
        slug_dir / "refs" / "paper.bib",
        slug_dir / "data",
        slug_dir / "preamble.tex",
        slug_dir / f"{slug}.tex",
    ]
    for path in required_paths:
        if not path.exists():
            rel = path.relative_to(root)
            rows.append(oms_doctor._row("FAIL", f"missing required path: {rel}"))

    wiki_dir = oms_wiki_dir(root)
    for cat in REQUIRED_WIKI_CATEGORIES:
        if not (wiki_dir / cat).is_dir():
            rows.append(oms_doctor._row("FAIL", f"missing required path: .oms/wiki/{cat}"))
    if (wiki_dir / "history").exists():
        rows.append(oms_doctor._row("FAIL", ".oms/wiki/history/ must not be created locally (Step 6)"))

    venue_file = venue_yaml(root, venue)
    if not venue_file.is_file():
        rows.append(oms_doctor._row("FAIL", f"missing required path: .oms/venues/{venue}.yaml"))
    elif not re.search(r"^key:", venue_file.read_text(encoding="utf-8"), re.MULTILINE):
        rows.append(oms_doctor._row("FAIL", f"{venue_file.relative_to(root)} has no 'key:' line"))

    gitignore = root / ".gitignore"
    if not gitignore.is_file() or GITIGNORE_ENTRY not in gitignore.read_text(encoding="utf-8"):
        rows.append(oms_doctor._row("FAIL", ".gitignore missing '.oms/' entry"))

    if not rows:
        rows.append(oms_doctor._row("PASS", f"{slug}/ scaffold matches output-layout.md §2"))
    return rows


# -------------------------------------------------------------------- preflight
def run_preflight(repo_root) -> list:
    """Read-only wiring check reused from `oms_doctor.py`, in-process. Any
    FAIL row here means the caller must not proceed to invoking `claude` —
    zero API spend on a broken wiring surface."""
    repo_root = Path(repo_root)
    rows = []
    rows += oms_doctor.check_version(repo_root)
    rows += oms_doctor.check_hooks(repo_root)
    rows += oms_doctor.check_agents(repo_root)
    rows += oms_doctor.check_skills(repo_root)
    return rows


# ---------------------------------------------------------------------- prompt
SMOKE_PROMPT_TEMPLATE = (
    "Unattended integration smoke test, no human present. "
    "/scholar-init — folder name: {slug}, venue: {venue}, topic: {topic}. "
    "This is disposable test data. Do not pause at GATE 0/GATE 1 to ask — "
    "auto-approve and proceed to write in this same turn. Do not skip the "
    "scholar-planner dispatch."
)


def _report(name, rows) -> bool:
    """Print `[name] STATUS: message` rows, return True iff no FAIL."""
    print(f"[{name}]")
    ok = True
    for row in rows:
        print(f"  {row['status']}: {row['message']}")
        if row["status"] == "FAIL":
            ok = False
    return ok


def _run_claude(prompt, plugin_dir, model, workspace, transcript_path):
    cmd = [
        "claude", "-p", prompt,
        "--plugin-dir", str(plugin_dir),
        "--bare",
        "--model", model,
        "--permission-mode", "acceptEdits",
        "--output-format", "stream-json",
        "--verbose",
    ]
    with open(transcript_path, "w", encoding="utf-8") as out:
        subprocess.run(cmd, cwd=workspace, stdout=out, check=False)


def _read_transcript(transcript_path):
    lines = []
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except ValueError:
                continue
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Manual plugin-reload integration smoke test (Tier 2, never run by CI)."
    )
    ap.add_argument(
        "--bare", action="store_true", default=True,
        help="always on (not user-toggleable) -- excludes real ~/.claude hooks/MCP/plugins/CLAUDE.md",
    )
    ap.add_argument("--topic", default="OMS integration smoke test")
    ap.add_argument("--slug", default="oms-smoke-test")
    ap.add_argument("--venue", default="generic")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--plugin-dir", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--keep", action="store_true", help="skip cleanup of the tmp workspace")
    ap.add_argument("--deep", action="store_true", help="also chain scholar-research after init")
    args = ap.parse_args(argv)

    plugin_dir = Path(args.plugin_dir).resolve()

    preflight_rows = run_preflight(plugin_dir)
    if not _report("preflight", preflight_rows):
        print("preflight FAIL — aborting before invoking claude", file=sys.stderr)
        return 2

    workspace = Path(tempfile.mkdtemp(prefix="oms-smoke-"))
    print(f"workspace: {workspace}")
    try:
        prompt = SMOKE_PROMPT_TEMPLATE.format(slug=args.slug, venue=args.venue, topic=args.topic)
        transcript_path = workspace / "transcript.jsonl"
        _run_claude(prompt, plugin_dir, args.model, workspace, transcript_path)

        transcript_lines = _read_transcript(transcript_path)
        dispatch = find_task_dispatch(transcript_lines, "oh-my-scholar:scholar-planner")
        dispatch_rows = (
            [oms_doctor._row("PASS", "Task dispatch to oh-my-scholar:scholar-planner found")]
            if dispatch is not None
            else [oms_doctor._row("FAIL", f"no Task dispatch to scholar-planner in {transcript_path}")]
        )
        ok = _report("dispatch", dispatch_rows)

        scaffold_rows = check_scaffold(workspace, args.slug, args.venue)
        ok = _report("scaffold", scaffold_rows) and ok

        if args.deep and ok:
            deep_prompt = (
                "Unattended integration smoke test, no human present. "
                f"/scholar-research — folder name: {args.slug}, venue: {args.venue}. "
                "This is disposable test data. Do not pause at GATE 0/GATE 1 to ask — "
                "auto-approve and proceed in this same turn. Do not skip the "
                "scholar-researcher dispatch."
            )
            deep_transcript_path = workspace / "transcript-deep.jsonl"
            _run_claude(deep_prompt, plugin_dir, args.model, workspace, deep_transcript_path)
            deep_lines = _read_transcript(deep_transcript_path)
            deep_dispatch = find_task_dispatch(deep_lines, "oh-my-scholar:scholar-researcher")
            deep_rows = (
                [oms_doctor._row("PASS", "Task dispatch to oh-my-scholar:scholar-researcher found")]
                if deep_dispatch is not None
                else [oms_doctor._row("FAIL", f"no Task dispatch to scholar-researcher in {deep_transcript_path}")]
            )
            ok = _report("deep-dispatch", deep_rows) and ok

        return 0 if ok else 1
    finally:
        if not args.keep:
            shutil.rmtree(workspace, ignore_errors=True)
        else:
            print(f"workspace kept: {workspace}")


if __name__ == "__main__":
    sys.exit(main())
