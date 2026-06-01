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

v0.5.0 — 12 skill + 6 agent + reference card(venues·rubrics·formats·learning-protocol·**writing-craft**·wiki) + citation-safe hook(`scholar_route_emit`/`scholar_verify_emit` + `oms_atomic` 원자적 쓰기). 0.5.0 추가: **글쓰기 craft 규칙 주입** — `references/writing-craft.md` 가 4차원(FLOW old→new·TONE 장식어/em-dash·LOGIC one-ping/과대일반화·STRUCTURE CARS Move-2/OCAR) 규칙의 단일 SSOT. drafter 가 prose 전 reasoning skeleton + 반환 전 silent self-audit 으로 *생성 시점에* 규칙을 따르고, planner 는 수사 구조 축(v0.4.0 섹션-순서 모델과 직교)을, verify 는 글쓰기 WARN(≠FAIL)을, inspect 는 reverse-outline + 과대일반화 flag 를 더한다. learn 은 보편 명제를 `venue.prose_defaults` 로 승격(특이 표현은 light wiki). 출처 anchor: Gopen-Swan·Swales CARS·Schimel·Peyton Jones·Nature HB 2025·AutoSurvey. 0.4.0: 논문 구조 모델(공통 골격 + 규모 변주 flat/system/thesis). 0.3.0: **`scholar-mock-review`**(venue reviewer 모의 심사). 0.2.0: `scholar-init`·`scholar-deepen`·`scholar-learn`·전역 wiki 2계층. 구조·hook은 pytest(plugin.json↔skills/ 1:1 강제 포함, **98 passed**)/grep로 검증. **runtime end-to-end는 plugin reload 세션에서 실측 필요.** translate / standardize는 후속 후보. 자세한 내역은 [CHANGELOG](CHANGELOG.md).
