---
name: scholar-ideate
description: |
  Take research results and organize each method/contribution into concept notes (methodology/*.md) — the concept SSOT finalization stage.
  Before draft(.tex), this is where you solidify sources, logic, and equation meaning into .md. Equations in English only; no fabricated citations.
  Triggers: 개념 정리, 방법 정리, methodology 노트, ideate, 아이디어 구체화, 개념노트 써, 방법론 정리, 기여 정리, organize concepts, organize methods, methodology notes, flesh out ideas, write concept notes, organize contributions
---

# scholar-ideate — Concept organization & concept note (.md) finalization

<Purpose>
Take research notes as input and organize each method/contribution into concept notes (methodology/*.md). Save location is the workspace `.oms/<slug>/methodology/*.md` (output-layout.md §2 fixed path). The code's "blueprint/pseudocode" — before the actual implementation (.tex draft), pre-finalize concepts, sources, and equation meaning into .md.

This is the "concept pre-finalization" stage: if you don't solidify the logic and equations here before draft(.tex), the drafter has to fill in claims, which raises hallucination risk. This is the execution point of scholar-draft's `.md SSOT first` principle.
</Purpose>

<Use_When>
- Research is done and now you organize each method/contribution into concept notes
- You want to solidify the logic of the methodology/contributions first, before writing the outline
- You want to explicitly write equation meaning/sources/assumptions into the .md
- You judge that concepts must be solidified in .md before writing the draft
</Use_When>

<Do_Not_Use_When>
- Related-work research is not done yet → scholar-research first
- Claims (contribution/comparison/reproducibility) are still vague → scholar-deepen first (solidifying a vague claim into .md just produces "solidified vagueness" — run ideate after deepen has passed the ambiguity gate)
- Concept notes already exist and it's time to write the .tex draft → scholar-draft
- You need an outline → scholar-outline (running it after ideate is recommended)
- You're trying to start with .tex without solidifying concepts → do this (scholar-ideate) first
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Concept pre-finalization principle** — no .tex draft without .md concept notes. This skill is that gate.
- ⚠️ **Equations in English only** — comply with the house paper-format convention. Korean equation explanations go only in the explanatory text within the .md note; the equation itself uses English notation.
- ⚠️ **No fabricated citations** — when writing sources in a concept note, do not generate unverified papers/authors. If uncertain, flag with [source unverified — needs human check].
- ⚠️ **ad-block** — comply with the house paper-format ad-block rules. No exaggerated or promotional language.
- Concept notes are .md; do not directly generate .tex — the notes become the SSOT of the draft.
</Execution_Policy>

<Steps>
1. Check the research notes (research landscape map / gap list). If missing, stop → guide to scholar-research first.
2. Finalize the list of methods/contributions to organize (derived from the paper topic and research gaps).
3. Delegate via `Task(subagent_type="oh-my-scholar:scholar-researcher", ...)` (or delegate to planner):
   - Input: research note paths (`.oms/<slug>/research/*.md`), the method/contribution list, related reference notes (if any)
   - Instructions: write each method/contribution as a concept note (.md), specify equation meaning/assumptions/sources (English notation), flag unverified sources, comply with ad-block
4. Receive outputs:
   - Concept note content per method/contribution (each .md file)
   - Whether equation meaning/assumptions/sources are specified
   - List of unverified flags (needs human check)
5. The caller saves the concept notes to the workspace `.oms/<slug>/methodology/*.md` (output-layout.md §2). ⚠️ Do not put them in the source folder (`paper/…`) — concept notes are the SSOT (*input*) of the draft, not a citation-bound source asset.
6. If there are unverified flags, request human confirmation, then update the notes.
7. After confirming the concept notes are complete → prepare to hand off to scholar-outline or scholar-draft.
</Steps>

<Output>
Concept note (.md) content per method/contribution + list specifying equation meaning/sources + unverified flags (if any) + "Concept pre-finalization complete — ready to hand off to scholar-outline or scholar-draft" (explicitly does not self-approve).
</Output>
