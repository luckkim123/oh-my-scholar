# Design — `scholar-init` (논문 부트스트랩 진입점) + 전역 wiki (사용자 누적 자산 2계층)

**Status**: DRAFT (설계 단계 — 구현 전 사람 승인 대기)
**Date**: 2026-05-31
**Author**: oms 사용자(luckkim123) + Claude 설계 세션
**Target harness**: oh-my-scholar (oms)
**Related**: `references/wiki/README.md`, `references/output-layout.md`, `references/learning-protocol.md`, `references/venues.md`, 형제 `oh-my-project/skills/omp-init`

---

## 0. 한 줄 요약

논문 작업의 **0단계(부트스트랩)**가 oms에 통째로 비어 있다. 새 논문을 시작할 때 폴더 위치·venue·주제를 사용자와 대화로 잡고, 표준 디렉토리를 깔고, 논문별 wiki를 초기화하는 진입 스킬 **`scholar-init`**을 신설한다. 동시에, 사용자가 *모든 논문에 걸쳐* 재사용하는 자산(즐겨 쓰는 표현·구조·venue별 양식·논문 history·성향)을 담는 **전역 wiki**를 도입해, `scholar-init`이 새 논문을 빈 손이 아니라 "당신은 보통 이렇게 쓰죠"라는 씨앗에서 시작하게 한다.

핵심 두 산출물:
1. **`scholar-init`** — 형제 `omp-init`의 검증된 부트스트랩 패턴을 oms 도메인에 이식한 1회성 진입 스킬.
2. **전역 wiki (상위 폴더 `.oms/` 계층)** — 머신 전역도 별도 자산 폴더도 아닌, **부모 폴더의 `.oms/wiki/`**다(`.omp`·`.omc`처럼 cwd 상대, 절대경로 0개). git의 `.git` 찾기처럼 ascent로 가장 가까운 상위 `.oms/`를 전역으로 삼는다. `wiki_query` 추상 함수의 구현만 교체해 호출부 불변.

---

## 1. 문제 정의 — 왜 필요한가

### 1.1 증거 (이 세션 조사 결과)

- **oms 8(→10)스킬 어디에도 "0단계"가 없다.** `scholar-pilot`은 폴더 생성·venue 결정·주제 인터뷰를 전부 건너뛰고 곧장 `research`로 진입한다 (`skills/scholar-pilot/SKILL.md` Steps). 산출물 경로조차 "호출자가 결정"하도록 떠넘겨져 있다 (`scholar-research` SKILL).
- **형제 `omp`엔 `omp-init`이 있다** — 1회 부트스트랩(스캔→프리셋 매칭→사람 게이트→`.omp/` SSOT 생성). oms엔 그 대응물이 없다. omd엔 `docs-intake`(Socratic 의중 파악)가 있으나 oms엔 없다.
- **누적 자산은 전부 그 논문 폴더에 갇혀 있다.** `.oms/wiki/`는 *그 논문* cwd의 `.oms/`만 읽는다 — 상위 폴더로 올라가 보지 않는다. → "내 모든 논문 공통 자산"을 둘 자리가 **아직 없다**. (단 oms·omp 설계가 *"user-scope/distributed config에 절대 쓰지 마라"*를 안티패턴으로 명시했으므로 — `learning-protocol.md` — 해법은 절대경로·환경변수가 아니라 **상위 폴더 `.oms/` ascent**여야 한다. §4 참조.)

### 1.2 외부 실무와의 대조 (웹 조사)

- 상용 도구(Jenni·Paperpal·SciSpace)는 죄다 "프로젝트 scaffold/세팅 단계"를 비워둔다 — 초안·문헌수집만 한다. 이 빈틈이 `scholar-init`의 niche.
- **AI Scientist (Sakana AI)**는 정확히 "style file + section header를 담은 LaTeX template folder"로 부트스트랩하고 아이디어를 누적 archive에 쌓는다 — 사용자 직감의 직접 선례.
- **user-global ↔ per-paper 2계층**은 LaTeX 실무 표준: 개인 매크로·preamble·`.bib`는 `~/texmf/`에 두고 모든 논문이 `\include`, 섹션·그림만 논문별.
- **함정**: 초기에 6개(폴더·양식·출판지·주제·방법론·자료)를 다 묻는 건 마찰. 첫 대화는 **2-3개만**, 나머지는 research/ideate에서 자연 추출 (progressive disclosure).

