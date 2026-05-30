---
name: scholar-pilot
description: |
  논문 전체 파이프라인 오케스트레이션 — research→ideate→outline(GATE1)→draft→inspect→verify
  →revise(GATE2)→제출(GATE3). OMC autopilot의 논문판. citation 안전 3원칙 강제.
  Triggers: 논문 만들어줘, 논문 써줘, 처음부터 끝까지, 논문 파이프라인, paper from scratch,
  write a paper, 논문 자동, 전체 논문 작업, oms pilot
---

# scholar-pilot — 논문 전체 오케스트레이션 (autopilot 논문판)

<Purpose>
research question부터 제출 준비까지 논문 전 단계를 조율한다. OMC autopilot의 논문판이되, citation-bound 안전을 위해 **생성은 단일·읽기는 병렬**로 제한하고 사람 GATE 3개를 끼운다.
</Purpose>

<Use_When>
- "논문 처음부터 끝까지 만들어줘" — 짧은 brief에서 전체 파이프라인
- 어느 단계부터 시작할지 명확하면 그 단계부터 (--from)
</Use_When>

<Do_Not_Use_When>
- 한 단계만 필요하면 → 해당 scholar-* skill 직접
- citation-bound 논문이라 **완전 무인 자동은 금지** — GATE 3개는 사람이 반드시 끊는다
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **citation 안전 3원칙 강제**:
  1. 읽기(research·inspect·verify)는 병렬 OK, **생성(draft)은 단일 신중 절대 병렬 금지**.
  2. verifier가 인용 결함 감지해도 **자동 수정 금지** — 사람 확인.
  3. draft(.tex) 전 ideate(.md)에서 개념·출처 선확정.
- GATE 3개는 사람 결정점 — 자동 통과 금지.
- 각 단계는 전용 skill에 위임 (재구현 금지).
- 단계 산출은 `.oms/state/`에 기록 (OMC state 패턴) — 중단 후 재개 가능.
- **진입 시 priority 컨텍스트 기록 (압축 생존)**: 파이프라인 시작 시 `.oms/notepad.md`의 `## Priority Context` 섹션에 치명 제약을 적는다 — "citation 날조 금지 / draft 병렬 금지 / .bib 수정 전 사람 확인 + 현재 GATE n/3 + 미검증 인용 목록". 긴 파이프라인에서 컨텍스트가 압축돼도 인용 안전 3원칙과 GATE 위치가 항상 복원되도록.
  - **.md가 기본**: 직접 `.oms/notepad.md`에 write/append(원본 notepad가 단일 .md + 섹션 파싱이라 .md 재현 손해 ≈ 0). notepad MCP가 가용하면 `notepad_write_priority(...)`로 미러 가능(같은 .md 대상, 선택 가속) — 부재해도 .md write로 동일 동작, 에러 아님.
- 단계 산출 경로는 **`.oms/state/`** 고정 (검증된 실재 경로; `.oms/specs`·`sessions/{sid}` 같은 미검증 하위 세그먼트는 박지 않는다).
  - ⚠️ **30s 트랩 (향후 state MCP 도입 시에만 — 지금은 미적용)**: state MCP를 쓰게 되면 단계 핸드오프 *직전*에 `state_clear`를 호출하지 말 것(30s간 모든 모드의 stop-hook이 비활성화돼 루프가 조용히 끊긴다). 비종료 핸드오프는 `state_write(active=false)`로, `state_clear`는 *terminal(파이프라인 완전 종료)에서만*. **현재는 state MCP를 실호출하지 않으므로(.md/`.oms/state/` 파일이 기본) 순수 미래 대비 메모.**
</Execution_Policy>

<Steps>
1. **research**: scholar-research → 연구맵·gap·검증된 인용 (.md)
2. **deepen**: scholar-deepen → 주장 모호성 게이트 (정성). research 다음, ideate 앞.
   - fresh subagent dispatch (컨트롤러 컨텍스트 오염 방지).
   - **skip 조건**: deepen 4차원(contribution/method-evidence/comparison/reproducibility)이 자명하게 전부 "명확"이거나, 사용자가 `--skip-deepen`을 명시하면 통과.
   - deepen 통과(사람 승인)는 **GATE 1 전의 내부 승인** — 별도 사용자 게이트를 신설하지 않는다 (deepen 자체의 "사람 승인"으로 충분).
