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

oms is a **domain handler** (the paper domain). The work-style lane decision (SP/OMC) is handled by [`oh-my-heroacademia`](https://github.com/luckkim123/oh-my-heroacademia) (omha) — oms does not decide the lane. Instead, after omha sets the lane, oms's UserPromptSubmit hook (`scholar_route_emit.py`) declares which **STAGE** (research/draft/verify…) within the paper domain applies each turn, in one line: `STAGE(paper) → …`. The PostToolUse hook (`scholar_verify_emit.py`) injects a citation-verification reminder after .tex/.bib edits (it does not auto-fix).

## Status

v0.5.0 — 12 skills + 6 agents + reference cards (venues·rubrics·formats·learning-protocol·**writing-craft**·wiki) + citation-safe hooks (`scholar_route_emit`/`scholar_verify_emit` + `oms_atomic` atomic writes). Added in 0.5.0: **writing-craft rule injection** — `references/writing-craft.md` is the single SSOT for rules across 4 dimensions (FLOW old→new·TONE decorative words/em-dash·LOGIC one-ping/overgeneralization·STRUCTURE CARS Move-2/OCAR). The drafter follows the rules *at generation time* via a reasoning skeleton before prose + a silent self-audit before returning; the planner adds the rhetorical-structure axis (orthogonal to the v0.4.0 section-order model); verify adds writing WARNs (≠FAIL); inspect adds reverse-outline + overgeneralization flags. learn promotes universal propositions into `venue.prose_defaults` (idiosyncratic phrasings go to a light wiki). Source anchors: Gopen-Swan·Swales CARS·Schimel·Peyton Jones·Nature HB 2025·AutoSurvey. 0.4.0: paper structure model (common skeleton + scale variations flat/system/thesis). 0.3.0: **`scholar-mock-review`** (venue reviewer mock review). 0.2.0: `scholar-init`·`scholar-deepen`·`scholar-learn`·2-tier global wiki. Structure·hooks verified via pytest (including enforced plugin.json↔skills/ 1:1, **98 passed**) / grep. **runtime end-to-end still needs real testing in a plugin-reload session.** translate / standardize are follow-up candidates. Full details in the [CHANGELOG](CHANGELOG.md).
