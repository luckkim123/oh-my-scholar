# Changelog

All notable changes to oh-my-scholar (oms).

## [Unreleased]

## [0.2.0] — 2026-05-31

### Added
- **`scholar-init` 스킬 — 새 논문 0단계 부트스트랩** (`skills/scholar-init/SKILL.md`). 형제
  `omp-init`의 검증된 부트스트랩 패턴(GATE 0 멱등성 → read-only 진단 → 사람 게이트 GATE 1 →
  write)을 논문 도메인으로 이식. 첫 세션에 ≤3개만 묻고(폴더 위치·venue·한 줄 주제, progressive
  disclosure) 표준 디렉토리 scaffold(`sections/`·`figures/`·`refs/`·`data/`·`preamble.tex`·
  `meta.md`) + `.oms/<slug>/` 작업장 + 논문별 `.oms/wiki/`를 생성. 시작 시 **상위 폴더의
  `.oms/wiki/`(전역 레벨, ascent로 발견)**를 씨앗으로 참조해 "당신이 보통 쓰는 venue·구조"를
  추천 — 쓸수록 다음 논문 시작이 빨라진다. scaffold만 — 본문·인용 생성 0(citation 안전).
- **전역 wiki 2계층 (상위 폴더 `.oms/` = 전역, 이 논문 `.oms/` = 로컬)**. `wiki_query` 추상
  함수의 *구현만* 2계층 ascent 병합으로 교체(`agents/scholar-inspector.md`) — git의 `.git`
  찾기처럼 가장 가까운 상위 `.oms/`를 전역으로 삼아 로컬과 병합, 출처를 `[wiki:local]`/
  `[wiki:global]`로 태깅. **호출부 불변** — ascent·병합은 전부 구현 안에 갇힘. 절대경로·
  환경변수·XDG 0개(work-root 상대, 배포물 오염 없음). 전역엔 재사용 자산만 승급(성향·venue
  양식·재사용 결정·`history/`); 논문 고유·**citation/.bib는 전역 승급 영구 금지**(§6.F).
- **`hooks/oms_atomic.py`** — atomic JSON write(tempfile→fsync→os.replace, stdlib only,
  cross-platform, `ensure_ascii=False`). omp_atomic 패턴 이식, scholar-init의 상태 파일 쓰기용.
- **`tests/test_plugin_integrity.py`** — plugin.json `skills` 필드 == 실제 `skills/` 디렉토리
  1:1 강제(드리프트 방지). 이 과정에서 한때 미등록이던 `scholar-deepen`·`scholar-learn`도 함께
  등록 보정(scholar-init 포함 11개 전부 등록).

### Changed
- **라우팅 hook에 `init` STAGE 추가** (`hooks/scholar_route_emit.py`): 0단계 부트스트랩 안내 +
  `STAGE(paper) → <init|research|…|scholar-pilot>` 토큰 줄에 init 추가. "이미 .oms/<slug>/
  있으면 init 아님" 멱등 단서 포함.
- **`scholar-pilot` Step 0 — init 흡수(권유)**: `.oms/<slug>/` 부재 시 research 전에
  scholar-init을 권유(자동 진입 아님 — 사용자 모르게 폴더 안 만듦). 이미 있으면 skip(멱등).
  Step 10 wiki capture에 전역 승급 후보 hint 추가(terminal에서만, citation 제외).
- **`scholar-learn` 로컬→전역 wiki 승급 경로** 추가 — light 자산(성향·양식·재사용 결정·history)을
  사람 게이트 후 상위 `.oms/wiki/`로 올리는 별도 lane(venue 기본값 승격과 구분, citation 제외).
- **`references/wiki/README.md`·`learning-protocol.md` §1.4** — 2계층 ascent 계약·전역 경계
  표(무엇이 전역에 갈 자격이 있나)·"user-scope 금지 안티패턴과 화해"를 명문화.
- **`references/omc-backport-analysis.md` §4 신설 — omp 0.2.0 역방향 backport 검토(채택 0).**
  형제 omp 가 0.2.0 에 추가한 5종(content_conventions·content audit·dead-link·CONVENTIONS.md·
  specificity content 항)을 oms 로 역방향 backport 할지 적대 검증 → 전부 REJECT. oms 는 생성
  파이프라인이라 rules.json 정규식 audit 루프 전제가 부재하고, prose 품질은 inspect/verify rubric 이
  이미 담당(citation-bound 는 패턴 아닌 의미가 정확성을 좌우). "역방향 채택 0" 을 영속 기록해 재검토
  반복 방지. 코드 변경 0 — 문서만.
- **라우팅 hook 계약 확장** (`hooks/scholar_route_emit.py`, UserPromptSubmit): STAGE 카탈로그에
  `deepen` 토큰 추가 — `scholar-deepen` 스킬(research↔ideate 사이 주장 모호성 게이트)이 신설돼
  단계 목록과 `STAGE(paper) →` 라인 양쪽에 반영
  (`research|deepen|ideate|outline|draft|inspect|verify|revise|scholar-pilot`). stdlib only·
  fail-open 패턴 유지. (omd `route_emit.py`의 `revise` 토큰 추가와 대칭 — hook 은 계약이라 양쪽
  변경을 명문 기록.)
- 라우팅 hook 테스트(`tests/test_scholar_route_emit.py`): 단계 열거 검증을 8→9개로 갱신
  (`deepen` 포함). 기존 7건 + verify 7건 = 14 passed 유지.

### Verification
- `pytest tests/` — **39 passed** (oms_atomic 7 + route 11 + verify 7 + scholar-init 린트 11 +
  plugin-integrity 4 — 일부 기존 테스트 포함). scholar-init·전역 wiki·hook 변경 후 회귀 0.
