# GATE 1 outline view — design

- **Date**: 2026-08-12
- **Status**: approved, ready for execution plan
- **Target version**: 0.14.0 (minor — new feature)
- **Scope**: oms only. The sibling omd change is deferred to its own spec (see §10).

---

## 1. Problem

`scholar-outline`'s GATE 1 is the cheapest moment in the pipeline to reject a
structure: the outline exists, the `.tex` does not. The gate's own text says so
(`skill-bodies/scholar-outline/SKILL.md:73-78` — proceed / revise / abort, no
automatic pass).

Two things weaken it in practice.

**The gate output is read serially.** `outline.md` is presented as running
markdown in the terminal. A reader scrolling section 7 cannot see section 2, so
defects that live *between* units — a section that never appears in the
necessity chain, a chain link whose justification is blank — are structurally
hard to notice. Reading each section in turn cannot surface a gap that only
exists across sections.

**The human gate has no mechanical floor, while the agent gates do.** The
`--consensus` path already enforces rubber-stamp prevention mechanically: the
next stage refuses to proceed unless the previous role's `.md` exists on disk
(`skill-bodies/scholar-outline/SKILL.md:92`). GATE 1, where a *human* approves,
has no equivalent — nothing surfaces "this outline has four sections with no
stated proposition" before the human types "proceed". The asymmetry is that we
distrust agents and trust humans, when the human is the one reading a wall of
prose under time pressure.

## 2. Scope

**In scope.** A derived, read-only visual rendering of `outline.md`, produced at
GATE 1, carrying mechanically-detectable structural gaps.

**Out of scope, deliberately.**

- Any judgment call (near-duplicate sections, "is this arc convincing"). The
  renderer detects *absence*, never *quality*. Judgment stays with
  `scholar-inspector` and the human.
- Editing through the rendered view. It is a view; the `.md` is the SSOT.
- omd's equivalent change. omd has no persisted outline file at all (§10).

## 3. Current state (verified 2026-08-12)

| Fact | Source |
|:---|:---|
| Outline path is fixed and documented | `skill-bodies/scholar-outline/SKILL.md:60`, `references/output-layout.md:97-98` |
| Per-section fields: Purpose, Core message, Proposition to argue, Dependent citations, optional `researcher recheck needed` | `agents/scholar-planner.md` `<Output_Format>` |
| Story arc is an explicit necessity chain (`→ establishes` / `→ why this is needed`) | same |
| Word budget target is `page_limit × 500` | same; venue card `references/venues.md` |
| No script parses or renders the outline today | `scripts/` — all seven serve other purposes |
| Skills invoke scripts as `python3 <plugin>/scripts/<name>.py` | `scholar-pilot`, `scholar-revise`, `scholar-verify`, `scholar-read`, `scholar-research` |
| `skills/<name>/SKILL.md` is a dispatch shim; `skill-bodies/` is authoritative | `tests/conftest.py:1-11` |

The necessity chain is the load-bearing discovery: oms already records the
inter-section justification that makes a broken narrative chain detectable. No
schema change to the planner is required.

## 4. Design

### 4.1 Artifact and path

`scripts/oms_outline_view.py` reads `.oms/<slug>/outline/outline.md` and writes
`.oms/<slug>/outline/gate1.html` — a self-contained HTML page (no external
requests: no CDN scripts, no remote fonts, no remote images).

`references/output-layout.md:98` currently declares the directory contents as
`*.md`; it is amended to admit the generated `.html`.

### 4.2 What a card shows

One card per section, in section order. Every field already exists in the
planner's output schema — nothing new is asked of the planner.

| Card element | Source field |
|:---|:---|
| Section number and name | Section tree heading (`#### §N. …`) |
| Purpose | `**Purpose**` |
| Core message | `**Core message**` |
| Proposition to argue | `**Proposition to argue**` |
| Word budget, drawn as a share of the total | `[word budget: N words]` |
| Citation keys, as chips | `**Dependent citations**` |
| Link to the next section | Story arc `→ why this is needed` |

The link text sits *between* cards rather than inside them, because it is a
property of the transition, not of either section.

### 4.3 Flags — nine, all mechanical

The renderer reports absence only. Each flag is decidable by inspection of the
text, with no judgment:

