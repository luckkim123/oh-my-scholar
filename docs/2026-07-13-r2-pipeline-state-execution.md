# R2 — Pipeline State & Loop Robustness (P1 #6–#13) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the pipeline's advertised guarantees real: a defined `.oms/state/` schema written atomically at every stage boundary (#6), a mechanical strike/round ledger for the revise loop (#7), a scoped exemption-laden Stop-guard (#8), a SessionStart resume advisory (#9), a verifier round-id token (#10), an abort/interrupt spec (#11), the notepad 3-tier convention (#12), and compaction-surviving Priority Context re-injection (#13) — release as v0.7.0, stacked on R1 (`feat/r1-citation-integrity`).

**Architecture:** One new stdlib CLI (`scripts/oms_state.py`) owns every state read/write — pilot stage state (`pilot-<slug>.json`) and revise loop marker (`revise-<slug>.json`) — all writes via `hooks/oms_atomic.py`. Two new hooks consume that state: a Stop hook (`hooks/scholar_stop_guard.py`) that blocks premature stops only while a live revise marker exists and no exemption fires, and a SessionStart hook (`hooks/scholar_resume_emit.py`, matcher `startup|resume|clear|compact`) that injects a resume advisory + re-injects notepad `## Priority Context` after compaction. Items #10/#11/#12 are prompt-contract edits with literal-substring regression tests (repo idiom). Spec = `docs/2026-07-11-oms-advancement-plan.md` §5 P1.

**Design deviations from the plan text (deliberate, contract-verified 2026-07-13 against code.claude.com/docs/en/hooks.md):**
- **#13 is implemented via `SessionStart(source: "compact")`, NOT a PreCompact hook.** Verified against https://code.claude.com/docs/en/hooks.md (fetched 2026-07-13): PreCompact has **no context-injection channel at all** — the JSON-output decision-control table grants `hookSpecificOutput.additionalContext` only to Stop/SubagentStop in its event group ("Stop and SubagentStop also accept `hookSpecificOutput.additionalContext` for non-error feedback"), leaving PreCompact with only `decision: "block"` + universal fields; whereas SessionStart's documented matcher set includes `compact` ("Auto or manual compaction") and SessionStart supports `additionalContext` into the fresh post-compaction context. The plan's intent (Priority Context survives compaction) is what we implement; the plan's named mechanism (PreCompact) cannot carry it per the verified contract. One hook file therefore serves both #9 and #13.
- **#14 (session envelope + O_EXCL lock) is deliberately NOT implemented** — the plan itself marks it conditional on an observed multi-session collision. Recorded in CHANGELOG Notes; revisit only on a real collision.

**Tech Stack:** Python 3 stdlib only (json, os, sys, time, uuid, argparse, pathlib, datetime), pytest, markdown prompt contracts.

## Global Constraints

