# Venue Configuration Card

> Per-conference/journal constraint SSOT. Referenced by scholar-outline (sections/pages), scholar-verify (page_limit/citation count), and scholar-drafter (class/template). A simplified absorption of the paper-write venues YAML.
>
> ⚠️ **The per-venue *review form* (score axes, scales, verdict vocabulary) is NOT here — its SSOT is `rubrics/venue-review-forms.md`** — scholar-mock-review/scholar-reviewer read that card. This card holds *constraints* (page_limit/min_citations/sections); that card holds the *review form* (NeurIPS 1-4/1-10, IROS letter A~D, journal minor/major revision). Role separation.
> Score bands (optional per-venue calibration data — band/meaning/source) live inside that same card too, as a per-form slot: see `rubrics/venue-review-forms.md`'s "Score bands" block. This card keeps delegating that content — no score data lands here.

## Schema

```yaml
name:            # display name (IROS 2026)
key:             # identifier (iros)
class:           # \documentclass (ieeeconf)
compile_engine:  # pdflatex | xelatex | lualatex
bib_style:       # IEEEtran
structure_type:  # flat | system | thesis — scale variation (scholar-planner <Structure_Types> is the SSOT)
                 #   Every paper shares a common skeleton (Intro→[Method unit 1..N: Overview→Proposed→experiments for that unit]→Conclusion).
                 #   structure_type only governs how many times that skeleton repeats and how far it unfolds (the structure itself is the same).
                 #   flat   = 1 Method unit. Short papers (IROS/ICRA/RA-L/CVPR). Related Work as standalone Section II.
                 #   system = multi-contribution journal system paper (T-RO, etc.). Skeleton repeated per contribution + shared system section + (if needed) a late integrated-experiments hybrid.
                 #   thesis = multi-contribution dissertation. Isomorphic to system + dissertation form elements. Subtypes: thesis-by-papers (self-contained chapters) vs monograph (cumulative chapters, standalone Ch.2 RW).
                 #   If unspecified, the planner infers it (small page_limit and 1 contribution→flat / large or null and multiple contributions→system/thesis).
page_limit:      # integer or null (unlimited)
sections:        # [Introduction, Related Work, Method, ...]  ← flat only. For system/thesis, the planner generates the per-contribution section/chapter skeleton from the number of contributions.
required_sections: # required sections
quality_threshold: # verify pass score (0-100, default 80)
max_review_rounds: # max revise loops (default 5)
regression_threshold: # allowed score drop (default 5)
min_citations:   # minimum citation count
self_citation_max_ratio: # self-citation cap (default 0.20)
llm_policy:       # this venue's LLM-use policy (drafter proposes disclosure, verify reminds of author responsibility)
                 #   {author_responsible: true, llm_authorship: forbidden, citation_verification: required, prompt_injection: forbidden, disclosure: required|optional}
                 #   ⚠️ self-verified grade — venue policies are updated yearly, so *cross-check against the policy source text before submission*.
                 #   Basis (2026-06 survey): NeurIPS 2025/ICML 2026/ICLR — LLM authorship forbidden + authors responsible for verifying every citation's existence and accuracy,
                 #   ICML explicitly forbids prompt injection. Source: neurips.cc/Conferences/2025/LLM. Landscape in the global wiki reference.
                 #   oms use: draft proposes an LLM-use acknowledgment in the produced paper (CLASSICA 3 criteria: verification, substantive contribution, transparency); verify reminds of "author responsibility to verify every citation."
review_weights:  # {logic: 1.0, prose: 0.8, ...} inspect weights
voice:           # active | passive | mixed — voice preference (STEM default mixed: passive for method, active for contributions). Rule SSOT = writing-craft.md §5
prose_defaults:  # list of *universal writing propositions* enforced for this venue (scholar-learn promotions). e.g. [old_new_flow, em_dash_cap]
                 #   Values are only the *keys* of writing-craft.md rules — the rule bodies are owned by writing-craft.md as SSOT (do not re-list here).
                 #   user/venue-specific *expression preferences* go to wiki pattern/ (light, advisory), not here (learning-protocol dual-track).
                 #   exemplars: paths to ~5 randomly chosen representative paragraphs for style imitation (no similarity-curated/embedding selection — writing-craft.md §6).

# ── ⭐ self-specialization meta (H5 — heavy-channel backport, 2026-05-31) ──
specificity:     # 0..1 — the fraction of this venue's defaults that have *hardened through learning* (0=pure template default, 1=fully user-specialized)
                 #   = (count of items with origin∈{inductive,learned}) / (count of active default items). monotonic (promotion raises or holds).
                 #   The computation/update rules are owned by references/learning-protocol.md §4 as SSOT.
origins:         # per-item provenance map {required_sections: learned, section_order: preset, ...}
                 #   preset=template default (0.0) / inductive=derived from past papers (1.0) / learned=promoted from learned.md (1.0)
learned_refs:    # [OBS-0003, ...] — provenance of learned defaults (which observation it was promoted from). No silent changes (§6.C).
```

