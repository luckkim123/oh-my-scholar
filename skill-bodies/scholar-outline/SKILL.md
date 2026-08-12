---
name: scholar-outline
description: |
  Takes the research·ideate outputs and designs the paper's section structure·story arc — single delegation to scholar-planner.
  Citation-bound, so citation-dependency mapping comes only from the verified researcher list. No fabricating citations.
  This skill's scope ends right before GATE 1 (outline approval — human). No automatic pass.
  Triggers: outline 짜줘, 논문 구조, 목차 설계, story arc, 섹션 구성, 아웃라인, 구조 설계, section outline, design outline, paper structure, table of contents design
---

# scholar-outline — section structure·story arc design

<Purpose>
Takes the outputs of the research·ideate stages (research map, concept notes .md) and designs the paper's section tree·story arc·word budget·citation-dependency mapping. This is the role corresponding to "architecture design" in code development. Single delegation to scholar-planner (the sole design authority). Once the outline is finalized, it must pass GATE 1 (human approval) before moving to the next stage (scholar-draft) — there is no automatic pass.
</Purpose>

<Use_When>
- When research (research map·gap statement) and ideate (concept notes .md) are done and it is time to set the paper structure
- When designing the section order·story arc·word budget for the first time
- When fully restructuring an existing outline
</Use_When>

<Do_Not_Use_When>
- If the research·concepts are not yet settled → do scholar-research / scholar-ideate first (concepts-finalized-first principle)
- If the outline already exists and it is time to write the .tex body → scholar-draft
- If you only want a structural critique of an existing draft → scholar-inspect
- If you want verification of a specific claim or calculation in the paper → scholar-verify
</Do_Not_Use_When>

<Modes>
This skill operates in three modes (default `--direct`):
- **`--direct`** (default): current behavior — single delegation to scholar-planner producing 1 outline. Fast and lightweight.
- **`--consensus`**: invokes the planner's `<Consensus_RALPLAN_DR_Protocol>` to converge to a final single outline through story arc Options≥2. A 4-agent **sequential** pipeline. Produces 2 separate outputs: `plan.md` (decision process) + `outline.md` (decision result).
- **`--review`**: takes an existing outline as input and only reviews it (not a redesign).

**`--consensus` auto-invocation (Deliberate trigger)**: if any one of top-tier venue (CVPR/ICLR/NeurIPS/Nature etc.) · breaking-method claim · baseline (comparison group) change applies, then even when called with `--direct`, propose to the user once: "this task recommends consensus — proceed?" (not auto-forced; the user can override).
</Modes>

<Execution_Policy>
- ⚠️ **planner is a single careful delegation** — even for multiple venues·papers, a single planner handles it. No parallel planner dispatch (it amplifies story arc inconsistency).
- ⚠️ **No fabricating citations** — each section's dependency citations come only from the list verified by the researcher. If a nonexistent citation is needed, mark "researcher re-check needed", never invent it.
- ⚠️ **GATE 1 has no automatic pass** — no matter how excellent the planner's output is, it is not passed to scholar-draft without the human's proceed/revise/abort.
- The outline is a design document — do not write paper-body prose inside the outline.
- Snapshot the existing outline before a large structural change.
- ⚠️ **The `--consensus` 4-agent flow is absolutely never parallel — sequential is enforced (triple wording)**:
  1. (step-level) each step instruction states "dispatch the next step *only after* the previous step finishes. Do not invoke two Tasks in the same parallel batch."
  2. (Important block) "researcher → planner → [architect responsibility within planner] → inspector MUST be sequential. After awaiting each stage's Task result, issue the next Task."
  3. (CRITICAL one-liner) "citation-bound pipeline — concurrent generation amplifies citation inconsistency. The controller guarantees sequencing only via await (no runtime lock)."
  Why this triple wording is needed: OMC also has no runtime lock and guarantees sequencing only via the controller's await (the ralplan SKILL "Steps 3 and 4 MUST run sequentially ... Always await" pattern), so a single instruction cannot prevent parallel invocation.
</Execution_Policy>

<Steps>
1. Check input: verify the paths of the researcher research map (gap statement·citation list) and the ideate concept notes (.md). If absent, stop → guide to the prerequisite skill. **Mode determination**: check the call flag (`--direct`/`--consensus`/`--review`). If unspecified, `--direct`, but if a Deliberate trigger applies, propose consensus once (`<Modes>`).

### `--direct` path (default)
2. Confirm the target venue for writing: check sections·page_limit·required_sections in `references/venues.md`. If venue unspecified, confirm with the human. **If it is a word venue (.docx/.hwpx — e.g., a degree thesis)**, then after passing GATE 1, instead of scholar-draft (.tex), **hand off to OMD `docs-build`** (pass the outline + concept notes .md to OMD). The format card (e.g., postech-thesis-format.md) is passed to OMD by the caller as well.
3. `Task(subagent_type="oh-my-scholar:scholar-planner", ...)` single delegation:
   - Input: research map, concept notes path, instruction to reference the venue card (`references/venues.md`)
   - Instruction: section tree (purpose·core message·word budget·dependency citation key) + story arc necessity chain + word budget total within page_limit×500 + citations only from the researcher-verified list + mark missing citations as "researcher re-check needed"
4. Receive the planner output — section tree·story arc·word budget summary·full citation-dependency mapping·unverified citation request list.
5. Save the output to the workspace `.oms/<slug>/outline/outline.md` (output-layout.md §2 fixed path). ⚠️ Do not put it in the source folder (`paper/…`) — the outline is the *input* (scaffolding) to the draft, not a citation-bound source asset.

