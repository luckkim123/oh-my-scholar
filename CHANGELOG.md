# Changelog

All notable changes to oh-my-scholar (oms).

## [0.1.0] — 2026-05-28

초판. 논문 작성을 "코드 작성처럼" 다루는 Claude Code plugin 하네스.

### Added
- **8 stage skills** (단일 SKILL.md, OMD 방식): `scholar-research`, `scholar-ideate`, `scholar-outline` (.md 레이어) → `scholar-draft`, `scholar-inspect`, `scholar-verify`, `scholar-revise` (.tex 레이어) → `scholar-pilot` (전체 오케스트레이션). 각 skill은 Triggers 키워드 + `Task(subagent_type="oh-my-scholar:scholar-*")` dispatch.
- **5 agents** (OMC 11섹션 `<Agent_Prompt>` XML):
  - `scholar-researcher` (sonnet, read-only) — 관련연구·gap·인용 검증
  - `scholar-planner` (opus, read-only) — outline·story arc
  - `scholar-inspector` (opus, read-only) — formative 비평 (logic/prose), pass/fail 아님
  - `scholar-verifier` (opus, read-only) — summative 자동 게이트, 3중 self-approval 금지
  - `scholar-drafter` (sonnet, write) — 유일한 .tex/.bib 작성, 단일 신중, 인용 날조 금지
- **4 reference cards** (가드레일 SSOT): `formats/latex.md`, `formats/bibtex.md`, `rubrics/paper-eval.md` (inspect/verify 2축 분리), `venues.md`.
- **citation-safe PostToolUse hook** (`scholar_verify_emit.py`): .tex/.bib 편집 시 인용 검증 리마인더 주입. OMC post-tool-verifier의 citation-safe 변형 — 자동 수정 지시 안 함.

### Notes — 설계 정체성
- **citation 안전 3원칙**: ①읽기 병렬/생성 단일 ②자동 수정 금지(.bib는 사람 확인) ③개념(.md) 선확정. 논문은 hallucination이 컴파일 에러로 안 잡혀, OMC의 자동 throughput을 *내용 생성*엔 쓰지 않는다.
- **reviewer 고도화**: paper-write의 평평한 5-reviewer score를 OMC inspect(formative)≠verify(summative) 2층으로 재배치. figure/citation/latex-lint는 별도 agent 아닌 verifier 내부 검사로 흡수 → 5 reviewer를 4 agent로 압축.
- **OMC 패턴 이식**: ralph PRD `passes:true` 게이트(scholar-revise), `<External_Consultation>`(OMD가 빠뜨린 것), 3중 self-approval, GATE 3개(human).
- **라우팅 비종속**: oms는 도메인 처리기. 작업방식 레인 판정은 omha(oh-my-heroacademia)가 담당 → oms는 UserPromptSubmit 라우팅 hook 없음.

### Verification
- `pytest tests/` — 7 passed (hook: .tex/.bib 감지·비논문 침묵·자동수정금지·stdlib only·fail-open).
- agent 5개: 11섹션 XML, 읽기전용 4개 disallowedTools, verifier 3중 self-approval, drafter만 write, 전부 External_Consultation (grep 검증).
- skill 8개: Triggers + dispatch + plugin.json skills 배열 정합 (8 exact match).

### Backlog
- v2 후보: `scholar-translate` (한→영), `scholar-standardize` (기존 논문서 스타일 귀납).
- OMD backport (별도 세션): #1 External_Consultation, #2 ralph PRD 게이트, #3 3중 self-approval, #4 PostToolUse 무결성 hook.
- runtime end-to-end 검증: 새 세션 로드 후 scholar-pilot 실측 (구조·hook만 검증됨, 실제 동작 미검증).

[0.1.0]: 신규
