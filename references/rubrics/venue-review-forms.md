# Rubric — Venue Review Forms (per-venue review form SSOT)

> Single source of truth for `scholar-mock-review`'s venue forms. `scholar-reviewer` (lens evaluation) and
> the Area Chair meta pass read this card to know **that venue's score axes, scales, and verdict vocabulary**.
> Pairs with `paper-eval.md` (the inspect/verify/mock-review 3-axis split) — paper-eval decides *which lane*,
> and this card decides *which form is used to judge in that venue*.

## Why it differs per venue

Real reviewer forms differ per venue in their score axes, scales, and verdict vocabulary. The substance of
"reviewing to fit the venue's character" is to **pick the relevant venue form from this card and inject it as-is**.
Hardcoding a single form leads to the error of reviewing IROS like NeurIPS.

⚠️ **Conference vs journal — the verdict vocabulary is fundamentally different.**
- **Conferences** (NeurIPS·ICLR·CVPR·IROS·ICRA): accept / borderline / reject (+ rebuttal window).
  **There is no major/minor revision.**
- **Journals** (IEEE T-RO·RA-L, etc.): minor revision / major revision / reject.

Even if the user says "major/minor revision" about a conference, conferences have no such stage —
convert it to a letter grade or score + accept/reject + "what the rebuttal must address" when answering.

---

## Form 1 — NeurIPS / ICLR / ICML (ML conferences)

Source: https://neurips.cc/Conferences/2024/ReviewerGuidelines · https://iclr.cc/Conferences/2025/ReviewerGuide

| Axis | Scale |
|:---|:---|
| Soundness | 1-4 (4 Excellent / 3 Good / 2 Fair / 1 Poor) |
| Presentation | 1-4 |
| Contribution | 1-4 |
| Overall | 1-10 (NeurIPS continuous) — **ICLR is discrete {1,3,5,6,8,10}** |
| Confidence | 1-5 (5 absolute certainty … 1 guess / outside area of expertise) |

Overall 1-10 meaning (NeurIPS): 10 Award quality · 9 Very Strong Accept · 8 Strong Accept ·
7 Accept · 6 Weak Accept · 5 Borderline accept · 4 Borderline reject · 3 Reject ·
2 Strong Reject · 1 Very Strong Reject.

**Free-text axes**: Summary · Strengths · Weaknesses · Questions · Limitations · Ethical concerns.
Strengths/Weaknesses are evaluated against originality·quality·clarity·significance.

**Verdict**: Overall score + accept/borderline/reject. No revision stage → "what the rebuttal must address".

### Score bands (populate from public venue stats — keep a source URL per row; never guess)

