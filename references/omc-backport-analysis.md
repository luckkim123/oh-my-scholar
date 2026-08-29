# OMC Backport Analysis — oh-my-scholar (oms)

oms's deepen gate, consensus layer, inspector critic techniques, and runtime accumulation (wiki/notepad/
verifier tokens) are the verified patterns of **oh-my-claudecode (OMC)** ported into the paper domain.
When OMC is updated, we need a persistent baseline to judge *what changed and whether oms must be updated*.
OMC has no CHANGELOG (only GitHub commits/releases exist) and no per-file versioning, so this document
keeps its own "diff baseline."

> **This document lives in the distributed plugin's references/, so it is independent of any personal environment.** OMC paths are written
> only as the *public plugin's internal structure* (relative expressions). No specific machine's absolute paths, working notes, or the user's organizational system are embedded.

---

## §1. OMC 4.14.4 Structure Snapshot — Backport Source Components

The OMC plugin has a **dual structure**: `skill-bodies/<name>/SKILL.md` holds the full logic, while
`skills/<name>/SKILL.md` is a *compact reference shim* that keeps the startup context light
(loading the body from `skill-bodies/`). The backport source is always the `skill-bodies/` side.

| Source (OMC 4.14.4 internal path) | What was taken |
|:---|:---|
| `skill-bodies/deep-interview/SKILL.md` | Round 0 topology · per-dimension ambiguity judgment · challenge agents(contrarian/simplifier/ontologist) · soft limits · 3-point injection → skeleton of **scholar-deepen** |
| `skill-bodies/plan/SKILL.md`, `skill-bodies/ralplan/SKILL.md` | RALPLAN-DR consensus(Principles/Drivers/Options≥2/steelman/tradeoff/ADR) · sequential-enforcement (no-parallel) prompt discipline → **scholar-planner** + **scholar-outline --consensus** |
| `skill-bodies/autopilot/SKILL.md` | brief→completion stage orchestration + gate skeleton → **scholar-pilot** |
| `skill-bodies/ralph/SKILL.md` | defect=PRD · fix/verify loop until passes:true gate · no scope reduction → **scholar-revise** |
| `agents/analyst.md` | pre-diagnosis · requirement-analysis idea → ambiguity judgment in deepen/research |
| `agents/architect.md` | steelman/antithesis/tradeoff → **absorbed into scholar-planner**(no new agent created) |
| `agents/planner.md` | structure design · word budget → scholar-planner |
| `agents/critic.md` | pre-commitment · assumption(VERIFIED/REASONABLE/FRAGILE) · pre-mortem · self-audit → **the 4 techniques of scholar-inspector** |
| OMC MCP tool servers (`wiki_*`/`notepad_*`/`shared_memory_*`/`state_*`) | the *ideas* of accumulation, compaction survival, handoff. ⚠️ oms defaults to **.md degrade** and MCP is an optional accelerator — no new Node MCP is added |

---

## §2. Analysis Baseline Version + Diff Baseline

- **Analysis baseline snapshot = OMC 4.14.4.** This is the OMC version this document saw when it read the backport
  sources (at the time the plugin's `package.json`·`.claude-plugin/plugin.json`·`.claude-plugin/marketplace.json`
  all three read `"version": "4.14.4"`). **This is a *snapshot at analysis time*, not a runtime pin** —
  the omc marketplace declaration in `~/.claude/settings.json` (`repo: Yeachan-Heo/oh-my-claudecode`) has
  no version or commit-SHA, so **OMC always auto-follows the marketplace latest**. Neither oms nor omd has any
  pin tying OMC to a specific version. Therefore an OMC upgrade requires no separate work, and
  the diff baseline below exists only to re-examine *whether the backport adopt/exclude decisions remain valid*.
- **Diff baseline**: OMC has no CHANGELOG (only GitHub commits/releases). On the next OMC update,
  directly inspect the diff of the §1 source files above (`skill-bodies/{deep-interview,plan,ralplan,autopilot,ralph}/SKILL.md`,
  `agents/{analyst,architect,planner,critic}.md`) and judge whether oms needs updating.
