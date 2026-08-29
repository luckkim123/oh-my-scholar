# Output Layout — directory & naming convention (OMS)

> **What this is**: A data file, not a skill. The OMS agents and stage skills (`scholar-draft`,
> `scholar-drafter`, `scholar-pilot`, `scholar-verifier`) read this card for the single, fixed answer
> to "where does each file go." Same input → always the same path. It is the SSOT for output paths.

**Design principle**: the layout is a *deterministic, fixed structure* — it does not vary by task.
The user sees exactly one finished copy in `outputs/` (the compiled PDF); everything the user does
not need to look at directly (version snapshots, page renders, generated figures, compile temp)
lives in the `.hq/` work area, cleaned at a terminal state or on request.

**Citation-bound asset protection (OMS identity)**: the `.tex`/`.bib` **source** is the user's
asset and stays in *the caller's project source folder* (the paper directory under the work root).
`outputs/` holds **only the compiled `.pdf`**; `.hq/` holds **only version snapshots and
intermediates**. The source is never moved into `.hq/`.

All paths are **relative to the work root** (the caller's working directory or an explicitly named
project root) — never hardcoded to any one machine or absolute path.

---

## 0. The two areas (invariant)

| Area | What goes in | Who reads it | Cleaned? |
|:---|:---|:---|:---:|
| `outputs/<slug>/` | **The one copy the user sees** (`<slug>.pdf`, the compiled output) + optional verify evidence | the user | ❌ never touched automatically (user asset) |
| `.hq/work/scholar/<slug>/` | Everything the user rarely needs directly — `.md` stage notes (research/methodology/outline), version snapshots, page renders, gen-image, compile temp | Claude (analysis) | ✅ confirmed-then-cleaned at terminal |