1. A section missing any of: Purpose, Core message, Proposition to argue, word
   budget.
2. A section present in the tree but absent from the necessity chain.
3. A chain link whose `why this is needed` is empty.
4. A section carrying `researcher recheck needed` (already an explicit marker in
   the schema).
5. Word-budget total exceeding the venue's `page_limit × 500`. Both numbers are
   read from the outline's own `### Venue constraints` block, which states
   `page_limit: [N] pages → word budget total: [N×500] words`. The renderer does
   not read `references/venues.md` or any venue instance file — it compares the
   summed per-section budgets against the total the outline itself declares.
6. A citation key appearing in the `### Full citation-dependency mapping` table
   but in no section's `**Dependent citations**` field, or the reverse. This is
   an inconsistency between the outline's two representations of the same data,
   which is mechanical to detect and invisible when reading serially.

7. A necessity-chain entry whose section number has no matching entry in the
   section tree. This is the reverse direction of flag 2: flag 2 catches a
   section that never made it onto the chain, but nothing originally caught the
   opposite — a chain entry naming a section that was never parsed as a section
   at all, typically because its heading is malformed (a missing `§`, for
   example). Without this flag a whole section can silently drop out of the
   tree while the chain still refers to it, and the sheet would report "no
   mechanical gap found" over an outline that is missing a section — the
   accelerated-rubber-stamp failure this feature exists to prevent.
8. A section number that appears more than once in the tree. Duplicate numbers
   make the per-section flag-to-card association ambiguous — a flag raised
   against one occurrence can render on both cards — so the renderer reports
   the duplication itself rather than silently mis-attributing a flag to a
   healthy section.
9. No section tree parsed at all. Without this the flags above are vacuous on a
   malformed outline — zero sections means zero per-section flags, so the most
   broken possible input would render as a clean page. This flag is what makes
   §4.6's "renders as a page of flags" true rather than aspirational.

Near-duplicate detection is excluded: deciding that two sections say the same
thing is judgment, and putting judgment in the renderer would make it a reviewer
that nobody reviews.

Three exemptions keep healthy outlines clean, and each corresponds to something
the planner's schema legitimately omits:

- The **last** chain entry ends with `→ paper contribution complete` instead of
  `→ why this is needed`. It is terminal by construction, so flag 3 never fires
  on it.
- `researcher recheck needed` is documented as "omit otherwise", so its absence
  is normal and only its presence is reported.
- Flag 5 is skipped when the venue states no page limit (`page_limit: null`),
  and flag 6 is skipped when the outline carries no
  `### Full citation-dependency mapping` block at all — a missing summary table
  is not a defect in the argument, only a disagreement between two present
  representations is.

The `### Word Budget summary` table is not parsed. Per-section budgets come from
the section headings, which are the field the planner is instructed to emit; a
second parse of the same numbers would invent a seventh check nobody asked for.

### 4.4 Components

One new file, two pure functions plus a thin CLI:

```
parse_outline(text: str) -> Outline      # no I/O
render_html(outline: Outline) -> str     # no I/O
```

```
python3 <plugin>/scripts/oms_outline_view.py <outline.md> [-o <out.html>]
```

Default output path is `gate1.html` beside the input. Keeping parse and render
pure makes both testable without touching the filesystem, matching the house
style in `tests/`.

### 4.5 Data flow, and the one rule that keeps it honest

```
planner  ->  outline.md   (SSOT, unchanged by this feature)
                 |
                 |  read-only parse
                 v
             gate1.html   (derived view)
                 |
                 v
       GATE 1: proceed / revise / abort   <- human
                 |
                 |  on revise
                 v
      planner re-delegated -> outline.md updated -> re-render
```

**The rendered view is never edited.** Approval and revision land in
`outline.md` and the sheet is regenerated. A derived view that can be edited
becomes a second source of truth, and the two drift — the failure mode this
repo already guards against by declaring `.md` the SSOT and MCP a mere
accelerator (`skill-bodies/scholar-outline/SKILL.md:88-95`).

### 4.6 Error handling