- Judgment rule: if an OMC update changes the ***adopted* areas of §3** → review the corresponding backport update.
  If it newly touches the ***excluded* areas of §3** → re-examine whether the exclude decision still holds.

---

## §3. Adopt/Exclude Mapping (internal backport task ID = Tn)

> Tn is this repo's internal backport task identifier (mnemonic). Each row is self-describing as *what changed*,
> so it reads without any external plan document.

### Adopt

| Tn | OMC pattern | oms application (actual change) |
|:---|:---|:---|
| T1 | stage boundaries of deep-interview/ralplan | deepen↔ideate↔outline triple-gate boundary convention. scholar-plan·architect agent **not created**(absorbed into outline·planner) |
| T2 | critic 4 techniques | inserted pre-commitment · assumption(V/R/F) · pre-mortem 5-7 · self-audit(LOW→Open Questions) *inside* the logic/prose 2-lens of `agents/scholar-inspector.md` |
| T4 | ralplan RALPLAN-DR + architect steelman | added `<Consensus_RALPLAN_DR_Protocol>`(Principles/Drivers/Options≥2/steelman/tradeoff/ADR/Short·Deliberate) to `agents/scholar-planner.md` |
| T5 | ralplan sequential consensus | `skills/scholar-outline/SKILL.md` 3 modes(--direct/--consensus/--review), triple sequential-enforcement phrasing, plan.md/outline 2-way split |
| T7 | shared_memory handoff | inter-consensus-stage transfer = `<slug>/consensus/*.md` files as the **default**, MCP is an optional mirror (degrades to .md when absent) |
| T8 | deep-interview gate | `skills/scholar-deepen/SKILL.md` **newly created**(the only net-new) — Round 0 topology + 4-dimension **qualitative** judgment (0 quantification) + 3 challenges + soft limits + human approval + citation-fragile flag |
| T8b | autopilot wiring | inserted the deepen stage + outline --consensus branch into `<Steps>` of `skills/scholar-pilot/SKILL.md` — so the engine actually fires on the autopilot path (preventing dead code) |
| T10 | wiki accumulation | data lives in the project workspace `.oms/wiki/*.md`(gitignore, OMC `.omc/wiki/` pattern) + deterministic grep as the **default**, `wiki_query(category)` is an abstract function (a future MCP swap point). Only the contract doc is in plugin `references/knowledge/README.md` (the store retired the page-tree form and moved to `.hq/community/posts/` — r7, 2026-08-30; this row records the original T10 decision as-is). The reject store is net-new (not a venues.md migration) |
| T11 | notepad compaction survival | on scholar-pilot entry, the citation 3 principles + GATE record go into the `## Priority Context` section of `.oms/notepad.md`(.md default) |
| T12 | verifier request-id | snapshot correlation token in `agents/scholar-verifier.md`(.tex/.bib mtime·hash + defect ID) — blocks stale-PASS reuse in multi-round revise |
| T13 | ralph regression idea | full re-verify of **structural regression**(global consistency of \ref/\cite/numbers) after PASS in `skills/scholar-revise/SKILL.md` — a separate axis from the existing score-regression (score) |
| T14 | (oms's own routing) | added the `deepen` token to the STAGE catalog of `hooks/scholar_route_emit.py` |
| T15 | state path | stage output = `.oms/state/` fixed (removing the unverified `.oms/specs`·`sessions/{sid}` segments). The 30s state-MCP trap is *a future-proofing note only* |

### Exclude (with rationale)

| OMC pattern | Exclude rationale |
|:---|:---|
| **creating** scholar-plan / doc-architect type agents | redundant with outline·planner → absorbed via extension |
| **actual state MCP calls** | overkill for the single·sequential philosophy. notepad(.md) survives compaction better. The 30s trap is documented only |
| persistent-mode **Stop-hook enforcement** | freeze·citation risk, the revise LLM loop suffices. Deferred |
| **ambiguity quantification**(weighted sum·threshold·stability_ratio) | qualitative gate adopted — the magic-number basis is weak, and qualitative is more honest for papers |
| **multi-perspective / realist / adversarial escalation** | redundant with pre-mortem·self-audit, conflicts with inspector's "stop within the requested scope" (blurs the formative↔verify boundary) |
| 15+ code-only runtime items (comment-checker·code-simplifier·ast/lsp·python_repl·ultragoal·loop_authority etc.) | domain-irrelevant |
| **embedding search** | citation-safe collapse — search pulls in hallucinated citations. Deterministic matching only (permanently forbidden now and in the future) |

---

## §4. Reverse Review — omp → oms backport (2026-05-31, 0 adopted)

This document is originally in the OMC → oms direction, but it also examines, by the same yardstick, whether
**what the sibling omp added in 0.2.0**(the result of omp pushing the OMC backport deeper than oms, omp
`references/omc-backport-analysis.md` T17~T25) is worth backporting *in reverse* into oms. (The verdict is
persistently recorded so the next session won't repeat the same analysis.)

**omp 0.2.0's 5 new items → oms adoption = 0.** In adversarial verification(propose↔refute, 2026-05-31), all 5 candidates were rejected:

| omp 0.2.0 candidate | oms verdict | main rationale |
|:---|:---|:---|
| `content_conventions[]` rule type | REJECT | domain asymmetry + redundancy — oms is a *generation pipeline* that creates new `.tex/.bib` on every run, so there is no persistent corpus to repeatedly re-scan with regex. prose quality is already handled by the scholar-inspect(formative)/scholar-verify(summative) **rubric**(qualitative·semantic) — for citation-bound prose, *meaning* (not pattern) governs correctness, so a rigid regex×present/absent engine is unsuitable and risks pressuring pattern-satisfying hallucination. |
| content audit axis (`check_content_rule`) | REJECT | the three premises — rules.json rule store · audit PASS/FAIL gate · specificity counter — are absent in oms (an intended absence). scholar-verify already performs compile/numeric/ref/placeholder/citation as *domain-specific* gates. |
| dead-link (`find_dead_links`, `[[backlink]]`) | REJECT | oms's cross-reference is not a `[[wikilink]]` web but LaTeX `\cite`/`\ref`, and that is already fully matched by scholar-verify. The `[[backlink]]` integrity of `.oms/wiki/` is a *nice-to-have* health-hint, not a *necessary* one (per the user's instruction not to overdo it), and as omp 0.2.1's fix for multi-directory stem false-positives shows, a correct implementation has a cost. |
| `.omp/CONVENTIONS.md` | REJECT | the human-facing mirror of content_conventions[] — since oms has no machine rules to mirror in the first place, it would become an orphan narrative. oms's "default catalog" role is already filled by `venues.md`. |
| specificity content term | REJECT | oms already has specificity (learning-protocol §4, a single origin-ratio value). There is no count target (number of content_conventions rules) for the content term, and redesigning the metric into a polynomial for one term + importing rules.json infrastructure is over-engineering. |

**Conclusion**: omp 0.2.0 is omp-domain-specific (a management loop that repeatedly re-inspects a living
`.omp/` with rules.json regex), so there is nothing — code, prose, or health-hint in any form — to flow over
to oms. This is isomorphic to the 2026-05-31 omx wiki comparative analysis (5 REJECT of 6 candidates, even the
sole ADOPT was "prose only"), and even the one wiki append-only sentence adopted then is already present in
oms's learning-protocol §2, so the residue is 0. The T20~T25 (atomic-write·doctor·worktree-safety etc.) where omp
backported *OMC* more deeply are also unsuitable for oms (generation-domain-irrelevant), so there is no separate adoption.

---

**Analysis snapshot**: OMC 4.14.4 (not a runtime pin — auto-follows marketplace latest, §2) · **isomorphic sibling**: oh-my-docs `references/omc-backport-analysis.md`(document domain) · **reverse review**: omp 0.2.0 → oms adoption 0(§4)
