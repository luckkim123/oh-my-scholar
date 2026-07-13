# GROBID Intake — optional PDF → proposed-BibTeX accelerator
> Consumer: `scholar-read` (single-paper PDF intake, R6 #36) and `scholar-research` (optional `refs/*.pdf` batch intake). Reference card only — no script, no hook ships with this round; GROBID itself is a self-hosted external service the user may or may not run.

---

## §1. What it is, and when it applies

[GROBID](https://github.com/kermitt2/grobid) is a self-hosted, optional machine-learning service that extracts structured metadata (title, authors, references, sections) from PDF documents and emits TEI-XML. It is one of the MCP swap-point candidates named in `references/wiki/README.md`'s `citation_lookup()` contract table — here it plays a different role: not a citation *lookup*, but a citation *proposal* source for PDFs already on disk.

Two intake shapes it can accelerate:
- **`scholar-read` single-paper intake** — Step 1's PDF resolution (today manual/Read-based).
- **`scholar-research` batch intake** — a folder of downloaded PDFs (e.g. `refs/*.pdf`, the scaffold folder `scholar-init` creates alongside `refs/paper.bib`) processed in bulk instead of one at a time.

No stage requires it. No plugin.json surface, no new hook, no new runtime dependency — same P5-A "optional means optional" rule as every other R6 accelerator.

## §2. Intake flow

```
refs/*.pdf  →  GROBID (TEI-XML)  →  proposed BibTeX entries (Crossref-consolidated)
                                          │
                                          ▼
                              human confirms EVERY entry
                                          │
                                          ▼
                    scripts/verify_bib_entry.py  (mechanical check, same as today)
                                          │
                                          ▼
                              only then written to .bib
```

Each proposed entry still goes through the unchanged mechanical gate: `verify_bib_entry.py` checks title/author/DOI against Crossref (OpenAlex fallback on HTTPError) before anything is recordable, and the `.bib` write itself still fires `hooks/scholar_cite_guard.py` — cite-guard does not know or care whether an entry's proposal originated from GROBID or from manual research. No new bypass path exists.

## §3. Accuracy & failure modes

GROBID's reference-extraction accuracy is commonly reported around **F1 ≈ 0.87–0.90** — cited as an external report, not independently re-measured by this plugin. Verify the current figure against GROBID's own documentation before relying on it for a specific decision.

Known failure modes, hedged the same way (**commonly reported — verify against GROBID's own documentation, not asserted here as settled fact**):
- Two-column academic layouts can misorder or truncate extracted reference text.
- Non-English references (title, author names in non-Latin scripts) degrade extraction quality.
- DOIs embedded in scanned or oddly-formatted PDFs can be mangled or dropped, pushing the entry to the title-only verification path.

None of these failure modes change the gate in §2 — a degraded extraction just means a *worse proposal*, still subject to the same human confirmation and mechanical check.

## §4. Degrade path

No GROBID instance configured or reachable → today's path, unchanged: manual/Read-based PDF resolution (`scholar-read` Step 1) or manual research-driven citation gathering (`scholar-research`), each followed by the same `verify_bib_entry.py` check before any `.bib` write. Absence of GROBID changes speed only, never which entries are allowed to land in `.bib`.

## §5. Boundary — proposes, never commits

- **GROBID proposes, never commits.** Every entry it extracts is a *proposal*, identical in standing to a manually-typed candidate — never auto-written to `.bib`.
- **cite-guard unaffected.** `hooks/scholar_cite_guard.py`'s deny-before-write interlock runs exactly as today; a GROBID-sourced entry with no verification record is denied exactly like any other unverified entry.
- **Not a citation authority.** GROBID is an extraction tool, not a verification source — `verify_bib_entry.py` (Crossref/OpenAlex) remains the sole mechanical authority that gates a `.bib` write, per the citation-safety invariants.
