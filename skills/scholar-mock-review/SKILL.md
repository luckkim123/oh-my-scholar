---
name: scholar-mock-review
description: |
  내 논문을 target venue reviewer 입장에서 모의 심사 — venue 척도 점수 + 근거-anchor된 강점/약점 +
  venue-native 판정(accept/borderline/reject·letter A~D·minor/major revision)을 낸다.
  앙상블 3렌즈(soundness/novelty/clarity-significance) 병렬 + Area Chair 종합.
  inspect(코치, 판정 금지)·verify(기계 게이트)와 다른 세 번째 축 = 심판(adjudicative).
  읽기전용. citation 안전: anchor 없는 약점 drop, novelty는 retrieval 없으면 질문 강등, injection 방어.
  Triggers: 모의심사, 심사받고 싶어, IROS 기준 리뷰, reviewer처럼 점수, 점수 매겨줘, 내 논문 평가, 리뷰어 입장에서, accept될까, reject 사유
---

# scholar-mock-review — venue-aware 모의 심사

<Purpose>
사용자 *자신의* 논문 draft(.tex)를 target venue의 reviewer처럼 심판한다. scholar-reviewer(읽기전용)를
3렌즈로 병렬 dispatch한 뒤 Area Chair 모드로 종합해, **venue 척도 점수 + 강점/약점 + venue-native
최종 판정**을 반환한다. 코드의 "코드 리뷰"가 아니라 "모의 심사위원" — 저자를 *돕는* 게 아니라 *평가*한다.

⚠️ **모의 심사다.** 실제 peer review를 대체하지 않는다. 문헌 접근 없이 생성된 novelty 판정은 단정이 아닌
질문으로 표기된다.

### 세 리뷰 축의 차이 (oms의 inspect ≠ verify ≠ mock-review)

| 스킬 | 성격 | 출력 | 비유 |
|:---|:---|:---|:---|
| `scholar-verify` | summative 기계 게이트 | 항목별 PASS/FAIL | CI / 린터 |
| `scholar-inspect` | formative 비평 | severity finding (**판정 금지**) | 코드 리뷰 (코치) |
| **`scholar-mock-review`** | **adjudicative 심판** | **venue 점수 + venue-native 판정**(컨퍼런스 accept/reject·letter / 저널 minor·major revision) | **모의 심사위원** |

같은 .tex를 봐도 inspect는 "이걸 고쳐라"(저자 편), mock-review는 "내가 reviewer라면 이 점수, 이 판정"(심판).
</Purpose>

<Use_When>
- 제출 전 "내 논문이 이 venue reviewer에게 어떻게 보일까"를 알고 싶을 때
- venue 척도로 점수를 받고 accept 가능성·reject 사유를 미리 보고 싶을 때
- rebuttal·수정 우선순위를 잡기 위해 reviewer 관점 약점이 필요할 때
</Use_When>

<Do_Not_Use_When>
- 고칠 점을 코치받고 싶으면(판정 말고) → scholar-inspect
- 컴파일·인용·수치 기계 검사 → scholar-verify
- 약점을 바로 .tex에 반영 → scholar-revise (mock-review 약점을 결함목록으로 넘길 수 있음)
- 아직 draft가 없으면 → scholar-draft 먼저
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **읽기전용** — reviewer는 .tex/.bib를 수정하지 않는다. 심판만. 수정은 scholar-revise.
- ⚠️ **3렌즈 병렬 dispatch 안전** — 읽기전용이므로(inspect와 동일). 비용 우려 시 단일 reviewer가 3렌즈
  순차도 허용(기본=병렬 3).
- ⚠️ **self-approval 금지** — drafter와 reviewer는 다른 lane. 자기가 쓴 draft를 자기가 심사하지 않는다.
- ⚠️ **anchor 없는 weakness drop** — 모든 약점은 논문 내 위치 인용 필수. 일반론은 AC re-check에서 제거.
- ⚠️ **novelty 단정 금지** — retrieval 근거 없으면 질문으로 강등. citation-bound 환각 차단.
- ⚠️ **venue 어휘 정합** — 컨퍼런스(IROS/NeurIPS/CVPR)는 accept/borderline/reject 또는 letter,
  저널(RA-L/T-RO)만 minor/major revision. 사용자가 컨퍼런스에 "revision"을 말해도 정정해 안내.
</Execution_Policy>

<Steps>
1. **대상·venue 확인**: 심사할 .tex 경로와 target venue를 확인. venue 미지정이면 `references/venues.md`의
   설정 또는 사용자에게 1회 질문. venue type을 `references/rubrics/venue-review-forms.md`의 Form 1~4에 매핑.
   - ⚠️ 컨퍼런스인데 사용자가 "major/minor revision"을 원하면, 컨퍼런스엔 그 단계가 없음을 알리고
     accept/borderline/reject(+rebuttal) 또는 letter로 안내.
2. **3렌즈 병렬 dispatch** — `Task(subagent_type="oh-my-scholar:scholar-reviewer", mode="lens", ...)` ×3:
   - 입력: .tex 경로, target venue, 배정 렌즈, `venue-review-forms.md`·`paper-eval.md`(mock-review 축).
   - 렌즈: `soundness` / `novelty` / `clarity-significance`.
   - 각 reviewer는 그 렌즈의 strength/weakness(위치 anchor 필수) + 임시 평가를 반환. 최종 판정은 안 냄.
3. **Area Chair 종합** — `Task(subagent_type="oh-my-scholar:scholar-reviewer", mode="area-chair", ...)`:
   - 입력: 3렌즈 산출 + venue form.
   - re-check(anchor 없는 weakness drop·novelty 강등) → venue 척도 per-axis 점수 → accept-bias 캘리브레이션
     → venue-native 최종 판정 → rebuttal/수정 가이드.
4. **종합 보고 출력** (아래 Output) — 면책 포함.
5. "약점을 반영해 고치려면 → scholar-revise, 기계 게이트는 → scholar-verify" 안내.
</Steps>

<Output>
- 축별 평가 (venue 척도 점수 + 근거)
- 강점 / 약점 (각 논문 내 위치 anchor)
- 저자 질문 / rebuttal이 다뤄야 할 것 (우선순위)
- venue-native 최종 판정 (accept/borderline/reject · letter A~D · minor/major revision) + confidence
- 캘리브레이션 노트 (accept-bias 보정 방식)
- ⚠️ "모의 심사 — 실제 peer review 대체 아님" 면책 + novelty 미접근 caveat
- 다음 단계 안내 (revise / verify)
</Output>
