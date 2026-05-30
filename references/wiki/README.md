# references/wiki — 세션 넘어 누적되는 2차 메모 store

inspector의 pre-commitment(본문 읽기 전 reject 예측)가 *이전 세션이 누적한* 패턴을 조회하는 곳이다. 이 store는 **세션 휘발 데이터를 "랩 표준"으로 compound**하기 위한 영속 메모.

`wiki_query(category)` 추상 함수의 현재 구현 대상이며, 비어 있거나 부재해도 동작이 깨지지 않는다(inspector가 자체 예측으로 진행).

---

## 디렉토리 레이아웃

```
references/wiki/
  convention/   *.md   ← venue별 reject 사유·양식 규칙 (inspector가 조회)
  decision/     *.md   ← 과거 결정 기록 (왜 이 baseline·이 비교군을 택했나)
  reference/    *.md   ← 외부 자원 포인터 (venue CFP·평가 rubric 링크)
```

- 파일 1개 = 한 주제 (예: `convention/neurips-reject-patterns.md`).
- 각 파일은 사람이 읽는 자유 형식 .md. 머신 파싱 스키마 없음(grep만 함).
- `category`는 위 3개 하위 디렉토리 이름과 1:1.

---

## `wiki_query(category)` 추상 함수 계약

```
wiki_query(category) → 매칭된 .md 발췌 목록 (없으면 빈 목록)
```

- **현재 구현**: `references/wiki/<category>/` 하위에서 **결정론적 grep**(키워드 매칭). 호출자(inspector)가 venue·논문 유형 키워드로 grep해 관련 발췌를 끌어온다.
- **호출부와 구현부 경계 (미래 교체점)**: inspector는 `wiki_query`라는 *추상 함수*를 호출할 뿐, 그 구현이 grep인지 자립 MCP인지 모른다. 나중에 자립 wiki MCP를 도입하면 **이 함수의 구현만 grep→MCP로 교체**하고 호출부(inspector pre-commitment)는 바꾸지 않는다.
- **부재 graceful degrade**: store가 비었거나 디렉토리가 없으면 빈 목록을 반환 — 에러가 아니다. inspector는 자체 예측만으로 진행한다.

---

## 이 store가 *새로* 수집하는 데이터 (net-new — 마이그레이션 아님)

reject 사유·결함 패턴은 **net-new 데이터**다. 기존 `references/formats/venues.md`(또는 venue 카드)는 `page_limit`·`sections`·`quality_threshold`만 있고 *reject 필드가 없다* — 따라서 이 wiki는 venue 카드에서 마이그레이션하는 게 아니라, inspector 세션이 비평하면서 *새로 수집해* 적재한다.

적재 주체 = inspector를 호출한 사람/세션이 비평 산출에서 "이 venue에서 반복되는 reject 패턴"을 발견하면 `convention/<venue>-reject-patterns.md`에 한 줄 추가. (자동 적재 강제 아님 — 누적은 선택.)

---

## ⚠️ citation 안전 경계 (필수 — 위반 시 OMS 정체성 붕괴)

- **wiki 내용은 *2차 메모*일 뿐 — 1차 인용 출처로 절대 쓰지 않는다.** .bib 갱신은 scholar-research가 검증한 1차 출처로만(citation 안전 3원칙 유지). wiki에 적힌 논문 언급을 인용으로 끌어오지 않는다.
- **조회는 결정론적 키워드 매칭만 — 임베딩 검색 영구 금지.** grep(현재) 또는 미래 MCP 모두 결정론적 매칭이어야 한다. 임베딩 유사도 검색은 환각 인용을 끌어오므로 **현재도 미래도 금지**(불변 제약).
- wiki는 *예측을 돕는 메모*지 *사실의 출처*가 아니다. inspector는 wiki 발췌를 `[wiki]`로 출처 표시해 자체 예측(`[자체예측]`)과 구분한다.
