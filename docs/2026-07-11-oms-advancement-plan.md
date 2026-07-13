# oms Advancement Plan — OMC v4.15.2 Alignment · Ecosystem Survey · Research-Companion Roadmap

| Field | Value |
|:--|:--|
| Subject harness | oh-my-scholar (oms) v0.5.0 + Unreleased, git `1940cc6` |
| Reference harness | oh-my-claudecode (OMC) v4.15.2, sha `d41f1730`, via the claudebase deep-analysis bundle (`claudebase/docs/reference/omc-deep-analysis-v4.15.2/`) |
| Date | 2026-07-11 |
| Method | 6 cluster auditors + 2 ecosystem researchers (parallel, sonnet). 34 load-bearing claims then re-derived by 7 independent adversarial verifiers — **27 CONFIRMED / 6 CORRECTED / 1 REFUTED**, verdicts folded in before use (the REFUTED claim is dropped below). ~15 further claims spot-verified directly by the lead session, including a runtime probe of the route hook. Final document reviewed by a 2-lens critic panel (consistency: sonnet; judgment: opus) — both approve; 5 findings folded in (see §9). |
| Prior work | claudebase `gaps/oh-my-scholar.md` (single-pass gap analysis, 6 candidates — this report supersedes-and-extends its oms-side view) and oms's own `references/omc-backport-analysis.md` (OMC 4.14.4 adopt/exclude ledger, T1–T15 — remains the adopt/exclude SSOT; this plan does not overturn any of its exclusions). |
| Scope beyond the omx precedent | Two axes the omx alignment audit did not have: an external ecosystem survey (academic AI tools + Claude Code/MCP ecosystem), and a **research-companion vision roadmap** (advisor / colleague / paper-reader / reviewer / consultant roles). |
| Scope note | `path:line` citations are against oms `1940cc6` and will drift with commits. |

---

## Executive verdict

**oms ported OMC's judgment IP faithfully and is ahead of OMC in several places; the deficit is concentrated in three axes — prose-only enforcement, packaging/state hygiene, and companion-role scope — and the external ecosystem both validates oms's core invariant with hard numbers and hands it its next integrity frontier.** Where oms chose to port (T1–T15), fidelity is high and often domain-improved: the mock-review lane carries injection defense and anchor-required weaknesses OMC's judge patterns lack (`agents/scholar-reviewer.md:45,67,83`), the verifier bakes a snapshot-correlation token into the *agent contract itself* rather than a mode wrapper (`agents/scholar-verifier.md:38,51`), the outline consensus adds a mechanical file-existence rubber-stamp guard OMC's ralplan does not have (`skills/scholar-outline/SKILL.md:92`), and the two-channel learning protocol ties promotion friction to consequence with a 5-condition AND-gate (`references/learning-protocol.md:249-267`) plus a schema-level citation exclusion stronger than anything in OMC's stores.

**Axis 1 — enforcement is prose where the harness's own reason-to-exist demands an interlock.** Every guarantee the pipeline advertises is text the model must voluntarily obey: the citation invariant has no PreToolUse backstop (a fabricated `@article{...}` lands in `.bib` before `scholar_verify_emit.py` fires — PostToolUse only), the GATE ladder is three prose markers (`skills/scholar-pilot/SKILL.md:50,54,56`), the revise 3-strike counts nothing anywhere durable (`skills/scholar-revise/SKILL.md:32,46` — no counter file), and `--from <stage>` resume has no state schema to read (`skills/scholar-pilot/SKILL.md:71`; the file never defines one). All six prior-gap candidates re-confirm; the deepened finding is that they share one root: **`.oms/state/` has prose, not a schema.**

**Axis 2 — hygiene drift accumulated silently because nothing checks it.** Four version surfaces disagree (plugin.json has *no* version field; CHANGELOG says 0.5.0; git tags stop at v0.3.0; the omha card hardcodes 0.1.0 — its skill list, however, is verified current). `hooks/oms_atomic.py` is a solid writer (mkstemp + fsync at `:41` + `os.replace` — an earlier "no fsync" claim was adversarially REFUTED) **with zero real call sites**: the one artifact its docstring names, the venue config, is written plain because it's YAML (`skills/scholar-init/SKILL.md:71`). A live schema drift exists (`consensus/` written by scholar-outline `:91` but absent from the output-layout SSOT — 0 grep hits). The always-loaded skill corpus is 89,236 B, past OMC's 64 KiB compaction threshold. The route hook injects ~4.4 KB of stdout on *every* prompt including non-paper ones (measured: `{"prompt":"hello"}` → rc 0, 4,448 B). There is no doctor, no kill switch, and no agent-reference integrity test.

