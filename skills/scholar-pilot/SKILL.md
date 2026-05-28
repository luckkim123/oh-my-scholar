---
name: scholar-pilot
description: |
  논문 전체 파이프라인 오케스트레이션 — research→ideate→outline(GATE1)→draft→inspect→verify
  →revise(GATE2)→제출(GATE3). OMC autopilot의 논문판. citation 안전 3원칙 강제.
  Triggers: 논문 만들어줘, 논문 써줘, 처음부터 끝까지, 논문 파이프라인, paper from scratch,
  write a paper, 논문 자동, 전체 논문 작업, oms pilot
---

# scholar-pilot — 논문 전체 오케스트레이션 (autopilot 논문판)

<Purpose>
research question부터 제출 준비까지 논문 전 단계를 조율한다. OMC autopilot의 논문판이되, citation-bound 안전을 위해 **생성은 단일·읽기는 병렬**로 제한하고 사람 GATE 3개를 끼운다.
</Purpose>

<Use_When>
- "논문 처음부터 끝까지 만들어줘" — 짧은 brief에서 전체 파이프라인
- 어느 단계부터 시작할지 명확하면 그 단계부터 (--from)
</Use_When>

<Do_Not_Use_When>
- 한 단계만 필요하면 → 해당 scholar-* skill 직접
- citation-bound 논문이라 **완전 무인 자동은 금지** — GATE 3개는 사람이 반드시 끊는다
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **citation 안전 3원칙 강제**:
  1. 읽기(research·inspect·verify)는 병렬 OK, **생성(draft)은 단일 신중 절대 병렬 금지**.
  2. verifier가 인용 결함 감지해도 **자동 수정 금지** — 사람 확인.
  3. draft(.tex) 전 ideate(.md)에서 개념·출처 선확정.
- GATE 3개는 사람 결정점 — 자동 통과 금지.
- 각 단계는 전용 skill에 위임 (재구현 금지).
- 단계 산출은 `.oms/state/`에 기록 (OMC state 패턴) — 중단 후 재개 가능.
</Execution_Policy>

<Steps>
1. **research**: scholar-research → 연구맵·gap·검증된 인용 (.md)
2. **ideate**: scholar-ideate → 개념노트 methodology/*.md (개념 SSOT 확정)
3. **outline**: scholar-outline → 섹션구조·story arc
   ━━━ **GATE 1**: outline 승인 (human) — proceed/revise/abort ━━━
4. **draft**: scholar-draft → .tex (drafter 단일 신중)
5. **inspect**: scholar-inspect → formative 비평 (병렬 OK, 읽기전용)
6. **verify**: scholar-verify → summative 자동 게이트
   ━━━ **GATE 2**: 리뷰 결과 확인 (human) — proceed/another round/address/abort ━━━
7. **revise**: scholar-revise → verify PASS까지 루프 (필요 시)
   ━━━ **GATE 3**: 제출 확인 (human) — confirm/revise/abort ━━━
8. 제출 준비물 정리 (PDF·소스·체크리스트).
</Steps>

<Output>
각 단계 산출물 경로 + GATE 3개 결정 이력 + 최종 PASS 논문(.tex/PDF) + 사람 확인 필요 잔여(미검증 인용·fixable=false) + .oms/state 진행 기록.
</Output>