- stdlib only — no third-party imports in hooks/ or scripts/ (repo invariant).
- All hooks fail-open: any parse/IO error → exit 0; a broken or unparseable state file must NEVER block a session.
- **Never-wedge guarantee (Stop guard)**: the guard must always have a monotonic escape — durable `stop_blocks` counter with a hard cap, TTL on the marker, strike/round exemptions, `OMS_STOP_GUARD=off` env hatch (never advertised in the block reason), and fail-open on any error. A user must never need to kill the terminal to escape the loop. Durability includes resume: `revise-start` on a live marker is idempotent (counters preserved) — a crash/compaction resume must never zero the counters the escapes depend on.
- **Scoped, not global**: both new hooks honor a state record only when the session `cwd` is inside that record's `paper_root` (recorded at write time), and directory ascent stops at the NEAREST `.oms/state/` (first hit — never enumerate ancestors past it). A stale loop marker in a shared ancestor workspace must never guard or advise an unrelated session.
- **Citation defects never enter loop mechanics**: strikes/defect-ids track fixable_by_llm=true defects only, and the guard's block reason explicitly says citation/content defects are escalated to a human, never looped (oms invariant). Enforcement layers, stated honestly: this rule is a *prompt contract* on scholar-revise plus the R1 cite-guard write interlock — `oms_state.py` does not (cannot) classify defect kinds mechanically; a classification flag supplied by the same model would be ceremony, not enforcement.
- State reads in hooks resolve by directory ascent from the payload `cwd` (same pattern as cite-guard's allowlist ascent) with the nearest-first + `paper_root` scoping above; the CLI takes explicit `--state-dir` with default `./.oms/state`.
- Prompt-contract edits are surgical: keep surrounding text and heading numbering intact; English corpus.
- Every task ends with `python3 -m pytest tests/ -q` green (baseline 144 passed; later tasks keep it green).
- Worktree: `/Users/kimseungmin/oh-my-scholar/.claude/worktrees/oms-r2`, branch `feat/r2-pipeline-state` (base: `feat/r1-citation-integrity` — R1 is an unmerged draft PR; this branch stacks on it and the PR targets it). Commit per task, message style `feat(oms): …` matching git log.

---

### Task 1: `.oms/state/` schema + `scripts/oms_state.py` (write/read) — item #6

**Files:**
- Create: `scripts/oms_state.py`
- Modify: `references/output-layout.md` (§2 tree + new §2.2 state schema), `skills/scholar-pilot/SKILL.md` (stage-boundary write contract)
- Test: `tests/test_oms_state.py` (CLI part), `tests/test_state_schema_docs.py` (literal locks)

**Interfaces:**
- Consumes: `hooks/oms_atomic.py` `atomic_write_json` (import via `sys.path.insert(0, …/hooks)` — same idiom as `verify_bib_entry.py`).
- Produces: `pilot-<slug>.json` in the state dir with schema:

```json
{
  "slug": "2026-07-13_paper-slug",
  "stage": "research|deepen|ideate|outline|draft|inspect|verify|revise|submission|terminal",
  "gate_status": "pending|approved|revise|abort|null",
  "open_fail_ids": ["defect-id", "…"],
  "paper_root": "/abs/cwd/where/the/pipeline/runs",
  "updated_at": "2026-07-13T09:00:00+00:00"
}
```

On create, `write` always initializes the full key set — `gate_status: null` and `open_fail_ids: []` when not named, `paper_root` = the resolved cwd at write time (`--paper-root` override allowed) — so every downstream consumer (T3 guard, T5 advisory) reads stable keys instead of `.get()`-guessing.

CLI contract (`python3 scripts/oms_state.py <verb> …`):
- `write --slug S --stage X [--gate-status Y] [--open-fail-ids a,b,c] [--state-dir D]` — merge-write `pilot-<S>.json` (existing fields not named are preserved), `updated_at` auto-set to UTC ISO-8601, written via `atomic_write_json`. Prints the resulting JSON. Invalid `--stage`/`--gate-status` enum → error message + exit 2, file untouched (strict: catches model typos).
- `read [--slug S] [--state-dir D]` — prints the pilot state JSON (or a JSON list of all `pilot-*.json` when `--slug` omitted). Missing file/dir → prints `{}` (or `[]`), exit 0 (read never fails a session).
- Slug is used verbatim in the filename — validate it matches `^[A-Za-z0-9._-]+$` (reject path separators; exit 2).

Prompt contract (scholar-pilot):
- In `<Execution_Policy>`, replace the sentence `Stage outputs are recorded in \`.oms/state/\` (OMC state pattern) — resumable after interruption.` with a concrete mechanism: at **every stage boundary and every GATE decision**, run `python3 <plugin>/scripts/oms_state.py write --slug <slug> --stage <stage> --gate-status <status> [--open-fail-ids …]` — the schema (documented in `references/output-layout.md` §2.2) is what `--from` resume, the Stop guard, and the SessionStart advisory read; a stage that skips the write is invisible to all three.
- In the `--from` note (line ~71): state that `--from` now *reads* `pilot-<slug>.json` (via `oms_state.py read`) and, when invoked without an explicit stage, proposes the recorded `stage` as the resume point.

- [ ] **Step 1: Write failing tests** — `tests/test_oms_state.py` (import the module via `importlib.util` like `test_verify_bib_entry.py`; drive `main(argv)` and the underlying functions with `tmp_path` state dirs):

```python
"""R2 #6 — .oms/state/ schema: pilot-<slug>.json written atomically (oms_atomic),
merge semantics, strict enums, read never fails. The substrate for #7–#11/#13."""
import importlib.util, json, sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "oms_state.py"
spec = importlib.util.spec_from_file_location("oms_state", SCRIPT)
oms_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oms_state)


def run(argv, tmp_path):
    return oms_state.main([*argv, "--state-dir", str(tmp_path)])


def read_file(tmp_path, slug):
    return json.loads((tmp_path / f"pilot-{slug}.json").read_text(encoding="utf-8"))


def test_write_creates_schema(tmp_path):
    assert run(["write", "--slug", "s1", "--stage", "draft"], tmp_path) == 0
    d = read_file(tmp_path, "s1")
    assert d["slug"] == "s1" and d["stage"] == "draft"
    assert "updated_at" in d and "T" in d["updated_at"]  # ISO-8601
    # create initializes the full key set — consumers read stable keys
    assert d["gate_status"] is None and d["open_fail_ids"] == []
    assert d["paper_root"]  # recorded cwd (or --paper-root)


def test_write_merges_not_overwrites(tmp_path):
    run(["write", "--slug", "s1", "--stage", "verify", "--open-fail-ids", "d1,d2"], tmp_path)
    run(["write", "--slug", "s1", "--gate-status", "pending"], tmp_path)
    d = read_file(tmp_path, "s1")
    assert d["stage"] == "verify" and d["open_fail_ids"] == ["d1", "d2"]
    assert d["gate_status"] == "pending"


def test_invalid_stage_rejected(tmp_path, capsys):
    assert run(["write", "--slug", "s1", "--stage", "vibing"], tmp_path) == 2
    assert not (tmp_path / "pilot-s1.json").exists()


def test_invalid_gate_status_rejected(tmp_path):
    assert run(["write", "--slug", "s1", "--stage", "draft", "--gate-status", "yolo"], tmp_path) == 2


def test_slug_path_traversal_rejected(tmp_path):
    assert run(["write", "--slug", "../evil", "--stage", "draft"], tmp_path) == 2
    assert run(["write", "--slug", "a/b", "--stage", "draft"], tmp_path) == 2


def test_read_missing_is_empty_not_error(tmp_path, capsys):
    assert run(["read", "--slug", "ghost"], tmp_path) == 0
    assert json.loads(capsys.readouterr().out) == {}


def test_read_all_lists_pilots(tmp_path, capsys):
    run(["write", "--slug", "a", "--stage", "draft"], tmp_path)
    run(["write", "--slug", "b", "--stage", "verify"], tmp_path)
    capsys.readouterr()
    assert run(["read"], tmp_path) == 0
    slugs = {d["slug"] for d in json.loads(capsys.readouterr().out)}
    assert slugs == {"a", "b"}


def test_write_goes_through_oms_atomic():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "atomic_write_json" in src
    assert "import requests" not in src  # stdlib only
```

And `tests/test_state_schema_docs.py` (locks for this task; T6 extends it):

```python
"""R2 #6/#11/#12 — the state schema and notepad tiers are documented in the
layout SSOT and wired into scholar-pilot (literal locks, repo idiom)."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
LAYOUT = (ROOT / "references" / "output-layout.md").read_text(encoding="utf-8")
PILOT = (ROOT / "skills" / "scholar-pilot" / "SKILL.md").read_text(encoding="utf-8")


def test_layout_documents_pilot_state():
    assert "pilot-<slug>.json" in LAYOUT
    assert re.search(r"gate_status", LAYOUT) and re.search(r"open_fail_ids", LAYOUT)
    assert re.search(r"oms_state\.py", LAYOUT), "state files are written only via the CLI"


def test_layout_documents_revise_marker():
    assert "revise-<slug>.json" in LAYOUT  # written by T2; documented together in §2.2


def test_pilot_writes_state_at_boundaries():
    assert "oms_state.py" in PILOT
    assert re.search(r"(every|each) stage boundary", PILOT, re.I)


def test_pilot_from_reads_state():
    idx = PILOT.index("--from")
    assert re.search(r"oms_state\.py read|pilot-<slug>\.json", PILOT[idx:idx + 600]), \
        "--from must read the recorded state, not just advertise"
```

- [ ] **Step 2: Run to verify failure** — both files fail (script/doc text absent).
- [ ] **Step 3: Implement `scripts/oms_state.py`.** Module docstring states: this CLI is the ONLY writer of `.oms/state/pilot-*.json`/`revise-*.json` (the verified-citations allowlist stays owned by `verify_bib_entry.py`); all writes go through `atomic_write_json`; it never touches `.tex`/`.bib`/notepad. Constants: `STAGES = ("research","deepen","ideate","outline","draft","inspect","verify","revise","submission","terminal")`, `GATE_STATUSES = ("pending","approved","revise","abort")`, `SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")`. Structure: `load(state_dir, name) -> dict`, `write_pilot(state_dir, slug, **fields)`, `main(argv) -> int` with argparse subcommands (this task: `write`, `read`; T2 adds the revise verbs to the same file). Also document `.oms/state/` in **`references/output-layout.md`**: extend the §2 tree's `.oms/state/` block with `pilot-<slug>.json` and `revise-<slug>.json` lines, and add a **§2.2 "state schema (pipeline mechanism state)"** subsection: both JSON shapes verbatim, "written only via `scripts/oms_state.py` (atomic)", who reads them (pilot `--from`, Stop guard, SessionStart advisory), and their cleanup fate (terminal → removable with the slug's work area; §5 table gains a `.oms/state/pilot-*.json / revise-*.json` row: ✅ clean at terminal, after GATE 3).
- [ ] **Step 4: Edit `skills/scholar-pilot/SKILL.md`** per the prompt contract above (surgical: the Execution_Policy bullet and the `--from` note only — T6 adds the interruption section).
- [ ] **Step 5: Run** — target tests green, then full suite green. (T1's §2.2 doc edit documents BOTH state-file shapes — `pilot-<slug>.json` and `revise-<slug>.json`, the latter defined in Task 2's Interfaces — so `test_layout_documents_revise_marker` is green from T1 onward; T2 then implements the marker verbs against the already-documented shape.)
- [ ] **Step 6: Commit** — `git add scripts/oms_state.py references/output-layout.md skills/scholar-pilot/SKILL.md tests/test_oms_state.py tests/test_state_schema_docs.py && git commit -m "feat(oms): .oms/state schema + oms_state CLI — pilot stage state written atomically (R2 #6)"`

