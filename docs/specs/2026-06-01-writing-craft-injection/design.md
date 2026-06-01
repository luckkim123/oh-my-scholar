# Design — Writing-Craft Injection (oms v0.5.0)

> **Status**: design (spec stage 1 of versioned release). Implementation deferred to a later session.
> **Date**: 2026-06-01
> **Author**: design via superpowers:brainstorming, gap analysis pre-completed.
> **Target version**: oms 0.4.0 → 0.5.0 (feature).

---

## 1. Problem

oms drafter output reads as awkward across four dimensions — **FLOW, TONE, LOGIC, STRUCTURE**. A read-only gap analysis (research note + 3-facet survey of the repo) found the root cause:

> oms's **architecture is strong** (inspect⊥verify⊥mock-review 3-axis split, severity taxonomy, the abstract-WARN precedent, human-gated learn loop) but its **writing-craft rule content is nearly empty**. Prose-craft vocabulary exists in exactly ONE place (`scholar-inspector.md` prose lens), and that is a *post-draft critic lane* — so there is **no means to shape flow/tone at generation time**.

### Root-cause gaps (by dimension)

| Dimension | Current state | Key hole |
|:---|:---|:---|
| **FLOW** | 4/5 MISSING, 1 WEAK | Gopen-Swan **old→new (stress position)** entirely absent — the #1 cause of "awkward flow" |
| **TONE** | 9/12 MISSING, 2 WEAK | ornamental verb/adjective ban, em-dash cap, hedge-gating all absent (only abstract-quantitative WARN exists, orthogonal) |
| **STRUCTURE** | v0.4.0 model is *section ordering only* (flat/system/thesis) | rhetorical-structure axis (CARS, OCAR) is wholly empty |
| **LOGIC** | citation-safety strong; *argument construction* weak | one-ping, refutable contributions, per-paragraph plan, reverse-outline, overgeneralization-flag all absent |

### Highest-value holes (priority)
1. **CARS Move-2 (gap) enforcement** — oms *already produces* a one-sentence gap in the researcher stage; what's missing is forcing the intro to *deploy* it as an explicit niche move. Low cost (placement, not new material), high effect.
2. **per-paragraph one-claim plan** — oms plans at section granularity and jumps straight to prose. The research note's "strongest single principle."
3. **overgeneralization flag** — AutoSurvey's empirical #1 hallucination mode (51%); oms has zero coverage distinct from citation-fabrication, despite this fitting oms's citation-safe identity perfectly.

### Evidence base
Authoritative rules consolidated in the research note:
`/Users/kimseungmin/Desktop/workspace/90-99_Inbox_Archive/91_Inbox/llm-paper-writing-research/2026-06-01-llm-academic-writing-survey.md`
Each rule traces to a verified source (Gopen-Swan 1990, Swales CARS, Schimel OCAR, Peyton Jones, Nature HB 2025 excess-vocabulary study, AutoSurvey/WriteHERE pipelines, plus peer Claude-Code skills academic-research-skills/sciwrite/Master-cai). Citation honesty caveat: Gopen-Swan/Pinker/Schimel rules came via secondary summaries — adopted as *drafter rules* (not cited claims), so the caveat does not block adoption; if ever quoted verbatim in an oms-produced paper, cross-check originals.

---

## 2. Solution principle

The missing piece is **content, not structure** — every gap maps cleanly onto an existing oms lane. The design therefore:

- adds **one new SSOT card** (`references/writing-craft.md`) holding all four-dimension rules;
- **augments the drafter's generation flow** so rules are enforced at write time (skeleton-first + silent self-audit);
- adds a **two-tier verification safety net** (mechanical checks → verify WARN; judgment checks → inspect lens);
- **bifurcates the learn loop** so universal propositions become enforced venue defaults while user/venue-specific phrasing stays light/advisory.

The **abstract-quantitative WARN (commit bce59f4)** is the proven template for every mechanical prose check: token SSOT in a reference card → verifier reports WARN (not FAIL) for venue variance → paper-eval row → multibyte-grep caveat (Python `re` only).

### Non-goals (YAGNI)
- **Embedding-based exemplar retrieval** — violates oms's §6.A anti-embedding stance; EMNLP 2025 shows similarity-curated exemplars *backfire*. Use ~5 random representative paragraphs instead.
- **Manchester phrasebank text bulk-copy** — IP. Adopt only the move×function *taxonomy*, author own examples.
- **Automatic hard-FAIL writing gate** — static blocklists decay (Nature HB §5-A); multibyte grep false-clean risk. Writing checks are WARN/formative, never auto-FAIL.

---

## 3. Components

