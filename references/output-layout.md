# Output Layout — directory & naming convention (OMS)

> **What this is**: A data file, not a skill. The OMS agents and stage skills (`scholar-draft`,
> `scholar-drafter`, `scholar-pilot`, `scholar-verifier`) read this card for the single, fixed answer
> to "where does each file go." Same input → always the same path. It is the SSOT for output paths.

**Design principle**: the layout is a *deterministic, fixed structure* — it does not vary by task.
The user sees exactly one finished copy in `outputs/` (the compiled PDF); everything the user does
not need to look at directly (version snapshots, page renders, generated figures, compile temp)
lives in the `.oms/` work area, cleaned at a terminal state or on request.

**Citation-bound asset protection (OMS identity)**: the `.tex`/`.bib` **source** is the user's
asset and stays in *the caller's project source folder* (the paper directory under the work root).
`outputs/` holds **only the compiled `.pdf`**; `.oms/` holds **only version snapshots and
intermediates**. The source is never moved into `.oms/`.

All paths are **relative to the work root** (the caller's working directory or an explicitly named
project root) — never hardcoded to any one machine or absolute path.

---

## 0. The two areas (invariant)

| Area | What goes in | Who reads it | Cleaned? |
|:---|:---|:---|:---:|
| `outputs/<slug>/` | **The one copy the user sees** (`<slug>.pdf`, the compiled output) + optional verify evidence | the user | ❌ never touched automatically (user asset) |
| `.oms/<slug>/` | Everything the user rarely needs directly — version snapshots, page renders, gen-image, compile temp | Claude (analysis) | ✅ confirmed-then-cleaned at terminal |

**Core**: `outputs/` is the "display shelf — this is the result right now," exactly one compiled
PDF. `.oms/` is the "workbench." Version snapshots count as work-product and live on the workbench.
This structurally prevents the output folder from bloating with snapshots and compile artifacts.

**Source location (critical)**: the `.tex`/`.bib` source is **neither** in `outputs/` **nor** in
`.oms/` — it stays in the project source folder the caller designates. OMS compiles *from* that
source *to* `outputs/<slug>/<slug>.pdf`, and snapshots *of* that source into
`.oms/<slug>/versions/`.

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
<project source folder>/                # caller-designated — NOT under outputs/ or .oms/
  <slug>.tex  sections/*.tex  references.bib   # the user's source asset (citation-bound)

outputs/<slug>/
  <slug>.pdf                          # the one copy the user sees (compiled PDF). The PASS copy.
  verify-evidence.md                  # (optional) verification evidence table — for the user

.oms/<slug>/                          # work area — everything the user rarely needs directly
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
```

### 2.1 Invariance rules

- The four subdirectories (`versions/ renders/ gen-image/ tmp/`) are **always this name, this
  place**. They do not change by paper type.
- The structure is identical even when empty (a paper with no generated figures either leaves an
  empty `gen-image/` or omits it — never a different name).
- A new kind of intermediate maps into one of the four (no inventing a new top-level folder). Only a
  genuinely new category that maps to none of them is added by amending this convention.

---

## 3. Version filename rule (deterministic)

Version snapshots under `.oms/<slug>/versions/`:

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
- A snapshot **copies** the source `.tex`/`.bib` to `.oms/<slug>/versions/v{NN}_{date}_{summary}.ext`
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
  directs generated-figure intermediates to `.oms/<slug>/gen-image/`.
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
| `.oms/<slug>/renders/` | ✅ all | Claude analysis, regenerable |
| `.oms/<slug>/gen-image/` | ✅ all | except figures the user asks to keep |
| `.oms/<slug>/tmp/` | ✅ all | LaTeX compile intermediates (.aux/.log/…) |
| `.oms/<slug>/versions/` | ✅ **all but the latest 1 + user-designated milestones** | keep the near-final snapshot, prune the middle |
| `outputs/<slug>/<slug>.pdf` | ❌ never | user asset — excluded from tally and deletion, mentioned only |
| `<project>/…tex/.bib` source | ❌ never | citation-bound source asset — outside cleanup scope entirely |

### 5.3 Safe procedure

1. **Tally** the cleanup targets under `.oms/<slug>/`: size and count.
2. **Ask the user [clean / keep]** — never auto-delete. Default conservative (keep).
3. On "clean" → **delete via a recoverable path** (never permanent `rm`). Environment-adaptive:
   - macOS: use the `trash` CLI if present, else move to `~/.Trash`
   - Linux desktop: `gio trash` / `trash-cli`
   - no-trash environment (CI / container / minimal): confirm "permanent delete" with the user
     explicitly before any `rm`
4. Verify what remains (latest 1 version + milestones, and the source asset, all present).

### 5.4 Absolute rules

- `outputs/` and the project source folder are never touched automatically by any cleanup.
- On "keep," leave everything — no forcing.
- Deletion always goes through a recoverable path (trash). Permanent deletion is forbidden.

---

## 6. Implementation checklist (consumers of this card)

- [ ] `scholar-draft` / `scholar-pilot` / `scholar-drafter` snapshot source into `.oms/<slug>/versions/`
- [ ] the `.tex`/`.bib` source stays in the project source folder (never moved into `.oms/`)
- [ ] `outputs/<slug>/<slug>.pdf` is the only compiled copy the user sees
- [ ] page renders go under `.oms/<slug>/renders/`, compile temp under `.oms/<slug>/tmp/`
- [ ] `.gitignore` excludes `.oms/` and `outputs/*` (keep `outputs/.gitkeep`)
- [ ] slug rule (§1.1) applied at research/intake (non-ASCII → ask once for an ASCII slug)
- [ ] terminal cleanup (§5) goes through AskUserQuestion + trash + excludes the PDF and the source
