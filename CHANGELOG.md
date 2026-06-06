# Changelog

All notable changes to oh-my-scholar (oms).

## [Unreleased]

### Fixed
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

### Added
- **Regression tests** `tests/test_ssot_priority_and_sync.py` (7 cases) — drift guard for the Defect A·B mechanisms
  (learning-protocol §8 existence·reading order, inspect SSOT-first, draft·revise sync completion conditions,
  output-layout checklist). 96 → 103 passed.

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
  (occurred in the real ASV-ROV dissertation). Now, at any scale, it mandates "experiments stay inside the unit where the method
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
