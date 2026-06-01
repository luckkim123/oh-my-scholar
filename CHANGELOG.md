# Changelog

All notable changes to oh-my-scholar (oms).

## [Unreleased]

### Fixed
- **SSOT 읽기 우선순위 강제 (결함 A)** — 사실검증/작성 스킬이 작업 시작 시 1차 SSOT
  (`.oms/<slug>/outline/outline.md` + `methodology/*.md`)를 먼저 읽도록 강제하는 메커니즘이
  없어, 2차 자료(`research_summary/code_survey/*`)부터 읽혀 구조 재설계로 stale된 노트의
  챕터 번호를 현행 구조에 잘못 매핑하는 오판이 가능했다. 처방: `references/learning-protocol.md`
  §8(SSOT reading order — 1차 outline·methodology > 2차 research·code_survey, "부재≠스코프밖"
  + "outline=챕터축 권위" 두 규칙) 신설 + `scholar-inspect` Steps §1 에 SSOT 먼저 읽기 강제
  (inspect 가 .tex 만 읽던 진짜 공백 자리). draft 는 기존 "⚠️ .md SSOT 우선"(L31)이 이미
  충족해 미변경(중복 회피).
- **`.tex`↔`.oms` 동기화 완료조건 명문화 (결함 B)** — `.tex` 구조 변경(절 이동·제목 변경·수식
  교체·\cite 추가) 후 같은 작업 안에서 outline·methodology·결정기록을 갱신하라는 완료조건이
  없어 .oms 가 stale 로 남는 drift 가 발생했다(omp "organize 후 인덱스 sync 완료조건" 동형).
  처방: `scholar-draft`·`scholar-revise` `<Output>` 에 동기화 완료조건(revise 는 결정기록
  `SECTION_REVIEW_DECISIONS`류 포함) + `references/output-layout.md` §6 체크리스트 항목.
  단순 산문 교정(구조 무변경)은 면제. verify 재실행 강제는 과중으로 제외.

### Added
- **회귀 테스트** `tests/test_ssot_priority_and_sync.py` (7건) — 결함 A·B 메커니즘 드리프트 가드
  (learning-protocol §8 존재·읽기순서, inspect SSOT-first, draft·revise 동기화 완료조건,
  output-layout 체크리스트). 96 → 103 passed.

## [0.5.0] — 2026-06-01

### Added
- **글쓰기 craft 규칙 주입 — `references/writing-craft.md` SSOT 신설**. drafter 산출물이 flow·tone·
  logic·structure 네 차원에서 어색했던 근본 원인은 *아키텍처가 아니라 글쓰기 규칙 내용의 부재*
  였다(글쓰기 어휘가 inspector prose lens 한 곳, 그나마 사후 비평 레인뿐 — 생성 시점에 흐름·어투를
  빚을 수단 0). 4차원 규칙을 단일 카드로: §1 FLOW(Gopen-Swan old→new·banana rule)·§2 TONE(장식
  동사·형용사 금지 원리·em-dash 캡)·§3 LOGIC(one-ping·TEEL·과대일반화 경고)·§4 STRUCTURE(CARS
  3-move·OCAR·모래시계)·§5 VOICE(discipline>journal>personal)·§6 EXEMPLAR(~5 무작위 대표,
  embedding 금지)·§7 기계 체크 토큰(verifier WARN SSOT). `latex.md`(조판)와 역할 분리, drafter·
  inspector·verifier 가 *참조*(재나열 금지 — abstract-WARN 선례와 동일 drift 방지). 출처 anchor:
  Gopen & Swan 1990·Swales CARS·Schimel OCAR·Peyton Jones·Nature HB 2025·AutoSurvey·WriteHERE.
