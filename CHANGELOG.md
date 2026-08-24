# Changelog

All notable changes to oh-my-scholar (oms).

## [Unreleased]

## [0.15.0] - 2026-08-24

### Added

- **The drafter's "needs figure" dead end now has a road out of it.** `scholar-drafter`
  surfaced every figure gap to the human as `fixable_by_llm=false`, which is right for a
  diagram or a scope call and wrong for an experiment curve — omx has held both the data
  and a renderer for that case the whole time (`omx plot`, `omx promote-plots`), and
  nothing in oms pointed at them. Neither half was missing; the contract between them was.
  The drafter now distinguishes *judgment* figures (still surfaced) from *curve* figures
  (procured), and reports a procured one with its run id, the flags used, and the path the
  `.tex` references.

  Two silent traps are written into the rule because both fail quietly:

  - Calling `omx plot` without the paper flags returns its **triage** render — 100 dpi, no
    axis labels, title inside the figure. That is ~158 effective dpi at an IEEE single
    column, and `omx promote-plots` moves the file rather than re-rendering it, so the
    triage PNG would ship in the paper. (The flags themselves are new in omx 0.12.0.)
  - The `.tex` must reference **omx's permanent analysis tree**. `.oms/<slug>/gen-image/`
    is a scratch intermediate that `scholar-pilot`'s terminal cleanup deletes, so a figure
    copied there disappears at the end of the run. omx never writes into an `.oms/` tree;
    oms points at omx's path. Ownership does not mix.

### Notes

- Requires `oh-my-experiments >= 0.12.0` for the paper-figure flags. Without it the drafter's
  procurement path still runs, but `omx plot` rejects `--dpi`/`--ext` and the fallback is the
  unchanged "surface it to the human" branch.

## [0.14.0] - 2026-08-12

### Added

- **GATE 1 outline view** — `scholar-outline` now renders `.oms/<slug>/outline/outline.md`
  as a self-contained read-only sheet at `.oms/<slug>/outline/gate1.html` before asking for
  approval, and reports nine mechanically-detectable structural gaps: a section missing
  Purpose / Core message / Proposition to argue / word budget, a section absent from the
  necessity chain, a chain link with no matching section in the tree, a chain link with no
  stated reason, a `researcher recheck needed` marker, a word-budget total over the venue's,
  a disagreement between a section's citations and the mapping table, a duplicate section
  number, and an outline with no section tree at all. The renderer detects *absence*
  only — never quality — so `GAPS=0` is not a verdict that the structure is good. New:
  `scripts/oms_outline_view.py`, `tests/test_oms_outline_view.py`.

- **`references/systematic-review.md`** — the protocol `mode=gap-research` does not run.
  gap-research is targeted (ground the topic, map the closest work, state the gap); it
  pre-specifies no search strategy, no inclusion/exclusion criteria, no dedup, no two-stage
  screening, and no re-runnable search log. Those are what "we systematically reviewed"
  actually asserts, so writing that sentence over a gap-research pass is an over-claim about
  *method* — and no citation check catches it, because every individual citation verifies fine.

  Adapted from ECC's `scientific-thinking-literature-review` (MIT, github.com/affaan-m/ECC).
  Its eight steps are kept; what is added is oms's own citation discipline — the verbatim
  quote + locator anchor `scholar-verify` re-reads, and unverified-is-reported-not-dropped.
  The card is explicit that an ordinary related-work section should stay on gap-research: a
  screening log buys nothing a reader sees.

### Changed

- **`scholar-research` names the boundary** (`skill-bodies/scholar-research/SKILL.md`
  Execution_Policy) — when the paper will claim survey-grade coverage or a reviewer will ask
  how the works were found, route to the protocol and report its flow counts. A reference
  nothing points at is a reference nobody reads.

### Fixed

- **`references/wiki/README.md` stale cross-reference** — pointed to a nonexistent
  `references/formats/venues.md`; corrected to `references/venues.md`, matching every other
  cross-reference to the venue card in the repo.
- **README doc-quality sweep**: Status section's version header and pytest count had drifted behind
  `plugin.json` (0.12.3) and the current test run; the 0.12.0–0.12.3 changes had no summary. Added an
  Installation section (marketplace-add/install commands via the `oh-my-heroacademia` marketplace,
  prerequisites, a first-command pointer to `scholar-init`) and a Routing clarification that oms's
  hooks work standalone without `oh-my-heroacademia`/`oh-my-claudecode` installed.
- Added a root `LICENSE` (MIT) — `plugin.json` declared `"license": "MIT"` with no license file backing
  the claim.

## [0.13.1] - 2026-07-19

### Changed

- **Vendored `hooks/oms_atomic.py` from the new shared `om-core` repo** — oms was the
  donor of this primitive, so this is a near-identical content-swap: only the temp-file
  prefix changed (`.oms-tmp-` -> `.om-tmp-`, no functional change). The failure-cleanup
  test's glob was updated to match (`test_atomic_write_cleans_up_on_failure`) — a
  RED/GREEN sanity check confirmed it stays a real (non-vacuous) leftover-temp-file
  guard after the rename. Adds a local-only `tests/test_atomic_vendored_sync.py` that
  byte-compares the vendored copy against `~/om-core/atomic_fn.py` and skips gracefully
  when that sibling repo is absent (clean CI).

## [0.13.0] - 2026-07-19

### Added

- **Tier 1: `tests/test_integration_smoke_script.py`** — unit-tests `scripts/integration_smoke.py`'s
  own logic (transcript-dispatch parsing, scaffold-assertion, preflight fail-fast) against synthetic
  fixtures only. Explicitly does **not** re-cover the existing wiring-integrity suite
  (`test_plugin_integrity.py`, `test_agent_integrity.py`, `oms_doctor.py`) — those already assert
  plugin.json↔skills/agents wiring, frontmatter parse, and dispatch-target existence in full.
- **Tier 2: `scripts/integration_smoke.py`** — a manual, developer-run `scholar-init` smoke test via
  `claude -p --plugin-dir` in a disposable `tempfile.mkdtemp()` workspace. Asserts the
  dispatch->artifact edge (skill invocation -> `Task(subagent_type="oh-my-scholar:scholar-planner")`
  -> `.oms/<slug>/` scaffold on disk) that six release cycles (v0.6.0→v0.12.3) shipped without
  exercising. Never invoked by CI, a git hook, or any other automated trigger. Requires either an
  interactively-logged-in `claude` CLI session or `ANTHROPIC_API_KEY`; cost is one sonnet-tier
  orchestrating turn plus one opus-tier `scholar-planner` dispatch — a few cents per run, not
  CI-reusable. `--deep` is an opt-in flag that chains `scholar-research` in the same workspace after
  a passing `scholar-init`, off by default.

## [0.12.3] - 2026-07-19

### Fixed

- **`oms_state.py`'s slug error-string duplication (6 sites), tracked as debt since v0.7.0/v0.8.0** —
  extracted a `_slug_error(value, flag="--slug")` helper alongside the existing `_valid_slug()`;
  all 6 `--slug` sites plus the sibling `--defect-id` message in `_cmd_strike` now build the
  string through it. Messages are byte-identical to before.
- **The two hooks' nearest-root ascent asymmetry, tracked as open debt since R2** — added
  `hooks/oms_paths.py::nearest_ancestor(start, predicate, include_start)`, a single directory-walk
  loop parameterized by a per-call-site marker predicate. `scholar_stop_guard.py`'s
  `nearest_state_dir` and `scholar_resume_emit.py`'s `nearest_oms_root` now both call it (each
  keeps its own marker check and its own return value — a `.oms/state` dir vs a `.oms` dir).
  `scholar_cite_guard.py`'s third, previously-untracked inline `list(start.parents)` walk in
  `allowlisted_keys` is unified too, using `include_start=False` plus its own cwd fallback
  candidate, to preserve its distinct exclusive-of-start / specific-file semantics.

## [0.12.2] - 2026-07-16

### Fixed

