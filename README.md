# oh-my-scholar (oms)

> Multi-agent orchestration harness for **academic paper writing** — treats writing a paper like writing code, with citation-integrity guardrails.

계보: [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode) (omc) → `oh-my-docs` (omd) → **`oh-my-scholar` (oms)**

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
[0단계 — 부트스트랩]
  scholar-init       폴더·venue·주제 → 디렉토리 scaffold + .oms/ 작업장  (research /init)
       ━━━ GATE 0: scaffold 승인 (멱등 — 이미 .oms/<slug>/ 있으면 skip) ━━━
[.md 레이어 — 개념 SSOT]
  scholar-research   RQ·관련연구·gap          (요구사항 수집)
  scholar-deepen     주장 모호성 게이트(정성)   (스펙 명료화)
  scholar-ideate     methodology/*.md 개념     (설계도)
  scholar-outline    섹션구조·story arc        (아키텍처)
       ━━━ GATE 1: outline 승인 ━━━
[.tex 레이어 — 논문]
  scholar-draft       .tex 생성 (단일 신중)        (함수 구현)
  scholar-inspect     formative 비평·코치          (코드 리뷰)
  scholar-mock-review venue reviewer 입장 심판      (모의 심사위원)
                      점수+venue-native 판정
                      (컨퍼런스 accept/reject·letter / 저널 revision)
  scholar-verify      자동 게이트(cite·수치·컴파일)  (CI)
       ━━━ GATE 2: 리뷰 확인 ━━━
  scholar-revise     verify 통과까지 루프       (ralph)
       ━━━ GATE 3: 제출 확인 ━━━
  scholar-pilot      전체 오케스트레이션        (autopilot)
[메타 — 진화]
  scholar-learn      관찰 → venue 기본값 승격 (사람 게이트) — 쓸수록 이 사용자 특화
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
| scholar-inspector | opus | read-only | formative 비평 (logic/prose) — 코치 |
| scholar-reviewer | opus | read-only | adjudicative 심판 (3렌즈+AC, venue 점수·판정) |
| scholar-verifier | opus | read-only | summative 자동 게이트 |
| scholar-drafter | sonnet | write | 유일한 .tex/.bib 작성 (단일 신중) |

## 라우팅

oms는 **도메인 처리기**(논문 도메인)다. 작업방식 레인(SP/OMC) 판정은 [`oh-my-heroacademia`](https://github.com/luckkim123/oh-my-heroacademia)(omha)가 담당한다 — oms는 레인을 정하지 않는다. 대신 omha가 레인을 잡아준 뒤, oms의 UserPromptSubmit hook(`scholar_route_emit.py`)이 논문 도메인 안에서 어느 **STAGE**(research/draft/verify…)인지를 매 턴 `STAGE(paper) → …` 한 줄로 선언한다. PostToolUse hook(`scholar_verify_emit.py`)은 .tex/.bib 편집 후 citation 검증 리마인더를 주입한다 (자동 수정 안 함).

## Status

v0.3.0 — 12 skill + 6 agent + reference card(venues·rubrics·formats·learning-protocol·wiki) + citation-safe hook(`scholar_route_emit`/`scholar_verify_emit` + `oms_atomic` 원자적 쓰기). 0.3.0 추가: **`scholar-mock-review`** — venue reviewer 입장 모의 심사(앙상블 3렌즈+Area Chair, venue 척도 점수 + venue-native 판정 — 컨퍼런스 accept/reject·letter / 저널 minor·major revision). inspect(코치)·verify(기계)와 구분되는 세 번째 *심판* 축. venue 양식 SSOT `venue-review-forms.md`(IROS letter A~D / NeurIPS 1-4·1-10 / 저널 minor·major revision), 가드레일은 LLM 리뷰 선행연구 근거(anchor 없는 weakness drop·novelty 질문 강등·injection 방어·accept-bias 캘리브레이션). 0.2.0 추가: `scholar-init` 0단계 부트스트랩, `scholar-deepen`, `scholar-learn`, 전역 wiki 2계층. 구조·hook은 pytest(plugin.json↔skills/ 1:1 강제 포함, 39 passed)/grep로 검증. **runtime end-to-end는 plugin reload 세션에서 실측 필요.** translate / standardize는 후속 후보. 자세한 내역은 [CHANGELOG](CHANGELOG.md).
