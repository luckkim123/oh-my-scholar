# references/wiki — secondary memo store that accumulates across sessions (more use = more specialized to this project)

This store is a persistent memo for **compounding session-volatile data into a "lab standard."** It operates as a **bidirectional loop**:
- **Write (automatic)**: scholar-pilot's wiki capture stage **auto-appends** the reject patterns and decisions discovered by inspect/verify (no approval needed — lightweight channel, `scholar-pilot/SKILL.md` Step 10).
- **Read (automatic)**: the next session's inspector pre-commitment queries that accumulated pattern via `wiki_query(category)`.

With write and read closed into a loop, **the more you use the harness, the more it specializes to this venue and this paper project** — even without the user explicitly invoking "learn this." At deployment the store is empty (general-purpose), but it diverges as you operate it.

This is the current implementation target of the `wiki_query(category)` abstract function, and behavior does not break even if it is empty or absent (the inspector proceeds with its own predictions).

---

## Directory layout

⚠️ **Data accumulates in the workspace (`.oms/wiki/`) — not in this plugin repo.** This README is a *contract document*, so it ships with the plugin (`references/wiki/README.md`), but the actual accumulated data is written to **`.oms/wiki/`** (`.oms/` is gitignored — so it diverges without polluting the plugin/distribution, which is how "specialized to this user / this paper" holds). Same as OMC's `.omc/wiki/` (project-local) pattern.

### ⭐ Two layers — local (this paper) + global (parent folder's `.oms/`, found by ascent)

`.oms/wiki/` lives at **two levels**. Both are cwd-relative — **zero absolute paths, env vars, or XDG** (oms philosophy "work-root relative" as-is, no distribution pollution):

```
<parent folder of the papers>/.oms/wiki/      ← ⭐ global level — reused by this *user* across all papers
  convention/   *.md   ← per-venue formats and section structure (reusable)
  pattern/      *.md   ← tendencies (favorite expressions, structures, working style, preferences) — light-only
  decision/     *.md   ← reusable decisions (e.g. always do ablation first)
  reference/    *.md   ← pointers to frequently used resources
  history/      *.md   ← ⭐new: my paper history (init references for duplicates and linking)
        ▲  discovery method = ascent (cwd→parent, the single nearest ancestor .oms/, excluding self; like git finding .git)
        │
<paper folder>/.oms/wiki/                ← local level — specialized to this paper only (outside slug, accumulates across sessions)
  convention/   *.md   ← this paper's reject reasons and format rules (queried by inspector) — ⭐ the source of heavy promotion candidates
  pattern/      *.md   ← (usually empty — tendencies gather at the global level)
  decision/     *.md   ← this paper's decisions (why this baseline)
  reference/    *.md   ← this paper's resource pointers
```

- One file = one topic (e.g. `convention/neurips-reject-patterns.md`).
- A note's **body** is human-readable free-form .md — no machine-parsing schema there (grep only); the frontmatter fence above it is the one machine-parsable part (thin, stdlib-only — see "Frontmatter standard" below).
- `category` maps 1:1 to the subdirectory names above (4 local + 5 for global including `history/`).
- ⚠️ `.oms/wiki/` is a *project-wide* accumulation, so it sits **outside** the per-task `.oms/<slug>/` (output-layout) — not bound to a slug, it lives across sessions and tasks.
- ⚠️ **Only "paper-agnostic reusable assets" go up to the global level** (tendencies, venue formats, history, reusable decisions). Paper-specific knowledge stays local to that paper, and **citation/.bib is permanently forbidden from global promotion** (hallucination risk). This is how it reconciles with oms's "no user-scope" anti-pattern — the global level is *the parent folder's `.oms/`* (still work-root relative), not distributed config, and what flows up is only reusable assets.

### ⭐ `convention/` vs `pattern/` — heavy promotion candidates come only from convention (2026-05-31 H6 backport)

The separation of these two is key (`references/learning-protocol.md` §1):
- **`convention/`** = *what the output looks like* (section order, caption format, reject reasons). When observed repeatedly it
  escalates to `learned.md` and becomes a **heavy channel promotion candidate** (may harden into a venue default).
