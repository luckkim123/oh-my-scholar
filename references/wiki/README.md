# references/wiki — 세션 넘어 누적되는 2차 메모 store (쓸수록 이 프로젝트에 특화)

이 store는 **세션 휘발 데이터를 "랩 표준"으로 compound**하기 위한 영속 메모다. **양방향 루프**로 동작한다:
- **쓰기 (자동)**: scholar-pilot의 wiki capture 단계가 inspect/verify가 발견한 reject 패턴·결정을 **자동 append**한다 (승인 불필요 — 가벼운 채널, `scholar-pilot/SKILL.md` Step 10).
- **읽기 (자동)**: 다음 세션 inspector의 pre-commitment가 `wiki_query(category)`로 그 누적 패턴을 조회한다.

쓰기와 읽기가 닫혀 **하네스를 쓸수록 이 venue·이 논문 프로젝트에 점점 특화**된다 — 사용자가 명시적으로 "학습해"라고 부르지 않아도. 배포 시엔 빈 store(범용)지만 운영하며 발산한다.

`wiki_query(category)` 추상 함수의 현재 구현 대상이며, 비어 있거나 부재해도 동작이 깨지지 않는다(inspector가 자체 예측으로 진행).

---

## 디렉토리 레이아웃

⚠️ **데이터는 작업장(`.oms/wiki/`)에 쌓인다 — 이 plugin repo가 아니다.** 이 README는 *계약 문서*라 plugin(`references/wiki/README.md`)에 배포되지만, 실제 누적 데이터는 **작업 대상 프로젝트 루트의 `.oms/wiki/`**에 쓰인다(`.oms/`는 gitignore — plugin/배포물을 더럽히지 않고, 프로젝트별로 발산해 "이 프로젝트에 특화"가 성립). OMC의 `.omc/wiki/`(project-local) 패턴과 동일.

```
<프로젝트 루트>/.oms/wiki/          ← 작업장, gitignore, 프로젝트별 발산 (slug 밖 — 세션 넘어 누적)
  convention/   *.md   ← venue별 reject 사유·양식 규칙 (inspector가 조회) — ⭐ heavy 승격 후보의 원천
  pattern/      *.md   ← ⭐신설: 사용자가 *어떻게 일하나* (성향) — light 전용, 승격 안 함
    work-profile.md      ← 주로 하는 작업·만지는 venue 종류 ("당신은 주로 IROS·디펜스 deck")
    working-style.md     ← 작업 방식 (반례부터·결론 먼저 검토)
    preferences.md       ← 성격·톤 선호 (장황함 싫어함·직설 선호)
  decision/     *.md   ← 과거 결정 기록 (왜 이 baseline·이 비교군을 택했나·뭐가 잘 먹혔나)
  reference/    *.md   ← 외부 자원 포인터 (venue CFP·평가 rubric 링크)
```

- 파일 1개 = 한 주제 (예: `convention/neurips-reject-patterns.md`).
- 각 파일은 사람이 읽는 자유 형식 .md. 머신 파싱 스키마 없음(grep만 함).
- `category`는 위 **4개** 하위 디렉토리 이름과 1:1.
- ⚠️ `.oms/wiki/`는 *프로젝트 전체* 누적이라 작업별 `.oms/<slug>/`(output-layout) **밖**이다 — slug에 묶이지 않고 세션·작업을 넘어 산다.

### ⭐ `convention/` vs `pattern/` — heavy 승격 후보는 convention 에서만 (2026-05-31 H6 backport)

이 둘의 분리가 핵심이다 (`references/learning-protocol.md` §1):
- **`convention/`** = *산출물이 어떻게 생겼나* (섹션 순서·캡션 양식·reject 사유). 반복 관측되면
  `learned.md` 로 escalate 돼 **heavy 채널 승격 후보**가 된다 (venue 기본값으로 굳을 수 있음).
- **`pattern/`** = *사용자가 어떻게 일하나* (성향·작업방식·선호). **light 전용 — 절대 승격 안 함.**
  성향은 enforce 대상이 아니라 모든 단계가 톤·상세도를 맞추려 *읽는* 메모일 뿐. `pattern/` 노트가
  `learned.md` 로 올라가는 일은 없다.

### ⭐ confidence frontmatter — 반복 관측이 신뢰도를 올린다 (OMC backport, H6)

