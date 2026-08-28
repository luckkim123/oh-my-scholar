# Heavy-Channel Backport — oms/omd self-specialization (design)

> **상태**: DESIGN (코드 한 줄도 안 고침). 두 repo(oms·omd) 공통 설계. GATE 후 execution plan.
> **Target artifacts**: oms = `~/oh-my-scholar/{references,skills,agents,hooks}`, omd = `~/oh-my-docs/{references,skills,agents,hooks}`.
> **정본 위치**: 이 파일(oms 작업장). omd 작업은 이 파일을 참조 (omp P0~P6 처럼 한 design → 두 repo 대칭 적용).
> **작성**: 2026-05-31. 후속: [[oms_omd_self_specialization_next]] 메모리 닫기.

---

## §0. 한 줄 요약

oms/omd 에 **이미 light 채널**(wiki 자동 append → grep 회수)은 작동 중이다. 이 backport 는
omp 의 **heavy 채널**(관찰 → 사람 승인 게이트 → *강제되는* 기본값 + specificity 추적)을
두 repo 의 도메인(venue / org-style)에 맞춰 이식해, "쓸수록 이 사용자에게 특화"를 *기억*에서
*강제*까지 닫는다. citation-safe·embedding-금지 불변은 그대로.

---

## §1. 진단 — 무엇이 이미 있고 무엇이 빠졌나 (검증된 사실)

| 축 | omp (원본) | oms | omd | OMC (원천) |
|:---|:---:|:---:|:---:|:---:|
| Light: wiki auto-append → grep | ✅ `.omp/wiki/` | ✅ `.oms/wiki/` | ✅ `.omd/wiki/` | ✅ `.omc/wiki/` (8 cat) |
| 양방향 루프 (write↔read) | ✅ | ✅ inspector pre-commit | ✅ doc-inspector | ✅ wiki_query |
| **confidence 등급** (반복→신뢰↑) | evidence_count | ❌ | ❌ | ✅ `high\|med\|low`, merge=keep-higher |
| **모순/반례 검사** | counter_examples | ❌ | ❌ | ✅ `wiki_lint`(contradiction) |
| **Heavy: 관찰→게이트→강제규칙** | ✅ learned.md→learn→rules | ❌ **없음** | ❌ **없음** | (암묵 — confidence+lint) |
| **specificity 0→1 지표** | ✅ rules.json | ❌ **없음** | ❌ **없음** | ❌ (없음) |

**결론**: oms/omd 는 *기억하고 다음에 조언*은 하지만(light 닫힘), 그 기억을 **다음 작업에서
강제되는 기본값**으로 굳히는 축과, **얼마나 특화됐나**를 보는 지표가 없다. OMC 조차 `confidence`
등급 + `wiki_lint` 모순검사라는 *약한 승격 장치*를 두는데, oms/omd 는 그것도 안 옮겼다.

---

## §2. 핵심 설계 결정 — omp 와 무엇이 같고 무엇이 다른가

### 2.1 승격 대상이 다르다 (파일 규칙 → 작업 사양 기본값)

omp heavy 채널은 **파일을 옮기는 규칙**(`structure.directories[]`·`naming.patterns[]`)을 승격한다 →
잘못 승격하면 파일이 잘못 이동 → 무거운 게이트. oms/omd 엔 옮길 파일이 없다. 대신 승격 대상은
**"작업 사양 기본값"**이다:

- **oms**: "이 사용자는 IROS 류에 항상 ablation 섹션을 넣는다 / related work 를 method 앞에 둔다 /
  self-citation 을 0.1 밑으로 유지한다" → **venue 기본값**으로 굳음.
- **omd**: "이 조직 디펜스 deck 은 캡션 12pt 검정 / contribution 슬라이드 필수 / 제목은 D-2 톤" →
  **org-style 기본값**으로 굳음. (omd `docs-standardize` 가 이미 N-문서 귀납으로 style-spec 을
  만든다 — heavy 채널은 그 spec 을 *반복 관측으로 승격된 강제 규칙*으로 격상.)

### 2.2 ⭐ scope 차원이 한 단계 더 있다 (omp 엔 없는 것)

omp 의 `rules.json` 은 **프로젝트당 하나**. 그런데 oms 는 venue 가 여럿(`iros.yaml`,
`postech_msc_thesis.yaml`…), omd 는 org/발표유형이 여럿이다. "항상 ablation 넣음"이 IROS 엔 맞고
thesis 엔 아닐 수 있다. 따라서 **승격된 규칙은 scope 에 묶인다**:

