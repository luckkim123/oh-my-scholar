# Writing-Craft Card — 논증·서술 규칙 (FLOW·TONE·LOGIC·STRUCTURE)

> oms 의 글쓰기 craft SSOT. scholar-drafter(생성)·scholar-inspector(prose/logic 비평)·scholar-verifier(§7 WARN 검출)가 이 카드를 *참조*한다. **중복 임베드 금지 — 규칙을 각 agent 에 재나열하지 말고 항상 이 파일을 가리킨다** (drift 방지, abstract-WARN 선례와 동일 규율).
>
> **역할 분리**: `latex.md` = *어떻게 조판*(컴파일·수식·`\tag`·섹션 모듈화) ⊥ 이 카드 = *어떻게 논증·서술*(흐름·어투·논리·구조). 둘은 겹치지 않는다.
>
> 각 규칙은 **출처 anchor**를 단다. ⚠️ 출처 honesty: Gopen-Swan·Schimel·Pinker 규칙 일부는 2차 요약 경유 — *drafter 규칙*으로 채택(인용 주장 아님)이라 무방하나, oms 산출 논문에 verbatim 인용 시 원본 대조. citation/.bib 는 이 카드의 승격 대상 아님(영구 금지).

---

## §1. FLOW — 흐름 (최우선; "전개가 어색하다"의 핵심)

- **old→new (Gopen-Swan, 흐름 최상위 규칙)**: 각 문장은 독자가 *이미 아는 정보(구정보)*로 시작하고(topic position), *새/강조 정보*는 문장 끝(**stress position**, 마침표·세미콜론 직전)에 둔다. 흐름이 어색하면 거의 항상 이 위반 — 신정보가 문장 머리에 와서 뒤-연결이 끊긴 것. ⚠️ **이 규칙은 능동태 선호보다 *상위 우선순위***: 구정보를 앞에 두기 위해 필요하면 수동태 허용. [Gopen & Swan 1990]
- **주어-동사 근접**: 문법 주어 뒤 가능한 빨리 동사를 둔다. 주어-동사 사이를 긴 삽입구로 끊지 마라(buried predicate 금지). [Gopen-Swan]
- **action-in-verb (anti-nominalization)**: 절의 행위를 명사화하지 말고 동사로. `we performed an analysis of`→`we analyzed`, `provides a review of`→`reviews`. [Gopen-Swan / Sainani]
- **맥락 먼저**: 새 주장·새 용어를 요구하기 전에 맥락을 한 문장 앞세운다. [Gopen-Swan]
- **banana rule**: 핵심 용어(기법명·변수·그룹명)는 *정확히 같은 단어*로 반복한다. 동의어로 변주하지 마라 — 변주하면 독자가 새 개념인 줄 안다. ("바나나를 '길쭉한 노란 과일'이라 부르지 마라.") [Sainani]

## §2. TONE — 어투 (AI slop 제거)

- **장식 동사·형용사 금지 (원리, 목록 아님)**: 실제 의미 payload 가 없으면 쓰지 않는다. 테스트 = "이 동사/형용사가 *내용*을 더하나, *장식*인가?". 씨앗 토큰: delve, underscore, showcase, foster, leverage, intricate, pivotal, crucial, comprehensive, meticulous, realm, tapestry, testament. ⚠️ 정적 목록은 부패하므로(저자들이 'delve' 회피 시작) *원리*를 강제하고 목록은 §7 검출 씨앗으로만. [Nature Human Behaviour 2025 — LLM 잉여어휘 66% 동사·14% 형용사 / humanizer]
- **copula 회피 금지**: `is`를 `serves as`/`stands as`/`boasts`/`features`로 바꾸지 마라. [humanizer]
- **em-dash 캡**: em-dash(`—`)는 절제가 아니라 거의 금지 — 마침표·쉼표·콜론·괄호로 대체하거나 문장 재구성. 한 섹션당 최대 1-3개. [humanizer / anti-ai-slop]
- **구조 slop 금지**: rule-of-three 강제, 동의어 cycling, 연속 3문장 동일 길이(문장 길이 변주하라), 부정 병렬("It's not just X, it's Y"), `-ing` 분사 padding. [anti-ai-slop]

## §3. LOGIC — 논증 구성

- **one ping**: 논문 1개 = sharp idea 1개, 본문에 **명시적으로** 진술("The main idea of this paper is…"). 독자에게 추측시키지 마라. 아이디어 여러 개면 논문 여러 개. [Peyton Jones]
- **반증가능 기여 bullet**: 기여를 Intro 앞에 **반증가능(refutable) bullet**로. NOT "We describe a cool system"; YES "We prove X (Section 4)". 이 bullet 리스트가 논문 전체를 끌고 간다. 문제는 grand claim 아닌 예시로(molehills not mountains). [Peyton Jones]
- **forward-reference**: 각 기여 bullet 은 그 증거를 forward-reference(Section X)한다. ⚠️ "The rest of this paper is structured as follows…" 금지 — 기여 bullet 의 forward-reference 가 그 역할을 대신. [Peyton Jones]
- **TEEL 문단**: 본문 문단 = Topic sentence(요점 먼저) → Evidence(데이터·인용) → Explanation(해석) → Link(다음 논지로). [academic-research-skills]
- **과대일반화(overgeneralization) 경고 — 최대 실패모드**: 인용 근거보다 넓은 주장이 LLM 의 #1 hallucination(실증 51%, 발명된 논문보다 흔함). 주장의 폭을 그 근거의 폭에 맞춘다. [AutoSurvey 오류분류]
- **LLM 학술글쓰기 추가 실패모드 (drafter 가 빠지는 함정)**: 외부가 문서화한 실패모드 중 위 과대일반화 외에 별도로 경계할 것 — ① **수치 hallucination**(그럴듯하나 source data 와 불일치하는 통계·수치) → 모든 정량 주장은 결과 노트에 대조 ② **method 일반화**(구체 구현 대신 표준 method 를 기술) → method 절은 *이* 시스템의 실제 구현을 쓴다. (③ 용어 혼동 = 관련 용어를 호환 취급은 §1 banana rule 의 이면 — 거기로.) ⚠️ blog 출처(drafter 규칙으로 채택, 인용 주장 아님 — §출처 honesty). [manuelcorpas 2026-01 / 전역 wiki reference]

