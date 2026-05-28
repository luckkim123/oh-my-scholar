# Format Knowledge Card — BibTeX (.bib)

> oms의 인용 무결성 SSOT. scholar-verifier가 검증, scholar-drafter만 수정(사람 확인 후). citation은 oms의 가장 엄격한 가드레일.

## 1. 형식 검사 (verifier = summative)

| 검사 | 방법 | 판정 |
|:---|:---|:---|
| BibTeX 문법 | `bibtex main` 로그 에러 0건 | pass |
| 필수 필드 | entry type별 필수(@article: author/title/journal/year; @inproceedings: author/title/booktitle/year) | 누락 0건 = pass |
| 중복 key | 같은 cite key 2회 정의 | 0건 = pass |
| 본문↔.bib 정합 | `\cite{key}` 전부 .bib에 존재 + .bib 항목 전부 본문서 인용 | dangling/orphan 0건 = pass |

## 2. 인용 검증 (verifier — 단, 자동수정 절대 금지)

- **DOI/존재 검증**: 가능하면 DOI·title을 CrossRef/Semantic Scholar로 조회해 실재 확인. 미발견 = critical 경고.
- **자기인용 비율**: 저자명 제공 시 self-citation ratio 계산, venue `self_citation_max_ratio`(기본 0.20) 초과 = 경고.
- **최소 인용 수**: venue `min_citations` 미만 = 경고.

## 3. ⚠️ citation 자동 수정 금지 (oms 핵심 원칙)

verifier·hook은 **감지·경고만** 한다. 절대 하지 않는 것:
- 누락된 인용을 자동으로 .bib에 추가 (= 인용 날조 위험)
- title/author를 "그럴듯하게" 채움 (= hallucination)
- DOI를 추측해 삽입

대신: "key `foo2024`가 본문엔 있으나 .bib에 없음 — 실제 논문 확인 후 추가 필요" 식으로 **사람에게 넘김**. .bib 수정은 drafter가 사람 확인 후에만.

## 4. 함정

- bibtex는 .bib 변경 후 `bibtex main` 재실행 + pdflatex 2회 — 안 하면 인용 안 갱신.
- key 명명 일관성(예: `author2024keyword`) — 일관 안 하면 관리 지옥.
- accented 문자는 `{\\'e}` 또는 UTF-8(biber/biblatex 쓸 때만) — 엔진 따라 다름.
