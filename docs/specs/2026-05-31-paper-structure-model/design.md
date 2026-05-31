# Paper Structure Model — scholar-planner 고도화 (2026-05-31)

## 문제

학위논문(POSTECH 석사, ASV-ROV)을 `scholar-outline`으로 outline 시켰더니 **"기술 백서"** 구조가
나왔다: 방법을 여러 섹션(§3·4·5)에 나열하고 **모든 실험을 끝의 한 챕터(§8)에 몰아넣음**. 사용자가
"누가 봐도 논문스럽지 않다"고 지적.

## 근본 원인 (oms 하네스 결함)

- `scholar-planner`에 **단일 평면(flat) 구조 모델만** 있었다. word budget 가이드(L43)가
  "Intro / Related Work / Method / Experiments / Conclusion" = *컨퍼런스 논문 한 편*의 IMRaD를 가정.
- multi-chapter / 다중 기여 / 시스템 논문 구조 모델이 **없음** → 어떤 학위논문·시스템 논문을 줘도
  컨퍼런스식으로 평면화.
- `references/venues.md`의 thesis 예시에 구조 정보(`structure_type`·`sections`)가 **비어 있어**
  planner가 참조할 게 없었다 → 내부 default(flat)로 떨어짐.
- → **범용 규칙 공백** (iCloud workspace 특수성 아님). 배포 하네스(planner + venues.md) 수정이 정답.

## 문헌조사 (external-context 4 facet, 2026-05-31)

핵심 발견:
1. **모든 학술 논문은 하나의 공통 골격을 공유**한다 — IMRaD의 공학 변주
   `Introduction → (Related Work) → Method → Experiments → Conclusion`. IROS/ICRA/RA-L 전부 동일.
   구조가 venue마다 다른 게 아니라 *규모*(골격을 몇 번 반복·얼마나 펼치나)만 다르다.
2. **"Overview → Proposed → 자체 실험"은 thesis 전용이 아니라 method 논문 보편 패턴.** 섹션명에
   "Proposed"를 꼭 붙일 필요 없음(`Method`/`Approach`/`Technical Overview` 다 관습적).
3. **monograph(챕터 축적) ≠ thesis-by-papers(챕터 자체완결)** — 둘은 학위논문의 다른 하위형. 자체완결
   패턴은 by-papers의 것; monograph에 쓰면 redundancy. (초기 설계가 이 둘을 혼동했었음 → 정정.)
4. **T-RO 통합 시스템 논문**(우리 ASV-ROV에 가장 가까움): 기여별 독립 섹션 + 컴포넌트 검증은 각
   섹션 안 + **통합 실험은 후반 별도 섹션**(hybrid).

### 출처 (각 주장 anchor)

**method 논문 작성 방법론**:
- IMRaD 공학 변주: https://www.thesify.ai/blog/how-to-structure-a-scientific-research-paper-imrad-format-guide
- Simon Peyton Jones, "How to Write a Great Research Paper": https://www.microsoft.com/en-us/research/academic-program/write-great-research-paper/
- Whitesides' Group: Writing a Paper (Harvard): https://www.gmwgroup.harvard.edu/publications/whitesides-group-writing-paper
- Brown H2R Lab, Writing a Technical Paper (motivation-first, 실험 직후 결과): https://h2r.cs.brown.edu/writing-a-technical-paper/

**로보틱스 컨퍼런스/저널 구조**:
- Michael Milford, Structuring Robotics Conference Papers: https://michaelmilford.com/structuring-robotics-conference-papers/
- IEEE RA-L Information for Authors: https://www.ieee-ras.org/publications/ra-l/ra-l-information-for-authors/
- ICRA 2025 final paper instructions: https://2025.ieee-icra.org/contribute/final-paper-submission-instructions/
- RA-L 논문 구조 실측(arXiv): https://arxiv.org/html/2408.00337v1 ; ICRA 시스템 논문 실측: https://arxiv.org/html/2502.19591v1

**T-RO / 저널 long-form**:
- T-RO 논문 구조 실측(arXiv): https://arxiv.org/html/2403.05500
- IJRR author instructions: https://journals.sagepub.com/author-instructions/ijr

**학위논문 구조**:
- monograph vs sandwich (Elmqvist): https://niklaselmqvist.medium.com/monograph-or-sandwich-dissertation-ac8ca4eb2de
- York Graduate School, monograph thesis format: https://www.york.ac.uk/research/graduate-school/progression/thesis/format/monograph-guidance/
- Oxbridge Essays, PhD thesis structure: https://www.oxbridgeessays.com/blog/phd-thesis-structure-examples-chapter-guide/
- 학위논문 유형: https://master-academia.com/phd-thesis-types/

> ⚠️ citation-bound 작업 아님 — 이건 "논문을 어떻게 구조화하나"의 방법론 조사(out-of-band). 위 URL은
> 조사 시점 확인. 논문 본문 인용용 .bib가 아니다.

## 처방 (구현됨)

1. `agents/scholar-planner.md` `<Structure_Types>` **전면 재작성**: 이분법(flat/thesis-by-contribution)
   폐기 → **공통 골격 1개 + 규모 변주(flat / system / thesis)**. monograph vs thesis-by-papers 구분 명시.
   Investigation_Protocol step 2·3·4·5 + Success_Criteria 정합.
2. `references/venues.md`: `structure_type` 필드 = `flat | system | thesis`. IROS 예시 `flat`,
   POSTECH thesis 예시 `thesis`로 명시 + 챕터 골격 주석.
3. 회귀 가드 `tests/test_thesis_structure.py` (6 cases): 공통 골격·세 변주·기술백서 안티패턴·
   monograph/by-papers 구분·structure_type 필드·폐기용어 negative·범용성(고유명사 0). 전체 48 passed.

## 범용성 점검 (배포 repo 오염 방지)

- planner·venues.md 스키마에 **이 논문/이 사용자 고유명사 0건** (한때 '유선철 랩'을 박았다가 제거 —
  test_planner_has_no_project_specific_proper_nouns 가드). 개념·스키마는 100% 범용, 예시만 구체값.

## 함께 처리

- `06_outline.md` 하드코딩 prefix 제거 → `outline.md` (scholar-outline·scholar-planner 7곳). 의미 없는
  번호 충돌(개념노트 01~06과 겹침) 제거.