| Band | Meaning | Source |
|:--|:--|:--|
| _(empty — add a row only from this venue's verified public acceptance-rate/score-distribution stats)_ | | |

Read by `scholar-reviewer` (lens/AC) when populated; when empty, state "no calibration data — uncalibrated
venue-scale estimate" rather than guessing a band.

---

## Form 2 — CVPR / ICCV (vision conferences)

Source: https://cvpr.thecvf.com/Conferences/2026/ReviewerGuidelines

| Axis | Scale |
|:---|:---|
| Overall recommendation | Strong Accept / Weak Accept / Borderline / Weak Reject / Strong Reject |
| Confidence | 1-5 |

Evaluation items (**free-text criteria — not separate 1-N score axes**. Unlike NeurIPS's 1-4 sub-axes, CVPR
handles these in prose and the score converges to a single Overall recommendation label): **originality/novelty ·
technical quality/soundness · clarity of presentation · significance/impact**.

Venue norms (must be reflected):
- To claim "already done" (denying novelty), you must **cite specific prior work**.
- **Failing to beat SOTA is not by itself a reject reason.**
- Do not reject for a minor fixable flaw — weigh novelty·potential impact alongside performance.

⚠️ The labels (Strong Accept … Strong Reject) are verified. The integer mapping (5/4/3/2/1 vs a 6-point variant)
**differs per year's OpenReview form** — confirm that year's form before hardcoding. v1 uses labels only.

### Score bands (populate from public venue stats — keep a source URL per row; never guess)

| Band | Meaning | Source |
|:--|:--|:--|
| _(empty — add a row only from this venue's verified public acceptance-rate/score-distribution stats)_ | | |

Read by `scholar-reviewer` (lens/AC) when populated; when empty, state "no calibration data — uncalibrated
venue-scale estimate" rather than guessing a band.

---

## Form 3 — IROS / ICRA (robotics conferences)

Source: https://www.ieee-ras.org/conferences-workshops/financially-co-sponsored/iros/information-for-iros-associate-editors/

⚠️ **Decisively different from NeurIPS/ICLR — there are no multi-axis numeric scores.** A single composite letter grade.

⚠️ The reviewer **picks only one letter.** The "internal weight" below is just a reference value PaperPlaza uses
to convert the letter into a number for aggregation — it is not a score the reviewer fills in per-axis (there are no per-axis numeric sub-scores).

| Letter | Internal weight (reference) | Meaning |
|:---|:---:|:---|
| **A** | 5.0 | Definitely accept (~top 15%) |
| **B+** | 4.5 | Accept |
| **B** | 4.0 | High borderline |
| **B-** | 3.5 | Borderline |
| **C** | 3.0 | Low borderline |
| **C-** | 2.5 | Reject |
| **D** | 2.0 | Definitely reject |
| **U** | 1.0 | Inappropriate / out of scope |

- Review management: **PaperPlaza**. The review body should be **≥~1,200 non-whitespace chars** of substantive length.
- Evaluation items (within the free-text): contribution · technical soundness/correctness · novelty/originality ·
  relevance to robotics · clarity/presentation · references.
- double-anonymous.

**Verdict**: a single letter grade (A~D) + overall free-text. No per-axis numeric sub-scores, no revision stage.

### Score bands (populate from public venue stats — keep a source URL per row; never guess)

| Band | Meaning | Source |
|:--|:--|:--|
| _(empty — add a row only from this venue's verified public acceptance-rate/score-distribution stats)_ | | |

Read by `scholar-reviewer` (lens/AC) when populated; when empty, state "no calibration data — uncalibrated
venue-scale estimate" rather than guessing a band.

---

## Form 4 — Journals (IEEE T-RO · RA-L, etc.)

Source: IEEE Transactions / RA-L editorial conventions.

| Verdict | Meaning |
|:---|:---|
| Accept | Publish as-is |
| **Minor revision** | Re-review after small revisions (usually no re-review, AE confirmation) |
| **Major revision** | Re-review after large revisions (goes back to reviewers) |
| Reject | Rejection |

**The key difference from conferences = only here does major/minor revision exist.** If the author
wants a "revision verdict", first confirm whether the venue is a journal — if a conference, correct it
to accept/reject + rebuttal and advise accordingly.

### Score bands (populate from public venue stats — keep a source URL per row; never guess)

| Band | Meaning | Source |
|:--|:--|:--|
| _(empty — add a row only from this venue's verified public acceptance-rate/score-distribution stats)_ | | |

Read by `scholar-reviewer` (lens/AC) when populated; when empty, state "no calibration data — uncalibrated
venue-scale estimate" rather than guessing a band.

---

## Usage — the procedure for a reviewer/AC to pick a venue

1. Confirm the paper's target venue (the key in `references/venues.md` or as specified by the user).
2. Map the venue type: ML conference→Form 1, vision→Form 2, robotics→Form 3, journal→Form 4.
   For an unknown venue, use the closest form + a "this venue's actual form unconfirmed" caveat.
3. Apply that form's axes·scales·verdict vocabulary **as-is** to per-axis evaluation and the final verdict.
4. Revision vocabulary applies only to Form 4 (journals). Conferences use accept/borderline/reject (+rebuttal).

---

## Source completeness note

The scales above (NeurIPS 1-10/1-4/1-5, ICLR discrete set, IROS A~D letters, CVPR labels, journal revision
vocabulary) were confirmed in the 2026-05-31 survey against primary sources (official reviewer guideline pages·IEEE RAS·arXiv).
Only the CVPR integer mapping is unfixed because it depends on each year's OpenReview form (labels only verified). For the
synthesized survey report, see §2·§4 of the design document that prompted this card's creation (`docs/specs/2026-05-31-scholar-mock-review/design.md`).
