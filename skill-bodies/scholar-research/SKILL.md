---
name: scholar-research
description: |
  Survey the related-work / prior-art landscape and identify gaps → produce a .md research note.
  Citation-bound, so citation verification is enforced and fabrication is prohibited. Parallel reading is OK; citation generation only after verification.
  Triggers: 관련연구 조사, related work, 선행연구, gap 찾아, 문헌조사, 리서치 해줘, 연구 지형, survey, 논문 조사
---

# scholar-research — Related-Work Survey & Gap Identification

<Purpose>
Systematically survey the related-work landscape before writing a paper and identify gaps. Delegate to scholar-researcher to produce verified citations, a research map, and a gap list as a .md research note. The code-equivalent of "requirements gathering" — the stage where you first build up the evidence for what to do and why.
</Purpose>

<Use_When>
- When you need a related-work map and gaps before starting a paper
- When you need substantive prior-art research before writing a related-work section
- When you want to systematically organize the limitations of existing methods
- When you need to secure supporting material ahead of ideate/outline
</Use_When>

<Do_Not_Use_When>
- If an outline already exists and it's now time to organize concepts → scholar-ideate
- If a draft exists and it's time to directly write the related-work section → scholar-draft
- If you're verifying the equations/claims of a specific paper → scholar-verify
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **No citation fabrication** — enforced by the researcher agent. Never generate non-existent papers, authors, or years. Leave unverified sources as flags and ask a human to confirm.
- ⚠️ **Parallel reading is OK, but parallel citation generation is prohibited** — reading and analyzing multiple sources at once is allowed. However, if multiple agents generate the citation entries themselves in parallel, hallucination is amplified.
- ⚠️ **passage-level grounding** — do not build citations from the abstract alone; ground them in the cited text span (the full passage). The abstract-only condition produces more hallucination than passage-level ([arXiv:2309.06365](https://arxiv.org/abs/2309.06365), self-verified). The structural reason that separating research (search) → draft (generation) reduces knowledge-hallucination ([arXiv:2510.24476](https://arxiv.org/abs/2510.24476)). Full external landscape: global wiki `reference/llm-paper-writing-landscape.md`.
- Quote anchors are the mechanical substrate of verify's claim-faithfulness (citation-misuse) check — a claim row without its quote can only be checked by a human.
- `citation_lookup()`'s abstract-function contract (signature, deterministic-lookup rule, today's implementation target, MCP swap-points) lives in `references/wiki/README.md`, adjacent to `wiki_query()`.
- Optional `refs/*.pdf` batch intake (GROBID-based, proposes never commits) is documented at `references/grobid-intake.md` — absence changes nothing about this stage.
- ⚠️ **`gap-research` is targeted, so it cannot back a coverage claim.** This stage grounds the topic, maps the closest prior work, and states the gap — it does not pre-specify a search strategy, inclusion/exclusion criteria, dedup, two-stage screening, or a re-runnable search log. If the paper will claim survey-grade coverage ("we systematically reviewed"), or a reviewer will ask *how* these works were found, run the protocol in `references/systematic-review.md` instead and report its flow counts. Writing "systematically reviewed" over a `gap-research` pass is an over-claim about method, and no citation check catches it. For an ordinary related-work section, stay here — a screening log buys nothing a reader sees.
- The deliverable is a .md research note — do not write .tex directly. The note becomes the input for ideate/outline/draft.
- The researcher must not self-approve — human review after producing the note is recommended.
</Execution_Policy>

<Steps>
1. Confirm the survey topic and scope (paper topic, target venue, prior work you already know).
2. Delegate via `Task(subagent_type="oh-my-scholar:scholar-researcher", ...)` using the **4-field delegation template** (Anthropic multi-agent-research pattern — objective / output format / tool guidance / boundaries):
   - **Objective**: survey the related-work landscape for the given topic/scope (pass along any references you already have and paths to relevant reference notes), cluster it by method family, and state the gap this paper fills.
   - **Output format**: research landscape map (by method family) + verified citation list (flag unverified) + gap list + per-claim verbatim quote + locator anchoring (quote rows feed scholar-verify's claim-faithfulness check).
   - **Tool guidance**: parallel reading is OK, and reading breadth scales with topic breadth — a narrow topic needs only a few sources; a broad multi-family survey may run up to **3 concurrent read batches inside this one dispatch** (cap anchored to scholar-mock-review's 3-lens dispatch precedent, a deliberate conservative ceiling). This fans out *reads*, never *dispatches* — the survey stays ONE `Task(mode=gap-research)` call, never a second parallel `mode=gap-research` dispatch to split citation generation. After each source batch, re-derive the gap list before continuing (interleaved gap-check). Stop expanding when 2 consecutive batches add no new method family AND no new gap — never "until exhausted" (the Undermind lesson: a marginal-returns stopping rule beats exhaustive search).
   - **Boundaries**: cite only verified items, flag the unverified; parallel reading is OK but parallel citation generation is prohibited (see Execution_Policy above) — the single synthesis inside this one dispatch remains the only citation generator. Optional: when per-paper reference lists (one `.bib` per paper) are already on hand, run `scripts/bib_coupling.py` first and treat its clusters as candidate method families — a mechanical seed only, advisory, the researcher's own judgment prevails.
3. Receive the researcher's output:
   - Research landscape map (classified by method family)
   - List of verified citations (those with confirmed author/year/title)
   - Gap list (what existing methods fail to solve)
   - List of unverified flags (need human confirmation)
4. The caller saves the output as a .md research note in the workspace — `.hq/work/scholar/<slug>/research/*.md` (fixed path per output-layout.md §2). ⚠️ Do not place it in the source folder (`paper/…`) — a research note is the *input* (scaffolding) for the draft, not a citation-bound source asset.
5. If there are unverified flags, ask a human to confirm and then update the note.
</Steps>

<Output>
The contents of a .md research note containing the research landscape map + list of verified citations + gap list + list of unverified flags (if any) + "ready to hand off to scholar-ideate or scholar-outline" (explicitly stating no self-approve).
</Output>