**Axis 3 — of the five companion roles the maintainer wants (advisor · colleague · paper-reader · reviewer · consultant), only "reviewer" is built.** scholar-mock-review is genuinely strong; the colleague-discussant role is essentially absent (deepen's Contrarian/Simplifier/Ontologist rounds — `skills/scholar-deepen/SKILL.md:59-61` — are consumed as a one-shot pre-outline gate, never exposed as a standing mode), and reading *someone else's* paper has no stage (scholar-researcher's output contract is my-paper-gap-shaped, `agents/scholar-researcher.md:60-77`). The ecosystem survey supplies the mechanics: Co-STORM's moderator + gap-tracking, AgentReview's rebuttal-and-reconsider round, co-scientist's meta-review, and — most importantly — measured citation-hallucination rates (GPT-4o 78–90% on multi-paper synthesis per OpenScholar's benchmark; 14–95% across 13 models in GhostCite; ~100 hallucinated citations found *in accepted NeurIPS 2025 papers* despite human peer review) that justify hardening the invariant into mechanism, and the next frontier beyond existence-checking: **claim-faithfulness** (does the cited source support *this specific claim*), which the 37k-star academic-research-skills plugin already ships.

### Per-cluster scorecard

| Cluster | Fidelity | Headline |
|:--|:--|:--|
| hooks-enforcement | mostly-parity | Fail-open discipline present and test-locked (better than OMC's dual-plane drift); no PreToolUse interlock, no kill switch, unconditional 4.4 KB/turn injection. |
| pipeline-loop | mostly-parity | Consensus/revise logic faithful with two oms-original guards; GATEs, 3-strike, and resume are prose-only — no state schema exists. |
| knowledge | mostly-parity | Two-channel protocol is principled and in places stronger than OMC; wiki health tooling exists only outside the plugin; light channel un-scored. |
| state-packaging | drift | 4-surface version drift, atomic-writer unused (writer itself sound), consensus/ schema drift, no doctor, corpus past compaction threshold. |
| research-lane | parity+ | Research/deepen/ideate faithful; mock-review ahead of OMC judge patterns; missing rebuttal round, calibration data, and any durable research log. |
| agents-skills | parity | 4-key frontmatter contract fully used; verifier over-provisioned at opus; no agent cross-reference tests; no shim layer at 89 KiB. |

---

## §1 Findings by cluster

Verification marks: ✅ = adversarially verified or lead-verified this pass; (C) = folded correction.

### 1.1 hooks & enforcement

- **No PreToolUse citation interlock — ABSENT ✅.** plugin.json registers exactly 2 hooks (UserPromptSubmit → `scholar_route_emit.py`, PostToolUse `Edit|Write|MultiEdit` → `scholar_verify_emit.py`). `scholar_verify_emit.py` fires *after* a `.tex`/`.bib` write lands and only reminds. Nothing structurally stops the main session from writing a fabricated `.bib` entry. This is the single highest-leverage gap in the harness (roadmap #1).
- **No kill switch — ABSENT ✅ (C).** No `os.environ`/`getenv`/`DISABLE` mechanism anywhere in `hooks/*.py` (one incidental grep hit is the Korean word "skip" inside injected prose, not a mechanism). OMC ships `DISABLE_OMC`/`OMC_SKIP_HOOKS`; oms's only off-switch is uninstalling.
- **Unconditional injection tax — PARTIAL ✅.** `main()` in `scholar_route_emit.py` reads no input and branches on nothing: every turn, paper-related or not, gets the same static CHECKPOINT (measured 4,448 B stdout on `{"prompt":"hello"}`). Safe (no self-echo surface — the payload never reflects prior output) but pure waste on non-paper turns in a mixed-use session.
- **Fail-open discipline — HAS ✅ (C).** Both hooks wrap their core op in try/except → exit 0 with explicit `# fail-open` comments (`scholar_route_emit.py:58-67`, `scholar_verify_emit.py:32-35`). With 2 tiny no-subprocess hooks, OMC's shared runner/timeout cushion is correctly NA.
- **Hook text is regression-locked — HAS, better than OMC ✅.** Tests assert literal substrings of the injected text (`tests/test_scholar_route_emit.py:41` et al.; 20/20 pass re-run this audit). Single implementation per hook — OMC's bridge-vs-mjs drift class structurally cannot occur.

### 1.2 pipeline, loops, gates

- **GATE ladder is prose-only — ABSENT (structure) ✅.** GATE markers at `scholar-pilot/SKILL.md:50,54,56`; `.oms/state/` is mentioned ("stage outputs are recorded", `:33`) but no field/schema is defined anywhere in the 76-line file.
- **`--from` resume is an advertisement — ABSENT ✅.** `SKILL.md:71` names the flag; Steps 0–11 contain no state-reading step. Deeper than the prior gap file put it: there is no state schema *to* read (root cause shared with the GATE finding).
- **3-strike & max-rounds are uncounted — PROMPT-ONLY ✅.** "Same defect recurs 3 times → stop" (`scholar-revise/SKILL.md:32,46`) and "venue max_review_rounds, default 5" (`:33`) both rely on LLM self-counting; no counter artifact exists.
- **Abort/interrupt is unspecified — ABSENT (new this pass).** No step anywhere in scholar-pilot covers "user interrupts mid-stage / stale marker on re-entry" — OMC's cancel is a dependency-ordered, evidence-gated handshake; oms has nothing, not even a doc'd convention.
- **Snapshot token — PARTIAL ✅ (self-aware).** `agents/scholar-verifier.md:51` states verbatim that only the "bind the target snapshot to the PASS" core was adapted. The un-adopted half (a controller-issued per-round id) is the cheap 80% fix (roadmap #10).
- **oms-original guards — HAS ✅.** Consensus handoff proceeds only after mechanically confirming the previous role's `.md` exists on disk (`scholar-outline/SKILL.md:92`); revise separates a structure-regression axis (\ref/\cite/number global consistency) from score regression (`scholar-revise/SKILL.md:35-36`). Neither exists in OMC.
- **Qualitative deepen gate — HAS ✅, exclusion holds.** `scholar-deepen/SKILL.md:17,35` explicitly bans weighted-sum/threshold/stability_ratio; the 4.14.4 exclusion decision stands unchanged.

### 1.3 knowledge lifecycle

- **Heavy channel is a real 5-condition AND-gate — HAS ✅ (C).** `learning-protocol.md:249-267`: evidence_count≥3 ∧ counter_examples==0 ∧ not user_overridden ∧ stability ∧ non-contradiction ("this is an AND, not a score", `:247`). Correction folded: 5 conditions, not the 2 the auditor first named.
- **Light channel is un-scored — PARTIAL ✅.** The "conclusion + evidence together" rule is an explicit *recommendation, not a reject gate* (`references/wiki/README.md:61-69`); a label-only page appends silently at whatever confidence it claims. Same gap omx identified for itself (its proposed `score_page`).
- **Wiki health tooling is not distributed — ABSENT-in-plugin ✅ (C).** A working 5-dimension read-only audit exists — but as `workspace/.oms/workflows/wiki-audit.js` (201 lines; DIMENSIONS at `:128-171`; read-only discipline at `:3,25,114,180`), *outside the plugin*. Every other oms install has zero wiki health-checking. omx ships `lint.py` installed; OMC ships wiki lint tools. Highest-leverage knowledge item (roadmap #23).
- **No usage signal — ABSENT ✅.** Zero `log.md`/frequency/usage-log vocabulary in either wiki README or learning-protocol (grep-clean). OMC logs wiki reads; omx uses query frequency as its promotion signal.
- **Capture-then-curate — PARTIAL.** pilot Step 10 auto-appends inspect/verify discoveries (light channel, `scholar-pilot/SKILL.md:58`); but a session that runs stages *outside* pilot leaves no breadcrumb (no SessionEnd hook; OMC's dumb-capture stub has no analog).
- **No wiki→reference-card promotion verb — ABSENT (new this pass).** The 2026-06 anchoring of an external LLM-writing survey into 5 reference files was hand-done; no skill/step makes it repeatable. Only wiki→venues.md promotion is specified.
- **Anti-pollution ascent — HAS ✅ (C).** scholar-learn refuses to auto-create a parent `.oms/` during elevation (advise-only, `scholar-learn/SKILL.md:56`).
- **Live corpus confirms the pending frontmatter debt ✅.** Only 4 of 16 files in the live global wiki carry confidence/sightings frontmatter; no INDEX.md. The already-decided direction (md + YAML frontmatter + INDEX.md hybrid, design doc 2026-06-02) is folded into the roadmap (#25) rather than re-litigated.

### 1.4 state, paths, packaging

- **Version drift across 4 surfaces — ABSENT (sync) ✅.** plugin.json: *no version field at all*; CHANGELOG top: 0.5.0; git tags: v0.2.0, v0.3.0 only (0.4.0/0.5.0 never tagged); omha `cards/oms.json:6`: "0.1.0". marketplace.json entry: no version field ✅. Correction folded ✅: the omha card's `triggers.skills` list is **current** (all 12 skills, same order) — the drift is version-only, not routing content.
- **Atomic writer unused — PARTIAL ✅ (claim corrected by REFUTATION).** `oms_atomic.py` itself is sound — mkstemp, `os.fsync(f.fileno())` at `:41`, `os.replace` (the audit claim "no fsync" was REFUTED and is dropped). The real defect: its only reference outside tests is prose in `scholar-init/SKILL.md:71`, which then says "for yaml use a plain write" — so the venue config, the writer's own motivating case, is written non-atomically.
- **Schema drift: `consensus/` — ABSENT-from-SSOT ✅.** Written by scholar-outline (`:91`), absent from `output-layout.md` entirely (0 hits; §2 tree, §5 cleanup, §6 checklist all silent). Its cleanup fate is therefore unspecified.
- **No doctor — ABSENT ✅.** Zero `doctor`/self-check anywhere. Direct causal link: the 4-way version drift accumulated over 3 untagged releases precisely because nothing checks surface agreement.
- **Integrity tests cover skills only — PARTIAL ✅ (C).** `test_plugin_integrity.py` (65 lines) enforces plugin.json↔skills/ 1:1 with the originating incident documented; zero references to `agents/`. A typo'd `Task(subagent_type=...)` in any skill would pass CI today.
- **Skill corpus past compaction threshold — 89,236 B ✅.** All 12 SKILL.md load at session start (no shim/skill-bodies split — none exists ✅); OMC compacts at 64 KiB.

### 1.5 research/ideation/review lane

- **Research note contract — HAS, correctly divergent ✅.** Free-prose sections with an explicit `Verified: N | Unverified: M` split (`agents/scholar-researcher.md:60-77`); sciomc's FINDING/EVIDENCE regex grammar would be a second schema on top — correctly not adopted.
- **Parallel-read / single-citation policy — HAS ✅** (`scholar-research/SKILL.md:30`, verbatim).
- **Mock-review is ahead of OMC — HAS+ ✅.** 3 parallel lens reviewers (blind to each other by construction) → area-chair synthesis; weaknesses dropped without anchors (reviewer `Output_Format` + AC step A3); injection sanitize before *and* after reading (`scholar-reviewer.md:83`); rebuttal guide exists (`:116,:173`). Missing vs the field: a rebuttal-and-reconsider *round*, and any venue score-distribution data (`venues.md`/`rubrics/`: none ✅ — one incidental "~top 15%" gloss only).
- **No durable research log — ABSENT.** `.oms/<slug>/` holds pipeline artifacts; nothing records "what we tried/decided this week" across sessions. OMC's ultragoal ledger is the analog; the oms-idiom fit is an append-only log, not a Stop-hook mode.
- **Multi-model exclusion holds, but doesn't cover discussion.** The 4.14.4 exclusion of ccg/adversarial escalation was argued from the formative↔verify boundary *inside the .tex pipeline* (`omc-backport-analysis.md:82`). A standing idea-stage discussion mode generates no `.tex` and needs no second model — the exclusion is not a blocker for roadmap #29.

### 1.6 agents & skills authoring

- **Frontmatter — HAS ✅.** All 6 agents use exactly the 4 live keys + a dead `level:` key (nothing consumes it — grep-clean ✅; OMC carries the same vestige).
- **Model routing — one clear misfit ✅.** drafter/researcher=sonnet, planner/inspector/reviewer/verifier=opus. scholar-verifier self-describes as mechanical PASS/FAIL CI with a Bash/grep/latexmk protocol — OMC's own tier table puts this class at sonnet (roadmap #20).
- **Author-vs-reviewer separation — HAS+, one inherited hole ✅.** Drafter is the only agent without `disallowedTools`; the other 5 all block Write/Edit/NotebookEdit. scholar-verifier legitimately retains Bash (`:12,:42,:87`) — so heredoc writes are prompt-blocked, not tool-blocked; identical posture to OMC's read-only advisors (inherited, not a regression; noted, not roadmapped).
- **Triple self-approval ban — HAS, better than OMC ✅** (`scholar-verifier.md:45-48`: tool block + separate-lane + not-responsible list naming drafting).
- **FRAGILE assumption class — HAS, genuine forward-adaptation ✅** (`scholar-inspector.md:62`: a finding depending on an unverified citation is FRAGILE, human-flagged, never guessed up to VERIFIED).
- **No agent cross-reference tests; no shim layer — ABSENT ✅** (see 1.4).

---

## §2 Prior-work verdicts (claudebase `gaps/oh-my-scholar.md`)

| # | Candidate | Verdict | Delta from this pass |
|:--|:--|:--|:--|
| 1 | PreToolUse citation-write interlock | **CONFIRM, elevate** | Still the top-leverage item; deny-with-feedback JSON shape verified against OMC §19. Now paired with a mechanical DOI/retraction pre-gate (#2) the prior file didn't have. |
| 2 | Scoped Stop-guard for scholar-revise | **CONFIRM, sharpened** | Strikes are prose-only with no counter file — the guard needs roadmap #6/#7's state substrate first. |
| 3 | Verifier per-attempt round-id | **CONFIRM** | Verifier's own prose acknowledges the un-adopted half (`scholar-verifier.md:51`). Pure prompt-contract fix. |
| 4 | Session state envelope + O_EXCL lock | **CONFIRM, downgraded** | Real but moot until state files exist at all (#6) and a multi-session collision is actually observed. Conditional item (#14). |
| 5 | SessionStart resume advisory | **CONFIRM, deepened** | Not just "no reader" — no state schema exists to read. #6 is the prerequisite. |
| 6 | Notepad 3-tier TTL | **CONFIRM** | Sketch stands as written; pure .md convention (#12). |

The gap file's "Knowledge lifecycle — HAS" row is too generous (§1.3): mechanics HAS, health/quality layer ABSENT-in-plugin.

---

## §3 Ecosystem survey

Feature-level, absorption-oriented; primary sources fetched during this audit. Repos/claims marked ✅ were re-fetched by an independent verifier.

### 3.A Evidence base: why the citation invariant is load-bearing (cite these in README/design docs — roadmap #0)

- GPT-4o hallucinates citations **78–90%** of the time on multi-paper synthesis (OpenScholar/ScholarQABench baseline; OpenScholar-8B ≈ human citation accuracy). [arXiv:2411.14199]
- GhostCite (13 LLMs, 40 domains, 375K citations): fabrication **14–95%** by model/domain. [arXiv:2602.06718]
- GPT-4: **18%** entirely fabricated (42-topic study); GPT-4o mental-health domain: **19.9% fabricated + 45.4%** of real ones with bibliographic errors.
- Human review does not catch it: GPTZero found ~**100 confirmed hallucinated citations in accepted NeurIPS 2025 papers** and 50+ under review at ICLR 2026, each missed by 3–5 reviewers.
- Survey: 42% of researchers admit copy-pasting BibTeX unchecked; 77% of reviewers don't thoroughly check references.

### 3.B Direct competitors / neighbors in the Claude ecosystem

- **academic-research-skills** (Imbad0202; ✅ 37,232 stars, v3.15.0 2026-07; **license CC-BY-NC 4.0 — NOT MIT ✅**, so mechanisms may be re-implemented clean-room but no code/text may be copied): citation gate cross-referencing Semantic Scholar+OpenAlex+Crossref+arXiv ✅; `ARS_CLAIM_AUDIT` claim-faithfulness pass ✅ (fetches the cited source and judges whether it supports the *specific claim* — one integrity level above existence-checking); `[MATERIAL GAP]` token instead of silent inference ✅; Devil's-Advocate "Concession Threshold Protocol" against reviewer sycophancy ✅; deliberately MCP-free (skill + direct API), same degrade-first philosophy as oms.
- **Oh My Paper** (LigphiDonk; ✅ 680 stars): 5-stage pipeline, per-agent isolated memory + shared `tasks.json`/`project_truth.md`; no confirmed citation safeguard — oms's integrity story is stronger; its single shared truth-file is a simpler cross-agent state pattern worth remembering.
- **agent-review-panel** (✅): independent-stance-before-cross-view review ordering (write blind, then debate) — oms's parallel lenses already satisfy the "blind" half by construction.
- **MCP swap-point candidates** (all repos verified to exist ✅): Semantic Scholar MCP (xiuyechen / JackKuo666), arxiv-mcp-server (blazickjp), grobid-MCP-Server (JackKuo666), zotero-mcp (54yyyu). All optional accelerators only, behind graceful fallback per oms's degrade-first rule.
- **Anthropic multi-agent research system** (✅ engineering blog): effort-scaling rule (simple = 1 agent/3–10 calls … complex = 10+ subagents) ✅; 4-field subagent task spec (objective / output format / tool guidance / boundaries) ✅; **CitationAgent as a separate final pass after the research loop** ✅ — external confirmation of oms's verify-before-cite ordering; hard caps against runaway fan-out; empirical tool-description validation before trusting an MCP server.

### 3.C Academic AI tools — mechanisms worth absorbing (condensed)

| Tool / work | Mechanism | oms absorption idea |
|:--|:--|:--|
| Scite (1.4B classified citation statements) | supporting / contrasting / mentioning label per citation-in-context | Require a stance tag per confirmed citation — prompt contract, no ML (feeds #3) |
| Crossref + Retraction Watch (merged 2023, daily) | `/works/{doi}` returns metadata + `update-to` retraction records | stdlib pre-gate script before any `.bib` entry (#2) |
| OpenAlex | free fallback graph, `referenced_works`, concept tags | Cross-check when Crossref misses (preprints) (#2) |
| GROBID (~0.87–0.90 F1 refs) | PDF → TEI-XML structured references, Crossref consolidation, BibTeX export | Optional refs/ intake: propose entries, human confirms (#36) |
| Elicit / PaperQA2 / NotebookLM | per-claim, sentence/passage-level citation anchoring | Quote-anchored claim rows in research notes (#5) |
| Undermind | iterative search with statistical stopping rule (marginal-returns) | Explicit termination heuristic for research fan-out (#37) |
| STORM / Co-STORM | perspective discovery from corpus; **Moderator injects questions from retrieved-but-unused info**; shared living mind-map | Gap-tracking + moderator pass (#29, #33) |
| Google AI co-scientist | Reflection critic + Meta-review feeds patterns back into the loop (Elo tournament — deferred, see §6) | Meta-review-of-reviews (#27) |
| AgentReview | 5-phase simulation; rebuttal round; finding: reviewers anchor — rebuttals under-influence | Rebuttal round with locked pre-rebuttal verdicts + delta report (#31) |
| OpenReviewer / CycleReviewer | trained on real reviews; score distributions match human ones; generic "be harsh" prompting is measurably less realistic | Don't train — calibrate: few-shot real reviews + venue score-band table + drift diagnostic (#32, #27) |
| Reviewer2 | enumerate aspects first, then judge each | Aspect-checklist-first lens prompts (#32) |
| Paperpal Preflight | 30+ mechanical checks in fixed categories, color-coded report | Categorized PASS/WARN/FAIL verify report + declarations/captions checks (#34) |
| Jenni "Claim Confidence" | flags unsupported claims & misattributed citations post-draft | Uncited-claim scan (#4) + claim-faithfulness (#3) |
| Sakana AI-Scientist v2 | 5-review ensemble ≈ 69% balanced accuracy vs OpenReview ground truth | Ensemble-variance signal for borderline verdicts (fold into #32); its ICLR episode is the cautionary case for oms's human gates (§6) |
| Connected Papers (mechanism) | co-citation + bibliographic coupling | Pure set-intersection clustering over .bib — zero embeddings (#37) |

---

## §4 Research-companion gap map

The maintainer's vision: oms as **지도교수 (advisor) + 연구 동료 (colleague) + 논문 리뷰어 (reviewer) + 논문 컨설턴트 (consultant)** — the whole research life, not only my-paper writing.

| Role | Has today (evidence) | Missing | Roadmap |
|:--|:--|:--|:--|
| Reviewer | mock-review 3-lens + AC, injection defense, anchor-required weaknesses, rebuttal *guide* | rebuttal *round*; venue score calibration; realism pack | #31, #32 |
| Colleague-discussant | deepen's 3 challenge personas (`scholar-deepen/SKILL.md:59-61`) — consumed as a one-shot gate | a standing, invokable discussion mode; persistence of what was argued | #29 |
| Paper-reader-analyst | scholar-research (but its contract is my-paper-gap-shaped, `scholar-researcher.md:60-77`) | a deep-read stage for an *external* paper; a reading-notes corpus; a PDF intake path | #28, #36 |
| Advisor / consultant | deepen challenges + mock-review rebuttal guide + inspect's severity/evidence critique are fragments | memory-grounded consultation — no research log exists, so every session advises from a blank slate. #30 supplies the *memory* substrate; the *judgment* layer ("is this direction worth 3 months?") is a future `scholar-consult` read-mode over research-log + wiki `decision/` notes, deliberately deferred until #30 has accumulated real data (a consult mode over an empty log is theater). Portfolio view across papers stays out of scope. | #30 (+#29) |

The advisor and consultant roles are merged deliberately: with only a log as substrate they differ in ambition, not deliverable — claiming them separately would overstate what this roadmap ships (critic-panel finding, folded).

Guard that makes the expansion citation-safe: **reading notes are never auto-citable** — `.oms/reading/*.md` is secondary memo like the wiki; the verified-citation path (scholar-research → human-confirmed `.bib`) stays the only door into the bibliography.

---

## §5 Consolidated adoption roadmap

Ordered within phases; provenance in parentheses. All items respect the three invariants (single-careful generation; no citation auto-fix, no embeddings in oms's own recall; stdlib-Python + .md-degrade-first, human GATEs). External APIs (Crossref/S2) are deterministic lookups, not embeddings-in-recall.

### P0 — Citation-integrity enforcement (the reason oms exists)

| # | Item | Leverage · idiom sketch |
|:--|:--|:--|
| 0 | **Cite the hallucination evidence in oms docs** (ecosystem 3.A) | Zero mechanism, pure documentation: put the 78–90% / 14–95% / NeurIPS-2025 numbers with URLs into README §citation-safety as the measured "why". |
| 1 | **PreToolUse citation-write interlock** (prior #1; OMC §19) | `hooks/scholar_cite_guard.py` on `Edit\|Write\|MultiEdit`: new `@type{key,` into `.bib` → deny-with-feedback (`permissionDecision:"deny"` + reason "confirm the source first — no fabricated citations"); `\cite{K}` with K absent from sibling `.bib` → deny "verify the key exists". Parse failure → exit 0 fail-open. Never auto-fixes — it stops, it never invents. |
| 2 | **Mechanical DOI/retraction pre-gate** (Crossref+RW, OpenAlex fallback) | stdlib `scripts/verify_bib_entry.py`: resolve DOI/title → fuzzy-match title+author → check `update-to` for retraction → emit verdict list for the human gate. Called by scholar-verify and by the interlock's feedback message. |
| 3 | **Claim-faithfulness sub-check in scholar-verify** (ARS/Scite/Jenni; clean-room — ARS is CC-BY-NC) | New defect class `citation-misuse`: for each claim+\cite pair, re-read the verified quote (from #5's anchors) and label supports/contrasts/mentions; mismatch → human-flag list, never auto-fix. "Citation exists" ≠ "citation supports this claim". |
| 4 | **Uncited-claim scan + `[MATERIAL GAP]` token** (Jenni; ARS) | verify WARN for claim-sentences with no adjacent \cite; drafter contract: emit `[MATERIAL GAP: …]` instead of inferring when grounding is absent — greppable, auditable. |
| 5 | **Per-claim quote anchoring in research notes** (Elicit/PaperQA2 pattern) | Researcher output contract: every claim row carries a verbatim source quote + locator. Feeds #3 mechanically; prompt-contract only. |

### P1 — Pipeline state & loop robustness (make the advertised guarantees real)

| # | Item | Leverage · idiom sketch |
|:--|:--|:--|
| 6 | **Define the `.oms/state/` schema** (root cause of P1/P2/GATE findings) | `pilot-<slug>.json` `{stage, gate_status: pending\|approved\|revise\|abort, open_fail_ids[], updated_at}` written via oms_atomic at every stage boundary; documented in output-layout.md. Prerequisite for #7–#11, #13. |
| 7 | **Strike ledger for revise** | `revise-<slug>.json` `{defect_id: count}` appended per round — 3-strike and max_review_rounds become countable by grep, not self-report. |
| 8 | **Scoped Stop-guard for scholar-revise** (prior #2) | Stop hook active only while the revise marker is live; exemptions: strikes≥3, GATE2, human abort, TTL, citation-content defects (never loop those). |
| 9 | **SessionStart resume advisory** (prior #5) | Reads #6; injects `<oms-resume>` naming last stage/GATE/open FAILs; advisory only — GATEs stay human. |
| 10 | **Verifier round_id** (prior #3) | revise mints a uuid per round into the verifier Task prompt; verifier echoes it in the verdict; mismatch → reject. Prompt contract, no code. |
| 11 | **Abort/interrupt spec in scholar-pilot** (new) | One SKILL.md section: on entry, if a non-terminal marker exists, surface it ("resume from X / discard?"); `gate_status: abort` semantics; stale-marker rule. |
| 12 | **Notepad 3-tier convention** (prior #6) | `## Priority Context` replace-on-write / `## Working Notes` dated append, prune >7d at pilot entry / `## Manual` never pruned. Pure .md. |
| 13 | **PreCompact Priority-Context re-injection** (critic-panel finding; OMC §04) | stdlib fail-open PreCompact hook re-injecting `## Priority Context` (citation principles + current GATE + open unverified-citation list) from `.oms/notepad.md`. The *active* counterpart of pilot's passive notepad write (`scholar-pilot/SKILL.md:34`): #9 covers new sessions, this covers in-session compaction — exactly when a multi-day citation-bound pipeline drops its constraints. Pairs with #12. |
| 14 | *(conditional)* **Session envelope + lock** (prior #4) | Only if #6's files ever show cross-session collisions in practice; `_meta{session_id, owner_pid}` + O_EXCL marker then. |

### P2 — Packaging & authoring hygiene

| # | Item | Leverage · idiom sketch |
|:--|:--|:--|
| 15 | **Version SSOT + sync** | Add `version` to plugin.json (anchor); `scripts/sync_version.py` checks CHANGELOG top + latest git tag + omha card and fails on drift; add `test_version_sync.py`; tag v0.5.x retroactively at release time. |
| 16 | **Wire the atomic writer** | Venue config → JSON (or add `atomic_write_text`) so `oms_atomic` protects its own motivating case. Writer needs no fixes (fsync verified present). |
| 17 | **output-layout.md: add `consensus/`** | New "per-run handoff artifacts" category + explicit cleanup fate in §5/§6. |
| 18 | **`oms doctor`** | Read-only stdlib check: version surfaces agree, hooks registered, agents parse, orphan `.oms/<slug>` scan. Would have caught the 4-way drift at commit time. |
| 19 | **Agent cross-reference integrity tests** | (a) every `agents/*.md` has the 4 live keys; (b) every `Task(subagent_type="oh-my-scholar:X")` across skills resolves to `agents/X.md`. Closes the silent-typo class. |
| 20 | **scholar-verifier opus→sonnet** | One-line frontmatter change; the agent self-describes as mechanical CI; matches OMC's verifier tier and the session's model-routing economics. |
| 21 | **Skill shim/compaction layer** | 89,236 B always-loaded > OMC's 64 KiB budget: adopt the shim + `skill-bodies/` split (OMC §16 names this exact sibling adaptation); add a byte-budget regression test. |
| 22 | **`DISABLE_OMS` kill switch + route-hook relevance gate** | 2 lines per hook for the env switch; a cheap keyword gate before injecting the 4.4 KB CHECKPOINT on clearly non-paper prompts (keep the STAGE contract text unchanged). |

### P3 — Knowledge lifecycle

| # | Item | Leverage · idiom sketch |
|:--|:--|:--|
| 23 | **Distribute the wiki audit** | Port the workspace `wiki-audit.js` 5 dimensions into the plugin (stdlib `scripts/oms_wiki_audit.py` + a reference-card procedure): dangling refs, duplicate section numbers, SSOT-delegation integrity, strength-tag evidence, empty/orphan. Detection-only, repair separate — the calibration lesson (audit the *criteria*, not just the corpus, when a dimension diverges) goes in the card. |
| 24 | **Light-channel quality signal** | At wiki append: no pointer/quote → force `confidence: low` + note. Non-blocking; makes README's recommendation mechanical without a reject gate. |
| 25 | **Frontmatter standardization + INDEX.md** (pending item ⑥) | Direction already decided (md + YAML frontmatter + INDEX.md); execute across the live corpus, spec in wiki/README, INDEX regenerated by #23's script. |
| 26 | **wiki→reference-card anchoring verb** | scholar-learn sub-step: promote a mature wiki cluster into a `references/` card with source anchors — the 2026-06 hand-done survey-anchoring, made repeatable (human-gated; citations still excluded). |
| 27 | **Mock-review history + meta-review-of-reviews** (co-scientist Meta-review; CycleReviewer diagnostic) | Append each mock-review verdict to `.oms/<slug>/reviews-log.md`; periodically mine for recurring weakness types → propose lens-prompt tweaks (human-approved); flag "always-moderate" score drift. |

### P4 — Research-companion expansion

| # | Item | Leverage · idiom sketch |
|:--|:--|:--|
| 28 | **`scholar-read` — external-paper deep-read stage** | New skill; reuse scholar-researcher via `mode=deep-read` (the mode-branch idiom mock-review already proved): input = one paper/PDF, output = `.oms/reading/<citekey>.md` structured note (claims / method / evidence / limitations / relation-to-my-work), metadata citation-verified. Hard guard: reading notes are NOT citable — `.bib` entry only via scholar-research verification. PDF path via #36 when available, else text. |
| 29 | **`scholar-discuss` — standing Socratic discussion mode** | New skill; re-exposes deepen's Contrarian/Simplifier/Ontologist as an on-demand debate partner (no `.tex`, so the 4.14.4 multi-model exclusion doesn't apply); adds the Co-STORM moderator move — track retrieved-but-unused evidence in a gap list and inject the highest-information-gain unasked question; session output appends to wiki `decision/` (light channel) and the living outline. |
| 30 | **Research log** | `.oms/<slug>/research-log.md`: dated append per session — tried/decided/dropped + why. Ultragoal's durable-ledger value without any Stop-hook; the substrate that lets advisor/consultant modes remember the project (a future `scholar-consult` judgment layer reads this once it has data — §4). Wire as a pilot/discuss/read exit step. |
| 31 | **Rebuttal round in mock-review** (AgentReview) | `--with-rebuttal`: lock each lens's pre-rebuttal verdict, author drafts responses, lenses re-score with the rebuttal in view, AC reports the delta — anchoring-aware by design (AgentReview: rebuttals under-influence real reviewers; the delta tells you fixable vs fundamental). |
| 32 | **Reviewer realism pack** | Aspect-checklist-first lens prompts (Reviewer2); few-shot real review examples per venue in the wiki (OpenReviewer lesson: personas alone are measurably too soft); a score-band table in venues.md cited from public venue stats (CycleReviewer lesson — calibrate, never train); concession-threshold rule for the AC (ARS pattern, clean-room); optionally N-sample ensemble variance on borderline verdicts (Sakana). |
| 33 | **Moderator pass before GATE1** (Co-STORM) | After the planner proposes the outline, one read-only pass scans research notes for retrieved-but-unused evidence and asks 1–2 pointed questions at the human gate — anti-groupthink between researcher and planner. |
| 34 | **Preflight-style categorized verify report** (Paperpal) | verify output as fixed category rows (language / citations / formatting-metadata / tables-figures / declarations) each PASS/WARN/FAIL + a blind-review anonymization check before submission venues that require it. |

### P5 — Optional ecosystem accelerators (MCP swap-points; degrade-first, never required)

| # | Item | Leverage · idiom sketch |
|:--|:--|:--|
| 35 | **Name MCP swap-points** | In wiki/README's abstract-function list: `citation_lookup()` → Semantic Scholar MCP or arxiv MCP when present, else WebSearch/WebFetch; Zotero MCP as an opt-in citation *source* for users with existing libraries (same human gate). Validate tool descriptions empirically before trusting (Anthropic lesson). |
| 36 | **GROBID intake (self-hosted, optional)** | refs/ PDF → proposed BibTeX (Crossref-consolidated); human confirms every entry — GROBID proposes, never commits (documented F1 ≈ 0.9, known failure modes). Supports #28. |
| 37 | **Deep-research mechanics in scholar-research** | 4-field delegation template for researcher dispatch; fan-out sizing rule + hard caps; interleaved after-each-source gap-check; explicit stopping heuristic (marginal returns); bibliographic-coupling clustering script (pure set ops over .bib — zero embeddings). |

Sequencing note: #6 unblocks #7–#11 and #13; #5 feeds #3; #23 precedes #25 (the audit regenerates the INDEX); #28 gains from #36 but doesn't require it. Everything else is independent.

---

## §6 Deliberately not adopting (or deferring)

- **Blunt "never stop" Stop-hook loop** — 4.14.4 exclusion stands (freeze/citation risk); only the scoped, marker-gated, exemption-laden variant (#8) is in scope.
- **Parallel generation / team worker bus** (OMC §07) — violates invariant #1. Read-only fan-out (mock-review lenses) remains the only parallelism.
- **Embeddings anywhere in oms's own recall** — permanent. External services' server-side embeddings (S2 search, TLDR) are consumed as API *results*, which is fine; nothing embedding-shaped enters oms's storage or retrieval.
- **Elo framing tournament for ideate** (co-scientist Ranking) — deferred as YAGNI (critic-panel finding): a single-author paper rarely carries ≥3 genuinely competing framings, and deepen's challenge rounds already stress-test the chosen one. Revisit only when a real multi-framing paper demands it (hard precondition: the human explicitly flags competing framings).
- **Fine-tuned reviewer models** (OpenReviewer/CycleReviewer as artifacts) — absorb their *calibration lessons* (#32), never a model dependency.
- **Full pipeline autonomy** (AI-Scientist / Agent Laboratory / AI-Researcher) — review/verification mechanics only. The ICLR 2025 episode is the standing cautionary case for oms's human gates: Sakana ran *with* organizer disclosure, reviewer consent, and a pre-agreed withdrawal (and still admitted citation-misattribution errors), while other labs' undisclosed AI submissions drew public criticism for exploiting reviewer labor — even the best-behaved autonomous pipeline treated "passed review" as insufficient grounds to publish.
- **ccg / multi-model CLI interop** — exclusion holds; scholar-discuss (#29) uses in-harness personas, not a second provider.
- **sciomc FINDING/EVIDENCE regex tag grammar** — oms's verified/unverified contract already separates verification state; a tag grammar would be a second schema (double bookkeeping).
- **Ambiguity quantification** in deepen — stays qualitative (re-verified `scholar-deepen/SKILL.md:17,35`).
- **Node MCP bridge / committed bundle; installer/HUD/notifications** — identity-level exclusions, unchanged.
- **omp content-conventions regex engine** — the 2026-05-31 reverse-review (0 adopted) stands; nothing in this pass disturbs it.
- **NotebookLM-style audio/podcast artifacts** — out of scope for a citation-bound harness; no absorption.

---

## §7 oms-better-than-OMC ledger (worth defending upstream)

1. **Mock-review as a hardened judge panel**: injection sanitize before/after reading, anchor-or-drop weaknesses, venue-native verdicts — ahead of OMC's judge patterns; a reverse-backport candidate for OMC.
2. **Triple self-approval ban** stated from both sides of the author/reviewer boundary (`scholar-verifier.md:45-48`) vs OMC's one-sided reviewer-only assertion.
3. **Snapshot-correlation token inside the agent contract** (`scholar-verifier.md:38,51`) — OMC keeps this only in the ralph mode wrapper.
4. **Consensus handoff file-existence gate** (`scholar-outline/SKILL.md:92`) — mechanical sequencing guard ralplan lacks.
5. **Structure-regression axis** in revise (`scholar-revise/SKILL.md:35-36`) — a dual-axis regression concept ralph doesn't have.
6. **FRAGILE assumption class tied to citation risk** (`scholar-inspector.md:62`) — domain forward-adaptation of the critic techniques.
7. **Two-channel learning with consequence-scaled friction**, 5-condition AND-gate, `user_stated` fast-path that skips the repetition bar but never the human gate, and schema-level exclusion of citations from promotion.
8. **Test-locked hook text** (literal-substring assertions, single implementation per hook) — the bridge-vs-script drift class OMC documents in itself cannot occur.
9. **Single-file layout SSOT** (`output-layout.md`) — auditable end-to-end; the one drift it had (consensus/) was caught by exactly the grep the design enables.

---

## §8 Cross-harness ticket (out of oms scope)

A stray **`.omc/state/last-tool-error.json` exists inside the oms global wiki** (`workspace/.oms/wiki/.omc/state/`, dated 2026-06-02): an OMC hook resolved its state root to the wiki directory (cwd-ascent misfire — the same class the claudebase marker-ascent patch targets). Action for a claudebase session: delete the stray dir, confirm the patch covers cwd=`.oms/wiki/` invocations.

---

## §9 Method & verification notes

- Cluster auditors and ecosystem researchers ran as parallel sonnet agents; their reports were then attacked by 7 independent verifiers (one per source) instructed to re-derive every cited `file:line`/URL. 34 claims: 27 CONFIRMED, 6 CORRECTED (all corrections folded into §1–§3: 5-condition AND-gate; wiki-audit line anchors; scholar-learn elevation context; hook line ranges; grep nuance on the kill-switch claim; academic-research-skills license CC-BY-NC), 1 REFUTED and dropped (the "no fsync in oms_atomic" claim — `os.fsync` exists at `oms_atomic.py:41`; only the zero-call-site finding survives).
- A 2-lens critic panel (consistency: sonnet; judgment: opus) then reviewed this document against the repos and reference bundle. Both lenses returned **approve**; 5 findings folded: PreCompact re-injection added as #13 (medium — the one real coverage gap); the Elo ideate tournament cut to a §6 deferral (YAGNI); advisor/consultant rows merged in §4 with the missing judgment-layer named honestly; Zotero folded into #35; a 66→65 line-count fix in §1.4.
- Lead spot-verifications included: plugin.json version-field absence, tag list, omha card version, atomic-writer call sites, consensus/ grep, 89,236 B corpus size, verifier frontmatter, drafter-only-writer check, contamination file, and a live hook probe (`{"prompt":"hello"}` → rc 0, 4,448 B injected).
- Ecosystem claims carry URLs fetched during the audit; the five highest-leverage repo/blog claims were independently re-fetched (✅ marks). One licensing correction matters operationally: **academic-research-skills is CC-BY-NC 4.0** — its mechanisms are re-implemented clean-room in this roadmap, never copied.
- This plan document is analysis and roadmap only; no oms code was modified in its production.