> ⚠️ **These three fields are written only by `scholar-learn` (after passing the human gate).** When the user writes venue values directly
> they can be omitted (unspecified = all preset = specificity 0). No automatic enforcement: no matter how high the confidence/evidence,
> venue defaults do not change without human approval (`learning-protocol.md` §6.B). citation/.bib and the like are
> permanently not promotion targets of this meta (§6.F).

## Example — IROS (conference)

```yaml
name: "IROS 2026"
key: iros
class: ieeeconf
compile_engine: pdflatex
bib_style: IEEEtran
structure_type: flat
page_limit: 6
sections: [Introduction, Related Work, Method, Experiments, Conclusion]
quality_threshold: 80
max_review_rounds: 5
min_citations: 15
self_citation_max_ratio: 0.20
review_weights: {logic: 1.0, prose: 0.8}
llm_policy: {author_responsible: true, llm_authorship: forbidden, citation_verification: required, prompt_injection: forbidden, disclosure: required}
```

## Example — POSTECH M.Sc. Thesis (thesis)

```yaml
name: "POSTECH M.Sc. Thesis"
key: postech_msc_thesis
class: report
compile_engine: xelatex   # includes Korean
structure_type: thesis   # multi-contribution dissertation. Common skeleton repeated per contribution. Subtype (thesis-by-papers/monograph) decided by the planner.
page_limit: null
quality_threshold: 80
min_citations: 50
review_weights: {logic: 1.2, prose: 1.2}
# When structure_type: thesis, the planner generates the chapter skeleton from the number of contributions (common skeleton repeated):
#   I. Introduction(Background, Contributions, Outline) → II. [shared platform/system](optional) →
#   III~. [per-contribution chapters, each Overview→Proposed→experiments for that contribution] → (if needed, a late integrated-experiments chapter) →
#   Conclusion → Summary(Korean) → References.
#   For thesis-by-papers, each chapter is self-contained + RW distributed / for monograph, chapters are cumulative + standalone Ch.2 RW (scholar-planner <Structure_Types> is SSOT).
```

## Example — IROS specialized through learning (specificity > 0)

What it looks like after `scholar-learn` promotes "IROS always includes Ablation" through the human gate:

```yaml
name: "IROS 2026"
key: iros
required_sections: [Introduction, Related Work, Method, Experiments, Ablation, Conclusion]
self_citation_max_ratio: 0.10        # user habit "self-cite below 0.1" promoted
# ── meta ──
specificity: 0.29                    # of 7 active defaults, 2 (Ablation, self-cite) are learned → 2/7 = 0.29
# origins lists all 7 active defaults (denominator = 7, numerator = 2 learned) — must match the fraction 1:1 (§4)
origins: {required_sections: learned, self_citation_max_ratio: learned, sections: preset, page_limit: preset, quality_threshold: preset, max_review_rounds: preset, min_citations: preset}
learned_refs: [OBS-0003, OBS-0011]   # provenance: which observation it came from
```

## Notes

- venue files live at `.oms/venues/<key>.yaml` or in the user's project. oms treats this card as the schema SSOT, while the actual values are per-project.
- No absolute-path coupling like `template_dir` is kept here (avoiding paper-write coupling points ①④). A venue is purely declarative constraints.
- ⭐ **self-specialization**: `specificity`/`origins`/`learned_refs` are the on-disk trace of "the more you use it, the more specialized to this user." The dynamics are owned by `references/learning-protocol.md` (2-channel, promotion criteria, specificity formula) as SSOT. Heavy-channel promotion always goes through the human gate.
