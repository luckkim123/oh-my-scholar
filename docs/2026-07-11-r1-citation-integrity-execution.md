# R1 — Citation-Integrity Enforcement (P0 #0–#5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote oms's citation invariant from prose to mechanism: a PreToolUse write interlock, a mechanical DOI/retraction pre-gate, claim-faithfulness + uncited-claim checks in verify, quote-anchored research notes, a `[MATERIAL GAP]` drafter token, and the measured hallucination evidence in README — release as v0.6.0.

**Architecture:** One new PreToolUse hook (`hooks/scholar_cite_guard.py`, stdlib, fail-open) denies unverified new `.bib` entries and dangling `\cite` keys; one new stdlib script (`scripts/verify_bib_entry.py`) verifies entries against Crossref (+Retraction Watch data) with OpenAlex fallback and records VERIFIED keys into an allowlist (`.oms/state/verified-citations.json`, written via `oms_atomic`); the hook reads that allowlist. Items #3/#4/#5 are prompt-contract edits to agents/skills with literal-substring regression tests (repo idiom). Spec = `docs/2026-07-11-oms-advancement-plan.md` §5 P0.

**Tech Stack:** Python 3 stdlib only (json, re, urllib, difflib, pathlib), pytest, markdown prompt contracts.

## Global Constraints

- stdlib only — no third-party imports in hooks/ or scripts/ (repo invariant).
- All hooks fail-open: any parse/IO error → exit 0, no output, session never blocked.
- The interlock NEVER auto-fixes and NEVER invents — it only denies with instructions; the script NEVER writes `.bib` (allowlist state file only).
- Citation auto-fix and embeddings remain forbidden (oms 3 principles); external APIs (Crossref/OpenAlex) are deterministic lookups, allowed.
- No personal values hardcoded (no email); polite-pool mailto only via `OMS_CROSSREF_MAILTO` env.
- Prompt-contract edits are surgical: keep the surrounding text and heading numbering intact; English text (post-1940c6 corpus).
- Every task ends with `python3 -m pytest tests/ -q` green (T0 makes the suite green first; later tasks keep it green).
- Worktree: `/Users/kimseungmin/oh-my-scholar/.claude/worktrees/oms-r1`, branch `feat/r1-citation-integrity`. Commit per task, message style `feat(oms): …` / `fix(oms): …` matching git log.

---

### Task 0: Repair pre-existing test↔doc English drift (22 failures)

**Files:**
- Modify: failing assertions only, in `tests/test_scholar_init_skill.py`, `tests/test_verify_writing_warn.py`, `tests/test_abstract_quantitative_guard.py`, `tests/test_writing_craft_card.py`, `tests/test_thesis_structure.py`, `tests/test_planner_rhetorical_axis.py`, `tests/test_inspector_writing_lenses.py`, `tests/test_ssot_priority_and_sync.py`

**Interfaces:** none (test-only repair; no product files change).

Background: commit `1940cc6` translated reference cards/skills to English; 22 regression tests still assert Korean (or wrong-synonym English) literals, e.g. `re.search(r"장식|ornamental", body)` fails because `writing-craft.md` now says "decorative".

- [ ] **Step 1: Enumerate failures** — Run `python3 -m pytest tests/ -q 2>&1 | grep FAILED`. Expect exactly 22, in the 8 files above.
- [ ] **Step 2: For each failing assertion, align the pattern with the current English vocabulary of the target file — never delete an assertion, never loosen it to something contentless.** Procedure per failure: open the asserted target file, find the sentence that carries the original guard intent, and extend the regex with the actual English term as an alternation (keep the Korean alternative), e.g. `r"장식|ornamental"` → `r"장식|ornamental|decorative"`. If the guarded concept genuinely no longer exists in the target file, STOP and report (do not delete the test) — that would be a real regression from 1940cc6, not drift.
- [ ] **Step 3: Run the full suite** — `python3 -m pytest tests/ -q`. Expected: `106 passed` (84+22), 0 failed.
- [ ] **Step 4: Self-check for weakening** — re-read the diff: every changed assertion still pins a specific content token (not `.` / empty alternation); no assertion removed; no product file touched.
- [ ] **Step 5: Commit** — `git add tests/ && git commit -m "fix(tests): align 22 regression guards with the English corpus (1940cc6 drift)"`

---

### Task 1: PreToolUse citation-write interlock (`scholar_cite_guard.py`) — item #1

**Files:**
- Create: `hooks/scholar_cite_guard.py`
- Modify: `.claude-plugin/plugin.json` (add PreToolUse block)
- Test: `tests/test_scholar_cite_guard.py`, extend `tests/test_plugin_integrity.py`