### 1.3 사용자가 묘사한 목표 흐름 (권위 — 받아쓰기)

> "ABC 논문 쓰려고 하면 — (1) 폴더 위치 물어보거나 추천 (2) 관련 주제 찾아보며 나랑 대화로 주제 잡기 (3) 관련 내용 데이터베이스화 (4) 초기 디렉토리 구조 딱 만들기. 전역 wiki도 필요하고 특정 논문 특화 wiki도 필요할 것 같다."

이 흐름이 `scholar-init`의 4단계 코어이고, 마지막 문장이 2계층 wiki의 근거다.

---

## 2. 설계 원칙 (불변 제약)

1. **citation 안전 최우선** — wiki(전역·로컬 모두)는 *2차 메모*이지 인용 출처가 아니다. `.bib`는 검증된 1차 출처로만. 임베딩 검색 영구 금지(결정론적 grep만). 전역 wiki에도 그대로 적용. (`references/wiki/README.md` §citation 안전 경계)
2. **read-진단 → 사람 게이트 → write 순서** — `scholar-init`의 모든 탐색은 read-only. 실제 디스크 쓰기는 사람 승인 후에만. (omp-init T20 패턴)
3. **progressive disclosure** — 첫 세션 질문 ≤ 3개. 나머지는 후속 단계에 위임.
4. **멱등성** — 이미 `.oms/`가 초기화된 폴더면 재초기화 경고 후 멈춤. 기존 wiki/learned 손실 방지.
5. **호출부 불변 원칙** — 전역 wiki는 `wiki_query` 추상 함수의 *구현*만 교체한다. inspector·planner 등 호출부는 건드리지 않는다. (`references/wiki/README.md` L70 "미래 교체점"이 명시한 자리)
6. **light → enforce 직승 금지** — 전역 wiki도 light 채널. venue 강제 기본값으로 굳히려면 `learned.md` → `scholar-learn` 사람 게이트를 거친다.

---

## 3. 산출물 1 — `scholar-init` 스킬

### 3.1 위치·트리거

- 파일: `skills/scholar-init/SKILL.md`
- 트리거: `논문 시작`, `새 논문`, `논문 셋업`, `프로젝트 만들어`, `scholar init`, `paper init`, `start a paper`, `bootstrap paper`, `ABC 논문 쓸래` 류.
- 라우팅: oms-routing hook에 STAGE `init` 추가 — `STAGE(paper) → init · <근거>`.
- pilot 통합: `scholar-pilot`이 `.oms/`가 없는 폴더에서 시작하면 `init`을 먼저 흡수(또는 권유)한 뒤 research로. (omp-pilot의 init 흡수 패턴과 동일.)

### 3.2 단계 (read-진단 → 게이트 → write)

