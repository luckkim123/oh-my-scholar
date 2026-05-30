---
name: scholar-learn
description: |
  관찰 → venue 기본값 승격 (oms의 핵심 진화 게이트) — 운영 중 `.oms/learned.md`에 쌓인 관찰과
  `.oms/wiki/`의 자동 누적 패턴을 scholar-inspector가 read-only로 검토해, 어느 것이
  `references/venues.md`의 강제 기본값(required sections·ordering·self-cite 상한 등)으로 승격될
  자격이 있는지 판단한다. 무거운 채널(기본값)은 반드시 사람 승인 게이트를 거치고, 승격될 때마다
  venue specificity가 올라가 "범용 → 이 사용자 특화"가 한 칸 진행된다. 자동 승격 없음 — 사람이
  게이트를 끊는다. citation/.bib 승격 영구 금지.
  Triggers: 학습 반영, 규칙 승격, 관찰 정리, learned 검토, 패턴 굳혀, 이거 기본값으로,
  scholar learn, promote observation, learn venue defaults, specificity 올려, 진화 게이트
---

# scholar-learn — 관찰 → venue 기본값 승격 (핵심 진화 게이트)

<Purpose>
oms의 비대칭 — "배포 시 범용, 쓸수록 이 사용자에게 특화" — 이 *강제까지 닫히는* 단계. 운영 중
`.oms/learned.md`에 쌓인 관찰(예: "IROS 논문엔 항상 Ablation 섹션 — 3회 반복")을
scholar-inspector(read-only)가 읽고, 어느 관찰이 `references/venues.md`의 **강제 기본값**으로
승격(promote)될 자격이 있는지 판단한다. 승격은 이후 모든 그 venue 작업의 *기본 가정*을 바꾸는
**한 방향 래칫**(잘못 승격되면 outline이 매번 틀린 섹션을 깔고, verify가 거짓 경고)이라 항상 사람
승인 게이트를 거친다. 승격마다 venue의 `specificity`가 0(순수 템플릿)→1(완전 특화) 쪽으로 오른다.
scholar-inspector는 **판단만** 한다 — 기본값을 직접 쓰거나 강제하지 않으며, 사람이 게이트를 끊은
뒤에야 이 스킬이 디스크에 반영한다. 동역학의 정본은 `references/learning-protocol.md`.
</Purpose>

<Use_When>
- 운영 중 `.oms/learned.md`에 관찰이 충분히 쌓여 "이제 venue 기본값으로 굳힐까?"를 판단할 때
- 같은 패턴(섹션·순서·self-cite 상한)이 반복 관측돼 강제 기본값으로 올리고 싶을 때
- 사용자가 "앞으로 IROS는 항상 X" 라고 명시했고(=user_stated) 그걸 venue 기본값으로 굳힐 때
- venue specificity를 올려 oms가 이 사용자에게 더 특화되길 원할 때
- scholar-pilot이 운영 루프 중 "승격 후보 N건 쌓임" 알림을 띄웠을 때
</Use_When>

<Do_Not_Use_When>
- `.oms/learned.md`가 비어 있으면 → 아직 승격할 관찰이 없다. 운영하며 inspect/verify가 채운다.
- 가벼운 패턴·성향·결정 메모일 뿐 강제 기본값까지는 아니면 → 승격하지 말고 `.oms/wiki/`에 자동
  누적되게 둔다(게이트 불필요, 다음 세션 grep 회수). 특히 `wiki/pattern/`(성향)은 영구히 light —
  절대 승격 대상 아님. 모든 관찰이 기본값이 되는 게 아니다.
- ⚠️ **citation·.bib·"이 논문 인용" 류라면 → 영구히 승격 금지** (`learning-protocol.md` §6.F).
  candidate_default.target에 citation/bib가 오면 스키마에서 거부. 인용은 paper-slug의 .tex/.bib
  SSOT에만 산다.
- 논문 *품질 검증*(PASS/FAIL)이라면 → `scholar-verify`. learn은 기본값을 *만들고*, verify는
  *판정*한다 — 다른 lane.
- 초안을 *쓰는* 거라면 → `scholar-draft`. learn은 파일 내용을 안 만든다(메타 학습만).
</Do_Not_Use_When>

<Execution_Policy>
- ⚠️ **사람 승인 게이트 절대 강제 (핵심)** — scholar-inspector는 승격 *제안*만 낸다. 어떤 관찰도
  사람 승인 없이 `venues.md`에 자동 반영되지 않는다. 자동 통과 없음. confidence·evidence가 아무리
  높아도(§6.B). 잘못 승격된 기본값 1개의 비용(매 작업 거짓 가정) > 놓친 기본값 1개의 비용(다음
  learn에서 다시 올림).
