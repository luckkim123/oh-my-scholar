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
oms-full-body: ../../skill-bodies/scholar-init/SKILL.md
---

<!-- OMS:COMPACT-SKILL-SHIM -->
This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/scholar-init/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory.
