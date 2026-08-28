# `.oms/learned.md` — heavy-channel observation ledger (append-only)

> **What this is**: the staging ledger for oms's **heavy channel** — candidate *defaults*
> (venue required sections, ordering, self-cite ceiling, global habits) awaiting promotion into
> `references/venues.md` through the **human gate**. This file is the oms backport of omp's
> `.omp/learned.md`. The promotion dynamics, the `≥3` repetition bar, the `user_stated` bypass,
> and the citation-safe invariant are all defined in `references/learning-protocol.md` — read
> that card first; this file only *holds* observations, it does not define the rules.

> **Lifecycle**: read-only stages (`scholar-inspect`, `scholar-verify`, `scholar-draft`) and
> any turn capturing user feedback **append** `OBS-NNNN` blocks here. Only `scholar-learn`,
> via the human gate, consumes/retires entries (sets `status: promoted|rejected|superseded`).
> Append-only — a re-observation bumps `evidence_count` and `last_seen`, it does not duplicate.

> **Location**: `.hq/config/scholar/learned.md` under the nearest anchor — the `config/` layer,
> which is **tracked** (store-spec §3, §5). This is a policy shift approved at the P4 cutover
> (2026-08-28): the pre-`.hq` location was `.oms/learned.md`, gitignored, so observations were
> invisible to git. They are now committed, which means a shipped repo's ledger travels to every
> machine that clones it. Shipped empty (generic); it diverges as oms is used. An empty ledger is
> the correct initial state — there is nothing to promote yet.

> ⚠️ **Citation-safe (absolute)**: a `candidate_default.target` naming `citation`/`bib`/a
> specific reference is rejected — citations are NEVER heavy-channel candidates
> (`learning-protocol.md` §6.F). Only structure/ordering/format/working defaults belong here.

---

## Observation block format (see `learning-protocol.md` §2 for the full spec)

```
## OBS-<NNNN>  <one-line summary>
- id: OBS-<NNNN>
- channel: default
- status: candidate | promoted | rejected | superseded
- scope: global | <venue-key>            # global = universal habit; <venue-key> = per-venue (iros, …)
- pattern: <precise, testable statement>
- candidate_default:
    target: venue.required_sections | venue.section_order | venue.self_cite_ceiling | global.<field>
    value: <concrete default>
    origin: learned
- evidence_count: <integer ≥ 1>
- evidence:
    - <paper-slug or session event>
- counter_examples: <integer>            # > 0 blocks promotion
- first_seen: <ISO date>
- last_seen: <ISO date>
- user_overridden: false
- user_stated: false                     # true → evidence 1 is enough (skips the ≥3 bar, still gated)
- source_stage: inspect | verify | draft | feedback
```

Promotion requires ALL of `learning-protocol.md` §3 (repetition ≥3 OR user_stated, no
counter-examples, not user-overridden, stable, non-contradicting). `scholar-learn` →
`scholar-inspector` judges → **human gate** → write to `venues.md`. No auto-promotion.

---

<!-- observations are appended below this line; the ledger ships empty -->
