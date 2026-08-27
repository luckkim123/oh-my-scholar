"""oms PreToolUse hook: citation-write interlock (R1 #1, stdlib, fail-open).

The single highest-leverage gap in the advancement plan: nothing structurally
stopped a fabricated `@article{...}` from landing in `.bib` (the PostToolUse
hook only reminds, after the fact). This hook denies, BEFORE the write:
  (a) new `.bib` entry keys with no verification record in the allowlist
      `.oms/state/verified-citations.json` (written by
      `scripts/verify_bib_entry.py --record` after a real Crossref/OpenAlex
      lookup — see that script), and
  (b) new `\\cite{K}` keys in `.tex` with no entry in any sibling `.bib`.
It never auto-fixes and never invents — deny-with-feedback only.
Escape hatch for humans: env OMS_CITE_GUARD=off (deliberately not mentioned
in the deny reason, so the model cannot talk itself past the interlock).
R3 #22: env DISABLE_OMS (1/true/on/yes) is the umbrella kill switch shared by
all 5 registered oms hooks, checked first, before OMS_CITE_GUARD and before
stdin -- same silent-hatch convention (never mentioned in the deny reason).
"""
import json
import os
import re
import sys
from pathlib import Path

from oms_paths import nearest_ancestor, verified_citations_json

WRITE_TOOLS = ("Edit", "Write", "MultiEdit")
ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s{}]+)\s*,")
CITE_RE = re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")


def new_and_old_text(tool_name: str, tool_input: dict):
    if tool_name == "Write":
        return tool_input.get("content", "") or "", None  # old = on-disk file
    if tool_name == "Edit":
        return tool_input.get("new_string", "") or "", tool_input.get("old_string", "") or ""
    edits = tool_input.get("edits", []) or []
    new = "\n".join(e.get("new_string", "") or "" for e in edits)
    old = "\n".join(e.get("old_string", "") or "" for e in edits)
    return new, old


def read_disk(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    except OSError:
        return ""


def entry_keys(text: str) -> set:
    return set(ENTRY_RE.findall(text or ""))


def cite_keys(text: str) -> set:
    keys = set()
    for group in CITE_RE.findall(text or ""):
        keys.update(k.strip() for k in group.split(",") if k.strip())
    return keys


def allowlisted_keys(start: Path, cwd: str) -> set:
    def has_allowlist(base) -> bool:
        return verified_citations_json(base).is_file()

    # start's parents (exclusive of start itself) take priority; cwd is an extra
    # fallback candidate checked last — same order as the original flat list.
    found = nearest_ancestor(start, has_allowlist, include_start=False)
    if found is None and cwd and has_allowlist(Path(cwd)):
        found = Path(cwd)
    if found is None:
        return set()
    f = verified_citations_json(found)
    try:
        return set(json.loads(f.read_text(encoding="utf-8")).get("keys", {}))
    except (OSError, ValueError):
        return set()


def sibling_bib_keys(tex: Path):
    """All entry keys across .bib files in the .tex's dir + parent. None = no .bib found."""
    bibs = []
    for d in (tex.parent, tex.parent.parent):
        try:
            bibs.extend(p for p in d.glob("*.bib") if p.is_file())
        except OSError:
            pass
    if not bibs:
        return None
    keys = set()
    for b in bibs:
        keys |= entry_keys(read_disk(b))
    return keys


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False))
    return 0


def script_path() -> str:
    return str(Path(__file__).resolve().parent.parent / "scripts" / "verify_bib_entry.py")


def check_bib(path: Path, new_text: str, old_text, cwd: str) -> int:
    old = old_text if old_text is not None else read_disk(path)
    fresh = entry_keys(new_text) - entry_keys(old) - entry_keys(read_disk(path))
    if not fresh:
        return 0
    unverified = fresh - allowlisted_keys(path.resolve(), cwd)
    if not unverified:
        return 0
    keys = ", ".join(sorted(unverified))
    return deny(
        f"[oms cite-guard] new .bib entr{'ies' if len(unverified) > 1 else 'y'} without a "
        f"verification record: {keys}. A citation must be verified against the real source "
        f"BEFORE it enters .bib — never fabricate or guess entries. Run: python3 "
        f"{script_path()} --key <key> --doi <doi> --title \"<title>\" --record  "
        f"(records VERIFIED keys into .oms/state/verified-citations.json), or have the human "
        f"explicitly confirm the source. Then retry this write."
    )


def check_tex(path: Path, new_text: str, old_text, cwd: str) -> int:
    old = old_text if old_text is not None else read_disk(path)
    fresh = cite_keys(new_text) - cite_keys(old)
    if not fresh:
        return 0
    bib_keys = sibling_bib_keys(path.resolve())
    if bib_keys is None:
        return 0  # fail-open: nothing to verify against yet
    missing = fresh - bib_keys
    if not missing:
        return 0
    keys = ", ".join(sorted(missing))
    return deny(
        f"[oms cite-guard] \\cite of key(s) with no .bib entry: {keys}. Add the verified "
        f".bib entry first (python3 {script_path()} … --record, human-confirmed), or rewrite "
        f"the claim without the citation — never invent citation keys."
    )


def _disable_oms() -> bool:
    try:
        return os.environ.get("DISABLE_OMS", "").strip().lower() in ("1", "true", "on", "yes")
    except Exception:
        return False  # env-read exception -> proceed as if unset


def main() -> int:
    if _disable_oms():
        return 0
    try:
        if os.environ.get("OMS_CITE_GUARD", "").lower() in ("off", "0", "false"):
            return 0
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {}) or {}
        if tool_name not in WRITE_TOOLS:
            return 0
        raw = tool_input.get("file_path", "") or tool_input.get("path", "")
        if not raw:
            return 0
        cwd = payload.get("cwd", "") or ""
        path = Path(raw)
        if not path.is_absolute() and cwd:
            path = Path(cwd) / path
        new_text, old_text = new_and_old_text(tool_name, tool_input)
        if raw.endswith(".bib"):
            return check_bib(path, new_text, old_text, cwd)
        if raw.endswith(".tex"):
            return check_tex(path, new_text, old_text, cwd)
        return 0
    except Exception:
        return 0  # fail-open: 세션을 절대 막지 않음


if __name__ == "__main__":
    sys.exit(main())
