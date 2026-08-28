---
name: scholar-pilot
description: |
  Full paper pipeline orchestration — research→ideate→outline(GATE1)→draft→inspect→verify
  →revise(GATE2)→submission(GATE3). The paper-domain version of OMC autopilot. Enforces the 3 citation-safety principles.
  Triggers: 논문 만들어줘, 논문 써줘, 처음부터 끝까지, 논문 파이프라인, paper from scratch,
  write a paper, 논문 자동, 전체 논문 작업, oms pilot
---

# scholar-pilot — Full paper orchestration (paper-domain autopilot)

<Purpose>
Orchestrates every paper stage from research question to submission readiness. It is the paper-domain version of OMC autopilot, but for citation-bound safety it restricts to **single generation, parallel reading** and inserts 3 human GATEs.
</Purpose>

<Use_When>
- "Build the whole paper from scratch for me" — full pipeline from a short brief
- When it's clear which stage to start from, start at that stage (--from reads `pilot-<slug>.json` via `oms_state.py read` — see the `--from` entry point note below)
</Use_When>

<Do_Not_Use_When>
- If only one stage is needed → use the corresponding scholar-* skill directly
- Because this is a citation-bound paper, **fully unattended automation is forbidden** — the 3 GATEs must always be broken by a human
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **The 3 citation-safety principles are enforced**:
  1. Reading (research·inspect·verify) may be parallel, but **generation (draft) is single and careful — absolutely no parallelism**.
  2. Even if the verifier detects a citation defect, **no automatic fix** — human confirmation.
  3. Before draft (.tex), lock down concepts·sources in ideate (.md) first.
- The 3 GATEs are human decision points — no automatic pass-through.
- Each stage is delegated to its dedicated skill (no re-implementation).
- At **every stage boundary and every GATE decision**, run `python3 <plugin>/scripts/oms_state.py write --slug <slug> --stage <stage> --gate-status <status> [--open-fail-ids …]` — the schema (documented in `references/output-layout.md` §2.2) is what `--from` resume, the Stop guard, and the SessionStart advisory read; a stage that skips the write is invisible to all three.
- **Record priority context on entry (survives compaction)**: at pipeline start, write the critical constraints into the `## Priority Context` section of `.hq/config/scholar/notepad.md` — "no citation fabrication / no parallel draft / human confirmation before editing .bib + current GATE n/3 + list of unverified citations". So that even if context is compacted during a long pipeline, the 3 citation-safety principles and the GATE position are always recoverable. (tiers: references/output-layout.md §2.3 — Priority Context replace-on-write / Working Notes dated-append, 7-day prune at pilot entry / Manual never touched) At pipeline entry, also prune `## Working Notes` entries older than 7 days (dated `### YYYY-MM-DD` sub-headings; the only automated deletion — `## Manual` is never touched).
  - **.md is the default**: write/append directly to `.hq/config/scholar/notepad.md` (since the original notepad is a single .md + section parsing, the loss of reproducing it as .md ≈ 0). If notepad MCP is available, you can mirror via `notepad_write_priority(...)` (same .md target, optional acceleration) — even when absent, a .md write produces identical behavior, not an error.
