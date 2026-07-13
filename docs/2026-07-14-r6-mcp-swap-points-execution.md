# R6 Execution Plan — Optional Ecosystem Accelerators (P5 #35–#37)

| Field | Value |
|:--|:--|
| Round | R6 → release v0.11.0 |
| Branch / worktree | `feat/r6-mcp-swap-points` @ `.claude/worktrees/oms-r6`, base = `feat/r5-research-companion` (**stacked PR** — R5 merges first; after R5's squash-merge, this branch needs the known `git merge -X ours origin/main` merge-back before its own merge) |
| Source roadmap | `docs/2026-07-11-oms-advancement-plan.md` §P5 (#35–#37) — "degrade-first, never required" |
| Method | Same SDD as R5 (fresh sonnet implementer + spec/quality review per task); final opus review before PR |
| Suite baseline | 518 passed on the R5 branch; every task keeps the suite green |

## Binding invariants (same as R5; violations BLOCKING)

R5 plan's invariants 1–7 apply verbatim (single careful generation / no citation auto-fix / no embeddings / degrade-first / human gates / packaging gates / detection-only). P5-specific sharpenings:

- **P5-A — Optional means optional.** No MCP server, GROBID instance, or external tool becomes a prerequisite for ANY stage. Every accelerator sits behind a named graceful fallback; its absence changes speed, never capability class. No new hook, no new runtime dependency, no plugin.json change other than version.
- **P5-B — The citation door does not widen.** Zotero/GROBID/MCPs are citation *proposal sources* only; every proposed entry still passes the same human gate + `verify_bib_entry.py` mechanical check + cite-guard as today. Nothing lands in `.bib` automatically.
- **P5-C — Recall stays deterministic.** External services may use embeddings server-side; their *results* are consumed as API results (roadmap §6 rule). Nothing embedding-shaped enters oms storage, retrieval, or the new clustering script.

## Design decisions locked by this plan

- **E1 — `citation_lookup()` is documented where `wiki_query()` is** (`references/wiki/README.md`), as the second entry of the abstract-function contract idiom: signature, deterministic-contract, today's implementation target described **precisely, not as one chain** (`scripts/verify_bib_entry.py`: DOI path = Crossref, then OpenAlex **only on HTTPError** — a URLError short-circuits to `NETWORK_ERROR` without trying OpenAlex; title-only path = Crossref bibliographic search **only**; WebSearch/WebFetch is a **separate agent-level manual fallback** invoked at the caller's discretion, never code-chained off exit codes), and the MCP swap-points (Semantic Scholar MCP, arXiv MCP; Zotero MCP as an opt-in citation *source* for users with existing libraries — same human gate). Includes the Anthropic lesson verbatim in substance: **validate an MCP server's tool descriptions empirically before trusting it** (dispatch one cheap probe call and compare observed behavior against the description before relying on it in a research pass).
- **E2 — GROBID gets a standalone reference card** `references/grobid-intake.md` (same genre as `references/wiki/audit.md`): what it is (self-hosted, optional), the intake flow (`refs/*.pdf` → TEI → proposed BibTeX, Crossref-consolidated), the hard rule **GROBID proposes, never commits** — every proposed entry is human-confirmed and then verified via `verify_bib_entry.py` before any `.bib` write (cite-guard still fires on the write), documented accuracy ceiling (F1 ≈ 0.87–0.90 on reference extraction — cite the figure as reported, do not overstate) and known failure modes **hedged as "commonly reported — verify against GROBID's own documentation", never asserted as settled fact** (an anti-fabrication plugin does not fabricate failure-mode claims), and the degrade path (no GROBID → today's manual + verify_bib_entry path, unchanged).
- **E3 — Bibliographic coupling is honest set math over reference LISTS, not `.bib` metadata.** A `.bib` entry does not carry the paper's own bibliography, so the script's input contract is: **each input `.bib` file = one paper's reference list** (exported from a publisher/Zotero/OpenAlex `referenced_works` dump). `scripts/bib_coupling.py` (stdlib only, zero network, zero embeddings): entry-key extraction re-derives the pattern of `hooks/scholar_cite_guard.py:25` `ENTRY_RE` (**read-only reuse — copy the pattern, never edit hooks/**, E5 freeze intact); title normalization reuses `verify_bib_entry.py`'s `_norm()` idiom; **per-entry DOI/title FIELD extraction from a raw `.bib` block is new parsing work — no existing idiom to copy wholesale** (do not import network code); identity key = lowercased DOI when present else normalized title (lowercase, strip TeX braces/accents/punctuation/whitespace); pairwise coupling strength = |refs(A) ∩ refs(B)|; clusters = connected components over pairs with strength ≥ threshold (`--min-shared`, default 2); output = human-readable cluster report to stdout (and `--json` for machine use). Exit 0 on success, 2 on usage error. Read-only.
- **E4 — Fan-out never touches citation generation.** #37's parallel fan-out applies to *reading* dispatches only, whose outputs are digests WITHOUT citation entries; the citation-bearing research note remains ONE careful researcher pass (existing invariant restated mechanically in the skill body).
- **E5 — Frozen surfaces.** No edits to hooks/, `scripts/oms_state.py`, `skill-bodies/scholar-deepen/SKILL.md`, GATE semantics, step-number headings (R5 D10 discipline), shim frontmatter (except none needed — no new skills in R6).

---

## Task list (sequential)

### U1 — #35 MCP swap-point naming (`citation_lookup()` contract)

- **`references/wiki/README.md`**: add a `citation_lookup()` abstract-function contract section adjacent to the existing `wiki_query(category)` contract (per E1): signature sketch `citation_lookup(doi_or_title) → verdict + normalized metadata`, deterministic-lookup rule (P5-C), today's impl target, swap-points table (Semantic Scholar MCP / arXiv MCP / Zotero MCP with the opt-in-source framing + human gate), the empirical tool-description validation rule, and the graceful fallback chain ending at WebSearch/WebFetch. Explicit sentence: absence of every MCP changes nothing about correctness guarantees.
- **`skill-bodies/scholar-research/SKILL.md`**: ONE pointer line in Execution_Policy naming `citation_lookup()`'s contract location (no behavior change).
- **Tests**: extend the wiki-spec doc test file (`tests/test_wiki_spec_docs.py`) with phrase locks: `citation_lookup(`, swap-point names, "human gate" adjacency for Zotero, empirical-validation rule, fallback chain; scholar-research pointer lock goes in `tests/test_researcher_quote_anchor.py` (the ONLY existing test file asserting scholar-research body content — its locks are loose `re.search` substrings, not exact phrases; `tests/test_scholar_research_skill.py` does NOT exist).
- **Acceptance**: suite green; `git grep citation_lookup -- 'references/**' 'skill-bodies/**' 'skills/**' 'agents/**' 'scripts/**' 'tests/**'` hits wiki README + scholar-research body + tests only (docs/ excluded — the roadmap and this plan legitimately mention it).

### U2 — #36 GROBID intake card

- **New `references/grobid-intake.md`** per E2. Structure: §1 what/when (optional accelerator, self-hosted, supports scholar-read PDF intake and refs/ batch intake), §2 flow (PDF → TEI → proposed entries → **human confirms every entry** → `verify_bib_entry.py` → only then `.bib`), §3 accuracy & failure modes (reported F1 range, cited as external report; two-column/non-English/DOI-mangling caveats), §4 degrade path (absence = today's path, unchanged), §5 boundary box: **proposes, never commits; cite-guard unaffected; not a citation authority**.
- **Wiring (one line each, no behavior change)**: `skill-bodies/scholar-read/SKILL.md` — replace/point its future-accelerator mention at the card; `skill-bodies/scholar-research/SKILL.md` — optional-intake pointer line.
- **Tests**: new `tests/test_grobid_card.py` (or extension of the existing reference-card doc-test convention): phrase locks for "proposes, never commits", human-confirm-every-entry, degrade path, and both skill-body pointer lines.
- **Acceptance**: suite green; card is documentation-only (no script, no hook, no plugin.json surface).

### U3 — #37 deep-research mechanics in scholar-research (+ coupling script)

- **`skill-bodies/scholar-research/SKILL.md`** — Steps section reworked WITHOUT rewording the existing locked lines (the ONLY test locking this body is `tests/test_researcher_quote_anchor.py::test_skill_mentions_anchoring_and_faithfulness_feed`, loose `re.search(r'quote')`/`(r'faithfulness')` over the whole body; the load-bearing sentence "parallel citation generation is prohibited" lives in Execution_Policy `:30`, which the Steps rework must not touch — add a phrase-lock test for it since U1/U2 also edit that region):
  - **4-field delegation template** (Anthropic pattern, named): every researcher dispatch carries `objective / output format / tool guidance / boundaries` — restructure Step 2's Input/Instructions bullet into this template.
  - **Fan-out sizing rule + hard cap** (E4, mechanism named per adversarial review): reading breadth scales with topic breadth, and the parallel reads happen **INSIDE the single `mode=gap-research` pass** — the agent contract already sanctions this ("Investigation reads can be parallel; synthesis is single and careful", `agents/scholar-researcher.md:40,69`). Narrow topic → few sources; broad multi-family survey → up to **3 concurrent read batches** in-pass (3 anchored to the house precedent of mock-review's 3-lens dispatch — a deliberate conservative cap). **NEVER separate citation-generating dispatches**: the single synthesis inside that one pass remains the only citation generator. Acceptance sub-check: the fan-out text cannot be read as authorizing parallel `Task(mode=gap-research)` dispatches.
  - **Interleaved gap-check**: after each source batch, re-derive the gap list before continuing (one bullet).
  - **Stopping heuristic** (marginal returns, Undermind lesson named qualitatively): stop expanding when 2 consecutive batches add no new method family AND no new gap — never "until exhausted".
  - **Clustering step (optional)**: when per-paper reference lists are available, run `scripts/bib_coupling.py` and use its clusters as candidate method families (mechanical seed for the landscape map — advisory, the researcher's judgment prevails).
- **New `scripts/bib_coupling.py`** per E3 (parsing pointers: `ENTRY_RE` pattern re-derived read-only from `scholar_cite_guard.py:25`; `_norm()` idiom from `verify_bib_entry.py:36`; DOI/title field extraction = new work) + **`tests/test_bib_coupling.py`** (import via the `importlib` idiom of `tests/test_oms_wiki_audit.py`): fixture `.bib` reference-lists (tmp files) covering: DOI-keyed intersection, title-fallback normalization (braces/case/punct), threshold behavior (`--min-shared`), connected-component merging (A–B, B–C ⇒ one cluster), singleton isolation, `--json` shape, usage-error exit 2, and a zero-network guarantee lock (no `urllib`/`socket` import — test greps the source).
- **Acceptance**: suite green; script runs standalone (`python3 scripts/bib_coupling.py --help` exits 0); skill body's existing locked phrases intact.

### U4 — Release prep with DEFERRED version bump (revised after SDD blocker — the regression locks are the authority)

**Why revised**: the original U4 sanctioned a tag-surface DRIFT, but two pre-existing live-repo locks (`tests/test_version_sync.py::test_live_repo_surfaces_agree`, `tests/test_oms_doctor.py::test_live_repo_is_healthy`) correctly hard-fail on a 2-deep untagged release stack — the 1-deep pre-tag window is deliberate tagging-discipline pressure, and weakening those locks (or the checker) to accommodate a stacked branch would gut the alarm. Therefore the bump is deferred, not the locks.

- **plugin.json stays `0.10.0` in this PR** — no version bump while v0.10.0 is untagged.
- **CHANGELOG**: R6 items land under the existing `## [Unreleased]` section (Added per item with `(file, test)` provenance; Notes: stacked-on-R5 merge order + merge-back procedure, the deferred-bump step below, omha card 0.11.0 follow-up, P5 closes the 2026-07-11 roadmap — §6 deferrals stay deferred). If any existing lock forbids a non-empty `[Unreleased]`, STOP and report — do not improvise.
- README: mention `citation_lookup()` swap-point contract + `bib_coupling.py` in the appropriate existing sections (no new top-level section unless the README idiom demands it); Status test count updated to measured value.
- **Acceptance**: full suite green (all live-repo locks pass unmodified); `sync_version.py` state IDENTICAL to the R5 branch — plugin.json/CHANGELOG/tag PASS, omha card-only DRIFT, exit 1; `oms_doctor.py` same as R5 (card WARN only).
- **Post-merge bump procedure (user, documented in the PR body)**: after R5 squash-merge + `v0.10.0` tag + R6 merge-back (`git merge -X ours origin/main`): one mechanical commit — plugin.json → `0.11.0`, retitle `## [Unreleased]` → `## [0.11.0] — <date>` (fresh empty `[Unreleased]` above) — then merge R6 and tag `v0.11.0`.

---

## Sequencing & risk notes

- U1 → U2 → U3 → U4. U1/U2 both touch scholar-research body (one pointer line each) — sequential order makes the second edit trivial; U3 does the structural rework last so pointer lines are already in place.
- **Stacked-PR discipline**: PR base = `feat/r5-research-companion`; PR body must state the merge order and the post-squash merge-back step (R2-on-R1 precedent).
- Out of scope: actually installing/configuring any MCP server or GROBID (docs only); Elo tournament and every §6 deferral; any change to verify_bib_entry.py behavior.