```
scope: global        # 이 사용자의 보편적 습관 (모든 작업 공통) — 예: 항상 한글 초록 동봉, 결론 먼저 검토
scope: <venue-key>   # 이 종류 작업에서의 습관 — 예: scope: iros / scope: defense-deck
```

이게 오히려 사용자 비전("내 작업 방식")에 더 정확하다 — 논문 쓸 때 습관 ≠ 디펜스 만들 때 습관.
`global` = 보편 특성, `<scope>` = 작업 종류별 특성.

### 2.3 specificity 의 의미 (같은 0→1, 다른 분모)

- omp: "규칙 중 몇 %가 프로젝트 소유냐"
- **oms/omd**: "이 venue/org 사양 중 몇 %가 *학습으로 굳은* 값이냐(범용 템플릿 default vs 내 반복
  패턴)". 분모 = 그 scope 의 활성 사양 항목 수, 분자 = origin∈{inductive,learned} 항목 수.
  scope 별로 따로 계산 (venue `iros` 의 specificity, `global` 의 specificity 가 각각).
  공식은 omp `learning-protocol.md` §4 그대로 — monotonic(승격은 올리거나 유지, 절대 조용히 안 내림).

### 2.4 ⚠️ citation-safe 불변 (oms 전용, 절대 위반 금지)

heavy 채널이 생겨도 oms 는 **절대 .bib·인용·"이 논문을 인용한다" 류를 승격하지 않는다**. 승격
대상은 *구조·양식·작업방식 사양*뿐. learned.md 의 candidate_rule.target 에 citation/bib 류가
오면 **스키마에서 거부**(허용 target enum 에 없음). embedding 회수도 omp/OMC 와 동일하게 영구 금지
— 회수는 결정론적 grep(CJK bi-gram 포함, OMC query.js 패턴)만.

---

## §2.5. ⭐ 학습 대상의 전체 지도 — 양식만이 아니다 (사용자 지적 반영)

> 사용자 지적: "양식뿐 아니라 대화로 생긴 규칙·내 작업 방식·성격·좋았던 점·주로 하는 작업
> 종류·주로 만지는 문서 종류 — 학습할 게 엄청 많지 않나?" → **맞다.** §2.1 이 승격 대상을
> *산출물 사양*에 가둔 건 너무 좁았다. 학습 대상은 두 부류로 갈리고, **채널이 다르다**.

핵심 구분: **enforce 가능한가**(다음 작업에 자동으로 *깔리는* 기본값) vs **조언으로만 의미**
(모든 단계가 참고하는 성향 메모). 전자=heavy(게이트), 후자=light(무게이트).

| 사용자가 말한 것 | 채널 | 카테고리 | 어떻게 적용 |
|:---|:---:|:---|:---|
| 대화 중 생긴 **명시적 규칙** ("앞으로 X는 이렇게") | **heavy** | learned.md | 게이트 거쳐 venue/style 기본값으로 강제 |
| 반복 관측된 산출물 사양 (ablation·캡션 12pt) | **heavy** | learned.md | 게이트 거쳐 기본값 강제 (§5 트레이스) |
| **주로 하는 작업 / 주로 만지는 문서 종류** | light | `pattern/work-profile.md` | 다음 작업 때 "당신은 주로 IROS·디펜스 deck" 컨텍스트 주입 |
| **내 작업 방식** (반례부터, 결론 먼저 검토) | light | `pattern/working-style.md` | inspector/planner 가 참고 |
| **성격·성향** (장황함 싫어함, 직설 선호) | light | `pattern/preferences.md` | 모든 단계 톤·상세도 조정 |
| **좋았던 점** (이 접근이 잘 먹혔다) | light | `decision/*.md` | 성공 패턴 누적 → 재사용 |

### light 채널 카테고리 확장 (OMC 8-cat 사상 일부 수용)

현재 oms/omd light 채널은 `convention/decision/reference` 3개뿐. **`pattern/` 신설** —
사용자라는 *사람*의 작업 성향을 담는 곳(OMC 의 `pattern`/preference 대응, 도메인 무관 부분).
`convention`=산출물이 어떻게 생겼나(heavy 승격 후보 원천), `pattern`=사용자가 어떻게 일하나
(light 전용, 승격 안 함 — 성향은 enforce 대상이 아니다).

