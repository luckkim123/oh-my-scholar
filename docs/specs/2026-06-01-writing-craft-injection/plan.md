# Plan — Writing-Craft Injection (oms v0.5.0)

> **Pairs with**: `design.md` (same folder). Read it first — this plan assumes its decisions.
> **Method**: TDD. Each task = write failing test (red) → implement (green) → reviewer 2-lane (spec-compliance ≠ code-quality). Fresh implementer per task to protect controller context.
> **Scope**: implementation deferred to a later session. This file IS the deliverable for *this* session.
> **Invariants** (every task must preserve — see design §7): citation safety, no self-approval, WARN≠FAIL, v0.4.0 structure model orthogonal, repo/project boundary, surgical.

---

## Task ordering & dependencies

```
T1 writing-craft.md (SSOT card) ──┬──► T2 drafter (reads §1-7)
                                  ├──► T3 planner (reads §4,§5)
                                  ├──► T4 verifier+paper-eval (reads §7)
                                  └──► T5 inspector (reads §1,§2,§3)
T6 learn bifurcation (learning-protocol + venues.md)  [independent of T1; can run parallel]
T7 release (v0.5.0 bump + CHANGELOG + README + full suite)  [last, depends on T1-T6]
```

**T1 is the hard prerequisite** — it is the SSOT every other component reads. T6 (learn) is independent and may proceed in parallel. T7 is the release gate, last.

---

## T1 — `references/writing-craft.md` (rule SSOT)

**Goal**: create the four-dimension rule card, the single source of truth read by drafter/inspector/verifier.

**Red — `tests/test_writing_craft_card.py`**:
- file `references/writing-craft.md` exists.
- contains 7 section headings (§1 FLOW … §7 mechanical-check tokens).
- each dimension's anchor rule token present: `old→new` / `stress position` (FLOW), ornamental-word ban + `em-dash` (TONE), `one ping` + `overgeneralization` (LOGIC), `CARS` + `Move 2` + `OCAR` (STRUCTURE).
- §7 token list is parseable (a fenced block or list a verifier can read).
- venue-variance note present (related-work placement NOT hardcoded).

**Green**: author the card per design §3.1. Rules terse, bilingual KO/EN matching repo voice. Each rule carries a source anchor (Gopen-Swan / Swales / Schimel / Peyton Jones / Nature HB / AutoSurvey / peer-skill). Ornamental-word rule stated as *principle* + a seed token list for §7. ⚠️ §7 must carry the multibyte-grep caveat (Python `re` only).

**Reviewer 2-lane**: (a) spec-compliance — all 7 sections + 3 non-goals respected (no embedding, no Manchester bulk-copy, no auto-FAIL). (b) code-quality — no duplication with `latex.md`; rules actionable not vague.

---

## T2 — `agents/scholar-drafter.md` (skeleton + self-audit)

**Goal**: insert Step A (reasoning skeleton) and Step C (silent self-audit) into the drafter protocol; preserve citation-safety core.

**Red — `tests/test_drafter_skeleton_step.py`**:
- drafter.md Investigation_Protocol names a skeleton step producing per-paragraph `{claim, evidence/cite-keys, link}` BEFORE prose.
- skeleton output path is `.oms/<slug>/` (not source folder).
- names a silent self-audit step before handoff, referencing writing-craft.md §2/§7.
- **regression**: inline-citation-fabrication ban text still present; "no self-approval" text still present; drafter still hands off to verifier/inspector (self-audit is not a gate).
- drafter references `writing-craft.md`.

**Green**: edit drafter.md per design §3.2. Step A between read-notes and draft-prose; Step C before handoff. Add "reads writing-craft.md §1-6" to its loaded-cards list.

**Reviewer 2-lane**: (a) spec — skeleton is terse (3 fields), self-audit silent, CARS Move-2/one-ping checked in skeleton. (b) quality — citation invariants verbatim-intact; no collapse of drafter/inspector lanes.

---

## T3 — `agents/scholar-planner.md` (rhetorical axis)

**Goal**: add rhetorical-structure axis orthogonal to the v0.4.0 section-ordering model.

**Red — `tests/test_planner_rhetorical_axis.py`**:
- planner.md contains CARS 3-move tokens with **Move-2 gap as a checklist/reject item**.
- contains OCAR + hourglass (Opening=Resolution width) + audience-patience arc selection.
- per-section brief includes a "must argue / proposition" field.
- **regression**: v0.4.0 model intact — `flat`/`system`/`thesis` structure_type tokens retained; no-experiments-at-end guard retained.
- arc/related-work selection marked venue-parameterized (not hardcoded).

