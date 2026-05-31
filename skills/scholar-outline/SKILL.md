---
name: scholar-outline
description: |
  research·ideate 산출물을 받아 논문의 섹션구조·story arc를 설계한다 — scholar-planner에게 단일 위임.
  citation-bound라 인용 의존 매핑은 검증된 researcher 목록에서만. 인용 날조 금지.
  GATE 1(outline 승인 — human) 직전까지가 이 skill의 범위. 자동 통과 없음.
  Triggers: outline 짜줘, 논문 구조, 목차 설계, story arc, 섹션 구성, 아웃라인, 구조 설계, section outline
---

# scholar-outline — 섹션구조·story arc 설계

<Purpose>
research·ideate 단계의 산출물(연구맵, 개념노트 .md)을 받아 논문의 섹션 트리·story arc·word budget·인용 의존 매핑을 설계한다. 코드 개발에서 "아키텍처 설계"에 해당하는 역할이다. scholar-planner(유일한 설계 권한)에게 단일 위임. outline이 확정되면 GATE 1(사람 승인)을 거쳐야만 다음 단계(scholar-draft)로 넘어간다 — 자동 통과는 없다.
</Purpose>

<Use_When>
- research(연구맵·gap 진술)와 ideate(개념노트 .md)가 끝나고 논문 구조를 잡을 때
- 섹션 순서·story arc·word budget을 처음 설계할 때
- 기존 outline을 전면 재구성할 때
</Use_When>

<Do_Not_Use_When>
- 연구·개념이 아직 안 굳었으면 → scholar-research / scholar-ideate 먼저 (개념 선확정 원칙)
- outline이 이미 있고 .tex 본문을 쓸 단계면 → scholar-draft
- 기존 draft의 구조 비평만 원하면 → scholar-inspect
- 논문의 특정 주장이나 계산 검증이면 → scholar-verify
</Do_Not_Use_When>

<Modes>
이 skill은 세 모드로 동작한다 (기본 `--direct`):
- **`--direct`** (기본): 현행 동작 — scholar-planner 단일 위임으로 outline 1개 산출. 빠르고 가볍다.
- **`--consensus`**: planner의 `<Consensus_RALPLAN_DR_Protocol>`을 발동해 story arc Options≥2를 거쳐 최종 1개로 수렴. 4-agent **순차** 파이프라인. `plan.md`(결정 과정) + `outline.md`(결정 결과) 2분리 산출.
- **`--review`**: 기존 outline을 입력받아 검토만 (재설계 아님).

**`--consensus` 자동 발동 (Deliberate 트리거)**: top-tier venue (CVPR/ICLR/NeurIPS/Nature 등) · breaking method 주장 · 비교군(baseline) 변경 중 하나라도 해당하면, `--direct`로 호출됐어도 사용자에게 "이 작업은 consensus 권장 — 진행?"을 1회 제안한다(자동 강제 아님, 사용자 override 가능).
</Modes>

<Execution_Policy>
- ⚠️ **planner는 단일 신중 위임** — 여러 venue·논문도 planner 하나가 처리. 병렬 planner dispatch 금지 (story arc 불일치 증폭).
- ⚠️ **인용 날조 금지** — 각 섹션의 의존 인용은 researcher가 검증한 목록 안에서만. 없는 인용이 필요하면 "researcher 재확인 필요" 표시, 절대 창작하지 않음.
- ⚠️ **GATE 1은 자동 통과 없음** — planner 산출이 아무리 훌륭해도 사람의 proceed/revise/abort 없이는 scholar-draft로 넘기지 않는다.
- outline은 설계 문서다 — 논문 본문 prose를 outline 안에 쓰지 않는다.
- 큰 구조 변경 전 기존 outline 스냅샷.
- ⚠️ **`--consensus` 4-agent는 절대 병렬 금지 — 순차 강제 (3중 문구)**:
  1. (step-level) 각 step 지시에 "이전 step이 끝난 *후에만* 다음 step을 dispatch한다. 두 Task를 같은 병렬 배치로 호출하지 않는다."
  2. (Important 블록) "researcher → planner → [planner 내 architect 책임] → inspector는 MUST 순차다. 각 단계의 Task 결과를 await한 뒤 다음 Task를 발행한다."
  3. (CRITICAL 한 줄) "citation-bound 파이프라인 — 동시 생성은 인용 불일치를 증폭한다. 컨트롤러가 await로만 순차를 보장한다 (런타임 lock 없음)."
  이 3중 문구가 필요한 이유: OMC도 런타임 lock이 없고 컨트롤러의 await로만 순차를 보장하므로(ralplan SKILL "Steps 3 and 4 MUST run sequentially ... Always await" 패턴), 단일 지시로는 병렬 호출을 막지 못한다.
