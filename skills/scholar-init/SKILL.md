---
name: scholar-init
description: |
  새 논문 0단계 부트스트랩 — 폴더 위치·venue·한 줄 주제를 대화로 잡고(질문 ≤3개),
  표준 디렉토리 scaffold(sections/figures/refs/data) + `.oms/<slug>/` 작업장 + 논문별
  `.oms/wiki/`를 생성한다. 시작 시 **상위 폴더의 `.oms/wiki/`(전역 레벨, ascent로 발견)**를
  씨앗으로 참조해 "당신이 보통 쓰는 venue·구조"를 추천한다. 초안 scaffold·venue-config는
  사람 승인 게이트를 거쳐야 디스크에 기록 — 범용으로 출발해 즉시 이 논문/이 사용자에 특화된
  시작점. 이미 `.oms/<slug>/`가 있으면 "재초기화?" 경고 후 멈춘다. citation/.bib 생성·날조 없음(여긴 scaffold만).
  Triggers: 논문 시작, 새 논문, 논문 셋업, 논문 부트스트랩, 초기 디렉토리, scholar init, paper init,
  start a paper, bootstrap paper, initialize paper, 새 논문 쓸래, 논문 폴더 만들어
---

# scholar-init — 새 논문 0단계 부트스트랩 (대화로 잡고 → scaffold 생성)

<Purpose>
논문을 처음 시작할 때 단 한 번 돌리는 부트스트랩. 사용자와 짧은 대화로 (1)폴더 위치 (2)venue (3)한 줄 주제를 잡고, 표준 디렉토리 scaffold와 `.oms/<slug>/` 작업장·논문별 wiki를 만든다. 핵심은 **빈 손이 아니라 씨앗에서 시작**하는 것 — 시작 시 *상위 폴더의 `.oms/wiki/`*(전역 레벨)를 ascent로 찾아 "당신은 보통 IROS에 내고, 늘 이런 섹션 구조를 쓰죠"라는 추천을 끌어온다. 그래서 논문을 쓸수록(전역 wiki가 쌓일수록) 다음 논문의 시작이 빨라진다. 이것이 oms의 "범용→이 사용자 특화" 비대칭의 출발점이고, 형제 `omp-init`의 부트스트랩 패턴을 논문 도메인으로 이식한 것이다.

⚠️ 이 단계는 **scaffold(빈 골격)만** 만든다 — 논문 *내용*(.tex 본문·인용)은 일절 생성하지 않는다. citation-bound 생성은 이후 research→ideate→draft가 단일·신중하게 한다.
</Purpose>

<Use_When>
- 새 논문 폴더에 아직 `.oms/<slug>/`가 없고, oms로 논문 작업을 시작할 때
- "새 논문 쓸래 / 논문 폴더 만들어 / 논문 셋업" 같은 첫 진입
- `scholar-pilot`이 `.oms/<slug>/` 부재를 감지해 init을 흡수(권유) 호출할 때
</Use_When>

