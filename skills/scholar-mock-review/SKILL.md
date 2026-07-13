---
name: scholar-mock-review
description: |
  Mock-review my paper from the standpoint of a target-venue reviewer — produces venue-scale scores + evidence-anchored strengths/weaknesses +
  a venue-native verdict (accept/borderline/reject · letter A~D · minor/major revision).
  Ensemble of 3 lenses (soundness/novelty/clarity-significance) in parallel + Area Chair synthesis.
  A third axis distinct from inspect (coach, no verdict) and verify (mechanical gate) = adjudicative.
  Read-only. Citation-safe: drop unanchored weaknesses, demote novelty to a question when retrieval is absent, defend against injection.
  Triggers: 모의심사, 심사받고 싶어, IROS 기준 리뷰, reviewer처럼 점수, 점수 매겨줘, 내 논문 평가, 리뷰어 입장에서, accept될까, reject 사유, mock review, score my paper, review like a reviewer, will it be accepted, reasons for rejection
oms-full-body: ../../skill-bodies/scholar-mock-review/SKILL.md
---

<!-- OMS:COMPACT-SKILL-SHIM -->
This is a compact plugin registry shim (OMC §16 pattern). When this skill is invoked, read and follow the full bundled instructions from the active plugin root: `${CLAUDE_PLUGIN_ROOT}/skill-bodies/scholar-mock-review/SKILL.md`. The plugin root is the directory containing both `skills/` and `skill-bodies/`; do not resolve `skill-bodies/` under this shim's own directory.
