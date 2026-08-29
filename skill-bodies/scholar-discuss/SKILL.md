---
name: scholar-discuss
description: |
  Standing Socratic discussion partner over ideas — on-demand debate (Contrarian / Simplifier / Ontologist stances) with a Co-STORM-style moderator move surfacing retrieved-but-unused evidence.
  Zero .tex/.bib surface: no drafting, no citations, no content generation, no subagent dispatch. Outline deltas are proposed at a human gate, never auto-applied.
  Triggers: 토론하자, 아이디어 논의, 반론해줘, 디스커션, discuss this idea, devil's advocate, argue with me, challenge my idea
---

# scholar-discuss — standing Socratic discussion partner (on-demand debate)

<Purpose>
Turn "let's argue this out" into a structured pressure-test of an idea — a devil's-advocate partner you can reach for at any time, not just at a fixed gate. Three self-contained personas (Contrarian / Simplifier / Ontologist) take turns challenging the idea in the main session, and a Co-STORM-style moderator move surfaces evidence you already gathered but haven't actually used. Zero `.tex`/`.bib` surface — discuss never drafts, never cites, never dispatches a subagent (invariant 1: no content generation stays untouched because there is nothing generated here to parallelize).
</Purpose>

<Use_When>
- You want a devil's-advocate pass on a contribution, baseline choice, claim, or naming decision — on demand, not gated by an ambiguity trigger
- You want a Co-STORM-style check for evidence already sitting in your research/reading notes that the discussion (or the outline) hasn't actually used yet
- You want to pressure-test an idea before or during outline/ideate without touching `.tex`/`.bib`
</Use_When>

<Do_Not_Use_When>
- If you need the ambiguity-gated research→ideate handoff check → `scholar-deepen` (deepen is gate-triggered right after research, all 4 dimensions or nothing; discuss is on-demand, any time, any scope — different lane)
- If you're ready to actually change the outline structure → `scholar-outline` (discuss only ever proposes deltas at a human gate, never applies them — D9)
- If you need a verified citation → `scholar-research` (discuss produces no citations; claims raised here stay `unverified` unless anchored to an existing note)
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Zero `.tex`/`.bib` surface** — this skill produces no `.tex`, no `.bib`, no citations. Any claim made during discussion is marked `unverified` unless it is anchored to a paper's own text, a `.hq/community/reading/` note, a `.hq/work/scholar/<slug>/research/` note, or an already-verified `.bib` entry.
- ⚠️ **No subagent dispatch** — the whole discussion runs interactively in the calling session. There is no `Task(...)` call anywhere in this skill; invariant 1 (single careful generation, parallel reading only) is untouched because discuss generates no content to parallelize in the first place.
- ⚠️ **Personas are self-contained restatements, not shared code** (D3) — the Contrarian / Simplifier / Ontologist prompts below are restated here, adapted for standing on-demand debate. Provenance: the original ambiguity-gated version of these three stances lives in `scholar-deepen` Round 4/6/8. This skill does **not** import, extract, or edit that file (`scholar-deepen/SKILL.md` is on the do-not-touch list) — deepen's gate semantics (triggered only on an ambiguous dimension) differ from discuss's on-demand semantics, so a shared personas card would blur two different lanes.
- ⚠️ **Outline deltas: proposed, never applied** (D9) — if the discussion surfaces a structural change worth folding into the outline, it is presented as an explicit numbered list at a human gate. It is **never auto-applied** to a GATE1-approved outline. This is deliberately more conservative than "appends to the living outline" would be — auto-mutating a GATE1-approved artifact from a discussion session would breach invariant 5 (human gates never automated away).
- ⚠️ **Post write is light-channel, append-only** — the exit summary is posted via `hq post --topic decision --subject <slug>` (a fresh post; a genuine update goes through `--supersedes`) with the standard R4 frontmatter (`confidence: high|med|low`, `sightings: <int>`). A summary with no source pointer and no verbatim quote anchor is still posted, but at `--confidence low` with an `(evidence: none — add a pointer before confidence can rise)` marker — the same append-time rule scholar-pilot Step 10 applies (#24, `references/knowledge/README.md` § confidence). No embeddings anywhere (invariant 3): both writing and any later recall of this post stay deterministic grep.
</Execution_Policy>

<Steps>
1. **Frame**: restate the topic in one or two sentences and load whatever context exists — `.hq/work/scholar/<slug>/research/*.md`, `.hq/community/reading/*.md`, `.hq/work/scholar/<slug>/outline/*.md` when present. None of these are required to start a discussion; a bare idea with no project behind it yet is a valid input too.

2. **Stance rounds**: the user picks a persona for the round, or the session proposes one that fits the moment. One persona per round:
   - **Contrarian**: "What if the opposite of this were true? What if the baseline already suffices? Does the idea survive without this piece?"
   - **Simplifier**: "If you kept only 1 of 3 contributions, which? If you halved the experiments, what would you drop?"
   - **Ontologist**: "What *is* this thing, really? Which entity's naming is shaky? Are two different things being called by the same name?"
   (Provenance note, D3: these three stances are restated here for standing debate; the ambiguity-gated original lives in `scholar-deepen` Round 4/6/8 — this file does not import or modify that skill.)

3. **Moderator move (Co-STORM)**: maintain an in-session gap list — evidence rows that are present in `.hq/work/scholar/<slug>/research/*.md` or `.hq/community/reading/*.md` but absent from both the discussion transcript so far and the outline. When a round closes, or the discussion stalls, inject the single highest-information-gain unasked question drawn from that gap list before starting the next round. This list is transient (in-conversation only) — it is not written to disk as a separate artifact.

4. **Exit**: summarize what was explored (stances taken, positions that moved, positions that held) and (both appends below are skipped when there is no active paper slug to attach them to — a bare-idea discussion ends with the in-session summary only):
   - `hq post --topic decision --subject <slug>` (a fresh post) — light channel, `confidence`/`sightings` frontmatter per Execution_Policy above
   - append one dated entry to `.hq/work/scholar/<slug>/research-log.md` (`## YYYY-MM-DD — discuss`, create-if-absent, append-only, `references/output-layout.md` §2.4) covering what was tried/decided/dropped in this discussion and why
   - if a structural change to the outline was surfaced, present it as a proposed numbered delta list at a human gate — never auto-applied (D9)
</Steps>

<Output>
- An in-session discussion transcript (stances explored, questions raised, positions that moved or held)
- One `topic: decision` post for `<slug>` (`confidence`/`sightings` frontmatter; `confidence: low` when the summary carries no pointer or quote — #24)
- One dated `.hq/work/scholar/<slug>/research-log.md` entry (context `discuss`)
- (optional) a proposed outline-delta list, presented at a human gate — never auto-applied to the outline
- ⚠️ No `.tex`, no `.bib`, no citations, and no subagent dispatch anywhere in this skill.
</Output>