```
.oms/wiki/                       .omd/wiki/
  convention/   ← heavy 후보       convention/   ← heavy 후보
  pattern/      ← ⭐신설 (성향)     pattern/      ← ⭐신설 (성향)
    work-profile.md                  work-profile.md
    working-style.md                 working-style.md
    preferences.md                   preferences.md
  decision/     ← 성공패턴           decision/
  reference/                         reference/
```

### ⭐ 프로필 위치 결정 (GATE 답변 2026-05-31): 각 하네스 작업장에 각자

"성격·선호·작업방식"은 oms·omd 공통이지만 **공유 프로필 1곳을 두지 않는다** — 각 repo 가 자기
작업장(`.oms/wiki/pattern/`, `.omd/wiki/pattern/`)에 각자 누적. 근거: ① 하네스 자족·독립 원칙
(각 repo 가 자기 작업장만 앎)을 안 깸 ② 논문 작업 성향 ≠ 문서 작업 성향이라 도메인별 분리가
실제로 더 정확. 중복 가능성(진짜 공통 성격)은 도메인 차이로 정당화. 전역 공유 프로필은 *필요성이
확인되면* 별도 세션(omha/전역 레벨)에서 — 이번 backport 범위 밖.

### heavy 채널이 받는 두 입구 (반복 관측 + 대화 규칙)

heavy 채널 candidate 는 두 경로로 들어온다:
- **(a) 반복 관측** — inspector/verify 가 같은 사양 이슈를 ≥3회 봄 (§5 자동 경로).
- **(b) 대화 규칙** — 사용자가 작업 중 "앞으로 이렇게 해줘"라고 명시. 이건 evidence_count 1 이어도
  `user_stated: true` 면 게이트에 바로 올림(반복 불필요 — 사용자가 직접 말한 규칙이라 증거가
  곧 사용자 의도). 단 **여전히 게이트는 거친다**(어느 scope 에 굳힐지·기존 규칙과 모순 없는지
  사람이 확인). 자동 강제는 여기서도 금지(§6.B).

---

## §3. OMC wiki 에서 추가로 가져올 것 (사용자 지시: "omc wiki 도 참고")

OMC wiki 실측(`dist/tools/wiki-tools.js`·`hooks/wiki/{ingest,query}.js`)에서 oms/omd 가 *아직 안
옮긴* 두 가지를 light 채널에 보강한다 — 이 둘이 heavy 채널과 잇는 고리다:

| OMC 기능 | 현재 oms/omd | backport |
|:---|:---|:---|
| frontmatter `confidence: high\|med\|low`, merge=**keep higher** | 없음(자유 .md) | wiki 노트에 confidence 추가. **반복 관측 → low→med→high 상승**이 곧 omp `evidence_count` 의 도메인판 |
| `wiki_lint`: orphan·stale·**structural contradiction** 탐지 | 없음 | learn 단계 진입 전 **반례/모순 검사**(omp `counter_examples==0` 게이트의 OMC식 구현) |
| append-only **timestamped section** merge (never replace) | 이미 있음(append) | 유지 — `## <ISO> — <one-line>` 컨벤션 명문화(omp §5 와 동일 규율) |
| `category` enum (8개) | 3개(convention/decision/reference) | **유지**(도메인 축소 정당). heavy 후보는 `convention` 에서만 승격 |
| NO vector embeddings (하드 제약) | 이미 명문 | 유지·재확인 |

**confidence ↔ 승격 게이트 연결**: light 채널에서 같은 패턴이 반복 관측되면 confidence 가 high 로
오른다. heavy 채널 승격 게이트(§4)는 **confidence==high + 반례 0(wiki_lint) + 사용자 미거부**일
때만 candidate 를 게이트에 올린다. 즉 OMC 의 confidence 누적 + omp 의 사람 게이트가 합쳐진다.

---

## §4. 채택·제외 매핑 (backport 작업 ID = Hn, "Heavy")

> oms/omd 동형. 각 행 = 무엇이 바뀌나. 기존 Tn(wiki light backport)과 별개 계열(Hn).

### 채택 (adopt)

