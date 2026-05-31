# Plan — `scholar-init` + 전역(상위 `.oms/`) wiki 구현

**Design**: `design.md` (같은 폴더) — 이 plan은 그 design의 실행 단계.
**Status**: DRAFT (사람 승인 후 실행)
**Repo**: `~/oh-my-scholar` (소스 클론, HEAD `c645193`)
**실행 방식**: `superpowers:subagent-driven-development` — task마다 fresh implementer + spec-compliance reviewer + code-quality reviewer.
**Target artifacts** (실제 경로):
- `~/oh-my-scholar/skills/scholar-init/SKILL.md` (신규)
- `~/oh-my-scholar/agents/scholar-inspector.md` (wiki_query 정의 수정 — ascent)
- `~/oh-my-scholar/references/wiki/README.md` (계약에 2계층 명시)
- `~/oh-my-scholar/references/learning-protocol.md` (전역 경계 문서화)
- `~/oh-my-scholar/skills/scholar-pilot/SKILL.md` (init 흡수 + wiki capture 승격 후보)
- `~/oh-my-scholar/skills/scholar-learn/SKILL.md` (상위 `.oms/` 승격 경로)
- `~/oh-my-scholar/hooks/scholar_route_emit.py` (STAGE에 init 추가)
- `~/oh-my-scholar/hooks/oms_atomic.py` (신규 — omp_atomic 이식)
- `~/oh-my-scholar/tests/` (각 task 검증)

---

## 설계 확정 사항 (이 plan이 전제하는 design 결론)

1. **전역 = 상위 폴더 `.oms/`** (ascent, git의 `.git` 찾기 방식, 가장 가까운 하나). 절대경로·환경변수·XDG 0개.
2. **`wiki_query` 추상 함수의 구현만 2계층화** — 호출부(inspector pre-commitment) 불변.
3. **citation/.bib는 전역 승격 영구 금지** (불변 제약). 임베딩 검색 영구 금지.
4. **런타임은 이미 10스킬 최신** — wiki/learn 동작 가능. "0.2.x 업데이트" 선결 불필요(개발 후 marketplace update 위생만).
5. **scholar-init은 독립 스킬**, pilot이 `.oms/<slug>/` 부재 시 흡수.

---

## Phase A — `scholar-init` 스킬 (전역 wiki와 독립; 전역 read는 graceful)

> 전역 wiki 없이도 완결 동작. 전역 read는 "있으면 씨앗, 없으면 skip".

### A1. `oms_atomic.py` 이식 (omp_atomic → oms)
- **무엇**: `omp_atomic.py`(tempfile→fsync→os.replace, stdlib only, `ensure_ascii=False`)를 `~/oh-my-scholar/hooks/oms_atomic.py`로 복사. 함수명·docstring만 oms 맥락으로.
- **왜**: scholar-init이 venue-config(.yaml/.json)·meta를 쓸 때 부분쓰기 손상 방지. (design §3.4)
- **검증 (TDD)**: `tests/test_oms_atomic.py` — (1) 정상 write 후 내용 일치 (2) 한글 보존(`ensure_ascii=False`) (3) tmp 파일 잔재 없음 (4) 기존 파일 atomic 교체. omp의 동등 테스트가 있으면 미러.
- **독립성**: 완전 독립. 다른 task 불요.

### A2. `scholar-init/SKILL.md` 작성 (omp-init 골격 이식 + oms 도메인)
- **무엇**: omp-init의 6-step 골격을 oms로 번안. frontmatter(name/description/triggers) + Purpose/Use_When/Do_Not_Use_When/Execution_Policy/Steps/Output.
- **Steps (design §3.2)**:
  - GATE 0: `<paper>/.oms/<slug>/` 또는 `meta.md` 존재 검사 → 있으면 멈춤+경고+백업 권유.
  - STEP 1: 폴더 위치 (질문 ①, slug 규칙 = output-layout §1.1, 비ASCII→ASCII 1회 질문).
  - STEP 2: venue + 한 줄 주제 + 기여 (질문 ②③). **전역 wiki read** `wiki_query('pattern')`·`wiki_query('convention')`로 추천 (없으면 graceful). 기존 자료위치 기록.
  - STEP 3: scaffold 합성 (read-only dispatch, scholar-planner 또는 신설 역할) → 디렉토리 트리 + venue-config + 논문별 wiki seed **텍스트 반환**(디스크 안 씀). specificity 정직(0.1~0.4).
  - GATE 1 (사람): 폴더·venue·트리·seed·가져온 전역 씨앗 제시. proceed/revise/abort.
  - STEP 4 (게이트 후 write): scaffold 생성(§3.3) + `.oms/<slug>/` + `.oms/wiki/`(빈 4-카테고리) + `meta.md` + venue-config(oms_atomic 경유).
  - STEP 5: 확인 리포트, 1회 종료.
