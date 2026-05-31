# Rubric — Venue Review Forms (venue별 심사 양식 SSOT)

> `scholar-mock-review`(모의 심사)의 venue 양식 단일 진실. `scholar-reviewer`(렌즈 평가)와
> Area Chair 메타 패스가 이 카드를 읽고 **해당 venue의 점수 축·척도·판정 어휘**를 안다.
> `paper-eval.md`(inspect/verify/mock-review 3축 분리)와 짝 — paper-eval이 *어느 lane인가*를,
> 이 카드가 *그 venue에서 어떤 양식으로 심판하나*를 정한다.

## 왜 venue마다 다른가

실제 reviewer 양식은 venue마다 점수 축도, 척도도, 판정 어휘도 다르다. "venue 성격에 맞게
리뷰"의 실질은 **이 카드에서 해당 venue form을 골라 그대로 주입**하는 것이다. 하나의 폼을
하드코딩하면 IROS를 NeurIPS처럼 심사하는 오류가 난다.

⚠️ **컨퍼런스 vs 저널 — 판정 어휘가 근본적으로 다르다.**
- **컨퍼런스**(NeurIPS·ICLR·CVPR·IROS·ICRA): accept / borderline / reject (+ rebuttal window).
  **major/minor revision이 없다.**
- **저널**(IEEE T-RO·RA-L 등): minor revision / major revision / reject.

사용자가 컨퍼런스를 두고 "major/minor revision"을 말해도, 컨퍼런스엔 그 단계가 없다 —
letter grade 또는 점수 + accept/reject + "rebuttal이 다뤄야 할 것"으로 변환해 답한다.

---

## Form 1 — NeurIPS / ICLR / ICML (ML 컨퍼런스)

출처: https://neurips.cc/Conferences/2024/ReviewerGuidelines · https://iclr.cc/Conferences/2025/ReviewerGuide

| 축 | 척도 |
|:---|:---|
| Soundness | 1-4 (4 Excellent / 3 Good / 2 Fair / 1 Poor) |
| Presentation | 1-4 |
| Contribution | 1-4 |
| Overall | 1-10 (NeurIPS 연속) — **ICLR은 이산 {1,3,5,6,8,10}** |
| Confidence | 1-5 (5 절대 확신 … 1 추측/전문영역 밖) |

Overall 1-10 의미(NeurIPS): 10 Award quality · 9 Very Strong Accept · 8 Strong Accept ·
7 Accept · 6 Weak Accept · 5 Borderline accept · 4 Borderline reject · 3 Reject ·
2 Strong Reject · 1 Very Strong Reject.

**자유서술 축**: Summary · Strengths · Weaknesses · Questions · Limitations · Ethical concerns.
Strengths/Weaknesses는 originality·quality·clarity·significance 기준으로 평가.

**판정**: Overall 점수 + accept/borderline/reject. revision 단계 없음 → "rebuttal이 다뤄야 할 것".

---

## Form 2 — CVPR / ICCV (비전 컨퍼런스)

출처: https://cvpr.thecvf.com/Conferences/2026/ReviewerGuidelines

| 축 | 척도 |
|:---|:---|
| Overall recommendation | Strong Accept / Weak Accept / Borderline / Weak Reject / Strong Reject |
| Confidence | 1-5 |

평가 항목(**자유서술 기준 — 별도 1-N 점수 축이 아니다**. NeurIPS의 1-4 sub-axis와 달리 CVPR은
이들을 서술로 다루고 점수는 Overall recommendation 라벨 하나로 수렴): **originality/novelty ·
technical quality/soundness · clarity of presentation · significance/impact**.

venue 규범(반드시 반영):
- "이미 했던 것"(novelty 부정)을 주장하려면 **구체적 선행연구를 인용**해야 함.
- **SOTA를 못 이긴 것 자체는 reject 사유 아님.**
- 사소한 수정 가능 결함으로 reject하지 말 것 — novelty·잠재 영향을 성능과 함께 저울질.