- **drafter 생성 흐름 보강 — skeleton 단계 + silent self-audit** (`agents/scholar-drafter.md`).
  Step 4.5: prose 전 문단별 reasoning skeleton `{claim, cite-keys, link}` 산출(CARS Move-2·
  one-ping 점유 확인, `.oms/<slug>/` 작업장에 — inspector reverse-outline 이 재사용). Step 5.5:
  반환 전 §2/§7 기준 silent self-audit(위생이지 게이트 아님 — 자기승인 금지 불위배). citation
  코어 불변(인라인 날조 금지가 skeleton 단계로 확장, 단일 신중 유지).
- **planner 수사 구조 축 — `<Rhetorical_Axis>`** (`agents/scholar-planner.md`). v0.4.0 섹션-순서
  모델(flat/system/thesis)과 *직교*: CARS 3-move(**Move-2 gap 강제** — Intro 가 territory 만
  말하면 reject 1순위)·OCAR 아크·모래시계 폭 일치·아크는 독자 인내심으로 선택(venue 변주). 섹션
  brief 에 "논증할 명제 1개" 필드 추가. researcher gap 진술을 niche move 로 배치(새 생성 아님).
- **verify 글쓰기 WARN** (`agents/scholar-verifier.md` step 9.6 + `references/rubrics/paper-eval.md`).
  writing-craft.md §7 토큰(장식어·em-dash·rule-of-three·부정 병렬)을 기계 검출하되 **WARN(FAIL
  아님)** — abstract-WARN(0.4.x) 선례 그대로(정적 blocklist 부패·과검출 위험으로 강제 FAIL 은
  false-positive). 멀티바이트 em-dash 는 Python `re` 로 확인.
- **inspect 렌즈 보강** (`agents/scholar-inspector.md`). prose lens 를 writing-craft.md §1/§2
  actionable 체크로 업그레이드 + **reverse-outline audit**(topic sentence 추출→논지 연결,
  drafter skeleton 재사용) + logic lens 에 **과대일반화 flag**(인용 근거보다 넓은 주장 = #1 우선,
  최대 실패모드 51% — formative-only, citation-safe 경계로 자동 FAIL 아님, assumption=FRAGILE 형제).
- **learn 이원화 — `venue.prose_defaults`** (`references/learning-protocol.md` enum +
  `references/venues.md` `voice`/`prose_defaults` 필드). 보편 글쓰기 명제(old→new·em-dash 캡)는
  venue-강제 default 로 승격(사람 게이트), user/venue 특이 *표현 선호*는 wiki `pattern/`
  light(advisory). citation/.bib 는 영구 비승격(§6.F) 유지.

### Verification
- 신규 회귀 가드 6 파일 45 tests (writing-craft 카드 7섹션·drafter skeleton/self-audit·planner
  수사 축 직교+v0.4.0 회귀·verify WARN≠FAIL·inspect 렌즈·learn 이원화). 53 → **98 passed**.
- reviewer 2-lane PASS: spec-compliance(6 컴포넌트 전부 COMPLIANT, 불변식·비목표 준수) +
  code-quality(ship-ready, CRITICAL/MAJOR 0, MINOR tautology 1건 반영).

### Notes
- **WARN ≠ FAIL** 근거: 글쓰기 규칙은 정적 blocklist 가 부패하고(저자들이 'delve' 회피 시작)
  문맥상 정당한 사용이 섞여(과검출) 강제 FAIL 은 false-positive — 검출은 WARN/formative 로만.
- **repo/project 경계**: writing-craft.md 는 모든 사용자에게 배포되는 *보편* 규칙. 이 논문/이
  사용자 특이 표현은 per-project `.oms/wiki/pattern/`(light)에만 — 배포 카드에 누출 금지(전 파일
  고유명사 0 가드).
- 설계·계획: `docs/specs/2026-06-01-writing-craft-injection/{design,plan}.md`.
- ⚠️ runtime 반영은 marketplace update + 앱 restart 후(plugin 캐시 reload).

## [0.4.0] — 2026-05-31