---

### Task 2: Revise marker + strike/round ledger — item #7

**Files:**
- Modify: `scripts/oms_state.py` (add verbs), `skills/scholar-revise/SKILL.md`
- Test: extend `tests/test_oms_state.py`; create `tests/test_revise_ledger_contract.py`

**Interfaces:**
- Produces: `revise-<slug>.json`:

```json
{
  "slug": "…",
  "active": true,
  "round": 2,
  "round_id": "uuid4-of-current-round",
  "max_rounds": 5,
  "ttl_hours": 6,
  "strikes": {"defect-id": 2},
  "stop_blocks": 0,
  "paper_root": "/abs/cwd/where/the/loop/was/started",
  "started_at": "2026-07-13T09:00:00+00:00",
  "status": "live|done|stopped|abort"
}
```

New CLI verbs (same file, same atomic writer):
- `revise-start --slug S [--max-rounds N] [--ttl-hours H] [--force-restart] [--state-dir D]` — creates the marker: `active=true, round=0, round_id=null, strikes={}, stop_blocks=0, paper_root=<resolved cwd>, started_at=now, status="live"`. `max_rounds` default 5 (venue `max_review_rounds` — the caller passes the venue value), clamped to 1–20; `ttl_hours` default 6, clamped to 1–168 — out-of-range values are rejected with the same strict-style error + exit 2 as `--stage` (an unbounded `max_rounds` would make both the round exemption and the stop_blocks cap unreachable). **Idempotent on resume**: re-running on an existing *live* marker for the same slug is a no-op that preserves `round`/`strikes`/`stop_blocks` (prints the existing marker plus `"resumed": true`) — a crash/compaction resume must never zero the never-wedge counters. Only an explicit `--force-restart` resets the marker (a deliberately new loop).
- `revise-round --slug S` — `round += 1`, mints a fresh `round_id` (uuid4), prints `{"round": N, "max_rounds": M, "round_id": "…"}`. If `round > max_rounds` after increment, prints the same JSON plus `"exceeded": true` (the SKILL decides to stop; the CLI never blocks).
- `strike --slug S --defect-id D` — `strikes[D] += 1`, prints `{"defect_id": D, "count": N, "third_strike": bool}`. Defect-id validated against `SLUG_RE`-like charset (no path chars).
- `revise-end --slug S [--status done|stopped|abort]` — `active=false`, `status` set (default `done`).
- All verbs on a missing marker (except `revise-start`) → error + exit 2 (a loop that never started can't be counted).

Prompt contract (scholar-revise SKILL.md — surgical edits inside `<Steps>` and `<Execution_Policy>`):
- Step 1 gains: at loop start run `revise-start` with the venue's `max_review_rounds`. `revise-start` is idempotent — after a crash or compaction it resumes the live marker with its counters intact; pass `--force-restart` only when the human explicitly starts a fresh loop (never to "clean up" a resumed one).
- Step 3 (each round) gains: (a) run `revise-round` and carry its `round_id` into both Task prompts (T4 wires the verifier echo); if `"exceeded": true` → stop and report (mechanical max-rounds, replaces self-counting).
- Step 3c gains: when the same defect re-appears in a new round's FAIL list, run `strike --defect-id <id>` — `third_strike: true` in the output IS the 3-strike stop condition ("countable by grep, not self-report"). Never call `strike` for fixable_by_llm=false (citation/content) defects — those never enter the loop at all.
- Step 4 gains: every exit path (PASS, 3-strike, max-rounds, regression stop, human abort) runs `revise-end --status …` — a live marker with no loop is what the Stop guard (T3) treats as "the loop is still running", so ending the loop without `revise-end` leaves the session guarded.

- [ ] **Step 1: Write failing tests** — extend `tests/test_oms_state.py`:

```python
def test_revise_start_creates_marker(tmp_path, capsys):
    assert run(["revise-start", "--slug", "s1", "--max-rounds", "3"], tmp_path) == 0
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["active"] is True and d["round"] == 0 and d["strikes"] == {}
    assert d["max_rounds"] == 3 and d["status"] == "live" and d["stop_blocks"] == 0


def test_revise_round_increments_and_mints_round_id(tmp_path, capsys):
    run(["revise-start", "--slug", "s1"], tmp_path)
    capsys.readouterr()
    run(["revise-round", "--slug", "s1"], tmp_path)
    r1 = json.loads(capsys.readouterr().out)
    run(["revise-round", "--slug", "s1"], tmp_path)
    r2 = json.loads(capsys.readouterr().out)
    assert (r1["round"], r2["round"]) == (1, 2)
    assert r1["round_id"] != r2["round_id"] and len(r1["round_id"]) >= 32


def test_revise_round_flags_exceeded(tmp_path, capsys):
    run(["revise-start", "--slug", "s1", "--max-rounds", "1"], tmp_path)
    run(["revise-round", "--slug", "s1"], tmp_path)
    capsys.readouterr()
    run(["revise-round", "--slug", "s1"], tmp_path)
    assert json.loads(capsys.readouterr().out).get("exceeded") is True


def test_strike_counts_to_three(tmp_path, capsys):
    run(["revise-start", "--slug", "s1"], tmp_path)
    capsys.readouterr()
    for expected in (False, False, True):
        run(["strike", "--slug", "s1", "--defect-id", "dangling-ref"], tmp_path)
        assert json.loads(capsys.readouterr().out)["third_strike"] is expected


def test_revise_end_deactivates(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    run(["revise-end", "--slug", "s1", "--status", "stopped"], tmp_path)
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["active"] is False and d["status"] == "stopped"


def test_ledger_verbs_require_started_loop(tmp_path):
    assert run(["strike", "--slug", "ghost", "--defect-id", "d"], tmp_path) == 2
    assert run(["revise-round", "--slug", "ghost"], tmp_path) == 2


def test_revise_start_idempotent_on_live_marker(tmp_path, capsys):
    run(["revise-start", "--slug", "s1"], tmp_path)
    run(["revise-round", "--slug", "s1"], tmp_path)
    run(["strike", "--slug", "s1", "--defect-id", "d"], tmp_path)
    capsys.readouterr()
    assert run(["revise-start", "--slug", "s1"], tmp_path) == 0
    assert json.loads(capsys.readouterr().out).get("resumed") is True
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["round"] == 1 and d["strikes"] == {"d": 1}  # never-wedge counters preserved


def test_revise_start_force_restart_resets(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    run(["revise-round", "--slug", "s1"], tmp_path)
    run(["revise-start", "--slug", "s1", "--force-restart"], tmp_path)
    d = json.loads((tmp_path / "revise-s1.json").read_text())
    assert d["round"] == 0 and d["strikes"] == {}


def test_revise_start_rejects_insane_bounds(tmp_path):
    assert run(["revise-start", "--slug", "s1", "--max-rounds", "999"], tmp_path) == 2
    assert run(["revise-start", "--slug", "s1", "--ttl-hours", "0"], tmp_path) == 2
    assert not (tmp_path / "revise-s1.json").exists()


def test_strike_defect_id_rejects_path_chars(tmp_path):
    run(["revise-start", "--slug", "s1"], tmp_path)
    before = (tmp_path / "revise-s1.json").read_text()
    assert run(["strike", "--slug", "s1", "--defect-id", "../x"], tmp_path) == 2
    assert run(["strike", "--slug", "s1", "--defect-id", "a/b"], tmp_path) == 2
    assert (tmp_path / "revise-s1.json").read_text() == before  # no marker mutation
```

And `tests/test_revise_ledger_contract.py` (literal locks on the SKILL):

```python
"""R2 #7 — the 3-strike and max-rounds guards become countable artifacts:
scholar-revise runs oms_state.py verbs instead of self-counting."""
import re
from pathlib import Path

REVISE = (Path(__file__).parent.parent / "skills" / "scholar-revise" / "SKILL.md").read_text(encoding="utf-8")


def test_loop_start_and_end_are_wired():
    assert "revise-start" in REVISE and "revise-end" in REVISE
    assert re.search(r"every exit path|all exit paths|each exit path", REVISE, re.I)


def test_strike_is_mechanical():
    assert re.search(r"strike --defect-id", REVISE)  # the CLI invocation itself, not a stray mention
    assert "third_strike" in REVISE
    assert re.search(r"not self-report|countable|mechanical", REVISE, re.I)


def test_rounds_are_mechanical():
    assert "revise-round" in REVISE and re.search(r"exceeded", REVISE)


def test_citation_defects_never_striked():
    idx = REVISE.index("strike --")  # anchor on the invocation token, not any prose 'strike'
    assert re.search(r"fixable_by_llm=false|citation.{0,80}never", REVISE[max(0, idx - 500):idx + 800], re.I | re.S)
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement the verbs in `scripts/oms_state.py`** (shared `load`/atomic-write helpers; `time`/`datetime` for `started_at`; `uuid.uuid4()` for `round_id`).
- [ ] **Step 4: Edit `skills/scholar-revise/SKILL.md`** per the prompt contract (Steps 1/3/3c/4 + one Execution_Policy line replacing "Same defect recurs 3 times → stop" prose with the mechanical `third_strike` reference — keep the sentence, add the mechanism).
- [ ] **Step 5: Run** — green (target + full suite).
- [ ] **Step 6: Commit** — `git add scripts/oms_state.py skills/scholar-revise/SKILL.md tests/test_oms_state.py tests/test_revise_ledger_contract.py && git commit -m "feat(oms): revise marker + mechanical strike/round ledger (R2 #7)"`

---

### Task 3: Scoped Stop-guard hook (`scholar_stop_guard.py`) — item #8

**Files:**
- Create: `hooks/scholar_stop_guard.py`
- Modify: `.claude-plugin/plugin.json` (add Stop block)
- Test: `tests/test_scholar_stop_guard.py`, extend `tests/test_plugin_integrity.py`

**Interfaces:**
- Consumes: `revise-<slug>.json` + `pilot-<slug>.json` (T1/T2), located by directory ascent from payload `cwd`.
- Produces: on block — `{"decision": "block", "reason": "…"}` on stdout, exit 0 (verified Stop-hook contract; Stop has NO matcher in plugin.json). Silence (no output, exit 0) = allow stop.

Behavior contract (the scoped, exemption-laden variant — §6 of the plan explicitly bans a blunt always-block loop):
1. `OMS_STOP_GUARD` env in `{off,0,false}` → exit 0 (never advertised in the reason).
2. Ascend from `cwd` to the NEAREST `.oms/state/` dir (first hit — never enumerate ancestors past it); no dir or no `revise-*.json` → exit 0. A found marker is **in scope** only when it carries a `paper_root` and the session `cwd` equals or is a descendant of it — out-of-scope markers (including hand-written ones missing `paper_root`) are ignored. Scope claim, stated honestly: the guard has zero effect outside the tree where a loop was actually started; *within* that tree (multi-session on one paper — by design) staleness is bounded by TTL/exemptions. Residual ceiling: a loop started from a broad workspace root scopes to that root — the user's own topology choice, still TTL/cap-bounded.
3. For each marker, ALL of the following must hold to block; ANY exemption → skip that marker (and if no marker blocks → exit 0):
   - `active` is true and `status == "live"`;
   - no strike ≥ 3 in `strikes`;
   - `round < max_rounds`;
   - marker age (now − `started_at`) < `ttl_hours` — computed skew-safe: a *negative* age (`started_at` in the future = clock skew) counts as exempt (skew must never extend the guard);
   - sibling `pilot-<slug>.json` (if present) has `gate_status != "abort"`;
   - `stop_blocks < max(10, 2 × max_rounds)` (hard cap — the guard gives up before a human has to).
4. On block: increment the marker's `stop_blocks` via `atomic_write_json` (durable — survives across stop attempts), then print the block JSON. Reason text: `[oms stop-guard] revise loop for '<slug>' is live (round R/M, open strikes: …): continue the revise-verify loop until PASS or a stop condition, or end it explicitly with `python3 <plugin>/scripts/oms_state.py revise-end --slug <slug> --status stopped` and report to the human. Citation/content defects are NEVER looped — escalate those to the human instead.` (The revise-end escape is *advertised deliberately* — the model ending the loop explicitly and reporting is the desired behavior, unlike the cite-guard's hidden env hatch.)
5. `stop_hook_active` true in the payload does not by itself exempt (the loop is allowed to persist across multiple stop attempts — that is its purpose). The docs define the field ("true when Claude Code is already continuing as a result of a stop hook. Check this value … to avoid blocking on a condition that will never resolve") and, decisively, document the platform's own structural backstop: **"Claude Code overrides the hook and ends the turn after 8 consecutive blocks"** (code.claude.com/docs/en/hooks.md, fetched 2026-07-13). So the true anti-infinite-block guarantee is the platform's 8-consecutive-block override *per stopping cycle*; the guard's durable `stop_blocks` cap in (3) is the secondary, *cross-turn* safeguard that makes the guard give up permanently over the marker's lifetime (the platform limit resets each cycle; the counter does not).
6. Any exception, unreadable marker, malformed JSON → exit 0 (fail-open; also: if incrementing `stop_blocks` fails, still allow — never trade a wedge for a count).

- [ ] **Step 1: Write failing tests** (`tests/test_scholar_stop_guard.py`; reuse the `run_hook` subprocess idiom from `test_scholar_cite_guard.py` — payload is `{"hook_event_name": "Stop", "cwd": str(tmp_path), "stop_hook_active": false}`; helper `mk_marker(tmp_path, **overrides)` writes `.oms/state/revise-s1.json` with live defaults **including `paper_root: str(tmp_path)`**):
  - `test_blocks_while_live_marker` — live marker → stdout JSON `decision == "block"`, reason names the slug and `revise-end`;
  - `test_silent_without_marker` / `test_silent_when_inactive` (`active: false`) / `test_silent_when_done` (`status: "done"`);
  - `test_third_strike_exempts` (`strikes: {"d": 3}`) / `test_max_rounds_exempts` (`round: 5, max_rounds: 5`) / `test_ttl_exempts` (`started_at` 7h ago, `ttl_hours: 6`) / `test_abort_gate_exempts` (sibling pilot with `gate_status: "abort"`);
  - `test_stop_blocks_cap_scales` — discriminates the `max(10, 2×max_rounds)` formula from a hardcoded 10: with `max_rounds: 8` (cap 16), `stop_blocks: 10` still blocks and `stop_blocks: 16` exempts; with defaults (`max_rounds: 5`), `stop_blocks: 10` exempts;
  - **scoping**: `test_ancestor_marker_ignored_when_local_state_exists` (live marker at a grandparent `.oms/state/`, session cwd has its own empty `.oms/state/` → silent — nearest-first ascent) / `test_marker_outside_paper_root_silent` (marker in a shared ancestor state dir with `paper_root: <ancestor>/paperA`, session cwd `<ancestor>/other` → silent — containment) / `test_marker_missing_paper_root_silent` (hand-written marker without `paper_root` → silent);
  - `test_future_started_at_exempts` (`started_at` 1h in the future → allow stop — skew-safe TTL);
  - `test_block_increments_stop_blocks_durably` — run twice, marker's `stop_blocks` goes 0→1→2 on disk;
  - `test_env_escape_hatch` (`OMS_STOP_GUARD=off` → silent) and `test_reason_never_advertises_env_hatch` (`"OMS_STOP_GUARD" not in reason`);
  - `test_reason_forbids_citation_looping` (reason contains `NEVER looped` / `escalate`);
  - `test_fail_open_on_bad_input` (`"not json"`) / `test_fail_open_on_corrupt_marker` (marker file contains `{broken`) — both silent exit 0.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `hooks/scholar_stop_guard.py`** (docstring: scoped Stop guard — blocks only while a live revise marker exists and no exemption fires; the blunt "never stop" loop is deliberately out of scope per advancement-plan §6; lists the six exemptions). Reuse the ascent idiom from `scholar_cite_guard.allowlisted_keys`; import `atomic_write_json` via `sys.path` for the counter increment.
- [ ] **Step 4: Register in `.claude-plugin/plugin.json`** — `"Stop": [{"hooks": [{"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/scholar_stop_guard.py"]}]}]` (no matcher — Stop hooks have none). Extend `tests/test_plugin_integrity.py`: `test_stop_guard_registered` (⑥).
- [ ] **Step 5: Run** — green (target + integrity + full suite).
- [ ] **Step 6: Commit** — `git add hooks/scholar_stop_guard.py .claude-plugin/plugin.json tests/test_scholar_stop_guard.py tests/test_plugin_integrity.py && git commit -m "feat(oms): scoped Stop-guard for the revise loop — marker-gated, exemption-laden (R2 #8)"`

---

### Task 4: Verifier round-id echo — item #10

**Files:**
- Modify: `agents/scholar-verifier.md`, `skills/scholar-revise/SKILL.md`
- Test: `tests/test_round_id_contract.py`

**Interfaces:**
- Consumes: T2's `revise-round` verb already mints and stores `round_id` (this task is pure prompt contract — no code).
- Produces: the verifier echoes the round-id it was handed; the revise loop rejects verdicts whose echo mismatches the marker's current `round_id`.

Prompt contract:
- `agents/scholar-verifier.md`:
  - `<Constraints>` snapshot-token bullet gains a sentence: `When the calling skill hands you a **round-id** (revise loop), echo it verbatim in the Round ID line of your verdict — a verdict without the exact round-id it was asked to carry is void for that round (the un-adopted half of the ralph correlation pattern, now adopted: controller-issued per-round id).`
  - `<Output_Format>` summary block, directly under the `**Target snapshot**` line, add: `**Round ID**: [echo the round-id from the task prompt, or "none given"]`
  - `<Final_Checklist>` add: `- Did you echo the round-id handed to you (if any) verbatim in the Round ID line?`
- `skills/scholar-revise/SKILL.md` Step 3b gains: include the current `round_id` (from `revise-round`) in the verifier Task prompt and accept the verdict only if the echoed Round ID matches — a mismatched or missing echo means a stale/crossed verdict: discard it and re-verify (do not count that round).

- [ ] **Step 1: Write failing tests** (`tests/test_round_id_contract.py` — literal locks: verifier has `Round ID` in Output_Format + echo constraint + checklist entry; revise SKILL passes round_id into the verifier prompt and discards mismatched echoes; lock the void-if-mismatch semantics with `re.search(r"(void|discard|stale).{0,120}(round[- _]?id)|round[- _]?id.{0,120}(void|discard|stale)", …, re.I | re.S)` on both files).
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Apply the two prompt edits** (surgical).
- [ ] **Step 4: Run** — green (target + full suite).
- [ ] **Step 5: Commit** — `git add agents/scholar-verifier.md skills/scholar-revise/SKILL.md tests/test_round_id_contract.py && git commit -m "feat(oms): verifier round-id echo — controller-issued per-round correlation (R2 #10)"`

---

### Task 5: SessionStart resume advisory + post-compaction Priority-Context re-injection (`scholar_resume_emit.py`) — items #9 + #13

**Files:**
- Create: `hooks/scholar_resume_emit.py`
- Modify: `.claude-plugin/plugin.json` (add SessionStart block)
- Test: `tests/test_scholar_resume_emit.py`, extend `tests/test_plugin_integrity.py`

**Interfaces:**
- Consumes: `pilot-*.json` + `revise-*.json` (ascent from `cwd`), `.oms/notepad.md` `## Priority Context` section (sibling of the found `state/` dir, i.e. `<root>/.oms/notepad.md`).
- Produces: `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "<oms-resume>…</oms-resume>"}}` on stdout, exit 0. Silence = nothing to advise (the common case — zero injection tax on non-paper sessions, deliberately unlike the route hook).

Behavior contract:
1. Read payload; `source` ∈ {startup, resume, clear, compact}.
2. Ascend from `cwd` to the NEAREST `.oms/state/` (first hit only); collect non-terminal pilot states (`stage != "terminal"` and `gate_status != "abort"`) and live revise markers — but only records whose `paper_root` contains the session `cwd` (same containment scoping as the Stop guard; records missing `paper_root` are ignored).
3. Compose `<oms-resume>` when there is anything to say:
   - Per non-terminal slug: `slug · stage · gate_status · open_fail_ids (count + ids) · live revise marker (round R/M, strikes summary)` + one closing line: `Advisory only — GATEs stay human. Resume with scholar-pilot --from <stage>; discard with oms_state.py write --slug <slug> --gate-status abort.`
   - When `source == "compact"`: additionally re-inject the notepad's `## Priority Context` section verbatim (bounded: first 2,000 characters; if the section is absent or the notepad missing, skip silently). This is #13, and the section pilot writes there carries **all three spec-named elements** — the citation-safety principles, the current GATE position (`GATE n/3`), and the open unverified-citation list — which survive compaction because SessionStart(compact) re-injects them into the fresh context. On `source == "compact"` the Priority Context is re-injected **even when no non-terminal pilot state exists** (a mid-stage session outside pilot still relies on it, if the section exists).
4. Nothing found (no state dir, no non-terminal states, and — for compact — no Priority Context) → exit 0 silent.
5. Fail-open everywhere; the hook never writes anything (read-only).

- [ ] **Step 1: Write failing tests** (`tests/test_scholar_resume_emit.py`; subprocess idiom; payload `{"hook_event_name": "SessionStart", "source": …, "cwd": str(tmp_path)}`; helpers write pilot/revise/notepad fixtures under `tmp_path/.oms/`):
  - `test_silent_when_no_state` (source=startup, empty dir → stdout empty);
  - `test_advisory_names_stage_and_gate` (pilot s1 stage=draft gate_status=pending → additionalContext contains `<oms-resume>`, `s1`, `draft`, `pending`, `Advisory only`);
  - `test_terminal_and_abort_states_are_silent` (stage=terminal; gate_status=abort → silent);
  - `test_live_revise_marker_reported` (marker round 2/5 → `2/5` or `round 2` in context);
  - `test_compact_reinjects_priority_context` (notepad `## Priority Context` fixture with all three elements — a citation-safety principles line, a `GATE 2/3` line, and an `unverified citations: kim2024, lee2025` line — + no pilot state, source=compact → context carries the section body including the unverified-citation list verbatim);
  - `test_startup_does_not_inject_priority_context_without_state` (same fixture, source=startup → silent);
  - `test_compact_bounds_priority_context` (section body of 10,000 chars → injected ≤ ~2,100 chars);
  - `test_sibling_cwd_not_under_paper_root_silent` (pilot state + marker in a shared ancestor state dir with `paper_root: <ancestor>/paperA`, session cwd `<ancestor>/other`, source=startup → silent — containment scoping);
  - `test_output_is_wellformed_hookspecificoutput` (json parse: `hookEventName == "SessionStart"`);
  - `test_fail_open_on_bad_input` (`"not json"` → silent exit 0);
  - `test_fail_open_on_corrupt_notepad` (`.oms/notepad.md` is a directory, or contains undecodable bytes → silent exit 0 on source=compact);
  - `test_hook_is_read_only` (source scan: no `atomic_write_json`, no `open(...,"w")` / `write_text` in the hook file).
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `hooks/scholar_resume_emit.py`** (docstring: #9 resume advisory + #13 post-compaction Priority-Context re-injection; names the verified-contract reason PreCompact was NOT used). Section extraction: from `## Priority Context` to the next `^## ` heading (Python `re`, MULTILINE).
- [ ] **Step 4: Register in `.claude-plugin/plugin.json`** — `"SessionStart": [{"matcher": "startup|resume|clear|compact", "hooks": [{"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/scholar_resume_emit.py"]}]}]`. Extend `tests/test_plugin_integrity.py`: `test_resume_emit_registered` (⑦) asserting the script AND the `compact` matcher.
- [ ] **Step 5: Run** — green (target + integrity + full suite).
- [ ] **Step 6: Commit** — `git add hooks/scholar_resume_emit.py .claude-plugin/plugin.json tests/test_scholar_resume_emit.py tests/test_plugin_integrity.py && git commit -m "feat(oms): SessionStart resume advisory + post-compaction Priority-Context re-injection (R2 #9+#13)"`

---

### Task 6: Abort/interrupt spec + notepad 3-tier convention — items #11 + #12

**Files:**
- Modify: `skills/scholar-pilot/SKILL.md`, `references/output-layout.md`
- Test: extend `tests/test_state_schema_docs.py`

**Interfaces:** none new (prose contracts over T1's schema).

Prompt contract:
- **#11 — `skills/scholar-pilot/SKILL.md`**, new section `<Interruption_And_Resume>` after `<Steps>`:
  - **On entry**: run `oms_state.py read`; if a non-terminal `pilot-<slug>.json` exists for this paper, surface it BEFORE starting any stage: "A pipeline marker exists (stage X, gate_status Y, updated_at Z) — resume from X / restart from an earlier stage / discard?" (AskUserQuestion when available). Never silently restart from stage 1 over a live marker.
  - **Abort semantics**: "discard" writes `gate_status=abort` (and `revise-end --status abort` if a live revise marker exists). `abort` is terminal: the advisory (T5) stops reporting it, the Stop guard stops honoring its marker, and the state files become cleanup-eligible (§5 of output-layout).
  - **Stale-marker rule**: `updated_at` older than 14 days → present as *stale* ("probably an abandoned run — discard unless you recognize it"); still the human's call.
  - **Mid-stage interruption**: a user interrupt mid-stage leaves the last boundary write as the resume point — document that this is exactly why every boundary writes (T1): the marker is always at most one stage behind reality.
- **#12 — `references/output-layout.md`**: add `.oms/notepad.md` to the §2 tree (workbench, cross-slug like `state/`), and a **§2.3 "notepad tiers"** subsection:
  - `## Priority Context` — replace-on-write (pilot entry and every GATE transition rewrite the whole section; it must stay short — it is what SessionStart(compact) re-injects, bounded to 2,000 chars);
  - `## Working Notes` — dated append (`### YYYY-MM-DD` sub-headings); at pilot entry, prune entries older than 7 days (the only automated deletion, and it is tier-scoped);
  - `## Manual` — human-owned; automation never writes or prunes here.
  - One-line pointer added to scholar-pilot's existing Priority-Context bullet in `<Execution_Policy>`: `(tiers: references/output-layout.md §2.3 — Priority Context replace-on-write / Working Notes dated-append, 7-day prune at pilot entry / Manual never touched)`.
- [ ] **Step 1: Write failing tests** — extend `tests/test_state_schema_docs.py`: pilot SKILL has `Interruption_And_Resume` (or equivalent heading) + `resume|discard` choice + `abort` terminal semantics + `stale` + `14 days`; layout documents `notepad.md` + the three tier names + `replace-on-write` + `7 day|7-day|7d` prune + `never` for Manual; pilot Execution_Policy points to §2.3.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Apply the two edits** (surgical).
- [ ] **Step 4: Run** — green (target + full suite).
- [ ] **Step 5: Commit** — `git add skills/scholar-pilot/SKILL.md references/output-layout.md tests/test_state_schema_docs.py && git commit -m "feat(oms): abort/interrupt spec + notepad 3-tier convention (R2 #11+#12)"`

---

### Task 7: Release — CHANGELOG 0.7.0 + README + full suite

**Files:**
- Modify: `CHANGELOG.md`, `README.md`
- Test: none new (existing `test_readme_evidence.py` must stay green; final full-suite count recorded).

- [ ] **Step 1: Edit `CHANGELOG.md`** — new `## [0.7.0] — 2026-07-13` above `[0.6.0]` (below `[Unreleased]`): **Added** — one bullet per mechanism with file paths (state schema + `oms_state.py` CLI; strike/round ledger; scoped Stop guard incl. the six exemptions + `OMS_STOP_GUARD` hatch; SessionStart resume advisory + compact re-injection; round-id echo; abort/interrupt spec; notepad tiers). **Notes** — (a) #13 implemented via `SessionStart(source: "compact")` not PreCompact (verified contract: PreCompact output does not survive compaction); (b) #14 (session envelope + lock) deliberately deferred pending an observed multi-session collision (plan §5 conditional); (c) stacked on the unmerged R1 branch — tag v0.7.0 only after both PRs merge (version-SSOT sync remains P2 #15). **Verification** — final `python3 -m pytest tests/ -q` count.
- [ ] **Step 2: Edit `README.md`** — Status line: `v0.7.0 — … + citation-safe hooks (\`scholar_route_emit\`/\`scholar_verify_emit\`/\`scholar_cite_guard\`/**\`scholar_stop_guard\`**/**\`scholar_resume_emit\`** + \`oms_atomic\`). Added in 0.7.0: **pipeline state & loop robustness (P1)** — .oms/state schema + oms_state CLI, mechanical strike/round ledger, scoped revise Stop-guard, SessionStart resume advisory + post-compaction Priority-Context re-injection, verifier round-id echo, abort/interrupt spec, notepad 3 tiers.` Keep the 0.6.0 sentence (history chain style). Update the quoted test count to the final one. If README enumerates hook count anywhere else ("third hook" phrasing from R1), reconcile.
- [ ] **Step 3: Run** — `python3 -m pytest tests/ -q` full suite green; README/CHANGELOG quote the real final count.
- [ ] **Step 4: Commit** — `git add CHANGELOG.md README.md && git commit -m "docs(oms): v0.7.0 release notes — pipeline state & loop robustness (R2 P1)"`

---

## Self-Review (done at plan time)

- **Spec coverage**: #6→T1, #7→T2, #8→T3, #9→T5, #10→T4, #11→T6, #12→T6, #13→T5 (mechanism deviation documented + CHANGELOG-noted), #14→deliberate deferral (documented). Sequencing honored: T1 defines the schema T2 extends; T3 consumes T2's marker; T4 consumes T2's `round_id`; T5 reads T1/T2's files; T6 documents over T1's schema.
- **Invariants**: no auto-fix anywhere; citation/content defects never enter strikes, loop, or block reasons as loopable; single-careful generation untouched (all of R2 is state/loop plumbing, no generation change); stdlib only; every hook fail-open; human GATEs untouched (advisory is advisory, abort/resume/discard are human choices).
- **Never-wedge**: Stop guard has six independent escapes (env hatch, inactive marker, strikes, rounds, skew-safe TTL, durable stop_blocks cap) + fail-open on any error + the documented platform override ("ends the turn after 8 consecutive blocks") as the structural backstop; `revise-end` is deliberately advertised in the block reason; `revise-start` is idempotent on resume so counters survive crash/compaction recovery.
- **Scoping**: both hooks are paper_root-contained + nearest-first — a stale ancestor marker can never guard or advise an unrelated session (regression-tested in T3 and T5).
- **Type consistency**: marker/state shapes identical across T1/T2 CLI, T3 guard, T5 advisory, output-layout §2.2, and all test fixtures (`pilot-<slug>.json` / `revise-<slug>.json`, field names as in the schemas above, `paper_root` recorded by the CLI in both). `round_id` minted in exactly one place (`revise-round`).
- **Injection budget**: unlike the route hook (audit finding: 4.4 KB unconditional), both new hooks are silent by default — they emit only when a live pipeline exists (advisory) or after compaction with a Priority Context present (bounded 2 KB).
