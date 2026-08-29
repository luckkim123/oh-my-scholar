# references/knowledge — the accumulated secondary-memo store (specializes the more it is used)

This store is a persistent memo for **compounding session-volatile data into a "lab standard."** It operates as a **bidirectional loop**:
- **Write (automatic)**: scholar-pilot's post-capture stage **auto-posts** the reject patterns and decisions discovered by inspect/verify (no approval needed — lightweight channel, `scholar-pilot/SKILL.md` Step 10).
- **Read (automatic)**: the next session's inspector pre-commitment queries that accumulated pattern via `hq query --ascend`.

With write and read closed into a loop, **the more you use the harness, the more it specializes to this venue and this paper project** — even without the user explicitly invoking "learn this." At deployment the store is empty (general-purpose), but it diverges as you operate it.

Behavior does not break even when the store is empty or absent — the inspector proceeds with its own predictions.

---

## ⚠️ The form changed on 2026-08-30: this is a POST store, not a page tree

Until r7 this store was `.hq/community/wiki/` — one free-form `.md` per topic under
category sub-directories, read by grep and by `scripts/oms_wiki_audit.py`'s own linter.
**That form is retired** (user decision: "wiki 는 아예 없애는 걸로. Wiki 폴더 안만들게").

It was retired because it had stopped being read at all. Measured across every anchor on
this machine, `community/wiki/` held **zero pages** while `community/posts/` beside it held
127 / 33 / 17 — and this harness's routing checkpoint named the empty directory as the
knowledge SSOT on every single turn.

- **Nothing in this harness creates a `community/wiki/` directory.** Not a skill, not a
  hook, not a helper. If you find prose telling you to write one, it is stale — fix it.
- A store that still holds wiki pages converts once, with omo's
  `skills/harness/convert-wiki-form.py` (`plan` then `apply`). It refuses to guess the
  fields the conversion cannot derive.
- `scripts/oms_wiki_audit.py` was deleted with the form. Its jobs are now `hq lint` (store
  invariants) and `hq query` (retrieval); the checks that were about the page-tree
  shape — misplaced files, unknown category directories, INDEX drift — describe a shape
  that no longer exists. The two judgment dimensions that survive (SSOT-delegation
  integrity, strength-tag discipline) still live in `references/knowledge/audit.md`.

---

## Directory layout

⚠️ **Data accumulates in the workspace (`.hq/community/posts/`) — not in this plugin repo.** This README is a *contract document*, so it ships with the plugin (`references/knowledge/README.md`), but the actual accumulated data is written to **`.hq/community/posts/`** (tracked *in the calling project*, not this plugin — so it diverges per-project without polluting the plugin/distribution, which is how "specialized to this user / this paper" holds).

### ⭐ Two levels — LOCAL (this paper) + GLOBAL (every ancestor `.hq/`, found by ascent)

The two-level model is unchanged; what changed is that **the ascent is now code, not
prose.** `hq query --ascend` walks every anchor from the cwd upward, nearest first, and
tags each result with the `anchor` it came from.

```
<parent folder of the papers>/.hq/community/posts/   ← ⭐ GLOBAL level — assets this *user* reuses across every paper
        ▲  discovery = ascent (cwd→parent, every anchor above, nearest first)
        │   ⚠️ the ascent never climbs above the user's home directory (ST-3) — the home
        │   directory is the hard lower bound, so unrelated projects can never merge through
        │   an accidental common ancestor above it. This is ENFORCED IN CODE, in hq's
        │   `find_anchors`.
        │
<paper folder>/.hq/community/posts/                   ← LOCAL level — specific to THIS paper (outside <slug>/, carries across sessions)
```

