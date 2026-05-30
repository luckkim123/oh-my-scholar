---
name: scholar-revise
description: |
  논문을 verify PASS 받을 때까지 수정-검증 루프 — ralph의 논문판. 결함목록을 PRD처럼 두고
  passes:true 게이트까지 drafter(수정)·verifier(검증) 반복. 같은 결함 3회면 멈추고 보고.
  ⚠️ "내용 생성" 결함은 자동수정 금지(단일 신중). Triggers: 통과까지 고쳐, 다 잡아줘,
  검증 통과할 때까지, revise until pass, fix until verified, 수정 루프, 리비전 돌려
---

# scholar-revise — 수정-검증 루프 (ralph 논문판)

<Purpose>
논문을 scholar-verify가 PASS 줄 때까지 수정한다. OMC ralph의 논문판: 결함을 PRD(acceptance criteria)처럼 두고 `passes:true` 게이트까지 drafter(수정)·verifier(검증)를 fresh 증거로 반복. "do your best"가 아니라 *게이트 통과 보장*.
</Purpose>

<Use_When>
- draft/inspect/verify가 끝났고 FAIL 항목을 자동 루프로 해소하고 싶을 때
- "통과까지 알아서 고쳐줘", "다 잡아줘" 류
</Use_When>

<Do_Not_Use_When>
- 새 초안이면 → scholar-draft
- 조언만 원하면 → scholar-inspect (수정 안 함)
- ⚠️ 인용·기여 같은 **내용 생성 결함**은 자동 루프로 돌리지 말 것 — drafter가 단일 신중으로, 사람 확인 거쳐. revise 루프는 fixable_by_llm=true(텍스트 재구성·컴파일 오류·참조 정합) 결함에만.
</Do_Not_Use_When>

<Execution_Policy>
- 결함목록을 PRD처럼: 각 결함이 acceptance criterion, `passes:true`는 verifier가 그 항목을 PASS 줄 때.
- 각 반복: drafter 수정(fixable_by_llm=true만) → verifier가 **fresh 증거**로 재검증 (이전 검증 재사용 금지).
- **scope 축소·placeholder·검사 우회로 PASS 만들지 말 것** (ralph: no scope reduction, no deleting tests, no faking).
- drafter와 verifier는 **다른 lane** — self-approval 금지.
- **같은 결함 3회 반복 → 멈추고 "fundamental issue" 보고** (무한 루프 차단).
- 최대 반복(venue max_review_rounds, 기본 5) 초과 시 멈추고 현황 보고.
- ⚠️ fixable_by_llm=false(실험·그림 누락·기여 범위·미검증 인용)는 루프에 안 넣음 → 사람에게.
- ⚠️ **PASS 직후 구조-regression 전수 재verify**: 한 회차가 전부 passes:true가 되면, 곧장 종료하지 말고 *이번 수정이 다른 섹션의 전역 정합을 깼는지* 한 번 더 전수 검증한다 — `\ref`↔`\label`·`\cite`↔.bib·본문↔표/그림 수치가 *수정한 섹션 밖에서* 깨졌는지. 한 곳을 고치면 다른 \ref 번호·인용 정합·수치 합이 어긋날 수 있다(국소 수정의 전역 부작용). 깨진 게 있으면 그 항목을 새 결함으로 루프에 되넣는다.
  - ==기존 score-regression과 별개 축(혼동 방지)==: 아래 Steps 3c의 `score-regression(품질 점수 하락 > venue regression_threshold)`은 **품질 점수 하락** 축(루프를 *멈추는* 가드)이다. 이 신설 조항은 **구조 정합 regression**(참조·인용·수치 전역 정합 깨짐) 축으로 *다른 종류* — 점수가 아니라 기계적 정합이고, 멈추는 게 아니라 깨진 항목을 루프로 되돌린다. 두 축은 독립적으로 검사한다.
</Execution_Policy>

<Steps>
1. 현재 상태: `Task(subagent_type="oh-my-scholar:scholar-verifier", ...)` → FAIL 항목 목록 = PRD.
2. fixable_by_llm으로 분류: true → 루프 대상, false → 사람 escalation 목록.
3. **루프** (각 회차):
   a. 수정: `Task(subagent_type="oh-my-scholar:scholar-drafter", ...)` — fixable=true 항목만, 단일 신중, 큰 수정 전 스냅샷.
   b. 재검증: `Task(subagent_type="oh-my-scholar:scholar-verifier", ...)` — fresh 증거 전수.
   c. 전부 passes:true → **구조-regression 전수 재verify**(\ref/\cite/수치 전역 정합이 수정 섹션 밖에서 깨졌는지). 깨진 항목 있으면 새 결함으로 (a)에 되넣음, 없으면 종료. 아니면 같은 결함 반복 여부:
      - 같은 결함 3회째 → 멈추고 "fundamental issue" 보고.
      - score-regression(품질 점수 하락 > venue regression_threshold) → 멈추고 보고. (구조-regression과 별개 축)
      - 아니면 (a)로.
4. PASS(+구조-regression 통과) 또는 stop 조건에서 종료. GATE 2(리뷰 결과 확인 — human) 제시.
</Steps>

<Output>
PASS 받은 .tex/.bib + 반복 이력(각 회차 FAIL→수정 요지) + 최종 verify 증거표 + 사람 escalation 목록(fixable=false·미검증 인용).
또는 stop 보고(같은 결함 3회 / regression / 최대 반복 초과 + 남은 결함).
</Output>
