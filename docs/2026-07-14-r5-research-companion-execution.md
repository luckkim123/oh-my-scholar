# R5 Execution Plan — Research-Companion Expansion (P4 #28–#34 + R4 carry-overs)

| Field | Value |
|:--|:--|
| Round | R5 → release v0.10.0 |
| Branch / worktree | `feat/r5-research-companion` @ `.claude/worktrees/oms-r5`, base = main `81a6831` (v0.9.0) |
| Source roadmap | `docs/2026-07-11-oms-advancement-plan.md` §P4 (#28–#34) + R4 final-review carry-overs (wiki-audit ×4) |
| Method | SDD: fresh implementer (sonnet) + spec-compliance review + code-quality review per task, sequential in one worktree; final opus review before PR |
| Suite baseline | 382 passed on main; every task keeps the full suite green |

## Binding invariants (verbatim from the roadmap + repo; violations are BLOCKING)

1. **Single careful generation, parallel reading only.** No task may introduce parallel `.tex`/content generation. Mock-review lens re-scoring (#31) is read-only fan-out — allowed.
2. **No citation auto-fix; citations never promoted; reading notes / research-log are NEVER `.bib` sources.** The only door into the bibliography remains scholar-research → human-confirmed `.bib` (cite-guard enforced).
3. **No embeddings in oms's own recall.** All new recall is deterministic grep/set-ops.
4. **Degrade-first.** No new runtime dependency, no MCP requirement, stdlib Python only.
5. **Human gates never automated away.** GATE1–3, learn promotion, mock-review "proposed never auto-applied", rebuttal authored at a human gate, discuss outline-deltas proposed-not-applied.
6. **Mechanical packaging gates**: new skills registered in `.claude-plugin/plugin.json` `skills[]`; shim ≤ 4,096 B with `oms-full-body` frontmatter key + `skill-bodies/<name>/SKILL.md` body (shim corpus ≤ 48 KiB — currently 13,083 B); `tests/test_skill_shim.py`, `test_plugin_integrity.py`, `test_agent_integrity.py` must pass unmodified in intent (extend, don't weaken); existing skill/agent frontmatter stays byte-frozen except where a task explicitly says otherwise.
7. **Detection-only discipline** for audit tooling (T8): the audit never repairs; `--write-index` remains the single write path.

## Design decisions locked by this plan (implementers do not re-litigate)

- **D1 — Reading notes live at `.oms/reading/<citekey>.md`** (sibling of `.oms/wiki/`, NOT under `.oms/<slug>/`): a reading corpus outlives any one paper project. `<citekey>` is a *filename convention* (`<firstauthor><year>-<short-slug>`), explicitly NOT a BibTeX key; every note carries a mandatory header line `> NOT CITABLE — secondary memo. A .bib entry may only be created via scholar-research verification.`
- **D2 — The calling session writes; dispatched agents stay read-only.** scholar-researcher (deep-read), scholar-inspector (moderator), scholar-reviewer (lens/AC) all keep `disallowedTools: Write, Edit, NotebookEdit`; the calling session materializes their returned content to disk (same carve-out as reviews-log, `skill-bodies/scholar-mock-review/SKILL.md:75-85`).
- **D3 — scholar-discuss personas are self-contained.** The Contrarian / Simplifier / Ontologist prompts are restated in the discuss body adapted for standing debate (one-line provenance note pointing at scholar-deepen Round 4/6/8). We do NOT extract a shared personas card and do NOT edit scholar-deepen — deepen's persona text is test-locked and its gate semantics differ (ambiguity-triggered rounds vs on-demand stances).
- **D4 — No fabricated calibration data.** #32's score-band table and few-shot review examples ship as *documented slots + population procedure*, never prefilled numbers or invented example reviews. Score-band structure lives in `references/rubrics/venue-review-forms.md` (the review-form SSOT — venues.md `:5` explicitly delegates review-form content there); few-shot examples are a wiki convention (`.oms/wiki/reference/venue-review-examples-<venue>.md`) the reviewer reads when present.
- **D5 — Moderator pass is a fresh read-only subagent** (`scholar-inspector`, new `mode=moderator`), not the calling session: fresh context is the anti-groupthink point (Co-STORM). Inspector fits the lane: formative questions, no verdict.
- **D6 — research-log is a skill-level `.md` contract, not an `oms_state.py` verb.** Machine state stays pipeline-only; the log is human-readable narrative memory.
- **D7 — Route-hook stage enum grows once**, in T3, adding both `read` and `discuss` (T2 ships the skill; T3 makes it routable — same PR, sequencing note). Hook literal-substring tests are updated in the same commit; the R3 relevance gate mechanism (fail-toward-inject) is not touched.
- **D8 — Rebuttal content is authored at a human gate.** The calling session drafts candidate rebuttal responses from the paper + verified evidence; the human edits/approves BEFORE lenses re-score. Lenses never see an unapproved rebuttal.
- **D9 — scholar-discuss outline deltas are proposed at a human gate, never auto-applied.** This is deliberately MORE conservative than roadmap #29's "appends to … the living outline": auto-mutating a GATE1-approved artifact from a discussion session would breach invariant 5. The deviation is intentional and visible here, not buried in a task bullet.
- **D10 — Step numbering is frozen.** `tests/` lock pilot and mock-review step headings via `str.index()` anchors (e.g. `_step10_section()`, `_step4_section()`). Every R5 insertion into an existing skill body is an **unnumbered sub-bullet or lettered sub-step inside an existing step** — never a new top-level number, never a renumbering.

---

## Task list (sequential; each = fresh implementer + 2 reviews; suite green after each)

### T1 — #30 research-log substrate

**Goal**: durable, dated, append-only project memory: `.oms/<slug>/research-log.md`.

- **Contract** (new §in `references/output-layout.md` + wired into scholar-pilot):
  - Location `.oms/<slug>/research-log.md`; entry format: `## YYYY-MM-DD — <context: pilot|discuss|read|manual>` followed by free-prose bullets covering `tried / decided / dropped — and why`. Append-only, create-if-absent; the calling session writes it (D2); never contains citation keys as authority (secondary memo clause, invariant 2).
  - Cleanup fate in output-layout §5: **KEEP** (same row style as reviews-log.md); add to §2 tree, §2.1 invariance, §6 checklist.
- **Pilot wiring**: append the research-log entry as an **unnumbered sub-bullet INSIDE the existing Step 10 (wiki-capture) block** (mirroring Step 10's existing sub-bullets), summarizing the run (stages executed, GATE outcomes, major decisions, dropped directions). The literal headings `10. **wiki capture` and `11. **terminal cleanup` stay byte-identical — no top-level renumbering (D10; `_step10_section()`'s two `.index()` anchors back 6 tests). `--no-log` opt-out flag mirroring `--no-wiki`.
- **Files**: `references/output-layout.md`, `skill-bodies/scholar-pilot/SKILL.md` (+shim byte-size stays ≤4,096 — shim unchanged), `tests/test_scholar_pilot_skill.py` (extend; keep both `_step10_section()` anchors valid), other tests.
- **Tests**: contract-phrase locks — output-layout mentions `research-log.md` in tree + KEEP fate; pilot body contains the append step + `--no-log`; grep-provable phrases (e.g. "append-only", "NOT a .bib source" wording per invariant 2).
- **Acceptance**: full suite green; `git grep research-log` hits output-layout, pilot body, tests only.

### T2 — #28 scholar-read (external-paper deep-read stage)

**Goal**: a 13th skill turning "read this paper for me" into a structured, citation-safe reading note.

- **New skill** `scholar-read` (shim + body, plugin.json registration):
  - Shim: standard `OMS:COMPACT-SKILL-SHIM` pattern, ≤4,096 B, frontmatter `name: scholar-read` + description + Triggers (`논문 읽어줘, 이 논문 정리, 딥리드, 리딩노트, read this paper, deep read, reading note, analyze this paper` …) + `oms-full-body`.
  - Body: input = ONE external paper (PDF path under `refs/` or elsewhere, arXiv id/URL, or pasted text). Steps: (1) resolve input, verify paper identity metadata mechanically (title/authors/venue/DOI via `scripts/verify_bib_entry.py` lookup path when a DOI/title is available — verification of the *paper's own identity*, no `.bib` write, no `--record`); (2) single dispatch `Task(subagent_type="oh-my-scholar:scholar-researcher", mode="deep-read")`; (3) calling session writes `.oms/reading/<citekey>.md` (D1 header mandatory); (4) research-log append (T1, context `read`); (5) surface note path + one-paragraph digest — a `RETRACTED` identity verdict is restated here, loudly.
  - Degrade path: no DOI/metadata resolvable → note carries `identity: unverified` in frontmatter and says so; PDF unreadable → ask for text. GROBID intake is R6 (#36) — body may name it as a future optional accelerator in one line.
- **Researcher mode branch** (`agents/scholar-researcher.md`): add a Modes section using scholar-reviewer's lens/area-chair idiom. `mode=gap-research` (default) = current contract verbatim (existing output contract text is NOT reworded); `mode=deep-read` output contract: `## Paper identity` — surfaces the `verify_bib_entry.py` verdict **verbatim** (`VERIFIED | MISMATCH | RETRACTED | NOT_FOUND | NETWORK_ERROR`; a `RETRACTED` source gets a loud explicit marker in the note — qualitatively different from merely-unchecked), `## Claims` (each with verbatim quote ≤3 sentences + locator — reuse the R1 #5 quote-anchor contract), `## Method`, `## Evidence` , `## Limitations`, `## Relation to my work` (only if the caller supplied project context; otherwise omitted), `## Open questions`. Same injection hygiene and no-fabrication rules as the default mode. The frontmatter `description:` of `agents/scholar-researcher.md` IS updated to mention both modes (scholar-reviewer's documented-in-description idiom); no test locks that string.
- **output-layout.md**: add `.oms/reading/` at root level (§2 tree, §2.1, §5 fate **KEEP**, §6) with the NOT-CITABLE clause.
- **Tests**: `tests/test_scholar_read_skill.py` (shim/body contract phrases: single dispatch, mode=deep-read, NOT CITABLE header, no `--record`, RETRACTED-handling phrase lock); researcher-agent mode locks (extend the existing researcher/agent test file); test_plugin_integrity + test_skill_shim pass with 13 skills.
- **Acceptance**: suite green; `.oms/reading/` present in all four output-layout surfaces; no `.bib`-writing instruction anywhere in the new skill.

### T3 — #29 scholar-discuss (standing Socratic discussion) + route-hook enum update

**Goal**: a 14th skill — on-demand debate partner over ideas, zero `.tex` surface.

- **New skill** `scholar-discuss` (shim + body, plugin.json):
  - Triggers: `토론하자, 아이디어 논의, 반론해줘, 디스커션, discuss this idea, devil's advocate, argue with me, challenge my idea` ….
  - Body: interactive mode in the main session (no content generation, so no subagent required; invariant 1 untouched). Steps: (1) frame — restate the topic + load context (`.oms/<slug>/research/*.md`, `.oms/reading/*.md`, outline if present); (2) stance rounds — user picks or session proposes one persona per round: **Contrarian** ("what if the opposite were true / baseline sufficient / paper survives without it?"), **Simplifier** ("keep only 1 of 3 contributions / halve the experiments — what drops?"), **Ontologist** ("what IS this thing; which entity's naming is shaky?") — self-contained restatement, provenance note → scholar-deepen Round 4/6/8 (D3); (3) **moderator move (Co-STORM)**: maintain an in-session gap list of retrieved-but-unused evidence (evidence present in research/reading notes but absent from the discussion and outline); when a round closes or discussion stalls, inject the highest-information-gain unasked question from that list; (4) exit — summary appended to wiki `decision/` (light channel, R4 frontmatter contract: `confidence:`/`sightings:`; pointerless summary → `confidence: low` per #24) + research-log entry (context `discuss`); outline deltas are **proposed as a list at a human gate, never applied** (D9).
  - Hard boundary section: discuss produces no `.tex`, no `.bib`, no citations; claims made during discussion are marked `unverified` unless anchored to a note.
- **Route hook** (`hooks/scholar_route_emit.py`): stage enum `init|research|deepen|ideate|outline|draft|inspect|mock-review|verify|revise|learn|scholar-pilot` grows to include `read|discuss`; one-line stage descriptions added in the CHECKPOINT text; relevance-gate keyword list gains **MULTI-WORD phrases matching each new skill's Triggers** (e.g. `deep read`, `reading note`, `read this paper`, `discuss this idea`, `devil's advocate`, `argue with me`, `논문 읽어`, `토론하자`) — **never the bare tokens `read` or `discuss`**, which are `\b`-matched and would fire the 4-KB CHECKPOINT on ordinary prompts. Add a regression test asserting a generic non-paper prompt containing the bare word "read" does NOT trigger injection. Update the literal-substring tests (`tests/test_scholar_route_emit.py`) in the same commit; DISABLE_OMS umbrella and fail-open behavior untouched.
- **Tests**: `tests/test_scholar_discuss_skill.py` (persona presence, gap-list move, wiki decision/ + confidence:low rule, no-.tex boundary, proposed-not-applied outline deltas); route hook tests updated for the new enum; shim/integrity suites pass with 14 skills.
- **Acceptance**: suite green; route hook emits `read` and `discuss` in the STAGE enum (test-locked).

### T4 — #31 rebuttal-and-reconsider round in mock-review

**Goal**: `--with-rebuttal` turns the rebuttal *guide* into a measured round with a delta report.

- **mock-review body** additions — the rebuttal round (a)–(d) lands as **lettered sub-steps of the EXISTING Step 4** (`4a/4b/4c/4d`, all gated on `--with-rebuttal`), keeping the literal headings `4. **Verdict-history append` and `5. **Output the synthesis report` byte-unchanged — no renumbering (D10; `_step4_section()` anchors must survive):
  - (a) **Lock**: record per-lens pre-rebuttal verdicts + per-axis scores verbatim (they are already in hand from Step 2) — the locked block is quoted in the final output; lenses are never re-asked to restate their originals.
  - (b) **Author rebuttal at a human gate (D8)**: calling session drafts point-by-point candidate responses to the AC's prioritized author-questions, each anchored to paper text or verified evidence (anchor-less responses are marked as such); human edits/approves before anything is re-dispatched.
  - (c) **Reconsider**: re-dispatch the SAME 3 lens roles (`mode="lens"`, parallel read-only) with: original paper target + their own locked pre-rebuttal review + the approved rebuttal. Anchoring-aware instruction (AgentReview lesson stated in the body: human reviewers systematically under-adjust): judge ONLY whether each rebuttal response materially addresses the weakness — re-score per axis, verdict `addressed | partially | unaddressed` per weakness, with anchors.
  - (d) **AC delta report**: pre vs post score table per axis + per-weakness classification **fixable vs fundamental** (addressed-by-rebuttal ⇒ fixable; untouched core weakness ⇒ fundamental); final verdict may move at most one venue-scale band per axis — an **LLM-sycophancy countermeasure** (distinct from the AgentReview under-adjustment finding, which motivates the anchoring-aware instruction in (c); this cap guards the opposite failure — an LLM AC over-rewarding a well-worded rebuttal).
  - (e) reviews-log: the rebuttal flag `true` + one-line delta summary **fold into the EXISTING Step-4 Verdict-history-append field list** — one write, one owner; NOT a separate append step.
- **Files**: `skill-bodies/scholar-mock-review/SKILL.md`, `agents/scholar-reviewer.md` (small: lens mode gains the reconsider-input contract; AC mode gains the delta-report format), `tests/test_scholar_mock_review_skill.py` (extend; `_step4_section()` anchors must survive).
- **Tests**: contract phrases in `test_scholar_mock_review_skill.py` (lock-before-rebuttal, human gate, one-band cap, fixable/fundamental, rebuttal flag in log fields); reviewer agent locks.
- **Acceptance**: suite green; without `--with-rebuttal` the flow is byte-wise unchanged behavior (default path untouched — tests assert existing contract phrases survive).

### T5 — #32 reviewer realism pack (calibrate, never fabricate)

**Goal**: measurably-less-generic lenses + a calibrated AC, with zero invented data (D4).

- **Aspect-checklist-first** (`agents/scholar-reviewer.md`, lens mode): before writing S/W items, enumerate the mapped venue form's aspects (from `rubrics/venue-review-forms.md` Form 1–4) and judge each aspect explicitly (`per-aspect: strong|adequate|weak|n/a` line), then derive S/W from the weak/strong aspects (Reviewer2 pattern, named).
- **Concession-threshold rule for the AC** (clean-room, idea only): the AC lowers a weakness's severity or raises a score ONLY on concrete anchored evidence (a quote, a number, an experiment) — never on rhetorical concession, author confidence, or repetition. One paragraph in AC mode + one line in the mock-review body.
- **Score-band slot** (`references/rubrics/venue-review-forms.md`): per-form optional block `Score bands (populate from public venue stats — keep a source URL per row; never guess)` with an empty 3-column template (band / meaning / source) + a one-line pointer from `references/venues.md` meta section (venues.md keeps delegating review-form content — no score data lands in venues.md). The reviewer/AC read the band block **when populated**; when empty they say "no calibration data — uncalibrated venue-scale estimate".
- **Few-shot review examples slot**: wiki convention documented in `references/wiki/README.md` reference/ category: `venue-review-examples-<venue>.md` (user-collected real reviews, private, never shipped); lens mode reads it when present (2-tier wiki_query as already specified). One paragraph, no new mechanism.
- **Ensemble variance (optional move)**: AC MAY request one additional independent sample of a single borderline lens (N=2 total for that axis, read-only) and report agreement/divergence instead of silently averaging — documented as optional, off by default.
- **Tests**: reviewer agent substrings (aspect-first, concession threshold, uncalibrated disclaimer); rubrics doc test (band template present, "never guess" phrase); wiki README mention.
- **Acceptance**: suite green; `git grep -i "score band"` hits rubrics card + venues.md pointer + tests only; no numeric score-band data anywhere.

### T6 — #33 moderator pass before GATE1

**Goal**: anti-groupthink check between researcher and planner, surfaced AT the human gate.

- **Pilot body**: new read-only sub-step between Step 4 (outline) and the GATE1 line: dispatch `Task(subagent_type="oh-my-scholar:scholar-inspector", mode="moderator")` with the proposed outline + paths to `.oms/<slug>/research/*.md` (and `.oms/reading/` when relevant). Output: (a) retrieved-but-unused evidence list (evidence rows present in notes, absent from outline), (b) 1–2 pointed questions. The calling session prints both verbatim alongside the GATE1 prompt; the human decides. `--skip-moderator` opt-out. On dispatch failure: proceed to GATE1 with a one-line notice (fail-open, gate never blocked by the moderator).
- **Inspector mode branch** (`agents/scholar-inspector.md`): Modes section — `mode=draft-critique` (default; current contract verbatim) / `mode=moderator` (read-only scan, questions only, NO verdict, no severity taxonomy — explicitly not a gate). The frontmatter `description:` IS updated to mention both modes (same idiom as scholar-reviewer/researcher); no test locks that string.
- **Tests**: pilot body substrings (between Step 4 and GATE1, opt-out flag, fail-open clause); inspector agent mode locks; agent-integrity suite untouched.
- **Acceptance**: suite green; GATE1 semantics unchanged (still human-only).

### T7 — #34 preflight-style categorized verify report

**Goal**: verify output readable as a submission checklist without changing what is checked.

- **Verifier agent** (`agents/scholar-verifier.md`): Output_Format regrouped — the existing per-item PASS/FAIL/WARN rows are presented under 5 fixed category headers: `language` (terminology, writing discipline, abstract discipline) / `citations` (citation consistency, claim-faithfulness, uncited-claim, DOI) / `formatting-metadata` (compilation, venue meta, page/cite limits) / `tables-figures` (fig/table refs, **undefined references** — the compile-log grep row, distinct from the \ref/\label row — and numeric consistency) / `declarations` (placeholders/[MATERIAL GAP], anonymization). Category header shows worst severity within it. **No check is added, removed, or reweighted** except the one new check below; WARN-never-FAILs rule unchanged.
- **New check — blind-review anonymization (WARN)**: only when the mapped venue form/venues.md indicates double-blind: grep for `\author`/`\thanks`/acknowledgment blocks, self-identifying phrases ("our prior work" + \cite pattern), non-anonymized repo/grant IDs. WARN with locations; never auto-edits (invariant).
- **Verify skill body**: one short section naming the categorized report + the anonymization check; defect-class list gains `anonymization (WARN)`.
- **Tests**: verifier agent substrings (5 category names, worst-severity roll-up, anonymization WARN + double-blind condition); verify body lock.
- **Acceptance**: suite green; every pre-existing defect class still named in the agent (mapping is complete — test enumerates them).

### T8 — R4 carry-overs: wiki-audit ×4 (verify-then-fix; detection-only preserved)

For each item the implementer FIRST writes/roots a failing-or-passing probe against current `scripts/oms_wiki_audit.py` behavior, then fixes only what is actually deficient (the R4 follow-up `5eb5a43` may have absorbed some):

1. **Orphan-vs-INDEX neutralization**: prove whether a content file mentioned ONLY by `INDEX.md` still WARNs as orphan after `--write-index` (it must — INDEX is generated). If already correct via META_FILENAMES, keep the regression test only.
2. **Frontmatter WARN: absent vs malformed**: split the single WARN message — `no frontmatter` (no opening fence) vs `malformed frontmatter` (opening fence without a closing fence — the one malformation `_parse_frontmatter` can actually distinguish today; a colon-less key line is silently skipped at `:52` and detecting it would be NEW mechanism, out of scope). Both stay WARN (never FAIL, #24 contract).
3. **Ambiguous-stem specification**: document the token grammar (`re.fullmatch`, `§?[A-Z][0-9]*[a-z]?`) and its boundary behavior in `references/wiki/audit.md` (mechanical-dimension section) — what is and is not a collision; add the missing spec sentence rather than new mechanism.
4. **Hyphen-adjacency regression guard**: explicit test locking `H-contrast.` vs `H.` non-collision (and `F1` vs `F1b`), if no such test exists.

- **Files**: `scripts/oms_wiki_audit.py` (only if a probe proves a defect), `references/wiki/audit.md`, `tests/test_oms_wiki_audit.py`.
- **Acceptance**: suite green; audit remains read-only (`--write-index` sole write path — test re-asserted).

### T9 — Release: v0.10.0

- `.claude-plugin/plugin.json` version → `0.10.0`; CHANGELOG `## [0.10.0] — <date>` (Added per feature with `(file, test)` provenance; Notes: carried-over items that remain — list explicitly; omha card follow-up named).
- README: stage skeleton gains scholar-read + scholar-discuss (now 14 skills); agents table notes researcher/inspector modes; citation-safety section unchanged; Status test count updated to measured value.
- `python3 scripts/sync_version.py` → pre-tag window PASS (tag v0.10.0 comes after merge, by the user; omha card 0.10.0 = separate omha-repo PR after merge — this task only NOTES it).
- Full suite run, count recorded; `oms_doctor.py` run clean.
- **Acceptance**: `sync_version.py`'s plugin.json / CHANGELOG / latest-tag surfaces all PASS; the **omha card shows expected DRIFT** (exit 1 on the card row is acceptable here, not a gate failure — the card bump is the separate post-merge omha-repo PR named in Notes); suite green; README/CHANGELOG/plugin.json agree.

---

## Sequencing & risk notes

- Order T1→T9 strictly (T1 substrate feeds T2/T3; T3 carries the single route-hook enum change; T4 before T5 because T5 edits the same reviewer file with knowledge of the rebuttal contract).
- **Do-not-touch list**: `hooks/scholar_cite_guard.py`, `hooks/scholar_stop_guard.py`, `hooks/oms_atomic.py`, `scripts/oms_state.py`, `skill-bodies/scholar-deepen/SKILL.md`, existing GATE semantics — R5 has no business there; any diff in these files is a spec violation except the explicitly-named test files.
- Shim-corpus budget: +2 shims ≈ +2–4 KiB on 13,083 B — far under 48 KiB; test enforces.
- The omha routing card (`oh-my-heroacademia/cards/oms.json`) lists skills — after R5 merges, the 0.10.0 card PR must add `scholar-read`/`scholar-discuss` to `triggers.skills` (out of this repo's scope; recorded in CHANGELOG Notes + PR body).
- Out of scope (unchanged §6 deferrals): Elo tournament, multi-model discuss, blunt Stop-loop, embeddings, fine-tuned reviewer artifacts. P5 (#35–#37) is R6.
