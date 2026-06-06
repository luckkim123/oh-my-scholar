# Learning Protocol — oms's generic→specialized self-evolution (SSOT)

This card is the single source of truth for **how oms gets smarter about *how this user
writes papers* the more it is used**. It is the oms-domain backport of omp's identity card:
shipped generic, specialized in place. Every skill or agent that reads, writes, or promotes
paper-writing knowledge MUST obey this card — `scholar-learn`, the `scholar-inspector`
agent (read-only judgment reuse), `scholar-pilot`'s wiki-capture step, and the `wiki/`
accumulation behavior.

> **Identity in one line.** oms ships as a *generic* paper harness (same logic for everyone)
> and becomes *specialized* purely through accumulated knowledge about this user's venues and
> working style. Specialization is data, not code. This card defines exactly how that data
> accumulates — safely, with the right friction in the right place.

The path contract for where this data lives is `references/output-layout.md`. The human venue
catalog is `references/venues.md`. This card governs the *dynamics* — what flows into those
files, when, and under whose approval.

> **Provenance.** Backported from omp's `references/learning-protocol.md` (the omp heavy
> channel) on 2026-05-31, adapted to the paper domain. Where omp promotes *file-moving rules*
> into `rules.json`, oms promotes *venue/working defaults* into `venues.md`. The two safety
> properties — human gate, deterministic grep recall — are carried over verbatim. The
> citation-safe invariant (§6.F) is oms-specific and absolute.

---

## 1. The two channels (asymmetric on purpose)

oms learns through **two channels with deliberately different friction**. The asymmetry is
the whole design: a promoted default changes what future paper work *assumes by default*, so
it pays a human gate; patterns and decisions are cheap memory, so they accumulate freely.

```
                          OBSERVATION (something oms noticed about how you write)
                                              │
                ┌─────────────────────────────┴──────────────────────────────┐
                │                                                             │
        is it a candidate DEFAULT                              is it a PATTERN / DECISION
        (could auto-apply to future paper work)?               (a note worth recalling later)?
                │                                                             │
        ── HEAVY CHANNEL (gated) ──                              ── LIGHT CHANNEL (no gate) ──
                │                                                             │
   learned.md  ──> scholar-learn ──> scholar-inspector          wiki/<cat>/*.md  (auto-append)
   (observation     (promotion       (read-only judgment)               │
    accrues)         skill)               │                      next session: deterministic
                │                          ▼                      grep recall (no model search)
                │                  HUMAN APPROVAL GATE                     │
                │                          │                               ▼
                │                          ▼                      injected as context,
                └────────────────> venues.md  (specificity bump)  never auto-applied as default
```

### Heavy channel — DEFAULTS (`learned.md` → `scholar-learn` → human gate → `venues.md`)

A **default** is anything a downstream oms stage would *assume without being told*: a venue's
required sections (e.g. "IROS papers always include an Ablation section"), a structural
ordering ("related work before method"), a self-citation ceiling, a per-venue page/format
habit. Because a promoted default silently shapes every future paper for that venue, it is a
heavy, consequential decision. It therefore travels the gated path:

1. Observations accrue in `.oms/learned.md` (any read-only stage may append; see §2).
2. `scholar-learn` reuses `scholar-inspector` (read-only) to judge which observations are ripe
   (§3) and to draft the `venues.md` edit + the specificity recompute (§4).
3. **A human approves the promotion.** This is the single most important gate in oms.
4. On approval, the default is written into `venues.md`, `specificity` is recomputed, the
   observation's id is recorded as provenance (`learned_refs`), and any paired human narrative
   is regenerated in the same pass so the catalog never drifts from its provenance.

`scholar-inspector` **judges only** — it never writes `venues.md` itself in the learn flow;
the human gate plus `scholar-learn`'s write step perform the write. (Design §8 #4: judgment ≠
approval ≠ enforcement — the three-way separation that forbids self-approval.)

### Light channel — PATTERNS / DECISIONS (`wiki/*.md` auto-append, grep recall, no gate)

A **pattern or decision** is a note about how this user works that is useful to *remember* but
is not an enforceable default: "the user reviews the conclusion first", "prefers terse prose",
"this framing of the contribution landed well". These are cheap. They auto-append to
`.oms/wiki/<category>/*.md` during any stage, with **no approval gate**, and are recalled next
session by **deterministic grep** over `wiki/` (§5). A wiki note is *context*, never an
enforced default — it can inform a future default proposal, but it cannot itself change what a
stage assumes. That promotion (wiki insight → candidate default) only happens by re-entering
the heavy channel through `learned.md`.