각 wiki 노트는 frontmatter `confidence: high | med | low` 를 단다. 같은 패턴을 다시 관측하면
confidence 가 `low → med → high` 로 오르고, merge 시 **높은 쪽을 유지**(약한 재관측에 강등 안 됨).
이 반복-상승이 omp `evidence_count` 의 light 채널판이고, heavy 게이트로 잇는 신호다:
`convention/` 노트가 **`confidence: high`** 에 도달 = 그 패턴의 `OBS` 가 `evidence_count ≥ 3` 에
근접했을 가능성 = `scholar-learn` 이 볼 만한 시점. confidence 는 정성 3등급(+관측횟수)일 뿐 —
**수치 가중합·threshold 매직넘버 없음.** 예:

```markdown
---
confidence: high
sightings: 3
---
# IROS reject patterns
## 2026-05-20 — ablation 누락 반복 지적 (3번째 관측 → high)
...
```

---

## `wiki_query(category)` 추상 함수 계약

```
wiki_query(category) → 매칭된 .md 발췌 목록 (없으면 빈 목록)
```

- **현재 구현**: 작업 대상 프로젝트의 `.oms/wiki/<category>/` 하위에서 **결정론적 grep**(키워드 매칭, CJK bi-gram 포함). 호출자(inspector·planner)가 venue·논문 유형·사용자 성향 키워드로 grep해 관련 발췌를 끌어온다. category 는 4개(`convention`·`pattern`·`decision`·`reference`) 중 하나. (디렉토리 부재면 빈 목록 — 신규 프로젝트는 빈 store에서 시작.)
- **호출부와 구현부 경계 (미래 교체점)**: inspector는 `wiki_query`라는 *추상 함수*를 호출할 뿐, 그 구현이 grep인지 자립 MCP인지 모른다. 나중에 자립 wiki MCP를 도입하면 **이 함수의 구현만 grep→MCP로 교체**하고 호출부(inspector pre-commitment)는 바꾸지 않는다.
- **부재 graceful degrade**: store가 비었거나 디렉토리가 없으면 빈 목록을 반환 — 에러가 아니다. inspector는 자체 예측만으로 진행한다.

---

## 이 store가 *새로* 수집하는 데이터 (net-new — 마이그레이션 아님)

reject 사유·결함 패턴은 **net-new 데이터**다. 기존 `references/formats/venues.md`(또는 venue 카드)는 `page_limit`·`sections`·`quality_threshold`만 있고 *reject 필드가 없다* — 따라서 이 wiki는 venue 카드에서 마이그레이션하는 게 아니라, inspector 세션이 비평하면서 *새로 수집해* 적재한다.

적재 주체 = **scholar-pilot의 wiki capture 단계가 자동으로** (verify 직후, terminal 전 — `scholar-pilot/SKILL.md` Step 10). inspect/verify가 이번 세션에 발견한 reject 패턴을 `convention/<venue>-reject-patterns.md`에 append. 단독 단계 실행 시엔 호출자가 직접 적재할 수도 있다. **자동이 기본** — 이것이 위 양방향 루프의 쓰기 절반이다. 사용자 `--no-wiki`면 skip. append-only·grep으로 중복 선확인·빈 세션이면 통과·추측 적재 금지(실제 발견한 것만).

---

## ⚠️ citation 안전 경계 (필수 — 위반 시 OMS 정체성 붕괴)

- **wiki 내용은 *2차 메모*일 뿐 — 1차 인용 출처로 절대 쓰지 않는다.** .bib 갱신은 scholar-research가 검증한 1차 출처로만(citation 안전 3원칙 유지). wiki에 적힌 논문 언급을 인용으로 끌어오지 않는다.
- **조회는 결정론적 키워드 매칭만 — 임베딩 검색 영구 금지.** grep(현재) 또는 미래 MCP 모두 결정론적 매칭이어야 한다. 임베딩 유사도 검색은 환각 인용을 끌어오므로 **현재도 미래도 금지**(불변 제약).
- wiki는 *예측을 돕는 메모*지 *사실의 출처*가 아니다. inspector는 wiki 발췌를 `[wiki]`로 출처 표시해 자체 예측(`[자체예측]`)과 구분한다.
- ⚠️ **light→enforce 직승 금지** (H6 backport, `learning-protocol.md` §6.D): wiki 노트(confidence high 여도)는 *조언*일 뿐 강제 기본값이 아니다. venue 기본값으로 굳히려면 반드시 `learned.md` 의 heavy 채널을 거쳐 **사람 게이트**를 통과해야 한다. confidence 가 아무리 높아도 wiki 가 직접 venue 기본값을 바꾸지 않는다. 특히 `pattern/`(성향)은 영구히 light — 승격 대상이 아니다.