### Added
- **논문 구조 모델 — `scholar-planner`에 '공통 골격 + 규모 변주'** (`agents/scholar-planner.md`
  `<Structure_Types>`, `references/venues.md` `structure_type`). 모든 학술 논문이 공유하는 공통
  골격(`Introduction → [Method 단위 1..N: Overview→Proposed→그 단위 실험] → Conclusion`)을
  planner에 명시하고, `structure_type`(`flat` | `system` | `thesis`)으로 그 골격을 *몇 번 반복·
  얼마나 펼치는가*(규모)를 가른다. flat=단편(IROS/RA-L), system=다중 기여 저널 시스템 논문(T-RO),
  thesis=다중 기여 학위논문(하위형 thesis-by-papers vs monograph). venues.md 스키마에 structure_type
  필드 + IROS=flat·POSTECH thesis=thesis 예시. 근거: external-context 문헌조사(IMRaD·Milford·
  Brown H2R·SPJ·IEEE RA-L·T-RO 실측·York/Oxbridge thesis guide — 출처 URL은
  `docs/specs/2026-05-31-paper-structure-model/design.md`).

### Fixed
- **"기술 백서" 안티패턴 차단** — 기존 planner는 flat(단편) 구조 모델만 있어, 학위논문·다중 기여
  시스템 논문을 줘도 방법을 여러 섹션에 나열 + **모든 실험을 끝 한 곳에 몰아넣는** 컨퍼런스식
  평면구조로 outline했다(실사용 ASV-ROV 학위논문에서 발생). 이제 어느 규모에서도 "실험은 그 방법이
  제안된 단위 안에" 두도록 규정. Investigation_Protocol·Success_Criteria 정합 + 회귀 가드
  `tests/test_thesis_structure.py`(6 cases — 공통골격·세 변주·기술백서 안티패턴·monograph/by-papers
  구분·structure_type 필드·범용성 고유명사 0). 39→48 passed.
- **`06_outline.md` 하드코딩 prefix 제거 → `outline.md`** (`skills/scholar-outline/SKILL.md`,
  `agents/scholar-planner.md`, 7곳). 의미 없는 번호(개념노트 `01~06_*.md`와 충돌)였다. plan.md와
  동일하게 번호 없는 파일명으로 통일.

## [0.3.1] — 2026-05-31

