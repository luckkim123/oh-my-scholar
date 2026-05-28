---
name: scholar-draft
description: |
  승인된 outline + 개념노트(.md)를 논문 .tex 초안으로 — scholar-drafter에게 단일 위임.
  citation-bound라 생성은 단일 신중, 절대 병렬 금지. 인용 날조 금지, .bib 수정 전 확인.
  Triggers: 초안 써, draft 써줘, 섹션 작성, .tex 써, 논문 본문 써, 초고 작성, write the draft, 섹션 초안
---

# scholar-draft — 논문 초안 작성 (.tex)

<Purpose>
승인된 outline과 개념노트(.md SSOT)를 논문 .tex 초안으로 변환한다. scholar-drafter(유일한 쓰기 권한)에게 단일 위임. 코드의 "함수 구현". draft는 ideate(.md) 완료 후에만 — 개념이 굳기 전엔 논문을 쓰지 않는다.
</Purpose>

<Use_When>
- outline이 GATE 1 승인됐고 이제 .tex 본문을 쓸 때
- 개념노트(methodology/*.md)가 준비됐을 때
- 한 섹션씩 초안/재작성할 때
</Use_When>

<Do_Not_Use_When>
- outline이 아직 없으면 → scholar-outline 먼저
- 개념이 .md에 안 굳었으면 → scholar-ideate 먼저 (개념 선확정 원칙)
- 기존 draft를 통과까지 고치는 거면 → scholar-revise
- 비평만 원하면 → scholar-inspect / 검증만 → scholar-verify
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **생성은 단일 신중, 절대 병렬 금지** — 여러 섹션도 drafter 하나가 직렬로. 병렬 drafter dispatch 금지 (citation hallucination 증폭).
- ⚠️ **인용 날조 금지** — 새 \cite는 검증된 .bib 항목에만. 미검증이면 주장 재작성 또는 사람에게 flag, 절대 지어내지 않음.
- ⚠️ **.md SSOT 우선** — .tex가 노트에 없는 주장을 필요로 하면 멈추고 ideate/research로.
- 큰 수정 전 버전 스냅샷.
- drafter는 self-approve 금지 — draft 후 scholar-inspect/verify 별도 pass로.
</Execution_Policy>

<Steps>
1. outline(planner 산출)과 개념노트(.md) 확인. 없으면 stop → 선행 skill 안내.
2. 작성 범위(섹션) 확정.
3. `Task(subagent_type="oh-my-scholar:scholar-drafter", ...)` 단일 위임:
   - 입력: outline, 개념노트 경로, 범위 섹션, 기존 .tex/.bib, latex.md 카드(스타일)
   - 지시: 한 섹션씩 직렬, 모든 \cite는 검증된 .bib에만, 미검증 인용은 flag, 큰 수정 전 스냅샷.
4. drafter 산출 받음 — 작성 파일 + 사람 확인 필요 목록(미검증 인용·fixable_by_llm=false).
5. **검증은 별도** — scholar-verify/inspect로 넘김 (여기서 self-approve 안 함).
</Steps>

<Output>
drafter가 쓴 .tex/.bib 파일 목록 + 스냅샷 위치 + 사람 확인 필요 목록(미검증 인용 등) + "scholar-verify로 넘길 준비됨" (self-approve 안 함 명시).
</Output>
