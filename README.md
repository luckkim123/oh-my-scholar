# oh-my-scholar (oms)

> Multi-agent orchestration harness for **academic paper writing** — treats writing a paper like writing code, with citation-integrity guardrails.

계보: [`oh-my-claudecode`](https://github.com/) (omc) → `oh-my-docs` (omd) → **`oh-my-scholar` (oms)**

## 철학 — 논문 ≈ 코드

| 코드 | 논문 |
|:---|:---|
| spec / 요구사항 | research question, 기여 정의 |
| 아키텍처 설계 | outline, story arc |
| 함수별 설계도 | 개념 정리 (.md) |
| 함수 구현 | 섹션 초안 (.tex) |
| 코드 리뷰 (formative) | 동료 비평 |
| CI 게이트 (pass/fail) | 인용·수치·컴파일 검사 |
| ralph (테스트 통과까지 루프) | revise 루프 |

두 레이어를 잇는다: **`.md`(개념 SSOT) → `.tex`(논문)**.

## Stage 골격

```
[.md 레이어 — 개념 SSOT]
  scholar-research   RQ·관련연구·gap          (요구사항 수집)
  scholar-ideate     methodology/*.md 개념     (설계도)
  scholar-outline    섹션구조·story arc        (아키텍처)
       ━━━ GATE 1: outline 승인 ━━━
[.tex 레이어 — 논문]
  scholar-draft      .tex 생성 (단일 신중)     (함수 구현)
  scholar-inspect    formative 비평            (코드 리뷰)
  scholar-verify     자동 게이트(cite·수치·컴파일) (CI)
       ━━━ GATE 2: 리뷰 확인 ━━━
  scholar-revise     verify 통과까지 루프       (ralph)
       ━━━ GATE 3: 제출 확인 ━━━
  scholar-pilot      전체 오케스트레이션        (autopilot)
```

## Citation 안전 3원칙 (oms 정체성)

논문은 citation-bound라 hallucination이 컴파일 에러로 안 잡힌다. 그래서:

1. **읽기는 병렬, 생성은 단일** — reviewer/inspector/verifier는 병렬 OK(읽기전용). draft(.tex 생성)는 절대 병렬 금지.
2. **자동 수정 금지** — verifier가 인용 누락 감지해도 자동으로 안 고침. .bib 수정 전 사람 확인.
3. **개념(.md) 선확정** — draft(.tex) 전에 ideate(.md)에서 출처·논리 굳힘.

## Agents

| agent | model | 권한 | 역할 |
|:---|:---|:---|:---|
| scholar-researcher | sonnet | read-only | 관련연구·gap 조사 |
| scholar-planner | opus | read-only | outline·story arc |
| scholar-inspector | opus | read-only | formative 비평 (logic/prose) |
| scholar-verifier | opus | read-only | summative 자동 게이트 |
| scholar-drafter | sonnet | write | 유일한 .tex/.bib 작성 (단일 신중) |

## 라우팅

oms는 **도메인 처리기**(논문 도메인)다. 작업방식 레인(SP/OMC) 판정은 [`oh-my-heroacademia`](https://github.com/)(omha)가 담당하므로 oms는 UserPromptSubmit 라우팅 hook을 두지 않는다. oms의 hook은 PostToolUse citation 검증 리마인더뿐 (자동 수정 안 함).

## Status

초판 구현 중. translate / standardize는 v2 후보.
