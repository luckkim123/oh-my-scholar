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

## 3. 스타일 규칙 (drafter가 따름 — house paper-format 규약)

- **수식 내 텍스트는 영어만**: `\text{Uncertainty Cancellation}` ✓ / `\text{불확실성 상쇄}` ✗
- **수식 번호는 `\tag{}`** 사용 (제목/섹션에 번호 박지 말 것)
- **섹션 모듈화**: `sections/*.tex` 분리, `main.tex`에서 `\input`/`\subfile`
- **인용은 `\cite{key}`**, .bib에서 centralized 관리 (bibtex.md 카드 참조)
- **figure 캡션** non-empty, subfigure 라벨 일관
- **abstract = 질적 의미만, 정량 수치·수식 금지** (drafter 규칙 + verifier WARN 검출):
  - abstract 영역에는 정량 수치·배수·임계치·인라인 수식을 넣지 않는다. 속도값·성공률·factor(예: `N×`)·임계치(예: `≤ X m`)·`$...$` 수식은 모두 본문 Results 로 미룬다. abstract 에는 질적 표현만('faster'/'robust'/'real-time'/'by an order of magnitude' 등).
  - **왜**: 본문과 중복이고, 맥락(baseline·조건) 없는 수치는 reviewer 의심을 사며, 수식이 평문 흐름을 끊는다. 학술지·Science·학위 공통 강한 관례.
  - **verifier 검출 (WARN, FAIL 아님)** — 이 토큰 목록이 검출의 SSOT(verifier·테스트는 여기를 따른다, 재정의 금지):
    - abstract 영역 추출: `\begin{abstract}`~`\end{abstract}` 환경, 또는 학위논문은 `ABSTRACT` 헤더~다음 `\clearpage`/`\chapter`. ⚠️ **둘 다 없으면 검사 skip(N/A) — 전체 문서 grep 금지** (abstract 못 찾았다고 본문 전체를 긁으면 Results 의 모든 수치가 오검출된다).
    - 주석(`%`로 시작하는 줄)은 출력 안 되므로 검사에서 제외.
    - grep 토큰: 인라인 수식 `$`; 배수 `\times`·유니코드 `×`·`[0-9][0-9.]*\s*\\?times`(escape 유무 무관, "5 times" 류 포함 — WARN 이라 과검출 허용); 부등호 LaTeX `\le`/`\geq` 와 유니코드 글리프 `≤`/`≥`; 수치+단위 `[0-9][0-9.]*\s*~?(m|cm|mm|km|s|ms|Hz|kHz|kg|g|dB|rad|deg|%|MB|GB)\b`(끝 `\b` 가 "6 missions" 류 오검출을 막는 load-bearing); 퍼센트 `[0-9][0-9.]*\s*\\?%`.
    - 1건 이상 = WARN(전체 PASS 막지 않음). 0건 = PASS. ⚠️ 멀티바이트(`×·§·≤`) grep 은 환경(C-locale)에 따라 거짓 0건 가능 — 잔여 0건 확정은 Python `re`로 재확인(`LC_ALL=C grep` 단독 신뢰 금지).
    - ⚠️ WARN 히트는 사람 확인 대상(단위처럼 보이는 영어 단어 `2 m`·`3 s` 같은 드문 오검출이 섞일 수 있음 — WARN 이라 무방).
  - **venue 변주**: 일부 venue 가 abstract 핵심 수치 1개를 허용하므로 강제 FAIL 아님 — 검출만 하고 판정은 사람. (paper-eval.md verify 축 `abstract 규율 (WARN)` 행과 짝.)

## 4. 함정

- soffice/libreoffice는 .tex를 렌더 못 함 — 검증은 반드시 LaTeX 엔진으로.
- `~$` 류 임시 파일 아님(LaTeX는 `.aux .log .out .bbl .blg` 부산물) — 검증 시 무시.
- bibtex는 `.bib` 변경 후 재실행 필요 — 한 번의 pdflatex로는 인용 갱신 안 됨.

## 5. citation 안전 (oms 정체성 — bibtex.md와 함께)

verifier가 인용 누락·undefined citation 감지해도 **자동으로 .bib에 추가 금지**. drafter에게 "이 key 검증 필요"만 전달하고, 실제 .bib 수정은 사람 확인 후 drafter가. 인용을 지어내는 것이 가장 위험한 hallucination.