### Fixed
- **`.md` 중간산출물 위치 규칙 명문화 — source 폴더 오염 방지** (`references/output-layout.md`,
  `skills/scholar-research|ideate|outline/SKILL.md`). 실사용(석사논문 작업) 중
  research/ideate/outline 의 `.md` 중간산출물(연구맵·개념노트·outline)이 citation-bound
  source 폴더(`paper/…`)에 잘못 생성되는 사고가 있었다. 원인 둘: ① `output-layout.md` 가
  `.tex`/`.bib`/PDF 위치만 규정하고 `.md` 레이어는 **규정하지 않음(공백)**, ②
  `scholar-research`/`scholar-ideate` 본문이 `paper/research`·`paper/methodology` 를
  **예시로 유도** → "source ≠ intermediate" 라는 카드의 source-protection 원칙과 **자기모순**.
  처방:
  - `output-layout.md` §0·§2·§2.1·§6 에 `.md` stage 레이어(`research/ methodology/ outline/`)를
    `.oms/<slug>/` 하위 **고정 경로 SSOT** 로 명시 — 이 노트들은 draft 의 *입력*(비계)이지
    사용자 자산이 아니므로 workbench(`.oms/`)에 두고, source 폴더엔 `.tex`/`.bib` 만 남긴다.
  - `scholar-research`/`scholar-ideate`/`scholar-outline` 본문의 산출물 저장 지시를
    `paper/…` → `.oms/<slug>/{research,methodology,outline}/` 로 정정 (모호했던 "프로젝트 노트
    폴더" 표현 포함).

### Added
- **회귀 가드 테스트** (`tests/test_md_stage_layout.py`, 3 cases). ① `output-layout.md` 가
  `.md` 레이어 3폴더를 SSOT 로 명시하는지(공백 재발 방지), ② `.md`-stage 스킬 본문에
  source-folder 오유도(`paper/research` 등)가 없는지(자기모순 재발 방지), ③ 각 스킬이
  올바른 작업장 경로를 가리키는지 검증. 전체 스위트 39 → 42 passed.

## [0.3.0] — 2026-05-31

### Added
- **`scholar-mock-review` 스킬 — venue-aware 모의 심사** (`skills/scholar-mock-review/SKILL.md`).
  사용자 *자신의* 논문을 target venue reviewer 입장에서 심판한다 — venue 척도 점수 + 근거-anchor된
  강점/약점 + venue-native 판정(accept/borderline/reject · letter A~D · minor/major revision). oms의
  세 번째 평가 축 = **adjudicative 심판**(inspect=코치, verify=기계 게이트와 구분). 같은 .tex를 봐도
  inspect는 "고쳐라"(저자 편), mock-review는 "내가 reviewer라면 이 점수·판정"(심판). 사용자 요청
  "IROS에 낸다면 그 성격에 맞게 점수 매기고 부족한 점·revision 판정"에서 출발.
- **`scholar-reviewer` agent** (`agents/scholar-reviewer.md`, opus, read-only). 두 mode:
  (1) `mode=lens` — soundness/novelty/clarity-significance 한 렌즈로 strength/weakness(위치 anchor 필수)
  평가, (2) `mode=area-chair` — 3렌즈 종합 → venue form per-axis 점수 → re-check → accept-bias
  캘리브레이션 → venue-native 최종 판정. 앙상블 3렌즈 병렬 + AC 메타 패스(읽기전용이라 citation 안전 정합).
- **`references/rubrics/venue-review-forms.md`** — venue별 심사 양식 SSOT. Form 1(NeurIPS/ICLR/ICML
  1-4/1-10/1-5) · Form 2(CVPR/ICCV 라벨) · Form 3(IROS/ICRA letter A~D, multi-axis 숫자 없음) ·
  Form 4(저널 minor/major revision). ⚠️ **컨퍼런스 vs 저널 판정 어휘 분리** — major/minor revision은
  저널만; 컨퍼런스는 accept/borderline/reject(+rebuttal). 모든 척도 primary source(공식 reviewer
  guideline·IEEE RAS·arXiv)로 검증, 출처 URL 명시.

### Changed
- **`references/rubrics/paper-eval.md` 2축 → 3축**: inspect(formative)/verify(summative)에
  mock-review(adjudicative) 축 추가. 핵심 분리 표·"분리가 중요한 이유"를 3축으로 확장(코치 ≠ 기계
  ≠ 심판). mock-review citation 안전(anchor 없는 weakness drop·novelty 질문 강등) 명문화.
- **`references/venues.md`** — venue *제약*(page_limit·sections)과 *심사 양식*(venue-review-forms.md)의
  역할 분리를 상단에 명시.
- **`hooks/scholar_route_emit.py`** — STAGE 카탈로그에 `mock-review` 추가(.tex 레이어, inspect와 다른
  심판 축). `STAGE(paper) → <…|inspect|mock-review|verify|…>` 토큰 줄 갱신. stdlib only·fail-open 유지.
- **`.claude-plugin/plugin.json`** — skills[]에 scholar-mock-review 등록(inspect↔verify 사이).
  `test_plugin_integrity.py`(plugin.json↔skills/ 1:1 강제) 통과.

### Design / Evidence
- 설계 근거: `docs/specs/2026-05-31-scholar-mock-review/design.md`. LLM 논문 리뷰 선행연구 조사
  (MARG arXiv:2401.04259 — 단일 프롬프트 일반론 60%→앙상블 29%; AI-Scientist Nature 2026 — 앙상블+AC
  ~인간 정확도; DeepReview ACL 2025 — re-check 단계; ICLR 2025 20K 실배포 — emit 전 신뢰성 게이트)에
  기반해 아키텍처(앙상블 3렌즈+AC)와 가드레일(anchor 강제·novelty 질문 강등·injection 방어·accept-bias
  캘리브레이션)을 결정. 모든 주장 URL 인용.

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
