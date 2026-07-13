---
name: scholar-read
description: |
  Deep-read ONE external paper (PDF / arXiv id / URL / pasted text) into a structured, citation-safe reading note.
  Single dispatch (no parallel content generation); the note is a secondary memo, NEVER a .bib source — the only door into the bibliography stays scholar-research → human-confirmed .bib.
  Triggers: 논문 읽어줘, 이 논문 정리, 딥리드, 리딩노트, read this paper, deep read, reading note, analyze this paper
oms-full-body: ../../skill-bodies/scholar-read/SKILL.md
---

<!-- OMS:COMPACT-SKILL-SHIM -->
This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/scholar-read/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory.
