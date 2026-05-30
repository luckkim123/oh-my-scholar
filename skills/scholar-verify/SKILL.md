---
name: scholar-verify
description: |
  .tex/.bib를 summative 자동 게이트 — 컴파일·수치·참조·용어·placeholder·인용을 기계적으로 PASS/FAIL.
  코드의 "CI". 비평·조언 없음, 객관 증거만.
  인용 결함 감지 시 자동수정 금지 — 사람 확인 목록으로만.
  Triggers: 검증해줘, verify, 통과 확인, 컴파일 체크, 인용 검증, 게이트 확인, PASS 판정
---

# scholar-verify — 논문 초안 summative 게이트

<Purpose>
draft/revise된 .tex/.bib를 기계적 pass/fail 게이트로 검사한다. scholar-verifier(읽기전용)에게 위임해 컴파일·수치 정합·그림표 참조·용어 일관·placeholder·인용 정합 항목을 점검한다. 코드의 "CI" — 객관 증거로만, 조언·비평 없음.

⚠️ **비평·조언을 하지 않는다.** 논리·문체 개선점이 목적이면 scholar-inspect를 쓸 것. 여기서 나오는 것은 항목별 PASS/FAIL과 증거뿐이다.
⚠️ **인용 결함은 자동 수정하지 않는다.** 인용 오류를 감지해도 .bib를 건드리지 않는다 — 사람 확인 목록으로만 돌려준다.
</Purpose>

<Use_When>
- draft/revise 후 제출 전 객관적 통과 판정이 필요할 때
- 컴파일 오류·undefined ref·수치 불일치·placeholder 잔존을 기계적으로 확인할 때
- 인용(\cite ↔ .bib) 정합을 검사할 때
- venue 페이지 한도·최소 인용 수 충족 여부를 확인할 때
</Use_When>

<Do_Not_Use_When>
- 논리·문체 비평·조언이 필요하면 → scholar-inspect
- 비평 결과를 .tex에 반영하고 싶으면 → scholar-revise / scholar-draft
- 아직 draft가 없으면 → scholar-draft 먼저
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **fresh 증거만** — "should/probably/seems/아마도" 금지. 로그 라인·grep 결과·실제 수치로만 판정.
- ⚠️ **인용 자동수정 절대 금지** — \cite ↔ .bib 불일치·DOI 미검증 등 인용 결함은 감지만 하고 .bib를 수정하지 않는다. 사람 확인 목록으로 반환.
- ⚠️ **조언·비평 금지** — verifier는 "이 문장이 약하다" 같은 판단형 코멘트를 달지 않는다.
- ⚠️ **self-approval 금지** — drafter/reviser와 verifier는 다른 lane.
- FAIL 항목은 무엇이 왜 실패했는지 증거(로그 라인·grep 결과·파일:줄 위치) 첨부 필수.
- FAIL이 있으면 fixable_by_llm 분류 — true(텍스트·ref 수정)는 scholar-revise로, false(실험 데이터 누락·그림 생성 등)는 사람 플래그.
</Execution_Policy>

<Steps>
1. 대상 .tex/.bib 파일 경로, venue 정보(page_limit·min_citations) 확인.
2. `Task(subagent_type="oh-my-scholar:scholar-verifier", ...)` 위임:
   - 입력: .tex/.bib 경로, paper-eval.md 루브릭(verify 축), latex.md 카드, bibtex.md 카드, venues.md
   - 지시: 아래 6개 항목 각각 PASS/FAIL + 증거 출력. 조언·비평 없음. 인용 결함은 목록만.
     - **컴파일**: latexmk exit 0, undefined ref/cite 0
     - **수치 정합**: 본문 수치 ↔ 표/그림 일치
     - **그림·표 참조**: `\ref` ↔ `\label` 전수 매칭
     - **용어 일관**: 같은 개념 동일 용어, 약어 첫 등장 정의
     - **placeholder**: TODO/FIXME/XX 잔존 0
     - **인용 정합**: `\cite` ↔ .bib 항목 존재 (DOI 실재는 사람 확인 목록)
     - **venue 메타 정합 (읽기전용)**: specificity↔origin↔learned_refs 무결성 (불일치=WARN, 수선 안 함)
3. verifier 산출 수령 — 항목별 PASS/FAIL 취합.
4. FAIL 항목 있으면 fixable_by_llm 분류:
   - fixable_by_llm=true → scholar-revise에 전달 가능
   - fixable_by_llm=false → 사람 확인 필요 목록
5. 미검증 인용(DOI 실재·저자명 정확도 등) → 자동수정 없이 사람 확인 목록으로만 반환.
6. **venue 메타 정합 (읽기전용, H10)** — venue 카드/yaml 에 self-specialization 메타가 있으면 무결성만 확인:
   - `specificity` ∈ [0,1] 이고 `(origin∈{inductive,learned} 항목 수)/(활성 기본값 수)` 와 일치하는가
   - `learned` origin 항목마다 `learned_refs` provenance 가 있는가 (§6.C silent 변경 금지)
   - 불일치 시 **경고(WARN)만** — FAIL 아님. ⚠️ verify 는 메타를 **읽기만**, 절대 수선하지 않는다
     (메타 수선은 `scholar-learn` 사람 게이트 몫). 자동수정 금지 원칙과 동일.
7. 최종 판정 출력 (PASS: 전 항목 통과 / FAIL: 실패 항목 수. 메타 WARN 은 FAIL 에 안 들어감).
</Steps>

<Output>
- 항목별 결과표 (컴파일·수치·참조·용어·placeholder·인용 각 PASS/FAIL + 증거, venue 메타 PASS/WARN)
- FAIL 항목 상세: 증거(로그 라인·grep 결과·파일:줄) + fixable_by_llm 분류
- 인용 미검증 목록 (자동수정 없음 — 사람 확인 전용)
- 최종 판정: **PASS** (전 항목 통과) 또는 **FAIL** (N개 항목 실패)
- FAIL 시 다음 단계: fixable=true → scholar-revise, fixable=false → 사람 처리 후 재verify
</Output>