### ⭐ Light-channel categories (4: the `pattern/` category is the oms/omd addition)

omp's light channel had `convention/decision/reference`. oms adds **`pattern/`** — notes about
the *user as a person* (how they work), distinct from `convention/` (how the *output* looks):

| category | holds | heavy-promotion candidate? |
|:---|:---|:---|
| `convention/` | how the output looks (section order, caption style) | **yes** — the source of heavy candidates |
| `pattern/` | how the user works (`work-profile.md`, `working-style.md`, `preferences.md`) | **no** — disposition is not enforceable; light only |
| `decision/` | decisions made + rationale, what worked well | no |
| `reference/` | pointers to external material | no |

`pattern/` is light-only on purpose: a *disposition* ("prefers terse", "reviews conclusion
first") is advice every stage reads to tune tone/depth, not a default to enforce. Only
`convention/` observations escalate to `learned.md`.

### Channel routing rule (which channel does an observation take?)

| The observation… | Channel | Why |
|:---|:---|:---|
| could be auto-applied by a future stage (venue required sections, ordering, self-cite ceiling) | **Heavy** (`learned.md`) | silently shapes future papers → needs the gate |
| is a fact, rationale, disposition, or decision worth remembering but not enforcing | **Light** (`wiki/`) | cheap memory → no gate |
| is ambiguous | **default to Light**, and let a human or a later `scholar-learn` pass escalate it into `learned.md` | safer to remember-without-enforcing than to enforce-without-asking |

### Capturing USER feedback (the most important, most-missed trigger)

The richest observations come from the **user correcting how oms works on their papers**:
"always put related work before method", "keep self-citations under 10%", "IROS submissions
always need an ablation". These encode the user's intent, not a tree scan, and they are
exactly the ones an automated stage will never produce.

The failure this section fixes: the model hears the correction, says sorry, fixes the one
instance — and **does not write it down**, so the same correction recurs next session. That is
not learning; it is repeated apology. oms's whole premise (specialize in place) collapses if
user corrections evaporate.

**The trigger is durable and unconditional.** Whenever the user corrects, constrains, or
states a preference about how oms should handle *their papers* — in ANY turn, not only inside a
running skill — capture it the same turn, before moving on:

1. **Route it** through the table above. An enforceable default (a venue required section, an
   ordering, a self-cite ceiling) → **Heavy**: append an `OBS-NNNN` block to `learned.md`
   (§2 format) with `source_stage: feedback` and `user_stated: true`. A working
   habit / disposition / decision that no stage can mechanically enforce ("reviews conclusion
   first", "prefers terse") → **Light**: append to the relevant `wiki/pattern/*.md` or
   `wiki/decision/*.md` (dated section, append-only). Ambiguous → default Light.
2. **⭐ user_stated bypasses the confidence gate, NOT the human gate (resolves review #1).** A
   `user_stated: true` candidate is promoted to the **human gate with `evidence_count: 1`** —
   it does NOT need the §3.1 three-repetition bar, because the user *directly stated* the rule,
   so one statement already IS the user's intent (not a coincidence to be confirmed by
   repetition). But it **still passes the human gate** (which scope? contradicts an existing
   default?) and **auto-promotion remains forbidden** (§6.B). This is the only path that skips
   the repetition bar; everything else needs ≥3 (§3.1).
3. **Mark provenance.** A feedback-sourced block sets `source_stage: feedback` and
   `user_overridden: false`; if the feedback *contradicts* an existing default, the existing
   default's candidate is marked `user_overridden: true` (the user's "no" is durable, §3).
4. **Do it without being asked.** Writing the note is part of honoring the correction. Paper
   knowledge goes to *this harness's* `.oms/`, never to a distributed/user-scope config.

### 1.4 Two wiki levels — local (this paper) vs global (parent `.oms/`)

The light channel `wiki/` exists at **two levels**, both `.oms/`-relative (no absolute path,
no env var, no XDG — preserves "never to a distributed/user-scope config" above):

- **Local** = `<cwd>/.oms/wiki/` — knowledge specific to *this paper* (its reject patterns,
  its decisions). Stays with the paper.
- **Global** = the nearest **ancestor `.oms/wiki/`** found by ascent (cwd → parent, first
  `.oms/` excluding self; git's `.git`-lookup pattern) — assets this *user* reuses across
  **every** paper. Discovered, not configured: when the user runs from a papers-parent folder
  (e.g. their workspace), that folder's `.oms/` is the global level.

**What may rise to global** (the only things that leak upward — this is how the anti-pattern is
honored, not violated): reusable assets only —

| category | global-eligible | why |
|:---|:---:|:---|
| `pattern/` (disposition: phrasing, structure, working style, preferences) | ✅ light-only, never enforced | identity, doesn't change per paper |
| `convention/` (venue format, section structure) | ✅ via human gate (§6.B) | reused per venue |
| **writing-craft split** (writing rules) | universal proposition → `venue.prose_defaults` ✅ via human gate (§6.B); user/venue-specific *phrasing preference* → `pattern/` light-only | a universal proposition (old→new, em-dash cap, etc.) is promoted to a venue-enforced default / specific phrasing is advisory. Rule body SSOT = `writing-craft.md` (do not re-list here) |
| `decision/` (reusable decision: "always ablation first") | ✅ | meta-decisions across papers |
| `history/` (my paper history) | ✅ (global-only category) | init uses it to relate/dedup new papers |
| this paper's topic/gap | ❌ stays local | paper-specific, not reusable |
| **citation / `.bib`** | ❌ **permanently forbidden** | hallucination risk — §6.F invariant, never promoted to global |

The global level is *the parent folder's `.oms/`* (still work-root-relative), **not** a
distributed config — and only reusable assets cross up. Paper-specific knowledge and citations
stay local/forbidden. `wiki_query` merges both levels (`references/wiki/README.md`), tagging
`[wiki:local]`/`[wiki:global]`; the call site never changes.

---

## 2. The `learned.md` observation format (heavy-channel staging)

`.oms/learned.md` is an append-only ledger of candidate defaults awaiting promotion. Stages
append; only `scholar-learn` (via the human gate) consumes/retires entries.

Each observation is one block:

```
## OBS-<NNNN>  <one-line summary>
- id: OBS-<NNNN>
- channel: default                   # always 'default' in learned.md (light notes go to wiki/)
- status: candidate | promoted | rejected | superseded
- scope: global | <venue-key>        # ⭐ global = this user's universal habit; <venue-key> = per-venue
- pattern: <precise, testable statement of the regularity>
- candidate_default:                 # the exact venues.md edit this would become, if promoted
    target: venue.required_sections | venue.section_order | venue.self_citation_max_ratio | venue.prose_defaults | global.<field>
    value: <the concrete default being proposed>
    origin: learned
- evidence_count: <integer ≥ 1>      # how many distinct papers/sessions support it
- evidence:                          # the actual support — paper-slugs/events, NOT a vibe
    - <paper-slug or session event #1>
    - <paper-slug or session event #2>
- counter_examples: <integer>        # papers/events that VIOLATE the pattern (kills promotion if > 0)
- first_seen: <ISO date>
- last_seen: <ISO date>
- user_overridden: false             # set true if the user has ever rejected/contradicted this
- user_stated: false                 # ⭐ true if user directly stated it (then evidence 1 is enough — §1.feedback.2)
- source_stage: <inspect|verify|draft|feedback>   # which stage logged it (feedback = user correction, any turn)
```

Worked example (per-venue, observed):

```
## OBS-0003  IROS papers always include an Ablation section
- id: OBS-0003
- channel: default
- status: candidate
- scope: iros
- pattern: Every IROS paper this user wrote ended up with a dedicated Ablation section.
- candidate_default:
    target: venue.required_sections
    value: "+Ablation"
    origin: learned
- evidence_count: 3
- evidence:
    - iros-2026-grasping (inspector flagged missing ablation, user added)
    - iros-2026-nav (same)
    - iros-2025-manip (same)
- counter_examples: 0
- first_seen: 2026-01-12
- last_seen: 2026-05-20
- user_overridden: false
- user_stated: false
- source_stage: inspect
```

Rules for the ledger (same append discipline as omp §2):
- **Append-only by stages.** Re-observing an existing pattern bumps `evidence_count`, appends
  to `evidence[]`, updates `last_seen` — no duplicate block.
- **Evidence is concrete.** `evidence[]` lists real paper-slugs/events. No enumerable evidence
  = a guess, and guesses do not enter `learned.md` (§6.E).
- **Counter-examples are tracked honestly.** A single violating paper increments
  `counter_examples`. This is what makes promotion safe (§3).
- **Status is a lifecycle, not a delete.** Promoted/rejected/superseded entries stay for
  provenance; they are filtered out of the candidate set, not erased.

---

## 3. Promotion criteria (the test `scholar-inspector` applies)

When `scholar-learn` runs, `scholar-inspector` (read-only) evaluates each `status: candidate`
observation against **all** of the following. A candidate is promotable to the human gate
**only if every condition holds** — this is an AND, not a score:

### 3.1 The repetition bar (the only criterion that gates evidence count)

1. **Repetition.** `evidence_count ≥ 3` across **distinct** papers/sessions. Three is the
   minimum that distinguishes a convention from a coincidence (resolves review #2 — this is
   the same bar omp §3.1 uses, not a magic number). **Exception:** a `user_stated: true`
   candidate skips this bar (§1.feedback.2) — the user said it directly, so it goes to the
   human gate at `evidence_count: 1`. No other path skips repetition.
2. **No counter-examples.** `counter_examples == 0`. A single paper that breaks the pattern
   means it is not yet a default — it is a tendency. Counter-examples block promotion outright;
   they are not outweighed by a high evidence count. (Computed from `wiki/convention/` scan,
   the oms equivalent of omp's wiki_lint contradiction check.)
3. **Not user-overridden.** `user_overridden == false`. If the user ever rejected this, oms
   does not keep re-proposing it. The user's "no" is durable.
4. **Stability over time.** `first_seen`/`last_seen` should span more than a single session
   burst where feasible. (Soft criterion: flagged as "burst evidence" at the gate so the human
   can judge; a same-session burst still qualifies if 1–3 hold.)
5. **Non-contradiction.** The proposed default must not contradict a default already in
   `venues.md` (same scope) unless explicitly framed as a *replacement*. Silent contradictions
   are never auto-resolved.

`scholar-inspector` outputs, per ripe candidate: the exact `venues.md` edit, the specificity
delta (§4), the provenance id, the scope, and a one-line rationale citing the evidence. **It
then stops at the gate.** Nothing reaches `venues.md` without explicit human approval.

Candidates that fail any condition stay `candidate` (keep accruing) — they are not rejected.
Only the human (or a clear counter-example) sets `status: rejected`.

---

## 4. Specificity — what the `0..1` number means and how it's computed

`specificity` answers: **"how much of this venue's (or the global) default set is owned by
*this user's* learned habits, versus the generic template default it shipped with?"** It is
the quantitative trace of the generic→specialized journey, and oms tracks it **per scope**.

- **specificity = 0** — just deployed. Every default for this scope is the generic template
  default (e.g. IEEEtran shipped sections). oms knows the *kind* of venue but nothing
  user-unique.
- **specificity = 1** — fully specialized. Every active default for this scope was either
  authored from this user's real papers or promoted from a learned observation.
- **in between** — a mix.

### Computation (per scope)

Each default entry carries an **origin**:

| origin | how it got there | weight |
|:---|:---|:---|
| `preset` | the generic template default shipped with the venue | 0.0 (generic) |
| `inductive` | authored from this user's actual past papers | 1.0 (user-specific) |
| `learned` | promoted from a `learned.md` observation through the gate | 1.0 (user-specific) |

```
specificity(scope) = (defaults with origin in {inductive, learned})
                     ──────────────────────────────────────────────
                     (total active defaults in that scope)
```

i.e. the **fraction of a scope's active defaults that are user-owned**. Each scope (`global`,
`iros`, `defense-deck`, …) has its own specificity — paper-writing habits ≠ thesis habits.

### Monotonicity + the deletion rule (resolves review #3)

`specificity` MUST be **monotonic under promotion**: a promotion can only raise or hold it,
never silently lower it. Because oms's denominator (active defaults in a scope) can change when
a default is **removed**, deletion is treated as an explicit recompute event, not a silent
drift: removing a default recomputes specificity in the **same pass**, records the removal's
provenance (which `learned_ref` retired, why), and surfaces the new value at the gate. A
specificity number that changed with no recorded cause is a §6.C violation.

### When it moves

- **First venue work** sets the initial value (mostly preset).
- **Each accepted `scholar-learn` promotion** flips one default's origin `preset → learned`
  (or adds a `learned` default), then recomputes — rising toward 1.
- **Explicit removal** recomputes (with provenance, never silent).

---

## 5. The obsidian / second-brain analogy (wiki = grep-recalled notes)

oms's light channel is a second brain modeled on Obsidian — same as omp §5:

- **`wiki/<category>/*.md` = a note.** Stages auto-append observations/decisions/dispositions.
- **`[[backlinks]]` = cross-references**, plain text — no database, no index to corrupt.
- **grep = recall.** Next session oms runs **deterministic grep** (CJK bi-gram included) over
  `wiki/` for terms relevant to the current paper, injecting matches as context. Reproducible,
  inspectable, no embedding drift. The second brain remembers *only what was written*, recalls
  *only by literal match*.

### ⭐ confidence on wiki notes (OMC backport — H6)

Wiki notes carry a frontmatter `confidence: high | med | low`. When a stage re-observes the
same pattern, the note's confidence rises (`low → med → high`) and on merge oms **keeps the
higher** confidence (never downgrades on a weaker re-sighting). This repeated-sighting climb is
the light-channel echo of omp's `evidence_count`, and it is what feeds the heavy gate: a
`convention/` note reaching **`confidence: high`** is the signal that an `OBS` for it has likely
hit `evidence_count ≥ 3` and is worth a `scholar-learn` look. confidence is qualitative (3
levels + sighting count) — **no numeric weighted sum, no threshold magic** (omp §exclude).

**Wiki notes are append-only.** A revisited topic deepens (old note + new dated `## <ISO> —
<one-line>` section coexist); whole-file overwrite is reserved for paired SSOT docs, never a
wiki note. The light channel accrues, never replaces — same discipline as `learned.md` (§2).

**A wiki note pairs its conclusion with the load-bearing evidence that produced it** — the
concrete instance, the contrast case, or an *internal* pointer to where in the user's own work
to re-look (a paper-slug / section), so a later session need not re-read the original to recover
the rationale. A label-only note ("X uses a stage axis") forces a costly re-read next session;
the reusable knowledge is the evidence behind the label ("X groups two independent contributions
across stage chapters — see `<slug>` ToC"). This is a **recommendation**, not the §6.E
hard-evidence gate of the heavy channel: the light channel's value is being cheap and
frictionless (§1), so missing evidence does not reject the note — it just makes it weaker. The
"internal pointer" is navigation within the user's work (which slug/section to revisit), **never a
`.bib` citation** (§6.F invariant holds — citations never enter the wiki).

---

## 6. Anti-patterns (forbidden — these break the trust model)

Hard prohibitions. oms's value collapses if any is violated.

### A. No embedding / semantic search for recall
Recall over `wiki/` and `learned.md` is **deterministic grep only** (CJK bi-gram). No vector
search, embeddings, or similarity-ranked retrieval. Embedding recall can surface a note that
does not literally support a claim — the same hallucination/citation-unsafe failure mode oms
exists to prevent. oms recalls *exactly and only* what was written.

### B. No auto-promotion without the human gate
A `learned.md` observation MUST NOT become a `venues.md` default without explicit human
approval — no matter how high its `evidence_count` or `confidence`. There is no count so high,
no confidence so strong, that it bypasses the gate. `scholar-inspector` judges; the human
disposes.

### C. No silent default changes
Every change to `venues.md` MUST be (1) traceable to its origin (a promoted observation records
its id; an inductive default records `origin: inductive`); (2) reflected in the paired human
narrative in the **same pass**; and (3) accompanied by a recomputed `specificity`. A default
with no provenance, or a specificity that moved with no recorded cause, is a violation —
`scholar-verify` should flag it (H10).

### D. (Corollary) No enforcement from the light channel
A `wiki/` note MUST NOT be treated as an enforceable default. To enforce, escalate to
`learned.md` and pass the gate (§B).

### E. (Corollary) No fabricated evidence
`learned.md` `evidence[]` MUST cite real, enumerable paper-slugs/events. oms does not invent
papers to reach `≥3`, and does not "round up" a count.

### F. ⚠️ No citation promotion (oms-specific, absolute)
`.bib` entries, citations, and "cite this paper" decisions are **permanently NOT heavy-channel
candidates**. A `candidate_default.target` naming `citation`/`bib`/a specific reference is
**rejected at the schema level** (not in the allowed target enum). Citations live only in the
`.tex`/`.bib` SSOT of a paper-slug; they never become a learned default and never enter the
wiki. This is the load-bearing oms invariant — violating it makes oms citation-unsafe.

> **External justification (why this invariant is not overkill)**: a citation being merely
> "real (correctness)" is not enough — if the model did not actually rely on that document but
> post-rationalizes it, it is *unfaithful*, and measurements show up to 57% of citations lack
> faithfulness
> ([Correctness is not Faithfulness in RAG Attributions, arXiv:2412.18004](https://arxiv.org/abs/2412.18004)).
> Even a state-of-the-art autonomous paper system (Zochi) deliberately keeps citation formatting
> human-in-the-loop ([intology.ai/blog/zochi-acl](https://www.intology.ai/blog/zochi-acl)).
> oms's refusal to auto-promote or auto-fix citations is in line with the field. (Full external
> landscape: global wiki `reference/llm-paper-writing-landscape.md`.)

---

## 7. End-to-end trace (how one learned default happens)

1. **operation** — the user writes 3 IROS papers. Each time `scholar-inspect` flags "no
   ablation section" and the user adds one. `scholar-pilot`'s wiki-capture appends to
   `.oms/wiki/convention/iros-*.md`; by the 3rd, the note's `confidence` reaches `high`. In
   parallel, the disposition "reviews conclusion first" lands in `wiki/pattern/working-style.md`
   (light, no gate).
2. **observation** — the same pattern is staged in `learned.md` as `OBS-0003`, `scope: iros`,
   `candidate_default: {target: venue.required_sections, value: +Ablation}`, evidence_count 3,
   counter_examples 0 (no IROS paper omitted it — `wiki/convention/` scan).
3. **learn** — `scholar-learn` runs. `scholar-inspector` (read-only) checks §3: count ≥ 3 ✓,
   counter-examples 0 ✓, not user-overridden ✓, stable across sessions ✓, no contradiction ✓.
   It drafts the `venues.md` edit + specificity bump + provenance, **stops at the gate**.
4. **gate** — the human approves. `scholar-learn` writes the default into `venues.md` (IROS row:
   required-sections += Ablation, origin: learned), sets `OBS-0003.status: promoted`, records
   provenance, recomputes `specificity(iros)` upward (e.g. 0.0 → 0.14), regenerates the human
   narrative in the same pass.
5. **enforce** — from now on `scholar-outline` lays down Ablation as a **default section** for
   IROS work, without the user asking. The second brain has specialized to *this user's IROS
   habit* — every step on disk, inspectable, reversible.

---

## 8. SSOT reading order (read before you write or critique)

This card is about *learned* knowledge (the wiki/venues channels). But the same trust model
applies to a paper's **own SSOT** — the per-project authority files that say what this paper
*currently* is. Skills that write (`scholar-draft`, `scholar-revise`) or critique
(`scholar-inspect`, `scholar-verify`) MUST read the SSOT *first*, in this priority order,
before acting:

```
1st (authority — read first, every time):
   .oms/<slug>/outline/outline.md        ← current section structure, story arc,
                                             contribution↔section mapping, word budget
   .oms/<slug>/methodology/*.md          ← each method/equation's source, meaning, assumptions

2nd (secondary — supporting only, may be stale):
   .oms/<slug>/research/*.md             ← related-work map / gaps (can be outdated post-ideate)
   research_summary/ · code_survey/*     ← code/repo inventory notes (NOT authority on
                                             chapter-axis or scope; structure redesigns
                                             leave their chapter numbers stale)
```

**Why the order is load-bearing.** The 1st-tier files are the *current* design; the 2nd-tier
notes are a snapshot of an earlier moment. A code-survey note that says "method X → Chapter 3"
was true under an *old* outline; if the chapter axis was later restructured, that "Chapter 3"
now points nowhere. Judging a draft (esp. the logic lens's "contribution↔evidence" check)
against a 2nd-tier note instead of the current outline produces confident-but-wrong verdicts —
mis-mapped contributions, scope mismatches, "this method is out of scope" calls that the
outline contradicts.

**Two rules that follow:**
- **Never treat absence-from-outline as "out of scope."** If a method is in the code but not
  in the outline, that is *either* a deliberate exclusion *or* an un-synced omission — you
  cannot tell from the notes alone. Ask the human whether the actual experiment used it.
- **The outline is the chapter-axis authority.** When a 2nd-tier note's section number
  disagrees with the outline, the outline wins; the note is stale.

(This is the per-project mirror of the wiki/venues trust model: 1st-tier SSOT is to a single
paper what `venues.md` defaults are to the user's whole corpus.)

---

## See also

- `references/output-layout.md` — where `.oms/` files live; the paper-slug / wiki layout.
- `references/venues.md` — the human venue catalog (heavy-channel promotion target).
- `references/wiki/README.md` — light-channel categories + append/confidence discipline.
- omp `references/learning-protocol.md` — the upstream this is backported from (same two-channel
  design, human gate, grep recall; omp promotes file-rules, oms promotes venue-defaults).
