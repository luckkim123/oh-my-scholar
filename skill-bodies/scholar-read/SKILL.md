---
name: scholar-read
description: |
  Deep-read ONE external paper (PDF / arXiv id / URL / pasted text) into a structured, citation-safe reading note.
  Single dispatch (no parallel content generation); the note is a secondary memo, NEVER a .bib source — the only door into the bibliography stays scholar-research → human-confirmed .bib.
  Triggers: 논문 읽어줘, 이 논문 정리, 딥리드, 리딩노트, read this paper, deep read, reading note, analyze this paper
---

# scholar-read — external-paper deep-read → structured reading note

<Purpose>
Turn "read this paper for me" into a structured, citation-safe reading note. Delegate a single dispatch to scholar-researcher (`mode="deep-read"`, read-only) to extract ONE external paper's identity, claims, method, evidence, limitations, and open questions into `.oms/reading/<citekey>.md` — a personal reading corpus that outlives any one paper project, kept strictly separate from this project's own citation pipeline.
</Purpose>

<Use_When>
- When you want to deep-read a single external paper (PDF path, arXiv id/URL, or pasted text) and keep a structured note for later reuse
- When you want the paper's identity mechanically checked (retraction/title-mismatch) before trusting anything it claims
- When you want a reading note other stages (scholar-research, scholar-discuss) can later reference — but never cite directly
</Use_When>

<Do_Not_Use_When>
- If you need a verified `.bib` citation for THIS project → scholar-research (the only door into the bibliography)
- If you want to survey many papers / build a related-work landscape → scholar-research
- If a note already exists for this paper → read `.oms/reading/<citekey>.md` directly instead of re-dispatching
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **Single careful dispatch, not parallel** — exactly one dispatch to scholar-researcher (`mode="deep-read"`) per paper (invariant 1: no parallel content generation).
- ⚠️ **NOT CITABLE — secondary memo only** — `.oms/reading/<citekey>.md` is never a `.bib` source. The only door into the bibliography stays scholar-research → human-confirmed `.bib` (invariant 2). `<citekey>` here is a *filename convention* (`<firstauthor><year>-<short-slug>`), explicitly NOT a BibTeX key.
- ⚠️ **No `.bib` write, no `--record`** — the mechanical identity pre-check (`scripts/verify_bib_entry.py`) is invoked WITHOUT `--record`. It verifies the *paper's own identity* (is it retracted, does the title match) — it never touches the citation allowlist and never writes `.bib`.
- ⚠️ **RETRACTED is loud** — when the identity verdict is `RETRACTED`, the note and the digest both restate it explicitly and prominently, before anything else — qualitatively different from a merely-unverified paper.
- Degrade gracefully: no DOI/title resolvable → the note's frontmatter carries `identity: unverified` and says so in prose; PDF unreadable → ask the user for pasted text instead of guessing at content.
</Execution_Policy>

<Steps>
1. **Resolve the input**: a PDF path (under `refs/` or elsewhere), an arXiv id/URL, or pasted text. Extract whatever title/authors/venue/DOI is available from it. (An optional accelerator — GROBID-based structured PDF intake — is documented at `references/grobid-intake.md`; today's resolution is manual/Read-based, and its absence changes nothing about this step.)
2. **Mechanical identity pre-check** — when a DOI or title is available, run `python3 scripts/verify_bib_entry.py --key <citekey> --title "<title>" --doi "<doi>" --author "<first-author-family>"` (no `--record`). Read the `VERDICT=` line: `VERIFIED | MISMATCH | RETRACTED | NOT_FOUND | NETWORK_ERROR`. When neither DOI nor title is resolvable, skip the check and mark `identity: unverified` instead of guessing.
3. **Single dispatch**: `Task(subagent_type="oh-my-scholar:scholar-researcher", mode="deep-read", ...)`:
   - Input: the resolved paper (path/id/text), the identity verdict from step 2, any project context the caller wants the note related to (optional — `.oms/<slug>/outline/` / `methodology/` paths if relevant)
   - Instructions: same no-fabrication / injection-hygiene discipline as `mode=gap-research`; every claim carries a verbatim quote (≤3 sentences) + locator — the R1 #5 quote-anchor contract, reused.
4. **The calling session writes** the note to `.oms/reading/<citekey>.md` (the dispatched agent stays read-only — same writer-identity carve-out as `reviews-log.md`/`research-log.md`). The note's first line is the mandatory header: `> NOT CITABLE — secondary memo. A .bib entry may only be created via scholar-research verification.`
5. **research-log append** (`references/output-layout.md` §2.4, context `read`): one dated entry `## YYYY-MM-DD — read` in `.oms/<slug>/research-log.md` summarizing what was read and why (create-if-absent, append-only). Skipped when there is no active paper slug to attach it to.
6. **Surface**: the note's path + a one-paragraph digest. If the identity verdict is `RETRACTED`, restate that loudly at the top of the digest, before anything else.
</Steps>

<Output>
- `.oms/reading/<citekey>.md` — the reading note (Paper identity / Claims / Method / Evidence / Limitations / Relation to my work if applicable / Open questions), NOT CITABLE header as its first line
- One dated `research-log.md` entry (context `read`)
- A one-paragraph digest, with a loud RETRACTED restatement when applicable
- ⚠️ No `.bib` is written or updated by this skill. A citation for this paper, if ever needed, goes through scholar-research → human confirmation.
</Output>