- ⚠️ **승격 기준은 AND (learning-protocol.md §3)** — 반복 `evidence_count ≥ 3` + 반례 0 +
  user_overridden 아님 + 안정 + 모순 없음. **전부** 충족해야 사람 게이트行. 점수 합산 아님.
  - ⭐ **user_stated 예외 (review #1 해소)**: 사용자가 직접 말한 규칙(`user_stated: true`)은
    evidence 1이어도 반복 바를 건너뛰고 게이트로 — 사용자가 직접 말한 = 이미 의도. 단 **게이트는
    여전히 거친다**(어느 scope? 기존과 모순?). 자동 강제는 여기서도 금지.
  - ⭐ **3회 바는 매직넘버가 아니다 (review #2 해소)**: omp §3.1이 "convention vs coincidence
    최소선"으로 정당화한 값. learning-protocol.md §3.1을 그대로 따른다.
- ⚠️ **scope 구분 (oms 특유 — omp엔 없음)** — 승격은 항상 scope에 묶인다: `global`(이 사용자
  보편 습관) vs `<venue-key>`(그 venue 한정). "Ablation 항상"이 IROS엔 맞고 thesis엔 아닐 수
  있다. inspector는 각 candidate의 scope를 명시하고, specificity는 scope별로 따로 계산.
- ⚠️ **2채널 분리 존중** — *무거운 채널*(기본값: learned.md → 승격 → venues.md)만 이 스킬의
  대상이고 게이트를 거친다. *가벼운 채널*(패턴/성향/결정: `.oms/wiki/*.md` 자동 append)은 게이트
  불필요 — 손대지 않고 읽기만. `wiki/pattern/`(성향)은 영구 light.
- ⚠️ **provenance 강제** — 승격되는 각 기본값은 근거 learned.md 관찰 id를 venue의
  `learned_refs[]`에 기록. 출처 없는 기본값 = 추측 = silent 변경(§6.C 위반).
- ⚠️ **specificity는 정직하게** — 항목 삭제 시에도 재계산(silent 변동 금지, §4 monotonic +
  deletion 규칙). 더 특화돼 보이려 부풀리지 않는다.
- **판정 ≠ 승인 ≠ 강제 (self-approval 3중 금지, review #4 해소)** — scholar-inspector는
  read-only로 승격을 *판정*만 하고(같은 컨텍스트에서 자기 판정을 승인하지 않음), scholar-learn은
  사람 게이트 통과분을 *디스크에 쓰기*만 하며(판정 안 함), 준수 *검증*은 별도 컨텍스트의
  scholar-verify 몫. 세 역할이 분리된다.
- **diff로 제시** — 기존 venues.md가 있으므로 inspector는 전체가 아니라 *delta*(Added/Changed
  기본값)로 제안해 사람이 변경분만 검토하게 한다.
- 학습 채널·승격 기준·specificity 공식의 정본은 `references/learning-protocol.md`,
  venue 스키마는 `references/venues.md`, wiki 규약은 `references/wiki/README.md`가 SSOT.
</Execution_Policy>

<Steps>
1. **SSOT·전제 확인**: 작업 루트와 `.oms/learned.md`가 있는지 확인. 비었으면 중단하고 "승격할
   관찰이 없다 — 운영하며 inspect/verify가 채운다"고 안내. 다음을 읽는다:
   - `.oms/learned.md` — 승격 대기 관찰 (이 스킬의 입력)
   - `references/venues.md` — 진화시킬 기존 venue 기본값 (blind 교체 아니라 *evolve*)
   - `.oms/wiki/convention/*.md` — 가벼운 채널. confidence high 신호가 쌓였나 grep(읽기만)
   - `references/learning-protocol.md` — 2채널·승격 기준·specificity 공식 (정본)
2. **관찰 분류 (2채널 판별)**: learned.md의 각 관찰을 (a) venue 기본값 승격 후보(무거운 채널 —
   게이트 대상) vs (b) 패턴/성향 메모(가벼운 채널 — wiki로 두고 게이트 불필요)로 가른다. 모든
   관찰이 기본값이 되는 게 아니다 — learning-protocol.md 채널 기준 적용. citation/.bib류는 즉시
   배제(§6.F).
3. **승격 후보 1차 선별 (증거 바)**: 무거운 채널 후보 각각에 §3 기준 적용 — evidence_count ≥ 3
   (또는 user_stated:true면 1) + 반례 0. 넘으면 "승격 제안", 애매하면 "held candidate". 근거
   수집까지가 컨트롤러 몫, 최종 판정·draft는 다음 단계 agent에 위임.
4. **agent 위임 (승격 판정 — read-only)** — scholar-inspector에 단일 위임. fresh subagent로
   컨트롤러 컨텍스트 오염 방지. 하나의 신중한 합성이므로 **병렬 inspector 금지**:

   ```
   Task(
     subagent_type="oh-my-scholar:scholar-inspector",
     description="scholar-learn: judge learned.md observations for promotion into venues.md",
     prompt="""
     역할: scholar-learn 승격 판단. 아래 .oms SSOT를 읽고, learned.md 관찰 중 어느 것이
     venues.md 강제 기본값으로 승격될 자격이 있는지 판단해 **제안(diff)** 을 내라. 너는
     read-only다 — venues.md를 직접 쓰지 말고, 준수를 판정하지 마라. 사람 승인 게이트가
     네 제안과 디스크 사이에 있다.

     입력 (읽을 것):
     - .oms/learned.md                # 승격 대기 관찰 (scope·evidence·반례·user_stated 포함)
     - references/venues.md           # 진화시킬 기존 기본값 (evolve, not replace)
     - .oms/wiki/convention/*.md      # 가벼운 채널 confidence 신호 (읽기만)
     - references/learning-protocol.md # 2채널·승격 기준 §3·specificity 공식 §4 (정본)

     지시:
     - 승격 기준은 AND(§3): evidence_count ≥ 3 + 반례 0 + user_overridden 아님 + 안정 + 모순 없음.
       단 user_stated:true 후보는 evidence 1이어도 게이트로(반복 바 면제, §1.feedback.2). 자동 강제 금지.
     - 각 candidate의 scope(global | <venue-key>)를 명시. specificity는 scope별 계산.
     - 승격되는 각 기본값은 근거 learned.md 관찰 id를 learned_refs[]에 기록(provenance).
     - specificity를 §4 공식으로 정직하게 재계산(부풀리지 말 것). 항목 삭제도 재계산 이벤트.
     - 전체 파일이 아니라 venues.md 대비 **diff**(Added/Changed 기본값)로 제시.
     - ⚠️ citation/.bib/특정 인용 target은 승격 후보에서 거부(§6.F).
     - 출력: 승격/held 결정 + scope + provenance 표 + specificity 근거 + 사람 결정 목록.
       venues.md를 쓰지 말고 제안만. self-approve 금지(판정 ≠ 승인 ≠ 검증).
     """
   )
   ```

   ━━━ **GATE (핵심 승격 게이트 — human)**: inspector의 diff·scope·provenance·specificity 근거를
   사람에게 제시하고 결정을 받는다 — promote(승인) / hold(보류) / edit(일부만) / abort.
   **자동 통과 절대 없음.** user_stated held candidate를 사람이 "올려"라고 하면 여기서 결정. ━━━
5. **승인분 반영 (게이트 통과 후에만)**: 사람이 승인한 기본값만 이 스킬이 디스크에 쓴다.
   - **먼저** 기존 venue 값을 스냅샷(작업장 versions/, `output-layout.md` work layer 규약 따름 —
     승격은 한 방향 래칫이라 롤백 지점). retention: 최신 N개만 남기고 trash 경유 prune(영구 rm 금지).
   - `references/venues.md`(또는 프로젝트 `.oms/venues/<key>.yaml`) — 승인된 기본값 추가/변경,
     `learned_refs[]`에 출처 관찰 id, `origins`에 해당 항목 `learned` 표시, scope별 `specificity`
     재계산. (스키마 부합 재확인.)
   - 페어 사람-narrative 동기(있으면) — venue 설명이 바뀌면 같은 패스에서 갱신(drift 방지, §6.C).
   - `.oms/learned.md` — 승격된 관찰은 "promoted → venues.md (date)"로 마킹, held는 candidate
     유지(다음 learn 재평가).
6. **후속 안내**: 기본값이 바뀌었으므로 다음 그 venue 작업부터 scholar-outline이 새 기본값을 깐다고
   안내. scholar-verify의 venue 메타 정합 점검(H10)으로 specificity↔origin 일관을 확인하라고 안내.
   learn 자체는 논문 내용을 안 만진다.
</Steps>

<Output>
- scholar-inspector의 **승격 제안 diff**(Added/Changed 기본값) + scope + provenance 표(각 기본값 →
  learned.md 관찰 id) + specificity 변화 근거 + 사람 결정 목록.
- GATE 결정 이력(promote/hold/edit/abort).
- 게이트 통과 시: 갱신된 `venues.md`(learned_refs[]·origins·specificity) + 마킹된 learned.md 경로.
- held candidate 목록(다음 learn 재평가) + "scholar-verify 메타 정합 점검 권장" 안내.
- inspector는 self-approve 안 함 명시 — 승격은 사람 게이트가 끊었고, 준수 판정은 별도 컨텍스트
  (scholar-verify)의 몫. citation/.bib는 승격 대상이 아니었음을 확인(§6.F).
</Output>

<Citation_Safety>
⚠️ oms 정체성의 핵심 불변. scholar-learn은 **절대** 다음을 하지 않는다:
- citation·.bib 엔트리·"이 논문을 인용한다" 류를 venue 기본값으로 승격 (target enum 거부, §6.F).
- 임베딩/유사도 검색으로 관찰을 회수 (결정론적 grep만, §6.A).
- 날조 evidence로 ≥3 바를 채움 (실제 paper-slug/이벤트만, §6.E).
승격 대상은 *구조·순서·양식·작업방식 사양*뿐. 인용은 학습되지 않는다.
</Citation_Safety>