- 독립 reviewer 2-lane(spec-compliance + code-quality) 통과 — must-fix 2건(plugin-integrity
  파서 `Path(s).name`化, oms_atomic mkstemp-unbound 가드) + 문서 명확성 1건(`history/` 전역
  전용 명시) 반영 후 재검증.
- plugin.json `skills` ↔ 실제 `skills/` 디렉토리 11:11 정합(integrity 테스트 강제).
- 옛 표현(절대경로·환경변수·XDG) 잔재 grep clean(부정 서술 "no env var, no XDG" 제외).
- 두 hook 실행 시 valid JSON emit (`init` 토큰 포함 확인).

## [0.1.1] — 2026-05-28

### Added
- **STAGE 라우팅 hook** (`scholar_route_emit.py`, UserPromptSubmit): omha가 레인을 잡아준 뒤, 논문 도메인 안에서 매 턴 `STAGE(paper) → <research|…|scholar-pilot> · 근거` 한 줄로 단계를 선언한다. omha의 `ROUTE →`, omd의 `STAGE(docs) →`와 톤 통일(이모지 없이 텍스트 레이블). plugin.json에 UserPromptSubmit 등록.
- 라우팅 hook 테스트 7건 (`test_scholar_route_emit.py`): contract 명시·8단계 열거·citation 안전 문구·레이블 충돌 없음·stdlib only·fail-open.

### Changed
- README 라우팅 섹션: "oms는 라우팅 hook을 두지 않는다" → STAGE hook을 둔다로 정정 (레인은 여전히 omha 담당, oms는 STAGE만).

### Verification
- `pytest tests/` — 14 passed (verify 7 + route 7).
- **runtime end-to-end 검증 완료**: scholar-verify를 실제 .tex/.bib(결함 5개 심음)에 돌려 5개 전부 적발, citation 자동수정 안 함(사람 확인 목록), inspect/verify 경계 준수 확인. (v0.1.0의 "runtime 미검증" 백로그 해소.)

## [0.1.0] — 2026-05-28

초판. 논문 작성을 "코드 작성처럼" 다루는 Claude Code plugin 하네스.

### Added
- **8 stage skills** (단일 SKILL.md, OMD 방식): `scholar-research`, `scholar-ideate`, `scholar-outline` (.md 레이어) → `scholar-draft`, `scholar-inspect`, `scholar-verify`, `scholar-revise` (.tex 레이어) → `scholar-pilot` (전체 오케스트레이션). 각 skill은 Triggers 키워드 + `Task(subagent_type="oh-my-scholar:scholar-*")` dispatch.
- **5 agents** (OMC 11섹션 `<Agent_Prompt>` XML):
  - `scholar-researcher` (sonnet, read-only) — 관련연구·gap·인용 검증
  - `scholar-planner` (opus, read-only) — outline·story arc
  - `scholar-inspector` (opus, read-only) — formative 비평 (logic/prose), pass/fail 아님
  - `scholar-verifier` (opus, read-only) — summative 자동 게이트, 3중 self-approval 금지
  - `scholar-drafter` (sonnet, write) — 유일한 .tex/.bib 작성, 단일 신중, 인용 날조 금지
- **4 reference cards** (가드레일 SSOT): `formats/latex.md`, `formats/bibtex.md`, `rubrics/paper-eval.md` (inspect/verify 2축 분리), `venues.md`.
- **citation-safe PostToolUse hook** (`scholar_verify_emit.py`): .tex/.bib 편집 시 인용 검증 리마인더 주입. OMC post-tool-verifier의 citation-safe 변형 — 자동 수정 지시 안 함.

### Notes — 설계 정체성
- **citation 안전 3원칙**: ①읽기 병렬/생성 단일 ②자동 수정 금지(.bib는 사람 확인) ③개념(.md) 선확정. 논문은 hallucination이 컴파일 에러로 안 잡혀, OMC의 자동 throughput을 *내용 생성*엔 쓰지 않는다.
- **reviewer 고도화**: paper-write의 평평한 5-reviewer score를 OMC inspect(formative)≠verify(summative) 2층으로 재배치. figure/citation/latex-lint는 별도 agent 아닌 verifier 내부 검사로 흡수 → 5 reviewer를 4 agent로 압축.
- **OMC 패턴 이식**: ralph PRD `passes:true` 게이트(scholar-revise), `<External_Consultation>`(OMD가 빠뜨린 것), 3중 self-approval, GATE 3개(human).
- **라우팅 비종속**: oms는 도메인 처리기. 작업방식 레인 판정은 omha(oh-my-heroacademia)가 담당 → oms는 UserPromptSubmit 라우팅 hook 없음.

### Verification
- `pytest tests/` — 7 passed (hook: .tex/.bib 감지·비논문 침묵·자동수정금지·stdlib only·fail-open).
- agent 5개: 11섹션 XML, 읽기전용 4개 disallowedTools, verifier 3중 self-approval, drafter만 write, 전부 External_Consultation (grep 검증).
- skill 8개: Triggers + dispatch + plugin.json skills 배열 정합 (8 exact match).

### Backlog
- v2 후보: `scholar-translate` (한→영), `scholar-standardize` (기존 논문서 스타일 귀납).
- OMD backport (별도 세션): #1 External_Consultation, #2 ralph PRD 게이트, #3 3중 self-approval, #4 PostToolUse 무결성 hook.
- runtime end-to-end 검증: 새 세션 로드 후 scholar-pilot 실측 (구조·hook만 검증됨, 실제 동작 미검증).

[0.1.0]: 신규