```
GATE 0 — 멱등성 검사
  └ <paper>/.oms/ 존재? → 있으면 멈춤+경고("재초기화 시 wiki/learned 손실")+백업 권유.
    사용자 명시 동의 시에만 재진입. 재방문은 init이 아니라 research/pilot로 라우팅.

STEP 1 — 폴더 위치 (대화, 질문 ①)
  └ "어디에 둘까요? 추천: <cwd>/<제안-slug>/" — 사용자 확인 또는 다른 경로 지정.
    slug 규칙은 output-layout §1.1 (비ASCII 제목 → ASCII slug 1회 질문).

STEP 2 — venue + 한 줄 주제 (대화, 질문 ②③) — ⭐ 전역 wiki가 여기서 거듦
  └ 전역 wiki read: wiki_query_global('pattern')·wiki_query_global('convention')로
    "사용자가 보통 쓰는 venue·구조·표현"을 끌어와 추천으로 제시.
    예: "당신은 보통 IROS에 내셨죠 — IROS 2027로 갈까요? 섹션은 늘 쓰시던 구조로?"
  └ 한 줄 주제 + 핵심 기여(contribution) 1문장 받기. (방법론·세부는 묻지 않음 — research가 함)
  └ 기존 자료 위치(있으면): Zotero/bib/PDF 폴더 경로 — 있으면 기록, 없으면 skip.

STEP 3 — venue 매칭 + scaffold 합성 (read-only dispatch, opus)
  └ scholar-planner(또는 신설 scaffold 역할)에게: 선택 venue 카드 + 전역 wiki 씨앗을 입력으로
    "이 논문의 초기 디렉토리 구조 + venue-config + 논문별 wiki seed" 초안을 텍스트로 반환(디스크 안 씀).
  └ 초안 specificity 정직 기록(0.1~0.4 — 전역 wiki 씨앗이 많을수록 높게).

━━━ GATE 1 (사람) — 텍스트 proceed/revise/abort ━━━
  └ 제시: 폴더 위치 · venue · 디렉토리 트리 · 논문별 wiki seed · 어떤 전역 씨앗을 가져왔는지.
    자동 통과 없음. revise면 STEP 3 재합성.

STEP 4 — write (게이트 통과 후에만, 컨트롤러가)
  └ 디렉토리 scaffold 생성 (§3.3).
  └ .oms/<slug>/ 작업장 + .oms/wiki/ (논문별, 빈 4-카테고리) 생성.
  └ meta.md (인터뷰 답 저장 — venue·주제·기여·자료위치) 기록.
  └ venue-config(.oms/venues/<key>.yaml) 생성 — 전역 wiki에서 상속한 기본값 주입.
  └ .json류는 atomic write 경유 (omp_atomic.py 패턴 이식).

STEP 5 — 확인 리포트 (루프 아님, 1회 종료)
  └ 생성된 경로 목록 + 가져온 전역 씨앗 요약 + 다음 단계(research) 안내.
```

### 3.3 생성하는 디렉토리 구조 (scaffold)

Good-enough-practices + Overleaf 절충, oms 기존 관습(`NN_*.tex ↔ §N`) 유지, 제출 함정(서브폴더 비허용) 대비:

```
<paper-root>/                      # 사용자 지정 (STEP 1)
  sections/        NN_intro.tex …  # oms 기존 NN 접두 ↔ PDF §N 1:1 관습
  figures/
  refs/            paper.bib       # per-paper bib (전역 bib에서 cherry-pick)
  data/                            # raw, read-only
  preamble.tex                     # 전역 매크로를 \input (전역 wiki 연결점)
  meta.md                          # venue·주제·기여·자료위치 (인터뷰 답 = 논문별 wiki의 사람용 뷰)
  <slug>.tex                       # 메인
outputs/<slug>/                    # 컴파일 PDF (output-layout 그대로)
.oms/<slug>/                       # 작업장 (output-layout 그대로)
.oms/wiki/                         # 논문별 wiki (convention/pattern/decision/reference)
.gitignore                         # .oms/ + outputs/* 제외
```

> ⚠️ 제출 직전 flatten이 필요한 venue는 `scholar-verify`에 flatten 체크를 추가 (별도 — 이 설계 범위 밖, 메모만).

### 3.4 omp-init에서 그대로 이식하는 것 (도메인 무관, 검증됨)

- `omp_atomic.py` (tempfile→fsync→os.replace, stdlib only, cross-platform, `ensure_ascii=False`) → `hooks/oms_atomic.py`로 복사.
- GATE 0 멱등성 검사 구조 / read-진단→게이트→write 순서 / 텍스트 게이트(AskUserQuestion 아님) / self-approval 금지 / specificity 정직 기록.

### 3.5 omp와 다르게 가야 하는 것 (도메인 차이 — 조사 경고)

- **dataset 추적(SHA256/split/lineage) 이식 안 함** — 논문 도메인 무의미. 대신 `.bib` 인용 인벤토리·section 매핑이 추적 대상.
- **organize류 파일 이동 안전 프로토콜 통째 이식 안 함** — venue 규칙은 파일을 옮기지 않고 내용/구조를 강제. 과잉.
- **specificity 소유 단위가 다름** — omp는 "이 프로젝트"가 단위. oms는 "이 사용자의 venue 습관"이 단위(전역 wiki). 이 설계가 그 차이를 전역 wiki로 해소한다.