- The stage-output path is fixed at **`.hq/runtime/scholar/`** (a verified real path; do not nail down unverified sub-segments like `.hq/runtime/scholar/specs`·`sessions/{sid}`).
  - ⚠️ **30s trap (only when state MCP is adopted in the future — not applied now)**: if you start using state MCP, do not call `state_clear` *right before* a stage handoff (it disables every mode's stop-hook for 30s, silently breaking the loop). For a non-terminal handoff use `state_write(active=false)`, and use `state_clear` *only at terminal (full pipeline shutdown)*. **Since state MCP is not actually called at present (the .md/`.hq/runtime/scholar/` files are the default), this is purely a future-proofing note.**
</Execution_Policy>

<Steps>
0. **init absorption (bootstrap — when `.hq/work/scholar/<slug>/` is absent)**: if the paper folder has no `.hq/work/scholar/<slug>/`·`meta.md`, do not jump straight into research; first **recommend** `scholar-init` — "This paper folder isn't set up yet. Shall we set the folder location·venue·topic and create the directory? (scholar-init)". If the user agrees, init creates the scaffold + `.hq/` (referencing the parent `.hq/` global seed), and after it finishes pilot continues to stage 1, research. If `.hq/work/scholar/<slug>/` already exists, skip this stage (no re-init — idempotent). ⚠️ This is a recommendation, not automatic entry — never create folders without the user's knowledge.
1. **research**: scholar-research → research map·gap·verified citations (.md)
2. **deepen**: scholar-deepen → claim-ambiguity gate (qualitative). After research, before ideate.
   - fresh subagent dispatch (prevents controller context contamination).
   - **skip condition**: pass if all 4 deepen dimensions (contribution/method-evidence/comparison/reproducibility) are self-evidently "clear", or if the user specifies `--skip-deepen`.
   - Passing deepen (human approval) is an **internal approval before GATE 1** — do not create a separate user gate (deepen's own "human approval" is sufficient).
3. **ideate**: scholar-ideate → concept notes methodology/*.md (lock concept SSOT)
4. **outline**: scholar-outline → section structure·story arc
   - **mode branching**: if a Deliberate trigger fires (top-tier venue / breaking-method claim / changed comparison group), use `scholar-outline --consensus` (RALPLAN-DR 4-agent sequential); otherwise `--direct`. Auto-decision + user override.
   - **moderator pass (anti-groupthink, read-only)**: before presenting GATE 1, dispatch `Task(subagent_type="oh-my-scholar:scholar-inspector", mode="moderator")` with the proposed outline + paths to `.hq/work/scholar/<slug>/research/*.md` (and `.hq/community/reading/` when relevant). Output: (a) a retrieved-but-unused evidence list (evidence rows present in the notes but absent from the outline), (b) 1-2 pointed questions. The calling session prints both verbatim alongside the GATE 1 prompt — the human decides what, if anything, to do with them; the moderator issues no verdict. `--skip-moderator` opts out. On dispatch failure, proceed to GATE 1 with a one-line notice (fail-open — the moderator never blocks the gate).
   ━━━ **GATE 1**: outline approval (human) — proceed/revise/abort. If consensus, present both plan.md+outline ━━━
5. **draft**: scholar-draft → .tex (drafter single·careful)
6. **inspect**: scholar-inspect → formative critique (parallel OK, read-only)
7. **verify**: scholar-verify → summative automatic gate
   ━━━ **GATE 2**: review-result confirmation (human) — proceed/another round/address/abort ━━━
8. **revise**: scholar-revise → loop until verify PASS (if needed)
   ━━━ **GATE 3**: submission confirmation (human) — confirm/revise/abort ━━━
9. Assemble submission deliverables (PDF·source·checklist).
10. **wiki capture (auto-specialization — the more you use it, the more it adapts to this project)**: patterns that inspect/verify *discovered* this session and that are reusable are **automatically appended** to the **target project's `.hq/community/wiki/<category>/*.md`** (the project workspace, not the plugin; tracked in that project, store-spec §3/§5) (no approval needed — light channel). This is the data that the next session's inspector's pre-commitment `wiki_query(category)` reads — with writing and reading forming a closed loop, the more you use the harness, the more it specializes to this venue/this paper project. (Being a workspace, it does not pollute plugin distributions·other projects, and it isn't blown away by a marketplace update.)
    - **What to load**: ① per-venue recurring reject patterns → `convention/<venue>-reject-patterns.md` ② the rationale for the baseline·comparison group·structure chosen this time → `decision/<slug>.md` ③ discovered external-resource pointers → `reference/*.md`. Only what the inspector/verifier actually saw — no speculative loading.
    - **conclusion + rationale together (no label-only)**: each entry should not record only the *conclusion (label)* but also the *concrete rationale* that supports it (which case·control group·which paper-slug/section to re-read = internal pointer) on the same line/item. Instead of "X is the stage axis", write "X juxtaposes two independent contributions across stages — `<slug>` §toc". If you record only the label, the next session has to re-read the original. ⚠️ The internal pointer is *re-visit navigation*, not a `.bib` citation (see citation-safe below·`references/wiki/README.md`). Recommended, not a gate (light channel).
    - **append format**: add one line (or a short item) to the end of the existing .md. If the same pattern already exists, don't record a duplicate (grep first). A new category file is a free-form body + the standard thin frontmatter (see `references/wiki/README.md` Frontmatter standard).
    - **light-channel evidence signal (append-time, #24)**: every appended entry states its evidence — an internal pointer (`<slug> §…`) or a verbatim quote. An entry with neither is **still appended** (no reject gate), but the note's frontmatter is created/kept at `confidence: low` with an `(evidence: none — add a pointer before confidence can rise)` marker. Evidence-less re-observation never raises confidence — only a pointer or quote lifts a note past `low` (`references/wiki/README.md` § confidence frontmatter).
    - **global promotion candidate hint (terminal only)**: at pipeline shutdown, if among what accumulated locally in `.hq/community/wiki/` this time there are assets *reusable for the next paper too* (tendencies·venue formats·reusable decisions·history), recommend to the user "Shall we promote this to the parent `.hq/` (global)?" — actual promotion goes through `scholar-learn`'s local→global path (human gate). ⚠️ citation/.bib is permanently forbidden from global promotion. No automatic promotion.
    - ⚠️ **citation-safe (mandatory — violation collapses OMS identity)**: the wiki is **secondary memo only**. The *content* of citations·claims·numbers is never loaded (only reject reasons·format rules that aid prediction). The .bib is updated only from scholar-research-verified primary sources — wiki excerpts are not pulled in as citations. Both loading·querying use **deterministic text only, no embeddings**. For the contract·boundary see `references/wiki/README.md`.
    - **automatic but non-destructive**: append-only (never erases existing lines), creates absent directories, and if there's nothing to load it just passes (empty session OK). If the user passes `--no-wiki`, skip.
    - **research-log entry (append-only project narrative memory, `references/output-layout.md` §2.4)**: append one dated entry to `.hq/work/scholar/<slug>/research-log.md` (create-if-absent) — heading `## YYYY-MM-DD — pilot`, then free-prose bullets covering `tried / decided / dropped — and why` for this run (stages executed, GATE outcomes, major decisions, dropped directions). Written by the calling session, never a dispatched agent — same writer identity as the wiki writes above. ⚠️ secondary memo only: a citation key in a research-log entry is never citation authority and this file is **never a `.bib` source** (invariant 2). If the user passes `--no-log`, skip.
11. **terminal cleanup** (after GATE 3 confirm, or when the user explicitly says "clean up"/"work done"):
    - **Aggregate** the cleanup targets in `.hq/work/scholar/<slug>/` (size·count): all of `renders/`·`gen-image/`·`tmp/` + the old versions in `versions/` **excluding** the latest 1·user-designated milestones. To let the user pick milestones, show them the versions list.
    - **AskUserQuestion [clean up / keep]** — never auto-delete, default conservative (keep).
    - On "clean up" → **delete via a recoverable path** (no permanent `rm`): macOS `trash` (if absent `~/.Trash`) / Linux `gio trash`·`trash-cli` / Windows PowerShell move-to-recycle-bin (`Shell.Application` ParseName+InvokeVerb('delete'), no permanent `Remove-Item` — documented, unverified) / in environments without a trash (CI·container) only after the user re-confirms "permanent deletion".
    - ⚠️ `outputs/<slug>/<slug>.pdf` (user asset) and the **project source folder's .tex/.bib (citation-bound assets)** are **fully excluded** from aggregation·deletion — mention only. For detailed procedure see `references/output-layout.md` §5.

> **`--from <stage>` entry point**: can start from an intermediate stage — `research|deepen|ideate|outline|draft|inspect|verify|revise`. e.g.: `--from deepen` means start from deepen using the existing research notes as input. `--from` now *reads* `pilot-<slug>.json` (via `python3 <plugin>/scripts/oms_state.py read --slug <slug>`) and, when invoked without an explicit stage, proposes the recorded `stage` as the resume point.
</Steps>

<Interruption_And_Resume>
- **On entry**: before starting any stage, run `python3 <plugin>/scripts/oms_state.py read --slug <slug>`. If a non-terminal `pilot-<slug>.json` exists for this paper, surface it first — "A pipeline marker exists (stage X, gate_status Y, updated_at Z) — resume from X / restart from an earlier stage / discard?" (use AskUserQuestion when available). **Never silently restart from stage 1 over a live marker.**
- **Abort semantics**: choosing "discard" writes `gate_status=abort` (`oms_state.py write --slug <slug> --gate-status abort`), plus `revise-end --slug <slug> --status abort` if a live revise marker also exists. `abort` is **terminal**: the SessionStart resume advisory stops reporting the marker, the Stop guard stops honoring it, and the state files become cleanup-eligible (`references/output-layout.md` §5).
- **Stale-marker rule**: if `updated_at` is older than 14 days, present the marker as *stale* — "probably an abandoned run — discard unless you recognize it." Still the human's call; never auto-discard.
- **Mid-stage interruption**: if the user interrupts mid-stage, the last boundary write is the resume point — the marker is always at most one stage behind reality. This is exactly why every stage boundary writes state (see `<Execution_Policy>`).
</Interruption_And_Resume>

<Output>
Each stage's output path + the 3-GATE decision history + the final PASS paper — the final version the user sees is `outputs/<slug>/<slug>.pdf` (the compiled output). The .tex/.bib **source originals are kept in the project source folder** (protecting citation-bound assets, not moved into `.hq/`); only version snapshots·compile intermediates go to `.hq/work/scholar/<slug>/` (`versions/`·`renders/`·`tmp/`). The path convention is SSOT in `references/output-layout.md`. + residual items needing human confirmation (unverified citations·fixable=false) + the `.hq/runtime/scholar/` progress record.
</Output>
