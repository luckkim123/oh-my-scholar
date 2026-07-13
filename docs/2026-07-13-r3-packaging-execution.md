# R3 — Packaging & Authoring Hygiene (P2 #15–#22) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the packaging/hygiene drift the advancement audit measured: a version SSOT with a mechanical 4-surface sync check (#15), the atomic writer finally wired to its own motivating case (#16), the `consensus/` schema drift closed in the layout SSOT (#17), a read-only `oms doctor` that would have caught the historical 4-way version drift at commit time (#18), agent cross-reference integrity tests that close the silent-typo class (#19), the verifier re-tiered to sonnet (#20), the always-loaded skill corpus compacted below OMC's 64 KiB budget via the shim + `skill-bodies/` split (#21), and a `DISABLE_OMS` kill switch plus a route-hook relevance gate that stops taxing non-paper turns 4.4 KB (#22) — release as v0.8.0, branched from main (R1/R2 both merged; this branch does NOT stack).

**Architecture:** Two new stdlib CLIs in `scripts/` — `sync_version.py` (pure drift-checker over the 4 version surfaces; the omha card surface is optional and skip-if-absent) and `oms_doctor.py` (read-only categorized PASS/WARN/FAIL self-diagnosis that *reuses* sync_version's checks and adds hooks/agents/skills structure checks). One library addition: `atomic_write_text` in `hooks/oms_atomic.py` (shared core with `atomic_write_json`). One repo-shape change: all 12 `skills/<name>/SKILL.md` bodies move to `skill-bodies/<name>/SKILL.md` (git mv) and each `skills/<name>/SKILL.md` becomes a compact shim carrying the original frontmatter verbatim + a pointer body (OMC §16's exact sibling adaptation); every literal-lock test that reads skill text is repointed through a new `tests/conftest.py` helper. Hook changes are additive: a `DISABLE_OMS` early-exit in all 5 registered hooks, and a keyword relevance gate in `scholar_route_emit.py` that skips injection on clearly non-paper prompts (fail-toward-inject). Spec = `docs/2026-07-11-oms-advancement-plan.md` §5 P2.

**Design decisions (deliberate, verified against the repo 2026-07-13):**

- **#15 tag semantics — a "pre-tag window" is legal.** Tags are cut by the human *after* merge (R1/R2 precedent), so at the release commit the latest tag is one release behind. Sync rule: `plugin.json version == CHANGELOG top released entry` always; `latest v* tag ∈ {plugin version, previous released version}`. Anything else (tag ahead, tag two behind, plugin ≠ CHANGELOG) is drift. The historical v0.4.0/v0.5.0 tag gap is irrelevant — only the *latest* tag is checked (documented in the script docstring so nobody "fixes" history retroactively).
- **#15 omha card is a foreign surface — locate via env, skip-if-absent, never edit.** The card lives in a different repo (`oh-my-heroacademia/cards/oms.json`). `sync_version.py` resolves it via `OMHA_ROOT` env (default `~/oh-my-heroacademia`); absent → surface reported as SKIP (fail-open, exit unaffected); present + version mismatch → DRIFT. The card's own version bump is a **separate PR in oh-my-heroacademia** (process step at release time, never part of this repo's diff). The *live* pytest self-check deliberately excludes the card surface: the card is currently 0.1.0 on the dev machine and its fix rides a separate PR — a local suite must not go red over a foreign repo's pending PR.
- **#16 — `atomic_write_text`, NOT a YAML→JSON migration.** `references/venues.md:113` pins `.oms/venues/<key>.yaml` as the schema surface and `skills/scholar-learn/SKILL.md:109` edits those files; migrating the format would ripple through both for zero safety gain. Instead `oms_atomic.py` gains `atomic_write_text` (same mkstemp + fsync + `os.replace` core, refactored to share). The scholar-init sentence `(via oms_atomic's atomic write — if json; for yaml use a plain write)` is **the defect itself** and is replaced — a named exception to the additive-only rule (grep-verified: no test pins that sentence; `grep -rn "plain write" tests/` → 0 hits).
- **#21 shim — the routing surface is frozen.** Each shim keeps the original frontmatter **byte-identical** (name/description/triggers are what omha and the user-visible skill list route on) plus one additive `oms-full-body:` metadata key; the body paragraph follows OMC's proven omc-reference shim wording (points to `${CLAUDE_PLUGIN_ROOT}/skill-bodies/<name>/SKILL.md`, states the plugin root is the directory containing both `skills/` and `skill-bodies/`). Bodies keep their full original content (frontmatter copy included — harmless, and it keeps `git mv` history clean). `plugin.json` still lists `./skills/<name>/` — the 1:1 integrity contract (`test_plugin_integrity.py`) is untouched by construction.
- **#22 gate fails toward injection.** Missing `prompt` key, undecodable payload, or any exception → inject (today's behavior). The gate only suppresses injection when the prompt parses cleanly AND contains no paper token. False positive (needless injection) = status quo; false negative costs one turn's STAGE checkpoint — mitigated by a generous KR+EN token list. When injected, the CHECKPOINT text stays **byte-identical** (existing literal locks prove it).
- **Scope guard — R2 carry-overs stay out.** From the PR #7 body Notes list: the two hooks' nearest-root asymmetry (unify or intent-comment), `oms_state.py` slug error-string DRY (6 sites) + the 4 deferred tests (create-without-stage · garbage started_at · resume/clear negative gate · multi-marker cap serialization doc), and **commenting the empty-Priority-Context drop**. From the R2 session record (not in the PR body): the compact-time SessionStart "6 fires" investigation. All are recorded again in the v0.8.0 CHANGELOG Notes as still-deferred; none are R3 work.