Both levels are **cwd-relative — no absolute path, no env var, no XDG** (oms's "work-root
relative" philosophy as-is, no distribution pollution).

- **The category axis moved from directories to the `topic:` field.** What used to be
  `wiki/convention/foo.md` is a post carrying `topic: convention`. The vocabulary is the
  same one the directories used — 4 local: `convention`·`pattern`·`decision`·`reference`;
  global adds `history`.
- **The post's own directory (`finding/`, `decision/`, `handoff/`, …) is a different
  axis** — it is what a *reader wants to do* with the post, never its subject. Putting
  everything in `finding/` is the named anti-pattern.
- One post = one topic. `subject:` is the mutable-record key: posts sharing a subject form
  a supersede chain with exactly one head, and that head is the current answer.
- ⚠️ `.hq/community/posts/` is a *project-wide* accumulation, so it sits **outside** the per-task `.hq/work/scholar/<slug>/` (output-layout) — not bound to a slug, it lives across sessions and tasks.
- ⚠️ **Only "paper-agnostic reusable assets" go up to the global level** (tendencies, venue formats, history, reusable decisions). Paper-specific knowledge stays local to that paper, and **citation/.bib is permanently forbidden from global promotion** (hallucination risk). This is how it reconciles with oms's "no user-scope" anti-pattern — the global level is *the parent folder's `.hq/`* (still work-root relative), not distributed config, and what flows up is only reusable assets.

> ⚠️ **`history` is oms-specific — omd has no equivalent.** The sibling `oh-my-docs` harness's
> post store deliberately omits `history`: omd has no `init` stage and no document-dedup
> need, so it would be a dead topic there. oms keeps it: `scholar-init` uses it to relate and
> dedup new papers against the user's past work. It is global-only by convention — `scholar-init`
> never posts it locally.

### ⭐ `convention` vs `pattern` — heavy promotion candidates come only from convention (2026-05-31 H6 backport)

The separation of these two is key (`references/learning-protocol.md` §1):
- **`convention`** = *what the output looks like* (section order, caption format, reject reasons). When observed repeatedly it
  escalates to `learned.md` and becomes a **heavy channel promotion candidate** (may harden into a venue default).
- **`pattern`** = *how the user works* (tendencies, working style, preferences). **Light-only — never promoted.**
  Tendencies are not enforcement targets, just memos that every stage *reads* to match tone and level of detail. A `pattern` post
  never rises to `learned.md`.

### ⭐ confidence — repeated observation raises confidence (OMC backport, H6)

Every post carries `confidence: high | medium | low | none`. Observing the same pattern
again means posting a follow-up (`hq post --subject <key> --supersedes <prior-id>`) whose
confidence has climbed (`low → medium → high`) — the poster **never lowers confidence from
the current chain head** on a weaker re-sighting (there is no automatic "keep the higher"
merge; `hq` always makes the newest post canonical, so carrying the higher confidence
forward is the poster's discipline, not the store's). This repetition-driven rise is the
light-channel version of omp's `evidence_count`, the signal that connects to the heavy
gate: when a `convention` post reaches **`confidence: high`**, the pattern's `OBS` has
likely approached `evidence_count ≥ 3` = a good time for `scholar-learn` to look.
confidence is just a qualitative 3-tier grade (+ chain length) —
**no numeric weighted sum or threshold magic number.**

### ⭐ A post holds *conclusion + evidence* together (no label-only — avoids re-reading cost)

A post should not record only the *conclusion (label)* but should hold **the load-bearing evidence that supports that conclusion — concrete cases, control groups,
internal source pointers (which paper-slug/section to revisit) — in the same post.** If only the label is left behind, the next
session has to *re-open the original* to verify the conclusion's basis (re-reading cost = the classic learning failure). "X is a stage axis"
is less reusable than "X juxtaposes two independent contributions across stages without bundling them into chapters — see `<slug>` §table-of-contents."
- ⚠️ **This is a *recommendation* — different from the heavy channel's enumerable-evidence enforcement (`learning-protocol.md` §6.E).**
  The light channel's value is being cheap and frictionless (§1), so missing evidence is not a *reject gate*. It is a discipline
  that says the more evidence you include the better, not a block when it is absent.
- ⚠️ **"Source pointer" = an internal paper-slug/section pointer, not a `.bib` citation** (§6.F · keeping the citation boundary
  invariant below). "Revisit such-and-such part of `<slug>` for this conclusion" is just *internal navigation*; it does not
  write a paper citation into the post store.
- ⚠️ **Append-time consequence (#24)**: `scholar-pilot/SKILL.md` Step 10 mechanically forces `--confidence low` (marked `evidence: none` in the body) on a posted entry that carries neither pointer nor quote, and evidence-less re-observation never raises it — the entry is **still posted**, so this stays consistent with "not a reject gate" above. Procedure detail lives at that Step 10 bullet (not restated here); it remains a prompt-contract rule, no automated compliance check.

Example (conclusion + evidence together, as a post body):

```markdown
## 2026-05-20 — repeated mention of missing ablation (3rd observation → high)
- Conclusion: IROS reviewers cite the absence of ablation as a reject reason.
- Evidence (revisit pointers): missing ablation flagged in `iros-2026-nav` §4 · `iros-2026-grasping` §5 → both added.
  (If re-verification is needed, look at the relevant sections of these two slugs — not a citation, internal navigation.)
```
posted via `hq post --category finding --topic convention --subject iros-reject-patterns --confidence high ...`
(a follow-up to the 2nd-sighting post, `--supersedes <its-id>`).

### `topic: reference` few-shot review examples (scholar-mock-review calibration, R5 #32)

A post with `subject: venue-review-examples-<venue>` holds user-collected real reviews for that venue —
private, hand-pasted by the user, and **never shipped** with the plugin (same non-distribution rule as the rest
of `.hq/community/posts/`). `scholar-reviewer` (lens mode) reads it when present through the same
`hq query --ascend --topic reference` contract already specified below — no new mechanism, no embedding search.
When absent, the lens proceeds on its own judgment only (same graceful-degrade rule as every other topic).

### ⚠️ Open corrections — `open-gap` carry-forward (family status convention)

`hq`'s `status:` enum (`none | needs-experiment | needs-apply-before-retrain | resolved`)
has no `open-gap` value, so the marker rides in `--keywords open-gap` at post time instead
of `status:`. `resolved` is a real, valid status — close a correction with
`hq edit --status resolved`. Enumerate everything still open with
`hq query --keyword open-gap --ascend --json`, then drop any result whose own `status`
already reads `resolved`. `scholar-verify`'s "open post-store gaps" check refuses a clean
PASS while one is neither addressed nor explicitly deferred — so a finding recorded here
cannot silently drop out of the next draft.

---

## Reading it — the `hq query --ascend` contract

The abstract function every stage calls reads the post store via:

```bash
hq query --keyword "<term>" --ascend --topic <category> --json
```

This is the **two-level ascent merge** with provenance: results come back
nearest-anchor-first, each carrying `anchor`, so a reader can always say which level
answered — the nearest anchor is local, any anchor above it is global. Ranking runs per
anchor and the lists are concatenated, because the local store is this project's answer
and the parent's is the fallback, which is what the two levels always meant.

⚠️ **Omitting `--ascend` reads the nearest anchor only.** That is the single most likely way
to lose the global level by accident, and it fails silently — a local-only answer looks
exactly like a complete one.

The post body is **sealed inside** the post: `hq query --post-id <id>` returns it, and the
retrieved text **does not change by a single line** on the way to the reader. Paraphrasing a
retrieved convention is how a store stops being a standard.

Writing goes through `hq post` — never a hand-written file, and never into a `wiki/`
directory, which does not exist. `hq` owns the frontmatter shape (store-spec §4) — there
is no separate syntax card to keep in sync in this plugin.

`.hq/community/INDEX.md` is generated automatically by `hq post`/`hq edit` on every write —
never hand-edited, and not a query surface (recall still runs `hq query`; the index is a
browsable summary for humans).

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
- **Caller/implementation boundary (future replacement point, same idiom as the `hq query` contract above)**: the researcher/verifier merely calls the abstract function `citation_lookup`; it does not know whether the implementation is "Crossref-then-OpenAlex" or a standalone MCP. Only this function's implementation swaps.
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

Reject reasons and defect patterns are **net-new data**. The existing `references/venues.md` (or venue cards) only have `page_limit`·`sections`·`quality_threshold` and *no reject field* — so this store is not migrated from venue cards; rather, inspector sessions *collect it newly* as they critique and load it in.

The loading party = **scholar-pilot's post-capture stage automatically** (right after verify, before terminal — `scholar-pilot/SKILL.md` Step 10). It posts the reject patterns discovered in this session by inspect/verify via `hq post --topic convention --subject <venue>-reject-patterns`. When running standalone stages, the caller may load it directly. **Automatic is the default** — this is the write half of the bidirectional loop above. Skipped if the user passes `--no-post`. Each entry is its own post · pre-check for duplicates with `hq query --subject` · pass through on an empty session · no speculative loading (only what was actually discovered).

---

## ⚠️ citation safety boundary (mandatory — violation collapses the OMS identity)

- **Post content is only a *secondary memo* — never used as a primary citation source.** .bib updates only use primary sources verified by scholar-research (keeping the 3 citation-safety principles). Paper mentions written in a post are not pulled in as citations.
- **Lookup is deterministic keyword matching only — embedding search is permanently forbidden.** Both `hq query` (current) and a future MCP must be deterministic matching. Embedding-similarity search pulls in hallucinated citations, so it is **forbidden now and in the future** (invariant constraint).
- The post store is a *memo that aids prediction*, not a *source of fact*. The inspector marks post excerpts with `[post]` to distinguish them from its own predictions (`[self-prediction]`).
- ⚠️ **No direct light→enforce promotion** (H6 backport, `learning-protocol.md` §6.D): a post (even at confidence high) is only *advice*, not an enforced default. To harden it into a venue default it must pass through the heavy channel of `learned.md` and clear a **human gate**. No matter how high the confidence, a post does not directly change a venue default. In particular `topic: pattern` (tendencies) is permanently light — not a promotion target.