---

## 4. 산출물 2 — 전역 wiki (상위 폴더 `.oms/` 계층)

### 4.1 현재 구조 (사실)

```
논문A/.oms/wiki/   ← A만. B와 분리, 서로 못 봄.
논문B/.oms/wiki/   ← B만.
전역 계층          ← 없음.
```

`wiki_query(category)`는 *현재* "작업 대상 프로젝트의 `.oms/wiki/<category>/` grep" (`references/wiki/README.md` L69).

### 4.2 목표 구조 (2계층) — ⭐ "전역" = 상위 폴더의 `.oms/` (절대경로 0개)

> **핵심 정정 (2026-05-31, 사용자 지적)**: "전역"은 머신 전역(`~/.config`)도, 별도 자산 폴더(vault)도 아니다.
> **상위(부모) 폴더의 `.oms/`**다. 사용자가 claude code를 *논문들의 부모 폴더*(예: `~/Desktop/workspace`)에서
> 실행하면 거기가 자연히 "전역 레벨"이고, 각 논문 폴더가 "로컬 레벨"이다. `.omp`·`.omc`와 똑같이 **항상 cwd 상대**.
> 배포물엔 절대경로·환경변수·XDG가 **하나도** 없다 (oms 철학 "모든 경로 work-root 상대" 그대로).

```
~/Desktop/workspace/              ← 사용자가 claude code 실행 (= 논문들의 부모)
├── .oms/wiki/                    ⭐ "전역" = 부모 폴더의 .oms/ (모든 논문 공통)
│     convention/  venue별 양식·섹션 구조
│     pattern/     ⭐성향(표현·구조·작업방식·선호)
│     decision/    재사용 결정(왜 이 baseline)
│     reference/   자주 쓰는 자원 포인터
│     history/     ⭐신설: 내 논문 history
│         ▲  │
│         │  │ ① init이 새 논문 시작 시 ascent로 READ (씨앗)
│         │  ▼
├── 10-19_Academic/.../ABC논문/
│     └── .oms/wiki/              ← 논문별 = 이 폴더의 .oms/ (ABC 전용)
│           convention/  이 논문 reject 패턴
│           pattern/     (대개 비어 있음)
│           decision/    이 논문 결정
│           reference/   이 논문 자원
│         │
│         │ ② 논문 끝나면 "재사용각" 후보를 사람 승인 후 부모 .oms/로 승격(scholar-learn 확장)
│         └──────────────────────────▲
└── .../DEF논문/.oms/wiki/  …
```

다른 사용자는 *자기* 논문 부모 폴더에서 실행 → 거기가 그 사람의 전역 레벨. 머신·사용자별 자동 분리, 박을 게 없음.

### 4.3 "전역 .oms/" 탐색 = ascent (git의 `.git` 찾기 방식) — 확정

- cwd에서 부모로 올라가며 **가장 가까운 상위 `.oms/` 하나**를 전역으로 삼는다 (자기 자신 `.oms/` 제외).
- git이 `.git`을, Node가 `node_modules`를, omp가 루트를 찾는 그 ascent 패턴. 검증됨, 절대경로 안 나옴.
- 당신 경우: `ABC논문/.oms/`(로컬) → 위로 → `workspace/.oms/`(전역) 발견. 둘 사이에 다른 `.oms/`가 없으니 깔끔히 2계층.
- **상위 `.oms/`가 없으면** 전역 계층은 그냥 비활성 (project-local만). graceful — 에러 아님.
- (경계 안전장치는 §6 열린 질문 3으로 — 홈까지 무한 ascent 방지가 필요한지는 구현 시 판단. git도 사실상 무한 ascent지만 문제 없음.)

### 4.4 구현 — `wiki_query` 추상 함수만 교체 (호출부 불변)

`references/wiki/README.md` L70이 명시한 "미래 교체점"이 바로 이 자리:

```
wiki_query(category) →   # 기존: 프로젝트 .oms/wiki/<category>/ grep
  변경 후:
    local_hits    = grep(<cwd>/.oms/wiki/<category>/, keywords)            # 이 논문
    parent_oms    = ascent(<cwd>, find first ancestor .oms/ excluding self) # git 방식
    global_hits   = grep(parent_oms/wiki/<category>/, keywords) if parent_oms else []
    return merge(local_hits, global_hits)   # 출처 태깅: [wiki:local] / [wiki:global]
```

- 병합 시 출처 구분: 호출자(inspector)는 `[wiki:global]`/`[wiki:local]`/`[자체예측]` 3종으로 출처 표시.
- 결정론적 grep만 (CJK bi-gram 포함). 임베딩 금지 — 전역에도 불변.
- graceful degrade: 상위 `.oms/` 부재면 local_hits만. 에러 아님.
- **호출부(inspector pre-commitment, planner)는 한 줄도 안 바꾼다.** ascent+병합은 전부 `wiki_query` 구현 안에 갇힘.

### 4.5 워크스페이스 §7 "`.oms/`=scratch"와 충돌하지 않는다 (정정)

- 이전 초안은 "전역 wiki는 영속 자산이라 `.oms/` 밖에 둬야 한다"고 했으나 **틀렸다** — "영속"과 "경로 위치"는 별개 축이고, cwd 상대 경로도 폴더가 안 지워지면 영속된다.
- 전역 wiki는 **상위 폴더의 `.oms/wiki/`** 안에 그대로 둔다 (`.omp/wiki`·`.omc/wiki`가 그러듯). 워크스페이스 §7이 `.oms/`를 scratch로 보는 건 **버전 스냅샷·렌더·tmp 같은 작업 중간물** 얘기고, `wiki/`·`learned.md`는 §7 안에서도 이미 "세션 넘어 사는 누적 메모"(output-layout §5 cleanup 제외 대상)다.
- 즉 전역 wiki는 워크스페이스 룰의 *예외가 아니라*, 이미 §7·output-layout이 인정한 "`.oms/wiki/`는 누적 보존" 범주에 자연히 속한다. 별도 정책 선언 불필요.

### 4.6 무엇이 전역에 갈 자격이 있나 (승격 정책)

| 종류 | 전역 승격 | 이유 |
|:---|:---:|:---|
| `pattern/` 성향(표현·구조·작업방식·선호) | ✅ 1순위 | 논문마다 안 바뀜. 사용자 정체성. light 전용(enforce 안 함) |
| `convention/` venue 양식·섹션 구조 | ✅ (사람 게이트) | venue별로 재사용. `learned.md`→`scholar-learn` 경유 |
| `decision/` 재사용 결정 패턴 | ✅ | "나는 늘 ablation 먼저" 같은 메타 결정 |
| `history/` 내 논문 history | ✅ (신설) | "이전에 쓴 논문들" — init이 중복·연결 참고 |
| **citation / `.bib` 내용** | ❌ **영구 금지** | 환각 인용 위험. learn 승격 대상 아님(불변) |
| 이 논문 한정 주제·gap | ❌ | project-local에 남음 |

### 4.7 oms 안티패턴("user-scope/distributed config에 쓰지 마라")과 화해된다

- 기존 원칙의 *취지*는 두 가지: (a) "이 논문 한정 지식이 전역으로 새어 모든 논문 오염" 방지, (b) "배포물(plugin)에 특정 사용자 경로·지식을 박지 마라".
- ascent 방식은 **둘 다 위반하지 않는다**:
  - (b) 배포물엔 절대경로·환경변수가 0개 — `.oms/`는 항상 cwd 상대. plugin 소스는 "상위 `.oms/`를 ascent로 찾아라"는 *로직*만 담고, 경로는 런타임에 결정. 이건 oms 철학("work-root 상대") 그 자체다.
  - (a) 전역(상위 `.oms/`)에 올라가는 건 **"논문 무관 재사용 자산"만**(성향·venue 양식·history). 논문 고유 지식은 그 논문 폴더 `.oms/`에 남는다.
- `learning-protocol.md`에 명시: "상위 `.oms/wiki/`(전역 레벨)는 재사용 자산 전용. 논문 고유 지식·citation은 영구히 그 논문 `.oms/`/금지." citation 전역 승격 금지는 불변.

