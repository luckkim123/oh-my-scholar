---
name: scholar-pilot
description: |
  Full paper pipeline orchestration — research→ideate→outline(GATE1)→draft→inspect→verify
  →revise(GATE2)→submission(GATE3). The paper-domain version of OMC autopilot. Enforces the 3 citation-safety principles.
  Triggers: 논문 만들어줘, 논문 써줘, 처음부터 끝까지, 논문 파이프라인, paper from scratch,
  write a paper, 논문 자동, 전체 논문 작업, oms pilot
oms-full-body: ../../skill-bodies/scholar-pilot/SKILL.md
---

<!-- OMS:COMPACT-SKILL-SHIM -->
This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/scholar-pilot/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory.