### 3.1 `references/writing-craft.md` (NEW — rule SSOT)

Single source of truth for four-dimension rules, read by drafter, inspector, verifier. Separated from `latex.md` by role: **latex = how to typeset; writing-craft = how to argue & narrate.**

Structure (each dimension = 1 section, each rule = source anchor + one-line rule):

- **§1 FLOW** — Gopen-Swan old→new (stress position) · subject-verb proximity · action-in-verb (anti-nominalization) · context-first · banana rule (exact keyword repetition). ⚠️ old→new is stated as *higher priority than active-voice* (passive allowed when it puts old info first).
- **§2 TONE** — ornamental verb/adjective ban as a *principle* ("does this carry payload?", not a decaying word list) · copula-avoidance ban · em-dash cap · bans on rule-of-three / uniform sentence length / negative parallelism / -ing padding.
- **§3 LOGIC** — one-ping (stated explicitly) · refutable bulleted contributions driving the paper · forward-referenced evidence · ban "rest of paper structured as follows" · TEEL paragraph model · overgeneralization warning (= top failure mode).
- **§4 STRUCTURE** — CARS 3-move (Move-2 gap mandatory) · OCAR/LDR arc · hourglass (Opening width = Resolution width) · arc selection by audience patience (venue variant).
- **§5 VOICE/VENUE** — discipline > journal > personal precedence · STEM method passive / contribution active.
- **§6 EXEMPLAR** — ~5 *random representative* paragraphs (no similarity-curation, ≤5 cap). References `venues.md` `voice`/`exemplars` fields.
- **§7 MECHANICAL-CHECK TOKENS** — the WARN token list the verifier reads (ornamental words, em-dash threshold, rule-of-three markers). ⚠️ multibyte grep false-negative caveat (em-dash `—`, `×` are multibyte; Python `re` only — abstract-WARN precedent verbatim).

Venue variance is explicit: related-work placement (Peyton Jones "end" ↔ CARS "front") and arc selection are NOT hardcoded — parameterized via venue card.

### 3.2 `agents/scholar-drafter.md` (MODIFIED — generation flow)

Current protocol fuses reasoning+composition in one pass. Insert two steps; citation-safety core unchanged.

- **Step A — reasoning skeleton (before prose, NEW)**: before writing a section, emit its **per-paragraph `{claim, evidence/cite-keys, link}` skeleton**. Confirm CARS Move-2 (gap) and one-ping are explicitly occupied here. Implements per-paragraph plan + reasoning-skeleton-first simultaneously. ⚠️ skeleton written to `.oms/<slug>/` workspace (output-layout compliant, no source-folder pollution) so inspect can reuse it.
- **Step B — prose render (existing)**: render skeleton to `.tex`, applying writing-craft.md §1–6 (old→new, TEEL, voice).
- **Step C — silent self-audit (before return, NEW)**: silent check against writing-craft.md §2 (tone) + §7 (tokens) — ornamental words, em-dash, rule-of-three, uniform length. anti-ai-slop 11-item pattern. ⚠️ this is *hygiene, not a gate* — does NOT violate "no self-approval" (inspector/verifier passes still run separately).

**Citation invariants preserved**: skeleton cite-keys must be verified `.bib` keys; no inline fabrication; no new citations minted skeleton→prose.

**Trade-off acknowledged**: drafter goes 1-pass → 3-step (heavier). Mitigated — skeleton is terse (3 fields/paragraph), self-audit is silent (no output). Consistent with oms's single-careful generation identity (aligned with citation-safety).

### 3.3 `agents/scholar-planner.md` (MODIFIED — rhetorical structure axis)