---

## 5. 빌드 순서 (구현 단계 — 별도 plan 문서로)

> 이 design 승인 후 `superpowers:writing-plans`로 TDD 실행 plan 작성.

1. ~~선결: 런타임을 0.2.x로 올린다~~ → **정정(2026-05-31 재확인)**: 활성 런타임은 **이미 10스킬(wiki/learn 포함) 최신 계열**(활성 캐시 `bf4633aa9916`, 소스 HEAD `c645193`=`c6451934685e`도 캐시에 존재). 조사 초기 "0.1.1/8스킬"은 *가장 오래된* 캐시(`013369a4`)를 읽은 오인. → 선결은 "wiki 미설치 해결"이 아니라, 개발 후 **활성 pin을 소스 HEAD에 맞추는 `marketplace update` 위생 작업**일 뿐. 논문별 wiki는 이미 동작 가능.
2. **Phase A — `scholar-init` (전역 wiki 없이)**: scaffold + 논문별 wiki seed + GATE + atomic write. 전역 read는 "있으면 읽고 없으면 skip"으로 graceful.
3. **Phase B — 전역 wiki 계층**: `wiki_query` 구현 2계층화 (ascent로 상위 `.oms/` 찾기 + 병합) + `learning-protocol.md` 경계 문서화 + 승격 정책(`scholar-learn` 확장).
4. **Phase C — 통합**: pilot의 init 흡수 + oms-routing hook에 `init` STAGE 추가 + 테스트.

각 Phase는 omp의 검증된 패턴(fresh implementer + spec-compliance reviewer + code-quality reviewer)으로.

---

## 6. 열린 질문 (구현 전 확정)

1. ~~`<global-root>` 위치~~ → **확정: 상위 폴더 `.oms/` ascent (git 방식, 가장 가까운 하나). 절대경로·환경변수 없음.** (§4.2-4.4)
2. ~~머신 간 sync~~ → **해당 없음.** 상위 `.oms/`가 sync되는 폴더(iCloud workspace 등)에 있으면 자동으로 따라감 — oms가 관여 안 함.
3. **ascent 경계 안전장치**: 홈/루트까지 무한 ascent를 막을 stop 조건이 필요한가? git은 사실상 무한 ascent지만 실무 문제 없음. 단순하게 "가장 가까운 상위 `.oms/` 하나, 없으면 비활성"이면 충분할 듯 — 구현 시 확정.
4. `history/` 카테고리를 전역 레벨에 신설할지, 아니면 `decision/`에 흡수할지.
5. `scholar-init`을 독립 스킬로 둘지(확정), pilot 흡수 시 사용자에게 물을지 자동 진입할지.
6. 첫 세션 질문 3개의 정확한 문구·순서 (venue 먼저? 주제 먼저?).
7. **부모 `.oms/`는 누가 만드나?** 사용자가 workspace에서 `scholar-init`을 한 번 돌리면 그게 부모 `.oms/`가 되는가, 아니면 별도로 "전역 init"이 필요한가? (첫 논문 init 시 상위 `.oms/`가 없으면 — 만들지 말지, 권유할지.)

---

## 7. 비고 — 이 설계가 안전한 이유 3가지

1. **전역 wiki 진입점이 이미 추상화돼 있다** (`wiki_query` "미래 교체점") — 구현만 바꾸면 됨, 호출부 안 건드림.
2. **omp-init이 검증된 부트스트랩 패턴을 이미 제공** — `scholar-init`은 새 발명이 아니라 이식.
3. **2계층(전역/로컬)은 보편 패턴** — Zettelkasten·texmf·Obsidian 모두 같은 모양. 재발명 아님.

가장 큰 리스크는 §4.5(워크스페이스 §7 충돌)와 §4.7(안티패턴 화해) — 둘 다 "전역엔 재사용 자산만, 논문 고유·citation은 절대 안 올림"으로 해소된다. 이 경계가 무너지면 oms 정체성(citation 안전)이 붕괴하므로, 구현 시 가장 엄격히 지킬 불변 제약이다.
