# Rubric — Paper Evaluation (inspect vs verify vs mock-review 3축 분리)

> oms의 평가 SSOT. paper-write의 평평한 5-reviewer score를 OMC의 inspect(formative)≠verify(summative) 철학으로 재배치하고, 여기에 adjudicative 심판 축(mock-review)을 더한 것. scholar-inspector·scholar-verifier·scholar-reviewer가 이 카드를 읽고 각자의 lane을 안다.

## 핵심 분리 — 코드의 "코드 리뷰 vs CI vs 모의 심사"

| | scholar-inspect (formative) | scholar-verify (summative) | scholar-mock-review (adjudicative) |
|:---|:---|:---|:---|
| **성격** | 비평·조언 (판단형) | pass/fail 게이트 (기계형) | venue 기준 심판 (점수+판정) |
| **코드 비유** | 코드 리뷰 | CI | 모의 심사위원 |
| **입장** | 저자 편 (이걸 고쳐라) | 기계 (통과/실패) | reviewer 편 (내 점수는 이것) |
| **출력** | 개선점 목록 + 심각도 | PASS / FAIL + 증거 | venue 척도 점수 + venue-native 판정(컨퍼런스 accept/reject·letter / 저널 minor·major revision) |
| **agent** | scholar-inspector (opus, read-only) | scholar-verifier (opus, read-only) | scholar-reviewer (opus, read-only, 3렌즈+AC) |
| **자동화** | 사람 판단 보조 | 자동 검사 가능 | 모의 — 실제 심사 대체 아님 |

## verify 축 (summative — 기계적 pass/fail)

코드의 CI처럼 객관적으로 통과/실패가 나온다. (latex.md / bibtex.md 카드의 검사 항목)

| 항목 | 검사 | 카드 |
|:---|:---|:---|
| 컴파일 | latexmk exit 0, undefined ref/cite 0 | latex.md §1 |
| 수치 정합 | 본문 수치 ↔ 표/그림 일치 | latex.md §2 |
| 그림·표 참조 | `\ref` ↔ `\label` 매칭 | latex.md §2 |
| 용어 일관 | 같은 개념 동일 용어, 약어 정의 | latex.md §2 |
| placeholder | TODO/FIXME 잔존 0 | latex.md §1 |
| 인용 정합 | `\cite` ↔ .bib, DOI 실재 | bibtex.md §1·2 |
| 페이지/인용수 | venue page_limit·min_citations | venues.md |

**FAIL이면 무엇이 왜 실패했는지 증거(로그 라인·grep 결과)와 함께.** "should/probably/seems" 금지 — fresh 증거만.

## inspect 축 (formative — 판단형 비평)

코드 CI에 없는 영역. reviewer의 비평이지 통과/실패가 아니다.

| 렌즈 | 본다 | 흡수 출처 |
|:---|:---|:---|
| **logic** | 기여-증거 대응, 구조 논리, 기저선 비교, devil's advocate | paper-logic-reviewer |
| **prose** | 학술 문체(한/영 다름), 과장 규율, 반복, 전환, 문장 길이 | paper-prose-reviewer |

각 finding: severity(critical/important/minor) + location + issue + evidence(.tex 인용) + suggestion + **fixable_by_llm**(텍스트 재구성=true / 실험·그림 누락·기여 범위변경=false).

## mock-review 축 (adjudicative — venue 기준 심판)

inspect가 *저자를 돕는* 코치라면, mock-review는 *저자를 평가하는* 심판이다. reviewer 페르소나로 venue 척도 점수와 venue-native 판정(컨퍼런스 accept/reject·letter / 저널 minor·major revision)을 낸다. 앙상블 3렌즈 병렬 + Area Chair 종합(`scholar-reviewer` agent의 두 mode).

| 렌즈 (mode=lens) | 본다 |
|:---|:---|
| **soundness** | 기술 건전성·정확성·실험 설계·baseline·ablation·재현 정보 |
| **novelty** | 신규성·관련연구 위치·기여 차별성 (⚠️ retrieval 없으면 단정 금지 → 질문 강등) |
| **clarity-significance** | 명료성·구조·의의/영향·재현성 정보 |

Area Chair(mode=area-chair): 3렌즈 종합 → venue form(`venue-review-forms.md`) per-axis 점수 → re-check(anchor 없는 weakness drop·novelty 강등) → accept-bias 캘리브레이션 → venue-native 판정.

venue 척도·판정 어휘는 `venue-review-forms.md`가 SSOT (NeurIPS 1-4/1-10/1-5, CVPR 라벨, IROS letter A~D, 저널 minor/major revision). ⚠️ 컨퍼런스엔 revision 단계 없음 — accept/borderline/reject 또는 letter.

각 strength/weakness: 논문 내 위치 anchor 필수(없으면 drop) + evidence(.tex 인용). 출력 맨 위 "모의 심사 — 실제 peer review 대체 아님" 면책.

## 분리가 중요한 이유

- inspect가 "통과/실패"나 "점수/판정"을 흉내내면 안 됨 — 논리·문체는 본질적 *조언*. 판정은 mock-review.
- verify가 "조언"하면 안 됨 — 게이트는 객관 증거로만.
- mock-review가 "고쳐라"고 하면 안 됨 — 심판은 점수·판정만. 수정은 scholar-revise로.
- **self-approval 금지**: inspect·verify·mock-review 모두 자기가 쓴 draft를 자기가 평가 못 함. drafter와 다른 lane(다른 agent, 읽기전용).
- **citation 안전(mock-review)**: anchor 없는 weakness는 환각 위험이라 drop. novelty 단정은 retrieval 없으면 질문으로 강등 — oms "인용 날조 금지"의 심사 도메인 확장.