- **`pattern/`** = *how the user works* (tendencies, working style, preferences). **Light-only — never promoted.**
  Tendencies are not enforcement targets, just memos that every stage *reads* to match tone and level of detail. A `pattern/` note
  never rises to `learned.md`.

### ⭐ confidence frontmatter — repeated observation raises confidence (OMC backport, H6)

Each wiki note carries the frontmatter `confidence: high | med | low`. Observing the same pattern again raises
confidence `low → med → high`, and on merge it **keeps the higher side** (no demotion from a weak re-observation).
This repetition-driven rise is the light-channel version of omp's `evidence_count`, the signal that connects to the heavy gate:
when a `convention/` note reaches **`confidence: high`**, the pattern's `OBS` has likely
approached `evidence_count ≥ 3` = a good time for `scholar-learn` to look. confidence is just a qualitative 3-tier grade (+ observation count) —
**no numeric weighted sum or threshold magic number.**

### ⭐ A note holds *conclusion + evidence* together (no label-only — avoids re-reading cost)

A wiki note should not record only the *conclusion (label)* but should hold **the load-bearing evidence that supports that conclusion — concrete cases, control groups,
internal source pointers (which paper-slug/section to revisit) — in the same note.** If only the label is left behind, the next
session has to *re-open the original* to verify the conclusion's basis (re-reading cost = the classic learning failure). "X is a stage axis"
is less reusable than "X juxtaposes two independent contributions across stages without bundling them into chapters — see `<slug>` §table-of-contents."
- ⚠️ **This is a *recommendation* — different from the heavy channel's enumerable-evidence enforcement (`learning-protocol.md` §6.E).**
  The light channel's value is being cheap and frictionless (§1), so missing evidence is not a *reject gate*. It is a discipline
  that says the more evidence you include the better, not a block when it is absent.
- ⚠️ **"Source pointer" = an internal paper-slug/section pointer, not a `.bib` citation** (§6.F · keeping the citation boundary
  invariant below). "Revisit such-and-such part of `<slug>` for this conclusion" is just *internal navigation*; it does not
  write a paper citation into the wiki.