## §4. STRUCTURE — 논문·섹션 구조

- **CARS 3-move (Intro 필수 골격)**: Move 1 영역 확립(territory) → **Move 2 틈 확립(niche/gap)** → Move 3 틈 점유(occupy: 목적·기여·구조). ⚠️ **Move 2(틈)를 절대 건너뛰지 마라** — 주제(territory)만 말하고 gap 을 명시 안 하면 reject 1순위. funnel = CARS 의 형식화(일반 영역→좁히는 틈→구체적 현 연구). [Swales CARS]
- **OCAR 아크**: Opening → Challenge → Action → Resolution 이 기본 저널 아크. 각 레벨(논문·섹션·문단)이 자기 아크를 가진다(중첩). 넓은 청중(Nature/Science)은 LD/LDR(핵심을 앞에 적재) — 아크는 독자 인내심으로 선택. [Schimel]
- **모래시계 폭 일치**: Opening(Intro 도입 폭)과 Resolution(Conclusion/Discussion 폭)이 일치해야 — 불일치 = 과대약속/과소이행 신호. Discussion 은 Intro 의 거울(역funnel: 구체 결과→넓은 함의). [Schimel]
- ⚠️ **venue 변주 (하드코딩 금지)**: related-work 위치(Peyton Jones "끝" ↔ CARS/저널 "앞")·아크 선택(OCAR↔LD)은 venue 카드로 파라미터화한다 — 한 방식을 하드코딩하지 마라. (planner `<Structure_Types>` 의 규모 축과 *직교* — 이 카드는 수사 구조 축.)

## §5. VOICE/VENUE — 태/venue

- **voice 우선순위**: discipline norms (hard) > journal conventions (strong) > personal style (soft). 분야 규범 > 저널 관례 > 개인 문체. 저자 voice 는 분야 규범을 넘지 못한다. [academic-research-skills]
- **태 선택**: STEM 논문에서 method 기술은 수동태 허용, *기여(contribution) 서술은 능동태*. (단 §1 old→new 가 상위 — 흐름을 위해선 수동 허용.) [academic-research-skills]

## §6. EXEMPLAR — 스타일 모방

- **~5개 무작위 대표 문단**: 목표 venue/저자의 실제 문단 ~5개를 verbatim exemplar 로 프롬프트에 주입한다. ⚠️ **유사도-curated 선택 금지(역효과 실증) — *무작위 대표* 표본**. ~5개 초과 금지(plateau). **embedding/임베딩 검색 영구 금지**(oms anti-embedding 정합). venues.md 의 `voice`/`exemplars` 필드로 공급. [EMNLP 2025 style-imitation; introduction few-shot 도 3-shot 후 plateau 재확인 — arXiv:2508.14273 (self-verified)]

## §7. 기계 체크 토큰 (verifier WARN 검출 SSOT)

> verifier 가 이 토큰을 읽어 **WARN** 으로 검출한다(FAIL 아님 — venue 변주, abstract-WARN 선례와 동일 처리). 토큰을 verifier·테스트에 재나열하지 말고 여기를 SSOT 로 따른다.

검출 토큰 (1건 이상 = WARN, 0건 = PASS):
- **장식어**: §2 씨앗 목록(`delve`·`underscore`·`showcase`·`foster`·`leverage`·`intricate`·`pivotal`·`crucial`·`comprehensive`·`meticulous`·`realm`·`tapestry`·`testament`) — 단어 경계 매칭. ⚠️ WARN 이라 과검출 허용(문맥상 정당한 `crucial` 1개는 사람 확인).
- **em-dash**: 유니코드 `—`(U+2014)·`–`(U+2013) 출현 수 > 섹션당 3 = WARN.
- **rule-of-three**: 콤마로 묶인 3항 병렬이 한 문단에 반복(`A, B, and C` 패턴 다발) — heuristic, WARN.
- **부정 병렬**: `not just .* but` / `not only .* but also` 다발 — WARN.

⚠️ **멀티바이트 grep 거짓음성 (확인된 함정)**: em-dash(`—`)·`×`·`§`·`≤` 같은 멀티바이트 글리프는 C-locale `grep`/`grep -P` 에서 거짓 0건이 난다. **잔여 0건 확정은 Python `re` 모듈로만 신뢰**(`LC_ALL=C grep` 단독 신뢰 금지). abstract-WARN(latex.md §3)이 같은 caveat 을 따른다.

---

## 비목표 (의도적으로 안 함)

- **embedding 기반 exemplar 검색** — oms anti-embedding 원칙 위배 + EMNLP 2025 가 유사도-curated 역효과 실증. §6 무작위 대표로 대체.
- **Manchester phrasebank 텍스트 bulk-copy** — IP. taxonomy(move×function)만 차용, 예시는 자체 작성/인용.
- **글쓰기 규칙 auto hard-FAIL** — 정적 blocklist 부패 + 멀티바이트 거짓음성 위험. 글쓰기 검출은 WARN/formative 로만, 자동 FAIL 아님.
