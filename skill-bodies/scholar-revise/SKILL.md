---
name: scholar-revise
description: |
  A revise-verify loop on a paper until verify gives a PASS — the paper-edition of ralph. Treats the defect list like a PRD and
  repeats drafter (revise) and verifier (verify) until the `passes:true` gate. Stops and reports if the same defect recurs 3 times.
  ⚠️ "Content generation" defects must NOT be auto-fixed (single, careful pass). Triggers: 통과까지 고쳐, 다 잡아줘,
  검증 통과할 때까지, revise until pass, fix until verified, 수정 루프, 리비전 돌려
---

# scholar-revise — revise-verify loop (paper-edition of ralph)

<Purpose>
Revise the paper until scholar-verify gives a PASS. The paper-edition of OMC ralph: treat defects like a PRD (acceptance criteria) and repeat drafter (revise) and verifier (verify) on fresh evidence until the `passes:true` gate. Not "do your best" but *guaranteed gate passage*.
</Purpose>

<Use_When>
- draft/inspect/verify are done and you want to clear the FAIL items in an automatic loop
- "fix it until it passes on its own", "catch them all" type requests
</Use_When>

<Do_Not_Use_When>
- If it's a new draft → scholar-draft
- If you only want advice → scholar-inspect (does not revise)
- ⚠️ **Content generation defects** like citations and contributions must NOT be run through the automatic loop — have the drafter handle them in a single, careful pass, with human confirmation. The revise loop is only for fixable_by_llm=true (text restructuring, compile errors, reference consistency) defects.
</Do_Not_Use_When>

<Execution_Policy>
- Treat the defect list like a PRD: each defect is an acceptance criterion, `passes:true` is when the verifier gives that item a PASS.
- Each iteration: drafter revises (fixable_by_llm=true only) → verifier re-verifies on **fresh evidence** (no reuse of a prior verification).
- **Do not manufacture a PASS by reducing scope, inserting placeholders, or bypassing checks** (ralph: no scope reduction, no deleting tests, no faking).
- drafter and verifier are **different lanes** — no self-approval.
- **Same defect recurs 3 times → stop and report a "fundamental issue"** (block infinite loops). Mechanical, not self-report: each recurrence runs `strike --defect-id <id>`, and `third_strike: true` in its output IS the stop condition — countable by grep, not self-report.
- When the max iterations (venue max_review_rounds, default 5) are exceeded, stop and report the current state. Mechanical: `scripts/oms_state.py revise-round --slug S` increments the round counter and mints a fresh `round_id`; `"exceeded": true` in its output is the max-rounds signal (the CLI never blocks — the SKILL decides to stop).
- ⚠️ fixable_by_llm=false (missing experiments/figures, contribution scope, unverified citations) are not put in the loop → escalate to a human.
- ⚠️ **Full structure-regression re-verify right after a PASS**: when one round makes everything passes:true, do not terminate immediately — verify once more, in full, *whether this revision broke the global consistency of other sections* — i.e. whether `\ref`↔`\label`, `\cite`↔.bib, body↔table/figure numbers broke *outside the section you revised*. Fixing one place can throw off other \ref numbers, citation consistency, or numeric sums (global side effects of a local fix). If anything broke, put that item back into the loop as a new defect.
  - ==A distinct axis from the existing score-regression (avoid confusion)==: the `score-regression (quality-score drop > venue regression_threshold)` in Steps 3c below is the **quality-score drop** axis (a guard that *stops* the loop). This new clause is the **structural-consistency regression** axis (broken global consistency of references, citations, numbers) — a *different kind*: mechanical consistency rather than a score, and it does not stop but puts the broken item back into the loop. The two axes are checked independently.
</Execution_Policy>

<Steps>
1. Current state: `Task(subagent_type="oh-my-scholar:scholar-verifier", ...)` → list of FAIL items = PRD. At loop start, run `scripts/oms_state.py revise-start --slug S --max-rounds <venue max_review_rounds>`. `revise-start` is idempotent — after a crash or compaction it resumes the live marker with its counters intact; pass `--force-restart` only when the human explicitly starts a fresh loop (never to "clean up" a resumed one).
2. Classify by fixable_by_llm: true → loop targets, false → human-escalation list.
3. **Loop** (each round):
   a. Round start: run `scripts/oms_state.py revise-round --slug S` — mints a fresh `round_id`; carry it into both Task prompts below (T4 wires the verifier echo). If the output has `"exceeded": true`, stop and report (mechanical max-rounds, replaces self-counting — the CLI never blocks, the SKILL decides to stop). Revise: `Task(subagent_type="oh-my-scholar:scholar-drafter", ...)` — fixable=true items only, single careful pass, snapshot before a large revision.
   b. Re-verify: `Task(subagent_type="oh-my-scholar:scholar-verifier", ...)` — fresh evidence, in full. Include the current `round_id` (from `revise-round`) in the verifier Task prompt, and accept the verdict only if the echoed Round ID matches — a mismatched or missing echo means a stale/crossed verdict: discard it and re-verify (do not count that round).
   c. All passes:true → **full structure-regression re-verify** (whether \ref/\cite/numeric global consistency broke outside the revised section). If any item broke, put it back into (a) as a new defect; if none, terminate. Otherwise, check whether the same defect recurs:
      - Same defect re-appears in a new round's FAIL list → run `strike --defect-id <id>` — `third_strike: true` in its output IS the 3-strike stop condition, countable by grep, not self-report. Same defect for the 3rd time → stop and report a "fundamental issue". Never call `strike` for fixable_by_llm=false (citation/content) defects — those never enter the loop at all.
      - score-regression (quality-score drop > venue regression_threshold) → stop and report. (a distinct axis from structure-regression)
      - Otherwise → go to (a).
4. Terminate on PASS (+ passing the structure-regression) or a stop condition. Present GATE 2 (confirm the review result — human). Every exit path (PASS, 3-strike, max-rounds, regression stop, human abort) runs `scripts/oms_state.py revise-end --slug S --status done|stopped|abort` — a live marker with no loop is what the Stop guard (T3) treats as "the loop is still running", so ending the loop without `revise-end` leaves the session guarded.
</Steps>

<Output>
The PASSed .tex/.bib + iteration history (each round's FAIL→revision summary) + final verify evidence table + human-escalation list (fixable=false, unverified citations).

⚠️ **Completion condition — .tex↔.hq synchronization (`references/learning-protocol.md` §8)**: if the revise loop made **changes that affect structure** relative to the outline (section moves, merges, splits, title changes, major equation replacements, \cite additions) — section merges and splits are common during a revise loop — then after the PASS, **within the same task**, bring `.hq/work/scholar/<slug>/outline/outline.md` and the relevant `.hq/work/scholar/<slug>/methodology/*.md`, plus the decision record (if something like `.hq/work/scholar/<slug>/outline/SECTION_REVIEW_DECISIONS.md` exists, a block there on what changed and why), into agreement with the current .tex. "revise PASS" is only granted once this synchronization is done. Skipping it leaves .hq stale, so the next session's draft/inspect will misjudge against the old structure — no drift.

Or a stop report (same defect 3 times / regression / max iterations exceeded + remaining defects).
</Output>