- ⚠️ **Append-time consequence (#24)**: `scholar-pilot/SKILL.md` Step 10 mechanically forces `confidence: low` (marked `evidence: none`) on an appended entry that carries neither pointer nor quote, and evidence-less re-observation never raises it — the entry is **still appended**, so this stays consistent with "not a reject gate" above. Procedure detail lives at that Step 10 bullet (not restated here); it remains a prompt-contract rule, no automated compliance check.

Example (conclusion + evidence together):

```markdown
---
confidence: high
sightings: 3
---
# IROS reject patterns
## 2026-05-20 — repeated mention of missing ablation (3rd observation → high)
- Conclusion: IROS reviewers cite the absence of ablation as a reject reason.
- Evidence (revisit pointers): missing ablation flagged in `iros-2026-nav` §4 · `iros-2026-grasping` §5 → both added.
  (If re-verification is needed, look at the relevant sections of these two slugs — not a citation, internal navigation.)
```

### `reference/` few-shot review examples (scholar-mock-review calibration, R5 #32)

A `reference/` note named `venue-review-examples-<venue>.md` holds user-collected real reviews for that venue —
private, hand-pasted by the user, and **never shipped** with the plugin (same non-distribution rule as the rest
of `.oms/wiki/`). `scholar-reviewer` (lens mode) reads it when present through the same 2-tier
`wiki_query(category="reference")` contract already specified below — no new mechanism, no embedding search.
When absent, the lens proceeds on its own judgment only (same graceful-degrade rule as every other category).

---

## Frontmatter standard (thin, stdlib-parsable)

This section is the SYNTAX contract for every wiki note's frontmatter — parsed by `scripts/oms_wiki_audit.py`'s stdlib-only splitter (no PyYAML). What `confidence` and `sightings` *mean*, and how confidence climbs on repeated observation, stays the SSOT of the confidence-frontmatter subsection above (§ confidence frontmatter) — this section only fixes the *shape*, not the semantics.

- **Flat `key: value` only.** One `---`-fenced block at the top of the file; each line splits on the first colon. No nesting, no lists, no multi-line values.
- **Required for new notes**: `confidence: high | med | low` and `sightings: <int>`.
- **Optional**: `keywords: a, b, c` — one line, comma-separated. A recall aid only; it never becomes a machine query index (recall stays deterministic grep over the note body, per the `wiki_query` contract below).
- **Optional (actionable status — family wiki-status convention)**: `status: open-gap | resolved` and, when open, `blocked-on: <free text>`. `open-gap` marks an unresolved reviewer/audit finding that must ride every summary until closed; `resolved` is terminal (record why in a dated body section — the note is never deleted). **Absent = not actionable** (every existing note). The audit's `open_gaps` dimension enumerates every `open-gap` note tree-wide (keyword-independent), and `scholar-verify` refuses a clean PASS while one is neither addressed nor explicitly deferred — so a finding recorded here cannot silently drop out of the next draft. A typo'd status is a WARN (`status` not in `{open-gap, resolved}`), because a mistyped value would silently leave the enumeration. `grep -rlE '^status:\s*open-gap' .oms/wiki/` is the family-wide fallback enumeration (the audit's splitter tolerates spacing, so the grep uses `\s*` to match it). WARN only — oms has no launch boundary to hard-block at.
- **Body stays free-form.** Headings, dated sections, prose (§ "A note holds conclusion + evidence" above) — the frontmatter fence is the only structured part of a note.
- Existing notes without frontmatter are not retroactively required to gain one — the audit's frontmatter check is WARN, never FAIL (`references/wiki/audit.md` §1) — but new notes should carry it from creation.

### INDEX.md — generated, not a query surface

Each wiki root (this paper's local `.oms/wiki/` and the ascent-discovered global `.oms/wiki/`) carries a generated `INDEX.md`, written only by `scripts/oms_wiki_audit.py --write-index` — never hand-edited. It is deterministic (same tree → same bytes: categories sorted, files sorted by relpath) and its own first line marks it as generated. Regenerate it with `--write-index` after adding or editing notes; if the tree drifts from the last-written `INDEX.md`, the audit's `index` dimension reports **WARN** (stale) — same non-blocking philosophy as the frontmatter check.

⚠️ **INDEX.md is for humans and for drift detection — not a query surface.** Recall still runs `wiki_query`'s deterministic grep over the notes themselves (below); `INDEX.md` is a browsable summary, never a stage-queried index.

---

## `wiki_query(category)` abstract function contract

```
wiki_query(category) → list of matched .md excerpts (empty list if none)
```

- **Current implementation (2-layer ascent merge)**:
  ```
  local_hits  = grep(<cwd>/.oms/wiki/<category>/, keywords)              # local — this paper
  parent_oms  = ascent(<cwd>): go cwd→parent to the first .oms/ (excluding self)     # like git finding .git
  global_hits = grep(parent_oms/wiki/<category>/, keywords) if parent_oms else []  # global — user reuse
  return merge(local_hits, global_hits)   # source-tagged [wiki:local] / [wiki:global]
  ```
  Deterministic grep only (keyword matching, including CJK bi-gram). The caller (inspector·planner) greps with venue, paper-type, and user-tendency keywords to pull excerpts. category is the 4 local ones (`convention`·`pattern`·`decision`·`reference`), plus `history` for global. (At any level, if the directory is absent, that level returns an empty list — new ones start from an empty store.)
- **Caller/implementation boundary (future replacement point)**: the inspector merely calls the *abstract function* `wiki_query`; it does not know whether the implementation is "2-layer grep" or a standalone MCP. **Ascent, merge, and source-tagging are all enclosed inside this function's implementation,** and the caller (inspector pre-commitment) does not change a single line. If a standalone wiki MCP is introduced later, only this function's implementation is swapped.
- **Graceful degrade on absence**: if either local or global is empty, or there is no ancestor `.oms/`, that side returns an empty list — not an error. The inspector proceeds with only what exists (or with its own prediction only).

---

## `citation_lookup(doi_or_title)` abstract function contract

```
citation_lookup(doi_or_title) → verdict + normalized metadata
```

- **Deterministic-lookup rule (P5-C)**: the verdict is always an API/database match result, never an embedding-similarity ranking. External services may use embeddings server-side; nothing embedding-shaped enters the verdict this function returns.
- **Current implementation (today's target)** — `scripts/verify_bib_entry.py`, described precisely rather than as one chain:
  - **DOI path**: try Crossref first. On `HTTPError` (not found / rejected), fall through to OpenAlex. On `URLError` (network unreachable), short-circuit straight to `NETWORK_ERROR` — OpenAlex is only tried after a Crossref *HTTP* failure, never after a Crossref *network* failure.
  - **Title-only path** (no DOI supplied): Crossref bibliographic search only — no OpenAlex fallback.
  - `WebSearch`/`WebFetch` is a **separate agent-level manual fallback**, reached for at the caller's discretion when the above returns `NOT_FOUND`/`NETWORK_ERROR` — it is never code-chained off an exit code; a human or the researcher agent decides whether to use it.
- **Caller/implementation boundary (future replacement point, same idiom as `wiki_query` above)**: the researcher/verifier merely calls the abstract function `citation_lookup`; it does not know whether the implementation is "Crossref-then-OpenAlex" or a standalone MCP. Only this function's implementation swaps.
- **MCP swap-points** (opt-in accelerators — P5-A: none becomes a prerequisite for any stage):

  | MCP | Role | Human gate |
  |:--|:--|:--|
  | Semantic Scholar MCP | citation lookup / metadata source | same as today — proposed entries still pass `verify_bib_entry.py` + cite-guard before any `.bib` write |
  | arXiv MCP | citation lookup / metadata source | same as today — same human gate |
  | Zotero MCP | **opt-in** citation source for users with an existing library | same human gate as today — proposed entries only, human confirms every one before write |

  Every MCP here is a *proposal source*, never a bypass (P5-B) — nothing lands in `.bib` automatically. Absence of every MCP changes nothing about correctness guarantees — only speed.
- **Empirical tool-description validation rule** (the Anthropic lesson): before trusting any MCP server's tool descriptions in a research pass, dispatch one cheap probe call and compare its observed behavior against the description — validate empirically, never trust the description alone.
- **Graceful fallback chain**: Crossref → OpenAlex (DOI path only, HTTPError-gated) → optional MCP (Semantic Scholar / arXiv / Zotero, if configured) → WebSearch/WebFetch (manual, agent discretion). Every link past Crossref is optional; with zero MCPs installed the chain degrades to today's Crossref/OpenAlex behavior unchanged.

---

## Data this store collects *newly* (net-new — not a migration)

Reject reasons and defect patterns are **net-new data**. The existing `references/formats/venues.md` (or venue cards) only have `page_limit`·`sections`·`quality_threshold` and *no reject field* — so this wiki is not migrated from venue cards; rather, inspector sessions *collect it newly* as they critique and load it in.

The loading party = **scholar-pilot's wiki capture stage automatically** (right after verify, before terminal — `scholar-pilot/SKILL.md` Step 10). It appends the reject patterns discovered in this session by inspect/verify into `convention/<venue>-reject-patterns.md`. When running standalone stages, the caller may load it directly. **Automatic is the default** — this is the write half of the bidirectional loop above. Skipped if the user passes `--no-wiki`. Append-only · pre-check for duplicates with grep · pass through on an empty session · no speculative loading (only what was actually discovered).

---

## ⚠️ citation safety boundary (mandatory — violation collapses the OMS identity)

- **Wiki content is only a *secondary memo* — never used as a primary citation source.** .bib updates only use primary sources verified by scholar-research (keeping the 3 citation-safety principles). Paper mentions written in the wiki are not pulled in as citations.
- **Lookup is deterministic keyword matching only — embedding search is permanently forbidden.** Both grep (current) and a future MCP must be deterministic matching. Embedding-similarity search pulls in hallucinated citations, so it is **forbidden now and in the future** (invariant constraint).
- The wiki is a *memo that aids prediction*, not a *source of fact*. The inspector marks wiki excerpts with `[wiki]` to distinguish them from its own predictions (`[self-prediction]`).
- ⚠️ **No direct light→enforce promotion** (H6 backport, `learning-protocol.md` §6.D): a wiki note (even at confidence high) is only *advice*, not an enforced default. To harden it into a venue default it must pass through the heavy channel of `learned.md` and clear a **human gate**. No matter how high the confidence, the wiki does not directly change a venue default. In particular `pattern/` (tendencies) is permanently light — not a promotion target.