### `--consensus` path (4-agent sequential — never parallel)
> ⚠️ The 2c-1~2c-4 below MUST be sequential. After awaiting each step's Task result, issue the next Task. Do not invoke two Tasks in the same parallel batch. (Execution_Policy triple wording)
2c-1. **researcher** (`scholar-researcher`): if gap·citation reinforcement is needed, re-invoke (if already sufficient, reuse the existing research map). Move on *only after this step finishes*.
2c-2. **planner** (`scholar-planner`, `--consensus` instruction): invoke `<Consensus_RALPLAN_DR_Protocol>` — Principles + Drivers + story arc Options≥2 + steelman + tradeoff + ADR + (if Deliberate) pre-mortem. *With the 2c-1 result as input*. Output = `plan.md` (decision process) + section tree.
2c-3. **[architect responsibility within planner]**: not a separate agent — the planner already performed it in 2c-2 via steelman/antithesis (T1 boundary convention: do not create a new architect agent). If external consultation is *truly* needed, only via the inspector's `<External_Consultation>` path.
2c-4. **inspector** (`scholar-inspector`): formative critique of 2c-2's plan.md+outline (4 critic techniques). Does not issue PASS/FAIL — improvement points only. *With the 2c-2 result as input*.
2c-5. **re-review loop**: if the inspector raises critical/important, re-delegate to the planner (back to 2c-2) then re-critique. **Max = venue.max_review_rounds (default 5 if the key is absent in venues.md)**. On reaching 5, take the best version and proceed to GATE 1 with "consensus not reached — N rounds, list of remaining findings" stated explicitly.
2c-6. **2 separate saves**: `plan.md` (RALPLAN-DR+ADR, decision process) + `outline.md` (Final single-arc section tree, decision result). Both in the workspace `.oms/<slug>/outline/` (output-layout.md §2). ⚠️ source folder (`paper/…`) prohibited.

### Common — GATE 1
> ⚠️ The handoff between `--consensus`'s 2c-* sequential stages follows the `<Consensus_Handoff>` convention below (rubber-stamp prevention).
6. **GATE 1 — request human approval**:
   - **Render the sheet first**: run `python3 <plugin>/scripts/oms_outline_view.py .oms/<slug>/outline/outline.md`. It writes `.oms/<slug>/outline/gate1.html` and prints one line per structural gap plus a final `GAPS=<n>`. The sheet is a *derived read-only view* — `outline.md` stays the SSOT, so never edit the HTML; revisions go to `outline.md` and the sheet is regenerated.
   - **Surface it**: when the running harness can publish an artifact, publish `gate1.html` and give the human the link; when it cannot, report the file path so they can open it in a browser. Its absence is a graceful degrade, not an error — the gate still functions on the text outline alone.
   - **Report the gaps verbatim, do not paper over them**: the script detects *absence* only (missing field, section off the necessity chain, blank chain link, researcher-recheck marker, over-budget total, citation-mapping mismatch, no section tree at all). `GAPS=0` means nothing mechanical is missing — it is **not** a judgment that the structure is good, and must never be presented as one.
   - Present the full outline (for consensus, both plan.md+outline) and specify the following three options:
     - **proceed**: outline approved → can proceed to scholar-draft
     - **revise**: instruct the revisions → re-delegate to the planner then re-run GATE 1
     - **abort**: discard this outline → return to the prerequisite stage (research/ideate)
   - Do not proceed to scholar-draft until the human's explicit response.
</Steps>

<Output>
The outline designed by the planner (section tree·story arc·word budget summary·citation-dependency mapping) + `outline.md` save location + unverified citation request list (if none, "none") + **GATE 1 approval request** (proceed / revise / abort option guidance, with a note that it does not self-approve).

**Additional when in `--consensus` mode**: `plan.md` (RALPLAN-DR+ADR — decision process) save location + re-review round count (N/5) + whether consensus was reached ("reached" or "not reached — list of remaining findings"). plan.md and outline.md are *two separate files* (decision process ≠ decision result).
</Output>

<Consensus_Handoff>
> The handoff convention between the `--consensus` 4-agent stages (isomorphic with docs-plan). **Default (SSOT) = .md files**, MCP is an *if-available* optional accelerator (decision1=C: OMS being 0 MCP / standalone is its identity).

**Default path (.md — works without MCP)**:
- Write each consensus stage's *structured output* (the planner's steelman/antithesis/tradeoff/ADR, the inspector's findings, etc.) to the workspace `.oms/<slug>/consensus/<stage>-<role>.md`. E.g., `consensus/planner-adr.md`, `consensus/inspector-findings.md`. Each file has a structured header (role / stage / timestamp) + body.
- **Rubber-stamp prevention (mechanical)**: the next stage proceeds only after *confirming that the previous role's .md file exists on disk*. If absent, refuse to proceed ("previous stage output missing — sequencing violation"). Directory isolation = namespace substitute. Since consensus is sequential there is no concurrent-write race, and one directory is sufficient.
- `<slug>`·paths are **relative to the work root** (based on the caller's cwd / the specified project root) — no specific-user absolute paths.

**Optional (accelerator) MCP**: if the config gate `agents.sharedMemory.enabled` is on and the shared_memory MCP is *available*, the same data may be mirrored via `shared_memory_write(namespace="paper-consensus", key="<stage>-<role>", value={...})` (precise key lookup·automatic TTL). ⚠️ **.md is SSOT, MCP is only an accelerator** — when MCP is absent it is not an error but a graceful degrade to the .md path, with the same guarantees.

**Mixed-use clarity**: *unstructured outputs* such as the researcher research map stay in the existing .md way as-is (the handoff convention applies *only to structured consensus outputs*). The consensus/ directory is a workspace — a T18 cleanup target on termination.
</Consensus_Handoff>