- **`references/wiki/audit.md` made dimension-count-agnostic** (2026-07-16 om* wiki audit
  finding): the card still read "the five mechanical dimensions" while the script docstring —
  which the same sentence declares to be the SSOT — says six. Rather than correcting the digit
  (which would drift again on the next dimension change), the count is removed ("the mechanical
  dimensions"): the card already defers to the docstring and does not re-list the dimensions, so
  the duplicated fact is deleted instead of guarded by a prose-parsing test.
- **scholar-verify uncited-claim WARN enumeration** (v0.12.1 verifier finding, committed
  post-release) ships in this release.

## [0.12.1] - 2026-07-16

### Fixed

- **scholar-verify's authoritative WARN enumeration now names every WARN check.** Step 7's
  "does not count toward FAIL" parenthetical and the Output PASS/WARN list only named
  meta consistency + abstract discipline, leaving claim-faithfulness, blind-review
  anonymization, and the new open-wiki-gaps check enumerable only from their own step-2
  bullets (2026-07-16 wiki-week review). Both sites now carry the complete list.
- `oms_wiki_audit.py` module docstring: five -> six mechanical dimensions (`open_gaps` was
  added in 0.12.0 without folding it into the docstring that `references/wiki/audit.md`
  defers to as the dimension SSOT).
- CHANGELOG 0.12.0 entry: grep fallback pattern aligned with the 6cbdbf4 loosened form
  (`^status:\s*open-gap`).

## [0.12.0] — 2026-07-14

### Added
- **Actionable-status wiki convention (family wiki-status backport)** (`references/wiki/README.md`,
  `scripts/oms_wiki_audit.py`, `skill-bodies/scholar-verify/SKILL.md`, `tests/test_oms_wiki_audit.py`) —
  a wiki note may now carry an optional `status: open-gap | resolved` frontmatter field (plus
  `blocked-on: <free text>` when open). `open-gap` marks an unresolved reviewer/audit finding that
  must ride every summary until closed; `resolved` is terminal; **absent = not actionable** (every
  existing note, byte-unchanged). This is the oms adaptation of the om*-family fix for the class of
  failure where actionable knowledge is recorded in the wiki but silently dropped from the dependent
  artifact — the wiki succeeds as an archive yet fails as a gate.
  - `oms_wiki_audit.py` gains a new `open_gaps` dimension that enumerates every `open-gap` note
    tree-wide (keyword-independent — walks the whole tree, not a ranked query), so a recorded finding
    cannot silently drop out of the next draft. A typo'd status is a WARN in the `frontmatter`
    dimension (`status` not in `{open-gap, resolved}`), because a mistyped value would silently leave
    the enumeration — the failure class itself.
  - `scholar-verify` gains an **Open wiki gaps (WARN)** check: it runs the `open_gaps` enumeration and
    refuses a clean PASS while any `open-gap` note is neither addressed in the draft nor explicitly
    deferred in the verdict. This is oms's carry-forward boundary (the summative gate). WARN only —
    oms has no launch boundary to hard-block at — so it does not count toward FAIL.
  - `grep -rlE '^status:\s*open-gap' .oms/wiki/` is the family-wide fallback enumeration (the on-disk
    `status:`/`blocked-on:` keys are identical across every om* harness).

### Verification
- `python3 -m pytest tests/test_oms_wiki_audit.py tests/test_scholar_verify_skill.py tests/test_wiki_spec_docs.py -q`
  green (5 new open-gap/unknown-status tests added; pre-existing verify-card item locks unaffected).

### Notes
- **Backwards compatible / additive-optional**: notes without a `status` key never surface as gaps and
  are byte-unchanged; the audit's frontmatter check stays WARN-never-FAIL. No new subsystem, storage,
  or scheduler — the existing audit CLI is the enumeration surface and the existing verify gate is the
  boundary.
- **Version-skew caveat**: the audit's stdlib splitter only reads `status`/`blocked-on`; it never
  strips them (read-only), so unlike a rewrite-on-merge tool there is no field-loss risk here.

## [0.11.0] — 2026-07-14

### Added
- **`citation_lookup()` MCP swap-point contract** (#35, `references/wiki/README.md`,
  `skill-bodies/scholar-research/SKILL.md`, `tests/test_wiki_spec_docs.py`,
  `tests/test_researcher_quote_anchor.py`) — abstract-function contract documented adjacent to
  `wiki_query()` (E1): signature `citation_lookup(doi_or_title) → verdict + normalized metadata`,
  the deterministic-lookup rule (P5-C), today's implementation target described precisely
  (`scripts/verify_bib_entry.py`: DOI path = Crossref then OpenAlex only on `HTTPError`, a
  `URLError` short-circuits to `NETWORK_ERROR`; title-only path = Crossref bibliographic search
  only; WebSearch/WebFetch is a separate agent-level manual fallback, never code-chained off exit
  codes), the Semantic Scholar/arXiv/Zotero MCP swap-points (opt-in citation sources, same human
  gate), and the empirical tool-description validation rule (probe an MCP server before trusting
  it). One pointer line in scholar-research's Execution_Policy naming the contract location.
- **GROBID intake reference card** (#36, `references/grobid-intake.md`,
  `skill-bodies/scholar-read/SKILL.md`, `skill-bodies/scholar-research/SKILL.md`,
  `tests/test_grobid_card.py`) — optional, self-hosted PDF-intake accelerator (E2, same genre as
  `references/wiki/audit.md`): flow (PDF → TEI → proposed BibTeX → human-confirm-every-entry →
  `verify_bib_entry.py` → only then `.bib`), hedged accuracy/failure-mode reporting (F1 ≈ 0.87–0.90,
  cited as externally reported, never asserted as settled fact), degrade path (absence = today's
  manual path, unchanged), and the proposes-never-commits boundary (cite-guard unaffected, not a
  citation authority). One pointer line each in `scholar-read` Step 1 and scholar-research's
  Execution_Policy.
- **Deep-research mechanics in `scholar-research` + `scripts/bib_coupling.py`** (#37,
  `skill-bodies/scholar-research/SKILL.md`, `scripts/bib_coupling.py`,
  `tests/test_bib_coupling.py`, `tests/test_researcher_quote_anchor.py`) — Step 2 reworked into
  the 4-field delegation template (objective / output format / tool guidance / boundaries, Anthropic
  pattern); fan-out sizing rule + hard cap (up to 3 concurrent read batches **inside** the single
  `mode=gap-research` pass, anchored to mock-review's 3-lens precedent — never separate
  citation-generating dispatches, E4); interleaved gap-check after each source batch; marginal-returns
  stopping heuristic (Undermind lesson — stop after 2 consecutive batches add no new method family and
  no new gap); optional `bib_coupling.py` clustering seed. `scripts/bib_coupling.py` (new, stdlib-only,
  zero-network, zero-embeddings, E3): bibliographic coupling over per-paper `.bib` reference lists —
  entry-key regex re-derived read-only from `hooks/scholar_cite_guard.py:25`, title normalization
  reuses `verify_bib_entry.py`'s `_norm()` idiom, DOI/title field extraction is new parsing work,
  connected components over pairwise shared-reference counts (`--min-shared`, default 2), `--json`
  output, exit 0/2. Step numbering (1–5) and Execution_Policy's "parallel citation generation is
  prohibited" sentence stay byte-unchanged (D10/E5); a new phrase-lock test pins that sentence since
  U1/U2/U3 all edit the same region.

### Fixed
- **`bib_coupling.py` final-review Minors (M1/M2)** — field extraction is delimiter-anchored so `title`
  never matches inside `booktitle`/`subtitle`; URL-form DOIs (`https://doi.org/…`, `dx.doi.org`) are
  normalized so they couple with their bare form. Both regression-tested (`tests/test_bib_coupling.py`).
- **Footprint tests skip `.claude/`** (`tests/test_scholar_pilot_skill.py`,
  `tests/test_scholar_pilot_moderator.py`) — the R5 footprint scans walked `ROOT.rglob("*")` excluding
  only `.git`/`node_modules`, so nested worktree checkouts under `.claude/worktrees/` leaked into the
  scan and failed the suite on the main checkout (surfaced right after the R5 squash-merge; green in
  any fresh clone — the tagged trees themselves are sound).

### Notes
- **Version bump deferred** — `plugin.json` stays `0.10.0` in this PR; `v0.10.0` is still untagged
  (R6 is stacked on the unmerged `feat/r5-research-companion`). Two pre-existing live-repo locks
  (`tests/test_version_sync.py::test_live_repo_surfaces_agree`,
  `tests/test_oms_doctor.py::test_live_repo_is_healthy`) correctly hard-fail on a 2-deep untagged
  release stack, so the bump waits rather than weakening those locks. **Post-merge procedure** (human,
  documented in the PR body): after R5 squash-merges, `v0.10.0` is tagged, and R6 merges back onto
  main (`git merge -X ours origin/main`) — one mechanical commit bumps `plugin.json` → `0.11.0` and
  retitles this section (formerly `## [Unreleased]`) to `## [0.11.0] — 2026-07-14` (with a fresh empty
  `[Unreleased]` above it), then R6 merges and `v0.11.0` is tagged. **Executed as documented — this
  section's retitle IS that mechanical commit.**
- **Stacked-PR merge order**: this branch's base is `feat/r5-research-companion`; R5 merges first.
- **omha card follow-up**: after this PR (eventually) merges, `oh-my-heroacademia`'s routing card
  (`cards/oms.json`) needs a separate PR bumping to `0.11.0` — out of this repo's scope; `sync_version.py`
  correctly shows `card:` DRIFT (routed to WARN by `oms_doctor.py`) until that PR lands.
- **P5 (#35–#37) closes the 2026-07-11 roadmap** (`docs/2026-07-11-oms-advancement-plan.md`). §6
  deferrals (Elo tournament, multi-model discuss, blunt Stop-loop, embeddings, fine-tuned reviewer
  artifacts) remain out of scope, unchanged from R5's Notes.

### Verification
- `python3 -m pytest tests/ -q` — **555 passed** (up from 518 at the R5 merge-base; R6 added 37 tests
  across `tests/test_bib_coupling.py` (new) and extensions to `tests/test_wiki_spec_docs.py`,
  `tests/test_researcher_quote_anchor.py`, `tests/test_grobid_card.py` (new)).
- `python3 scripts/sync_version.py` — exit 1, identical state to the R5 branch: `plugin`/`changelog`/`tag`
  rows PASS (pre-tag window), `card:` DRIFT only (foreign `cards/oms.json` read 0.8.0 at review time,
  0.9.0 after omha PR #5; the 0.11.0 card PR follows this merge). `oms_doctor.py` routes `card:` to WARN,
  so the doctor run stays exit 0 — same pattern as R4/R5.

## [0.10.0] — 2026-07-14

### Added
- **Research-log substrate** (#30, `references/output-layout.md`, `skill-bodies/scholar-pilot/SKILL.md`,
  `tests/test_scholar_pilot_skill.py`) — `.oms/<slug>/research-log.md`: durable, dated, append-only project
  narrative memory ("tried / decided / dropped — and why"), sibling of `reviews-log.md`. New §2.4
  entry-format contract in the output-layout SSOT (+ tree/§2.1 invariance bullet/§5 **KEEP** fate/§6
  checklist); wired into `scholar-pilot` Step 10 as an unnumbered sub-bullet (D10 — no renumbering) with a
  `--no-log` opt-out mirroring `--no-wiki`. Written only by the calling session; never a `.bib` source or
  citation authority (invariant 2).
- **`scholar-read` — external-paper deep-read (13th skill)** (#28, `skill-bodies/scholar-read/SKILL.md`,
  `skills/scholar-read/SKILL.md`, `agents/scholar-researcher.md`, `references/output-layout.md` §2.5,
  `tests/test_scholar_read_skill.py`, `tests/test_researcher_quote_anchor.py`) — turns "read this paper for
  me" into a structured, citation-safe note at `.oms/reading/<citekey>.md` (D1, sibling of `.oms/wiki/`,
  **NEVER** a `.bib` source — mandatory `NOT CITABLE` header). Single dispatch (invariant 1) to
  `scholar-researcher`'s new `mode=deep-read`; `mode=gap-research` stays the default with its output contract
  unchanged verbatim. Identity pre-check via `scripts/verify_bib_entry.py` runs without `--record`; a
  `RETRACTED` verdict is surfaced loudly. Wires into the research-log (context `read`).
- **`scholar-discuss` — standing Socratic discussion partner (14th skill)** (#29,
  `skill-bodies/scholar-discuss/SKILL.md`, `skills/scholar-discuss/SKILL.md`, `hooks/scholar_route_emit.py`,
  `tests/test_scholar_discuss_skill.py`, `tests/test_scholar_route_emit.py`) — on-demand debate partner
  (Contrarian / Simplifier / Ontologist stances, self-contained restatement per D3, provenance to
  `scholar-deepen` Round 4/6/8 without touching that file) with a Co-STORM-style moderator move over an
  in-session gap list of retrieved-but-unused evidence; exit appends to `.oms/wiki/decision/<slug>.md`
  (confidence/sightings frontmatter, pointerless → `confidence: low` per #24) and the research-log (context
  `discuss`). Zero `.tex`/`.bib` surface, no subagent dispatch (invariant 1 untouched); outline deltas are
  proposed at a human gate, never auto-applied (D9). Route hook STAGE enum grows to include `read|discuss`
  (D7 — same PR as `scholar-read`), gated on multi-word Trigger phrases only, never the bare tokens
  `read`/`discuss` (regression-tested against false-positive injection on ordinary prompts).
- **Mock-review rebuttal-and-reconsider round** (`--with-rebuttal`, #31,
  `skill-bodies/scholar-mock-review/SKILL.md`, `agents/scholar-reviewer.md`,
  `tests/test_scholar_mock_review_skill.py`) — lettered sub-steps 4(a)–4(e) inside the existing mock-review
  Step 4 (D10 — no renumbering): lock pre-rebuttal verdicts verbatim; author rebuttal at a human gate (D8);
  re-dispatch the same 3 lens roles to reconsider with an anchoring-aware under-adjustment guard (AgentReview
  finding); Area-Chair delta report capped at one venue-scale band per axis (LLM-sycophancy countermeasure)
  with per-weakness fixable/fundamental classification; the rebuttal flag + delta summary fold into the
  existing reviews-log field list rather than a second append step. Default path (no `--with-rebuttal`) is
  byte-unchanged.
- **Reviewer realism pack** (#32, `agents/scholar-reviewer.md`, `references/rubrics/venue-review-forms.md`,
  `references/venues.md`, `references/wiki/README.md`, `skill-bodies/scholar-mock-review/SKILL.md`,
  `tests/test_scholar_reviewer_realism.py`) — lens mode gains an aspect-checklist-first step (Reviewer2
  pattern: judge each venue-form aspect `strong|adequate|weak|n/a` before deriving strengths/weaknesses, never
  the reverse) plus a 2-tier `wiki_query` read of a private `reference/venue-review-examples-<venue>.md`
  few-shot note when present. AC mode gains a concession-threshold rule (severity/score moves only on
  concrete anchored evidence — a quote, a number, an experiment — never rhetorical concession) and an
  optional, off-by-default ensemble-variance move (N=2 resample of one borderline lens, reporting
  agreement/divergence instead of silently averaging). `venue-review-forms.md` gains a per-form empty
  "Score bands" template (band/meaning/source, "never guess") with a one-line pointer from `venues.md`; zero
  numeric calibration data is prefilled anywhere (D4).
- **Moderator pass before GATE 1** (#33, `skill-bodies/scholar-pilot/SKILL.md`, `agents/scholar-inspector.md`,
  `tests/test_scholar_pilot_moderator.py`) — unnumbered read-only sub-step in `scholar-pilot` Step 4
  (outline), between the mode-branching bullet and the GATE 1 line (D10 — GATE 1 line byte-unchanged):
  dispatches `scholar-inspector`'s new `mode=moderator` with the proposed outline + research/reading notes,
  printing a retrieved-but-unused evidence list + 1–2 pointed questions alongside the GATE 1 prompt for the
  human to weigh. `--skip-moderator` opts out; a dispatch failure fails open (GATE 1 is never blocked).
  `scholar-inspector` gains a Modes section (`mode=draft-critique` default, unchanged contract /
  `mode=moderator`, no verdict, no severity taxonomy — explicitly not a gate).
- **Preflight-style categorized verify report** (#34, `agents/scholar-verifier.md`,
  `skill-bodies/scholar-verify/SKILL.md`, `tests/test_scholar_verify_skill.py`) — `scholar-verifier`'s
  Output_Format regrouped under 5 fixed submission-checklist categories (`language` / `citations` /
  `formatting-metadata` / `tables-figures` / `declarations`), each showing a worst-severity roll-up;
  presentation-only regrouping — no pre-existing check added, removed, or reweighted. One new check: blind-
  review anonymization (WARN, double-blind venues only, never auto-edits).
- **Wiki-audit carry-overs — R4 follow-ups** (`scripts/oms_wiki_audit.py`, `references/wiki/audit.md`,
  `tests/test_oms_wiki_audit.py`) — frontmatter WARN split into "no frontmatter" (absent opening fence) vs
  "malformed frontmatter" (opening fence, no closing fence), both remain WARN (#24 non-blocking contract
  unchanged); regression test proving a content file mentioned ONLY by generated `INDEX.md` still clears the
  orphan WARN (already correct via `META_FILENAMES` — no script fix needed there); the ambiguous-stem token
  grammar's boundary behavior documented (`H.` vs `H-contrast.`, `F1` vs `F1b` non-collisions); the
  hyphen-adjacency regression guard was confirmed already present, so no new test was added. Detection-only
  discipline preserved — `--write-index` remains the sole write path.

### Notes
- **Carried over from R4's still-deferred list** — the do-not-touch list (`hooks/scholar_cite_guard.py`,
  `hooks/scholar_stop_guard.py`, `hooks/oms_atomic.py`, `scripts/oms_state.py`,
  `skill-bodies/scholar-deepen/SKILL.md`) kept R5 out of these, so they remain open: hooks' nearest-root
  ascent asymmetry (unify or intent-comment); `oms_state.py`'s slug error-string duplication (6 sites) plus
  its 4 deferred tests; the empty-Priority-Context drop path comment; the compact-time SessionStart "6 fires"
  investigation; `oms doctor` PASS-row suppression (cosmetic); `sync_version.py` row() wording coupling; a
  basename ceiling comment; live-corpus wiki migration (frontmatter backfill + INDEX generation on the actual
  workspace wiki — iCloud-synced, not git).
- GROBID intake for `scholar-read` is deferred to R6 (#36) — named in the skill body as a one-line future
  accelerator only, not implemented here.
- **omha card follow-up**: after this PR merges, the `oh-my-heroacademia` routing card (`cards/oms.json`)
  needs a separate PR adding `scholar-read`/`scholar-discuss` to `triggers.skills` and bumping its version —
  out of this repo's scope; the card correctly shows DRIFT below until that PR lands.
- **Out of scope this round** (unchanged §6 deferrals from the roadmap): Elo tournament, multi-model discuss,
  blunt Stop-loop, embeddings, fine-tuned reviewer artifacts. P5 (#35–#37) is R6.

### Verification
- `python3 -m pytest tests/ -q` — **518 passed** (up from 382 at the R4 merge-base; R5 added 136 tests across
  `test_scholar_read_skill.py`, `test_scholar_discuss_skill.py`, `test_scholar_reviewer_realism.py`,
  `test_scholar_pilot_moderator.py`, `test_scholar_verify_skill.py`, and extensions to
  `test_scholar_pilot_skill.py`, `test_scholar_mock_review_skill.py`, `test_researcher_quote_anchor.py`,
  `test_scholar_route_emit.py`, `test_oms_wiki_audit.py`).
- `python3 scripts/sync_version.py` — exit 1, exactly one drift line (`card:` — the foreign omha
  `cards/oms.json` still reads 0.8.0 until its separate PR lands; `plugin`/`changelog`/`tag` rows PASS via
  the pre-tag window). `oms_doctor.py` routes `card:` to WARN, so the doctor run stays clean — same pattern
  as the R4 (0.9.0) release.

## [0.9.0] — 2026-07-14

### Added
- **Wiki audit CLI — mechanical dimensions + INDEX generation** (`scripts/oms_wiki_audit.py`, `tests/test_oms_wiki_audit.py`)
  — read-only health-check over ONE `.oms/wiki/` tree per invocation (`--root`, default `./.oms/wiki`, no ascent
  — run once per level, local then global); five mechanical dimensions as pure functions over an in-memory
  `scan()` inventory: duplicate section tokens (fullmatch grammar, not prefix — `H-contrast.` never collides
  with `H.`), dangling cross-refs (`[[slug]]` / `[text](x.md)` / `file.md §S`), empty/orphan categories (fixed
  five names `convention/ pattern/ decision/ reference/ history/`, `.gitkeep`-documented-empty exempted),
  frontmatter validity (WARN only, never FAIL — non-blocking by design), and INDEX.md drift; dot-directories
  (`.omc/`, `.git`) are skipped during scan so the live corpus's stray `.omc/state/` never surfaces as a
  finding. The single opt-in write path is `--write-index`, which deterministically (re)generates
  `<root>/INDEX.md` via `atomic_write_text` — a derived, never-hand-edited artifact. Doctor-style
  `[PASS|WARN|FAIL] <dimension>: <message>` rows; exit 0 clean, 1 a FAIL-severity finding exists, 2 `--root`
  missing/usage error. A follow-up fix (`5eb5a43`) excluded self-refs and exact-name mentions from the orphan
  check.
- **Wiki audit procedure card — judgment dimensions + calibration lesson** (`references/wiki/audit.md`,
  `tests/test_wiki_audit_card.py`) — the two dimensions that require reading meaning and stay LLM-run: §2
  SSOT-delegation integrity (broken delegation, cyclic delegation — never flag a healthy one-directional
  delegation) and §3 strength-tag discipline, carrying the 2026-06-02 calibration block verbatim in substance
  (the rule's exact wording governs; a `[N편공통]` tag naming 2+ distinct papers passes even without inline
  quotes; a defect is only tagged-count > named-or-quoted distinct sources; at most one independence-cluster
  reminder per file). §4 generalizes the incident into a reusable lesson — **when a dimension's findings
  diverge from expectation, audit the criteria before the corpus.** §5 states detection-only discipline
  binding on both halves: the audit never edits the wiki: the one `--write-index` write is generated-artifact
  regeneration, not repair.
- **Frontmatter standard + INDEX.md contract in the wiki spec** (`references/wiki/README.md`,
  `references/output-layout.md`, `references/learning-protocol.md` pointer, `tests/test_wiki_spec_docs.py`)
  — a thin, stdlib-parsable frontmatter contract for every wiki note: flat `key: value` lines inside one
  `---` fence, no nesting/no lists/no PyYAML; required for new notes: `confidence: high|med|low` and
  `sightings: <int>`; optional `keywords: a, b, c` (one line, grep-only recall aid, never a query index).
  The old unscoped README sentence ("Each file is human-readable free-form .md. No machine-parsing schema
  (grep only)") is re-scoped to the **body** only — the frontmatter fence above it is the one machine-parsable
  part. `output-layout.md`'s `.oms/wiki/` block now lists all five categories (`pattern/` and `history/`
  added; `history/` global-level only) plus `INDEX.md — generated by scripts/oms_wiki_audit.py --write-index,
  never hand-edited`; `INDEX.md` is documented as browsable-for-humans-and-drift-detection, explicitly **not**
  a query surface (`wiki_query` recall stays deterministic grep over the notes themselves).
- **Light-channel evidence signal — force `confidence: low` on pointer-less appends** (`skill-bodies/scholar-pilot/SKILL.md`
  Step 10, `references/wiki/README.md`, `tests/test_scholar_pilot_skill.py`) — every wiki entry
  `scholar-pilot` auto-appends now states its evidence (an internal `<slug> §…` pointer or a verbatim quote);
  an entry with neither is **still appended** (no reject gate) but the note's frontmatter is created/kept at
  `confidence: low` with an `(evidence: none — add a pointer before confidence can rise)` marker, and
  evidence-less re-observation never raises confidence. Remains a **prompt-contract rule with no automated
  compliance check** — the audit script does not police it. The old Step 10 "no machine schema" sentence is
  replaced by a pointer to the new frontmatter standard.
- **Mock-review verdict history + meta-review mining** (`skill-bodies/scholar-mock-review/SKILL.md`,
  `references/output-layout.md`, `tests/test_scholar_mock_review_skill.py`) — one named carve-out in
  mock-review's read-only rule (the `.tex`/`.bib` prohibition itself stays verbatim): after the Area Chair
  verdict, the **calling session** (never the dispatched `scholar-reviewer` agent, whose
  `disallowedTools: Write, Edit, NotebookEdit` would silently no-op) appends one dated, append-only,
  create-if-absent entry to `.oms/<slug>/reviews-log.md` — date, venue, lens set, per-axis venue-scale
  scores, final verdict, top weakness types (anchored one-liners), rebuttal flag. A meta-review sub-step
  gates on **at least 3** logged entries (or explicit user request): mines recurring weakness types, flags
  "always-moderate" score drift (all verdicts borderline-band, low variance = calibration suspicion), and
  outputs **proposed** lens-prompt tweaks at a human gate — never auto-applied. `output-layout.md` records
  `reviews-log.md` as a durable **KEEP** fate at T18 cleanup (unlike renders/gen-image/tmp/versions/consensus).
- **Wiki-to-reference-card anchoring verb in `scholar-learn`** (`skill-bodies/scholar-learn/SKILL.md` new
  Step 6, `references/learning-protocol.md` pointer, `tests/test_scholar_learn_skill.py`) — a third
  promotion lane, distinct from venue-default promotion and local→global wiki elevation: promotes a mature
  *global*-wiki cluster (`confidence: high`, `sightings ≥ 3`, or explicit user request) into a `references/`
  card draft or existing-card update that **anchors, never copies wholesale** (wiki source pointers +
  `file:line` anchors into affected oms surfaces). Write happens only when the plugin root's `.git` **exists
  in any form** — an existence check, explicitly not `isdir` — because a linked git worktree's `.git` is a
  plain gitfile, not a directory; when `.git` is absent (marketplace install), the proposed card is emitted
  as text only, for the human to carry elsewhere. Human gate mandatory (reuses the core promotion gate);
  citation/.bib content permanently excluded, identical to the existing §6.F invariant.

### Notes
- **#25 scope — spec + script only, live-corpus migration deferred.** v0.9.0 ships the frontmatter standard,
  the audit script's INDEX generation, and the INDEX contract in the docs. It does **not** migrate the live
  workspace wiki corpus: adding frontmatter to the ~10 unmigrated files and generating the live `INDEX.md` is
  a separate, post-merge, workspace-side dogfood step (iCloud-synced, not git; conservative
  source-grounded confidence values; pre-migration file listing kept). No overclaiming — this release is
  spec + tooling, not a completed migration.
- **No hook changes this round** — nothing in #23–#27 needed turn-time injection; all 5 registered hooks
  (`scholar_route_emit`/`scholar_verify_emit`/`scholar_cite_guard`/`scholar_stop_guard`/`scholar_resume_emit`)
  are untouched, keeping this round's regression surface to CLI + prompt contracts + spec cards.
- **Still-deferred carry-overs** (excluded from R4, not silently forgotten — re-recorded from the R4 plan's
  Design-decisions Scope guard): the two hooks' nearest-root ascent asymmetry (unify or intent-comment);
  `oms_state.py`'s slug error-string duplication (6 sites) plus its 4 deferred tests (create-without-stage,
  garbage `started_at`, resume/clear negative gate, multi-marker cap serialization doc); the
  empty-Priority-Context drop path comment; the compact-time SessionStart "6 fires" investigation; `oms doctor`
  PASS-row suppression (cosmetic); `sync_version.py` row() wording coupling; a basename ceiling comment. The
  stray `.omc/state/` contamination inside the live global wiki is a **claudebase ticket**, not R4 — the audit
  script correctly does *not* surface it (dot-directories are skipped by the scan), and R4 does not delete it
  either.

### Verification
- `python3 -m pytest tests/ -q` — **382 passed** (up from 287 at the R3 merge-base; R4 added 95 tests across
  `test_oms_wiki_audit.py`, `test_wiki_audit_card.py`, `test_wiki_spec_docs.py`, and extensions to
  `test_scholar_pilot_skill.py`, `test_scholar_mock_review_skill.py`, `test_scholar_learn_skill.py`).
- `python3 scripts/sync_version.py` — exit 1, exactly one drift line (`card:` — the foreign omha
  `cards/oms.json` still reads 0.8.0 until its separate PR lands; `plugin`/`changelog`/`tag` rows PASS via
  the pre-tag window). `oms_doctor.py` routes `card:` to WARN; `sync_version.py` is a strict CLI and is
  expected to fail here — the live pytest lock (`test_live_repo_surfaces_agree`) deliberately excludes the
  card, so the suite stays green.

## [0.8.0] — 2026-07-13

### Added
- **Version SSOT + 4-surface sync checker** (`.claude-plugin/plugin.json` `"version"` field, `scripts/sync_version.py`)
  — pure drift-checker comparing `plugin.json`/CHANGELOG-top/latest git tag/the foreign omha card
  (`<OMHA_ROOT>/cards/oms.json`, skip-if-absent); tags parsed by exact `^v(\d+)\.(\d+)\.(\d+)$` match, a
  pre-tag window (latest tag may equal the *previous* released version, since tags are cut by the human
  after merge) is legal, and a non-object/malformed card degrades to `card: None` instead of crashing
  (fail-open on this externally-controlled surface). Read-only CLI (`tests/test_version_sync.py`'s
  `test_cli_read_only` pins this).
- **`atomic_write_text` wired to venue config** (`hooks/oms_atomic.py`, `skills/scholar-init/SKILL.md`) —
  the atomic writer (mkstemp + fsync + `os.replace`, shared core with `atomic_write_json`) is now used for
  `.oms/venues/<key>.yaml` writes, replacing the stale "if json; for yaml use a plain write" scaffolding
  sentence that had never been implemented against.
- **`consensus/` documented in the output-layout SSOT** (`references/output-layout.md`) — `.oms/<slug>/consensus/{stage}-{role}.md`
  per-run `--consensus`-mode handoff artifacts are now a named schema surface (workspace, cleaned at terminal),
  closing a drift between what `scholar-outline` actually writes and what the layout doc specified.
- **`oms doctor` — read-only packaging self-diagnosis** (`scripts/oms_doctor.py`) — categorized PASS/WARN/FAIL
  report over `[version]` (reuses `sync_version`), `[hooks]`, `[agents]`, `[skills]`, and optional `[state]`
  (with `--paper-root`); never writes anything. Card-absent and card-mismatched both map to WARN (foreign
  surface, separate release process), every other version-drift surface maps to FAIL. Exit 1 iff any FAIL row.
- **Agent cross-reference integrity tests** (`tests/test_agent_integrity.py`) — closes the silent-typo class
  across agents/skills/rubrics cross-references (model field validity, permission declarations, doc↔code
  tier agreement).
- **`scholar-verifier` re-tiered opus → sonnet** (`agents/scholar-verifier.md`, `README.md`,
  `references/rubrics/paper-eval.md`) — model field and both doc mentions reconciled together (closing the
  drift `test_agent_integrity.py` now guards).
- **Skill shim + `skill-bodies/` split** (`skills/<name>/SKILL.md` compact shims + `skill-bodies/<name>/SKILL.md`
  full bodies for all 12 skills, `tests/conftest.py` skill-body-path helper) — the always-loaded skill corpus
  (~92 KiB combined) is compacted under OMC's 64 KiB budget by moving full bodies to `skill-bodies/` and
  leaving byte-identical-frontmatter shims (+ one additive `oms-full-body:` key) in `skills/`; every
  pre-existing regression lock that reads skill text is repointed through the new conftest helper.
  `tests/test_skill_shim.py::test_corpus_under_omc_budget` asserts the live `skills/*/SKILL.md` corpus
  ≤ 48 KiB headroom (not just under the 64 KiB cliff itself).
- **`DISABLE_OMS` kill switch + route-hook relevance gate** (`hooks/scholar_route_emit.py`,
  `hooks/scholar_cite_guard.py`, `hooks/scholar_verify_emit.py`, `hooks/scholar_stop_guard.py`,
  `hooks/scholar_resume_emit.py`) — a universal early-exit env switch (`1/true/on/yes`, case/whitespace-insensitive,
  mirrors `DISABLE_OMC`) added to all 5 registered hooks, umbrella over the existing per-hook hatches
  (`OMS_CITE_GUARD`, `OMS_STOP_GUARD`); plus a keyword relevance gate (`is_paper_related`) in
  `scholar_route_emit.py` that skips the ~4.4 KB STAGE injection on clearly non-paper prompts
  (fail-toward-inject: any parse error or ambiguity still injects). Neither hatch is ever advertised in
  injected/deny/block text.

### Notes
- **omha card surface**: skip-if-absent by design (foreign repo, optional surface); present-but-mismatched
  routes to WARN in `oms doctor`, never FAIL. The card's own version bump (`oh-my-heroacademia/cards/oms.json`)
  rides a **separate `oh-my-heroacademia` PR**, never bundled into this repo's diff.
- Tag `v0.8.0` is cut by the human **after** this PR merges — `sync_version.py`'s pre-tag window (latest tag
  may equal the previous released version) covers the interim where `plugin.json`/CHANGELOG already say 0.8.0
  but the tag still reads `v0.7.0`.
- #16 deliberately chose `atomic_write_text` over a YAML→JSON migration — `references/venues.md`'s
  `.oms/venues/<key>.yaml` schema surface is untouched; only the writer underneath it changed.
- **Still-deferred R2 carry-overs** (excluded from R3 work, not silently forgotten): the two hooks' nearest-root
  ascent asymmetry (unify or intent-comment); `oms_state.py`'s slug error-string duplication (6 sites) plus its
  4 deferred tests (create-without-stage, garbage `started_at`, resume/clear negative gate, multi-marker cap
  serialization doc) — both from PR #7's Notes; commenting the empty-Priority-Context drop path, also from
  PR #7's Notes; and the compact-time SessionStart "6 fires" investigation, sourced from the R2 session record
  rather than the PR body.

### Verification
- `python3 -m pytest tests/ -q` — **287 passed** (up from 213 at the R2 merge-base; R3 added 74 tests across
  `test_version_sync.py`, `test_consensus_layout.py`, `test_oms_atomic.py` (extended), `test_oms_doctor.py`,
  `test_agent_integrity.py`, `test_skill_shim.py`, `test_kill_switch.py`, and `test_scholar_route_emit.py`
  (extended), plus repointing every pre-existing skill-body regression lock through the new `tests/conftest.py`
  helper).

## [0.7.0] — 2026-07-13

### Added
- **`.oms/state/` pipeline schema + `scripts/oms_state.py` CLI** (`references/output-layout.md` §2.2) — two
  state shapes, both written *only* through this CLI (atomic via `oms_atomic`, strict enum validation, slug
  regex, `paper_root` recorded on create): `pilot-<slug>.json` (`write` — stage/gate_status/open_fail_ids/
  paper_root) and `revise-<slug>.json` (the round/strike ledger, below). `scholar-pilot` now writes state at
  every stage boundary and GATE decision, and `--from` reads it (`oms_state.py read`) to propose a resume
  stage instead of guessing.
- **Revise marker + mechanical strike/round ledger** (`scripts/oms_state.py`, `skills/scholar-revise/SKILL.md`)
  — `revise-start` is idempotent on resume (a crash/compaction resume never zeroes the counters or extends
  the TTL clock), takes `--force-restart` for an intentional reset, and clamps `--max-rounds` to 1–20 /
  `--ttl-hours` to 1–168; `revise-round` mints a fresh `round_id` each round and flags `"exceeded": true` past
  max-rounds (the CLI never blocks — the skill decides to stop); `strike --defect-id` counts recurrences and
  flags `third_strike: true` at 3 — replacing self-reported "recurs 3 times" with a grep-countable signal;
  `revise-end` closes the marker (`done|stopped|abort`) on every loop exit path.
- **Scoped Stop guard for the revise loop** (`hooks/scholar_stop_guard.py`) — blocks a stop attempt only while
  a `revise-<slug>.json` marker is live, scoped by nearest-first ascent to `.oms/state/` and containment
  against the marker's `paper_root` (never guesses scope); the slug is derived from the marker filename, never
  from trusted JSON content. Six independent exemptions let the guard step aside: inactive/non-live marker,
  any strike ≥3, round ≥ max_rounds, TTL expiry (skew-safe — a negative age never extends the guard), a
  sibling pilot marker's `gate_status == "abort"`, and a durable `stop_blocks` cap of `max(10, 2×max_rounds)`.
  On block, `stop_blocks` is incremented via atomic write *before* the block reason is printed — a failed
  increment allows the stop instead of risking a wedge. Human escape hatch `OMS_STOP_GUARD` in
  `{off,0,false}` (env, never advertised in the reason); the `revise-end` exit path *is* advertised in the
  block reason (unlike cite-guard's hidden hatch — ending the loop and reporting to the human is the desired
  behavior here); the platform's own turn-ender after 8 consecutive blocks is documented as the structural
  backstop underneath all of this.
- **Verifier round-id echo** (`agents/scholar-verifier.md`) — when `scholar-revise` hands the verifier a
  `round_id`, the verdict's `Round ID` line must echo it verbatim; a missing or mismatched echo voids that
  verdict, and `scholar-revise` discards it and re-verifies rather than counting the round.
- **SessionStart resume advisory + post-compaction re-injection** (`hooks/scholar_resume_emit.py`, matcher
  `startup|resume|clear|compact`) — on any session start, ascends to the nearest `.oms/` and, for each
  in-scope non-terminal pilot, prints a one-line advisory (stage/gate_status/open_fail_ids, plus round/strikes
  if a live revise marker exists); silent when there is nothing to advise, so a plain non-paper session pays
  zero injection tax. When `source == "compact"`, additionally re-injects the notepad's `## Priority Context`
  section verbatim (bounded to 2,000 chars) — implemented as `SessionStart(source: "compact")`, not
  `PreCompact` (see Notes). Read-only — the hook never writes a file.
- **`<Interruption_And_Resume>` abort/resume spec** (`skills/scholar-pilot/SKILL.md`) — on entry, a
  non-terminal `pilot-<slug>.json` is surfaced before any stage starts (resume / restart-from-earlier-stage /
  discard, never a silent restart from stage 1); choosing "discard" writes `gate_status=abort` (plus
  `revise-end --status abort` if a revise loop is also live), and `abort` is terminal — the resume advisory
  stops reporting the marker and the Stop guard stops honoring it; markers older than 14 days are flagged
  stale (still the human's call, never auto-discarded); mid-stage interruption resumes from the last
  stage-boundary write.
- **Notepad 3-tier convention** (`references/output-layout.md` §2.3) — `## Priority Context` (replace-on-write,
  bounded to 2,000 chars, owned by scholar-pilot), `## Working Notes` (dated append under `### YYYY-MM-DD`,
  7-day auto-prune at pilot entry — prune duty explicitly assigned to scholar-pilot), `## Manual` (human-owned,
  never written or pruned by automation).

### Notes
- #13 (post-compaction re-injection) is implemented via `SessionStart(source: "compact")`, not `PreCompact` —
  verified against the hooks documentation: `PreCompact`'s JSON-output contract has no context-injection
  channel (`additionalContext` is only available from `Stop`/`SubagentStop`/`SessionStart`), so a `PreCompact`
  hook's output cannot survive compaction.
- #14 (session envelope + `O_EXCL` lock) is deliberately deferred, pending an observed multi-session collision
  (plan §5, conditional) — not implemented in this release.
- This branch is stacked on the unmerged R1 branch (`feat/r1-citation-integrity`, CHANGELOG `[0.6.0]`); tag
  `v0.7.0` only after both PRs merge. Version-SSOT sync across `plugin.json`/README/CHANGELOG remains open as
  P2 #15.

### Verification
- `python3 -m pytest tests/ -q` — **213 passed** (baseline at the R1 merge-base was 144; R2 added 69 tests
  across 7 new/extended test files: `test_oms_state.py`, `test_revise_ledger_contract.py`,
  `test_round_id_contract.py`, `test_scholar_stop_guard.py`, `test_scholar_resume_emit.py`,
  `test_state_schema_docs.py`, and an extension to `test_plugin_integrity.py`).

## [0.6.0] — 2026-07-11

### Added
- **PreToolUse citation-write interlock** (`hooks/scholar_cite_guard.py`) — denies (a) new `.bib` entry keys with no
  record in the `.oms/state/verified-citations.json` allowlist and (b) new `\cite{K}` in `.tex` with no entry in any
  sibling `.bib`. Fail-open, stdlib only. Human escape hatch `OMS_CITE_GUARD=off` (env; deliberately not advertised
  in deny reasons). Registered as a third hook in `.claude-plugin/plugin.json`.
- **Mechanical DOI/retraction pre-gate** (`scripts/verify_bib_entry.py`) — verifies DOI existence + retraction status
  via publisher-registered retraction notices in Crossref `update-to` relations, plus OpenAlex's `is_retracted` flag. Verdicts VERIFIED/MISMATCH/RETRACTED/NOT_FOUND/NETWORK_ERROR
  (exit 0/1/1/1/2). `--record` writes only VERIFIED keys into the allowlist via `oms_atomic` (never touches `.bib`).
  Polite-pool mailto via `OMS_CROSSREF_MAILTO` env.
- **Claim-faithfulness (`citation-misuse`) WARN check** (scholar-verifier / scholar-verify) — stance labels
  supports/contrasts/mentions judged only from research-note quote anchors; mismatches surface as a human-confirmation
  list; unanchored pairs are reported as "check not run".
- **`% [MATERIAL GAP: …]` drafter token** + uncited-claim WARN scan in the verifier — missing material becomes a
  greppable token instead of a plausible inference, and FAILs the verify gate like TODO.
- **Per-claim verbatim quote anchoring** (`Quote: "…" (locator)` / `quote-missing (abstract-only)`) in the
  scholar-researcher output contract — the substrate the claim-faithfulness check reads from.

### Fixed
- **22 (+1 latent) regression-guard assertions realigned with the English corpus** (1940cc6 drift) — suite was red
  at 84/106 before this branch.
- **Enforced SSOT reading priority (Defect A)** — fact-checking/writing skills had no
  mechanism forcing them to read the primary SSOT
  (`.oms/<slug>/outline/outline.md` + `methodology/*.md`) first when starting work,
  so secondary material (`research_summary/code_survey/*`) got read first, making it possible to
  misjudge by mapping the chapter numbers of notes that went stale through structural
  redesign onto the current structure. Prescription: new `references/learning-protocol.md`
  §8 (SSOT reading order — primary outline·methodology > secondary research·code_survey, with the two rules
  "absence ≠ out of scope" and "outline = authority on the chapter axis") + enforcing SSOT-first reading in
  `scholar-inspect` Steps §1 (the real gap where inspect only read .tex). draft was
  left unchanged because the existing "⚠️ .md SSOT first" (L31) already satisfies it (avoiding duplication).
- **Codified the completion condition for `.tex`↔`.oms` sync (Defect B)** — there was no completion
  condition requiring that, after a `.tex` structural change (moving a section, changing a title, swapping an equation,
  adding a \cite), the outline·methodology·decision records be updated within the same task,
  so .oms drift remained stale (isomorphic to omp's "completion condition for index sync after organize").
  Prescription: added a sync completion condition to the `<Output>` of `scholar-draft`·`scholar-revise` (revise includes a decision record
  of the `SECTION_REVIEW_DECISIONS` type) + a `references/output-layout.md` §6 checklist item.
  Simple prose corrections (no structural change) are exempt. Forcing a verify re-run was excluded as too heavy.

### Docs
- `docs/2026-07-11-oms-advancement-plan.md` — roadmap #0–#37 (P0 citation interlock through P5 MCP swap-points +
  scholar-read/discuss).
- `docs/2026-07-11-r1-citation-integrity-execution.md` — R1 execution plan.

### Verification
- `python3 -m pytest tests/ -q` — **144 passed** (up from 141 pre-R1 + Defect A/B's 103; includes the citation-integrity
  regression suites and `tests/test_ssot_priority_and_sync.py` (7 cases, that suite's own lineage at the time: 96 → 103 passed) — drift guard for the Defect A·B mechanisms
  (learning-protocol §8 existence·reading order, inspect SSOT-first, draft·revise sync completion conditions,
  output-layout checklist)).

## [0.5.0] — 2026-06-01

### Added
- **Injected writing craft rules — new `references/writing-craft.md` SSOT**. The root cause of the drafter's output being awkward across the four dimensions of flow·tone·
  logic·structure was *not architecture but the absence of writing-rule content*
  (writing vocabulary lived only in the inspector prose lens, and even that only in the post-hoc critique lane — zero means to shape flow·tone at generation time). The
  four-dimension rules in a single card: §1 FLOW (Gopen-Swan old→new·banana rule)·§2 TONE (banning ornamental
  verbs·adjectives on principle·em-dash cap)·§3 LOGIC (one-ping·TEEL·overgeneralization warning)·§4 STRUCTURE (CARS
  3-move·OCAR·hourglass)·§5 VOICE (discipline>journal>personal)·§6 EXEMPLAR (~5 random representatives,
  no embedding)·§7 machine check tokens (verifier WARN SSOT). Role-separated from `latex.md` (typesetting); drafter·
  inspector·verifier *reference* it (no re-listing — same drift prevention as the abstract-WARN precedent). Source anchors:
  Gopen & Swan 1990·Swales CARS·Schimel OCAR·Peyton Jones·Nature HB 2025·AutoSurvey·WriteHERE.
- **Reinforced the drafter generation flow — skeleton stage + silent self-audit** (`agents/scholar-drafter.md`).
  Step 4.5: before prose, produce a per-paragraph reasoning skeleton `{claim, cite-keys, link}` (confirming occupation of CARS Move-2·
  one-ping, in the `.oms/<slug>/` workbench — reused by the inspector reverse-outline). Step 5.5:
  silent self-audit against §2/§7 criteria before returning (hygiene, not a gate — does not violate the no-self-approval rule). Citation
  core unchanged (the ban on inline fabrication extends to the skeleton stage, retaining single-careful generation).
- **planner rhetorical structure axis — `<Rhetorical_Axis>`** (`agents/scholar-planner.md`). *Orthogonal* to the v0.4.0 section-order
  model (flat/system/thesis): CARS 3-move (**Move-2 gap enforced** — if the Intro only states territory,
  reject is the #1 priority)·OCAR arc·hourglass width matching·arc chosen by reader patience (venue variation). A
  "1 proposition to argue" field added to the section brief. Places the researcher gap statement as the niche move (not new generation).
- **verify writing WARN** (`agents/scholar-verifier.md` step 9.6 + `references/rubrics/paper-eval.md`).
  Machine-detects the writing-craft.md §7 tokens (ornamental words·em-dash·rule-of-three·negation parallelism) but as **WARN (not FAIL)** —
  exactly the abstract-WARN (0.4.x) precedent (forced FAIL would be a false-positive due to static-blocklist rot·over-detection risk).
  Multibyte em-dash is confirmed via Python `re`.
- **Reinforced inspect lenses** (`agents/scholar-inspector.md`). Upgraded the prose lens to writing-craft.md §1/§2
  actionable checks + a **reverse-outline audit** (extract topic sentences → connect to thesis,
  reusing the drafter skeleton) + added an **overgeneralization flag** to the logic lens (a claim broader than its cited support = #1 priority,
  the #1 failure mode at 51% — formative-only, no auto-FAIL by the citation-safe boundary, sibling to assumption=FRAGILE).
- **learn bifurcation — `venue.prose_defaults`** (`references/learning-protocol.md` enum +
  `references/venues.md` `voice`/`prose_defaults` fields). Universal writing propositions (old→new·em-dash cap) are
  promoted to venue-enforced defaults (human gate), while user/venue-specific *expression preferences* are wiki `pattern/`
  light (advisory). citation/.bib remains permanently non-promotable (§6.F).

### Verification
- 6 new regression-guard files, 45 tests (writing-craft card 7 sections·drafter skeleton/self-audit·planner
  rhetorical-axis orthogonality+v0.4.0 regression·verify WARN≠FAIL·inspect lenses·learn bifurcation). 53 → **98 passed**.
- reviewer 2-lane PASS: spec-compliance (all 6 components COMPLIANT, invariants·non-goals observed) +
  code-quality (ship-ready, 0 CRITICAL/MAJOR, 1 MINOR tautology addressed).

### Notes
- **WARN ≠ FAIL** rationale: writing rules suffer static-blocklist rot (authors start avoiding 'delve') and
  mix in contextually legitimate uses (over-detection), so forced FAIL would be a false-positive — detection is WARN/formative only.
- **repo/project boundary**: writing-craft.md is a *universal* rule distributed to all users. This-paper/this-user-specific
  expressions go only into per-project `.oms/wiki/pattern/` (light) — never leak into the distributed card (all-file
  proper-noun-0 guard).
- Design·plan: `docs/specs/2026-06-01-writing-craft-injection/{design,plan}.md`.
- ⚠️ Runtime reflection requires a marketplace update + app restart (plugin cache reload).

## [0.4.0] — 2026-05-31

### Added
- **Paper structure model — 'common skeleton + scale variation' in `scholar-planner`** (`agents/scholar-planner.md`
  `<Structure_Types>`, `references/venues.md` `structure_type`). The common skeleton shared by all academic papers
  (`Introduction → [Method unit 1..N: Overview→Proposed→experiments for that unit] → Conclusion`) is
  made explicit in planner, and `structure_type` (`flat` | `system` | `thesis`) divides *how many times the skeleton is repeated·
  how far it is unfolded* (scale). flat=short paper (IROS/RA-L), system=multi-contribution journal system paper (T-RO),
  thesis=multi-contribution dissertation (sub-forms thesis-by-papers vs monograph). Added a structure_type
  field to the venues.md schema + IROS=flat·POSTECH thesis=thesis examples. Rationale: external-context literature survey (IMRaD·Milford·
  Brown H2R·SPJ·IEEE RA-L·T-RO field data·York/Oxbridge thesis guide — source URLs in
  `docs/specs/2026-05-31-paper-structure-model/design.md`).

### Fixed
- **Blocked the "technical white paper" anti-pattern** — the previous planner had only a flat (short-paper) structure
  model, so even given a dissertation·multi-contribution system paper, it would outline in a conference-style
  flat structure that listed methods across multiple sections + **piled all experiments into one place at the end**
  (occurred in a real dissertation). Now, at any scale, it mandates "experiments stay inside the unit where the method
  was proposed". Investigation_Protocol·Success_Criteria alignment + regression guard
  `tests/test_thesis_structure.py` (6 cases — common skeleton·three variations·technical-white-paper anti-pattern·monograph/by-papers
  distinction·structure_type field·generality proper-noun-0). 39→48 passed.
- **Removed the hardcoded `06_outline.md` prefix → `outline.md`** (`skills/scholar-outline/SKILL.md`,
  `agents/scholar-planner.md`, 7 places). It was a meaningless number (clashing with concept notes `01~06_*.md`). Unified
  to a number-free filename, the same as plan.md.

## [0.3.1] — 2026-05-31

### Fixed
- **Codified the `.md` intermediate-output location rule — preventing source folder pollution** (`references/output-layout.md`,
  `skills/scholar-research|ideate|outline/SKILL.md`). During real use (master's thesis work),
  there was an incident where the `.md` intermediate outputs of research/ideate/outline (research map·concept notes·outline) were
  mistakenly created in the citation-bound source folder (`paper/…`). Two causes: ① `output-layout.md`
  specified only `.tex`/`.bib`/PDF locations and **did not specify (a gap)** the `.md` layer, ②
  the bodies of `scholar-research`/`scholar-ideate` **induced as examples** `paper/research`·`paper/methodology`
  → **self-contradicting** the card's "source ≠ intermediate" source-protection principle.
  Prescription:
  - In `output-layout.md` §0·§2·§2.1·§6, specify the `.md` stage layers (`research/ methodology/ outline/`) as a
    **fixed-path SSOT** under `.oms/<slug>/` — since these notes are *inputs* (scaffolding) for the draft and
    not user assets, they go in the workbench (`.oms/`), leaving only `.tex`/`.bib` in the source folder.
  - Corrected the output-save instructions in the bodies of `scholar-research`/`scholar-ideate`/`scholar-outline`
    from `paper/…` → `.oms/<slug>/{research,methodology,outline}/` (including the ambiguous "project note
    folder" wording).

### Added
- **Regression-guard tests** (`tests/test_md_stage_layout.py`, 3 cases). ① whether `output-layout.md`
  specifies the 3 `.md`-layer folders as SSOT (preventing gap recurrence), ② whether the `.md`-stage skill bodies are free of
  source-folder misdirection (`paper/research` etc.) (preventing self-contradiction recurrence), ③ whether each skill points to
  the correct workbench path. Full suite 39 → 42 passed.

## [0.3.0] — 2026-05-31

### Added
- **`scholar-mock-review` skill — venue-aware mock review** (`skills/scholar-mock-review/SKILL.md`).
  Judges the user's *own* paper from the standpoint of a target-venue reviewer — venue-scale score + evidence-anchored
  strengths/weaknesses + venue-native verdict (accept/borderline/reject · letter A~D · minor/major revision). oms's
  third evaluation axis = **adjudicative judgment** (distinct from inspect=coach, verify=machine gate). Seeing the same .tex,
  inspect says "fix it" (author's side), mock-review says "if I were the reviewer, this is my score·verdict" (judge). Originated from the user's request
  "if I submit to IROS, score it to match its character and give the shortcomings·revision verdict".
- **`scholar-reviewer` agent** (`agents/scholar-reviewer.md`, opus, read-only). Two modes:
  (1) `mode=lens` — evaluate strength/weakness (location anchor required) through one lens of soundness/novelty/clarity-significance,
  (2) `mode=area-chair` — synthesize 3 lenses → venue-form per-axis score → re-check → accept-bias
  calibration → venue-native final verdict. Ensemble 3-lens parallel + AC meta pass (read-only, so citation-safe aligned).
- **`references/rubrics/venue-review-forms.md`** — SSOT of per-venue review forms. Form 1 (NeurIPS/ICLR/ICML
  1-4/1-10/1-5) · Form 2 (CVPR/ICCV labels) · Form 3 (IROS/ICRA letter A~D, multi-axis, no numbers) ·
  Form 4 (journal minor/major revision). ⚠️ **Conference vs journal verdict vocabulary separation** — major/minor revision is
  journal-only; conferences use accept/borderline/reject (+rebuttal). All scales verified against the primary source (official reviewer
  guideline·IEEE RAS·arXiv), source URLs specified.

### Changed
- **`references/rubrics/paper-eval.md` 2-axis → 3-axis**: added the mock-review (adjudicative) axis to
  inspect(formative)/verify(summative). Expanded the core separation table·"why separation matters" to 3 axes (coach ≠ machine
  ≠ judge). Codified mock-review citation safety (drop anchorless weakness·downgrade novelty questions).
- **`references/venues.md`** — at the top, made explicit the role separation between venue *constraints* (page_limit·sections) and *review forms* (venue-review-forms.md).
- **`hooks/scholar_route_emit.py`** — added `mock-review` to the STAGE catalog (.tex layer, a judgment axis different from inspect).
  Updated the `STAGE(paper) → <…|inspect|mock-review|verify|…>` token line. Retains stdlib only·fail-open.
- **`.claude-plugin/plugin.json`** — registered scholar-mock-review in skills[] (between inspect↔verify).
  Passes `test_plugin_integrity.py` (plugin.json↔skills/ 1:1 enforced).

### Design / Evidence
- Design rationale: `docs/specs/2026-05-31-scholar-mock-review/design.md`. Based on a survey of prior work on LLM paper review
  (MARG arXiv:2401.04259 — single-prompt generality 60%→ensemble 29%; AI-Scientist Nature 2026 — ensemble+AC
  ~human accuracy; DeepReview ACL 2025 — re-check stage; ICLR 2025 20K real deployment — reliability gate before emit),
  decided the architecture (ensemble 3-lens+AC) and guardrails (anchor enforcement·novelty-question downgrade·injection defense·accept-bias
  calibration). All claims cite URLs.

## [0.2.0] — 2026-05-31

### Added
- **`scholar-init` skill — stage-0 bootstrap for a new paper** (`skills/scholar-init/SKILL.md`). Ports the sibling
  `omp-init`'s verified bootstrap pattern (GATE 0 idempotency → read-only diagnosis → human gate GATE 1 →
  write) into the paper domain. Asks only ≤3 things in the first session (folder location·venue·one-line topic, progressive
  disclosure) and creates a standard directory scaffold (`sections/`·`figures/`·`refs/`·`data/`·`preamble.tex`·
  `meta.md`) + `.oms/<slug>/` workbench + a per-paper `.oms/wiki/`. At start, references the **parent folder's
  `.oms/wiki/` (global level, discovered via ascent)** as a seed to recommend "the venue·structure you usually use"
  — the more you use it, the faster the next paper starts. Scaffold only — 0 body·citation generation (citation-safe).
- **2-tier global wiki (parent folder `.oms/` = global, this paper's `.oms/` = local)**. Replaced *only the implementation*
  of the `wiki_query` abstract function with a 2-tier ascent merge (`agents/scholar-inspector.md`) — like git's `.git`
  lookup, takes the nearest parent `.oms/` as global and merges with local, tagging the source as `[wiki:local]`/
  `[wiki:global]`. **Call sites unchanged** — ascent·merge are all confined inside the implementation. 0 absolute paths·
  env vars·XDG (work-root relative, no distributed-artifact pollution). Only reusable assets are promoted to global (disposition·venue
  forms·reusable decisions·`history/`); paper-unique·**citation/.bib are permanently banned from global promotion** (§6.F).
- **`hooks/oms_atomic.py`** — atomic JSON write (tempfile→fsync→os.replace, stdlib only,
  cross-platform, `ensure_ascii=False`). Port of the omp_atomic pattern, for scholar-init's state-file writes.
- **`tests/test_plugin_integrity.py`** — enforces plugin.json `skills` field == actual `skills/` directory
  1:1 (drift prevention). In this process, the once-unregistered `scholar-deepen`·`scholar-learn` were also
  corrected to be registered (all 11 including scholar-init registered).

### Changed
- **Added the `init` STAGE to the routing hook** (`hooks/scholar_route_emit.py`): stage-0 bootstrap guidance +
  added init to the `STAGE(paper) → <init|research|…|scholar-pilot>` token line. Includes the idempotency cue "if `.oms/<slug>/`
  already exists, it's not init".
- **`scholar-pilot` Step 0 — absorb init (recommend)**: when `.oms/<slug>/` is absent, recommend
  scholar-init before research (not auto-entry — won't create folders without the user knowing). Skip if already present (idempotent).
  Added a global-promotion candidate hint to Step 10 wiki capture (terminal only, citation excluded).
- **`scholar-learn` local→global wiki promotion path** added — a separate lane that, after a human gate, raises light assets (disposition·forms·reusable decisions·history)
  to the parent `.oms/wiki/` (distinct from venue-default promotion, citation excluded).
- **`references/wiki/README.md`·`learning-protocol.md` §1.4** — codified the 2-tier ascent contract·global boundary
  table (what is eligible to go global)·"reconciliation with the user-scope-ban anti-pattern".
- **New `references/omc-backport-analysis.md` §4 — review of reverse backport of omp 0.2.0 (0 adopted).**
  Adversarially verified whether to reverse-backport into oms the 5 items the sibling omp added in 0.2.0 (content_conventions·content audit·dead-link·CONVENTIONS.md·
  specificity content item) → all REJECT. oms is a generation pipeline, so it lacks the premise of an rules.json regex audit loop, and
  prose quality is already handled by the inspect/verify rubrics (for citation-bound work, meaning rather than patterns governs
  accuracy). Recorded "0 reverse adoptions" permanently to prevent repeated re-review. 0 code changes — docs only.
- **Extended the routing hook contract** (`hooks/scholar_route_emit.py`, UserPromptSubmit): added the
  `deepen` token to the STAGE catalog — the `scholar-deepen` skill (claim-ambiguity gate between research↔ideate) was newly added and is
  reflected on both the stage list and the `STAGE(paper) →` line
  (`research|deepen|ideate|outline|draft|inspect|verify|revise|scholar-pilot`). Retains stdlib only·
  fail-open pattern. (Symmetric with omd `route_emit.py`'s addition of the `revise` token — since the hook is a contract, both
  changes are recorded explicitly.)
- Routing hook test (`tests/test_scholar_route_emit.py`): updated stage-enumeration verification from 8→9
  (including `deepen`). Retains the existing 7 + verify 7 = 14 passed.

### Verification
- `pytest tests/` — **39 passed** (oms_atomic 7 + route 11 + verify 7 + scholar-init lint 11 +
  plugin-integrity 4 — some include existing tests). 0 regressions after scholar-init·global wiki·hook changes.
- Independent reviewer 2-lane (spec-compliance + code-quality) passed — re-verified after addressing 2 must-fix (plugin-integrity
  parser `Path(s).name`-ification, oms_atomic mkstemp-unbound guard) + 1 doc clarity (`history/` global-only
  specification).
- plugin.json `skills` ↔ actual `skills/` directory 11:11 alignment (integrity test enforced).
- Old expressions (absolute paths·env vars·XDG) grep clean for residuals (excluding the negative statement "no env var, no XDG").
- Both hooks emit valid JSON when run (confirmed `init` token included).

## [0.1.1] — 2026-05-28

### Added
- **STAGE routing hook** (`scholar_route_emit.py`, UserPromptSubmit): after omha decides the lane, within the paper domain it declares the stage each turn in one line, `STAGE(paper) → <research|…|scholar-pilot> · rationale`. Tone-unified with omha's `ROUTE →` and omd's `STAGE(docs) →` (text labels, no emoji). Registered UserPromptSubmit in plugin.json.
- 7 routing-hook tests (`test_scholar_route_emit.py`): contract specification·8-stage enumeration·citation-safety wording·no label collision·stdlib only·fail-open.

### Changed
- README routing section: corrected "oms does not place a routing hook" → it does place a STAGE hook (lane is still omha's job, oms handles STAGE only).

### Verification
- `pytest tests/` — 14 passed (verify 7 + route 7).
- **Runtime end-to-end verification complete**: ran scholar-verify on a real .tex/.bib (5 defects planted), caught all 5, did not auto-fix citations (human-confirm list), confirmed inspect/verify boundary adherence. (Resolved v0.1.0's "runtime unverified" backlog.)

## [0.1.0] — 2026-05-28

First edition. A Claude Code plugin harness that treats paper writing "like code writing".

### Added
- **8 stage skills** (single SKILL.md, OMD style): `scholar-research`, `scholar-ideate`, `scholar-outline` (.md layer) → `scholar-draft`, `scholar-inspect`, `scholar-verify`, `scholar-revise` (.tex layer) → `scholar-pilot` (full orchestration). Each skill has Triggers keywords + `Task(subagent_type="oh-my-scholar:scholar-*")` dispatch.
- **5 agents** (OMC 11-section `<Agent_Prompt>` XML):
  - `scholar-researcher` (sonnet, read-only) — related work·gap·citation verification
  - `scholar-planner` (opus, read-only) — outline·story arc
  - `scholar-inspector` (opus, read-only) — formative critique (logic/prose), not pass/fail
  - `scholar-verifier` (opus, read-only) — summative automatic gate, triple no-self-approval
  - `scholar-drafter` (sonnet, write) — the only .tex/.bib writer, single-careful, no citation fabrication
- **4 reference cards** (guardrail SSOT): `formats/latex.md`, `formats/bibtex.md`, `rubrics/paper-eval.md` (inspect/verify 2-axis separation), `venues.md`.
- **citation-safe PostToolUse hook** (`scholar_verify_emit.py`): injects a citation-verification reminder on .tex/.bib edits. A citation-safe variant of OMC's post-tool-verifier — does not instruct auto-fix.

### Notes — design identity
- **3 citation-safety principles**: ① read in parallel / generate singly ② no auto-fix (.bib is human-confirmed) ③ concepts (.md) settled first. Because hallucinations in papers aren't caught as compile errors, OMC's automatic throughput is *not* used for *content generation*.
- **reviewer upgrade**: rearranged paper-write's flat 5-reviewer score into the two layers OMC inspect(formative)≠verify(summative). figure/citation/latex-lint are absorbed as internal verifier checks rather than separate agents → compressing 5 reviewers into 4 agents.
- **OMC pattern port**: ralph PRD `passes:true` gate (scholar-revise), `<External_Consultation>` (what OMD missed), triple self-approval, 3 GATEs (human).
- **Routing non-dependence**: oms is a domain handler. The work-mode lane decision is omha (oh-my-heroacademia)'s job → oms has no UserPromptSubmit routing hook.

### Verification
- `pytest tests/` — 7 passed (hook: .tex/.bib detection·silence on non-papers·no-auto-fix·stdlib only·fail-open).
- 5 agents: 11-section XML, 4 read-only disallowedTools, verifier triple self-approval, only drafter writes, all have External_Consultation (grep verified).
- 8 skills: Triggers + dispatch + plugin.json skills array alignment (8 exact match).

### Backlog
- v2 candidates: `scholar-translate` (KO→EN), `scholar-standardize` (inductive style from existing papers).
- OMD backport (separate session): #1 External_Consultation, #2 ralph PRD gate, #3 triple self-approval, #4 PostToolUse integrity hook.
- runtime end-to-end verification: real scholar-pilot run after loading a new session (only structure·hook verified, actual behavior unverified).

[0.1.0]: new