**Green**: edit planner.md per design §3.3. New `<Rhetorical_Axis>` (or extend `<Structure_Types>`) block; reuse researcher's one-sentence gap for Move-2.

**Reviewer 2-lane**: (a) spec — Move-2 enforced as top reject reason; orthogonality stated. (b) quality — does not duplicate or contradict v0.4.0; venue-variance honored.

---

## T4 — `agents/scholar-verifier.md` + `references/rubrics/paper-eval.md` (mechanical WARN)

**Goal**: add a writing WARN row reading writing-craft.md §7 tokens.

**Red — `tests/test_verify_writing_warn.py`**:
- verifier.md has a writing-check row reading writing-craft.md §7.
- it is classified **WARN, not FAIL** (assert the WARN tier explicitly, mirroring the abstract-WARN row).
- multibyte detection specified via Python `re` (assert no `LC_ALL=C grep` for em-dash/×).
- paper-eval.md verify-axis has a corresponding row.

**Green**: edit verifier.md + paper-eval.md per design §3.4, mirroring the bce59f4 abstract-WARN pattern exactly.

**Reviewer 2-lane**: (a) spec — WARN≠FAIL, token source = writing-craft.md §7. (b) quality — inherits multibyte caveat; no new FAIL path for writing.

---

## T5 — `agents/scholar-inspector.md` (judgment lenses)

**Goal**: upgrade prose lens to actionable; add reverse-outline + overgeneralization flag.

**Red — `tests/test_inspector_writing_lenses.py`** (new; or extend existing inspector test):
- prose lens references writing-craft.md §1 (FLOW) / §2 (TONE) with actionable checks (not the old vague list).
- a reverse-outline audit procedure present (topic-sentence extraction → thesis check), noting reuse of Step-A skeleton.
- logic lens has an **overgeneralization** flag marked #1 priority and **formative-only** (no auto-FAIL).
- severity mapping for writing findings uses existing critical/important/minor.

**Green**: edit inspector.md per design §3.5.

**Reviewer 2-lane**: (a) spec — overgeneralization formative-only (citation-safe boundary). (b) quality — reverse-outline reuses skeleton, no duplication with verifier's mechanical pass.

---

## T6 — `references/learning-protocol.md` + `references/venues.md` (learn bifurcation)

**Goal**: enable promoting universal prose rules to venue-enforced defaults; keep user/venue phrasing light.

**Red — `tests/test_learn_prose_defaults.py`**:
- learning-protocol `candidate_default.target` enum includes `venue.prose_defaults`.
- venues.md schema documents `prose_defaults` and `voice` fields.
- light channel (wiki `convention/`) documented for user/venue-specific phrasing.
- **regression**: citation/.bib explicitly NON-promotable (assert the permanent ban text retained).
- promotion remains human-gated (no auto-promotion).

**Green**: edit learning-protocol.md (enum + channel doc) + venues.md (schema fields) per design §3.6.

**Reviewer 2-lane**: (a) spec — bifurcation (enforced + light) both present; human-gated. (b) quality — citation ban regression intact; enum addition does not break existing promotable targets.

---

## T7 — Release (v0.5.0)

**Goal**: version bump + docs + full suite green.

**Steps** (single task, no new feature):
- bump version (whatever oms's version locus is — CHANGELOG header / manifest).
- `CHANGELOG.md`: Added (writing-craft.md, skeleton+self-audit, rhetorical axis, writing WARN, prose lenses, prose_defaults) / Changed / Verification (test count 53 → ~63) / Notes (WARN≠FAIL rationale, repo/project boundary).
- README: mention writing-craft as the prose-rule SSOT.
- run full suite; confirm 53 baseline + ~10 new all pass.

**Reviewer 2-lane**: (a) spec — all 4 release artifacts synchronized (branch/commits/CHANGELOG/PR). (b) quality — no orphaned tests, version coherent.

**PR**: Summary + Test plan checklist; squash merge on explicit approval.

---

## Risk notes for the implementer

- **multibyte grep false-clean** (memory: confirmed trap) — any em-dash/× detection MUST use Python `re`; `grep`/`grep -P` give false 0 on macOS C-locale. The §7 verifier check inherits this.
- **plugin cache vs source repo** (memory) — edits go to `~/oh-my-scholar` (source). Runtime reflection needs marketplace update + app restart; `/clear` is not enough.
- **don't over-specialize** (memory) — writing-craft.md ships to everyone; no machine/user-specific names or paths in it. User/venue specifics belong in light wiki only.
- **Edit not Write for existing files** — T2–T6 modify existing agent/reference files; read then surgical Edit, do not regenerate whole files.
- **53-test baseline** — run the suite before starting to confirm the true baseline count; the "~63" target is an estimate.
