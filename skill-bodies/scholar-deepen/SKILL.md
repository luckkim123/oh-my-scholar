---
name: scholar-deepen
description: |
  A qualitative stage that gates the *ambiguity* of claims right after research — judging, dimension by dimension, whether
  contribution/method-evidence/comparison/reproducibility are clear, and pressuring them with a challenge round when ambiguous. After passing (all clear + human approval), proceed to ideate.
  A qualitative gate with no numeric weighted sum or threshold. No citation fabrication; unverified citations get a citation-fragile flag.
  Triggers: 주장 명확히, 모호성 점검, deepen, 기여 또렷하게, 무엇을 주장하는지, 깊이 파보자, deepen gate, clarify the claim, ambiguity check, sharpen contribution
---

# scholar-deepen — Claim Ambiguity Gate (qualitative)

<Purpose>
*Right after* research builds a verified citation map, and *before* ideate solidifies the concept SSOT, this gates whether **what the paper claims** is stable. It corresponds to the code-development step of "preventing handoff to design while requirements are still ambiguous."

Why deepen comes before ideate: if you solidify an ambiguous claim into a concept note (.md), it becomes "solidified ambiguity." Resolving ambiguity must precede fixing the concept SSOT. The triple gate (deepen/ideate/outline-GATE1) each checks a different thing — deepen=claim ambiguity / ideate=concept SSOT / outline GATE 1=human approval of structure.

This is a **qualitative gate**. It does not convert ambiguity into a number (weighted sum, threshold, stability_ratio) — whether a paper's contribution is sharp cannot be judged by a magic number, and a qualitative judgment is more honest.
</Purpose>

<Use_When>
- When research (research map, gap, verified citations) is done and you want to check whether the claim is sharp before solidifying concepts
- When there are several contributions but which one is core keeps shifting
- When "what does this paper really claim" cannot be stated in a single sentence
- When, as for top-tier submissions, the sharpness of the claim is what separates a reject
</Use_When>

<Do_Not_Use_When>
- If research is not yet done → scholar-research first (deepen presupposes a verified citation map)
- If the claim is already sharp and it is time to solidify concepts into .md → scholar-ideate
- If it is time to set the structure (sections, arc) → scholar-outline
- If the user explicitly stated `--skip-deepen`, or the 4 dimensions are self-evidently clear → pass it through and go to ideate
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Qualitative gate — no quantification**: the per-dimension judgment is a qualitative "clear / ambiguous" judgment. Do not introduce magic numbers like an ambiguity score weighted sum, threshold, or stability_ratio.
- ⚠️ **No citation fabrication + strengthened citation safety**: no agent in the challenge round guesses the *content* of a citation. It references "only citations within the researcher-verified list." A claim that depends on an unverified citation is flagged separately as **citation-fragile** (human check) — it is not used in a pass judgment.
- ⚠️ **Passing requires human approval**: even if every dimension is "clear," do not auto-pass to ideate without the human's explicit approval.
- ⚠️ **Math in English only** (paper format rule — per the `references/formats/latex.md` card, common across domains). Korean explanations go only in the .md note text.
- The output is .md (a record of the qualitative judgment) — do not generate .tex directly. Since the research notes serve as the trace, no separate `.omc/specs` output is produced.
</Execution_Policy>

<Steps>
1. Confirm inputs: confirm the research map (gap, verified citation list) and the contribution the user stated. If absent, stop → scholar-research first.

2. **Round 0 — Topology**: lock the paper's top-level components (commonly 3-6):
   - contributions (the list of claimed contributions)
   - core sections (method / experiment)
   - experiments (the empirical evidence backing each contribution)
   This topology must be fixed first to prevent depth-first digging into one branch and obscuring its siblings.

3. **Per-dimension clear/ambiguous qualitative judgment** (4 dimensions, no numbers):
   - **Contribution clarity**: is the contribution sharp in a single sentence? Are several contributions mixed so that the core is blurred?
   - **Method-evidence binding**: which experiment/analysis backs each method? Any floating claims?
   - **Comparison clarity**: superior compared to what? Is the baseline sharp and fair?
   - **Reproducibility clarity**: can what is needed for reproduction (data, code, hyperparameters, environment) be specified?
   Judge each dimension as "clear / ambiguous." ==**If one or more is 'ambiguous', trigger the corresponding challenge round**==.

4. **Challenge agents** (for ambiguous dimensions, one prompt each — delegated or direct):
   - **Round 4 Contrarian**: "What if the opposite of this contribution were true? What if the baseline were already sufficient? Could the paper do without this contribution?"
   - **Round 6 Simplifier**: "If you kept only 1 core contribution out of 3? If you ran only half the experiments, what would you drop?"
   - **Round 8 Ontologist**: "What *is* this paper really? Which entity's naming is shaky? Are you calling the same thing by different names?"

5. **Soft limits** (since it is qualitative, soft instead of a hard threshold):
   - at round 3, if all 4 dimensions are clear, early exit is allowed.
   - upon reaching round 10, a soft warning ("ambiguity is not resolving fast — time to reconsider the topic itself").
   - round 20 hard cap (beyond this is a problem deepen cannot resolve — escalate to the human).

6. **Citation safety check**: confirm that every citation relied on during judgment and challenge is within the researcher-verified list. Collect unverified dependencies as citation-fragile flags.

7. **Pass judgment**: all dimensions "clear" → **request deepen pass approval** from the human (proceed/keep challenging/abort). Hand off to ideate only after the human says proceed.

8. **3-point injection (ideate handoff)**: when handing off to ideate, inject three things:
   - enriched initial_idea (the contribution statement sharpened by deepen)
   - research note wrap (the verified citation map)
   - missing-citation / critical-unknown as questions for ideate's first 1-3 rounds
</Steps>

<Output>
Round 0 topology (lock contributions/sections/experiments) + the 4-dimension qualitative judgment table (clear/ambiguous) + the output of the triggered challenge rounds + the citation-fragile flag list (or "none") + round count + **request for deepen pass approval** (proceed/keep/abort, explicitly stating no self-approval). On pass: the 3-point injection bundle for the ideate handoff.
</Output>
