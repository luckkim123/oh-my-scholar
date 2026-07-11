---
name: scholar-draft
description: |
  Turn an approved outline + concept notes (.md) into a paper .tex draft — single delegation to scholar-drafter.
  Citation-bound, so generation is single and careful, NEVER parallel. No fabricated citations; confirm before editing .bib.
  Triggers: 초안 써, draft 써줘, 섹션 작성, .tex 써, 논문 본문 써, 초고 작성, write the draft, 섹션 초안
---

# scholar-draft — Paper draft writing (.tex)

<Purpose>
Convert an approved outline and concept notes (.md SSOT) into a paper .tex draft. Single delegation to scholar-drafter (the only writer with write access). The "function implementation" of code. Draft only after ideate (.md) is complete — do not write the paper before the concepts are settled.
</Purpose>

<Use_When>
- The outline is GATE 1-approved and it is now time to write the .tex body
- Concept notes (methodology/*.md) are ready
- Drafting/rewriting one section at a time
</Use_When>

<Do_Not_Use_When>
- No outline yet → scholar-outline first
- Concepts not yet settled in .md → scholar-ideate first (concept-first principle)
- Fixing an existing draft until it passes → scholar-revise
- Want critique only → scholar-inspect / verification only → scholar-verify
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Generation is single and careful, NEVER parallel** — even multiple sections go through one drafter serially. No parallel drafter dispatch (amplifies citation hallucination).
- ⚠️ **No fabricated citations** — a new \cite goes only to a verified .bib entry. If unverified, rewrite the claim or flag it to the human; never invent it.
- ⚠️ **.md SSOT first** — if the .tex requires a claim not in the notes, stop and go back to ideate/research.
- Version snapshot before large edits — into `.oms/<slug>/versions/` as `v{NN}_{date}_{summary}.tex` (fixed workspace path, `references/output-layout.md` SSOT). Keep the .tex/.bib source originals in the project source folder; only snapshots go to `.oms/`.
- The drafter must not self-approve — after drafting, go through scholar-inspect/verify as a separate pass.
</Execution_Policy>

<Steps>
1. Check the outline (planner output) and concept notes (.md). If missing, stop → point to the prerequisite skill.
2. Confirm the writing scope (sections).
3. Single delegation via `Task(subagent_type="oh-my-scholar:scholar-drafter", ...)`:
   - Input: outline, concept-note paths, scope sections, existing .tex/.bib, latex.md card (style)
   - Instructions: one section at a time serially, every \cite only to a verified .bib, flag unverified citations, snapshot to `.oms/<slug>/versions/` before large edits, emit `% [MATERIAL GAP: …]` at any site whose grounding material is absent (never infer plausible content).
4. Receive drafter output — written files + list requiring human confirmation (unverified citations / fixable_by_llm=false).
5. **Verification is separate** — hand off to scholar-verify/inspect (no self-approve here).
</Steps>

<Output>
List of .tex/.bib files the drafter wrote (project source folder) + snapshot location (`.oms/<slug>/versions/`) + list requiring human confirmation (unverified citations, etc.) + MATERIAL GAP token list (if any) + "ready to hand off to scholar-verify" (explicitly no self-approve).

⚠️ **Completion condition — .tex↔.oms sync (`references/learning-protocol.md` §8)**: if the draft made a **structure-affecting change** relative to the outline (new/moved section, title change, introduction of a major equation, added \cite), then **within the same task** update `.oms/<slug>/outline/outline.md` (section tree, citation-dependency mapping) and the relevant `.oms/<slug>/methodology/*.md` (reflected concepts, equations) so they match the current .tex. Pure prose proofreading (no structural change) does not require an update. If you skip the update the outline goes stale, and the next inspect/verify will misjudge against the old structure — no drift.
</Output>
