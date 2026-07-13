---
name: scholar-revise
description: |
  A revise-verify loop on a paper until verify gives a PASS — the paper-edition of ralph. Treats the defect list like a PRD and
  repeats drafter (revise) and verifier (verify) until the `passes:true` gate. Stops and reports if the same defect recurs 3 times.
  ⚠️ "Content generation" defects must NOT be auto-fixed (single, careful pass). Triggers: 통과까지 고쳐, 다 잡아줘,
  검증 통과할 때까지, revise until pass, fix until verified, 수정 루프, 리비전 돌려
oms-full-body: ../../skill-bodies/scholar-revise/SKILL.md
---

<!-- OMS:COMPACT-SKILL-SHIM -->
This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/scholar-revise/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory.
