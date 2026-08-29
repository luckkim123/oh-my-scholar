# Knowledge Store Audit — health-check procedure (mechanical verbs + judgment lenses)
> Consumer: any session asked to "audit the post store." Two halves: `hq lint`/`hq query` do the mechanical half (§1); an LLM auditor does the judgment half (§2-§3) by following this procedure. Detection only — §5 is binding on both halves.

Ported from the workspace source workflow (`.oms/workflows/wiki-audit.js`) that originated this audit as five LLM-run dimensions. Three of those five (dangling refs, duplicate section tokens, empty/orphan — plus frontmatter validity and INDEX drift) described the retired wiki page-tree's *shape* and had no equivalent once the form changed (r7, 2026-08-30 — see `references/knowledge/README.md`); this card covers only the two dimensions that were never about page-tree shape and remain judgment-bound.

---

## §1. Run the mechanical verbs

```
hq lint
hq query --ascend --json          # spot-check the two-level merge actually answers
```

- `hq lint` reports the store invariants a page-tree audit used to check by hand: post ids, supersede-chain integrity, `topic`/`confidence`/`status` enum membership, and uncounted review comments. It walks every anchor from the resolved root, so there is no "once per level" step to remember — unlike the retired script's `--root`, `hq` itself owns ascent.
- `hq query --ascend --json` (optionally `--topic <category>`) is the retrieval sanity check — confirm a term you expect to be findable actually comes back, tagged with the right `anchor`.
- `.hq/community/INDEX.md` is generated automatically on every `hq post`/`hq edit` — there is no `--write-index` step to run by hand any more.
- Exit codes (`hq lint`): `0` clean, `1` an error-severity finding exists.
- `hq lint`'s own source (`skills/harness/hq/verbs.py::lint`) is the SSOT for what each mechanical check does — this card does not re-list them.

## §2. Judgment dimension A — SSOT-delegation integrity

This documentation corpus's design is directed SSOT delegation: a file says "X is the SSOT for topic T, I only add Y" and links to X. Two defects only a reader can find:

- **Broken delegation** — file A delegates topic T to file B, but B no longer covers T (B was trimmed or refocused since the delegation was written).
- **Cyclic delegation** — A says "B is SSOT for T" and B says "A is SSOT for T" (no real owner).

Procedure: read each file's header and its cross-refs, then re-open the file it delegates to and verify the delegated topic is actually owned there. Quote the delegating sentence and the missing-or-cyclic target, with `file:line` for both sides.

This is the subtle dimension — be rigorous, cite evidence, and **do not flag a healthy one-directional delegation as a defect.** A file pointing at its SSOT and staying silent on the topic is the design working as intended, not a finding.

## §3. Judgment dimension B — strength-tag discipline

⚠️ **CALIBRATION — read this before auditing (the rule's exact wording governs, established 2026-06-02).** The store's own quality rule (a `convention` post, historically at `wiki/convention/writing-guide/README.md` before the r7 form change — "강도 표기 규율") reads:

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

The audit **never edits the post store.** Repair is a separate, human-decided lane (same split as `omp-audit` vs `omp-organize`). `.hq/community/INDEX.md` regeneration (§1) is the one write path anywhere near this procedure — it happens automatically inside `hq post`/`hq edit`, not as a step this audit performs.

Findings are ranked **high / medium / low** and each carries `file:line` evidence quoting the offending text — never a paraphrase. If a dimension turns up nothing, report an empty findings list; do not invent defects to look productive.