| Hn | 무엇 | oms 적용 | omd 적용 |
|:---|:---|:---|:---|
| **H1** | learning-protocol 카드 신설 | `references/learning-protocol.md` — omp 카드를 도메인 적응(승격 대상=venue 기본값, scope 차원, citation-safe 불변 추가) | 동일, 승격 대상=org-style 기본값 |
| **H2** | 관찰 원장 | 작업장 `.oms/learned.md`(gitignore, append-only, OBS 블록 §2 형식 + `scope` 필드 추가) | `.omd/learned.md` |
| **H3** | 승격 skill 신설 | `skills/scholar-learn/SKILL.md` — learned.md candidate 를 §4 기준 판정 → 사람 게이트 → venue.yaml 기본값 승격 | `skills/docs-learn/SKILL.md` → org-style-spec 승격 |
| **H4** | 승격 판정 agent | 기존 `scholar-inspector`/신설? → **rule-architect 대응 신설 안 함**, scholar-learn 이 inspector 의 read-only 판정 재사용(self-approval 금지: 판정≠승인, 승인은 사람) | doc 측 동일, doc-inspector 재사용 |
| **H5** | specificity 필드 | `venue.yaml` 스키마에 `specificity: 0..1` + 항목별 `origin: preset\|inductive\|learned` | style-spec 에 `specificity` + origin |
| **H6** | confidence 등급 (OMC) | wiki frontmatter 에 `confidence` + merge keep-higher (§3) | 동일 |
| **H7** | wiki_lint 모순검사 (OMC) | scholar-learn 진입 전 `.oms/wiki/convention/` 반례/모순 스캔 → counter_examples 산정 | 동일 |
| **H8** | pilot wiring | `scholar-pilot` 에 learn 단계는 **자동 발동 안 함**(heavy=사람 게이트). 대신 "승격 후보 N건 쌓임 → scholar-learn 제안" 한 줄 알림만. wiki capture 단계에 `pattern/` 적재 추가(work-profile·working-style·preferences — §2.5) | docs-pilot 동일 |
| **H8b** | 대화-규칙 입구 | scholar-learn 이 `user_stated: true` candidate(사용자가 "앞으로 이렇게" 명시)를 evidence 1 이어도 게이트에 올림(§2.5 입구 b). 자동 강제는 여전히 금지 | docs-learn 동일 |
| **H9** | 라우팅 토큰 | `hooks/scholar_route_emit.py` STAGE 카탈로그에 `learn` 추가 | `hooks/route_emit.py` 에 `learn` + 테스트 |
| **H10** | 자체 audit 대응 | oms 엔 omp-audit 대응 없음 → scholar-verify 가 venue.yaml 의 specificity↔origin 정합만 가볍게 확인(경고) | doc-verify 동일 |

### 제외 (exclude — 사유)

| omp 패턴 | 제외 사유 |
|:---|:---|
| `structure.directories[]`·`naming.patterns[]` 승격 | oms/omd 엔 옮길 파일 없음 — 승격 대상은 venue/style 사양뿐 |
| `omp-organize`(파일 이동) 대응 | 동상 — 강제는 "다음 작업의 기본값 적용"이지 파일 이동 아님 |
| `manifest.json`/dataset 추적 | 도메인 무관(논문/문서엔 ML dataset 없음) |
| rule-architect *별도 agent 신설* | inspector 재사용으로 흡수(omp T1 "agent 신설 안 함" 사상 계승) |
| confidence **수치화 가중합/threshold** | OMC 도 정성 3등급뿐 — magic number 없이 high/med/low + 반복횟수로 충분 |
| embedding 회수 | **영구 금지**(citation-safe 붕괴) — grep only |
| 자동 승격(게이트 우회) | **영구 금지** — confidence high 여도 사람 승인 없이는 venue 기본값 안 굳음(omp §6.B) |

---

## §5. End-to-end 트레이스 (oms 예시 — 한 습관이 굳는 전 과정)

1. **운영**: 사용자가 IROS 논문 3편 작업. 매번 inspector 가 "ablation 섹션 없음"을 지적하고
   사용자가 매번 추가. scholar-pilot wiki capture 가 `.oms/wiki/convention/iros-*.md` 에
   "ablation 누락 반복 지적" append. 3회째 → confidence high 로 상승(OMC merge keep-higher).
2. **관찰 적재**: 같은 패턴이 `learned.md` 에 OBS 블록으로 — `scope: iros`,
   `candidate_rule: {target: venue.required_sections, value: +Ablation}`, evidence_count 3,
   counter_examples 0(다른 IROS 작업서 ablation 뺀 적 없음 — wiki_lint 검사).
3. **learn**: `scholar-learn` 실행. inspector(read-only)가 §4 기준 판정 — high·반례0·미거부·안정 →
   ripe. venue.yaml 편집 초안 + specificity delta + provenance + 근거 한 줄 제시, **게이트서 멈춤**.
