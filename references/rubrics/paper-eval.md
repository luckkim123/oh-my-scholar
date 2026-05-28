# Rubric — Paper Evaluation (inspect vs verify 2축 분리)

> oms의 평가 SSOT. paper-write의 평평한 5-reviewer score를 OMC의 inspect(formative)≠verify(summative) 철학으로 재배치한 것. scholar-inspector와 scholar-verifier가 이 카드를 읽고 각자의 lane을 안다.

## 핵심 분리 — 코드의 "코드 리뷰 vs CI"

| | scholar-inspect (formative) | scholar-verify (summative) |
|:---|:---|:---|
| **성격** | 비평·조언 (판단형) | pass/fail 게이트 (기계형) |
| **코드 비유** | 코드 리뷰 | CI |
| **출력** | 개선점 목록 + 심각도 | PASS / FAIL + 증거 |
| **agent** | scholar-inspector (opus, read-only) | scholar-verifier (opus, read-only) |
| **자동화** | 사람 판단 보조 | 자동 검사 가능 |

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

## 분리가 중요한 이유

- inspect가 "통과/실패"를 흉내내면 안 됨 — 논리·문체는 본질적으로 판단. 사람이 결정.
- verify가 "조언"하면 안 됨 — 게이트는 객관 증거로만.
- **self-approval 금지**: inspect도 verify도 자기가 쓴 draft를 자기가 승인 못 함. drafter와 다른 lane(다른 agent, 읽기전용).