</Execution_Policy>

<Steps>
1. 입력 확인: researcher 연구맵(gap 진술·인용 목록)과 ideate 개념노트(.md) 경로 확인. 없으면 stop → 선행 skill 안내. **모드 판정**: 호출 플래그(`--direct`/`--consensus`/`--review`) 확인. 미지정이면 `--direct`, 단 Deliberate 트리거 해당 시 consensus 1회 제안(`<Modes>`).

### `--direct` 경로 (기본)
2. 작성 대상 venue 확인: `references/venues.md`에서 sections·page_limit·required_sections를 확인. venue 미지정이면 사람에게 확인. **워드 venue(.docx/.hwpx — 예: 학위논문)** 면 GATE 1 통과 후 scholar-draft(.tex) 대신 **OMD `docs-build`로 핸드오프** (outline + 개념노트 .md 를 OMD 에 넘김). 양식 카드(예: postech-thesis-format.md)는 호출자가 OMD 에 함께 전달.
3. `Task(subagent_type="oh-my-scholar:scholar-planner", ...)` 단일 위임:
   - 입력: 연구맵, 개념노트 경로, venue 카드(`references/venues.md`) 참조 지시
   - 지시: 섹션 트리(목적·핵심 메시지·word budget·의존 인용 key) + story arc 필요성 사슬 + word budget 합계 page_limit×500 이내 + 인용은 researcher 검증 목록에서만 + 누락 인용은 "researcher 재확인 필요" 표시
4. planner 산출 받음 — 섹션 트리·story arc·word budget 요약·인용 의존 전체 매핑·미검증 인용 요청 목록.
5. 산출물을 작업장 `.oms/<slug>/outline/outline.md`에 저장 (output-layout.md §2 고정 경로). ⚠️ source 폴더(`paper/…`)에 두지 말 것 — outline은 draft의 *입력*(비계)이지 citation-bound source 자산이 아니다.

### `--consensus` 경로 (4-agent 순차 — 병렬 절대 금지)
> ⚠️ 아래 2c-1~2c-4는 MUST 순차. 각 step의 Task 결과를 await한 뒤 다음 Task를 발행한다. 같은 병렬 배치로 두 Task를 호출하지 않는다. (Execution_Policy 3중 문구)
2c-1. **researcher** (`scholar-researcher`): gap·인용 보강이 필요하면 재호출(이미 충분하면 기존 연구맵 재사용). *이 step이 끝난 후에만* 다음으로.
2c-2. **planner** (`scholar-planner`, `--consensus` 지시): `<Consensus_RALPLAN_DR_Protocol>` 발동 — Principles + Drivers + story arc Options≥2 + steelman + tradeoff + ADR + (Deliberate면) pre-mortem. *2c-1 결과를 입력으로*. 산출 = `plan.md`(결정 과정) + 섹션 트리.
2c-3. **[planner 내 architect 책임]**: 별도 agent 아님 — planner가 2c-2에서 steelman/antithesis로 이미 수행(T1 경계 규약: architect agent 신설 안 함). 외부 자문이 *정말* 필요하면 inspector의 `<External_Consultation>` 경로로만.
2c-4. **inspector** (`scholar-inspector`): 2c-2의 plan.md+outline을 formative 비평(critic 4기법). PASS/FAIL 안 냄 — 개선점만. *2c-2 결과를 입력으로*.
2c-5. **재리뷰 loop**: inspector가 critical/important를 내면 planner 재위임(2c-2로) 후 재비평. **최대 = venue.max_review_rounds (venues.md에 키 없으면 기본 5)**. 5회 도달 시 best version + "consensus not reached — N rounds, 잔여 finding 목록" 명시하고 GATE 1로.
2c-6. **2분리 저장**: `plan.md`(RALPLAN-DR+ADR, 결정 과정) + `outline.md`(Final 단일 arc 섹션 트리, 결정 결과). 둘 다 작업장 `.oms/<slug>/outline/` (output-layout.md §2). ⚠️ source 폴더(`paper/…`) 금지.

