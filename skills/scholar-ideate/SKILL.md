---
name: scholar-ideate
description: |
  research 결과를 받아 각 방법·기여를 개념노트(methodology/*.md)로 정리 — 개념 SSOT 확정 단계.
  draft(.tex) 전에 여기서 출처·논리·수식 의미를 .md에 굳힌다. 수식은 영어만, 인용 날조 금지.
  Triggers: 개념 정리, 방법 정리, methodology 노트, ideate, 아이디어 구체화, 개념노트 써, 방법론 정리, 기여 정리
---

# scholar-ideate — 개념 정리 & 개념노트(.md) 확정

<Purpose>
research 노트를 입력받아 각 방법·기여를 개념노트(methodology/*.md)로 정리한다. `paper/methodology/*.md` 구조가 모델. 코드의 "설계도/의사코드" — 실제 구현(.tex draft) 전에 개념·출처·수식 의미를 .md에 선확정한다.

이것이 "개념 선확정" 단계: draft(.tex) 전에 여기서 논리와 수식을 굳히지 않으면 drafter가 주장을 채워야 해서 hallucination 위험이 올라간다. scholar-draft의 `.md SSOT 우선` 원칙의 실행 지점.
</Purpose>

<Use_When>
- research가 끝났고 이제 각 방법·기여를 개념노트로 정리할 때
- outline 작성 전 방법론·기여의 논리를 먼저 굳히고 싶을 때
- 수식의 의미·출처·가정을 .md에 명시적으로 적어두고 싶을 때
- draft를 쓰기 전에 개념이 .md에 굳어 있어야 한다고 판단될 때
</Use_When>

<Do_Not_Use_When>
- 관련연구 조사가 아직 안 됐으면 → scholar-research 먼저
- 주장(기여·비교·재현)이 아직 모호하면 → scholar-deepen 먼저 (모호한 주장을 .md로 굳히면 "굳어진 모호함"이 됨 — deepen이 모호성 게이트를 통과시킨 후 ideate)
- 개념노트가 이미 있고 .tex 초안을 쓸 단계라면 → scholar-draft
- outline이 필요하면 → scholar-outline (ideate 후 진행 권장)
- 개념을 안 굳힌 채 .tex부터 쓰려 한다면 → 여기(scholar-ideate) 먼저
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **개념 선확정 원칙** — .md 개념노트 없이 .tex draft 금지. 이 skill이 그 gate.
- ⚠️ **수식은 영어만** — house paper-format 규약 준수. 한국어 수식 설명은 .md 노트 내 설명 텍스트에만, 수식 자체는 영어 notation.
- ⚠️ **인용 날조 금지** — 개념노트에 출처를 쓸 때 미확인 논문·저자 생성 금지. 불확실하면 [출처 미확인 — 사람 확인 필요] flag.
- ⚠️ **ad-block** — house paper-format의 ad-block 규칙 준수. 과장·광고성 표현 금지.
- 개념노트는 .md, .tex 직접 생성 금지 — 노트가 draft의 SSOT가 됨.
</Execution_Policy>

<Steps>
1. research 노트(연구 지형 맵·gap 목록) 확인. 없으면 stop → scholar-research 먼저 안내.
2. 정리할 방법·기여 목록 확정 (논문 주제와 research gap에서 도출).
3. `Task(subagent_type="oh-my-scholar:scholar-researcher", ...)` 위임 (또는 planner 위임):
   - 입력: research 노트 경로, 방법·기여 목록, 관련 참고 노트(있으면), methodology/*.md 모델 경로
   - 지시: 각 방법/기여를 개념노트(.md)로 작성, 수식 의미·가정·출처 명시(영어 notation), 미확인 출처는 flag, ad-block 준수
4. 산출 받음:
   - 방법/기여별 개념노트 내용 (각 .md 파일)
   - 수식 의미·가정·출처 명시 여부
   - 미확인 flag 목록 (사람 확인 필요)
5. 호출자가 개념노트를 `methodology/*.md`로 저장.
6. 미확인 flag 있으면 사람에게 확인 요청 후 노트 갱신.
7. 개념노트 완비 확인 후 → scholar-outline 또는 scholar-draft로 넘길 준비.
</Steps>

<Output>
방법/기여별 개념노트(.md) 내용 + 수식 의미·출처 명시 목록 + 미확인 flag(있으면) + "개념 선확정 완료 — scholar-outline 또는 scholar-draft로 넘길 준비됨" (self-approve 안 함 명시).
</Output>
