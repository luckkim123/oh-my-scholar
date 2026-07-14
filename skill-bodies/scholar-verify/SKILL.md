---
name: scholar-verify
description: |
  Summative automatic gate for .tex/.bib — mechanically PASS/FAIL on compilation, numbers, references, terminology, placeholders, and citations.
  The "CI" of code. No critique or advice, objective evidence only.
  On detecting a citation defect, no auto-fix — human-confirmation list only.
  Triggers: 검증해줘, verify, 통과 확인, 컴파일 체크, 인용 검증, 게이트 확인, PASS 판정, verify, compile check, citation verification, gate check, PASS verdict
---

# scholar-verify — summative gate for the paper draft

<Purpose>
Inspect drafted/revised .tex/.bib through a mechanical pass/fail gate. Delegate to scholar-verifier (read-only) to check compilation, numerical consistency, figure/table references, terminology consistency, placeholders, and citation consistency. The "CI" of code — objective evidence only, no advice or critique.

⚠️ **Does not give critique or advice.** If the goal is logic/prose improvement points, use scholar-inspect. What comes out here is only per-item PASS/FAIL and evidence.
⚠️ **Does not auto-fix citation defects.** Even when a citation error is detected, it does not touch .bib — it returns a human-confirmation list only.
</Purpose>

<Use_When>
- When an objective pass verdict is needed after draft/revise, before submission
- When mechanically verifying compile errors, undefined refs, numerical mismatches, or leftover placeholders
- When inspecting citation (\cite ↔ .bib) consistency
- When confirming whether the venue page limit and minimum citation count are met
</Use_When>

<Do_Not_Use_When>
- If logic/prose critique or advice is needed → scholar-inspect
- If you want to apply critique results to the .tex → scholar-revise / scholar-draft
- If there is no draft yet → scholar-draft first
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Fresh evidence only** — "should/probably/seems/아마도" forbidden. Judge only with log lines, grep results, and actual numbers.
- ⚠️ **Citation auto-fix absolutely forbidden** — citation defects such as \cite ↔ .bib mismatches or unverified DOIs are detected only, never fixing the .bib. Return them as a human-confirmation list.
- ⚠️ **No advice or critique** — the verifier does not attach judgmental comments like "this sentence is weak".
- ⚠️ **No self-approval** — drafter/reviser and verifier are different lanes.
- For FAIL items, attaching evidence of what failed and why (log line, grep result, file:line location) is mandatory.
- If there are FAILs, classify by fixable_by_llm — true (text/ref fixes) goes to scholar-revise, false (missing experimental data, figure generation, etc.) is flagged for a human.
</Execution_Policy>

<Steps>
1. Confirm the target .tex/.bib file paths and venue info (page_limit·min_citations).
2. Delegate via `Task(subagent_type="oh-my-scholar:scholar-verifier", ...)`:
   - Input: .tex/.bib paths, paper-eval.md rubric (verify axis), latex.md card, bibtex.md card, venues.md, scripts/verify_bib_entry.py (mechanical DOI/retraction lookup for the DOI-existence item)
   - Instruction: output PASS/FAIL + evidence for each of the items below. No advice or critique. Citation defects as a list only.
     - **Compilation**: latexmk exit 0, undefined ref/cite 0
     - **Numerical consistency**: body numbers ↔ tables/figures match
     - **Figure/table references**: `\ref` ↔ `\label` matched exhaustively
     - **Terminology consistency**: same concept uses the same term, abbreviations defined on first appearance
     - **placeholder**: TODO/FIXME/XX/[MATERIAL GAP] leftovers 0
     - **Citation consistency**: `\cite` ↔ .bib entry exists (DOI existence goes to the human-confirmation list)
     - **Claim-faithfulness / citation-misuse (WARN)**: claim↔\cite stance check against the researcher's quote anchors (supports/contrasts/mentions) — misuse → human-confirmation list; unanchored pairs = "check not run". "Exists" ≠ "supports".
     - **Abstract discipline (WARN)**: quantitative numbers, formulas, or multipliers left in the abstract region (it should be qualitative meaning only) — latex.md §3. Detection = WARN (not FAIL), venue variation exists
     - **Uncited-claim scan (WARN)**: claim-shaped sentences without \cite — WARN list, human judges (never auto-cite).
     - **Blind-review anonymization (WARN)**: only when the mapped venue form/venues.md indicates double-blind — grep for `\author`/`\thanks`/acknowledgment blocks, self-identifying phrases, non-anonymized repo/grant IDs. No such indication → N/A. WARN with locations, never auto-edits.
     - **Venue meta consistency (read-only)**: specificity ↔ origin ↔ learned_refs integrity (mismatch = WARN, not repaired)
     - **Open wiki gaps (WARN — family wiki-status convention)**: run `python3 scripts/oms_wiki_audit.py --root <wiki-root>` and read its `open_gaps` dimension (equivalently `grep -rl '^status: open-gap' <wiki-root>`). Every note flagged `status: open-gap` must be either addressed in this draft or explicitly deferred in the verdict — an open gap left silent (neither) is a WARN, not a clean PASS. This is the carry-forward boundary: a reviewer/audit finding recorded in the wiki cannot drop out of the next submission without a human deciding to defer it. WARN only (does not count toward FAIL); N/A if no wiki root exists.
3. Receive the verifier output — collate per-item PASS/FAIL.
4. If there are FAIL items, classify by fixable_by_llm:
   - fixable_by_llm=true → can be passed to scholar-revise
   - fixable_by_llm=false → list requiring human confirmation
5. Unverified citations (DOI existence, author-name accuracy, etc.) → return as a human-confirmation list only, with no auto-fix.
6. **Venue meta consistency (read-only, H10)** — if the venue card/yaml has self-specialization meta, confirm only its integrity:
   - is `specificity` ∈ [0,1] and does it match `(count of items with origin∈{inductive,learned}) / (count of active defaults)`
   - does each `learned`-origin item have `learned_refs` provenance (§6.C no silent changes)
   - on mismatch, **WARN only** — not FAIL. ⚠️ verify only **reads** the meta, never repairs it
     (meta repair is `scholar-learn`'s human-gate job). Same as the auto-fix-forbidden principle.
7. Output the final verdict (PASS: all items pass / FAIL: number of failed items. **WARN (meta consistency, abstract discipline) does not count toward FAIL** — reported only, human judgment).

**Categorized report (#34 preflight-style)**: scholar-verifier's per-item report reads as a submission checklist — the same PASS/FAIL/WARN rows are grouped under 5 fixed category headers (language / citations / formatting-metadata / tables-figures / declarations), each showing the worst severity among its rows. Presentation only — no check is added, removed, or reweighted, except the new blind-review anonymization (WARN) check, which lands under `declarations` and only runs for venues the mapped venue form/venues.md marks double-blind.
</Steps>

<Output>
- Per-item results, grouped under 5 categories (language / citations / formatting-metadata / tables-figures / declarations) with a worst-severity roll-up per category (compilation, numbers, references, terminology, placeholder, citation each PASS/FAIL + evidence; abstract discipline, claim-faithfulness (quote anchor stance), venue meta, blind-review anonymization (double-blind venues only) PASS/WARN)
- FAIL item details: evidence (log line, grep result, file:line) + fixable_by_llm classification
- List of unverified citations (no auto-fix — human confirmation only)
- Final verdict: **PASS** (all items pass) or **FAIL** (N items failed)
- On FAIL, next step: fixable=true → scholar-revise, fixable=false → re-verify after human handling
</Output>