**Core**: `outputs/` is the "display shelf — this is the result right now," exactly one compiled
PDF. `.hq/` is the "workbench." Both the `.md` stage notes (the draft's *inputs*) and the version
snapshots count as work-product and live on the workbench. This structurally prevents the output
folder from bloating — and keeps the project source folder holding *only* the citation-bound
`.tex`/`.bib`, never scaffolding.

**Source location (critical)**: the `.tex`/`.bib` source is **neither** in `outputs/` **nor** in
`.hq/` — it stays in the project source folder the caller designates. OMS compiles *from* that
source *to* `outputs/<slug>/<slug>.pdf`, and snapshots *of* that source into
`.hq/work/scholar/<slug>/versions/`.

---

## 1. slug generation (deterministic)

Each job's folder name = **`{YYYY-MM-DD}_{kebab-title}`**.

### 1.1 Algorithm (same input → always the same slug)

```
slug = "{ISO_DATE}_{KEBAB}"

ISO_DATE = job start date YYYY-MM-DD (current date; never an arbitrary past date)
KEBAB    = normalize(title):
  1) English title input (if the title is non-ASCII → ask the user once for an ASCII slug;
     do NOT auto-romanize)
  2) lowercase
  3) spaces / underscores → '-'
  4) drop everything matching [^a-z0-9-]
  5) collapse runs of '-' → single '-', trim leading/trailing '-'
  6) length > 40 → cut at a word boundary at 40
```

Examples:
- "ICLR 2027 Rebuttal" + 2026-05-30 → `2026-05-30_iclr-2027-rebuttal`
- "Kalman Filter Survey" → `2026-05-30_kalman-filter-survey`

### 1.2 Non-ASCII titles (explicit)

Non-ASCII titles (CJK, Cyrillic, …) are **never auto-romanized** — romanization differs by tool and
locale, which breaks "same input → same slug," and it invites filesystem encoding issues (e.g.
NFC/NFD). At the research/intake stage, ask the user once for an ASCII slug. The confirmed slug is
then fixed for the life of the job (never re-asked).

### 1.3 slug collisions (deterministic)

- Same day + same title → same slug → treated as **continuing the same job** (append, not
  overwrite). For a separate job, the user gives a different title.
- Different day + same title → the date prefix separates them naturally.
- The slug is fixed once at job start and is immutable for the job's lifetime.

---

## 2. Fixed directory structure (invariant — does not vary)

```
<project source folder>/                # caller-designated — NOT under outputs/ or .hq/
  <slug>.tex  sections/*.tex  references.bib   # the user's source asset (citation-bound)

outputs/<slug>/
  <slug>.pdf                          # the one copy the user sees (compiled PDF). The PASS copy.
  verify-evidence.md                  # (optional) verification evidence table — for the user

.hq/work/scholar/<slug>/                          # work area — everything the user rarely needs directly
  research/
    *.md                              # research stage: related-work map, gap analysis, axis notes
  methodology/
    *.md                              # ideate stage: concept notes (one per method/contribution) — the draft's SSOT
  outline/
    *.md                              # outline stage: section tree, story arc, figure plan
    gate1.html                        # derived read-only GATE 1 sheet — regenerated from
                                      # outline.md by scripts/oms_outline_view.py, never edited
  consensus/
    {stage}-{role}.md                 # per-run consensus handoff artifacts (`<stage>-<role>.md`) — written only in `--consensus` mode
  versions/
    v{NN}_{YYYY-MM-DD}_{summary}.tex     # .tex/.bib version snapshots (before a large edit)
    v{NN}_{YYYY-MM-DD}_{summary}.bib
  renders/
    current/
      page-{NNN}.png                  # PNG pages of the compiled PDF (inspect/verify, ≥150 dpi)
    v{NN}/                            # (optional) renders kept for a specific version
      page-{NNN}.png
  gen-image/
    {YYYY-MM-DD}_{purpose}.png        # generated figure intermediates (when used)
  tmp/
    *.aux *.log *.out *.blg …         # LaTeX compile intermediates — disposable anytime
  compile-notes.md                    # (optional) compile notes — for Claude's analysis
  reviews-log.md                      # (optional) scholar-mock-review verdict history — append-only, create-if-absent, never touches .tex/.bib
  research-log.md                     # (optional) dated project narrative memory — append-only, create-if-absent, never a .bib source (see §2.4)

.hq/config/scholar/verified-citations.json    # cite-guard allowlist — written ONLY by scripts/verify_bib_entry.py --record (atomic, oms_atomic)

.hq/runtime/scholar/                  # cross-slug mechanism state (NOT per-job)
  pilot-<slug>.json                   # pilot pipeline stage state — written ONLY by scripts/oms_state.py write (atomic, oms_atomic)
  revise-<slug>.json                  # revise-loop round/strike ledger — written ONLY by scripts/oms_state.py revise-* (atomic, oms_atomic)

.hq/community/posts/                           # project-wide accrual — NOT per-job (carries across sessions)
  <category>/<NNN>-<slug>.md          # one immutable post per file, `hq post` owns naming and numbering;
                                       # topic: convention|pattern|decision|reference|history in frontmatter —
                                       # history is global-level only (see references/knowledge/README.md)

.hq/community/INDEX.md                # generated by `hq post`/`hq edit` on every write, never hand-edited

.hq/community/reading/                         # personal reading corpus — NOT per-job (sibling of posts/, outlives any one paper project — see §2.5)
  <citekey>.md                        # one structured deep-read note per external paper — written ONLY by the calling session (scholar-read)
                                       # NOT CITABLE — secondary memo, never a .bib source (invariant 2); <citekey> is a filename convention, NOT a BibTeX key

.hq/config/scholar/notepad.md                       # cross-slug workbench notepad (NOT per-job, like `.hq/runtime/scholar/`) — see §2.3
```

### 2.1 Invariance rules

- The subdirectories split into two layers, both **always this name, this place** (they do not vary
  by paper type):
  - **`.md` stage layer** (`research/ methodology/ outline/`) — the `.md` intermediates produced by
    the `.md`-stage skills (`scholar-research`, `scholar-ideate`, `scholar-outline`). These are the
    draft's *inputs* (concept SSOT, gap map, section plan), **not** the citation-bound `.tex`/`.bib`
    source. They are work-product (scaffolding for the draft), so they live on the workbench
    (`.hq/`), **never inside the project source folder** (`paper/…`). Putting them next to the
    `.tex`/`.bib` would mix scaffolding with the user's citation-bound asset — exactly what §0's
    source-protection rule forbids.
  - **`.tex` pipeline layer** (`versions/ renders/ gen-image/ tmp/`) — snapshots and compile
    artifacts of the `.tex`/`.bib` source.
- The structure is identical even when empty (a paper with no generated figures either leaves an
  empty `gen-image/` or omits it — never a different name; likewise an early-stage paper may have
  only `research/` populated).
- A new kind of intermediate maps into one of the existing subdirectories (no inventing a new
  top-level folder). Only a genuinely new category that maps to none of them is added by amending
  this convention.
- Two narrative-memory files sit directly under `.hq/work/scholar/<slug>/` (not inside either layer's
  subdirectories, so the two-layer split above doesn't cover them) and are equally invariant in
  name/place: `reviews-log.md` (mock-review verdict history) and `research-log.md` (dated project
  narrative memory — see §2.4). Both are append-only, create-if-absent, written by the calling
  session, and **KEEP** at T18 cleanup (§5).
- `.hq/community/reading/` sits **outside** the per-slug `.hq/work/scholar/<slug>/` tree (sibling of `.hq/community/posts/`, not
  per-job) — a reading note outlives any one paper project. It is equally invariant in name/place;
  see §2.5 for the entry format.

### 2.2 State schema (pipeline mechanism state)

`.hq/runtime/scholar/` holds cross-slug **mechanism state** — not paper content, not citations. Both shapes
below are written **only via `scripts/oms_state.py`** (atomic, `oms_atomic.atomic_write_json`); no
other script or skill writes these files directly.

**`pilot-<slug>.json`** — the pilot pipeline's current stage/gate, written by `oms_state.py write`:

```json
{
  "slug": "2026-07-13_paper-slug",
  "stage": "research|deepen|ideate|outline|draft|inspect|verify|revise|submission|terminal",
  "gate_status": "pending|approved|revise|abort|null",
  "open_fail_ids": ["defect-id", "…"],
  "paper_root": "/abs/cwd/where/the/pipeline/runs",
  "updated_at": "2026-07-13T09:00:00+00:00"
}
```

On create, `write` always initializes the full key set (`gate_status: null`, `open_fail_ids: []`,
`paper_root` = resolved cwd unless `--paper-root` overrides) so downstream consumers read stable
keys instead of `.get()`-guessing. On merge, unnamed fields (including `paper_root`) are preserved.

**`revise-<slug>.json`** — the revise-loop's round/strike ledger, written by `oms_state.py
revise-start`/`revise-round`/`strike`/`revise-end`:

```json
{
  "slug": "…",
  "active": true,
  "round": 2,
  "round_id": "uuid4-of-current-round",
  "max_rounds": 5,
  "ttl_hours": 6,
  "strikes": {"defect-id": 2},
  "stop_blocks": 0,
  "paper_root": "/abs/cwd/where/the/loop/was/started",
  "started_at": "2026-07-13T09:00:00+00:00",
  "status": "live|done|stopped|abort"
}
```

**Who reads them**: `pilot-<slug>.json` is read by `scholar-pilot`'s `--from` resume (proposes the
recorded `stage`), the Stop guard, and the SessionStart advisory; `revise-<slug>.json` is read by
the same Stop guard (a live marker means the loop is still running) and the revise-loop itself
(round/strike counters).

**Cleanup fate**: both files are per-slug mechanism state, not paper content — at pilot terminal
(GATE 3 confirm) they are removable together with the slug's work area (see §5 table).

### 2.3 notepad tiers (`.hq/config/scholar/notepad.md`)

`.hq/config/scholar/notepad.md` is a **cross-slug workbench notepad** (cross-slug like `.hq/runtime/scholar/`, not per-job —
see §2). It is a single `.md` file with three fixed sections (`## <name>`), each with its own
write/prune contract:

| Tier | Write mode | Prune | Owner |
|:---|:---|:---|:---|
| `## Priority Context` | **replace-on-write** — pilot entry and every GATE transition rewrite the whole section | n/a (rewritten, not accumulated) | scholar-pilot |
| `## Working Notes` | dated append — new entries under `### YYYY-MM-DD` sub-headings | entries older than **7 days** pruned automatically at pilot entry (the only automated deletion, and it is scoped to this tier only) | scholar-pilot |
| `## Manual` | human-owned | **never** — automation never writes or prunes this section | human |

- `## Priority Context` must stay short — bounded to **2,000 chars** — because it is what
  `SessionStart(compact)` re-injects verbatim after context compaction (see
  `hooks/scholar_resume_emit.py`). Replace-on-write (not append) keeps it current instead of
  growing unbounded.
- `## Working Notes` is where session-scoped observations accumulate across a pipeline run; the
  7-day prune keeps it from becoming a permanent log while still surviving a single long pipeline.
- `## Manual` is the human's own space in the same file — automation must not touch it, ever
  (no write, no prune), regardless of age.

### 2.4 research-log entry format (`.hq/work/scholar/<slug>/research-log.md`)

`.hq/work/scholar/<slug>/research-log.md` is a **durable, dated, append-only project narrative memory** — "what
we tried / decided / dropped, and why" — sibling of `reviews-log.md` directly under `.hq/work/scholar/<slug>/`.
Written **only by the calling session** (never a dispatched agent), create-if-absent, append-only
(never rewritten, never pruned).

**Entry format**:

```
## YYYY-MM-DD — <context: pilot|discuss|read|manual>
- tried: …
- decided: …
- dropped: … — and why
```

- `<context>` names the stage that produced the entry (`pilot` for scholar-pilot Step 10; `discuss`
  / `read` for the R5 scholar-discuss / scholar-read skills; `manual` for a human-added entry).
- Free-prose bullets under the dated heading cover `tried / decided / dropped — and why` — no fixed
  machine schema beyond the heading line.
- ⚠️ **secondary memo only** (same discipline as the post store, `references/knowledge/README.md`): a citation
  key that appears in a research-log entry is never treated as citation authority, and this file is
  **never a `.bib` source** — the only door into the bibliography stays scholar-research →
  human-confirmed `.bib` (invariant 2).

**Who writes it**: `scholar-pilot` Step 10 appends a run summary (context `pilot`: stages executed,
GATE outcomes, major decisions, dropped directions) alongside the post-capture step. `--no-log`
opts out, mirroring `--no-post`.

**Cleanup fate**: KEEP — see §5.

### 2.5 reading note format (`.hq/community/reading/<citekey>.md`)

`.hq/community/reading/` is a **personal reading corpus** — sibling of `.hq/community/posts/`, NOT under any one
`.hq/work/scholar/<slug>/` — because a deep-read note outlives any one paper project (produced by the R5
`scholar-read` skill, T2). Written **only by the calling session** (never the dispatched
`scholar-researcher` agent, same writer-identity carve-out as `reviews-log.md`/`research-log.md`),
create-if-absent, one file per external paper.

- `<citekey>` is a **filename convention** (`<firstauthor><year>-<short-slug>`), explicitly **NOT**
  a BibTeX key — no `.bib` entry is implied or created by this file existing.
- Every note's **first line** is the mandatory header:
  `> NOT CITABLE — secondary memo. A .bib entry may only be created via scholar-research verification.`
- ⚠️ **secondary memo only** (same discipline as the post store and `research-log.md`): a citation key
  that appears in a reading note is never treated as citation authority, and this file is **never a
  `.bib` source** — the only door into the bibliography stays scholar-research → human-confirmed
  `.bib` (invariant 2).
- Body sections (produced by `scholar-researcher` `mode=deep-read`): `## Paper identity` (the
  mechanical `scripts/verify_bib_entry.py` verdict, restated verbatim — a `RETRACTED` verdict is
  marked loudly), `## Claims` (verbatim quote + locator per claim), `## Method`, `## Evidence`,
  `## Limitations`, `## Relation to my work` (only when project context was supplied), `## Open
  questions`.

**Who writes it**: `scholar-read` resolves the input, runs the identity pre-check (no `--record`),
dispatches a single `scholar-researcher` `mode=deep-read` call, and writes the note.

**Cleanup fate**: KEEP — see §5.

---

## 3. Version filename rule (deterministic)

Version snapshots under `.hq/work/scholar/<slug>/versions/`:

**`v{NN}_{YYYY-MM-DD}_{summary}.{tex|bib}`**

```
v{NN}        = zero-padded 2-digit version number. v01, v02, … v10. (so v1 and v10 sort right)
{YYYY-MM-DD} = the snapshot's date
{summary}    = short kebab-case summary (same KEBAB rule as §1.1, length ≤ 30)
```

Examples:
- `v01_2026-05-30_initial.tex`
- `v02_2026-05-31_methodology-rewrite.tex`

### 3.1 When to snapshot

- **Only before a large edit** (section rewrite, structural change, many sections affected). Not for
  a one-line tweak or a single citation fix — keeps the version count bounded.
- A snapshot **copies** the source `.tex`/`.bib` to `.hq/work/scholar/<slug>/versions/v{NN}_{date}_{summary}.ext`
  (copy, not move — the source stays in the project folder and work continues on it).
- `NN` = max existing version number + 1; if empty, `v01`.

### 3.2 Why zero-pad

`ls` sorts lexically: without padding, `v1, v10, v2` is wrong. With `v01, v02, … v10`, chronological
order = version number order = sort order, always.

---

## 4. gen-image / render PNG naming

### 4.1 gen-image (`gen-image/`)

`{YYYY-MM-DD}_{purpose}.png` — purpose is kebab. e.g. `2026-05-30_architecture-fig.png`.

- **Separate from any image tool's own default path**: in a *paper workflow* the caller explicitly
  directs generated-figure intermediates to `.hq/work/scholar/<slug>/gen-image/`.
- ⚠️ A generated figure is an *intermediate* — the figure that ships in the paper is referenced from
  the `.tex` source and is a citation-bound asset decision, never auto-fabricated.

### 4.2 render PNGs (`renders/`)

- inspect/verify renders the compiled PDF to PNG → `renders/current/page-{NNN}.png`. NNN zero-padded
  3 digits.
- Re-rendering the same job overwrites `renders/current/` (only the latest matters). Keep a specific
  version's render only when needed, under `renders/v{NN}/`.

---

## 5. Terminal cleanup (T18 — pilot end-of-pipeline)

### 5.1 Trigger

- (a) the pilot pipeline reaches terminal (verify PASS + GATE 3 user confirmation), **or**
- (b) the user explicitly says "clean up" / "we're done."

### 5.2 Scope (intermediates + old versions together)

| Target | Clean | Note |
|:---|:---:|:---|
| `.hq/work/scholar/<slug>/renders/` | ✅ all | Claude analysis, regenerable |
| `.hq/work/scholar/<slug>/gen-image/` | ✅ all | except figures the user asks to keep |
| `.hq/work/scholar/<slug>/tmp/` | ✅ all | LaTeX compile intermediates (.aux/.log/…) |
| `.hq/work/scholar/<slug>/versions/` | ✅ **all but the latest 1 + user-designated milestones** | keep the near-final snapshot, prune the middle |
| `.hq/work/scholar/<slug>/consensus/` | ✅ all | per-run `--consensus` mode handoff artifacts — a workspace, T18 cleanup target |
| `.hq/runtime/scholar/pilot-*.json` / `revise-*.json` | ✅ clean | at terminal, after GATE 3 (mechanism state, not paper content) |
| `.hq/work/scholar/<slug>/reviews-log.md` | ❌ **KEEP** | durable mock-review verdict history — lives in `.hq/work/scholar/<slug>/` but is never aggregated or deleted at T18 (unlike renders/gen-image/tmp/versions/consensus) |
| `.hq/work/scholar/<slug>/research-log.md` | ❌ **KEEP** | durable dated project narrative memory (tried/decided/dropped, §2.4) — lives in `.hq/work/scholar/<slug>/` but is never aggregated or deleted at T18; never a `.bib` source |
| `.hq/community/reading/*.md` | ❌ **KEEP** | personal reading corpus (§2.5) — sibling of `.hq/community/posts/`, outside any one slug's T18 cleanup scope entirely; never a `.bib` source |
| `outputs/<slug>/<slug>.pdf` | ❌ never | user asset — excluded from tally and deletion, mentioned only |
| `<project>/…tex/.bib` source | ❌ never | citation-bound source asset — outside cleanup scope entirely |

### 5.3 Safe procedure

1. **Tally** the cleanup targets under `.hq/work/scholar/<slug>/`: size and count.
2. **Ask the user [clean / keep]** — never auto-delete. Default conservative (keep).
3. On "clean" → **delete via a recoverable path** (never permanent `rm`). Environment-adaptive:
   - macOS: use the `trash` CLI if present, else move to `~/.Trash`
   - Linux desktop: `gio trash` / `trash-cli`
   - Windows: send to the Recycle Bin via PowerShell
     (`powershell -c "(New-Object -ComObject Shell.Application).Namespace(0).ParseName('<abs-path>').InvokeVerb('delete')"`),
     or the `recycle-bin` / `trash` module if installed; never `Remove-Item` permanently
     (documented; unverified on Windows)
   - no-trash environment (CI / container / minimal): confirm "permanent delete" with the user
     explicitly before any `rm`
4. Verify what remains (latest 1 version + milestones, and the source asset, all present).

### 5.4 Absolute rules

- `outputs/` and the project source folder are never touched automatically by any cleanup.
- On "keep," leave everything — no forcing.
- Deletion always goes through a recoverable path (trash). Permanent deletion is forbidden.

---

## 6. Implementation checklist (consumers of this card)

- [ ] `scholar-research` / `scholar-ideate` / `scholar-outline` write their `.md` notes into
      `.hq/work/scholar/<slug>/research|methodology|outline/` — **never** into the project source folder (`paper/…`)
- [ ] `scholar-draft` / `scholar-pilot` / `scholar-drafter` snapshot source into `.hq/work/scholar/<slug>/versions/`
- [ ] `scholar-outline` writes per-run consensus handoff artifacts into `.hq/work/scholar/<slug>/consensus/` (`--consensus` mode only); T18 cleans them at terminal
- [ ] the `.tex`/`.bib` source stays in the project source folder (never moved into `.hq/`)
- [ ] `outputs/<slug>/<slug>.pdf` is the only compiled copy the user sees
- [ ] page renders go under `.hq/work/scholar/<slug>/renders/`, compile temp under `.hq/work/scholar/<slug>/tmp/`
- [ ] `.gitignore` excludes `.hq/work/`, `.hq/runtime/`, and `outputs/*` (`.hq/config/`, `.hq/community/` stay tracked; keep `outputs/.gitkeep`)
- [ ] slug rule (§1.1) applied at research/intake (non-ASCII → ask once for an ASCII slug)
- [ ] terminal cleanup (§5) goes through AskUserQuestion + trash + excludes the PDF and the source
- [ ] **`.tex`↔`.hq` sync** (`learning-protocol.md` §8): after `scholar-draft`/`scholar-revise` makes a
      structure-affecting `.tex` change (section move/merge/split, title change, major equation, \cite added),
      `.hq/work/scholar/<slug>/outline/outline.md` + relevant `.hq/work/scholar/<slug>/methodology/*.md` (+ decision log if present)
      are updated to match the `.tex` **in the same task** — a "revise PASS" is not complete until they agree
- [ ] `.hq/community/INDEX.md` is regenerated automatically by `hq post`/`hq edit` after every post
      change — never hand-edited (`references/knowledge/README.md`)
- [ ] `scholar-mock-review` appends one dated entry per completed review to `.hq/work/scholar/<slug>/reviews-log.md`
      (create-if-absent, append-only, never touches `.tex`/`.bib`) — written by the calling session, not the
      dispatched `scholar-reviewer` agent (§5 KEEP fate — never aggregated for T18 cleanup)
- [ ] `scholar-pilot` appends one dated entry per pipeline run to `.hq/work/scholar/<slug>/research-log.md`
      (create-if-absent, append-only, never a `.bib` source, format in §2.4; `--no-log` opts out) —
      written by the calling session at Step 10, alongside the post-capture step (§5 KEEP fate)
- [ ] `scholar-read` writes one `.hq/community/reading/<citekey>.md` note per external paper (create-if-absent,
      NOT CITABLE header first line, format in §2.5) — written by the calling session, never the
      dispatched `scholar-researcher` agent; never a `.bib` source; no `--record` (§5 KEEP fate)
