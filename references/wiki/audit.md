# Wiki Audit — health-check procedure (mechanical script + judgment lenses)
> Consumer: any session asked to "audit the wiki." Two halves: `scripts/oms_wiki_audit.py` does the mechanical half (§1); an LLM auditor does the judgment half (§2-§3) by following this procedure. Detection only — §5 is binding on both halves.

Ported from the workspace source workflow (`.oms/workflows/wiki-audit.js`) that originated this audit as five LLM-run dimensions. Three of those five are now pure code (dangling refs, duplicate section tokens, empty/orphan — plus frontmatter validity and INDEX drift, added when the script was written); this card covers only the two that remain judgment-bound.

---

## §1. Run the script (mechanical half)

```
python3 <plugin>/scripts/oms_wiki_audit.py --root <wiki-tree>
```

- `.oms/wiki/` exists at two levels (`references/wiki/README.md`'s local + global model) and the script takes exactly one `--root` per invocation — no ascent built in. Run it **once per level**: once against the local `.oms/wiki/`, once against the parent global `.oms/wiki/` (found by ascent, same discovery method as `wiki_query`).
- `--write-index` regenerates `<root>/INDEX.md` — a derived artifact, never hand-edited. Run it only *after* the findings from a plain run have been reviewed, not blind.
- Exit codes: `0` clean, `1` a FAIL-severity mechanical finding exists, `2` `--root` does not exist or another usage error.
- The script's `--help` and module docstring are the SSOT for what the five mechanical dimensions check and how each is defined — this card does not re-list them.
- **Ambiguous-stem token grammar (boundary note, T8 #3)**: a section token is the first whitespace-delimited word of a `^##+ ` heading, one trailing `.`/`:` stripped, then required to `re.fullmatch(§?[A-Z][0-9]*[a-z]?)` against the *whole* remainder. `H.` and `H-contrast.` never collide — `H-contrast` fails the fullmatch (hyphen + multi-char suffix isn't a token at all), so it is simply not extracted. `F1` and `F1b` never collide either — the optional trailing lowercase letter is part of the token string itself, not stripped, so the two strings are already distinct before comparison. Only an exact string match after this normalization counts as a duplicate-token finding.

## §2. Judgment dimension A — SSOT-delegation integrity

This wiki's design is directed SSOT delegation: a file says "X is the SSOT for topic T, I only add Y" and links to X. Two defects only a reader can find:

- **Broken delegation** — file A delegates topic T to file B, but B no longer covers T (B was trimmed or refocused since the delegation was written).
- **Cyclic delegation** — A says "B is SSOT for T" and B says "A is SSOT for T" (no real owner).

Procedure: read each file's header and its cross-refs, then re-open the file it delegates to and verify the delegated topic is actually owned there. Quote the delegating sentence and the missing-or-cyclic target, with `file:line` for both sides.

This is the subtle dimension — be rigorous, cite evidence, and **do not flag a healthy one-directional delegation as a defect.** A file pointing at its SSOT and staying silent on the topic is the design working as intended, not a finding.

## §3. Judgment dimension B — strength-tag discipline

⚠️ **CALIBRATION — read this before auditing (the rule's exact wording governs, established 2026-06-02).** The wiki's own quality rule (`convention/writing-guide/README.md` "강도 표기 규율") reads:

> `[N편공통]` — N편에서 반복 관찰 (2편 이상이라야 진짜 패턴).
> ⚠️ 1편에서만 본 걸 "공통"이라 쓰지 않는다 (품질 검수 통과 기준).

The rule requires the habit be *observed* in 2+ papers — it does **not** require an inline quote from every paper on every line. A tag naming 2+ distinct papers passes even without inline quotes; naming them attests the multi-paper observation.

So a defect is **only** when the tagged count exceeds the count of named-or-quoted distinct sources:

- `[N편공통]` where the line names or quotes just one paper — the 1편 violation the rule explicitly bans.
- `[N편공통]` with zero named source and zero quote — an uncheckable maximal claim.

Do **not** flag a tag merely because it doesn't inline-quote all N papers — naming them is enough. Do **not** re-flag the same independence-cluster caveat on every line it could apply to; if the file header or the line already carries that caveat, it is satisfied — report **at most one reminder per file, not one per tag.**

Quote the tag and its evidence with `file:line`. If a tag names 2+ distinct papers, it passes — do not report it.

## §4. The calibration lesson (generalized)

The strength-tag calibration in §3 exists because on 2026-06-02 the dimension's raw findings diverged from expectation — an early pass over-flagged tags that named multiple papers but only quoted one, reading the rule as "every named paper needs an inline quote." The fix was not to rewrite the corpus (add quotes everywhere); it was to re-read the rule's own exact wording and correct the auditor's criteria.

Generalize this: when a dimension's findings diverge from what you expected going in, **audit the criteria first, then the corpus.** A pile of findings that "feel like too many" or "feel like too few" is a prompt to re-derive the rule from its source text before trusting either the findings or the files they're about.

## §5. Detection-only discipline

The audit **never edits the wiki.** Repair is a separate, human-decided lane (same split as `omp-audit` vs `omp-organize`). The one write path anywhere in this procedure is `--write-index` (§1) — that is generated-artifact regeneration, not repair, and it stays opt-in and post-review.

Findings are ranked **high / medium / low** and each carries `file:line` evidence quoting the offending text — never a paraphrase. If a dimension turns up nothing, report an empty findings list; do not invent defects to look productive.