3. **ideate**: scholar-ideate → 개념노트 methodology/*.md (개념 SSOT 확정)
4. **outline**: scholar-outline → 섹션구조·story arc
   - **모드 분기**: Deliberate 트리거(top-tier venue / breaking method 주장 / 비교군 변경)면 `scholar-outline --consensus`(RALPLAN-DR 4-agent 순차), 아니면 `--direct`. 자동 판정 + 사용자 override.
   ━━━ **GATE 1**: outline 승인 (human) — proceed/revise/abort. consensus면 plan.md+outline 둘 다 제시 ━━━
5. **draft**: scholar-draft → .tex (drafter 단일 신중)
6. **inspect**: scholar-inspect → formative 비평 (병렬 OK, 읽기전용)
7. **verify**: scholar-verify → summative 자동 게이트
   ━━━ **GATE 2**: 리뷰 결과 확인 (human) — proceed/another round/address/abort ━━━
8. **revise**: scholar-revise → verify PASS까지 루프 (필요 시)
   ━━━ **GATE 3**: 제출 확인 (human) — confirm/revise/abort ━━━
9. 제출 준비물 정리 (PDF·소스·체크리스트).
10. **wiki capture (자동 특화 — 쓸수록 이 프로젝트에 맞춰짐)**: inspect/verify가 이번 세션에 *발견한* 재사용 가능한 패턴을 **작업 대상 프로젝트의 `.oms/wiki/<category>/*.md`**(plugin이 아니라 프로젝트 작업장; `.oms/`는 gitignore)에 **자동 append**한다 (승인 불필요 — 가벼운 채널). 이것이 다음 세션 inspector의 pre-commitment `wiki_query(category)`가 읽는 데이터 — 쓰기와 읽기가 닫혀 하네스를 쓸수록 이 venue/이 논문 프로젝트에 특화된다. (작업장이라 plugin 배포물·다른 프로젝트를 오염시키지 않고, marketplace update에도 안 날아간다.)
    - **무엇을 적재**: ① venue별 반복 reject 패턴 → `convention/<venue>-reject-patterns.md` ② 이번에 택한 baseline·비교군·구조의 근거 → `decision/<slug>.md` ③ 발견한 외부 자원 포인터 → `reference/*.md`. inspector/verifier가 실제로 본 것만 — 추측 적재 금지.
    - **append 형식**: 기존 .md 끝에 한 줄(또는 짧은 항목) 추가. 같은 패턴이 이미 있으면 중복 안 적음(grep 선확인). 새 category 파일은 자유 형식 .md(머신 스키마 없음).
    - ⚠️ **citation-safe (필수 — 위반 시 OMS 정체성 붕괴)**: wiki는 **2차 메모**만. 인용·주장·수치 *내용*은 절대 적재 안 함(예측을 돕는 reject 사유·양식 규칙만). .bib는 scholar-research 검증 1차 출처로만 갱신 — wiki 발췌를 인용으로 끌어오지 않는다. 적재·조회 모두 **결정론적 텍스트만, 임베딩 금지**. 계약·경계는 `references/wiki/README.md` 참조.
    - **자동이되 비파괴**: append-only(기존 줄 안 지움), 부재 디렉토리는 생성, 적재할 게 없으면 그냥 통과(빈 세션 OK). 사용자가 `--no-wiki`면 skip.
11. **terminal cleanup** (GATE 3 confirm 후, 또는 사용자가 "정리해줘"/"작업 끝" 명시 시):
    - `.oms/<slug>/`의 정리 대상 **집계**(크기·개수): `renders/`·`gen-image/`·`tmp/` 전부 + `versions/`의 최신 1개·사용자 지정 이정표를 **제외한** 구버전. 이정표 선택을 위해 versions 목록을 사용자에게 보여준다.
    - **AskUserQuestion [정리 / 유지]** — 자동 삭제 절대 없음, 기본값 보수적(유지).
    - "정리" 선택 시 → **복구 가능 경로로 삭제**(영구 `rm` 금지): macOS `trash`(없으면 `~/.Trash`) / Linux `gio trash`·`trash-cli` / Windows PowerShell 휴지통 이동(`Shell.Application` ParseName+InvokeVerb('delete'), 영구 `Remove-Item` 금지 — documented, unverified) / 휴지통 없는 환경(CI·컨테이너)은 "영구 삭제" 사용자 재확인 후에만.
    - ⚠️ `outputs/<slug>/<slug>.pdf`(사용자 자산)와 **프로젝트 소스 폴더의 .tex/.bib(citation-bound 자산)**는 집계·삭제 대상에서 **완전 제외** — 언급만. 상세 절차는 `references/output-layout.md` §5.

> **`--from <stage>` 진입점**: 중간 단계부터 시작 가능 — `research|deepen|ideate|outline|draft|inspect|verify|revise`. 예: `--from deepen`이면 기존 research 노트를 입력으로 deepen부터.
</Steps>

<Output>
각 단계 산출물 경로 + GATE 3개 결정 이력 + 최종 PASS 논문 — 사용자가 보는 최종본은 `outputs/<slug>/<slug>.pdf`(컴파일 산출물). .tex/.bib **소스 원본은 프로젝트 소스 폴더에 유지**(citation-bound 자산 보호, `.oms/`로 옮기지 않음); 버전 스냅샷·컴파일 중간물만 `.oms/<slug>/`(`versions/`·`renders/`·`tmp/`). 경로 규약은 `references/output-layout.md`가 SSOT. + 사람 확인 필요 잔여(미검증 인용·fixable=false) + `.oms/state` 진행 기록.
</Output>
