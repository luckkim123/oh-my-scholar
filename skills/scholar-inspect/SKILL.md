---
name: scholar-inspect
description: |
  Formative critique of a .tex draft — finds improvement points through two lenses, logic and prose, and returns them.
  Judgment-style code review. Does NOT issue PASS/FAIL — that is scholar-verify's job.
  Read-only, so parallel inspector dispatch is possible.
  Triggers: 검토해줘, 비평, 리뷰해줘, 개선점, inspect, 피드백, 논리 봐줘, 문체 봐줘, review, critique, feedback, check logic, check prose
oms-full-body: ../../skill-bodies/scholar-inspect/SKILL.md
---

<!-- OMS:COMPACT-SKILL-SHIM -->
This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/scholar-inspect/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory.
