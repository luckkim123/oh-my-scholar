# oh-my-scholar (oms)

> Multi-agent orchestration harness for **academic paper writing** — treats writing a paper like writing code, with citation-integrity guardrails.

Lineage: [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) (omc) → `oh-my-docs` (omd) → **`oh-my-scholar` (oms)**

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
| scholar-researcher | sonnet | read-only | related work·gap survey |
| scholar-planner | opus | read-only | outline·story arc |
| scholar-inspector | opus | read-only | formative critique (logic/prose) — coach |
| scholar-reviewer | opus | read-only | adjudicative judgment (3 lenses + AC, venue score·verdict) |
| scholar-verifier | opus | read-only | summative automated gate |
| scholar-drafter | sonnet | write | the only .tex/.bib author (single, careful) |

## Routing

oms is a **domain handler** (the paper domain). The work-style lane decision (SP/OMC) is handled by [`oh-my-heroacademia`](https://github.com/luckkim123/oh-my-heroacademia) (omha) — oms does not decide the lane. Instead, after omha sets the lane, oms's UserPromptSubmit hook (`scholar_route_emit.py`) declares which **STAGE** (research/draft/verify…) within the paper domain applies each turn, in one line: `STAGE(paper) → …`. The PostToolUse hook (`scholar_verify_emit.py`) injects a citation-verification reminder after .tex/.bib edits (it does not auto-fix). A third hook (PreToolUse `scholar_cite_guard.py`) structurally denies unverified citation writes (see citation-safety above).

## Status

v0.6.0 — 12 skills + 6 agents + reference cards (venues·rubrics·formats·learning-protocol·writing-craft·wiki) + citation-safe hooks (`scholar_route_emit`/`scholar_verify_emit`/**`scholar_cite_guard`** + `oms_atomic`). Added in 0.6.0: **citation-integrity enforcement (P0)** — PreToolUse cite interlock, Crossref/OpenAlex DOI+retraction pre-gate with allowlist recording, claim-faithfulness (citation-misuse) WARN, `[MATERIAL GAP]` token + uncited-claim WARN, per-claim quote anchoring in research notes. 0.5.0: writing-craft rule injection — `references/writing-craft.md` is the single SSOT for rules across 4 dimensions (FLOW old→new·TONE decorative words/em-dash·LOGIC one-ping/overgeneralization·STRUCTURE CARS Move-2/OCAR); drafter skeleton+self-audit, planner rhetorical-structure axis, verify writing WARNs, inspect reverse-outline. 0.4.0: paper structure model (common skeleton + scale variations flat/system/thesis). 0.3.0: **`scholar-mock-review`** (venue reviewer mock review). 0.2.0: `scholar-init`·`scholar-deepen`·`scholar-learn`·2-tier global wiki. Structure·hooks verified via pytest (including enforced plugin.json↔skills/ 1:1, **144 passed**) / grep. **runtime end-to-end still needs real testing in a plugin-reload session.** translate / standardize are follow-up candidates. Full details in the [CHANGELOG](CHANGELOG.md).
