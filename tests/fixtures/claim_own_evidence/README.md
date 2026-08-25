# Calibrating the claim ↔ own-evidence axis

The axis shipped in 0.16.0 labelled `NOT_CALIBRATED`: it had never been run against
planted over-claims, so a clean report from it meant nothing. This is the measurement
that replaced that label, and the corpus is here so the number can be re-derived rather
than trusted.

## What is here

| File | What it is |
|:---|:---|
| `results.tex` | 17 sentences of a plausible results section, each tagged `% Sxx`. 8 planted defects, 9 clean. |
| `ground_truth.json` | The key. Never shown to a grader. |
| `runs/*.json` | One grader's flagged-id list per file. |
| `score.py` | Deterministic scoring of `runs/` against the key. |

## Method (2026-08-25)

Two subagents on **Sonnet** — the tier `scholar-verifier` itself is pinned to, so the
measurement describes the shipped configuration — each received `results.tex`, the
verbatim text of step 7.6 and its §3 rule, and nothing else. They were told not to open
`ground_truth.json`; both confirmed they did not. Neither saw the other's answer.

A third grader was dispatched and returned no result, so **n = 2**, not 3.

## Result

| class | recall | false positives |
|:---|:---|:---|
| `verb_exceeds_anchor` | 4/4 | 0/9 |
| `unanchored` | 0/4 | — |

Both graders returned the identical set `S07, S11, S12, S13`.

**The false-positive column is the part that took design.** Five of the nine clean
sentences are hard negatives, each aimed at a specific way the rule could over-fire: an
anchor sitting in the paragraph rather than the sentence (S05), a hedged verb over a weak
anchor that §2.5 explicitly protects (S08), a numeral anchor with no `\ref` at all (S09),
a legitimate `demonstrates` whose anchor spans three tables (S15), and a correctly hedged
limitation (S17). Neither grader flagged any of them. The rule's exceptions work.

**The recall column found a defect in the rule, not in the graders.** Step 7.6 said to
search "the sentence **and its paragraph**" for an anchor. Every planted unanchored claim
sits in a paragraph that contains a `\ref` or a number — because that is what a real
results paragraph looks like. So both graders read the rule correctly and concluded, in
one case explicitly, that the corpus contained no instances of that class. Paragraph
scope did not weaken the check; it removed it.

The wording was changed in 0.16.2 to add a sentence-level requirement for unquantified
claims. **That fix is not validated.** It was derived from the corpus that exposed the
bug, so scoring it here would be scoring a rule against its own training set. The class
stays `NOT_CALIBRATED` until a fresh corpus, written without reference to this one, is
graded blind.

## Re-running

    python3 tests/fixtures/claim_own_evidence/score.py

To add a grader, hand a subagent `results.tex` plus the current step 7.6 text, forbid
`ground_truth.json`, and drop its `FLAGGED:` line into `runs/`. `score.py` picks it up.

## Known limits of this measurement

- **n = 2, one model.** No cross-model spread, and no estimate of run-to-run variance.
- **The ids help the grader.** `% Sxx` comments remove the sentence-splitting step a real
  run has to do. This measures the judgment, not the segmentation.
- **One corpus, one domain.** Nothing here says the numbers hold on a different paper.
- **Graders saw the rule alone**, not the full verifier context of eleven other steps.