- **도메인 차이 (design §3.5)**: dataset 추적 이식 안 함, organize 안전프로토콜 이식 안 함, specificity 소유단위 = 사용자 venue 습관.
- **검증**: SKILL.md 구조 린트(frontmatter 필수 키, Steps에 GATE 0/1 존재) + scaffold 디렉토리 목록이 design §3.3과 1:1 + "절대경로·~ 하드코딩 0" grep 통과 + citation 안전 문구 존재.
- **의존**: A1(oms_atomic) 완료 후 STEP 4 기술 가능. (SKILL 본문 작성 자체는 병행 가능, write 단계 명세만 A1 참조.)

### A3. routing hook에 `init` STAGE 추가
- **무엇**: `hooks/scholar_route_emit.py`의 STAGE 목록(`research|deepen|ideate|outline|draft|inspect|verify|revise|learn|scholar-pilot`)에 `init` 추가. 안내 문구에 "새 논문 시작·부트스트랩 = init" 한 줄.
- **검증**: `tests/test_scholar_route_emit.py` 확장 — "새 논문 쓸래" 류 입력에서 STAGE 목록에 init이 포함된 안내가 emit되는지. (기존 테스트 회귀 없음 확인.)
- **독립**: A2와 독립(hook은 안내문, 스킬 본문과 분리).

---

## Phase B — 전역(상위 `.oms/`) wiki 계층

> `wiki_query` 구현만 2계층화. 호출부 불변이 핵심 검증 포인트.

### B1. `wiki_query` ascent+병합 구현 명세 (scholar-inspector.md)
- **무엇**: `agents/scholar-inspector.md:53`의 "현재 구현" 서술을 2계층으로 갱신:
  - `local_hits = grep(<cwd>/.oms/wiki/<category>/)`
  - `parent_oms = ascent(cwd, 가장 가까운 상위 .oms/ 제외 self)`; `global_hits = grep(parent_oms/wiki/<category>/) if parent_oms else []`
  - `merge(local, global)`, 출처 태깅 `[wiki:local]`/`[wiki:global]`.
- **불변**: pre-commitment 호출부(`wiki_query(category)` 호출 형태)와 `:105` 출처표시 로직은 *형태* 유지 — `[wiki]` → `[wiki:local]`/`[wiki:global]`로 세분만.
- **검증**: (1) inspector.md에 ascent·2계층·`[wiki:global]` 서술 존재 (2) "임베딩 금지"·"citation 2차메모" 경계 문구 유지 (3) graceful(상위 부재→local만) 명시.
- **의존**: 없음(서술 변경). B2 계약 문서와 페어로 검토.

### B2. `references/wiki/README.md` 계약에 2계층 명시
- **무엇**: §"`wiki_query(category)` 추상 함수 계약"(L63-71)에 ascent 2계층 추가. "미래 교체점"(L70) 옆에 "현재 교체: 상위 `.oms/` ascent 병합". 디렉토리 레이아웃(L17-26)에 "전역 레벨 = 상위 폴더 `.oms/wiki/`(ascent로 발견)" 박스 추가. `history/` 카테고리 신설 여부는 design §6-Q4 따름(잠정: 신설).
- **검증**: README에 2계층·ascent·출처태깅·"전역에도 임베딩 금지" 일관. design §4.2-4.4와 모순 0.
- **의존**: B1과 동일 개념 — 같이 리뷰(spec-compliance reviewer가 inspector.md ↔ README 정합 확인).

### B3. `learning-protocol.md` 전역 경계 + 승격 정책 문서화
- **무엇**: (1) 전역(상위 `.oms/`)에 올라가는 건 재사용 자산만(성향·venue양식·history·재사용결정), 논문 고유·citation은 영구 그 논문 `.oms/`/금지 (design §4.6-4.7). (2) `pattern/`은 영구 light(승격 안 함) 유지. (3) ascent 방식이 "user-scope 금지" 안티패턴과 화해되는 이유 명시.
- **검증**: learning-protocol에 전역 경계 표(§4.6) 반영 + citation 전역승격 금지 불변 + omp의 "never user-scope" 와 모순 없는 설명.
- **의존**: 없음. B1/B2와 개념 정합 리뷰.

