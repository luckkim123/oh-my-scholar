---
name: scholar-inspect
description: |
  .tex 초안을 formative 비평 — logic·prose 두 렌즈로 개선점을 찾아 돌려준다.
  판단형 코드 리뷰. PASS/FAIL 안 냄 — 그건 scholar-verify 몫.
  읽기전용이라 병렬 inspector dispatch 가능.
  Triggers: 검토해줘, 비평, 리뷰해줘, 개선점, inspect, 피드백, 논리 봐줘, 문체 봐줘
---

# scholar-inspect — 논문 초안 formative 비평

<Purpose>
draft된 .tex에 코드 리뷰를 건다. scholar-inspector(읽기전용)에게 위임해 logic·prose 두 렌즈로 개선점을 찾아 반환한다. 코드의 "코드 리뷰" — 판단형이지 기계 게이트가 아니다.

⚠️ **PASS/FAIL을 내지 않는다.** 통과·실패 판정이 목적이면 scholar-verify를 쓸 것. 여기서 나오는 것은 severity 분류된 개선점 목록이며, 최종 판단은 사람이 한다.
</Purpose>

<Use_When>
- draft/revise 후 제출 전에 논리·문체 개선점을 비평받고 싶을 때
- 기여-증거 대응, 구조 논리, 학술 문체, 과장 표현을 점검받고 싶을 때
- 수정 우선순위를 잡기 위해 severity 분류된 피드백이 필요할 때
</Use_When>

<Do_Not_Use_When>
- 통과/실패 게이트 판정이 필요하면 → scholar-verify
- 비평 결과를 바로 .tex에 반영하고 싶으면 → scholar-revise
- 아직 draft가 없으면 → scholar-draft 먼저
- 개념이 .md에 굳지 않은 상태면 → scholar-ideate 먼저
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **PASS/FAIL 판정 금지** — inspector가 "통과" "실패" "거절" 같은 게이트 언어를 쓰면 이 분리가 무너진다. finding은 severity(critical/important/minor) + 개선 제안으로만.
- ⚠️ **읽기전용** — inspector는 .tex/.bib를 수정하지 않는다. 비평만.
- ⚠️ **self-approval 금지** — drafter와 inspector는 다른 lane. 자기가 쓴 draft를 자기가 inspect하지 않는다.
- logic과 prose는 독립적이므로 inspector를 병렬 dispatch해도 안전(읽기전용).
- fixable_by_llm=false 항목(실험 누락·기여 범위 변경 등)은 자동 수정 시도 금지 — 사람 플래그만.
</Execution_Policy>

<Steps>
1. **SSOT 먼저 읽기 (필수, `references/learning-protocol.md` §8)** — .tex만 보고 비평하지 말 것. logic 렌즈가 "기여-증거 대응"을 판단하려면 *무엇이 이 논문의 진짜 기여·챕터축·절배치인지*를 1차 SSOT에서 알아야 한다. 비평 전 반드시 `.oms/<slug>/outline/outline.md`(현행 섹션 구조·story arc·기여 매핑)와 `.oms/<slug>/methodology/*.md`(각 방법·수식의 출처·의미)를 읽어 현행 상태를 파악한다. `research_summary/`·code_survey 노트는 2차 보조일 뿐 — 챕터축·스코프 판단의 권위가 아니다(구조 재설계로 stale될 수 있음). SSOT를 건너뛰면 outdated 노트를 기준으로 오판한다.
2. 대상 .tex 파일 경로와 비평 범위(전체 또는 특정 섹션) 확인.
3. `Task(subagent_type="oh-my-scholar:scholar-inspector", ...)` 위임 (logic·prose 병렬 dispatch 가능):
   - 입력: .tex 파일 경로, 비평 범위, **현행 outline·methodology SSOT 경로(§1에서 읽은 것)**, paper-eval.md 루브릭(inspect 축), latex.md 카드
   - 지시:
     - **logic 렌즈**: 기여-증거 대응(현행 outline 기준), 구조 논리, 기저선 비교, devil's advocate
     - **prose 렌즈**: 학술 문체, 과장 규율, 반복, 전환, 문장 길이
     - 각 finding: severity(critical/important/minor) + location(.tex 섹션·줄) + issue + evidence(.tex 원문 인용) + suggestion + fixable_by_llm(true/false)
     - PASS/FAIL 판정 출력 금지
4. inspector 산출 수령 — finding 목록 취합.
5. 요약 출력: severity별 finding 수 + critical 항목 우선 나열 + fixable_by_llm 분류.
6. "수정 원하면 → scholar-revise, 게이트 판정 원하면 → scholar-verify" 안내.
</Steps>

<Output>
- finding 목록 (severity · location · issue · evidence · suggestion · fixable_by_llm)
- severity별 카운트 (critical N / important N / minor N)
- fixable_by_llm=false 항목 → 사람 확인 필요 목록
- 다음 단계 안내 (revise / verify)
- ⚠️ PASS/FAIL 판정 없음 — 판단은 사람이.
</Output>
