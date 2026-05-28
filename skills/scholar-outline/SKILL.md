---
name: scholar-outline
description: |
  research·ideate 산출물을 받아 논문의 섹션구조·story arc를 설계한다 — scholar-planner에게 단일 위임.
  citation-bound라 인용 의존 매핑은 검증된 researcher 목록에서만. 인용 날조 금지.
  GATE 1(outline 승인 — human) 직전까지가 이 skill의 범위. 자동 통과 없음.
  Triggers: outline 짜줘, 논문 구조, 목차 설계, story arc, 섹션 구성, 아웃라인, 구조 설계, section outline
---

# scholar-outline — 섹션구조·story arc 설계

<Purpose>
research·ideate 단계의 산출물(연구맵, 개념노트 .md)을 받아 논문의 섹션 트리·story arc·word budget·인용 의존 매핑을 설계한다. 코드 개발에서 "아키텍처 설계"에 해당하는 역할이다. scholar-planner(유일한 설계 권한)에게 단일 위임. outline이 확정되면 GATE 1(사람 승인)을 거쳐야만 다음 단계(scholar-draft)로 넘어간다 — 자동 통과는 없다.
</Purpose>

<Use_When>
- research(연구맵·gap 진술)와 ideate(개념노트 .md)가 끝나고 논문 구조를 잡을 때
- 섹션 순서·story arc·word budget을 처음 설계할 때
- 기존 outline을 전면 재구성할 때
</Use_When>

<Do_Not_Use_When>
- 연구·개념이 아직 안 굳었으면 → scholar-research / scholar-ideate 먼저 (개념 선확정 원칙)
- outline이 이미 있고 .tex 본문을 쓸 단계면 → scholar-draft
- 기존 draft의 구조 비평만 원하면 → scholar-inspect
- 논문의 특정 주장이나 계산 검증이면 → scholar-verify
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **planner는 단일 신중 위임** — 여러 venue·논문도 planner 하나가 처리. 병렬 planner dispatch 금지 (story arc 불일치 증폭).
- ⚠️ **인용 날조 금지** — 각 섹션의 의존 인용은 researcher가 검증한 목록 안에서만. 없는 인용이 필요하면 "researcher 재확인 필요" 표시, 절대 창작하지 않음.
- ⚠️ **GATE 1은 자동 통과 없음** — planner 산출이 아무리 훌륭해도 사람의 proceed/revise/abort 없이는 scholar-draft로 넘기지 않는다.
- outline은 설계 문서다 — 논문 본문 prose를 outline 안에 쓰지 않는다.
- 큰 구조 변경 전 기존 outline 스냅샷.
</Execution_Policy>

<Steps>
1. 입력 확인: researcher 연구맵(gap 진술·인용 목록)과 ideate 개념노트(.md) 경로 확인. 없으면 stop → 선행 skill 안내.
2. 작성 대상 venue 확인: `references/venues.md`에서 sections·page_limit·required_sections를 확인. venue 미지정이면 사람에게 확인.
3. `Task(subagent_type="oh-my-scholar:scholar-planner", ...)` 단일 위임:
   - 입력: 연구맵, 개념노트 경로, venue 카드(`references/venues.md`) 참조 지시
   - 지시: 섹션 트리(목적·핵심 메시지·word budget·의존 인용 key) + story arc 필요성 사슬 + word budget 합계 page_limit×500 이내 + 인용은 researcher 검증 목록에서만 + 누락 인용은 "researcher 재확인 필요" 표시
4. planner 산출 받음 — 섹션 트리·story arc·word budget 요약·인용 의존 전체 매핑·미검증 인용 요청 목록.
5. 산출물을 `06_outline.md`에 저장 (프로젝트 노트 폴더 기준).
6. **GATE 1 — 사람 승인 요청**:
   - outline 전문을 제시하고 다음 세 가지 선택지를 명시한다:
     - **proceed**: outline 승인 → scholar-draft로 진행 가능
     - **revise**: 수정 사항 지시 → planner 재위임 후 GATE 1 재실행
     - **abort**: 이 outline 폐기 → 선행 단계(research/ideate)로 복귀
   - 사람의 명시적 응답 전까지 scholar-draft 진행 금지.
</Steps>

<Output>
planner가 설계한 outline(섹션 트리·story arc·word budget 요약·인용 의존 매핑) + `06_outline.md` 저장 위치 + 미검증 인용 요청 목록(없으면 "없음") + **GATE 1 승인 요청** (proceed / revise / abort 선택 안내, self-approve 안 함 명시).
</Output>