Add a rhetorical-structure axis **orthogonal** to the v0.4.0 section-ordering model (does NOT overwrite flat/system/thesis):
- CARS 3-move with **Move-2 gap as a Final_Checklist item** (top reject reason if intro states territory but never carves the gap; reuse researcher's existing one-sentence gap).
- OCAR arc · hourglass width-match · arc selection by audience patience (venue-parameterized).
- per-section brief gains a "the one proposition this section must argue" field.

### 3.4 `agents/scholar-verifier.md` + `references/rubrics/paper-eval.md` (MODIFIED — mechanical WARN)

Add a writing WARN row reading writing-craft.md §7 tokens (ornamental words, em-dash threshold, rule-of-three). **WARN ≠ FAIL** (abstract-WARN precedent, venue variance preserved). ⚠️ multibyte detection via Python `re`, never `LC_ALL=C grep`. paper-eval verify-axis gains a row.

### 3.5 `agents/scholar-inspector.md` (MODIFIED — judgment lenses)

- *prose lens upgrade*: replace the vague list with actionable checks against writing-craft.md §1 (FLOW) / §2 (TONE). Add **reverse-outline audit** procedure (extract topic sentences → check each against thesis → flag orphans; reuse Step-A skeleton).
- *logic lens*: add **overgeneralization flag** (claim broader than cited support = #1 priority, top failure mode). Citation-safe boundary → *formative flag only*, never auto-FAIL; sibling of the existing `assumption: FRAGILE` label.
- severity: reuse existing `critical/important/minor`; map writing finding types (e.g. buried predicate = important).

### 3.6 `references/learning-protocol.md` + `references/venues.md` (MODIFIED — learn bifurcation)

- **enforced default**: add `venue.prose_defaults` to the `candidate_default.target` enum — universal propositions (old→new, em-dash cap) promotable to venue-enforced. Add `prose_defaults`/`voice` fields to `venues.md` schema.
- **light**: user/venue-specific phrasing preferences → wiki `convention/` (advisory, never enforced). Aligns with §5-A "blocklists decay."
- Both human-gated (no auto-promotion). **citation/.bib remains permanently non-promotable** (regression guard).

---

## 4. Data flow

```
research(gap 1-sentence) ──┐
                           ▼
planner ── rhetorical axis (CARS Move-2 gap, OCAR, hourglass) + section brief("must argue")
   │            reads: writing-craft.md §4, §5
   ▼
drafter
   ├─ Step A skeleton {claim, cite-keys, link} ──► .oms/<slug>/ (inspect reuses)
   │     reads: writing-craft.md §3 (one-ping), §4 (Move-2)
   ├─ Step B prose render
   │     reads: writing-craft.md §1 (FLOW), §2 (TONE), §5 (voice), §6 (exemplar)
   └─ Step C silent self-audit
         reads: writing-craft.md §2, §7
   ▼
verify ── mechanical WARN (writing-craft.md §7 tokens, Python re)      [WARN≠FAIL]
inspect ── prose lens (FLOW/TONE) + reverse-outline (reuse skeleton)
           logic lens (overgeneralization flag)                        [formative]
   ▼
learn ── prose_defaults → venue-enforced (human gate)
         user/venue phrasing → light wiki convention/ (advisory)
```

---

## 5. Testing strategy (TDD)

oms convention: `tests/` regression guards (currently 53 tests). Each component gets a guard; reviewer 2-lane (spec-compliance ≠ code-quality) per task.

| Test | Asserts |
|:---|:---|
| `test_writing_craft_card.py` | writing-craft.md exists; 7 sections; each dimension's key rule tokens present; §7 token list parseable |
| `test_drafter_skeleton_step.py` | drafter.md states Step A (skeleton) + Step C (self-audit); citation-safety invariant intact (inline-fabrication ban text retained) |
| `test_planner_rhetorical_axis.py` | planner.md has CARS Move-2 gap / OCAR / hourglass tokens; v0.4.0 ordering model regression 0 (flat/system/thesis retained) |
| `test_verify_writing_warn.py` | verifier classifies writing issues as WARN not FAIL; multibyte (em-dash) detection via Python re |
| `test_learn_prose_defaults.py` | learning-protocol enum has `venue.prose_defaults`; venues.md schema has `prose_defaults`/`voice`; citation/.bib non-promotable retained |

---

## 6. Release plan (versioned)

1. **Spec** (this session) — `docs/specs/2026-06-01-writing-craft-injection/design.md`
2. **Plan** (this session) — `.../plan.md` (TDD tasks)
3. **Execute** (later session) — subagent-driven; per task: fresh implementer + spec-compliance reviewer + code-quality reviewer
4. **Release** (later session) — v0.5.0 bump + CHANGELOG (Added/Changed/Verification/Notes) + README + full suite (53 → ~63 tests)
5. **PR** — Summary + Test plan checklist; squash merge on explicit approval

**Scope boundary (this session)**: stages 1–2 (spec + plan) only. Zero implementation.

---

## 7. Constraints & invariants (must survive implementation)

- **Repo vs project boundary**: writing-craft.md ships to everyone (generic); project-specific writing decisions live in per-project `.oms/wiki/convention/`, never leak into the shipped harness.
- **Citation safety**: no fabricated citations; no auto-`.bib` edits; citation/.bib never learn-promotable.
- **No self-approval**: drafter self-audit is hygiene; inspector/verifier remain separate gates.
- **WARN ≠ FAIL** for all writing checks (venue variance).
- **v0.4.0 structure model orthogonal** — rhetorical axis adds, never overwrites section-ordering.
- **Surgical**: this is harness meta-work — line-by-line review, no OMC team/autopilot.
