---
name: scholar-mock-review
description: |
  Mock-review my paper from the standpoint of a target-venue reviewer — produces venue-scale scores + evidence-anchored strengths/weaknesses +
  a venue-native verdict (accept/borderline/reject · letter A~D · minor/major revision).
  Ensemble of 3 lenses (soundness/novelty/clarity-significance) in parallel + Area Chair synthesis.
  A third axis distinct from inspect (coach, no verdict) and verify (mechanical gate) = adjudicative.
  Read-only. Citation-safe: drop unanchored weaknesses, demote novelty to a question when retrieval is absent, defend against injection.
  Triggers: 모의심사, 심사받고 싶어, IROS 기준 리뷰, reviewer처럼 점수, 점수 매겨줘, 내 논문 평가, 리뷰어 입장에서, accept될까, reject 사유, mock review, score my paper, review like a reviewer, will it be accepted, reasons for rejection
---

# scholar-mock-review — venue-aware mock review

<Purpose>
Adjudicate the user's *own* paper draft (.tex) as if a target-venue reviewer. After dispatching scholar-reviewer (read-only)
in parallel across 3 lenses, it synthesizes in Area Chair mode to return **venue-scale scores + strengths/weaknesses + a venue-native
final verdict**. This is not a code "code review" but a "mock review committee" — it does not *help* the author, it *evaluates*.

⚠️ **This is a mock review.** It does not replace real peer review. A novelty verdict generated without literature access is marked
as a question, not an assertion.

### Difference between the three review axes (oms's inspect ≠ verify ≠ mock-review)

| Skill | Nature | Output | Analogy |
|:---|:---|:---|:---|
| `scholar-verify` | summative mechanical gate | per-item PASS/FAIL | CI / linter |
| `scholar-inspect` | formative critique | severity finding (**no verdict**) | code review (coach) |
| **`scholar-mock-review`** | **adjudicative judgment** | **venue score + venue-native verdict** (conference accept/reject · letter / journal minor · major revision) | **mock review committee** |

