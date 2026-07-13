---
name: scholar-inspect
description: |
  Formative critique of a .tex draft — finds improvement points through two lenses, logic and prose, and returns them.
  Judgment-style code review. Does NOT issue PASS/FAIL — that is scholar-verify's job.
  Read-only, so parallel inspector dispatch is possible.
  Triggers: 검토해줘, 비평, 리뷰해줘, 개선점, inspect, 피드백, 논리 봐줘, 문체 봐줘, review, critique, feedback, check logic, check prose
---

# scholar-inspect — formative critique of a paper draft

<Purpose>
Run a code review on a drafted .tex. Delegates to scholar-inspector (read-only) to find improvement points through two lenses, logic and prose, and returns them. The "code review" of code — judgment-style, not a mechanical gate.

⚠️ **Does not issue PASS/FAIL.** If your goal is a pass/fail verdict, use scholar-verify. What comes out here is a severity-classified list of improvement points; the final judgment is made by a human.
</Purpose>

<Use_When>
- After draft/revise, before submission, when you want logic and prose improvement points critiqued
- When you want contribution-evidence correspondence, structural logic, academic prose, and overclaiming checked
- When you need severity-classified feedback to prioritize revisions
</Use_When>

<Do_Not_Use_When>
- If you need a pass/fail gate verdict → scholar-verify
- If you want to apply the critique results directly to the .tex → scholar-revise
- If there is no draft yet → scholar-draft first
- If the concepts are not yet settled in .md → scholar-ideate first
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **No PASS/FAIL verdict** — if the inspector uses gate language like "pass," "fail," or "reject," this separation collapses. A finding must be only severity (critical/important/minor) + an improvement suggestion.
- ⚠️ **Read-only** — the inspector does not modify .tex/.bib. Critique only.
- ⚠️ **No self-approval** — the drafter and the inspector are different lanes. You do not inspect a draft you wrote yourself.
- Since logic and prose are independent, dispatching inspectors in parallel is safe (read-only).
- For fixable_by_llm=false items (missing experiments, contribution-scope changes, etc.), do not attempt automatic fixes — human flag only.
</Execution_Policy>

<Steps>
1. **Read the SSOT first (required, `references/learning-protocol.md` §8)** — do not critique by looking only at the .tex. For the logic lens to judge "contribution-evidence correspondence," it must know *what this paper's true contributions, chapter axis, and section placement actually are* from the primary SSOT. Before critiquing, you must read `.oms/<slug>/outline/outline.md` (current section structure, story arc, contribution mapping) and `.oms/<slug>/methodology/*.md` (the source and meaning of each method and equation) to grasp the current state. The `research_summary/` and code_survey notes are only secondary aids — they are not the authority for chapter-axis and scope judgments (they can go stale through structural redesign). If you skip the SSOT, you will misjudge against outdated notes.
2. Confirm the target .tex file path and the critique scope (whole document or a specific section).
3. Delegate via `Task(subagent_type="oh-my-scholar:scholar-inspector", ...)` (logic and prose can be dispatched in parallel):
   - Inputs: .tex file path, critique scope, **current outline and methodology SSOT paths (the ones read in §1)**, paper-eval.md rubric (inspect axes), latex.md card
   - Instructions:
     - **logic lens**: contribution-evidence correspondence (against the current outline), structural logic, baseline comparison, devil's advocate
     - **prose lens**: academic prose, overclaiming discipline, repetition, transitions, sentence length
     - Each finding: severity (critical/important/minor) + location (.tex section, line) + issue + evidence (quote from the .tex source) + suggestion + fixable_by_llm (true/false)
     - Do not output a PASS/FAIL verdict
4. Receive the inspector's output — collect the finding list.
5. Output a summary: number of findings per severity + critical items listed first + fixable_by_llm classification.
6. Guidance: "If you want to apply fixes → scholar-revise; if you want a gate verdict → scholar-verify."
</Steps>

<Output>
- Finding list (severity · location · issue · evidence · suggestion · fixable_by_llm)
- Per-severity counts (critical N / important N / minor N)
- fixable_by_llm=false items → list requiring human confirmation
- Next-step guidance (revise / verify)
- ⚠️ No PASS/FAIL verdict — the judgment is the human's.
</Output>
