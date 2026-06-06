# Rubric — Paper Evaluation (inspect vs verify vs mock-review: 3-axis separation)

> oms evaluation SSOT. It re-arranges paper-write's flat 5-reviewer score into OMC's inspect(formative) ≠ verify(summative) philosophy, and adds an adjudicative judging axis (mock-review) on top. scholar-inspector, scholar-verifier, and scholar-reviewer read this card and each know their own lane.

## Core separation — code's "code review vs CI vs mock review"

| | scholar-inspect (formative) | scholar-verify (summative) | scholar-mock-review (adjudicative) |
|:---|:---|:---|:---|
| **Nature** | critique/advice (judgment type) | pass/fail gate (mechanical type) | venue-criteria judging (score + verdict) |
| **Code analogy** | code review | CI | mock reviewer |
| **Stance** | on the author's side (fix this) | machine (pass/fail) | on the reviewer's side (my score is this) |
| **Output** | list of improvements + severity | PASS / FAIL + evidence | venue-scale score + venue-native verdict (conference accept/reject/letter / journal minor/major revision) |
| **agent** | scholar-inspector (opus, read-only) | scholar-verifier (opus, read-only) | scholar-reviewer (opus, read-only, 3 lenses + AC) |
| **Automation** | aids human judgment | can be auto-checked | mock — not a substitute for actual review |

## verify axis (summative — mechanical pass/fail)

Like code's CI, pass/fail comes out objectively. (Check items from the latex.md / bibtex.md cards.)

| Item | Check | Card |
|:---|:---|:---|
| Compile | latexmk exit 0, undefined ref/cite 0 | latex.md §1 |
| Numeric consistency | body numbers ↔ tables/figures match | latex.md §2 |
| Figure/table references | `\ref` ↔ `\label` matching | latex.md §2 |
| Term consistency | same concept = same term, abbreviations defined | latex.md §2 |
| placeholder | TODO/FIXME residue 0 | latex.md §1 |
| Citation consistency | `\cite` ↔ .bib, DOI exists | bibtex.md §1·2 |
| Page/citation count | venue page_limit / min_citations | venues.md |
| abstract discipline (WARN) | quantitative numbers / equations / multipliers in abstract region residue 0 (qualitative meaning only) | latex.md §3 |
| writing discipline (WARN) | decorative words / excessive em-dashes / rule-of-three / negative parallelism residue 0 in body | writing-craft.md §7 |

**On FAIL, report what failed and why, with evidence (log lines / grep results).** No "should/probably/seems" — fresh evidence only.

> **WARN ≠ FAIL** (handled the same as venue meta consistency): `abstract discipline` / `writing discipline` violations do not block the overall PASS and are reported only as a **warning (WARN)**. Rationale — not putting quantitative numbers in the abstract is a common strong convention, but some venues allow one key number, and writing (decorative words / rule-of-three) static blocklists decay and contextually legitimate uses get mixed in (over-detection), so forced FAIL risks false-positives. Therefore detect but leave the verdict to the human/inspector. (Abstract numbers are deferred to the body Results; writing is handled in judgment form by the inspector's prose lens.)

## inspect axis (formative — judgment-type critique)

An area absent from code CI. This is reviewer critique, not pass/fail.

| Lens | Looks at | Absorbed from |
|:---|:---|:---|
| **logic** | contribution-evidence correspondence, structural logic, baseline comparison, devil's advocate | paper-logic-reviewer |
| **prose** | academic style (differs KO/EN), exaggeration discipline, repetition, transitions, sentence length | paper-prose-reviewer |

Each finding: severity(critical/important/minor) + location + issue + evidence(.tex citation) + suggestion + **fixable_by_llm** (text restructuring = true / missing experiment/figure or contribution-scope change = false).

## mock-review axis (adjudicative — venue-criteria judging)

If inspect is a coach who *helps the author*, mock-review is a judge who *evaluates the author*. With a reviewer persona it produces a venue-scale score and venue-native verdict (conference accept/reject/letter / journal minor/major revision). Ensemble of 3 lenses in parallel + Area Chair synthesis (the two modes of the `scholar-reviewer` agent).

| Lens (mode=lens) | Looks at |
|:---|:---|
| **soundness** | technical soundness/correctness, experiment design, baseline, ablation, reproducibility info |
| **novelty** | novelty, positioning vs related work, contribution differentiation (⚠️ without retrieval, no assertions → demote to a question) |
| **clarity-significance** | clarity, structure, significance/impact, reproducibility info |

Area Chair (mode=area-chair): 3-lens synthesis → venue form (`venue-review-forms.md`) per-axis scores → re-check (drop anchor-less weaknesses / demote novelty) → accept-bias calibration → venue-native verdict.

The venue scale / verdict vocabulary is SSOT in `venue-review-forms.md` (NeurIPS 1-4 / 1-10 / 1-5, CVPR labels, IROS letter A~D, journal minor/major revision). ⚠️ Conferences have no revision stage — accept/borderline/reject or letter.

Each strength/weakness: an in-paper location anchor is required (drop if absent) + evidence(.tex citation). At the very top of the output, the disclaimer "mock review — not a substitute for actual peer review."

## Why the separation matters

- inspect must not imitate "pass/fail" or "score/verdict" — logic/style are inherently *advice*. The verdict belongs to mock-review.
- verify must not "advise" — the gate is by objective evidence only.
- mock-review must not say "fix it" — the judge gives only scores/verdicts. Fixes go through scholar-revise.
- **No self-approval**: inspect, verify, and mock-review all cannot evaluate a draft they themselves wrote. A different lane from the drafter (different agent, read-only).
- **citation safety (mock-review)**: anchor-less weaknesses are a hallucination risk, so drop them. Novelty assertions are demoted to questions without retrieval — a review-domain extension of oms's "no fabricated citations."