<Do_Not_Use_When>
- 이미 `.oms/<slug>/`가 존재 → 재초기화는 그 논문의 작업장·논문별 wiki를 날린다. 작업을 이어가려면 → `scholar-research`/`scholar-pilot`, 관찰을 venue 기본값으로 승격하려면 → `scholar-learn`.
- 관련연구 조사만 → `scholar-research`. 개념 정리만 → `scholar-ideate`. 섹션 구조만 → `scholar-outline`.
- 논문 본문 생성 → `scholar-draft` (init은 scaffold만, 본문 생성 안 함).
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **질문은 최소(≤3개)**: 첫 세션엔 (1)폴더 위치 (2)venue (3)한 줄 주제+기여만 묻는다. 방법론·세부 섹션 구조·관련연구는 묻지 말 것 — research/ideate 단계가 자연스럽게 추출한다(progressive disclosure). 6개를 한꺼번에 물으면 시작이 마찰이 된다.
- ⚠️ **읽기 우선·쓰기 게이트 후**: 폴더 스캔·전역 wiki read·scaffold 합성(dispatch)은 전부 read-only — 디스크 변경 0. 실제 scaffold/`.oms/` 기록은 GATE 1(사람) 통과 후 호출 컨텍스트(이 스킬)가 수행. self-approval 금지: scaffold를 합성한 dispatch가 같은 패스에서 그것을 승인·기록할 수 없다.
- ⚠️ **citation 안전**: init은 scaffold만 만든다. `.bib`에 인용 항목을 *생성*하지 않는다(빈 `paper.bib` 골격만). 전역 wiki 씨앗을 읽을 때도 wiki 내용은 *2차 메모*일 뿐 — 인용 출처로 쓰지 않는다(임베딩 검색 영구 금지, 결정론적 grep만). citation/.bib는 전역 wiki 승격 대상이 영구히 아니다.
- **`.oms/<slug>/` 존재 시 멈춤**: 첫 단계에서 검사. 있으면 즉시 멈추고 "이미 초기화됨 — 재초기화하면 그 논문 작업장·wiki 손실" 경고 + 사용자 명시 재확인을 받아야만 진행.
- **전역 wiki는 graceful**: 상위 폴더에 `.oms/`가 없으면 씨앗 없이 진행(에러 아님). 추천이 빈약할 뿐, init은 완결 동작한다.
- **`specificity` 정직하게**: 전역 wiki 씨앗을 많이 가져왔으면 venue-config specificity가 살짝 높게(0.1~0.4), 빈 손이면 0. 1로 부풀리지 말 것 — 진짜 특화는 `scholar-learn` 승격으로.
- **크로스플랫폼**: 모든 경로는 상대경로 또는 `Path.cwd()` 기준. 절대경로·`~` 하드코딩 금지(배포물 오염). 전역 wiki는 *상위 폴더의 `.oms/`*를 ascent로 찾아 — 절대경로가 아니다. ignore 시드: `.git/**`·`.oms/**`·`outputs/**`·LaTeX 빌드 산출물.
- **비ASCII 제목**: slug 규칙은 `references/output-layout.md` §1.1. 비ASCII 제목이면 ASCII slug를 1회 묻는다(자동 romanize 금지).
</Execution_Policy>

<Steps>
1. **`.oms/<slug>/` 존재 검사 (게이트 0)**: 의도한 논문 폴더에 `.oms/<slug>/` 또는 `meta.md`가 있으면 멈추고 경고 — "이미 초기화됨. 재초기화 시 이 논문 작업장·wiki 손실. 정말?" 사용자 명시 동의해야만 계속(기존 보존 권유). 없으면 다음으로.

2. **폴더 위치 (질문 ①)**: "어디에 둘까요? 추천: `<cwd>/<제안-slug>/`" — 사용자 확인 또는 다른 경로. slug = output-layout §1.1(비ASCII→ASCII 1회 질문). 확정 slug는 작업 수명 동안 불변.

3. **전역 wiki 씨앗 read (ascent, read-only)**: cwd에서 부모로 올라가 **가장 가까운 상위 `.oms/`**(자기 제외)를 찾는다(git의 `.git` 찾기 방식). 있으면 `wiki_query('pattern')`·`wiki_query('convention')`·`wiki_query('history')`로 "이 사용자가 보통 쓰는 venue·섹션 구조·표현 성향·과거 논문"을 끌어온다(결정론적 grep). 없으면 씨앗 없이 진행. (계약: `references/wiki/README.md`.)

4. **venue + 한 줄 주제 (질문 ②③)**: 전역 씨앗을 추천으로 제시 — "당신은 보통 IROS에 내셨죠 — IROS 2027로 갈까요? 섹션은 늘 쓰시던 구조로?". venue 미정이면 generic. 한 줄 주제 + 핵심 기여 1문장을 받는다(방법론 세부는 안 물음). 기존 자료 위치(Zotero/bib/PDF 폴더)가 있으면 경로만 기록.