**Interfaces:**
- Consumes: allowlist file `.oms/state/verified-citations.json` with shape `{"keys": {"<bibkey>": {…}}}` (produced by Task 2's `--record`; the hook only reads, tolerates absence).
- Produces: deny JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<reason>"}}` on stdout, exit 0. Silence (no output, exit 0) = allow.

Behavior contract:
- Only `Edit|Write|MultiEdit` on `.bib`/`.tex` files are inspected; everything else is silent.
- `.bib`: entry keys appearing in the *new* text (`@\w+{key,`) that are neither in the old text/on-disk file nor in the allowlist → deny, naming the keys and instructing to verify via `scripts/verify_bib_entry.py` (path computed from `__file__`) or explicit human confirmation — never fabricate.
- `.tex`: `\cite{K}` (all `\*cite*` variants, comma lists) keys new vs old text and absent from every sibling `.bib` (same dir + parent dir) → deny "add the verified .bib entry first". No sibling `.bib` found at all → fail-open allow.
- Allowlist lookup: ascend from the edited file's directory to filesystem root looking for `.oms/state/verified-citations.json`; also try payload `cwd`. First hit wins.
- `OMS_CITE_GUARD` env in `{off,0,false}` → exit 0 (human escape hatch; deliberately NOT mentioned in the deny reason so the model cannot self-bypass).
- Any exception anywhere → exit 0 (fail-open), consistent with the other two hooks.

- [ ] **Step 1: Write the failing tests** (`tests/test_scholar_cite_guard.py`; follow `test_scholar_verify_emit.py` subprocess idiom — `run_hook(payload, env=None, cwd=None)` helper returning `(returncode, stdout)`):

```python
"""Tests for the PreToolUse citation-write interlock (item #1, R1).

핵심 계약: 미검증 새 .bib entry / dangling \cite 는 deny-with-feedback 으로
구조적으로 차단하되, 절대 auto-fix 를 지시하지 않는다. 그 외엔 침묵·fail-open."""
import json, os, subprocess, sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "scholar_cite_guard.py"


def run_hook(payload, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    env.pop("OMS_CITE_GUARD", None) if env_extra is None else None
    proc = subprocess.run([sys.executable, str(HOOK)],
                          input=json.dumps(payload) if isinstance(payload, dict) else payload,
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def decision_of(stdout):
    if not stdout.strip():
        return None
    return json.loads(stdout)["hookSpecificOutput"]


def bib_payload(path, content, tool="Write", old="", cwd=None):
    ti = {"file_path": str(path)}
    if tool == "Write":
        ti["content"] = content
    else:
        ti.update({"old_string": old, "new_string": content})
    p = {"tool_name": tool, "tool_input": ti}
    if cwd:
        p["cwd"] = str(cwd)
    return p


def test_new_unverified_bib_entry_denied(tmp_path):
    bib = tmp_path / "refs.bib"
    out = decision_of(run_hook(bib_payload(bib, "@article{smith2024,\n title={X}\n}", cwd=tmp_path)))
    assert out and out["permissionDecision"] == "deny"
    assert "smith2024" in out["permissionDecisionReason"]
    assert "verify_bib_entry" in out["permissionDecisionReason"]


def test_allowlisted_key_passes(tmp_path):
    state = tmp_path / ".oms" / "state"
    state.mkdir(parents=True)
    (state / "verified-citations.json").write_text(json.dumps({"keys": {"smith2024": {"doi": "10.1/x"}}}))
    bib = tmp_path / "refs.bib"
    out = run_hook(bib_payload(bib, "@article{smith2024,\n title={X}\n}", cwd=tmp_path))
    assert out.strip() == ""


def test_editing_existing_entry_allowed(tmp_path):
    bib = tmp_path / "refs.bib"
    bib.write_text("@article{kim2023,\n title={Old}\n}")
    out = run_hook(bib_payload(bib, "@article{kim2023,\n title={New}\n}", tool="Edit",
                               old="@article{kim2023,\n title={Old}\n}", cwd=tmp_path))
    assert out.strip() == ""


def test_dangling_cite_in_tex_denied(tmp_path):
    (tmp_path / "refs.bib").write_text("@article{real2020,\n title={R}\n}")
    tex = tmp_path / "main.tex"
    out = decision_of(run_hook(bib_payload(tex, r"as shown \cite{ghost2025}", cwd=tmp_path)))
    assert out and out["permissionDecision"] == "deny"
    assert "ghost2025" in out["permissionDecisionReason"]


def test_cite_of_existing_key_allowed(tmp_path):
    (tmp_path / "refs.bib").write_text("@article{real2020,\n title={R}\n}")
    tex = tmp_path / "sections" / "intro.tex"
    tex.parent.mkdir()
    out = run_hook(bib_payload(tex, r"\cite{real2020}", cwd=tmp_path))  # parent-dir .bib
    assert out.strip() == ""


def test_tex_without_any_bib_fails_open(tmp_path):
    out = run_hook(bib_payload(tmp_path / "main.tex", r"\cite{x2020}", cwd=tmp_path))
    assert out.strip() == ""


def test_non_paper_and_non_write_are_silent(tmp_path):
    assert run_hook({"tool_name": "Edit", "tool_input": {"file_path": "a.py", "new_string": "@x{y,}"}}).strip() == ""
    assert run_hook({"tool_name": "Read", "tool_input": {"file_path": "refs.bib"}}).strip() == ""


def test_fail_open_on_bad_input():
    assert run_hook("not json").strip() == ""


def test_env_escape_hatch(tmp_path):
    out = run_hook(bib_payload(tmp_path / "refs.bib", "@article{new2025,\n t={x}\n}", cwd=tmp_path),
                   env_extra={"OMS_CITE_GUARD": "off"})
    assert out.strip() == ""


def test_deny_reason_never_instructs_autofix(tmp_path):
    out = decision_of(run_hook(bib_payload(tmp_path / "refs.bib", "@misc{k2025,\n t={x}\n}", cwd=tmp_path)))
    reason = out["permissionDecisionReason"]
    assert "fabricat" in reason or "지어내" in reason or "invent" in reason  # forbids invention
    assert "OMS_CITE_GUARD" not in reason  # never advertises the bypass to the model


def test_stdlib_only():
    src = HOOK.read_text()
    assert "import requests" not in src and "import a2a" not in src
```

- [ ] **Step 2: Run to verify failure** — `python3 -m pytest tests/test_scholar_cite_guard.py -q` → all fail (hook file absent).
- [ ] **Step 3: Implement `hooks/scholar_cite_guard.py`:**

```python
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
"""
import json
import os
import re
import sys
from pathlib import Path

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
    candidates = list(start.parents)
    if cwd:
        candidates.append(Path(cwd))
    for base in candidates:
        f = base / ".oms" / "state" / "verified-citations.json"
        if f.is_file():
            try:
                return set(json.loads(f.read_text(encoding="utf-8")).get("keys", {}))
            except (OSError, ValueError):
                return set()
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


def main() -> int:
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
```

- [ ] **Step 4: Register in `.claude-plugin/plugin.json`** — add before the PostToolUse block:

```json
"PreToolUse": [
  {
    "matcher": "Edit|Write|MultiEdit",
    "hooks": [
      {
        "type": "command",
        "command": "python3",
        "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/scholar_cite_guard.py"]
      }
    ]
  }
],
```

- [ ] **Step 5: Extend `tests/test_plugin_integrity.py`** — append:

```python
def test_cite_guard_registered():
    """⑤ scholar_cite_guard hook 이 PreToolUse 에 등록돼 있다 (R1 #1)."""
    hooks = load_plugin()["hooks"]
    pre = json.dumps(hooks.get("PreToolUse", []))
    assert "scholar_cite_guard.py" in pre
```

- [ ] **Step 6: Run** — `python3 -m pytest tests/test_scholar_cite_guard.py tests/test_plugin_integrity.py -q` → all pass; then full suite green.
- [ ] **Step 7: Commit** — `git add hooks/scholar_cite_guard.py .claude-plugin/plugin.json tests/ && git commit -m "feat(oms): PreToolUse citation-write interlock — deny unverified .bib entries and dangling \cite (R1 #1)"`

---

### Task 2: Mechanical DOI/retraction pre-gate (`scripts/verify_bib_entry.py`) — item #2

**Files:**
- Create: `scripts/verify_bib_entry.py`
- Modify: `references/output-layout.md` (§2 tree: document `.oms/state/verified-citations.json`), `skills/scholar-verify/SKILL.md` (step 2 input: name the script for DOI checks)
- Test: `tests/test_verify_bib_entry.py`

**Interfaces:**
- Consumes: `hooks/oms_atomic.py` `atomic_write_json(target, data)` (import via `sys.path.insert(0, …/hooks)`).
- Produces: CLI `python3 scripts/verify_bib_entry.py --key K [--doi D] [--title T] [--author FAMILY] [--record] [--state-dir DIR]`; stdout line `VERDICT=<VERIFIED|MISMATCH|RETRACTED|NOT_FOUND|NETWORK_ERROR> key=… source=… detail=…`; exit 0 VERIFIED / 1 MISMATCH·RETRACTED·NOT_FOUND / 2 NETWORK_ERROR. `--record` (VERIFIED only) merges `{key: {doi, title, source, verified_at}}` into `<state-dir>/verified-citations.json` (default `./.oms/state/`) via `atomic_write_json`. Never touches any `.bib`.

Core logic (testable pure function `verify(key, doi, title, author, fetch)` where `fetch(url)->dict` raises `urllib.error.URLError`/`HTTPError`):
1. DOI given → Crossref `https://api.crossref.org/works/<quote(doi)>` (append `?mailto=` from `OMS_CROSSREF_MAILTO` env if set). From `message`: retraction if any `update-to[].type` contains `retract` → RETRACTED. Title check (when `--title` given): `difflib.SequenceMatcher(None, norm(a), norm(b)).ratio() >= 0.75` where `norm` lowercases and strips non-alphanumerics → else MISMATCH. Author check (when given): family name case-insensitive among `message.author[].family` → else MISMATCH. All checks pass (or not provided) → VERIFIED (source=crossref).
2. Crossref HTTPError → OpenAlex `https://api.openalex.org/works/doi:<doi>`: `is_retracted` → RETRACTED; fuzzy `display_name` vs title same threshold; pass → VERIFIED (source=openalex); OpenAlex HTTPError too → NOT_FOUND.
3. No DOI → Crossref `https://api.crossref.org/works?query.bibliographic=<quote(title)>&rows=5`; best item by fuzzy title ratio; ratio ≥ 0.9 and author matches (if given) → VERIFIED with `detail=candidate-doi:<doi>`; else NOT_FOUND. (Conservative: title-only match never auto-records a different title.)
4. `URLError`/timeout/`ConnectionError` at any point → NETWORK_ERROR (never a false VERIFIED).

- [ ] **Step 1: Write failing tests** (`tests/test_verify_bib_entry.py` — import the module, inject fake `fetch`):

```python
"""Tests for the DOI/retraction pre-gate (R1 #2). Network is always faked —
verdict logic must be fully testable offline; --record writes the allowlist
atomically and refuses non-VERIFIED."""
import importlib.util, json, sys, urllib.error
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "verify_bib_entry.py"
spec = importlib.util.spec_from_file_location("verify_bib_entry", SCRIPT)
vbe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vbe)

CROSSREF_OK = {"message": {"title": ["Deep Learning for Sonar"], "author": [{"family": "Smith"}], "update-to": []}}
CROSSREF_RETRACTED = {"message": {"title": ["Bad Paper"], "author": [], "update-to": [{"type": "retraction"}]}}
OPENALEX_OK = {"display_name": "Deep Learning for Sonar", "is_retracted": False}


def test_verified_by_crossref():
    v = vbe.verify("smith2024", "10.1/x", "Deep Learning for Sonar", "Smith", fetch=lambda url: CROSSREF_OK)
    assert v.verdict == "VERIFIED" and v.source == "crossref"


def test_title_mismatch():
    v = vbe.verify("smith2024", "10.1/x", "Completely Different Topic Entirely", None, fetch=lambda url: CROSSREF_OK)
    assert v.verdict == "MISMATCH"


def test_retraction_detected():
    v = vbe.verify("bad2020", "10.1/y", None, None, fetch=lambda url: CROSSREF_RETRACTED)
    assert v.verdict == "RETRACTED"


def test_openalex_fallback():
    def fetch(url):
        if "crossref" in url:
            raise urllib.error.HTTPError(url, 404, "nf", None, None)
        return OPENALEX_OK
    v = vbe.verify("smith2024", "10.1/x", "Deep Learning for Sonar", None, fetch=fetch)
    assert v.verdict == "VERIFIED" and v.source == "openalex"


def test_not_found_anywhere():
    def fetch(url):
        raise urllib.error.HTTPError(url, 404, "nf", None, None)
    assert vbe.verify("ghost", "10.1/z", None, None, fetch=fetch).verdict == "NOT_FOUND"


def test_network_error_is_not_a_verdict():
    def fetch(url):
        raise urllib.error.URLError("offline")
    assert vbe.verify("k", "10.1/x", None, None, fetch=fetch).verdict == "NETWORK_ERROR"


def test_record_writes_allowlist(tmp_path):
    v = vbe.Verdict("VERIFIED", "crossref", "ok", doi="10.1/x", title="T")
    vbe.record("smith2024", v, state_dir=tmp_path)
    data = json.loads((tmp_path / "verified-citations.json").read_text())
    assert data["keys"]["smith2024"]["doi"] == "10.1/x"
    vbe.record("kim2023", vbe.Verdict("VERIFIED", "openalex", "ok", doi="10.2/y", title="U"), state_dir=tmp_path)
    data = json.loads((tmp_path / "verified-citations.json").read_text())
    assert set(data["keys"]) == {"smith2024", "kim2023"}  # merge, not overwrite


def test_record_refuses_unverified(tmp_path):
    try:
        vbe.record("ghost", vbe.Verdict("NOT_FOUND", "crossref", "nf"), state_dir=tmp_path)
        assert False, "must raise"
    except ValueError:
        pass
    assert not (tmp_path / "verified-citations.json").exists()


def test_never_touches_bib_and_stdlib_only():
    src = SCRIPT.read_text()
    assert "NEVER writes .bib" in src  # docstring contract line (guard intent)
    assert "import requests" not in src and "import a2a" not in src  # stdlib only
    assert "atomic_write_json" in src  # allowlist write goes through oms_atomic
```

- [ ] **Step 2: Run to verify failure** — `python3 -m pytest tests/test_verify_bib_entry.py -q` → fails (script absent).
- [ ] **Step 3: Implement `scripts/verify_bib_entry.py`** per the core logic above. Structure: `Verdict` = `dataclasses.dataclass` (fields: verdict, source, detail, doi=None, title=None); `fetch_json(url, timeout=10)` using `urllib.request` with `User-Agent: oms-verify-bib` (+ `mailto` from env); `verify(key, doi, title, author, fetch=fetch_json) -> Verdict`; `record(key, verdict, state_dir)` raising `ValueError` unless `verdict.verdict == "VERIFIED"`, merging into `verified-citations.json` via `atomic_write_json`; `main(argv)` with argparse wiring `--key/--doi/--title/--author/--record/--state-dir`, printing the VERDICT line, returning 0/1/2. Module docstring states: "This script NEVER writes .bib — it verifies against Crossref (retraction records included) with OpenAlex fallback and, on --record, appends the key to the cite-guard allowlist. The human gate stays: MISMATCH/RETRACTED/NOT_FOUND are never recordable."
- [ ] **Step 4: Run tests** — target file green, then full suite green.
- [ ] **Step 5: Document the state file** — in `references/output-layout.md` §2 tree, directly above the `.oms/wiki/` line, add:

```
.oms/state/                           # cross-slug mechanism state (NOT per-job)
  verified-citations.json             # cite-guard allowlist — written ONLY by scripts/verify_bib_entry.py --record (atomic, oms_atomic)
```

  And in `skills/scholar-verify/SKILL.md` Step 2 input list, extend the line `- Input: .tex/.bib paths, paper-eval.md rubric (verify axis), latex.md card, bibtex.md card, venues.md` with `, scripts/verify_bib_entry.py (mechanical DOI/retraction lookup for the DOI-existence item)`.
- [ ] **Step 6: Commit** — `git add scripts/ tests/test_verify_bib_entry.py references/output-layout.md skills/scholar-verify/SKILL.md && git commit -m "feat(oms): mechanical DOI/retraction pre-gate + cite-guard allowlist recorder (R1 #2)"`

---

### Task 3: Per-claim quote anchoring in research notes — item #5

**Files:**
- Modify: `agents/scholar-researcher.md`, `skills/scholar-research/SKILL.md`
- Test: `tests/test_researcher_quote_anchor.py`

**Interfaces:**
- Produces: research-note claim rows carry `Quote: "…" (locator)` — Task 4's claim-faithfulness check consumes these anchors from `.oms/<slug>/research/*.md`.

- [ ] **Step 1: Write failing test:**

```python
"""R1 #5 — researcher output contract: every claim row carries a verbatim
source quote + locator (Elicit/PaperQA2 pattern). Feeds the claim-faithfulness
check (#3) mechanically."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-researcher.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "scholar-research" / "SKILL.md").read_text(encoding="utf-8")


def test_agent_output_format_has_quote_anchor():
    assert re.search(r"Quote:", AGENT), "Output_Format 에 Quote 앵커 행 누락"
    assert re.search(r"verbatim", AGENT, re.I), "verbatim(원문 그대로) 계약 누락"
    assert re.search(r"locator|page|section", AGENT, re.I), "locator 계약 누락"


def test_agent_forbids_reconstructed_quotes():
    assert re.search(r"never.*(reconstruct|from memory)|reconstruct.*never", AGENT, re.I | re.S), \
        "기억 재구성 인용 금지 문구 누락"


def test_agent_quote_missing_degrade():
    assert re.search(r"quote-missing|abstract-only", AGENT, re.I), "전문 접근 불가 시 degrade 표기 누락"


def test_skill_mentions_anchoring_and_faithfulness_feed():
    assert re.search(r"quote", SKILL, re.I), "SKILL 에 quote 앵커 지시 누락"
    assert re.search(r"claim-faithfulness|faithfulness", SKILL, re.I), "verify 연계(#3 feed) 언급 누락"
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Edit `agents/scholar-researcher.md`** (surgical insertions):
  - `<Success_Criteria>` add bullet: `- Every claim row carries a **verbatim quote** from the source (≤3 sentences, copied exactly — never reconstructed from memory) plus a locator (section/page/paragraph). If only the abstract was accessible, the row is marked `quote-missing (abstract-only)` — passage-level grounding beats abstract-only.`
  - `<Investigation_Protocol>` step 3, append: `Record a verbatim supporting quote + locator for each claim you will report (the quote is the anchor scholar-verify's claim-faithfulness check re-reads).`
  - `<Output_Format>` Related Work row template, after the Relevance sentence add a second line: `  Quote: "…verbatim source sentence(s)…" (§2.1 / p.4). [or: quote-missing (abstract-only)]`
  - `<Final_Checklist>` add: `- Does every claim row carry a verbatim quote + locator (or an explicit quote-missing mark)?`
- [ ] **Step 4: Edit `skills/scholar-research/SKILL.md`:** in `<Steps>` item 2 Instructions, append `, per-claim verbatim quote + locator anchoring (quote rows feed scholar-verify's claim-faithfulness check)`; in `<Execution_Policy>` after the passage-level grounding bullet, add: `- Quote anchors are the mechanical substrate of verify's claim-faithfulness (citation-misuse) check — a claim row without its quote can only be checked by a human.`
- [ ] **Step 5: Run** — target test green, full suite green.
- [ ] **Step 6: Commit** — `git add agents/scholar-researcher.md skills/scholar-research/SKILL.md tests/test_researcher_quote_anchor.py && git commit -m "feat(oms): per-claim verbatim quote anchoring in research notes (R1 #5)"`

---

### Task 4: Claim-faithfulness (`citation-misuse`) sub-check in verify — item #3

**Files:**
- Modify: `agents/scholar-verifier.md`, `skills/scholar-verify/SKILL.md`
- Test: `tests/test_verify_claim_faithfulness.py`

**Interfaces:**
- Consumes: Task 3's quote anchors in `.oms/<slug>/research/*.md`.
- Produces: new WARN-class check `claim-faithfulness (citation-misuse)` with stance labels `supports/contrasts/mentions`; mismatches go to the human-confirmation list. Clean-room re-implementation (ARS is CC-BY-NC — mechanism only, no copied text).

- [ ] **Step 1: Write failing test:**

```python
"""R1 #3 — "citation exists" ≠ "citation supports this claim". verify gains a
claim-faithfulness sub-check (stance: supports/contrasts/mentions) sourced from
the researcher's quote anchors. WARN + human list, never auto-fix, never guess
without an anchor."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENT = (ROOT / "agents" / "scholar-verifier.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "scholar-verify" / "SKILL.md").read_text(encoding="utf-8")


def test_agent_has_citation_misuse_check():
    assert "citation-misuse" in AGENT
    assert re.search(r"supports.*contrasts.*mentions", AGENT, re.S), "3-stance 라벨 누락"


def test_agent_check_is_warn_and_human_flagged():
    block = AGENT[AGENT.index("citation-misuse"):]
    assert re.search(r"WARN", block), "citation-misuse 는 WARN 급이어야"
    assert re.search(r"human", block, re.I), "human-confirmation 연결 누락"


def test_agent_no_anchor_means_not_run_not_guessed():
    assert re.search(r"(no|without).{0,40}anchor.{0,120}(not run|manual|never guess)", AGENT, re.I | re.S), \
        "앵커 부재 시 '미실행/사람 확인' 처리 누락 (추측 금지)"


def test_agent_output_table_has_row():
    assert re.search(r"claim-faithfulness", AGENT), "Output_Format 표에 행 누락"


def test_skill_step_names_the_check():
    assert "citation-misuse" in SKILL or "claim-faithfulness" in SKILL
    assert re.search(r"quote anchor", SKILL, re.I), "research 노트 앵커 소스 명시 누락"
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Edit `agents/scholar-verifier.md`:**
  - `<Role>` check-items list, after the "Citation consistency" line add: `- Claim-faithfulness / citation-misuse (**WARN**): for each claim↔\cite pair, re-read the verbatim quote anchor from the research notes (.oms/<slug>/research/*.md) and label the stance — **supports / contrasts / mentions**. A cited-but-contrasting or merely-mentioning source used as support = citation-misuse → WARN + human-confirmation list. "The citation exists" ≠ "the citation supports this claim". Pairs without a quote anchor: "check not run — needs manual confirmation" (never guess a stance, never fetch to improvise one).`
  - `<Investigation_Protocol>` insert step `7.5)`: `**Claim-faithfulness (citation-misuse, WARN)**: collect claim sentences containing \cite{K}; for each, find K's quote anchor row in .oms/<slug>/research/*.md; compare the claim against the verbatim quote and label supports/contrasts/mentions. contrasts/mentions-used-as-support → WARN with both texts as evidence + human-confirmation list entry. No anchor row → list the pair under "check not run — needs manual confirmation". Never auto-fix, never guess.`
  - `<Output_Format>` per-item table add row: `| claim-faithfulness (citation-misuse) | PASS/**WARN** | misused N, unanchored M (WARN=does not block overall PASS) |`
  - `<Final_Checklist>` add: `- Did you label claim↔cite stances only from quote anchors (supports/contrasts/mentions), WARN-flagging misuse to the human list and marking unanchored pairs "check not run" instead of guessing?`
- [ ] **Step 4: Edit `skills/scholar-verify/SKILL.md`:** in `<Steps>` item 2 checklist add: `- **Claim-faithfulness / citation-misuse (WARN)**: claim↔\cite stance check against the researcher's quote anchors (supports/contrasts/mentions) — misuse → human-confirmation list; unanchored pairs = "check not run". "Exists" ≠ "supports".`; in `<Output>` add `claim-faithfulness` to the WARN examples in the results-table line.
- [ ] **Step 5: Run** — green (target + full suite).
- [ ] **Step 6: Commit** — `git add agents/scholar-verifier.md skills/scholar-verify/SKILL.md tests/test_verify_claim_faithfulness.py && git commit -m "feat(oms): claim-faithfulness citation-misuse WARN check in verify (R1 #3)"`

---

### Task 5: `[MATERIAL GAP]` token + uncited-claim scan — item #4

**Files:**
- Modify: `agents/scholar-drafter.md`, `agents/scholar-verifier.md`, `skills/scholar-draft/SKILL.md`, `skills/scholar-verify/SKILL.md`
- Test: `tests/test_material_gap_contract.py`

**Interfaces:**
- Produces: drafter emits `% [MATERIAL GAP: …]` instead of inferring when grounding is absent; verifier counts `[MATERIAL GAP` among placeholder FAIL tokens and adds an uncited-claim WARN scan.

- [ ] **Step 1: Write failing test:**

```python
"""R1 #4 — when grounding material is absent the drafter emits a greppable
`% [MATERIAL GAP: …]` token instead of inferring (clean-room ARS mechanism);
verify FAILs leftover MATERIAL GAP tokens (placeholder class) and WARNs on
claim-shaped sentences with no adjacent \\cite."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DRAFTER = (ROOT / "agents" / "scholar-drafter.md").read_text(encoding="utf-8")
VERIFIER = (ROOT / "agents" / "scholar-verifier.md").read_text(encoding="utf-8")
DRAFT_SKILL = (ROOT / "skills" / "scholar-draft" / "SKILL.md").read_text(encoding="utf-8")
VERIFY_SKILL = (ROOT / "skills" / "scholar-verify" / "SKILL.md").read_text(encoding="utf-8")


def test_drafter_material_gap_contract():
    assert "MATERIAL GAP" in DRAFTER
    assert re.search(r"instead of inferring|never.*infer|inferring", DRAFTER, re.I), \
        "근거 부재 시 추론 대신 토큰 방출 계약 누락"


def test_drafter_surfaces_gaps_in_output():
    assert re.search(r"MATERIAL GAP", DRAFTER[DRAFTER.index("<Output_Format>"):]), \
        "Output_Format 의 gap 목록 누락"


def test_verifier_fails_leftover_material_gap():
    assert "MATERIAL GAP" in VERIFIER
    idx = VERIFIER.index("Placeholder check") if "Placeholder check" in VERIFIER else VERIFIER.index("MATERIAL GAP")
    assert re.search(r"MATERIAL GAP", VERIFIER[idx:idx + 800]), "placeholder 토큰 목록에 MATERIAL GAP 누락"


def test_verifier_uncited_claim_scan_is_warn():
    assert re.search(r"uncited[- ]claim", VERIFIER, re.I)
    block = VERIFIER[re.search(r"uncited[- ]claim", VERIFIER, re.I).start():]
    assert "WARN" in block[:600], "uncited-claim 스캔은 WARN 급이어야"


def test_skills_carry_both_contracts():
    assert "MATERIAL GAP" in DRAFT_SKILL
    assert re.search(r"uncited[- ]claim|MATERIAL GAP", VERIFY_SKILL)
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Edit `agents/scholar-drafter.md`:**
  - `<Constraints>` NEVER-invent bullet, append: `When the *material itself* is missing (no concept note, no data, no verified source for a needed claim), emit a greppable token at the exact site — `% [MATERIAL GAP: <what is missing>]` — instead of inferring plausible content. The token is auditable by grep and FAILs the verify gate until a human resolves it.`
  - `<Output_Format>` "Surfaced to Human" section add line: `- MATERIAL GAP tokens emitted: [list of `% [MATERIAL GAP: …]` sites, or "none"]`
  - `<Final_Checklist>` add: `- Did I emit `% [MATERIAL GAP: …]` (never plausible inference) wherever grounding material was absent, and surface the list?`
- [ ] **Step 4: Edit `agents/scholar-verifier.md`:**
  - Protocol step 4 (Placeholder check) grep, extend pattern with `\[MATERIAL GAP`: `grep -rn "\\\\todo\|\\[TODO\]\|\\[FIXME\]\|XXX\|TBD\|\\[MATERIAL GAP" sections/ main.tex` and note: `MATERIAL GAP tokens are deliberate drafter flags for missing grounding — they FAIL the gate (same class as TODO) and each carries its own description of what the human must supply.`
  - Insert protocol step `9.7)`: `**Uncited-claim scan (WARN)**: in body sections, flag claim-shaped sentences with no \cite in the same sentence — seed shapes: superlatives/firsts (`state-of-the-art|first|novel|outperform`), comparatives (`better than|superior to|significantly (higher|lower)`), universals (`always|never|all existing`). 1+ hits = WARN list with file:line (over-detection allowed — a human judges; some claims are the paper's own contribution and legitimately uncited). Never auto-insert citations.`
  - `<Output_Format>` table add row: `| uncited claims | PASS/**WARN** | N flagged (WARN=does not block overall PASS) |` and add `[MATERIAL GAP` to the leftover-placeholders row note: `N (includes [MATERIAL GAP …] tokens)`.
  - `<Role>` check-items: extend the "Leftover placeholders" line with `/[MATERIAL GAP …]` and add line: `- Uncited claims (**WARN**): claim-shaped sentences with no adjacent \cite — over-detection allowed, human judges.`
- [ ] **Step 5: Edit skills:** `skills/scholar-draft/SKILL.md` `<Steps>` item 3 Instructions append: `, emit `% [MATERIAL GAP: …]` at any site whose grounding material is absent (never infer plausible content)`; and in `<Output>` add `+ MATERIAL GAP token list (if any)`. `skills/scholar-verify/SKILL.md` `<Steps>` item 2 checklist: extend the **placeholder** line to `TODO/FIXME/XX/[MATERIAL GAP] leftovers 0` and add `- **Uncited-claim scan (WARN)**: claim-shaped sentences without \cite — WARN list, human judges (never auto-cite).`
- [ ] **Step 6: Run** — green (target + full suite).
- [ ] **Step 7: Commit** — `git add agents/scholar-drafter.md agents/scholar-verifier.md skills/scholar-draft/SKILL.md skills/scholar-verify/SKILL.md tests/test_material_gap_contract.py && git commit -m "feat(oms): [MATERIAL GAP] token + uncited-claim WARN scan (R1 #4)"`

---

### Task 6: README evidence + CHANGELOG 0.6.0 release notes — item #0 + release

**Files:**
- Modify: `README.md`, `CHANGELOG.md`
- Test: `tests/test_readme_evidence.py`

**Interfaces:** none (docs).

- [ ] **Step 1: Write failing test:**

```python
"""R1 #0 — the measured hallucination numbers live in README §citation-safety
as the load-bearing "why" (pure documentation, zero mechanism)."""
import re
from pathlib import Path

README = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")


def test_readme_cites_measured_rates():
    assert re.search(r"78[–-]90\s*%", README), "OpenScholar 합성 인용 오류율 누락"
    assert re.search(r"14[–-]95\s*%", README), "GhostCite 모델별 범위 누락"
    assert re.search(r"NeurIPS 2025", README), "인간 리뷰 미검출 사례 누락"


def test_readme_evidence_has_sources():
    assert "2411.14199" in README, "OpenScholar arXiv id 누락"
    assert "2602.06718" in README, "GhostCite arXiv id 누락"


def test_readme_names_the_interlock():
    assert "scholar_cite_guard" in README
    assert "verify_bib_entry" in README
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Edit `README.md`:**
  - Under "## The 3 citation-safety principles (oms identity)", after the numbered list add:

```markdown
**Why this is load-bearing (measured, 2026 audit — see `docs/2026-07-11-oms-advancement-plan.md` §3.A):**
- GPT-4o fabricates citations **78–90%** of the time on multi-paper synthesis ([OpenScholar benchmark, arXiv:2411.14199](https://arxiv.org/abs/2411.14199)).
- Across 13 models / 40 domains / 375K citations, fabrication runs **14–95%** by model and domain ([GhostCite, arXiv:2602.06718](https://arxiv.org/abs/2602.06718)).
- Human review does not catch it: ~**100 confirmed hallucinated citations in accepted NeurIPS 2025 papers** (GPTZero), each missed by 3–5 reviewers; 77% of reviewers admit not checking references thoroughly.

Since v0.6.0 principle 2 is **enforced, not just stated**: a PreToolUse interlock (`hooks/scholar_cite_guard.py`) denies unverified new `.bib` entries and dangling `\cite` keys before they land, and `scripts/verify_bib_entry.py` verifies DOI existence + retraction status against Crossref (Retraction Watch data included) with OpenAlex fallback, recording human-gated VERIFIED keys into the `.oms/state/verified-citations.json` allowlist.
```

  - "## Routing" section, append: `A third hook (PreToolUse `scholar_cite_guard.py`) structurally denies unverified citation writes (see citation-safety above).`
  - "## Status" first line: `v0.6.0 — 12 skills + 6 agents + reference cards … + citation-safe hooks (`scholar_route_emit`/`scholar_verify_emit`/**`scholar_cite_guard`** + `oms_atomic`). Added in 0.6.0: **citation-integrity enforcement (P0)** — PreToolUse cite interlock, Crossref/OpenAlex DOI+retraction pre-gate with allowlist recording, claim-faithfulness (citation-misuse) WARN, `[MATERIAL GAP]` token + uncited-claim WARN, per-claim quote anchoring in research notes.` Update the stale test count (`98 passed`) to the real final count from the full suite run.
- [ ] **Step 4: Edit `CHANGELOG.md`** — new `## [0.6.0] - 2026-07-11` section above `[Unreleased]`'s current content (move the existing Unreleased items into 0.6.0 as previously-unreleased fixes), with Added (the five P0 mechanisms, one bullet each incl. file paths + the `OMS_CITE_GUARD=off` human escape hatch + `OMS_CROSSREF_MAILTO`), Fixed (22 test↔doc English-drift regression guards realigned, Task 0), Docs (advancement plan + this execution plan committed), Verification (`python3 -m pytest tests/ -q` final counts). Follow the existing entry style.
- [ ] **Step 5: Run** — `python3 -m pytest tests/ -q` full suite green; note the final passed count and make sure README Status quotes it.
- [ ] **Step 6: Commit** — `git add README.md CHANGELOG.md tests/test_readme_evidence.py && git commit -m "docs(oms): measured hallucination evidence + v0.6.0 release notes (R1 #0)"`

---

## Self-Review (done at plan time)

- Spec coverage: #0→T6, #1→T1, #2→T2, #3→T4, #4→T5, #5→T3, plus T0 (suite must be green to release — pre-existing drift). Sequencing honored: T2 consumes T1's allowlist shape; T4 consumes T3's anchors (tasks ordered).
- Invariants: no auto-fix anywhere (deny/WARN/human lists only); no embeddings; stdlib only; fail-open hooks; human gates kept (allowlist records only mechanically VERIFIED facts; MISMATCH/RETRACTED/NOT_FOUND never recordable).
- Type consistency: allowlist shape `{"keys": {key: {...}}}` identical in T1 hook, T1 tests, T2 `record()`, T2 tests. Verdict strings identical across T2 code/tests. Token `% [MATERIAL GAP: …]` identical in T5 drafter/verifier/skills/tests.
