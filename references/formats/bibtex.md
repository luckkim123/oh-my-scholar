# Format Knowledge Card — BibTeX (.bib)

> oms's citation-integrity SSOT. scholar-verifier verifies, only scholar-drafter edits (after human confirmation). citation is oms's strictest guardrail.

## 1. Format checks (verifier = summative)

| Check | Method | Verdict |
|:---|:---|:---|
| BibTeX syntax | 0 errors in `bibtex main` log | pass |
| Required fields | required per entry type (@article: author/title/journal/year; @inproceedings: author/title/booktitle/year) | 0 missing = pass |
| Duplicate key | same cite key defined twice | 0 = pass |
| Body↔.bib consistency | every `\cite{key}` exists in .bib + every .bib entry is cited in the body | 0 dangling/orphan = pass |

## 2. Citation verification (verifier — but auto-fixing is absolutely forbidden)

- **DOI/existence verification**: where possible, look up the DOI/title via CrossRef/Semantic Scholar to confirm it actually exists. Not found = critical warning.
- **Self-citation ratio**: when author names are provided, compute the self-citation ratio; exceeding venue `self_citation_max_ratio` (default 0.20) = warning.
- **Minimum citation count**: below venue `min_citations` = warning.

> **External verification pattern — zero-assumption multi-DB**: the verified pattern trusts no citation and cross-checks *every* reference
> independently against multiple DBs (Semantic Scholar, CrossRef, arXiv). One study
> verified 2,581 refs this way at 91.7%, detecting fabricated/retracted/orphan/predatory entries
> ([Zero-Assumption Protocol, arXiv:2511.04683](https://arxiv.org/abs/2511.04683)). oms's
> DOI/existence verification above is a partial implementation of this pattern — where possible, extend it from a single DB to multi-DB cross-checking.
> ⚠️ This only strengthens *detection* — auto-fixing is permanently forbidden per §3 (verification flags defects, humans fix them).

## 3. ⚠️ No automatic citation fixing (oms core principle)

verifier/hook only **detect and warn**. Never:
- automatically add a missing citation to .bib (= risk of citation fabrication)
- fill in title/author "plausibly" (= hallucination)
- guess and insert a DOI

Instead: **hand it to a human** with something like "key `foo2024` is in the body but not in .bib — confirm the actual paper and add it." .bib edits are made by the drafter only after human confirmation.

## 4. Pitfalls

- After changing .bib, bibtex requires re-running `bibtex main` + pdflatex twice — otherwise citations don't update.
- Key naming consistency (e.g. `author2024keyword`) — inconsistency leads to maintenance hell.
- Accented characters use `{\\'e}` or UTF-8 (only when using biber/biblatex) — varies by engine.