5. **scaffold 합성 (dispatch, read-only)**: `scholar-planner`에게 위임 — 선택 venue 카드(`references/venues.md`) + 전역 씨앗을 입력으로 "이 논문의 초기 디렉토리 트리 + venue-config(yaml) + 논문별 wiki seed"를 **텍스트로 반환**(디스크 안 씀). venue-config는 venues.md 스키마 준수, `specificity`·`origins`는 전역 씨앗 반영분만 정직 기록. self-approve 금지.
   ```
   Task(
     subagent_type="oh-my-scholar:scholar-planner",
     description="Synthesize paper scaffold + venue-config draft",
     prompt="선택 venue=<key>, 전역 wiki 씨앗=<발췌>를 입력으로 references/venues.md 스키마에 맞는 "
            "venue-config 초안 + 디렉토리 scaffold 트리 + 논문별 wiki seed 를 합성. "
            "references/output-layout.md 구조 준수. specificity 정직(씨앗 반영분만). "
            "read-only — 디스크에 쓰지 말고 초안 텍스트만 반환. self-approve 금지(GATE 1은 사람)."
   )
   ```
   ━━━ **GATE 1 (핵심): 초안 승인 (human)** — proceed / revise / abort. 사람에게 폴더 위치·venue·디렉토리 트리·논문별 wiki seed·**어떤 전역 씨앗을 가져왔는지**·추정 specificity를 제시하고 결정을 받는다. 자동 통과 없음. revise면 5로 되돌아 재합성. ━━━

6. **scaffold 기록 (게이트 통과 후에만)**: 승인된 초안으로 `references/output-layout.md`의 구조대로 생성 —
   - 논문 소스 폴더: `sections/`(NN_*.tex 빈 골격) · `figures/` · `refs/paper.bib`(빈) · `data/` · `preamble.tex`(상위 전역 매크로를 `\input`하는 라인 — 상위 `.oms/`에 매크로가 있으면) · `<slug>.tex`(최소 골격) · `meta.md`(venue·주제·기여·자료위치 = 인터뷰 답)
   - `.oms/<slug>/`: output-layout의 작업장(versions/renders/gen-image/tmp는 빈 채 또는 생략)
   - `.oms/wiki/`: 논문별 wiki, 빈 4-카테고리(convention/pattern/decision/reference). ⚠️ `history/`는 **전역 전용** 카테고리(상위 `.oms/`에만 존재) — 로컬엔 만들지 않는다. Step 3의 `wiki_query('history')`는 ascent로 전역만 읽으며, 로컬에 없어도 graceful(빈 목록, 에러 아님).
   - venue-config: `.oms/venues/<key>.yaml` (oms_atomic 의 atomic write 경유 — json이면, yaml은 일반 write)
   - `.gitignore`: `.oms/`·`outputs/*` 제외
   > ⚠️ 본문·인용은 생성하지 않는다. .tex는 컴파일되는 최소 골격(documentclass + 빈 섹션 include)일 뿐.

7. **확인 리포트**: 생성된 경로 목록 + 가져온 전역 씨앗 요약 + venue + 초안 specificity + "다음 단계: scholar-research로 관련연구 조사 →" 안내. **상위 `.oms/`가 없었으면**: "전역 wiki(모든 논문 공통 자산)를 두려면 *논문들의 부모 폴더*에서 한 번 더 init하거나 그 폴더에 `.oms/wiki/`를 두세요" 안내(init이 부모에 임의로 만들지 않음 — 홈 오염 방지). init은 1회 부트스트랩이므로 여기서 종료(루프 진입 아님).

> **dispatch 실체**: 3·5의 read는 read-only 진단 — 디스크 변경 0. 실제 scaffold/`.oms/` 쓰기는 GATE 1 통과 후 6번에서만. pilot이 흡수 호출한 경우, init 종료 후 pilot이 research로 이어간다.
</Steps>

<Output>
생성된 scaffold 경로 전체(`sections/`·`figures/`·`refs/paper.bib`·`data/`·`preamble.tex`·`<slug>.tex`·`meta.md` + `.oms/<slug>/` + `.oms/wiki/` 4-카테고리 + `.oms/venues/<key>.yaml` + `.gitignore`) + 선택 venue + 가져온 전역 씨앗 요약(없었으면 "전역 wiki 부재 — 부모 폴더 init 안내") + 초안 specificity(정직한 시작값) + GATE 1 결정 이력 + 다음 단계(scholar-research). `.oms/<slug>/` 이미 존재 시: 경고 + 재초기화 미진행(또는 사용자 명시 동의 시에만)임을 명시. 게이트 통과 전엔 디스크에 아무것도 기록 안 했음을 보고. ⚠️ 본문·인용 생성 0(scaffold만).
</Output>
