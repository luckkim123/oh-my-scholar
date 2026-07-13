---
name: scholar-learn
description: |
  Observation → venue default promotion (oms's core evolution gate) — during operation, the observations
  accumulated in `.oms/learned.md` and the auto-accumulated patterns in `.oms/wiki/` are reviewed read-only
  by scholar-inspector to judge which ones qualify for promotion into the enforced defaults of
  `references/venues.md` (required sections, ordering, self-cite caps, etc.). The heavy channel (defaults)
  must always pass a human approval gate, and each promotion raises venue specificity, advancing one step from
  "general → specialized to this user". No automatic promotion — the human breaks the gate. Citation/.bib
  promotion is permanently forbidden.
  Triggers: 학습 반영, 규칙 승격, 관찰 정리, learned 검토, 패턴 굳혀, 이거 기본값으로,
  scholar learn, promote observation, learn venue defaults, specificity 올려, 진화 게이트
---

# scholar-learn — observation → venue default promotion (core evolution gate)

<Purpose>
The stage where oms's asymmetry — "general at deployment, specialized to this user the more it's used" — *closes
all the way to enforcement*. During operation, scholar-inspector (read-only) reads the observations accumulated
in `.oms/learned.md` (e.g. "IROS papers always have an Ablation section — repeated 3 times") and judges which
observations qualify for promotion into the **enforced defaults** of `references/venues.md`. Promotion is a
**one-way ratchet** that changes the *baseline assumption* of all subsequent work on that venue (if promoted
wrongly, the outline lays down the wrong section every time and verify raises false warnings), so it always
passes a human approval gate. Each promotion raises the venue's `specificity` toward 0 (pure template) → 1
(fully specialized). scholar-inspector **only judges** — it does not write or enforce defaults directly, and
only after the human breaks the gate does this skill commit it to disk. The canonical reference for the dynamics
is `references/learning-protocol.md`.
</Purpose>

<Use_When>
- During operation, when enough observations have accumulated in `.oms/learned.md` to judge "should we now solidify these into venue defaults?"
- When the same pattern (section, ordering, self-cite cap) has been observed repeatedly and you want to raise it to an enforced default
- When the user explicitly stated "from now on IROS is always X" (=user_stated) and you want to solidify it as a venue default
- When you want to raise venue specificity so oms becomes more specialized to this user
- When scholar-pilot has surfaced a "N promotion candidates accumulated" notice during the operating loop
</Use_When>

<Do_Not_Use_When>
- If `.oms/learned.md` is empty → there are no observations to promote yet. inspect/verify fill it as you operate.
- If it's merely a light pattern, preference, or decision memo and not an enforced default → don't promote; leave it to auto-accumulate in `.oms/wiki/` (no gate needed, recovered via grep next session). In particular, `wiki/pattern/` (preferences) is permanently light — never a promotion target. Not every observation becomes a default.
- ⚠️ **If it's a citation, .bib, or "cite this paper" type → permanently forbidden from promotion** (`learning-protocol.md` §6.F). If candidate_default.target is citation/bib, the schema rejects it. Citations live only in the paper-slug's .tex/.bib SSOT.
- If it's *quality verification* of the paper (PASS/FAIL) → `scholar-verify`. learn *creates* defaults, verify *judges* — different lane.
- If you're *writing* a draft → `scholar-draft`. learn does not create file content (meta-learning only).
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Human approval gate is absolutely mandatory (core)** — scholar-inspector only issues promotion *proposals*. No observation is auto-committed to `venues.md` without human approval. No automatic passing. No matter how high confidence/evidence is (§6.B). The cost of 1 wrongly-promoted default (a false assumption on every task) > the cost of 1 missed default (raise it again at the next learn).
- ⚠️ **Promotion criteria are AND (learning-protocol.md §3)** — repeated `evidence_count ≥ 3` + 0 counterexamples + not user_overridden + stable + no contradiction. **All** must be met to go to the human gate. Not a score sum.
  - ⭐ **user_stated exception (resolves review #1)**: a rule the user stated directly (`user_stated: true`) skips the repetition bar even with evidence 1 and goes to the gate — the user stating it directly = already intent. But it **still passes the gate** (which scope? does it contradict an existing one?). Auto-enforcement is forbidden here too.
  - ⭐ **The 3-times bar is not a magic number (resolves review #2)**: it's the value omp §3.1 justifies as the "minimum line for convention vs coincidence". Follows learning-protocol.md §3.1 verbatim.
- ⚠️ **scope distinction (oms-specific — not in omp)** — promotion is always bound to a scope: `global` (this user's universal habit) vs `<venue-key>` (limited to that venue). "Always Ablation" may be right for IROS but not for a thesis. The inspector states each candidate's scope, and specificity is computed separately per scope.
- ⚠️ **Respect the 2-channel separation** — only the *heavy channel* (defaults: learned.md → promote → venues.md) is the target of this skill and passes the gate. The *light channel* (patterns/preferences/decisions: `.oms/wiki/*.md` auto-append) needs no gate — read only, don't touch. `wiki/pattern/` (preferences) is permanently light.
- ⚠️ **Local→global wiki elevation (separate path, storage-location axis)** — separate from `scope: global` above being a *scope-of-application* label in venues.md, there is a path that elevates light-channel assets by **physical storage location** from the local `.oms/wiki/` to the *parent folder's `.oms/wiki/`* (global level, discovered by ascent). At paper close, candidates that "this asset is reusable for the next paper too" (preferences, venue formats, reuse decisions, history) are copied **after human approval** into the parent `.oms/wiki/<category>/`. Criteria:
  - Targets: among `pattern/` (preferences), `convention/` (venue formats), `decision/` (reuse decisions), `history/` (paper records), only *paper-agnostic reusable* assets. This paper's unique rejects/gaps stay local.
  - ⚠️ **citation/.bib are permanently forbidden from global elevation** (whether heavy or light, `learning-protocol.md` §6.F·§1.4).
  - Human gate required — no automatic elevation. If the parent `.oms/` does not exist, advise "init in the parent folder or place a `.oms/wiki/` there" (do not arbitrarily create one in the parent or home).
  - This is a different lane from venues.md default promotion (heavy) — it's merely a *location* move of light assets, not making them an enforced default. `wiki/pattern/` remains permanently light even when elevated to global (not enforced).
- ⚠️ **provenance enforcement** — each promoted default records the source learned.md observation id in the venue's `learned_refs[]`. A default without a source = a guess = a silent change (§6.C violation).
- ⚠️ **specificity honestly** — recompute even on item deletion (no silent drift, §4 monotonic + deletion rule). Don't inflate it to look more specialized.
- **Judgment ≠ approval ≠ enforcement (triple self-approval ban, resolves review #4)** — scholar-inspector only *judges* promotion read-only (it does not approve its own judgment in the same context), scholar-learn only *writes to disk* what passed the human gate (no judging), and compliance *verification* is the job of scholar-verify in a separate context. The three roles are separated.
- **Present as a diff** — since venues.md already exists, the inspector proposes not the whole file but a *delta* (Added/Changed defaults) so the human reviews only the changes.
- The canonical reference for the learning channels, promotion criteria, and specificity formula is `references/learning-protocol.md`; the venue schema is `references/venues.md`; the wiki convention SSOT is `references/wiki/README.md`.
</Execution_Policy>

<Steps>
1. **Confirm SSOT and prerequisites**: check that the working root and `.oms/learned.md` exist. If empty, stop and advise "there are no observations to promote — inspect/verify fill it as you operate". Read the following:
   - `.oms/learned.md` — observations awaiting promotion (the input to this skill)
   - `references/venues.md` — existing venue defaults to evolve (an *evolve*, not a blind replace)
   - `.oms/wiki/convention/*.md` — light channel. grep whether high-confidence signals have accumulated (read only)
   - `references/learning-protocol.md` — 2-channel, promotion criteria, specificity formula (canonical)
2. **Classify observations (2-channel discrimination)**: split each observation in learned.md into (a) venue default promotion candidates (heavy channel — gate target) vs (b) pattern/preference memos (light channel — leave in wiki, no gate needed). Not every observation becomes a default — apply the learning-protocol.md channel criteria. Citation/.bib types are excluded immediately (§6.F).
3. **First-pass screening of promotion candidates (evidence bar)**: apply the §3 criteria to each heavy-channel candidate — evidence_count ≥ 3 (or 1 if user_stated:true) + 0 counterexamples. If it clears, "promotion proposal"; if ambiguous, "held candidate". The controller's job is up to gathering the evidence; the final judgment/draft is delegated to the agent in the next step.
4. **Delegate to agent (promotion judgment — read-only)** — single delegation to scholar-inspector. Fresh subagent to prevent controller-context pollution. Since it's one careful synthesis, **no parallel inspectors**:

   ```
   Task(
     subagent_type="oh-my-scholar:scholar-inspector",
     description="scholar-learn: judge learned.md observations for promotion into venues.md",
     prompt="""
     Role: scholar-learn promotion judgment. Read the .oms SSOT below and, among the learned.md observations,
     judge which qualify for promotion into venues.md enforced defaults and issue a **proposal (diff)**. You are
     read-only — do not write venues.md directly, and do not judge compliance. A human approval gate sits
     between your proposal and disk.

     Inputs (to read):
     - .oms/learned.md                # observations awaiting promotion (incl. scope, evidence, counterexamples, user_stated)
     - references/venues.md           # existing defaults to evolve (evolve, not replace)
     - .oms/wiki/convention/*.md      # light-channel confidence signals (read only)
     - references/learning-protocol.md # 2-channel, promotion criteria §3, specificity formula §4 (canonical)

     Instructions:
     - Promotion criteria are AND (§3): evidence_count ≥ 3 + 0 counterexamples + not user_overridden + stable + no contradiction.
       But a user_stated:true candidate goes to the gate even with evidence 1 (repetition bar waived, §1.feedback.2). No auto-enforcement.
     - State each candidate's scope (global | <venue-key>). Compute specificity per scope.
     - Each promoted default records the source learned.md observation id in learned_refs[] (provenance).
     - Recompute specificity honestly with the §4 formula (don't inflate). Item deletion is also a recompute event.
     - Present as a **diff** against venues.md (Added/Changed defaults), not the whole file.
     - ⚠️ Reject citation/.bib/specific-citation targets from promotion candidates (§6.F).
     - Output: promote/held decisions + scope + provenance table + specificity rationale + human decision list.
       Do not write venues.md, propose only. No self-approve (judgment ≠ approval ≠ verification).
     """
   )
   ```

   ━━━ **GATE (core promotion gate — human)**: present the inspector's diff, scope, provenance, and specificity rationale to the human and obtain a decision — promote (approve) / hold / edit (only some) / abort.
   **Absolutely no automatic passing.** If the human says "raise it" for a user_stated held candidate, the decision is made here. ━━━
5. **Commit approved items (only after passing the gate)**: only defaults the human approved are written to disk by this skill.
   - **First** snapshot the existing venue values (workspace versions/, following the `output-layout.md` work-layer convention — promotion is a one-way ratchet, so this is the rollback point). retention: keep only the latest N and prune via trash (no permanent rm).
   - `references/venues.md` (or project `.oms/venues/<key>.yaml`) — add/change approved defaults, source observation id in `learned_refs[]`, mark the relevant item `learned` in `origins`, recompute `specificity` per scope. (Re-confirm schema conformance.)
   - Paired human-narrative companion (if present) — if the venue description changes, update it in the same pass (drift prevention, §6.C).
   - `.oms/learned.md` — mark promoted observations "promoted → venues.md (date)", keep held ones as candidates (re-evaluated at the next learn).
6. **Wiki → reference-card anchoring (a third lane — distinct from venue-default promotion above and the local→global wiki elevation bullet in Execution_Policy)**: promote a mature *global*-wiki cluster into a `references/` card, making the 2026-06 hand-done pattern (an external survey anchored into 5 oms files) a repeatable step. Runs independently of Steps 1-5 — no `learned.md`/`venues.md` involvement, a separate target.
   - **Trigger**: a *global*-wiki cluster (the parent-ascent `.oms/wiki/` level, `references/learning-protocol.md` §1.4) that is paper-agnostic and harness-relevant (informs how oms itself should work, not this paper's content) — `confidence: high` with `sightings ≥ 3` — or the user explicitly requests it regardless of confidence/sightings.
   - **Verb**: propose a `references/` card draft (new file) or an existing-card update that **anchors, never copies wholesale** — pointers into the wiki source file(s) plus `file:line` anchors into the affected oms surfaces (skills/agents/other reference cards), following the "no duplicate embedding — reference the SSOT" card discipline (`references/writing-craft.md:3`). The proposal states what changed and why; it does not paste wiki prose verbatim into the card.
   - **Dev-mode guard**: write the proposed card to disk ONLY when the plugin root's `.git` exists — an **existence check (file or directory), explicitly not `isdir`** — because a linked git worktree's `.git` is a plain gitfile (a `gitdir: …` pointer, not a directory, including the very worktree this step runs in), and an `isdir`-only check would silently degrade every worktree dev session to proposal-only. When `.git` is absent in any form (e.g. a marketplace install with no dev checkout), emit the proposed card as text only, for the human to carry elsewhere — never write.
   - **Gate**: mandatory, no exception — reuses the core promotion gate's approval discipline (`:47`). Present the proposed card draft/diff with its anchors for a promote/hold/edit/abort decision. No proposed card is written without a human gate decision, no matter how high confidence or how many sightings.
   - **Citation/.bib permanently excluded**: identical invariant to §6.F — a proposed card MUST NOT include citations, `.bib` entries, or specific-paper citation content. Reject such clusters from this verb entirely; citations stay only in the paper-slug's own `.bib` SSOT.
7. **Follow-up guidance**: since the defaults changed, advise that scholar-outline will lay down the new defaults starting from the next work on that venue. Advise checking specificity↔origin consistency via scholar-verify's venue meta-consistency check (H10). learn itself does not touch paper content.
</Steps>

<Output>
- scholar-inspector's **promotion proposal diff** (Added/Changed defaults) + scope + provenance table (each default → learned.md observation id) + specificity-change rationale + human decision list.
- GATE decision history (promote/hold/edit/abort).
- On passing the gate: updated `venues.md` (learned_refs[]·origins·specificity) + path to the marked learned.md.
- Held-candidate list (re-evaluated at the next learn) + "scholar-verify meta-consistency check recommended" advisory.
- Note that the inspector does not self-approve — promotion was broken by the human gate, and compliance judgment is the job of a separate context (scholar-verify). Confirm that citation/.bib were not promotion targets (§6.F).
</Output>

<Citation_Safety>
⚠️ A core invariant of oms identity. scholar-learn **never** does the following:
- Promote a citation, .bib entry, or "cite this paper" type into a venue default (target enum rejects it, §6.F).
- Recover observations via embedding/similarity search (deterministic grep only, §6.A).
- Fill the ≥3 bar with fabricated evidence (only real paper-slug/events, §6.E).
The promotion targets are *structure, ordering, format, and working-method specs* only. Citations are not learned.
</Citation_Safety>
