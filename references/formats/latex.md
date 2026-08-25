# Format Knowledge Card — LaTeX (.tex)

> The SSOT for oms LaTeX integrity and style. scholar-verifier (automated gate) and scholar-drafter (authoring) read this card to operate. Do not embed duplicates — always reference this file.

## 1. Compile Integrity Checks (verifier = summative pass/fail)

Items that yield a mechanical pass/fail. Equivalent to CI for code.

| Check | Method | Verdict |
|:---|:---|:---|
| Compile succeeds | `latexmk -pdf -interaction=nonstopmode main.tex` (or venue compile_engine) | exit 0 = pass |
| undefined references | log's `LaTeX Warning: Reference ... undefined` | 0 = pass |
| undefined citations | log's `Citation ... undefined` | 0 = pass |
| overfull hbox | log's `Overfull \hbox` | at or below venue tolerance = pass |
| page count | vs venue `page_limit`. Default: whole compiled PDF. When the venue sets `page_limit_excludes_bibliography: true`, main-text pages only — see the ReferencesStart procedure below | at or below = pass |
| placeholder leftovers | `\todo`, `[TODO]`, `[FIXME]`, `XXX`, `TBD` grep | 0 = pass |

Compile procedure (multi-pass): `pdflatex → bibtex → pdflatex → pdflatex`, or `latexmk` handles it automatically. The engine follows the venue card's `compile_engine` (pdflatex/xelatex/lualatex).

**Main-text page count (only when `page_limit_excludes_bibliography: true`).** Do not
try to infer where the bibliography starts from the log — ask LaTeX, which already
knows. Put one line in the preamble of the venue template:

```latex
\AddToHook{env/thebibliography/begin}{\label{ReferencesStart}}
```

After compiling, `main.aux` carries `\newlabel{ReferencesStart}{{...}{P}...}` where `P`
is the page the bibliography opens on; main-text pages = `P` (the reference-start page
is not main text, so it is excluded, not subtracted-then-added). Read the total from
`main.log` as usual and report both numbers.

⚠️ **The `.aux` groups are nested, so a single regex will mis-parse them.** Walk the
braces with a depth counter and take the **second** top-level group of the `\newlabel`
line. If the label is absent — the template predates this line, or the compile failed
before the bibliography — report "main-text page count not available" rather than
falling back to the total, which would silently answer a different question.


## 2. Numeric and Reference Consistency (verifier)

- **Body numbers ↔ table/figure numbers match**: do the figures cited in the body equal the values in the tables and figures? Mismatch = fail.
- **Figure/table numbers ↔ body references**: do `\ref{fig:x}`/`\ref{tab:y}` match an actual `\label`? Dangling ref = fail.
- **Terminology/abbreviation consistency**: is the same concept never called by different terms? Is the abbreviation defined on first occurrence?

## 3. Style Rules (drafter follows — house paper-format convention)

- **Text inside math is English only**: `\text{Uncertainty Cancellation}` ✓ / `\text{불확실성 상쇄}` ✗
- **Equation numbers use `\tag{}`** (do not embed numbers in titles/sections)
- **Section modularization**: split into `sections/*.tex`, `\input`/`\subfile` from `main.tex`
- **Citations use `\cite{key}`**, managed centrally in .bib (see the bibtex.md card)
- **Figure captions** non-empty, subfigure labels consistent
- **Abstract = qualitative meaning only, no quantitative figures or math** (drafter rule + verifier WARN detection):
  - Do not put quantitative figures, multipliers, thresholds, or inline math in the abstract region. Speed values, success rates, factors (e.g. `N×`), thresholds (e.g. `≤ X m`), and `$...$` math are all deferred to the body Results. Use only qualitative phrasing in the abstract ('faster'/'robust'/'real-time'/'by an order of magnitude', etc.).
  - **Why**: it duplicates the body, figures without context (baseline, conditions) draw reviewer suspicion, and math interrupts the prose flow. A strong common convention across journals, Science, and theses.
  - **verifier detection (WARN, not FAIL)** — this token list is the SSOT for detection (verifier and tests follow this; do not redefine):
    - Abstract region extraction: the `\begin{abstract}`~`\end{abstract}` environment, or for theses the `ABSTRACT` header~next `\clearpage`/`\chapter`. ⚠️ **If neither is found, skip the check (N/A) — do not grep the whole document** (grepping the whole body because the abstract could not be found falsely flags every number in Results).
    - Comments (lines starting with `%`) are not output, so they are excluded from the check.
    - grep tokens: inline math `$`; multiplier `\times` · unicode `×` · `[0-9][0-9.]*\s*\\?times` (with or without escape, includes "5 times" forms — over-detection acceptable since it is WARN); inequalities LaTeX `\le`/`\geq` and unicode glyphs `≤`/`≥`; number+unit `[0-9][0-9.]*\s*~?(m|cm|mm|km|s|ms|Hz|kHz|kg|g|dB|rad|deg|%|MB|GB)\b` (the trailing `\b` is load-bearing, preventing false hits like "6 missions"); percent `[0-9][0-9.]*\s*\\?%`.
    - 1 or more hits = WARN (does not block overall PASS). 0 = PASS. ⚠️ Multibyte (`×·§·≤`) grep can yield a false 0 depending on the environment (C-locale) — confirm a residual 0 with Python `re` (do not trust `LC_ALL=C grep` alone).
    - ⚠️ WARN hits are for human review (a rare false hit may slip in, such as English words that look like units, `2 m`·`3 s` — harmless since it is WARN).
  - **Venue variation**: some venues allow a single key figure in the abstract, so this is not a hard FAIL — detect only and let a human judge. (Paired with the paper-eval.md verify-axis `abstract discipline (WARN)` row.)

## 4. Pitfalls

- soffice/libreoffice cannot render .tex — verification must use a LaTeX engine.
- `~$`-style files are not temp files (LaTeX byproducts are `.aux .log .out .bbl .blg`) — ignore them during verification.
- bibtex must be re-run after `.bib` changes — a single pdflatex pass does not refresh citations.

## 5. Citation Safety (oms identity — together with bibtex.md)

Even when the verifier detects a missing citation or undefined citation, **do not automatically add it to .bib**. Only relay "this key needs verification" to the drafter, and the actual .bib edit is done by the drafter after human confirmation. Fabricating citations is the most dangerous hallucination.