4. **게이트(사람)**: 승인. `iros.yaml` 의 `required_sections` 에 Ablation 추가, origin: learned,
   specificity 0.0→0.14(7항목 중 1 learned), OBS status: promoted, learned_refs 기록,
   venues.md 사람용 narrative 동기 갱신(.md↔.yaml drift 0).
5. **강제**: 이후 IROS 작업은 scholar-outline 이 Ablation 을 **기본 섹션으로 깐다**. 사용자가
   매번 말 안 해도. 두 번째 brain 이 *이 사용자의 IROS 습관*에 특화됨 — 전 과정 디스크에 남고
   사람이 grep 으로 재현 가능.

omd 대칭: "디펜스 deck 캡션 12pt 검정"이 3회 반복 관측 → high → docs-learn 게이트 →
`defense-deck` style-spec 기본값 → 이후 docs-build 가 캡션을 자동으로 12pt 검정으로.

---

## §6. 작업 규모·순서 (execution plan — 2026-05-31 GATE 통과 확정)

- **공통 선행**: H1(learning-protocol 카드) 을 omp 것에서 도메인 적응. oms·omd 각각 1개.
- **oms**: H2~H10 — learned.md 시드(빈), scholar-learn skill 신설(omp-learn 참고, 도메인 적응),
  venue.yaml 스키마에 specificity/origin, wiki frontmatter confidence, route_emit learn 토큰.
- **omd**: 동형 — docs-learn skill, style-spec 에 specificity/origin, route_emit learn + 테스트.
- **검증**: 각 repo 에서 reviewer pass(spec compliance ≠ code quality 분리) + route_emit 테스트.
- **순서**: oms 먼저 완주(citation-safe 가드 검증 포함) → omd 대칭 적용 → 양 repo 각각 PR.
- ⚠️ **push 전 사용자 승인** — 하네스 repo 수정이므로 surgical. omp backport(P0~P6) 와 같은 규율.
- ⚠️ **marketplace 운영 사실 (2026-05-31 확인)**: oms/omd 는 `heroacademia` marketplace 설치라
  `~/.claude/plugins/cache/heroacademia/{oh-my-scholar,oh-my-docs}` 에 *별도 사본*이 산다. **repo
  를 고쳐도 marketplace update 전엔 라이브 미반영** — claudebase(심링크 라이브)와 다르다. 따라서
  "구현 = repo 수정 + 테스트", "라이브 반영 = 별도(marketplace update / uninstall→install)" 2단계.

### §6.1 단계별 실행 순서 (oms 먼저, 각 단계 = 하나의 검증 가능한 산출)

> 워크스페이스 룰: spec/plan 은 작업장(`.oms/_backport-design/`)에. target artifact 경로 명시.

1. **H1 — oms learning-protocol 카드** → `~/oh-my-scholar/references/learning-protocol.md`
   (omp 카드를 venue 도메인 적응: 승격 대상=venue 기본값, scope 차원, citation-safe F 추가).
   검증: 카드가 §3 5조건·§4 specificity 공식·§7 불변 6종을 venue 어휘로 담는지 self-review.
2. **H2 — learned.md 시드** → `~/oh-my-scholar/.oms/learned.md` 빈 ledger(append-only, OBS 형식
   + `scope` 필드). gitignore 확인(작업장은 .gitignore 대상). 검증: 파일 존재 + 형식 주석.
3. **H6 — wiki confidence** → `~/oh-my-scholar/references/wiki/` README 에 frontmatter
   `confidence: high|med|low` + merge=keep-higher 규약 추가. 검증: 규약 문서화.
4. **H3 — scholar-learn skill** → `~/oh-my-scholar/skills/scholar-learn/SKILL.md`
   (omp-learn 구조 차용, scholar-inspector read-only 재사용으로 판정≠승인 분리). 가장 리스키 —
   §8 의 #1·#2·#4 가 다 여기 모임. 검증: skill frontmatter + Steps + GATE 명시 + 라우팅 등록.
5. **H5 — venue.yaml 스키마** → venue YAML 에 `specificity: 0..1` + 항목별 `origin`. 검증:
   기존 venue 1개에 필드 추가해 round-trip(파싱) 확인.
6. **H9 — route_emit learn 토큰** → `~/oh-my-scholar/hooks/scholar_route_emit.py` STAGE 카탈로그에
   `learn` 추가 + 테스트. 검증: route_emit 테스트 GREEN.