### 공통 — GATE 1
> ⚠️ `--consensus`의 2c-* 순차 stage 간 전달은 아래 `<Consensus_Handoff>` 규약을 따른다 (rubber-stamp 방지).
6. **GATE 1 — 사람 승인 요청**:
   - outline 전문(consensus면 plan.md+outline 둘 다)을 제시하고 다음 세 가지 선택지를 명시한다:
     - **proceed**: outline 승인 → scholar-draft로 진행 가능
     - **revise**: 수정 사항 지시 → planner 재위임 후 GATE 1 재실행
     - **abort**: 이 outline 폐기 → 선행 단계(research/ideate)로 복귀
   - 사람의 명시적 응답 전까지 scholar-draft 진행 금지.
</Steps>

<Output>
planner가 설계한 outline(섹션 트리·story arc·word budget 요약·인용 의존 매핑) + `outline.md` 저장 위치 + 미검증 인용 요청 목록(없으면 "없음") + **GATE 1 승인 요청** (proceed / revise / abort 선택 안내, self-approve 안 함 명시).

**`--consensus` 모드일 때 추가**: `plan.md`(RALPLAN-DR+ADR — 결정 과정) 저장 위치 + 재리뷰 회차(N/5) + consensus 도달 여부("도달" 또는 "not reached — 잔여 finding 목록"). plan.md와 outline.md는 *분리된 두 파일*이다 (결정 과정 ≠ 결정 결과).
</Output>

<Consensus_Handoff>
> `--consensus` 4-agent의 stage 간 전달 규약 (docs-plan과 동형). **기본(SSOT) = .md 파일**, MCP는 *있으면 쓰는* 선택 가속 (결정1=C: OMS는 MCP 0건/standalone이 정체성).

**기본 경로 (.md — MCP 없이 동작)**:
- 각 consensus stage의 *구조화 산출*(planner의 steelman/antithesis/tradeoff/ADR, inspector의 finding 등)을 작업장 `.oms/<slug>/consensus/<stage>-<role>.md`로 쓴다. 예: `consensus/planner-adr.md`, `consensus/inspector-findings.md`. 각 파일은 구조화 헤더(role / stage / 작성 시점) + 본문.
- **rubber-stamp 방지 (기계적)**: 다음 stage는 *이전 role의 .md 파일이 디스크에 존재하는지 확인*한 뒤에만 진행한다. 부재면 진행 거부("이전 stage 산출 없음 — 순차 위반"). 디렉토리 격리 = namespace 대체. consensus는 순차라 동시쓰기 race 없음, 한 디렉토리로 충분.
- `<slug>`·경로는 **작업 루트 상대** (호출자 cwd / 명시 프로젝트 루트 기준) — 특정 사용자 절대경로 금지.

**선택(가속) MCP**: config gate `agents.sharedMemory.enabled`가 켜져 있고 shared_memory MCP가 *가용*하면 동일 데이터를 `shared_memory_write(namespace="paper-consensus", key="<stage>-<role>", value={...})`로 미러 가능(정밀 key 조회·TTL 자동). ⚠️ **.md가 SSOT, MCP는 가속일 뿐** — MCP 부재 시 에러 아니라 .md 경로로 graceful degrade, 동일 보장.

**혼용 명확**: researcher 연구맵 등 *비구조 산출*은 기존 .md 방식 그대로 (handoff 규약은 *구조화 consensus 산출에만* 적용). consensus/ 디렉토리는 작업장 — 종료 시 T18 정리 대상.
</Consensus_Handoff>
