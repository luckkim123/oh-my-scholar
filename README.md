# oh-my-scholar (oms)

> Multi-agent orchestration harness for **academic paper writing** — treats writing a paper like writing code, with citation-integrity guardrails.

Lineage: [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) (omc) → `oh-my-docs` (omd) → **`oh-my-scholar` (oms)**

## Installation

**Prerequisites**: a Claude Code build with plugin support (the `/plugin` command family), and `python3` on `PATH` — every hook and script is Python-stdlib-only, no `pip install` needed.

oms is distributed through [`oh-my-heroacademia`](https://github.com/luckkim123/oh-my-heroacademia)'s marketplace (this repo has no `.claude-plugin/marketplace.json` of its own):

```
/plugin marketplace add luckkim123/oh-my-heroacademia
/plugin install oh-my-scholar@heroacademia
```

To confirm it loaded, say something like "start a paper" to trigger `scholar-init` — it scaffolds a folder·venue·topic workspace and is safe to run standalone.

## Philosophy — a paper ≈ code

| Code | Paper |
|:---|:---|
| spec / requirements | research question, contribution definition |
| architecture design | outline, story arc |
| per-function design | concept notes (.md) |
| function implementation | section draft (.tex) |
| code review (formative) | peer critique |
| CI gate (pass/fail) | citation / numbers / compile checks |
| ralph (loop until tests pass) | revise loop |

It bridges two layers: **`.md` (concept SSOT) → `.tex` (paper)**.

## Stage skeleton

```
[Stage 0 — bootstrap]
  scholar-init       folder·venue·topic → directory scaffold + .oms/ workspace  (research /init)
       ━━━ GATE 0: scaffold approval (idempotent — skip if .oms/<slug>/ already exists) ━━━
[.md layer — concept SSOT]
  scholar-research   RQ·related work·gap          (requirements gathering)
  scholar-deepen     claim-ambiguity gate (qualitative)   (spec clarification)
  scholar-ideate     methodology/*.md concepts     (design)
  scholar-outline    section structure·story arc        (architecture)
       ━━━ GATE 1: outline approval ━━━
[.tex layer — paper]
  scholar-draft       .tex generation (single, careful)        (function implementation)
  scholar-inspect     formative critique·coaching          (code review)
  scholar-mock-review judges from the venue reviewer's stance      (mock review committee)
                      score + venue-native verdict
                      (conference accept/reject·letter / journal revision)
  scholar-verify      automated gate (cite·numbers·compile)  (CI)
       ━━━ GATE 2: review confirmation ━━━
  scholar-revise     loop until verify passes       (ralph)
       ━━━ GATE 3: submission confirmation ━━━
  scholar-pilot      full orchestration        (autopilot)
[on-demand — no fixed stage, usable any time]
  scholar-read       external paper → structured reading note (.oms/reading/, never a citation source)
  scholar-discuss    standing Socratic discussion partner (Contrarian·Simplifier·Ontologist; no .tex/.bib)
[meta — evolution]
  scholar-learn      observation → promote venue defaults (human gate) — more specialized to this user the more you use it
```

## The 3 citation-safety principles (oms identity)

A paper is citation-bound, so hallucinations are not caught as compile errors. Therefore:

1. **Reading is parallel, generation is single** — reviewer/inspector/verifier may run in parallel (read-only). draft (.tex generation) is never parallel.
2. **No auto-fixing** — even when the verifier detects a missing citation it does not fix it automatically. Get human confirmation before editing the .bib.
3. **Lock concepts (.md) first** — solidify sources and logic in ideate (.md) before draft (.tex).

**Why this is load-bearing (measured, 2026 audit — see `docs/2026-07-11-oms-advancement-plan.md` §3.A):**
- GPT-4o fabricates citations **78–90%** of the time on multi-paper synthesis ([OpenScholar benchmark, arXiv:2411.14199](https://arxiv.org/abs/2411.14199)).
- Across 13 models / 40 domains / 375K citations, fabrication runs **14–95%** by model and domain ([GhostCite, arXiv:2602.06718](https://arxiv.org/abs/2602.06718)).
- Human review does not catch it: ~**100 confirmed hallucinated citations in accepted NeurIPS 2025 papers** (GPTZero), each missed by 3–5 reviewers; 77% of reviewers admit not checking references thoroughly.

Since v0.6.0 principle 2 is **enforced, not just stated**: a PreToolUse interlock (`hooks/scholar_cite_guard.py`) denies unverified new `.bib` entries and dangling `\cite` keys before they land, and `scripts/verify_bib_entry.py` verifies DOI existence + retraction status via publisher-registered retraction notices in Crossref `update-to` relations, plus OpenAlex's `is_retracted` flag, recording human-gated VERIFIED keys into the `.oms/state/verified-citations.json` allowlist.

## Agents

| agent | model | permissions | role |
|:---|:---|:---|:---|
| scholar-researcher | sonnet | read-only | related work·gap survey (`mode=gap-research`, default) · external-paper deep-read (`mode=deep-read`) |
| scholar-planner | opus | read-only | outline·story arc |
| scholar-inspector | opus | read-only | formative critique (logic/prose) — coach (`mode=draft-critique`, default) · pre-GATE1 anti-groupthink moderator scan (`mode=moderator`, no verdict) |
| scholar-reviewer | opus | read-only | adjudicative judgment (3 lenses + AC, venue score·verdict); lens `reconsider` sub-mode + AC delta report for `--with-rebuttal` |
| scholar-verifier | sonnet | read-only | summative automated gate |
| scholar-drafter | sonnet | write | the only .tex/.bib author (single, careful) |

## Routing

oms is a **domain handler** (the paper domain). The work-style lane decision (SP/OMC) is handled by [`oh-my-heroacademia`](https://github.com/luckkim123/oh-my-heroacademia) (omha) — oms does not decide the lane. Instead, after omha sets the lane, oms's UserPromptSubmit hook (`scholar_route_emit.py`) declares which **STAGE** (research/draft/verify…) within the paper domain applies each turn, in one line: `STAGE(paper) → …` — a keyword relevance gate skips this injection on clearly non-paper prompts (fail-toward-inject on any ambiguity). oms's hooks are self-contained and work without omha or `oh-my-claudecode` installed; the STAGE line simply rides alongside omha's ROUTE line when omha happens to be present. The PostToolUse hook (`scholar_verify_emit.py`) injects a citation-verification reminder after .tex/.bib edits (it does not auto-fix). A PreToolUse hook (`scholar_cite_guard.py`) structurally denies unverified citation writes (see citation-safety above). A Stop hook (`scholar_stop_guard.py`) keeps a live revise loop from ending early — scoped, six-exemption, fail-open. A SessionStart hook (`scholar_resume_emit.py`) advises on any in-scope non-terminal pipeline and re-injects Priority Context after compaction — silent otherwise. All 5 registered hooks fail-open and share a universal `DISABLE_OMS` kill switch (env `1/true/on/yes`, mirrors `DISABLE_OMC`), umbrella over the narrower per-hook hatches (`OMS_CITE_GUARD`, `OMS_STOP_GUARD`); none of these hatches are ever advertised in injected/deny/block text. Run `python3 scripts/oms_doctor.py` for a read-only PASS/WARN/FAIL packaging self-diagnosis (version SSOT, hooks/agents/skills registration, optional pipeline state).

## Status

v0.12.3 — 14 skills + 6 agents + reference cards (venues·rubrics·formats·learning-protocol·writing-craft·wiki·`grobid-intake`) + citation-safe hooks (`scholar_route_emit`/`scholar_verify_emit`/`scholar_cite_guard`/`scholar_stop_guard`/`scholar_resume_emit` + `oms_atomic`). Added in 0.12.0: **actionable-status wiki convention** — a wiki note may carry an optional `status: open-gap | resolved` frontmatter field (absent = not actionable, every existing note byte-unchanged); `oms_wiki_audit.py` gains an `open_gaps` dimension that enumerates every open-gap note tree-wide, and `scholar-verify` gains a WARN-only **Open wiki gaps** check so a recorded finding can't silently drop out of the next draft. 0.12.1–0.12.3 are fix-only releases: `scholar-verify`'s WARN enumeration now names every WARN check (claim-faithfulness, blind-review anonymization, open-wiki-gaps included, not just the two it used to name); `oms_wiki_audit.py`'s docstring and `references/wiki/audit.md` were brought back in sync on the mechanical-dimension count; and two small debt items were paid down — `oms_state.py`'s repeated slug-error string is now a single helper, and the two hooks' nearest-ancestor directory walks share one `hooks/oms_paths.py::nearest_ancestor` implementation. Added in 0.11.0: **ecosystem accelerators (P5 #35–#37)** — the `citation_lookup()` abstract-function contract is documented next to `wiki_query()` in `references/wiki/README.md` (today's Crossref/OpenAlex implementation described precisely, plus Semantic Scholar/arXiv/Zotero MCP swap-points as opt-in citation sources behind the same human gate); a standalone `references/grobid-intake.md` card documents the optional, self-hosted GROBID PDF-intake accelerator (proposes, never commits — every entry still passes `verify_bib_entry.py` and the human gate); `scholar-research`'s Step 2 gains the 4-field delegation template, a fan-out sizing rule capped at 3 concurrent read batches inside the single `mode=gap-research` pass, an interleaved gap-check, and a marginal-returns stopping heuristic; a new stdlib-only, zero-network `scripts/bib_coupling.py` computes bibliographic coupling clusters over per-paper `.bib` reference lists as an optional clustering seed. No MCP server or GROBID instance is a prerequisite for any stage (P5-A); nothing lands in `.bib` without the existing human gate + mechanical check (P5-B). Added in 0.10.0: **research-companion expansion (P4)** — `scholar-read` (13th skill: deep-reads ONE external paper into a structured `.oms/reading/<citekey>.md` note, never a citation source) and `scholar-discuss` (14th skill: standing Socratic discussion partner — Contrarian/Simplifier/Ontologist stances + a Co-STORM-style moderator move, zero `.tex`/`.bib` surface) join the roster; `scholar-researcher` gains `mode=deep-read`, `scholar-inspector` gains a read-only `mode=moderator` anti-groupthink pass before GATE 1, `scholar-reviewer`/mock-review gain a `--with-rebuttal` reconsider round (locked pre-rebuttal verdicts, human-gated rebuttal, one-band sycophancy cap) plus an aspect-checklist-first + concession-threshold realism pack, `scholar-verifier`'s report is regrouped into 5 submission-checklist categories with a new blind-review-anonymization WARN, a `research-log.md` narrative-memory substrate lands alongside `reviews-log.md`, and 4 R4 wiki-audit carry-overs (frontmatter WARN split, orphan-vs-INDEX regression guard, token-grammar spec, hyphen-adjacency guard) are closed out — the route hook STAGE enum growing to include `read`/`discuss` is the only hook change this round. Added in 0.9.0: **knowledge lifecycle (P3)** — wiki audit CLI (`scripts/oms_wiki_audit.py`: mechanical dimensions + `--write-index` INDEX generation), wiki audit procedure card (judgment dimensions + 2026-06-02 calibration lesson), thin frontmatter standard + INDEX.md contract in the wiki spec, light-channel evidence signal (`confidence: low` forced on pointer-less wiki appends), mock-review verdict history (`reviews-log.md`) + meta-review mining, wiki→reference-card anchoring verb in `scholar-learn` — no hook changes this round; live-corpus migration deferred to post-merge dogfood. Added in 0.8.0: **packaging & authoring hygiene (P2)** — version SSOT + sync checker, oms doctor, agent cross-reference locks, verifier re-tiered sonnet, skill shim/skill-bodies split under the 64 KiB budget, DISABLE_OMS kill switch + route relevance gate, atomic venue-config writes. Added in 0.7.0: **pipeline state & loop robustness (P1)** — `.oms/state` schema + `oms_state` CLI, mechanical strike/round ledger, scoped revise Stop-guard, SessionStart resume advisory + post-compaction Priority-Context re-injection, verifier round-id echo, abort/interrupt spec, notepad 3 tiers. Added in 0.6.0: **citation-integrity enforcement (P0)** — PreToolUse cite interlock, Crossref/OpenAlex DOI+retraction pre-gate with allowlist recording, claim-faithfulness (citation-misuse) WARN, `[MATERIAL GAP]` token + uncited-claim WARN, per-claim quote anchoring in research notes. 0.5.0: writing-craft rule injection — `references/writing-craft.md` is the single SSOT for rules across 4 dimensions (FLOW old→new·TONE decorative words/em-dash·LOGIC one-ping/overgeneralization·STRUCTURE CARS Move-2/OCAR); drafter skeleton+self-audit, planner rhetorical-structure axis, verify writing WARNs, inspect reverse-outline. 0.4.0: paper structure model (common skeleton + scale variations flat/system/thesis). 0.3.0: **`scholar-mock-review`** (venue reviewer mock review). 0.2.0: `scholar-init`·`scholar-deepen`·`scholar-learn`·2-tier global wiki. Structure·hooks verified via pytest (including enforced plugin.json↔skills/ 1:1, full suite green) / grep. Runtime end-to-end verified via `scripts/integration_smoke.py`, run manually — GATE 1 auto-approved for this run only; see script docstring for cost/auth. R1–R5 are merged and tagged (`v0.6.0`–`v0.10.0`); this release (R6, v0.11.0) was stacked on R5 and merged back over main, and tag `v0.11.0` is cut after it merges. translate / standardize are follow-up candidates. Full details in the [CHANGELOG](CHANGELOG.md).
