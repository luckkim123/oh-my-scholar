# R4 — Knowledge Lifecycle (P3 #23–#27) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the wiki a maintainable lifecycle: a distributed health audit that every install gets (#23 — today the only audit lives outside the plugin as a workspace-local LLM workflow), a mechanical quality signal at the light-channel append site (#24), the already-decided storage format executed as a spec — thin YAML frontmatter + a generated INDEX.md (#25), a repeatable human-gated verb that anchors a mature wiki cluster into a `references/` card (#26), and a mock-review verdict history with a meta-review mining pass (#27) — release as v0.9.0, branched from main @ 46f842b (not stacked).

**Architecture:** One new stdlib CLI — `scripts/oms_wiki_audit.py`, a read-only detector over ONE wiki tree (run per level: local or global) covering the five *mechanical* dimensions (dangling cross-refs, duplicate section tokens, empty categories, orphan files, frontmatter validity) plus INDEX drift, with a single opt-in write path (`--write-index`, via `atomic_write_text`). One new reference card — `references/wiki/audit.md` — carrying the *procedure*: script first, then the two *judgment* dimensions (SSOT-delegation integrity, strength-tag discipline) run by an LLM auditor, with the 2026-06-02 calibration lesson embedded. Everything else is surgical prompt-contract and spec-card edits: scholar-pilot Step 10 (#24), `references/wiki/README.md` + `references/learning-protocol.md` + `references/output-layout.md` (#25), skill-bodies of scholar-learn (#26) and scholar-mock-review (#27). **No hook changes this round** — the 5 registered hooks are untouched. Spec = `docs/2026-07-11-oms-advancement-plan.md` §5 P3.

**Design decisions (deliberate, verified against the repo 2026-07-13):**

- **#23 mechanical/judgment split.** The source workflow (`workspace/.oms/workflows/wiki-audit.js`, 201 lines) runs 5 dimensions as LLM auditors. Two of them (SSOT-delegation integrity, strength-tag discipline) require reading *meaning* and cannot be a deterministic script; they stay LLM-run, but their prompts — including the strength-tag calibration block ("the rule's EXACT wording governs"; a tag naming 2+ papers PASSES; one reminder per file, not per tag) — move into the card as a written procedure. The three mechanical ones (dangling refs, duplicate section tokens, empty/orphan) become pure code, plus two net-new mechanical dimensions the roadmap items #24/#25 need: frontmatter validity and INDEX drift. The card's calibration lesson generalizes: **when a dimension's findings diverge from intuition, audit the criteria before the corpus.**
- **#23 script scope = ONE tree per invocation, no ascent.** The wiki has two levels (local + global, `references/wiki/README.md:17-41`); the *script* takes `--root <dir>` (default `./.oms/wiki` if present, else error) and audits that tree only. The card instructs the operator to run it once per level. Ascent stays enclosed in the `wiki_query` abstract-function contract — a CLI that silently walked up to a parent `.oms/` would surprise (and the audit of the *global* tree is a deliberate act).
- **#23/#25 INDEX.md is a generated artifact, never hand-edited.** `--write-index` (re)generates `<root>/INDEX.md` deterministically (sorted by category, then filename; one row per content file: path — H1 title (confidence, sightings)); the audit's INDEX-drift dimension is "INDEX.md absent or differs from regeneration" → WARN. Regeneration is not "repair" (detection-only discipline intact): INDEX is derived output, like a build product. Written via `atomic_write_text` (`hooks/oms_atomic.py:69`), imported the `oms_state.py:17-18` way (`sys.path.insert` of `hooks/`).
- **#25 frontmatter is a THIN, stdlib-parsable schema; the body stays free-form.** Standard: `confidence: high|med|low` (required for new notes), `sightings: <int>` (required for new notes), `keywords:` (optional, comma-separated on one line — grep fodder). Flat `key: value` lines between `---` fences only — **no nesting, no lists-with-dashes, no PyYAML** (stdlib invariant; the script parses it with a 10-line splitter). `references/wiki/README.md:38` ("No machine-parsing schema (grep only)") is **the defect itself** and is re-scoped to the *body* ("Body is human-readable free-form .md, grep only; the frontmatter above is the only machine-readable surface") — a named exception to additive-only. Existing corpus files without frontmatter are a WARN, never FAIL (#24's non-blocking philosophy; the live corpus migrates post-merge, see Post-plan).
- **#24 forces `confidence: low`, it never blocks.** At the scholar-pilot Step 10 append site: an entry carrying neither an internal pointer (`<slug> §…`) nor a verbatim quote is still appended, but the note's frontmatter must be created/kept at `confidence: low` and the entry line gets an `(evidence: none — add a pointer before confidence can rise)` marker. Evidence-less re-observation does not raise confidence. This turns the README's `:61-72` *recommendation* into a stated rule at the append site — note honestly: it remains a **prompt-contract rule with no automated compliance check** (the audit script does not police it; adding that backstop would be scope creep), and there is still no reject gate. The Step 10 sentence "A new category file is free-form .md (no machine schema)" (`skill-bodies/scholar-pilot/SKILL.md:61`) is the second named exception — replaced by "free-form body + standard thin frontmatter (`references/wiki/README.md`)".
- **#26 targets the PLUGIN's `references/`, with a dev-mode guard.** The verb repeats the 2026-06 hand-done pattern (external survey → global-wiki page `reference/llm-paper-writing-landscape.md` + anchors into 5 oms files). Promotion proposes a card draft (or an existing-card update) that **anchors, never copies wholesale** (the "no duplicate embedding — reference the SSOT" card discipline, `references/writing-craft.md:3`): pointers into the wiki source files + `file:line` anchors into affected oms surfaces. Write happens ONLY when the plugin root is a writable git checkout — the guard is **`.git` EXISTENCE (file or directory), explicitly not `isdir`**: in a linked git worktree `.git` is a plain gitfile (`gitdir: …` pointer) — including the very worktree this plan executes in — and an `isdir` check would silently degrade every worktree dev session to proposal-only. On a marketplace install (no `.git` at all) the step emits the proposed card as text for the human to carry. Human gate mandatory (reuses the scholar-learn gate discipline `:47`); citation/.bib content permanently excluded (`learning-protocol.md` §6.F). Slot: new Step 6 in scholar-learn (after Step 5 commit; old Step 6 follow-up renumbers to 7 — grep first that nothing external pins "Step 6" of this skill).
- **#27 makes mock-review "read-only except the log".** The skill's read-only rule (`skill-bodies/scholar-mock-review/SKILL.md:47`) gains ONE carve-out (third named exception): after the AC verdict (Step 3), append a dated entry to `.oms/<slug>/reviews-log.md` — date, venue, lens set, per-axis venue-scale scores, final verdict, top weakness types (one line each, anchors kept), rebuttal flag. Append-only, create-if-absent, never touches `.tex`/`.bib`. **The append is performed by the orchestrating SKILL flow (the calling session), NEVER by the dispatched scholar-reviewer agent** — `agents/scholar-reviewer.md:6` declares `disallowedTools: Write, Edit, NotebookEdit`, so an agent-side reading would silently never write (mirror how scholar-pilot writes `.oms/state/` from the calling session). Two frozen surfaces also say "read-only" — the shim frontmatter `skills/scholar-mock-review/SKILL.md:8` and `references/rubrics/paper-eval.md:68` — both mean read-only *w.r.t. the reviewed draft* (no `.tex`/`.bib` edits), which a metadata log append does not violate; they are deliberately left untouched (frontmatter frozen; ceiling-scoped simplification, noted in the body edit). The **meta-review pass** is a sub-step gated on ≥3 entries in the log (or explicit user request): mine recurring weakness *types* across entries; flag "always-moderate" score drift (all verdicts in the borderline band with low variance = calibration suspicion, the CycleReviewer lesson); output = *proposed* lens-prompt tweaks presented at a human gate — never auto-applied, and lens prompts are only ever edited by the human. Frontmatter (name/description/triggers) of every skill is **frozen** (R3 shim byte-equality) — all skill edits in this round are body-only.
- **Scope guard — carried-over items stay out.** Still-deferred, re-recorded in the v0.9.0 CHANGELOG Notes: the two hooks' nearest-root asymmetry; `oms_state.py` slug error-string DRY (6 sites) + 4 deferred tests; empty-Priority-Context drop comment; compact-time SessionStart 6-fires investigation; doctor PASS-row suppression cosmetic; sync row() wording coupling; basename ceiling comment. The stray `.omc/state/` contamination inside the live global wiki is a **claudebase ticket** (plan §8), not R4 — the audit script will *find* it (orphan/unknown entry) and that is correct behavior, but R4 does not delete it.
- **Live-corpus migration is NOT in this PR.** The plugin ships spec + script; adding frontmatter to the 10 unmigrated workspace wiki files and generating the live INDEX.md is a workspace-side operation executed post-merge as dogfood (Post-plan process). Workspace is iCloud-synced, not git — follow the safe-write discipline (no bulk in-place rewrites without a listing first; conservative confidence values grounded in each file's own stated sources).

**Tech Stack:** Python 3 stdlib only (argparse, pathlib, re, os, sys, difflib not needed — string compare suffices), pytest, markdown prompt contracts.

## Global Constraints

- stdlib only — no third-party imports in `scripts/` (repo invariant; no PyYAML — the thin frontmatter splitter is local code).
- `oms_wiki_audit.py` is read-only except under `--write-index`, which writes exactly one file (`<root>/INDEX.md`) via `atomic_write_text`. No other file writes anywhere in the script.
- Prompt-contract edits are surgical and additive-only, with THREE named exceptions (Design decisions): `references/wiki/README.md:38` schema sentence, `skill-bodies/scholar-pilot/SKILL.md:61` "no machine schema" sentence, `skill-bodies/scholar-mock-review/SKILL.md:47` read-only sentence (gains a carve-out clause, its prohibition on `.tex`/`.bib` edits stays verbatim).
- Skill **frontmatter is frozen** (R3 shim byte-equality contract) — body-only edits; `tests/test_skill_shim.py` must stay green. ⚠️ Do NOT cite its byte-budget test as the safety net for body edits: `test_corpus_under_omc_budget` sums the **shims** (`skills/`, 13,083 B of the 48 KiB cap) and is structurally blind to `skill-bodies/` growth (94,407 B, lazy-loaded, **no enforced ceiling by design**). The real invariant for T4/T5/T6 is *shims untouched* — assert it mechanically with `git diff --quiet skills/` after each of those tasks.
- Every task ends with `python3 -m pytest tests/ -q` green (baseline **287 passed**; later tasks keep it green at higher counts).
- Worktree: `/Users/kimseungmin/oh-my-scholar/.claude/worktrees/oms-r4`, branch `feat/r4-knowledge-lifecycle`, **base: main @ 46f842b**. Commit per task, message style `feat(oms): …`.
- **Pitfalls from prior releases (measured, all bind here):**
  1. A test that *adds a lock* carries a discriminance-proof duty: demonstrate the lock FAILs when the target token is removed (temporarily revert the target text once, or assert on a token only the new text introduces).
  2. Multibyte grep trap: verification greps involving `§` or CJK must use Python `re` (or `grep -P` never C-locale BRE) — macOS `grep` returns false-clean on multibyte classes.
  3. Tests pin **content tokens**, not just file existence; vacuous locks banned.
  4. All skill-text reads in tests go through `conftest.skill_md(name)` (the R3 split indirection) — never raw `skills/<name>/` paths.
  5. Exact-token anchors in any git/grep extraction (`v0.9.0` not `0.9`).

---

### Task 1: `scripts/oms_wiki_audit.py` — item #23 (mechanical dimensions) + #25 (INDEX generation)

**Files:**
- Create: `scripts/oms_wiki_audit.py`
- Test: `tests/test_oms_wiki_audit.py`

**Interfaces:**
- CLI: `python3 scripts/oms_wiki_audit.py [--root DIR] [--write-index]`. `--root` defaults to `./.oms/wiki` (error with exit 2 if the resolved root does not exist — mirroring `oms_state.py`'s `_err` pattern). Output: one row per finding plus a per-dimension summary row, doctor-style `[PASS|WARN|FAIL] <dimension>: <message>` (`oms_doctor.py:36` `_row` pattern). Exit 0 iff no FAIL rows; exit 1 otherwise; exit 2 usage errors.
- Dimensions (pure functions over an in-memory inventory, each unit-testable without I/O):
  - `scan(root) -> inventory`: walks the tree once (**skipping dot-directories** — `.omc`, `.git` and kin are not wiki content; the known stray `.omc/state/` in the live corpus must NOT surface as findings); per `.md` file: relative path, frontmatter dict (thin splitter: lines between leading `---` fences, `key: value` split on first colon; absent/malformed → `{}` + a flag), H1 title (first `# ` line), section tokens, outbound refs (`[[slug]]` wikilinks; `[text](x.md)` md-links; prose `file.md §S` mentions; regexes compiled once, applied per line with line numbers). **Section-token extraction is `re.fullmatch`, never prefix-match**: take the first word of a `^##+ ` heading, strip exactly one trailing `.` or `:`, and require the WHOLE remainder to fullmatch `§?[A-Z][0-9]*[a-z]?`; a first word that does not fullmatch (e.g. `H-contrast.` — a real live-corpus heading that under prefix-match would collide with `H.`) is not a section-token heading and is excluded from both duplicate detection and `§`-ref resolution.
  - `check_duplicate_tokens(inv)`: same token twice in ONE file → FAIL per duplicate (quote both heading lines with line numbers). `F1` vs `F1b` are distinct.
  - `check_dangling_refs(inv)`: `[[slug]]` resolves iff some file's stem equals the slug anywhere in the tree; `[text](x.md)` resolves relative to the source file's directory (plus tree-wide stem fallback for bare names); `file.md §S` resolves iff the file exists AND has token `S`. Unresolved → FAIL with source `file:line` and the target as written. INDEX.md is excluded as a *source* (generated).
  - `check_empty_and_orphan(inv, root)`: the category universe is the **fixed five names** (`convention/ pattern/ decision/ reference/ history/`) directly under root — other directories are neither categories nor findings. A category dir with no content `.md` → WARN ("silently empty") unless a `.gitkeep` or README placeholder documents it → PASS row noting "documented empty". Content file with zero inbound refs from any other file AND no mention in any README/INDEX → WARN (candidate orphan). `README.md`/`INDEX.md` themselves are exempt from orphan checks.
  - `check_frontmatter(inv)`: content file with no frontmatter → WARN; `confidence` outside `{high,med,low}` or `sightings` non-integer → WARN. Never FAIL (#24 non-blocking philosophy). `README.md`/`INDEX.md` exempt.
  - `render_index(inv) -> str`: deterministic — categories sorted, files sorted by name; header line `# Wiki INDEX — generated by scripts/oms_wiki_audit.py — do not hand-edit`; per file: `- \`<relpath>\` — <H1 title or (untitled)> (confidence: <val or ?>, sightings: <val or ?>)`.
  - `check_index(inv, root)`: INDEX.md absent → WARN "run --write-index"; present but ≠ `render_index` output → WARN "stale".
- Module docstring cites "R4 #23/#25" and names the two judgment dimensions as **card-run, not script-run** (pointer to `references/wiki/audit.md`).

- [ ] **Step 1: Write failing tests** — `tests/test_oms_wiki_audit.py` (import via `sys.path.insert` like `tests/test_oms_state.py`; fixtures build tmp wiki trees with `tmp_path`):
  - `test_healthy_tree_passes` — categories with frontmattered, cross-linked files → all PASS, exit 0 (drive `main(["--root", str(tmp)])`).
  - `test_missing_root_exits_2`.
  - `test_duplicate_token_fails` — one file with two `### F2` headings → FAIL row quoting both lines; `F1`+`F1b` in the same file → no finding.
  - `test_hyphenated_suffix_heading_not_a_token` — a file with `## H. Title` + `### H-contrast. Title` → NO duplicate finding (mirrors the real live-corpus pair; locks the fullmatch grammar).
  - `test_dot_directories_skipped` — a `.omc/state/foo.json` (and a `.omc/whatever.md`) under root → zero findings referencing it; not in the inventory.
  - `test_dangling_wikilink_fails` / `test_dangling_mdlink_fails` / `test_prose_section_ref_missing_token_fails` — each unresolved form → FAIL naming source `file:line` and target; resolvable counterparts → no finding.
  - `test_silently_empty_category_warns` and `test_documented_empty_category_passes` (`.gitkeep` present).
  - `test_orphan_file_warns` — file nobody links → WARN; same file once linked from README → no finding.
  - `test_missing_frontmatter_warns` / `test_bad_confidence_warns` / `test_bad_sightings_warns` — all WARN (exit stays 0 when no FAIL).
  - `test_index_absent_warns` / `test_index_stale_warns` / `test_write_index_then_clean` — after `--write-index`, rerunning the audit shows the INDEX dimension PASS and the file content equals `render_index` (determinism: two consecutive `--write-index` runs byte-identical).
  - `test_read_only_without_flag` — run the full audit (no `--write-index`) over a tree snapshot; assert the tree's file set + contents are unchanged (walk before/after).
  - `test_exit_1_on_fail` — a dangling ref makes the process exit 1.
- [ ] **Step 2: Run to verify failure** (module absent).
- [ ] **Step 3: Implement `scripts/oms_wiki_audit.py`** per Interfaces (argparse, `main(argv=None) -> int`, `sys.exit(main())`, stdlib only, `atomic_write_text` import via `sys.path.insert`).
- [ ] **Step 4: Run the new tests green, then full suite** (`python3 -m pytest tests/ -q`) — baseline 287 + new.
- [ ] **Step 5: Commit** `feat(oms): wiki audit CLI — mechanical dimensions + INDEX generation (#23, #25)`.

### Task 2: `references/wiki/audit.md` — item #23 (the procedure card, judgment dimensions)

**Files:**
- Create: `references/wiki/audit.md`
- Test: `tests/test_wiki_audit_card.py`

**Interfaces:**
- Card format per house convention: `# Wiki Audit — health-check procedure (mechanical script + judgment lenses)` + `> blockquote` consumer line (who runs this: any session asked to "audit the wiki"; the script does the mechanical half, an LLM auditor does the judgment half). §-numbered sections:
  - §1 Run the script (`python3 <plugin>/scripts/oms_wiki_audit.py --root <wiki>`; once per level — local, then the parent global tree; `--write-index` only after findings are reviewed).
  - §2 Judgment dimension A — SSOT-delegation integrity: broken delegation (A delegates topic T to B but B no longer covers T) and cyclic delegation (A↔B both claim the other is SSOT). Ported from the source workflow's prompt: quote the delegating sentence, verify the target actually owns the topic, never flag healthy one-directional delegation.
  - §3 Judgment dimension B — strength-tag discipline, WITH the calibration block ported verbatim in substance: the rule's exact wording governs ("[N편공통] = observed in N papers, 2+ = real pattern"); a tag NAMING 2+ distinct papers PASSES even without inline quotes; a defect is ONLY tagged-count > named-or-quoted distinct sources; at most one independence-cluster reminder per file.
  - §4 The calibration lesson (generalized): when a dimension's findings diverge from expectation, audit the *criteria* first, then the corpus — the 2026-06-02 incident is the worked example.
  - §5 Detection-only discipline: the audit NEVER edits the wiki (repair is a separate human-decided lane; the one INDEX write is generated-artifact regeneration, not repair). Findings ranked high/medium/low, each with `file:line` evidence quoting the offending text.
  - No duplicate embedding: the card does NOT restate the mechanical dimension definitions — it points to the script's `--help`/docstring and `references/wiki/README.md`.
- [ ] **Step 1: Write failing tests** — card exists; line 1 matches `^# Wiki Audit — `; line 2 is a `> ` consumer blockquote; locks content tokens: `oms_wiki_audit.py`, `SSOT-delegation`, `strength-tag`, a calibration token (`audit the criteria`), the detection-only token (`never edits the wiki`), the per-level instruction (`once per level`).
- [ ] **Step 2: Verify failure, implement the card, tests green, full suite green.**
- [ ] **Step 3: Commit** `feat(oms): wiki audit procedure card — judgment dimensions + calibration lesson (#23)`.

### Task 3: Frontmatter standard + INDEX contract in the spec cards — item #25

**Files:**
- Modify: `references/wiki/README.md` (frontmatter standard section; `:38` re-scope; INDEX.md contract)
- Modify: `references/learning-protocol.md` (confidence-note sections `:339-362` gain a one-line pointer to the standard; no restatement)
- Modify: `references/output-layout.md` (`.oms/wiki/` block `:120-124`: list all five categories `convention/ pattern/ decision/ reference/ history/` (history: global level only), add `INDEX.md — generated by scripts/oms_wiki_audit.py --write-index, never hand-edited`; §6 consumer checklist row)
- Test: extend `tests/test_output_layout_doc.py`-style locks (find the existing output-layout lock test by grep; if none exists, add `tests/test_wiki_spec_docs.py`)

**Interfaces:** the README gains one `## Frontmatter standard (thin, stdlib-parsable)` section: required-for-new-notes `confidence: high|med|low` + `sightings: <int>`, optional `keywords: a, b, c` (one line, comma-separated), flat `key: value` only — no nesting/no lists, body free-form; INDEX.md = generated artifact at each wiki root, regenerated by the script, never hand-edited, and *not* a query surface (grep still runs over the notes themselves — INDEX is for humans and for drift detection). The `:38` sentence is re-scoped per Design decisions (body-scoped). Existing prose stays otherwise intact.

- [ ] **Step 1: Failing lock tests** — tokens: `Frontmatter standard`, `never hand-edited`, `pattern/` and `history/` inside the output-layout wiki block, the README body-scope sentence replacement (discriminance: assert the OLD unscoped sentence `No machine-parsing schema (grep only)` no longer appears verbatim while the new body-scoped one does).
- [ ] **Step 2: Verify failure, apply the three card edits, tests green, full suite green.**
- [ ] **Step 3: Commit** `feat(oms): frontmatter standard + INDEX.md contract in wiki spec (#25)`.

### Task 4: Light-channel quality signal at the append site — item #24

**Files:**
- Modify: `skill-bodies/scholar-pilot/SKILL.md` (Step 10, lines `:58-64` region — body only)
- Modify: `references/wiki/README.md` (the `:61-72` evidence-recommendation block gains the mechanical rule, cross-referenced not restated)
- Test: `tests/test_scholar_pilot_skill.py` additions (via `conftest.skill_md("scholar-pilot")`; grep for the existing pilot-skill test file name first and extend it)

**Interfaces:** Step 10 gains the append-time rule (one bullet, additive) + the `:61` sentence replacement (named exception): every appended entry states its evidence; an entry with neither an internal pointer nor a verbatim quote is still appended but the note's frontmatter is created/kept at `confidence: low` with an `(evidence: none — add a pointer before confidence can rise)` marker, and evidence-less re-observation never raises confidence. New note files are created WITH the standard frontmatter (`references/wiki/README.md` Frontmatter standard).

- [ ] **Step 1: Failing lock tests** — tokens: `confidence: low` forcing clause, `evidence: none`, the new-note frontmatter clause; discriminance: the old `:61` "(no machine schema)" token gone from the body.
- [ ] **Step 2: Verify failure, apply, tests green, full suite green; assert shims untouched (`git diff --quiet skills/`).**
- [ ] **Step 3: Commit** `feat(oms): light-channel evidence signal — force confidence:low on pointer-less appends (#24)`.

### Task 5: Mock-review history + meta-review-of-reviews — item #27

**Files:**
- Modify: `skill-bodies/scholar-mock-review/SKILL.md` (Execution_Policy `:47` carve-out; new step after Step 3/4; Output section rows)
- Modify: `references/output-layout.md` (per-slug tree: `reviews-log.md` alongside `compile-notes.md:113`; §5 cleanup table: KEEP — review history is durable; §6 checklist row)
- Test: `tests/test_scholar_mock_review_skill.py` (extend existing if present — grep first)

**Interfaces:** per Design decisions — append one dated entry per completed review to `.oms/<slug>/reviews-log.md` (create-if-absent, append-only, never touch `.tex`/`.bib`): date, venue, lens set, per-axis scores, final verdict, top weakness types (anchored one-liners), rebuttal flag. Meta-review sub-step gated on ≥3 log entries or explicit user request: recurring weakness types; "always-moderate" drift flag (all verdicts borderline-band, low variance → calibration suspicion); output = proposed lens-prompt tweaks at a human gate, never auto-applied.

- [ ] **Step 1: Failing lock tests** — tokens: `reviews-log.md`, `append-only`, `≥3` gate (use an ASCII-safe token like `at least 3` — pick what the body actually says and lock that), `always-moderate`, human-gate clause for tweaks; output-layout tokens: `reviews-log.md` row + KEEP fate; discriminance: `:47` still contains the `.tex/.bib` prohibition verbatim.
- [ ] **Step 2: Verify failure, apply, tests green, full suite green; assert shims untouched (`git diff --quiet skills/`).**
- [ ] **Step 3: Commit** `feat(oms): mock-review verdict history + meta-review mining (#27)`.

### Task 6: wiki→reference-card anchoring verb in scholar-learn — item #26

**Files:**
- Modify: `skill-bodies/scholar-learn/SKILL.md` (new Step 6 after Step 5; old Step 6 → Step 7; Execution_Policy cross-ref line `:62` extended if needed)
- Modify: `references/learning-protocol.md` (one pointer line in the heavy-channel section — the verb is a *third* lane: neither venue-default promotion nor local→global elevation; placement and non-restatement per the SSOT discipline)
- Test: `tests/test_scholar_learn_skill.py` (extend existing if present — grep first)

**Interfaces:** per Design decisions — trigger: a *global*-wiki cluster that is paper-agnostic, harness-relevant, `confidence: high` with `sightings ≥ 3` (or user-requested); verb: propose a `references/` card draft or existing-card update that anchors (wiki source pointers + `file:line` anchors into oms surfaces), never copies wholesale; dev-mode guard: write only when the plugin root has `.git` **present in ANY form — plain directory OR linked-worktree gitfile (existence check, explicitly not isdir)** — else emit the proposal as text; human gate mandatory; citation/.bib permanently excluded. Precedent named in the step: the 2026-06 survey anchoring.

- [ ] **Step 0: Grep guard** — `grep -rn "Step 6" tests/ skills/ skill-bodies/ references/ docs/` and confirm nothing external pins scholar-learn's step numbering before renumbering (Python `re` if any multibyte class involved).
- [ ] **Step 1: Failing lock tests** — tokens: `anchoring`, `references/` card target, the `.git`-existence guard clause **including its worktree-gitfile form** (lock a token like `file or directory` / whatever the body actually says — the test must fail if the guard regresses to directory-only), human-gate clause, citation-exclusion clause, `anchors, never copies` (or the body's actual phrasing).
- [ ] **Step 2: Verify failure, apply, tests green, full suite green; assert shims untouched (`git diff --quiet skills/`).**
- [ ] **Step 3: Commit** `feat(oms): wiki-to-reference-card anchoring verb in scholar-learn (#26)`.

### Task 7: Release — v0.9.0 CHANGELOG + version bump + README

**Files:**
- Modify: `.claude-plugin/plugin.json` (`"version": "0.9.0"`)
- Modify: `CHANGELOG.md` (new `## [0.9.0] — <date>` block: Added per item #23–#27 in house `**bold lead** (file anchors) — description` style; Notes = carried-over list from Design decisions Scope guard, restated, **plus the #25 deferral stated plainly: v0.9.0 ships spec + script + INDEX generation — the live-corpus migration itself is a separate post-merge dogfood step** (no overclaiming))
- Modify: `README.md` (test count, any stale feature list rows; grep `287` first)

- [ ] **Step 1: Apply the three edits together** (the `test_version_sync.py` live lock forces plugin.json + CHANGELOG to move in the same commit).
- [ ] **Step 2: `python3 scripts/sync_version.py`** — expected outcome after the bump: **exit 1 with EXACTLY ONE drift line, the `card:`-prefixed one** (the omha card still reads 0.8.0 until its separate PR lands — `sync_version.py` is a strict CLI and fails on card drift; only `oms_doctor.py` routes `card:` to WARN). Plugin/CHANGELOG rows PASS; tag row PASS via the pre-tag window (latest tag v0.8.0 = previous released). **Any OTHER drift line is a real failure — fix it; do NOT touch the foreign omha repo to force exit 0.** The live pytest lock (`test_live_repo_surfaces_agree`) deliberately excludes the card, so the suite stays green.
- [ ] **Step 3: Full suite green; commit** `feat(oms): release v0.9.0 — knowledge lifecycle (P3 #23–#27)`.

---

## Post-plan process (not tasks — the R1–R3 verified pattern)

1. Final review: one opus `code-reviewer`-tier pass over the full branch diff ("Ready to merge?"); fix rounds until Critical/Important = 0.
2. Draft PR #9 (`gh pr create --draft`), base `main`, body = summary + per-item map + test evidence + Notes (carried-over list). Merge + `v0.9.0` tag = user's call (`gh pr ready` before merge — draft PRs refuse merge).
3. omha card bump (`cards/oms.json` → 0.9.0): prepare the local commit in `oh-my-heroacademia`, hand to the user (auto-mode push gate — R3 lesson).
4. **Dogfood on the live corpus (workspace-side, after PR opens):** run `oms_wiki_audit.py --root ~/Desktop/workspace/.oms/wiki` read-only; review findings (expected: ~10 files missing frontmatter → WARN; the stray `.omc/state/` dir is invisible to the scan — dot-directories skipped, and deleting it stays a claudebase ticket; decision/.gitkeep documented-empty; the `H`/`H-contrast` heading pair produces NO duplicate finding). Then migrate: add thin frontmatter to the 10 unmigrated files with conservative, source-grounded confidence values; `--write-index`; re-run audit expecting frontmatter PASS. No git — iCloud; keep a pre-migration file listing.
5. Runtime reload note to the user: marketplace update + app restart (standing rule).

## Self-Review (done at plan time)

- **Why no hook changes?** Nothing in #23–#27 needs turn-time injection; everything is CLI + prompt contracts + spec cards. This keeps the round's regression surface small (the R2/R3 hook rounds were the risky ones).
- **Why does the script own INDEX but not frontmatter repair?** INDEX is derived (regenerable from the tree, zero information added); frontmatter values encode *judgment* (confidence). Detection-only discipline: the script may rebuild what is derived, never what is authored.
- **Why is the meta-review inside mock-review, not scholar-learn?** The log and its mining input live per-slug; learn operates on `learned.md`/venue defaults. A lens-prompt tweak is not a venue default — routing it through learn would stretch learn's schema for zero gain. The human gate is preserved either way.
- **Shim-freeze check** is explicitly in T4/T5/T6 (three body-growing edits): the byte-budget test covers only the always-loaded shims (13,083 B used of the 48 KiB cap — ~36 KiB headroom) and cannot see body growth; bodies (94,407 B) are lazy-loaded with no enforced ceiling by design, so the mechanical assertion is `git diff --quiet skills/` per task.
- **Open risk (for the adversarial pass):** the `[[slug]]`/`file.md §S` regex grammar in T1 is inferred from the source workflow's prompts, not from a formal spec — the live-corpus dogfood is the empirical check; false-positive dangling refs should be treated as criteria-defects per the card's own calibration lesson.
