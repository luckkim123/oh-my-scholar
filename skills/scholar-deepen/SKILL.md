---
name: scholar-deepen
description: |
  research 직후 주장의 *모호성*을 게이트하는 정성 단계 — contribution/method-evidence/comparison/reproducibility가
  명확한가를 차원별로 판정하고, 모호하면 challenge 라운드로 압박한다. 통과(전부 명확 + 사람 승인) 후 ideate.
  수치 가중합·threshold 없는 정성 게이트. 인용 날조 금지, 미검증 인용은 citation-fragile flag.
  Triggers: 주장 명확히, 모호성 점검, deepen, 기여 또렷하게, 무엇을 주장하는지, 깊이 파보자, deepen gate
---

# scholar-deepen — 주장 모호성 게이트 (정성)

<Purpose>
research가 검증된 인용맵을 만든 *직후*, ideate가 개념 SSOT를 굳히기 *전*에, 논문이 **무엇을 주장하는지**가 흔들리지 않는지 게이트한다. 코드 개발의 "요구사항이 모호한 채 설계로 넘어가지 않게 막는" 단계에 해당한다.

deepen이 ideate 앞에 있는 이유: 모호한 주장을 개념노트(.md)로 굳히면 "굳어진 모호함"이 된다. 모호성 해소가 개념 SSOT 확정보다 선행해야 한다. 게이트 3중(deepen/ideate/outline-GATE1)은 각각 다른 것을 검사한다 — deepen=주장 모호성 / ideate=개념 SSOT / outline GATE 1=구조 사람 승인.

이것은 **정성 게이트**다. 모호성을 수치(가중합·threshold·stability_ratio)로 환산하지 않는다 — 논문의 기여가 또렷한지는 magic number로 판정할 수 없고, 정성 판정이 더 정직하다.
</Purpose>

<Use_When>
- research(연구맵·gap·검증 인용)가 끝났고, 개념을 굳히기 전 주장이 또렷한지 점검할 때
- contribution이 여러 개인데 무엇이 핵심인지 흔들릴 때
- "이 논문이 진짜 무엇을 주장하나"가 한 문장으로 안 나올 때
- top-tier 투고처럼 주장의 또렷함이 reject를 가르는 경우
</Use_When>

<Do_Not_Use_When>
- research가 아직 안 됐으면 → scholar-research 먼저 (deepen은 검증 인용맵을 전제)
- 주장이 이미 또렷하고 개념을 .md로 굳힐 단계면 → scholar-ideate
- 구조(섹션·arc)를 잡을 단계면 → scholar-outline
- 사용자가 `--skip-deepen`을 명시했거나 4차원이 자명하게 명확하면 → 통과시키고 ideate로
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **정성 게이트 — 수치화 금지**: 차원별 판정은 "명확 / 모호"의 정성 판정이다. ambiguity score 가중합·threshold·stability_ratio 같은 magic number를 도입하지 않는다.
- ⚠️ **인용 날조 금지 + citation 안전 강화**: challenge 라운드의 어떤 agent도 인용 *내용*을 추측하지 않는다. "researcher 검증 목록 내 인용만 참조"한다. 미검증 인용에 의존하는 주장은 **citation-fragile**로 별도 flag(사람 확인) — 통과 판정에 쓰지 않는다.
- ⚠️ **통과는 사람 승인 필수**: 모든 차원이 "명확"이어도 사람의 명시 승인 없이 ideate로 자동 통과하지 않는다.
- ⚠️ **수식은 영어만** (논문 포맷 규칙 — `references/formats/latex.md` 카드 기준, 도메인 공통). 한국어 설명은 .md 노트 텍스트에만.
- 산출물은 .md (정성 판정 기록) — .tex 직접 생성 금지. research 노트가 trace 역할을 하므로 별도 `.omc/specs` 산출 안 함.
</Execution_Policy>

<Steps>
1. 입력 확인: research 연구맵(gap·검증 인용 목록)과 사용자가 진술한 contribution 확인. 없으면 stop → scholar-research 먼저.

2. **Round 0 — Topology**: 논문의 top-level component를 잠근다 (흔히 3-6개):
   - contributions (주장하는 기여 목록)
   - 핵심 섹션 (method / experiment)
   - 실험 (각 contribution을 뒷받침하는 실증)
   이 topology를 먼저 고정해야 depth-first로 한 갈래만 파다 sibling을 가리는 것을 막는다.

3. **차원별 명확/모호 정성 판정** (4차원, 수치 없음):
   - **Contribution clarity**: 기여가 한 문장으로 또렷한가? 여러 기여가 섞여 무엇이 핵심인지 흐린가?
   - **Method-evidence binding**: 각 방법이 어느 실험·분석으로 뒷받침되는가? 떠 있는 주장은?
   - **Comparison clarity**: 무엇과 비교해 우월한가? baseline이 또렷하고 공정한가?
   - **Reproducibility clarity**: 재현에 필요한 것(데이터·코드·하이퍼파라미터·환경)이 명시될 수 있는가?
   각 차원을 "명확 / 모호"로 판정. ==**'모호' 1개 이상이면 해당 challenge 라운드를 발동**==.

4. **Challenge agents** (모호 차원에 대해, 각 1회 prompt — 위임 또는 직접):
   - **Round 4 Contrarian**: "이 contribution의 반대가 사실이라면? baseline이 이미 충분하다면? 이 기여가 없어도 되는가?"
   - **Round 6 Simplifier**: "기여 3개 중 핵심 1개만 남긴다면? 실험을 절반만 한다면 무엇을 버리나?"
   - **Round 8 Ontologist**: "이 논문이 진짜 *무엇*인가? naming이 흔들리는 entity는? 같은 것을 다르게 부르고 있지 않나?"

5. **Soft limits** (정성이라 hard threshold 대신 soft):
   - round 3에서 4차원 전부 명확이면 early exit 허용.
   - round 10 도달 시 soft warning("모호성이 빨리 안 풀린다 — 주제 자체를 재고할 때").
   - round 20 hard cap (이 이상은 deepen으로 안 풀리는 문제 — 사람에게 에스컬레이션).

6. **citation 안전 점검**: 판정·challenge 과정에서 의존한 인용이 전부 researcher 검증 목록 내인지 확인. 미검증 의존은 citation-fragile flag로 모은다.

7. **통과 판정**: 모든 차원 "명확" → 사람에게 **deepen 통과 승인 요청** (proceed/계속 challenge/abort). 사람 proceed 후에만 ideate handoff.

8. **3-point injection (ideate handoff)**: ideate로 넘길 때 세 가지를 주입한다:
   - enriched initial_idea (deepen으로 또렷해진 기여 진술)
   - research 노트 wrap (검증 인용맵)
   - missing-citation / critical-unknown을 ideate 첫 1-3 라운드의 질문으로
</Steps>

<Output>
Round 0 topology(기여/섹션/실험 잠금) + 4차원 정성 판정표(명확/모호) + 발동된 challenge 라운드 산출 + citation-fragile flag 목록(없으면 "없음") + round 수 + **deepen 통과 승인 요청** (proceed/계속/abort, self-approve 안 함 명시). 통과 시: ideate handoff용 3-point injection 묶음.
</Output>