⚠️ 라벨(Strong Accept … Strong Reject)은 검증됨. 정수 매핑(5/4/3/2/1 vs 6점 변형)은 **연도별
OpenReview form마다 다름** — 하드코딩 전 해당 연도 form 확인. v1은 라벨만 사용.

---

## Form 3 — IROS / ICRA (로보틱스 컨퍼런스)

출처: https://www.ieee-ras.org/conferences-workshops/financially-co-sponsored/iros/information-for-iros-associate-editors/

⚠️ **NeurIPS/ICLR와 결정적으로 다르다 — multi-axis 숫자 점수가 없다.** 단일 composite letter grade.

⚠️ reviewer는 **letter 하나만 고른다.** 아래 "내부 가중치"는 PaperPlaza가 letter를 집계용 숫자로
환산하는 참조값일 뿐 — reviewer가 per-axis로 직접 기입하는 점수가 아니다(per-axis 숫자 sub-score 없음).

| Letter | 내부 가중치(참조용) | 의미 |
|:---|:---:|:---|
| **A** | 5.0 | Definitely accept (~상위 15%) |
| **B+** | 4.5 | Accept |
| **B** | 4.0 | High borderline |
| **B-** | 3.5 | Borderline |
| **C** | 3.0 | Low borderline |
| **C-** | 2.5 | Reject |
| **D** | 2.0 | Definitely reject |
| **U** | 1.0 | Inappropriate / out of scope |

- 리뷰 관리: **PaperPlaza**. 리뷰 본문은 **≥~1,200 non-whitespace chars** 실질 분량.
- 평가 항목(free-text 안에서): contribution · technical soundness/correctness · novelty/originality ·
  relevance to robotics · clarity/presentation · references.
- double-anonymous.

**판정**: 단일 letter grade(A~D) + 종합 free-text. per-axis 숫자 sub-score 없음, revision 단계 없음.

---

## Form 4 — 저널 (IEEE T-RO · RA-L 등)

출처: IEEE Transactions / RA-L 편집 관례.

| 판정 | 의미 |
|:---|:---|
| Accept | 그대로 게재 |
| **Minor revision** | 작은 수정 후 재검토(보통 재심 없이 AE 확인) |
| **Major revision** | 큰 수정 후 재심사(reviewer에게 다시 감) |
| Reject | 거절 |

**컨퍼런스와의 핵심 차이 = 여기서만 major/minor revision이 있다.** 저자가 "revision 판정"을
원하면 venue가 저널인지 먼저 확인 — 컨퍼런스면 accept/reject + rebuttal로 정정해 안내.

---

## 사용 — reviewer/AC가 venue를 고르는 절차

1. 논문의 target venue 확인(`references/venues.md`의 key 또는 사용자 명시).
2. venue type 매핑: ML 컨퍼런스→Form 1, 비전→Form 2, 로보틱스→Form 3, 저널→Form 4.
   미지 venue면 가장 가까운 form + "이 venue 실제 form 미확인" caveat.
3. 해당 form의 축·척도·판정 어휘를 **그대로** per-axis 평가와 최종 판정에 적용.
4. revision 어휘는 Form 4(저널)에서만. 컨퍼런스는 accept/borderline/reject(+rebuttal).

---

## 출처 완전성 노트

위 척도(NeurIPS 1-10/1-4/1-5, ICLR 이산 집합, IROS A~D letter, CVPR 라벨, 저널 revision 어휘)는
2026-05-31 조사에서 primary source(공식 reviewer guideline 페이지·IEEE RAS·arXiv)로 확인.
CVPR 정수 매핑만 연도별 OpenReview form 의존이라 미고정(라벨만 검증). 조사 종합 보고는
이 카드 신설을 유발한 design 문서(`docs/specs/2026-05-31-scholar-mock-review/design.md`) §2·§4 참조.