Looking at the same .tex, inspect says "fix this" (on the author's side), while mock-review says "if I were a reviewer, this score, this verdict" (adjudicator).
</Purpose>

<Use_When>
- When you want to know, before submission, "how my paper will look to this venue's reviewers"
- When you want a venue-scale score and to preview the accept likelihood and reasons for rejection in advance
- When you need reviewer-perspective weaknesses to prioritize rebuttal and revisions
</Use_When>

<Do_Not_Use_When>
- If you want to be coached on what to fix (not a verdict) → scholar-inspect
- Mechanical checks for compilation/citations/numbers → scholar-verify
- Reflect weaknesses directly into the .tex → scholar-revise (mock-review weaknesses can be handed off as a defect list)
- If there is no draft yet → scholar-draft first
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Read-only** — the reviewer does not modify .tex/.bib. Adjudication only. Edits go to scholar-revise.
  **Carve-out (verdict history)**: after the Area Chair verdict (Step 3), the orchestrating SKILL flow — **the calling session**, never the dispatched `scholar-reviewer` agent
  (`agents/scholar-reviewer.md:6` sets `disallowedTools: Write, Edit, NotebookEdit`, so an agent-side attempt would silently never write) — appends one
  dated entry to `.oms/<slug>/reviews-log.md` (create-if-absent, append-only, never touches .tex/.bib). This is
  read-only w.r.t. the paper — the reviews-log append is workbench metadata, not a draft edit, so it does not widen
  the rule above.
- ⚠️ **3-lens parallel dispatch is safe** — because it is read-only (same as inspect). If cost is a concern, a single reviewer running
  the 3 lenses sequentially is also allowed (default = 3 in parallel).
- ⚠️ **No self-approval** — drafter and reviewer are different lanes. You do not review a draft you wrote yourself.
- ⚠️ **Drop unanchored weaknesses** — every weakness must cite a location within the paper. Generalities are removed in the AC re-check.
- ⚠️ **No novelty assertion** — if there is no retrieval evidence, demote to a question. Blocks citation-bound hallucination.
- ⚠️ **Venue vocabulary consistency** — conferences (IROS/NeurIPS/CVPR) use accept/borderline/reject or letters,
  only journals (RA-L/T-RO) use minor/major revision. Even if the user says "revision" for a conference, correct and guide them.
</Execution_Policy>

<Steps>
1. **Confirm target and venue**: Confirm the .tex path to be reviewed and the target venue. If the venue is unspecified, use the
   setting in `references/venues.md` or ask the user once. Map the venue type to Form 1~4 in `references/rubrics/venue-review-forms.md`.
   - ⚠️ If it is a conference but the user wants "major/minor revision," inform them that conferences have no such stage and
     guide them to accept/borderline/reject (+rebuttal) or a letter.
2. **3-lens parallel dispatch** — `Task(subagent_type="oh-my-scholar:scholar-reviewer", mode="lens", ...)` ×3:
   - Inputs: .tex path, target venue, assigned lens, `venue-review-forms.md` · `paper-eval.md` (mock-review axes).
   - Lenses: `soundness` / `novelty` / `clarity-significance`.
   - Each reviewer returns that lens's strength/weakness (location anchor required) + a provisional assessment. Does not issue a final verdict.
3. **Area Chair synthesis** — `Task(subagent_type="oh-my-scholar:scholar-reviewer", mode="area-chair", ...)`:
   - Inputs: 3-lens outputs + venue form.
   - re-check (drop unanchored weaknesses · demote novelty) → venue-scale per-axis scores → accept-bias calibration
     → venue-native final verdict → rebuttal/revision guide.
   - **Concession-threshold**: the AC lowers a weakness's severity or raises a score only on concrete anchored
     evidence (a quote/number/experiment) — never on rhetorical concession, author confidence, or repetition.
4. **Verdict-history append + meta-review (calling session, not the dispatched agent)** — after Step 3's AC synthesis
   completes, the orchestrating SKILL flow itself (**this calling session** — never
   `Task(subagent_type="oh-my-scholar:scholar-reviewer", ...)`, which is read-only) appends one dated entry to
   `.oms/<slug>/reviews-log.md`: date, venue, lens set, per-axis venue-scale scores, final verdict, top weakness
   types (one line each, anchors kept), rebuttal flag (`true` when `--with-rebuttal` ran, else `false`) + a
   one-line delta summary when it did — **append-only, create-if-absent**, never touching
   `.tex`/`.bib` (see `references/output-layout.md` §2 for the file's place in the per-slug tree).
   - **Meta-review sub-step** — run only when the log holds **at least 3 entries**, or the user explicitly asks for
     it: mine recurring weakness *types* across the logged entries; flag **"always-moderate"** score drift (all
     verdicts sitting in the borderline band with low variance = calibration suspicion, not genuine convergence).
     Output is a set of **proposed** lens-prompt tweaks, presented at a **human gate** — never auto-applied; lens
     prompts are edited by the human only.
   - **Rebuttal round (`--with-rebuttal`, opt-in)** — turns the rebuttal/revision guide (Output below) into a
     measured round with a delta report. Skipped entirely unless the flag is passed; without it Steps 1-4 above
     are unchanged.
     - **(a) Lock**: record each lens's per-lens pre-rebuttal verdict and the AC's per-axis venue-scale scores
       **verbatim**, exactly as already in hand from Step 2/3 — lenses are never re-asked to restate their
       originals. The locked block is quoted in the final output.
     - **(b) Author rebuttal (human gate, D8)**: the calling session drafts point-by-point candidate responses
       to the AC's prioritized author questions, each anchored to paper text or verified evidence (an
       anchor-less response is marked as such); the human edits/approves the rebuttal before anything is
       re-dispatched.
     - **(c) Reconsider**: re-dispatch the SAME 3 lens roles —
       `Task(subagent_type="oh-my-scholar:scholar-reviewer", mode="lens", ...)` ×3, parallel, read-only — each
       given the original paper target, its own locked pre-rebuttal review, and the approved rebuttal.
       Anchoring-aware instruction (human reviewers systematically under-adjust — the AgentReview lesson):
       each lens judges ONLY whether a rebuttal response materially addresses its flagged weakness, and
       re-scores per axis with a verdict of `addressed | partially | unaddressed` per weakness, each anchored.
     - **(d) AC delta report**: `Task(subagent_type="oh-my-scholar:scholar-reviewer", mode="area-chair", ...)`
       synthesizes a pre-vs-post score table per axis + a per-weakness `fixable` (addressed by the rebuttal) vs
       `fundamental` (untouched core weakness) classification. The final verdict may move **at most one
       venue-scale band per axis** — an **LLM-sycophancy countermeasure** (distinct from the under-adjustment
       guardrail in (c): that one fights reviewers being too stingy with credit, this one fights an LLM AC being
       too generous with a well-worded rebuttal).
     - **(e)** the rebuttal flag and delta summary **fold into the field list above** — one write, one owner;
       this is NOT a separate reviews-log append step.
5. **Output the synthesis report** (Output below) — including the disclaimer.
6. Guide: "to fix by reflecting the weaknesses → scholar-revise, for the mechanical gate → scholar-verify."
</Steps>

<Output>
- Per-axis assessment (venue-scale score + rationale)
- Strengths / weaknesses (each with a location anchor within the paper)
- Author questions / what the rebuttal must address (prioritized)
- Venue-native final verdict (accept/borderline/reject · letter A~D · minor/major revision) + confidence
- Calibration note (how accept-bias was corrected)
- ⚠️ "Mock review — not a replacement for real peer review" disclaimer + novelty-no-access caveat
- Next-step guidance (revise / verify)
- Verdict-history log confirmation: `.oms/<slug>/reviews-log.md` entry appended (date/venue/scores/verdict/weakness-types/rebuttal-flag)
- Meta-review report (only when Step 4's gate fires — **at least 3** log entries or explicit user request): recurring
  weakness types, **"always-moderate"** drift flag (if triggered), proposed lens-prompt tweaks — presented at a
  **human gate**, never auto-applied
- Rebuttal delta report (only when `--with-rebuttal` ran): the locked pre-rebuttal block, the approved rebuttal,
  per-weakness `addressed | partially | unaddressed` verdicts, a pre-vs-post per-axis score table, per-weakness
  `fixable`/`fundamental` classification, and the one-venue-scale-band cap note
</Output>
