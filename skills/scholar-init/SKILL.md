---
name: scholar-init
description: |
  Stage-0 bootstrap for a new paper — settle the folder location, venue, and one-line topic through dialogue (≤3 questions),
  then create the standard directory scaffold (sections/figures/refs/data) + an `.oms/<slug>/` workspace + a per-paper
  `.oms/wiki/`. At start it references the **parent folder's `.oms/wiki/` (global level, discovered via ascent)** as a
  seed to recommend "the venue·structure you usually use". The draft scaffold·venue-config is written to disk only after
  passing a human approval gate — a starting point that begins generic and is immediately specialized to this paper / this user.
  If an `.oms/<slug>/` already exists, it warns "re-initialize?" and stops. No citation/.bib generation·fabrication (this stage is scaffold only).
  Triggers: 논문 시작, 새 논문, 논문 셋업, 논문 부트스트랩, 초기 디렉토리, scholar init, paper init,
  start a paper, bootstrap paper, initialize paper, 새 논문 쓸래, 논문 폴더 만들어
---

# scholar-init — Stage-0 bootstrap for a new paper (settle via dialogue → generate scaffold)

<Purpose>
A bootstrap you run exactly once when first starting a paper. Through a short dialogue with the user, settle (1) the folder location (2) the venue (3) the one-line topic, then create the standard directory scaffold and the `.oms/<slug>/` workspace · per-paper wiki. The key is to **start from a seed, not from empty hands** — at start it finds the *parent folder's `.oms/wiki/`* (global level) via ascent and draws out recommendations like "you usually submit to IROS, and you always use this section structure". So the more papers you write (the more the global wiki accumulates), the faster the next paper's start becomes. This is the origin of oms's "generic→this-user-specialized" asymmetry, and it is the bootstrap pattern of its sibling `omp-init` ported to the paper domain.

⚠️ This stage creates **scaffold (empty skeleton) only** — it generates none of the paper *content* (.tex body·citations). Citation-bound generation is done afterward, singly and carefully, by research→ideate→draft.
</Purpose>

<Use_When>
- A new paper folder does not yet have an `.oms/<slug>/`, and you are starting paper work with oms
- First entry such as "새 논문 쓸래 / 논문 폴더 만들어 / 논문 셋업"
- When `scholar-pilot` detects the absence of `.oms/<slug>/` and absorbs (recommends) calling init
</Use_When>

<Do_Not_Use_When>
- An `.oms/<slug>/` already exists → re-initializing would wipe that paper's workspace·per-paper wiki. To continue the work → `scholar-research`/`scholar-pilot`; to promote observations into venue defaults → `scholar-learn`.
- Related-work survey only → `scholar-research`. Concept organization only → `scholar-ideate`. Section structure only → `scholar-outline`.
- Paper body generation → `scholar-draft` (init is scaffold only, does not generate body).
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Minimal questions (≤3)**: in the first session, ask only (1) folder location (2) venue (3) one-line topic + contribution. Do not ask about methodology·detailed section structure·related work — the research/ideate stages extract those naturally (progressive disclosure). Asking 6 at once makes the start friction.
- ⚠️ **Read first·write after gate**: folder scan·global wiki read·scaffold synthesis (dispatch) are all read-only — zero disk changes. The actual scaffold/`.oms/` writing is performed by the calling context (this skill) after passing GATE 1 (human). No self-approval: the dispatch that synthesized the scaffold cannot approve·record it in the same pass.
- ⚠️ **Citation safety**: init creates scaffold only. It does not *generate* citation entries in `.bib` (only an empty `paper.bib` skeleton). Even when reading the global wiki seed, the wiki content is merely a *secondary memo* — it is not used as a citation source (embedding search permanently forbidden, deterministic grep only). citation/.bib is permanently never a global-wiki promotion target.
- **Stop when `.oms/<slug>/` exists**: check at the first step. If it exists, stop immediately and warn "already initialized — re-initializing loses that paper's workspace·wiki" + proceed only after receiving the user's explicit re-confirmation.
- **Global wiki is graceful**: if the parent folder has no `.oms/`, proceed without a seed (not an error). Recommendations will just be thin; init runs to completion.
- **Be honest about `specificity`**: if you pulled in a lot of global wiki seed, the venue-config specificity is slightly higher (0.1~0.4); if empty-handed, 0. Do not inflate to 1 — real specialization comes via `scholar-learn` promotion.
- **Cross-platform**: all paths are relative or based on `Path.cwd()`. No hardcoding of absolute paths·`~` (pollutes the distributed artifact). The global wiki is found by ascent to the *parent folder's `.oms/`* — not an absolute path. ignore seeds: `.git/**`·`.oms/**`·`outputs/**`·LaTeX build artifacts.
- **Non-ASCII titles**: slug rules are in `references/output-layout.md` §1.1. For a non-ASCII title, ask once for an ASCII slug (no automatic romanization).
</Execution_Policy>

<Steps>
1. **Check `.oms/<slug>/` existence (gate 0)**: if the intended paper folder has `.oms/<slug>/` or `meta.md`, stop and warn — "already initialized. Re-initializing loses this paper's workspace·wiki. Really?" Continue only with the user's explicit consent (recommend preserving the existing one). If absent, move on.

