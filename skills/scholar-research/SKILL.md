---
name: scholar-research
description: |
  관련연구·선행연구 지형을 조사하고 gap을 식별 → .md 연구노트로 산출.
  citation-bound라 인용 검증 강제, 날조 금지. 병렬 읽기는 OK, 인용 생성은 검증 후만.
  Triggers: 관련연구 조사, related work, 선행연구, gap 찾아, 문헌조사, 리서치 해줘, 연구 지형, survey, 논문 조사
---

# scholar-research — 관련연구 조사 & gap 식별

<Purpose>
논문 작성 전 관련연구 지형을 체계적으로 조사하고 gap을 식별한다. scholar-researcher에게 위임해 검증된 인용·연구맵·gap 목록을 .md 연구노트로 산출. 코드의 "요구사항 수집" — 무엇을 왜 해야 하는지 근거를 먼저 쌓는 단계.
</Purpose>

<Use_When>
- 논문을 시작하기 전 관련연구 맵과 gap이 필요할 때
- related work 섹션 작성 전 실질적인 선행연구 조사가 필요할 때
- 기존 방법들의 한계를 체계적으로 정리하고 싶을 때
- ideate/outline에 앞서 근거 자료를 확보해야 할 때
</Use_When>

<Do_Not_Use_When>
- outline이 이미 있고 이제 개념을 정리할 단계라면 → scholar-ideate
- 초안이 있고 관련연구 섹션을 직접 작성할 단계라면 → scholar-draft
- 특정 논문의 수식·주장을 검증하는 거라면 → scholar-verify
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **인용 날조 금지** — researcher agent가 강제. 존재하지 않는 논문·저자·연도 생성 절대 금지. 미확인 출처는 flag로 남기고 사람에게 확인 요청.
- ⚠️ **병렬 읽기는 OK, 병렬 인용 생성은 금지** — 여러 자료를 동시에 읽고 분석하는 것은 허용. 단, 인용 항목 자체를 여러 agent가 병렬 생성하면 hallucination 증폭.
- 산출물은 .md 연구노트 — .tex 직접 작성 금지. 노트가 ideate/outline/draft의 입력이 됨.
- researcher는 self-approve 금지 — 노트 산출 후 사람 검토 권장.
</Execution_Policy>

<Steps>
1. 조사 주제·범위 확인 (논문 주제, 타깃 베뉴, 이미 알고 있는 선행연구).
2. `Task(subagent_type="oh-my-scholar:scholar-researcher", ...)` 위임:
   - 입력: 논문 주제, 조사 범위, 이미 가진 참고문헌 목록(있으면), 관련 참고 노트 경로(있으면)
   - 지시: 관련연구 클러스터링, 각 방법의 한계·gap 식별, 인용은 검증된 것만(미확인은 flag), 병렬 읽기 OK
3. researcher 산출 받음:
   - 연구 지형 맵 (방법 계열별 분류)
   - 검증된 인용 목록 (저자·연도·제목 확인된 것)
   - gap 목록 (기존 방법이 해결 못한 것)
   - 미확인 flag 목록 (사람 확인 필요)
4. 산출을 .md 연구노트로 호출자가 저장 (경로는 호출자가 결정 — 보통 `paper/research/*.md`).
5. 미확인 flag가 있으면 사람에게 확인 요청 후 노트 갱신.
</Steps>

<Output>
연구 지형 맵 + 검증된 인용 목록 + gap 목록이 담긴 .md 연구노트 내용 + 미확인 flag 목록(있으면) + "scholar-ideate 또는 scholar-outline으로 넘길 준비됨" (self-approve 안 함 명시).
</Output>