7. **H10 — verify 정합 체크** → scholar-verify 에 specificity↔origin 경고 1줄. 검증: 경고 경로.
8. **omd 대칭(H1~H10)** → `~/oh-my-docs/{references,skills,hooks}` 동형. docs-learn, style-spec
   specificity/origin, route_emit learn+테스트. 검증: omd route_emit 테스트 GREEN.
9. **리뷰 패스(작성≠검토)** — 각 repo 구현 후 fresh reviewer 컨텍스트로 spec-compliance +
   citation-safe 가드(§6.F) 검증. self-approve 금지.

---

## §8. 적대적 검토 결과 — GATE 통과 (2026-05-31)

설계를 4 렌즈(내부일관성·citation안전·omp충실도·구현가능성)로 검토. **Major 2 + Minor 2**.
omp `learning-protocol.md` 정독으로 **셋(#1·#2·#4)은 omp 가 이미 푼 것을 backport 가 명시
누락한 것**으로 판명 — 새 설계 불필요, omp 조항의 도메인 명문화로 해소. 해소책을 H1 카드에 박는다.

| # | 심각도 | 문제 | 해소 (H1 카드에 명문화) |
|:---|:---|:---|:---|
| **#1** | Major | §3 confidence==high 게이트 vs §2.5 입구(b) user_stated(evidence 1) 모순 — 반복 0인데 high 불가 | omp §"Capturing USER feedback" 차용: user_stated candidate 는 `source_stage: feedback` 로 **confidence 게이트 우회**, evidence 1 로 바로 사람 게이트行. 단 자동 강제는 여전히 금지(§6.B). |
| **#2** | Major | "confidence high 가 몇 회?"가 magic-number 없이 미정의. §5 는 3회라는데 §4 엔 미기재 | omp §3.1 `evidence_count ≥ 3` 그대로 채택. H1 카드에 "**반복 3회 = high 승격 threshold**" 명문(매직넘버 아님 — omp 가 "convention vs coincidence 최소선"으로 정당화한 값). |
| **#3** | Minor | specificity monotonic 인데 venue 항목 삭제 시 분모 변동으로 비단조 가능 | omp §4 "monotonic: 승격은 올리거나 유지, 절대 silent 하락 금지" 채택 + **항목 삭제는 specificity 재계산 이벤트로 명시**(삭제도 provenance 남김, silent 변동 금지 = §6.C). |
| **#4** | Minor | H4 "판정≠승인"이 scholar-learn 이 inspector 판정을 받아 게이트 제시 → 같은 컨텍스트 긴장 | omp 정답 채택: rule-architect(read-only, `disallowedTools:[Write,Edit]`) **제안만**, 사람이 끊음, 준수판정은 별도 컨텍스트. oms 는 scholar-inspector 를 read-only 판정에 재사용하되 **scholar-learn 은 디스크 쓰기만**(판정 안 함). self-approval 3중 금지(설계≠강제≠검증). |

**GATE 판정**: 4건 모두 H1 카드 명문화로 해소 가능 → **설계 승인, 구현 진입 OK**. 잘된 점(유지):
§2.5 enforce vs 조언 이분법, §7 불변 6종(특히 F citation 승격 금지), §2.2 scope 차원(omp 엔 없는
진짜 개선). 검토자: 단일 컨텍스트 4 렌즈(이번 세션). 구현 후 fresh reviewer 가 spec-compliance 재검(§6.1-9).

---

## §7. 불변 제약 (위반 시 정체성 붕괴 — omp §6 계승 + oms/omd 추가)

- **A. embedding 회수 영구 금지** — grep only(CJK bi-gram). OMC query.js·omp §6.A·oms wiki README 일치.
- **B. 자동 승격 금지** — confidence high·evidence 아무리 높아도 사람 게이트 없이 venue/style 안 굳음.
- **C. silent 변경 금지** — venue.yaml/style-spec 변경은 provenance(learned_refs)+페어 .md 동기+
  specificity 재계산 동반. 셋 중 하나라도 빠지면 verify 가 flag.
- **D. light→enforce 직승 금지** — wiki 노트는 조언일 뿐. 강제하려면 learned.md 거쳐 게이트로.
- **E. 날조 evidence 금지** — evidence[] 는 실제 세션 이벤트/파일만. ≥3 채우려 지어내지 않음.
- **F. ⚠️ citation 승격 금지 (oms)** — .bib·인용·출처는 영구히 heavy 채널 대상 아님. target enum 거부.