2. **Folder location (question ①)**: "Where should this go? Recommendation: `<cwd>/<proposed-slug>/`" — user confirms or gives a different path. slug = output-layout §1.1 (non-ASCII→ask once for ASCII). The confirmed slug is immutable for the lifetime of the work.

3. **Global wiki seed read (ascent, read-only)**: ascend from cwd to find the **nearest parent `.oms/`** (excluding self) (the way git finds `.git`). If found, use `wiki_query('pattern')`·`wiki_query('convention')`·`wiki_query('history')` to draw out "the venue·section structure·expression tendencies·past papers this user usually uses" (deterministic grep). If absent, proceed without a seed. (Contract: `references/wiki/README.md`.)

4. **Venue + one-line topic (questions ②③)**: present the global seed as recommendations — "You usually submitted to IROS — go with IROS 2027? Sections in your usual structure?". If venue is undecided, generic. Receive the one-line topic + one sentence of the core contribution (methodology details not asked). If there is a location for existing materials (Zotero/bib/PDF folder), record only the path.

5. **Scaffold synthesis (dispatch, read-only)**: delegate to `scholar-planner` — with the chosen venue card (`references/venues.md`) + global seed as input, **return as text** (does not write to disk) "this paper's initial directory tree + venue-config (yaml) + per-paper wiki seed". The venue-config conforms to the venues.md schema; `specificity`·`origins` honestly record only what the global seed reflects. No self-approve.
   ```
   Task(
     subagent_type="oh-my-scholar:scholar-planner",
     description="Synthesize paper scaffold + venue-config draft",
     prompt="With chosen venue=<key> and global wiki seed=<excerpt> as input, synthesize a "
            "venue-config draft conforming to the references/venues.md schema + a directory scaffold tree + a per-paper wiki seed. "
            "Comply with the references/output-layout.md structure. Be honest about specificity (only what the seed reflects). "
            "read-only — do not write to disk, return draft text only. No self-approve (GATE 1 is human)."
   )
   ```
   ━━━ **GATE 1 (key): draft approval (human)** — proceed / revise / abort. Present to the human the folder location·venue·directory tree·per-paper wiki seed·**which global seeds were pulled in**·estimated specificity, and receive a decision. No automatic pass. On revise, go back to 5 and re-synthesize. ━━━

6. **Write scaffold (only after passing the gate)**: from the approved draft, create per the structure in `references/output-layout.md` —
   - Paper source folder: `sections/` (NN_*.tex empty skeletons) · `figures/` · `refs/paper.bib` (empty) · `data/` · `preamble.tex` (a line that `\input`s the upper global macros — if the parent `.oms/` has macros) · `<slug>.tex` (minimal skeleton) · `meta.md` (venue·topic·contribution·material location = interview answers)
   - `.oms/<slug>/`: the output-layout workspace (versions/renders/gen-image/tmp left empty or omitted)
   - `.oms/wiki/`: per-paper wiki, empty 4-category (convention/pattern/decision/reference). ⚠️ `history/` is a **global-only** category (exists only in the parent `.oms/`) — do not create it locally. Step 3's `wiki_query('history')` reads only global via ascent, and is graceful even if absent locally (empty list, not an error).
   - venue-config: `.oms/venues/<key>.yaml` (via oms_atomic's atomic write — if json; for yaml use a plain write)
   - `.gitignore`: exclude `.oms/`·`outputs/*`
   > ⚠️ Body·citations are not generated. The .tex is merely a compilable minimal skeleton (documentclass + empty section includes).

7. **Confirmation report**: list of created paths + summary of pulled-in global seed + venue + draft specificity + guidance "Next step: survey related work with scholar-research →". **If there was no parent `.oms/`**: guidance "To place a global wiki (an asset common to all papers), run init once more in the *parent folder of the papers*, or place an `.oms/wiki/` in that folder" (init does not arbitrarily create one in the parent — to avoid home pollution). init is a one-time bootstrap, so end here (not entering a loop).

> **dispatch reality**: the reads in 3·5 are read-only diagnostics — zero disk changes. The actual scaffold/`.oms/` write happens only in step 6 after passing GATE 1. If pilot absorbed the call, after init ends pilot continues into research.
</Steps>

<Output>
The entire created scaffold paths (`sections/`·`figures/`·`refs/paper.bib`·`data/`·`preamble.tex`·`<slug>.tex`·`meta.md` + `.oms/<slug>/` + `.oms/wiki/` 4-category + `.oms/venues/<key>.yaml` + `.gitignore`) + chosen venue + summary of pulled-in global seed (if absent, "no global wiki — guidance to init the parent folder") + draft specificity (honest starting value) + GATE 1 decision history + next step (scholar-research). If `.oms/<slug>/` already exists: state the warning + that re-initialization did not proceed (or only proceeded with the user's explicit consent). Report that nothing was written to disk before passing the gate. ⚠️ Zero body·citation generation (scaffold only).
</Output>
