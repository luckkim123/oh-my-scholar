# Systematic review — the protocol `gap-research` does not run

`scholar-researcher mode=gap-research` is **targeted**: ground the topic, map the
closest prior work, verify each citation, state the gap as a necessity chain. That
is the right shape for positioning your own contribution, and it is what
`scholar-research` dispatches by default.

It is the wrong shape for a **coverage claim**. "We systematically reviewed the
literature" asserts that the search was pre-specified, that inclusion was decided
by a rule rather than by what you happened to find, and that someone else could
re-run it. `gap-research` makes none of those claims and carries none of the
machinery: no search strategy recorded before searching, no inclusion/exclusion
criteria, no dedup step, no two-stage screening, no search log.

So the two are not a strong-and-weak pair, they are different products:

| | `gap-research` | systematic review |
|:---|:---|:---|
| Question | where does my contribution sit | what does the field actually contain |
| Stopping rule | the gap is stated and citations verified | the pre-specified search is exhausted |
| Selection | whatever is closest to my method | whatever meets the criteria, including inconvenient results |
| Reproducible by a third party | no | **yes — that is the deliverable** |
| Fails when | the gap is over-claimed | the search was narrowed after seeing results |

Adapted from ECC's `scientific-thinking-literature-review` (MIT,
github.com/affaan-m/ECC). Its eight steps are kept; what is added is oms's own
citation discipline — the verbatim quote + locator anchor that `scholar-verify`
re-reads, and the never-fabricate rule.

## When this protocol, and when not

Use it when the paper claims survey-grade coverage, when a reviewer will ask "how
did you find these", when a research-question scope must be settled before reading,
or when the same search must be re-runnable months later for a revision.

Do **not** use it to write an ordinary related-work section. A four-page paper
positioning one contribution does not need a screening log, and producing one is
the expensive kind of thoroughness that buys nothing a reader will see.

## The protocol

1. **Define the question before searching.** Population / intervention-or-method /
   comparison / outcome, or the field's equivalent. Write it down. A question
   edited after seeing results is the failure this protocol exists to prevent, and
   it is invisible in the output unless the original was recorded.

2. **Pre-specify the search strategy.** Databases and their exact query strings,
   date window, language limits, and how the strings differ per database (they must
   — syntax is not portable). Record the strings verbatim; a paraphrased query is
   not reproducible.

3. **Pre-specify inclusion and exclusion criteria.** Each criterion must be
   decidable from title/abstract or from full text — say which. "Relevant" is not a
   criterion. Every later exclusion cites one of these by name.

4. **Search and log.** For each database: the query, the date run, the hit count.
   Nothing is discarded at this stage.

5. **Deduplicate.** Across databases, by DOI first, then by normalized
   title+first-author+year. Record how many duplicates were removed — the number
   is part of the audit trail, not bookkeeping.

6. **Screen in two stages.** Title/abstract first, then full text on the survivors.
   Every exclusion records **which criterion** excluded it. Counts at each stage
   are what the flow diagram reports.

7. **Extract into a fixed table.** One row per included work, columns fixed in
   advance (method, data, metric, result, limitation). A fixed schema is what makes
   the syntheses comparable; extending columns mid-extraction silently changes what
   "not reported" means for the rows already done.

8. **Synthesize by theme, not by paper.** Group by mechanism or finding. Report
   disagreements between sources explicitly rather than averaging them away — a
   contradiction in the literature is a result.

9. **Verify every citation and anchor every claim.** oms's rule, not ECC's, and it
   overrides anything softer: each reported claim carries a verbatim quote (≤3
   sentences, copied, never reconstructed from memory) plus a locator, because
   `scholar-verify`'s claim-faithfulness check re-reads exactly that anchor. A
   source you could not verify is reported as unverified — never dropped silently
   and never upgraded by confidence.

## What to report

The question as originally written; the per-database queries with dates and hit
counts; the criteria; the flow counts (found → deduped → title/abstract screened →
full-text screened → included); the extraction table; the thematic synthesis; the
gaps and limitations *of the review itself*, including which databases were not
searched and what that plausibly missed.

## Failure modes

- **Narrowing after seeing results.** Editing the question or criteria to fit a
  tidy set. The pre-written record in steps 1–3 is the only defence, which is why
  it is written before searching rather than reconstructed afterwards.
- **Claiming systematic while running targeted.** If the search was not
  pre-specified, the honest word is "we survey", not "we systematically review".
- **Silent zero results.** A query returning nothing is a finding about the field
  or a broken query string. Report the count; never omit the row.
- **One database.** Coverage claims from a single index inherit that index's blind
  spots. Name the ones you skipped.
- **Extraction drift.** Adding a column halfway makes every earlier row's blank
  ambiguous — is it "not reported" or "not asked"? Fix the schema in step 7 or
  re-extract.