**Content problems never raise.** The outline is LLM-generated markdown; a
heading may be malformed, a field may be missing, a table may be truncated.
Every such case resolves to a flag, not an exception. A parser that throws on a
malformed outline would hide exactly the outline that most needs looking at.

The single raising condition is a missing input file, which is an operator
error rather than a content signal.

A consequence worth stating: a completely unparseable outline renders as a page
of flags. That is the correct output — it says the structure is not yet in a
shape a human can approve.

### 4.7 Publishing, and degrading without it

The script writes a file and stops. It never publishes.

The skill, after generating the file, publishes it as an artifact when the
running harness offers that capability, and reports the file path when it does
not. This mirrors the existing accelerator convention: the durable `.md`/file
path is the guarantee, the richer surface is opportunistic, and its absence is a
graceful degrade rather than an error. oms remains standalone — the gate
functions with nothing but a browser, or with nothing but a text editor.

## 5. Files touched

| File | Change |
|:---|:---|
| `scripts/oms_outline_view.py` | new — parser, renderer, CLI |
| `tests/test_oms_outline_view.py` | new — see §6 |
| `skill-bodies/scholar-outline/SKILL.md` | `<Steps>` step 6 (GATE 1) gains the render call and the present-or-degrade instruction |
| `references/output-layout.md` | line 98 admits the generated `.html` |
| `CHANGELOG.md` | new `### Added` under `[Unreleased]` |
| `.claude-plugin/plugin.json` | version bump at release |

`skills/scholar-outline/SKILL.md` is **not** touched. It is a 13-line dispatch
shim; content added there is never surfaced.

## 6. Testing

`tests/test_oms_outline_view.py`, following the house convention (pytest, plain
asserts, `conftest.skill_md()` for skill-text locks):

- A complete fixture outline parses every field and produces zero flags.
- Seven fixtures, one per flag, each producing **exactly** its own flag and no
  others — this is what stops a flag from firing on healthy outlines. Each is
  the complete fixture with one targeted mutation, so the delta under test is
  visible in the test body.
- The three exemptions each get a test: a terminal chain entry does not trip
  flag 3, an absent `researcher recheck needed` does not trip flag 4, and a null
  page limit skips flag 5.
- Garbage input raises nothing and produces exactly the no-section-tree flag.
- Rendered HTML contains no external URL and no `<script src=`, locking the
  self-contained property.
- `skill-bodies/scholar-outline/SKILL.md` mentions the render step within its
  GATE 1 window, scoped with `.index()` per house style.

## 7. Non-goals

Near-duplicate detection; cross-checking citation keys against
`.oms/state/verified-citations.json`; a defect-only filter toggle (a paper has
5–30 sections, which fit on one screen); editing from the view; theme options; a
new declarative flag in the venue card.

## 8. Release

`0.13.1 -> 0.14.0`. The three doc/packaging fixes already sitting in
`[Unreleased]` ship with it. Version consistency spans four surfaces —
`.claude-plugin/plugin.json` (anchor), `CHANGELOG.md` top released entry, the
latest `v*` git tag, and the omha card at `<OMHA_ROOT>/cards/oms.json` — checked
by `scripts/sync_version.py`.

## 9. Decision deferred to implementation

Showing Purpose, Core message, and Proposition to argue in full makes a tall
card; roughly five fit on a screen. Whether Proposition collapses behind a
disclosure control depends on how the first real render reads, and cannot be
settled from the spec. The implementer decides at first render and records the
choice in the execution plan. Either resolution satisfies this design; nothing
downstream depends on it.

## 10. Follow-up: the omd counterpart

omd's `docs-plan` has the same gate and the same argument applies, but it cannot
consume this design as-is: **omd has no outline file**. In `--direct` mode the
outline is presented conversationally and never written
(`skills/docs-plan/SKILL.md:44`); in `--consensus` mode only the companion
`plan.md` has a stated path; `references/output-layout.md` has no outline entry
at all. Its Outline table also carries no inter-unit link field, so the
necessity-chain flags have no substrate there.

Persisting omd's outline is a change to a path SSOT consumed by `docs-build`,
`doc-builder`, `doc-verifier`, and `docs-pilot`. It is worth doing on its own
merits — a gate artifact that survives compaction — and deserves review on those
merits rather than riding along with a visualization. It gets its own spec.