### B4. 승격 경로 — scholar-learn이 상위 `.oms/`로 승격
- **무엇**: `scholar-learn/SKILL.md`에 "논문 종료 시 재사용 후보를 사람 승인 후 **상위 `.oms/wiki/`**(전역 레벨)로 승격" 단계 추가. 기존 venue 기본값 승격과 별개 경로. citation 제외 불변.
- **검증**: scholar-learn에 전역 승격 단계 + 사람 게이트 강제 + citation/.bib 제외 명시. 자동 승격 0.
- **의존**: B3(경계 정의) 후.

---

## Phase C — 통합 + 위생

### C1. pilot이 init 흡수
- **무엇**: `scholar-pilot/SKILL.md`에 "`.oms/<slug>/`·meta.md 부재 시 init을 먼저 흡수(또는 권유)한 뒤 research로" 분기 추가. (omp-pilot의 init 흡수 패턴.) design §6-Q5: 자동 진입 vs 권유 — 잠정 "권유 후 진행"(사용자 1회 확인).
- **검증**: pilot에 init-흡수 분기 + 이미 init된 폴더면 skip + 무한 루프 없음.
- **의존**: A2(scholar-init 존재) 후.

### C2. 전체 테스트 + 문서 정합 회귀
- **무엇**: `tests/` 전체 통과 + design↔plan↔구현 1:1 + 옛 표현(절대경로/환경변수/XDG) 잔재 0 grep.
- **검증**: 테스트 스위트 green + grep clean + reviewer 최종 PASS.
- **의존**: A·B·C 전부 후.

### C3. CHANGELOG + 버전 + marketplace update (위생)
- **무엇**: `CHANGELOG.md`에 scholar-init + 전역 wiki 항목(Added/Changed/Verification) + plugin.json 버전 bump. 배포는 `git pull`+marketplace update로 활성 pin을 새 HEAD에 맞춤.
- **검증**: CHANGELOG 4-섹션 + 버전 일관 + (선택) 라이브 설치 후 init STAGE emit 실확인.
- **의존**: C2 후. PR은 사용자 명시 승인 시.

---

## 의존 그래프 (병렬 가능 단위)

```
A1 (oms_atomic) ──┐
A2 (SKILL)    ────┼─→ C1 (pilot 흡수) ─→ C2 (회귀) ─→ C3 (release)
A3 (routing)  ────┘                          ▲
B1 (inspector) ─┐                            │
B2 (README)   ──┼─(개념 정합 리뷰)─→ B4 (learn 승격) ─┘
B3 (protocol) ──┘
```
- **A1·A3·B1·B2·B3은 서로 독립** → 병렬 implementer 가능.
- A2는 A1 참조(write 명세), C1은 A2 의존, B4는 B3 의존.
- 모든 .md/.py는 citation-bound 생성이 아니므로 병렬 OK (논문 본문 생성 아님 — OMC 병렬 금지 대상 아님).

---

## 검증 총괄 (완료 정의)

- [ ] `tests/` 전부 green (oms_atomic, route_emit, 신규 init 린트)
- [ ] `scholar-init/SKILL.md`: GATE 0/1 존재, scaffold = design §3.3, 절대경로 0
- [ ] `wiki_query`: ascent 2계층, 호출부 형태 불변, graceful, 임베딩 금지 유지
- [ ] citation 전역 승격 금지 — 모든 문서 일관
- [ ] design↔plan↔구현 모순 0, 옛 표현 잔재 0
- [ ] (배포) marketplace update 후 init STAGE 실emit 1회 확인

---

## 미해결 (구현 중 사람 확인)

- Q4: `history/` 카테고리 신설 확정? (잠정 신설)
- Q5: pilot init 흡수 = 자동 vs 권유? (잠정 권유)
- Q7: 첫 논문 init 시 상위 `.oms/` 없으면 — 만들지/권유? (잠정: 만들지 않음, "전역 wiki 두려면 상위 폴더에서 init 한 번" 안내)
- 첫 세션 질문 3개 정확한 문구·순서 (잠정: 위치→venue→주제)