**Tech Stack:** Python 3 stdlib only (json, os, sys, re, ast, argparse, pathlib, subprocess for git-tag read, tempfile), pytest, markdown prompt contracts.

## Global Constraints

- stdlib only — no third-party imports in `hooks/` or `scripts/` (repo invariant; tests enforce).
- All hooks fail-open: any parse/IO error → exit 0. The kill switch and the relevance gate must never invert this (an exception in the gate → inject, not crash; an exception reading env → proceed as if unset).
- Prompt-contract edits are surgical and additive-only (keep surrounding text and heading numbering intact; English corpus) — the ONE named exception is the scholar-init "plain write" sentence (#16, see Design decisions).
- Every task ends with `python3 -m pytest tests/ -q` green (baseline **213 passed**; later tasks keep it green at higher counts).
- Worktree: `/Users/kimseungmin/oh-my-scholar/.claude/worktrees/oms-r3`, branch `feat/r3-packaging`, **base: main @ 423e277** (R1/R2 merged — not stacked). Commit per task, message style `feat(oms): …` matching git log.
- **Pitfalls from prior releases (measured, all four bind here):**
  1. A test fix that *adds a lock* carries a discriminance-proof duty: before committing, demonstrate the lock FAILs when the target sentence/token is removed (run once with the target text temporarily reverted, or assert on a token that exists only in the new text).
  2. grep-based commit/tag SHA extraction must anchor exactly — the R2 incident: `--grep "#6"` also matched "#6–#13". Use full-token anchors (`v0.7.0` not `0.7`), and in `sync_version.py` parse tags by exact `^v(\d+)\.(\d+)\.(\d+)$` match, never substring.
  3. Tests pin **content tokens**, not just file existence (vacuous locks banned): every new lock asserts a token that only the intended edit introduces.
  4. After the #21 split, every pre-existing regression lock must read the **skill-bodies** path (via the conftest helper) — T5's checklist includes a full-suite discriminance spot-check (corrupt one moved body token → the repointed test FAILs).

---

### Task 1: Version SSOT + `sync_version.py` — item #15

**Files:**
- Modify: `.claude-plugin/plugin.json` (add `"version": "0.7.0"` — the anchor surface, matching the current released CHANGELOG top; T7 bumps it to 0.8.0 together with the CHANGELOG)
- Create: `scripts/sync_version.py`
- Test: `tests/test_version_sync.py`

**Interfaces:**
- The 4 surfaces: ① `plugin.json` `version` (anchor) ② CHANGELOG top *released* entry (first `^## \[(\d+\.\d+\.\d+)\]` — `[Unreleased]` is skipped) ③ latest git tag (all `v*` tags parsed by `^v(\d+)\.(\d+)\.(\d+)$`, max by numeric tuple; read via `subprocess.run(["git","-C",repo_root,"tag","-l","v*"], …)`) ④ omha card `<OMHA_ROOT>/cards/oms.json` `version` key (optional surface).
- Pure core, testable without a repo: `check(plugin, changelog_top, changelog_prev, latest_tag, card) -> list[str]` returning human-readable drift strings (empty = in sync). Rules: `plugin == changelog_top`; `latest_tag in (plugin, changelog_prev)` when any tag exists (no tags at all → tag surface SKIP — a fresh clone without tags must not fail); `card == plugin` when card is not None. **The card drift string carries a machine-routable `card:` prefix** — the card is a foreign surface, and downstream consumers (oms_doctor, T3) must be able to route it to WARN while every other drift stays FAIL.
- Gathering: `gather(repo_root) -> dict` reads the three local surfaces + resolves the card path from `os.environ.get("OMHA_ROOT", "~/oh-my-heroacademia")` (expanduser); unreadable/absent card → `card=None`.
- CLI: `python3 scripts/sync_version.py [--repo-root D]` prints one row per surface (`PASS` / `SKIP (reason)` / `DRIFT: …`) and exits 0 iff no drift, 1 otherwise. Read-only — never writes any file.

- [ ] **Step 1: Write failing tests** — `tests/test_version_sync.py` (import via `importlib.util` like `test_verify_bib_entry.py`):
  - `test_in_sync_passes` — `check("0.8.0","0.8.0","0.7.0","v0.7.0","0.8.0") == []` (pre-tag window) and `check("0.8.0","0.8.0","0.7.0","v0.8.0","0.8.0") == []` (post-tag).
  - `test_plugin_changelog_drift_detected` — `check("0.8.0","0.7.0",…)` names both values in the drift string.
  - `test_tag_two_behind_is_drift` — `latest_tag="v0.6.0"` with plugin 0.8.0/prev 0.7.0 → drift.
  - `test_tag_ahead_is_drift` — `latest_tag="v0.9.0"` → drift.
  - `test_no_tags_skips_tag_surface` — `latest_tag=None` → no tag drift (fresh clone).
  - `test_card_absent_skips` — `card=None` → no card drift (fail-open, the foreign-repo rule).
  - `test_card_mismatch_is_drift` — `card="0.1.0"` vs plugin 0.8.0 → drift naming the card surface AND starting with the `card:` prefix (the routing token T3's doctor depends on).
  - `test_changelog_parser_skips_unreleased` — parser fixture: a CHANGELOG string with `## [Unreleased]` above `## [0.8.0]` → top released is 0.8.0 (drive the module's changelog-parsing function directly on a tmp file).
  - `test_tag_parse_is_exact_match` — tag list `["v0.7.0", "v0.7.0-rc1", "x0.9.9", "v10.0"]` → latest is `v0.7.0` (pitfall 2: no substring/prefix matching).
  - `test_live_repo_surfaces_agree` — **the live lock**: real `plugin.json` version == real CHANGELOG top released entry; if any `v*` tag exists in the repo, latest tag ∈ {plugin version, previous released}. Deliberately does NOT touch the omha card (Design decisions). This is the test that forces every future release commit to bump plugin.json and CHANGELOG together.
  - `test_cli_read_only` — source scan: no `atomic_write_json`, no `open(..., "w")`/`write_text` in `sync_version.py`.
- [ ] **Step 2: Run to verify failure** (module absent; plugin.json has no version).
- [ ] **Step 3: Implement** — add `"version": "0.7.0"` to plugin.json (top, after `"name"`); write `scripts/sync_version.py` (docstring: the 4 surfaces, the pre-tag-window rule, the foreign-card skip rule, and why only the *latest* tag is checked — the v0.4.0/v0.5.0 historical gap is not retro-fixed).
- [ ] **Step 4: Run** — target tests green, then full suite green (baseline 213 + new).
- [ ] **Step 5: Commit** — `git add .claude-plugin/plugin.json scripts/sync_version.py tests/test_version_sync.py && git commit -m "feat(oms): version SSOT in plugin.json + 4-surface sync checker (R3 #15)"`

---

### Task 2: Wire the atomic writer + `consensus/` in the layout SSOT — items #16 + #17

**Files:**
- Modify: `hooks/oms_atomic.py` (add `atomic_write_text`), `skills/scholar-init/SKILL.md` (line ~71 venue-config sentence), `references/output-layout.md` (§2 tree + §5.2 cleanup scope + §6 checklist)
- Test: extend `tests/test_oms_atomic.py`; extend `tests/test_md_stage_layout.py` (or a small new `tests/test_consensus_layout.py` if that file's shape doesn't fit); extend `tests/test_scholar_init_skill.py`

**Interfaces:**
- `atomic_write_text(target, text: str) -> None` — same guarantees as `atomic_write_json` (parent mkdir, same-dir mkstemp, fsync, `os.replace`, temp cleanup on failure, UTF-8, Korean preserved). Refactor the shared core so both writers use one code path (e.g. private `_atomic_write(target, dump_fn)`); `atomic_write_json` behavior byte-for-byte unchanged (existing tests prove it).
- scholar-init venue-config sentence becomes: `.oms/venues/<key>.yaml` written **via `oms_atomic.atomic_write_text`** (the YAML text is composed first, then written atomically — no more plain-write carve-out). This is the named additive-only exception.
- output-layout.md gains `consensus/` exactly as scholar-outline already writes it (`skills/scholar-outline/SKILL.md:91-97`): §2 tree gets a `consensus/` line under `.oms/<slug>/` annotated "per-run consensus handoff artifacts (`<stage>-<role>.md`) — written only in `--consensus` mode"; §5.2 cleanup scope gains a `consensus/` row (✅ clean at terminal — it is a workspace, the outline SKILL already calls it a T18 cleanup target); §6 checklist gains one consumer line (scholar-outline writes, T18 cleans).

- [ ] **Step 1: Write failing tests**
  - `tests/test_oms_atomic.py` additions: `test_atomic_write_text_roundtrip` (content + Korean preserved, file exists); `test_atomic_write_text_creates_parents` (nested target); `test_atomic_write_text_no_temp_left_behind` (after success, no `.oms-tmp-*` sibling); `test_text_and_json_share_atomic_core` (source scan: `os.replace` appears in the shared core exactly once / both public writers route through the shared helper — pin the refactor, not just the API).
  - Layout locks: `test_layout_documents_consensus_dir` (`consensus/` present in §2 tree region of output-layout.md AND a cleanup-fate mention in §5 — assert both tokens `consensus/` and a cleanup keyword within the §5 block; discriminance: neither token exists today, grep-verified 0 hits).
  - `tests/test_scholar_init_skill.py` addition: `test_venue_config_written_atomically` — scholar-init text contains `atomic_write_text` and no longer contains `for yaml use a plain write`.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — refactor `oms_atomic.py` (docstring gains one line: text variant exists so YAML state files get the same crash-safety; venue-config is the motivating case per the R3 audit); edit the scholar-init sentence; edit output-layout.md (three surgical insertions).
- [ ] **Step 4: Run** — green (target + full suite).
- [ ] **Step 5: Commit** — `git add hooks/oms_atomic.py skills/scholar-init/SKILL.md references/output-layout.md tests/test_oms_atomic.py tests/test_md_stage_layout.py tests/test_scholar_init_skill.py && git commit -m "feat(oms): atomic_write_text wired to venue config + consensus/ in layout SSOT (R3 #16+#17)"` (adjust the layout-test filename if a new file was chosen).

---

### Task 3: `oms doctor` — item #18

**Files:**
- Create: `scripts/oms_doctor.py`
- Test: `tests/test_oms_doctor.py`

**Interfaces:**
- Read-only categorized self-diagnosis, Paperpal-style fixed categories, each row `PASS` / `WARN` / `FAIL` + evidence:
  - **[version]** — reuse `sync_version.py` (`sys.path.insert` sibling import, the `scripts/` twin of the established hooks-import idiom): each drift string → FAIL row, **EXCEPT the omha-card surface: card absent (SKIP) AND card version-mismatch (`card:`-prefixed drift string) both map to WARN, never FAIL** — the card is a foreign surface whose bump rides a separate oh-my-heroacademia PR, and on this dev machine it legitimately sits at 0.1.0 until that PR merges; a doctor FAIL there would turn `test_live_repo_is_healthy` red at the T3 commit boundary.
  - **[hooks]** — every hook command registered in plugin.json resolves to an existing file under `hooks/` and parses (`ast.parse`) → FAIL if not; any `hooks/*.py` that is neither registered nor a known library module (`oms_atomic.py`) → WARN (orphan).
  - **[agents]** — every `agents/*.md` frontmatter parses; `name`/`description`/`model` present; `model` ∈ {haiku, sonnet, opus} → FAIL on violation. (The disallowedTools contract is T4's *test*; doctor checks only parseability + enum so the two don't drift apart on policy.)
  - **[skills]** — plugin.json `skills` ↔ `skills/` dirs 1:1 (same rule as `test_plugin_integrity.py`); **if** `skill-bodies/` exists (post-T5): `skills/` ↔ `skill-bodies/` 1:1 and every shim references its own body path → FAIL on violation. Doctor checks what exists — it must be green both before and after T5 lands.
  - **[state]** *(optional, only with `--paper-root D`)* — scan `D/.oms/<slug>/` dirs: slug dirs with a terminal/abort pilot state or no pilot state at all → WARN cleanup candidates (never FAIL — advisory, human decides; doctor never deletes).
- Exit 1 iff any FAIL; 0 otherwise. Never writes.

- [ ] **Step 1: Write failing tests** — `tests/test_oms_doctor.py` (importlib idiom; build tmp fixture repos with minimal plugin.json/hooks/agents where needed; run doctor's section functions directly rather than one giant main):
  - `test_live_repo_is_healthy` — doctor over the real repo root: zero FAIL rows (WARNs allowed — the omha card surface, absent OR mismatched, routes to WARN by design, so this stays green while `cards/oms.json` is 0.1.0 pending its separate PR). This is the "would have caught the 4-way drift" lock.
  - `test_version_drift_becomes_fail` — fixture repo with plugin 0.8.0 vs CHANGELOG 0.7.0 → a FAIL row naming both.
  - `test_unregistered_hook_file_warns` — fixture with a stray `hooks/extra_hook.py` → WARN, not FAIL; `oms_atomic.py` never flagged.
  - `test_missing_registered_hook_fails` — plugin.json registering a hook whose file is absent → FAIL.
  - `test_bad_agent_model_fails` — fixture agent with `model: gpt4` → FAIL.
  - `test_skills_mismatch_fails` — fixture with a skills/ dir missing from plugin.json → FAIL.
  - `test_state_scan_warns_on_terminal_slug` — `--paper-root` fixture: slug dir with `pilot-<slug>.json` `stage: terminal` → WARN row naming the slug; live slug → no row.
  - `test_doctor_read_only` — source scan: no write APIs in `oms_doctor.py`.
  - `test_exit_codes` — fixture healthy → 0; fixture with FAIL → 1.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `scripts/oms_doctor.py`** (docstring: read-only; the categories; the direct causal motivation — the 4-way version drift accumulated over 3 untagged releases because nothing checked surface agreement; doctor is that check, sync_version is its version section).
- [ ] **Step 4: Run** — green (target + full suite).
- [ ] **Step 5: Commit** — `git add scripts/oms_doctor.py tests/test_oms_doctor.py && git commit -m "feat(oms): oms doctor — read-only packaging self-diagnosis (R3 #18)"`

---

### Task 4: Agent cross-reference integrity tests + verifier re-tier — items #19 + #20

**Files:**
- Modify: `agents/scholar-verifier.md` (frontmatter `model: opus` → `model: sonnet`; description suffix `(Opus)` → `(Sonnet)` — the only two changes, everything else untouched); `references/rubrics/paper-eval.md` (line ~13 says `scholar-verifier (opus, read-only)` — a LIVE evaluation SSOT card read by scholar-verify, not a historical audit; reconcile to sonnet); `README.md` if it names the verifier tier (line ~71 does — reconcile)
- Test: `tests/test_agent_integrity.py` (new)

**Interfaces:**
- Frontmatter contract (from the audit's live-key inventory): every `agents/*.md` has `name`/`description`/`model`; `model` ∈ {haiku, sonnet, opus}; every agent EXCEPT `scholar-drafter` carries `disallowedTools` including `Write` and `Edit`; `scholar-drafter` carries NO `disallowedTools` (it is the single writer — lock the author/reviewer asymmetry from BOTH sides, same both-sides idiom as the triple self-approval ban).
- Cross-reference contract: every `subagent_type="oh-my-scholar:<X>"` occurrence across `skills/**/SKILL.md` AND `skill-bodies/**/SKILL.md` (glob both — T5-order-independent) resolves to an existing `agents/<X>.md`. Regex `r'subagent_type="oh-my-scholar:([a-z-]+)"'` (the verified live form; also scan the unquoted variant `oh-my-scholar:[a-z-]+` inside `Task(` lines to catch prose-form references).
- Tier lock: `scholar-verifier` frontmatter `model` is `sonnet` and its description says `(Sonnet)` — pins #20 so a future edit can't silently revert the tier (the audit's routing-economics rationale goes in the test docstring, not the agent file).

- [ ] **Step 1: Write failing tests** — `tests/test_agent_integrity.py`:
  - `test_all_agents_have_live_keys` / `test_model_values_are_valid_tiers`
  - `test_reviewer_agents_block_writes` (5 agents have disallowedTools ⊇ {Write, Edit}) / `test_drafter_is_the_only_writer` (drafter has no disallowedTools key)
  - `test_skill_agent_references_resolve` (cross-ref scan; must FAIL today only if a dangling ref exists — expected green; its discriminance proof: temporarily typo one `subagent_type` locally → FAIL, revert)
  - `test_every_agent_is_reachable` — every `agents/*.md` name is referenced by at least one skill (catches dead agents; if legitimately unreferenced agents exist at implementation time, downgrade this one assert to a WARN-style skip with a comment naming them — decide from evidence, don't force it)
  - `test_verifier_is_sonnet` (frontmatter `model: sonnet` + description `(Sonnet)`, `(Opus)` absent) — RED until the frontmatter edit lands in this same task.
- [ ] **Step 2: Run to verify failure** (`test_verifier_is_sonnet` RED; cross-ref tests likely green — their discriminance is proven by the temporary-typo check, pitfall 1).
- [ ] **Step 3: Apply the verifier frontmatter edit** (2 tokens). Grep for stale tier references: `grep -rn "verifier.*[Oo]pus\|Opus.*verifier" README.md references/ docs/` — known hits (verified at plan time): `README.md:71` and `references/rubrics/paper-eval.md:13` (`scholar-verifier (opus, read-only)`). Reconcile BOTH so no live surface still asserts the verifier is opus — paper-eval.md is a live SSOT card consumed by scholar-verify, so the "leave historical docs alone" carve-out covers ONLY `docs/` audit records.
- [ ] **Step 4: Run** — green (target + full suite).
- [ ] **Step 5: Commit** — `git add agents/scholar-verifier.md references/rubrics/paper-eval.md README.md tests/test_agent_integrity.py && git commit -m "feat(oms): agent cross-reference integrity tests + scholar-verifier opus→sonnet (R3 #19+#20)"`.

---

### Task 5: Skill shim + `skill-bodies/` split — item #21

**Files:**
- Move (git mv): `skills/<name>/SKILL.md` → `skill-bodies/<name>/SKILL.md` for all 12 skills
- Create: 12 new shim `skills/<name>/SKILL.md`; `tests/conftest.py` (skill-text helper)
- Modify: the 10 grep-verified test files that read skill text by path — `test_abstract_quantitative_guard.py`, `test_material_gap_contract.py`, `test_md_stage_layout.py`, `test_researcher_quote_anchor.py`, `test_revise_ledger_contract.py`, `test_round_id_contract.py`, `test_scholar_init_skill.py`, `test_ssot_priority_and_sync.py`, `test_state_schema_docs.py`, `test_verify_claim_faithfulness.py` (re-grep `skills/` in `tests/` at implementation time — the list must be re-derived, not trusted)
- Test: `tests/test_skill_shim.py` (new); `tests/test_plugin_integrity.py` untouched (must stay green by construction)

**Interfaces:**
- Shim format (per skill):
  - Frontmatter: the original frontmatter **byte-identical** (routing surface frozen — name/description/triggers) + one additive metadata line `oms-full-body: ../../skill-bodies/<name>/SKILL.md` (mirrors OMC's `omc-full-body:` key).
  - Body (short, fixed template): an `<!-- OMS:COMPACT-SKILL-SHIM -->` marker; "This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/<name>/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory."
- Body files: full original content unchanged (frontmatter included — `git mv` keeps history; the duplicate frontmatter in the body is inert).
- `tests/conftest.py`: `SKILL_BODIES = Path(__file__).parent.parent / "skill-bodies"` + `def skill_md(name: str) -> str` returning the body text (reads `skill-bodies/<name>/SKILL.md`; raises with a clear message if absent). All repointed tests import this helper instead of hand-building `skills/...` paths — one future-proof indirection, no per-test path knowledge.
- `tests/test_skill_shim.py` locks:
  - `test_shim_body_one_to_one` — `skills/` dirs == `skill-bodies/` dirs (both directions).
  - `test_every_shim_points_to_its_own_body` — each shim contains `skill-bodies/<its-name>/SKILL.md` literally and the target file exists, non-empty.
  - `test_shim_frontmatter_name_matches_body` — `name:` identical in shim and body (drift lock).
  - `test_shim_is_compact` — every shim ≤ 4,096 B.
  - `test_corpus_under_omc_budget` — `sum(skills/*/SKILL.md sizes) ≤ 64 KiB` **with headroom asserted at ≤ 48 KiB** (a budget test that passes at 99% of budget is a time bomb; expected actual ≈ 15–20 KiB given frontmatter sizes).
  - `test_bodies_kept_full` — every body ≥ its shim's size (moved content really lives there; cheap sanity).
  - `test_doctor_fails_on_shim_body_mismatch` — discriminance for T3's post-split doctor branch (pitfall 3: that FAIL branch would otherwise have no test that proves it can fire): build a tmp fixture repo with a `skills/`↔`skill-bodies/` count mismatch (or a shim pointing at a nonexistent body path), invoke `oms_doctor`'s [skills] section function directly (importlib, same idiom as `test_oms_doctor.py`), and assert a FAIL row. Mirrors the fixture rigor of T3's `test_missing_registered_hook_fails`.

- [ ] **Step 1: Write failing tests** — `tests/test_skill_shim.py` as above (+ `tests/conftest.py` helper created here so the shim tests can use it).
- [ ] **Step 2: Run to verify failure** (no `skill-bodies/` yet).
- [ ] **Step 3: Execute the split** — for each of the 12 skills: `git mv skills/<n>/SKILL.md skill-bodies/<n>/SKILL.md`, then write the shim (script the loop; frontmatter extracted verbatim from the body file — mechanical, no paraphrasing). Repoint the ~10 test files through `conftest.skill_md` (mechanical edit; re-grep first).
- [ ] **Step 4: Discriminance spot-check (pitfall 4)** — temporarily remove one pinned token from one moved body (e.g. `revise-start` in scholar-revise) → the repointed lock (`test_revise_ledger_contract.py`) must FAIL; restore. Confirms the locks follow the bodies, not vacuously pass against shims.
- [ ] **Step 5: Run** — full suite green (213+ maintained — every repointed lock still binding); `test_plugin_integrity.py` green untouched.
- [ ] **Step 6: Commit** — `git add -A skills/ skill-bodies/ tests/ && git commit -m "feat(oms): skill shim + skill-bodies split — always-loaded corpus under the 64KiB budget (R3 #21)"`

---

### Task 6: `DISABLE_OMS` kill switch + route-hook relevance gate — item #22

**Files:**
- Modify: `hooks/scholar_route_emit.py`, `hooks/scholar_cite_guard.py`, `hooks/scholar_verify_emit.py`, `hooks/scholar_stop_guard.py`, `hooks/scholar_resume_emit.py`
- Test: `tests/test_kill_switch.py` (new); extend `tests/test_scholar_route_emit.py` (gate tests + 2 fixture payload updates)

**Interfaces:**
- **Kill switch (all 5 registered hooks):** first thing in `main()` (before reading stdin): `if os.environ.get("DISABLE_OMS", "").strip().lower() in ("1", "true", "on", "yes"): return 0` — silent, universal, mirrors `DISABLE_OMC`. The per-hook hatches (`OMS_CITE_GUARD`, `OMS_STOP_GUARD`) stay — DISABLE_OMS is the umbrella, they are the scalpels. Like the stop-guard's env hatch, DISABLE_OMS is never advertised in any injected/deny text.
- **Relevance gate (route hook only):** read the payload; `prompt = payload.get("prompt")`. `is_paper_related(prompt) -> bool`: `True` when prompt is missing/not-a-string (fail-toward-inject) or any token matches. Token matching: lowercase the prompt; CJK tokens by substring; ASCII tokens by word-boundary regex (`\btex\b` must not fire on "context", `\boms\b` not on "atoms"); dotted tokens (`.tex`, `.bib`) by plain substring. Token list (KR): 논문, 학위, 초안, 원고, 관련연구, 선행연구, 문헌, 인용, 참고문헌, 서지, 투고, 게재, 심사, 리비전, 초록, 목차, 아웃라인, 저널, 학회, 모의심사; (EN, word-bounded): paper, thesis, dissertation, manuscript, latex, tex, bib, bibtex, citation, cite, venue, survey, outline, draft, journal, conference, arxiv, doi, review, reviewer, rebuttal, revise, verify, abstract, scholar, oms, ideate, related. Non-paper → print nothing, exit 0 (same silence convention as the resume hook). Injected text: **byte-identical CHECKPOINT** (the existing literal-lock tests are the proof — they keep passing with keyword-bearing payloads).
- Two existing fixture payloads gain a paper token (they currently carry none and would go silent): `test_learn_stage_in_routing_token_line` `{"prompt": "이 관찰 규칙으로 굳혀줘"}` → `"이 관찰 venue 규칙으로 굳혀줘"`; `test_learn_routing_keeps_citation_guard` `{"prompt": "promote observation"}` → `"promote observation to venue default"`. Fixture-only change; every asserted contract token is untouched (pitfall 3 respected — the locks still pin the same CHECKPOINT content).

- [ ] **Step 1: Write failing tests**
  - `tests/test_kill_switch.py` — parametrized over the 5 registered hook files: run each as a subprocess with `DISABLE_OMS=1` in env and a payload that would otherwise produce output/deny (route: paper prompt; cite_guard: a fabricated `.bib` write payload reusing `test_scholar_cite_guard.py`'s deny fixture; verify_emit: a `.tex` PostToolUse payload reusing its emit fixture; stop_guard: a live revise marker fixture; resume_emit: a non-terminal pilot fixture with `source: "startup"`) → stdout empty (or explicitly-allow for cite_guard: no deny JSON), exit 0. Plus `test_disable_oms_unset_leaves_hooks_live` (one spot-check per hook family: same fixtures, env without DISABLE_OMS → output present; the existing per-hook suites already cover this in depth) and `test_hatch_never_advertised` — assert on **runtime output surfaces, not source counts**: run each hook against its live fixture (env WITHOUT the switch) and assert the string `DISABLE_OMS` appears nowhere in the produced stdout (injected additionalContext / deny or block reason). Source-level docstring documentation stays unconstrained — the existing hatches (OMS_CITE_GUARD, OMS_STOP_GUARD) each appear twice in their files (docstring note + env check) by repo convention, and DISABLE_OMS follows the same convention.
  - `tests/test_scholar_route_emit.py` additions: `test_non_paper_prompt_is_silent` (`{"prompt": "hello"}` → stdout empty, exit 0); `test_git_housekeeping_is_silent` (`{"prompt": "git 커밋 정리해줘"}` → silent); `test_word_boundary_no_false_positive` (`{"prompt": "look at the atoms in this context"}` → silent — "oms"/"tex" must not fire inside words); `test_missing_prompt_key_injects` (`{}` → full CHECKPOINT — fail-toward-inject); `test_paper_prompt_still_injects_full_checkpoint` (`{"prompt": "이 논문 introduction 초안 써줘"}` → CHECKPOINT contains `STAGE(paper) →` and `누락 금지` — byte-identity is carried by the whole pre-existing lock suite).
- [ ] **Step 2: Run to verify failure** (gate absent → "hello" currently injects; kill switch absent → hooks emit under DISABLE_OMS=1).
- [ ] **Step 3: Implement** — 5 hook edits (kill switch is ~2 lines each; route hook additionally gains `PAPER_TOKENS` + `is_paper_related()` + the gate in `main()`; docstring updated: "MVP: static checkpoint text (no keyword parsing)" sentence gets a follow-up line noting the R3 relevance gate — additive, keep the original sentence). Update the two fixture payloads.
- [ ] **Step 4: Run** — green (target + full suite; the pre-existing route-hook literal locks all still pass — that IS the "STAGE 계약 문구 유지" proof).
- [ ] **Step 5: Commit** — `git add hooks/ tests/test_kill_switch.py tests/test_scholar_route_emit.py && git commit -m "feat(oms): DISABLE_OMS kill switch + route-hook relevance gate (R3 #22)"`

---

### Task 7: Release — v0.8.0 CHANGELOG + README + version bump

**Files:**
- Modify: `CHANGELOG.md`, `README.md`, `.claude-plugin/plugin.json` (version → `"0.8.0"`)
- Test: none new (`test_version_sync.py`'s live lock now *enforces* that the plugin bump and the CHANGELOG entry land together; `test_readme_evidence.py` must stay green).

- [ ] **Step 1: Edit `CHANGELOG.md`** — new `## [0.8.0] — <today>` above `[0.7.0]` (below `[Unreleased]`): **Added** — one bullet per item with file paths (#15 version SSOT + sync_version.py; #16 atomic_write_text + venue-config wiring; #17 consensus/ in output-layout; #18 oms_doctor.py; #19 test_agent_integrity.py; #20 verifier sonnet; #21 shim + skill-bodies split + budget test; #22 DISABLE_OMS + relevance gate). **Notes** — (a) omha card surface: skip-if-absent by design; the card's version bump rides a **separate oh-my-heroacademia PR**; (b) tag v0.8.0 is cut after merge — sync_version's pre-tag window covers the interim; (c) #16 deliberately chose `atomic_write_text` over a YAML→JSON migration (venues.md schema surface untouched); (d) still-deferred R2 carry-overs restated (nearest-root asymmetry, oms_state slug-error DRY + 4 tests, empty-Priority-Context drop comment, compact 6-fire investigation — the last item sourced from the R2 session record, the rest from PR #7 Notes). **Verification** — final `python3 -m pytest tests/ -q` count.
- [ ] **Step 2: Edit `README.md`** — Status line: v0.8.0 + one sentence for P2 ("packaging & authoring hygiene — version SSOT + sync checker, oms doctor, agent cross-reference locks, verifier re-tiered sonnet, skill shim/skill-bodies split under the 64 KiB budget, DISABLE_OMS kill switch + route relevance gate, atomic venue-config writes"). Keep the retrospective **"Added in 0.7.0: …"** history bullet ONLY (history-chain style) — but **strike/rewrite the now-falsified branch-status clause** in the README tail ("oms is stacked on the unmerged R1 branch — tag `v0.7.0` only after both PRs merge"): R1 and R2 are merged and v0.7.0 is tagged; restate current reality (v0.8.0 tag cut after this PR merges). Update the quoted test count. Add `DISABLE_OMS` to whatever section documents env hatches (alongside OMS_CITE_GUARD/OMS_STOP_GUARD if listed) and a one-line `oms doctor` usage mention (`python3 scripts/oms_doctor.py`).
- [ ] **Step 3: Bump `.claude-plugin/plugin.json`** version to `"0.8.0"` — same commit as the CHANGELOG entry (the live sync lock makes splitting them a red suite).
- [ ] **Step 4: Run** — `python3 -m pytest tests/ -q` full green; README/CHANGELOG quote the real final count.
- [ ] **Step 5: Commit** — `git add CHANGELOG.md README.md .claude-plugin/plugin.json && git commit -m "docs(oms): v0.8.0 release notes — packaging & authoring hygiene (R3 P2)"`

---

## Post-plan process (not tasks — the R1/R2 verified pattern)

1. Whole-branch review (opus, read-only) over `git diff main...feat/r3-packaging` — findings folded or explicitly declined with reasons.
2. Push `feat/r3-packaging`; open **draft PR** (base=main) — body: summary per item #15–#22, test delta (213 → final), Notes carrying the same deferral list as the CHANGELOG. **Stop there — merge and tag are the human's.**
3. Separate repo, separate PR: `oh-my-heroacademia` `cards/oms.json` `"version": "0.1.0"` → `"0.8.0"` (pull/fetch first; small draft PR; never bundled into the oms PR).

## Self-Review (done at plan time)

- **Spec coverage:** #15→T1, #16→T2, #17→T2, #18→T3, #19→T4, #20→T4, #21→T5, #22→T6, release→T7. Sequencing: T3 imports T1's checker; T4's cross-ref scan globs `skills/` + `skill-bodies/` so T4/T5 order can't break it; T5's conftest repoint precedes nothing that depends on old paths; T6 touches only hooks; T7 is last and the live sync lock (T1) polices it.
- **Invariants:** stdlib only throughout; every hook stays fail-open (kill switch and gate both default to today's behavior on any error); no citation-path change anywhere in R3 (cite-guard logic untouched — it only gains the umbrella env check); human GATEs untouched; single-careful generation untouched; doctor and sync are read-only by test.
- **Routing surface frozen:** shim frontmatter byte-identical + additive key only; CHECKPOINT text byte-identical when injected; STAGE contract locks carry the proof. omha card never edited from this repo.
- **Budget honesty:** the corpus test asserts ≤ 48 KiB (headroom), not the nominal 64 KiB cliff; shim cap 4,096 B each.
- **Pitfall coverage:** discriminance proofs named at T4 Step 2 and T5 Step 4; exact-match tag parsing tested (T1); content-token pinning in every new lock; skill-bodies path realignment via one conftest helper + re-grep instruction instead of a trusted static list.
- **Carry-over discipline:** the four R2 deferrals (three from PR #7 Notes + the 6-fire investigation from the R2 session record) are named in Design decisions AND restated in the CHANGELOG Notes — excluded from R3 work, not silently forgotten.
- **Plan verification:** this document passed a 4-lens adversarial panel (sonnet: spec-coverage / tdd-soundness / repo-reality / packaging-safety) + opus judge — verdict READY-AFTER-MUST-FIX; all 6 must-fix items (card-surface WARN routing, paper-eval.md tier reconcile, README stale branch-status clause, hatch-advertising test rephrase, carry-over ledger completeness, doctor [skills]-branch discriminance test) are folded into the text above.
