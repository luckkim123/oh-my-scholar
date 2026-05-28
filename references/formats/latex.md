# Format Knowledge Card — LaTeX (.tex)

> oms의 LaTeX 무결성·스타일 SSOT. scholar-verifier(자동 게이트)와 scholar-drafter(작성)가 이 카드를 읽고 동작한다. 중복 임베드 금지 — 항상 이 파일을 참조.

## 1. 컴파일 무결성 검사 (verifier = summative pass/fail)

기계적으로 pass/fail이 나오는 항목. 코드의 CI에 해당.

| 검사 | 방법 | 판정 |
|:---|:---|:---|
| 컴파일 성공 | `latexmk -pdf -interaction=nonstopmode main.tex` (또는 venue compile_engine) | exit 0 = pass |
| undefined references | 로그의 `LaTeX Warning: Reference ... undefined` | 0건 = pass |
| undefined citations | 로그의 `Citation ... undefined` | 0건 = pass |
| overfull hbox | 로그의 `Overfull \hbox` | venue 허용치 이하 = pass |
| 페이지 수 | 컴파일된 PDF 페이지 수 vs venue `page_limit` | 이하 = pass |
| placeholder 잔존 | `\todo`, `[TODO]`, `[FIXME]`, `XXX`, `TBD` grep | 0건 = pass |

컴파일 절차 (다중 패스): `pdflatex → bibtex → pdflatex → pdflatex` 또는 `latexmk`가 자동 처리. 엔진은 venue 카드의 `compile_engine` 따름(pdflatex/xelatex/lualatex).

## 2. 수치·참조 정합 (verifier)

- **본문 수치 ↔ 표/그림 수치 일치**: 본문에서 인용한 수치가 표·그림의 값과 같은가. 불일치 = fail.
- **그림·표 번호 ↔ 본문 참조**: `\ref{fig:x}`/`\ref{tab:y}`가 실제 `\label`과 매칭되는가. dangling ref = fail.
- **용어·약어 일관성**: 같은 개념을 다른 용어로 부르지 않는가. 첫 등장 시 약어 정의됐는가.

## 3. 스타일 규칙 (drafter가 따름 — vault rules-paper-format 흡수)

- **수식 내 텍스트는 영어만**: `\text{Uncertainty Cancellation}` ✓ / `\text{불확실성 상쇄}` ✗
- **수식 번호는 `\tag{}`** 사용 (제목/섹션에 번호 박지 말 것)
- **섹션 모듈화**: `sections/*.tex` 분리, `main.tex`에서 `\input`/`\subfile`
- **인용은 `\cite{key}`**, .bib에서 centralized 관리 (bibtex.md 카드 참조)
- **figure 캡션** non-empty, subfigure 라벨 일관

## 4. 함정

- soffice/libreoffice는 .tex를 렌더 못 함 — 검증은 반드시 LaTeX 엔진으로.
- `~$` 류 임시 파일 아님(LaTeX는 `.aux .log .out .bbl .blg` 부산물) — 검증 시 무시.
- bibtex는 `.bib` 변경 후 재실행 필요 — 한 번의 pdflatex로는 인용 갱신 안 됨.

## 5. citation 안전 (oms 정체성 — bibtex.md와 함께)

verifier가 인용 누락·undefined citation 감지해도 **자동으로 .bib에 추가 금지**. drafter에게 "이 key 검증 필요"만 전달하고, 실제 .bib 수정은 사람 확인 후 drafter가. 인용을 지어내는 것이 가장 위험한 hallucination.
