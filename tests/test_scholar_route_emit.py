"""Tests for the paper-stage UserPromptSubmit routing hook.

핵심 계약: 매 턴 STAGE 판정을 응답 맨 앞에 출력하라는 contract 를 주입한다
(omha 의 🧭 ROUTE 줄과 같은 방식, 단 oms 는 도메인 처리기라 LANE 이 아닌
STAGE). citation 안전 문구 포함. stdlib only, fail-open."""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "scholar_route_emit.py"


def run_hook(payload: dict) -> str:
    """훅을 서브프로세스로 실행하고 stdout 반환."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def context_of(stdout: str) -> str:
    if not stdout.strip():
        return ""
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]


def test_emits_userpromptsubmit_context():
    """① UserPromptSubmit 이벤트로 라우팅 contract 주입."""
    out = run_hook({"prompt": "이 논문 introduction 초안 써줘"})
    d = json.loads(out)
    assert d["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


def test_context_states_stage_emit_contract():
    """② 매 턴 STAGE 한 줄 판정 contract 가 명시돼야 (omha ROUTE 와 동형)."""
    out = context_of(run_hook({"prompt": "verify this section"}))
    assert "STAGE(paper) →" in out
    assert "누락 금지" in out  # 매 턴 출력 의무


def test_context_lists_all_stages():
    """③ 13개 단계가 contract 에 모두 열거돼야 (skill 과 정합).

    deepen 은 scholar-deepen 스킬(research↔ideate 사이 모호성 게이트)이
    실재하므로 STAGE 카탈로그에 포함돼야 한다 (T14 에서 추가).
    learn 은 scholar-learn 스킬(관찰→venue 기본값 승격, 사람 게이트)이
    실재하므로 메타 단계로 포함돼야 한다 (H9 에서 추가).
    init 은 scholar-init 스킬(0단계 부트스트랩 — 새 논문 시작)이 실재하므로
    포함돼야 한다 (scholar-init 도입에서 추가).
    read/discuss 는 R5 T2/T3 의 scholar-read·scholar-discuss 스킬이 실재하므로
    보조 단계로 포함돼야 한다 (D7: 라우팅 enum 확장은 T3 한 번, 두 스킬 모두)."""
    out = context_of(run_hook({"prompt": "논문 작업"}))
    for stage in ("init", "research", "deepen", "ideate", "outline", "draft",
                  "inspect", "verify", "revise", "learn", "read", "discuss", "scholar-pilot"):
        assert stage in out, f"stage '{stage}' missing from contract"


def test_read_discuss_stages_described_in_checkpoint():
    """③-e R5 T3: read/discuss 보조 단계 설명이 STAGE 카탈로그 본문에도 등장해야
    (토큰 줄뿐 아니라 단계 설명 문단에도 — omha ROUTE 카드와 동형 규율)."""
    out = context_of(run_hook({"prompt": "논문 작업"}))
    assert "read(" in out
    assert "discuss(" in out
    assert ".hq/community/reading/" in out
    assert "자동 적용 금지" in out  # D9: outline 델타는 제안만, 자동 적용 금지


def test_init_stage_is_bootstrap_zero():
    """③-d init 0단계가 STAGE 토큰 줄과 안내문에 명시돼야 (scholar-init).

    새 논문 시작 = 부트스트랩이라는 의미와, 이미 .hq/work/scholar/<slug>/ 가 있으면
    init 이 아니라는 멱등성 단서가 라우팅에 박혀야 한다."""
    out = context_of(run_hook({"prompt": "새 논문 쓸래 폴더 만들어줘"}))
    assert "init" in out
    assert "부트스트랩" in out          # 0단계 의미
    assert ".hq/" in out                # 전역/로컬 .hq 언급
    # 이미 초기화된 폴더면 init 아님 (멱등성 단서)
    assert "있으면 init 아님" in out


def test_learn_stage_in_routing_token_line():
    """③-b learn 메타 단계가 STAGE 토큰 줄에 명시돼야 (H9)."""
    out = context_of(run_hook({"prompt": "이 관찰 venue 규칙으로 굳혀줘"}))
    assert "learn" in out
    # learn 은 메타 단계 — 자동 발동 아님(사람 게이트)이 명시돼야
    assert "사람 게이트" in out


def test_learn_routing_keeps_citation_guard():
    """③-c learn 추가가 citation 안전 가드를 깨지 않아야 (H9·§6.F)."""
    out = context_of(run_hook({"prompt": "promote observation to venue default"}))
    # citation/.bib 는 learn 승격 대상이 아님이 라우팅에 박혀야
    assert "citation" in out
    assert "영구 금지" in out or "승격 대상 아님" in out


def test_context_states_citation_safety():
    """④ citation 안전 — 생성 단일·인용 날조 금지가 contract 에 박혀야."""
    out = context_of(run_hook({"prompt": "draft"}))
    assert "citation" in out or "인용" in out
    assert "날조" in out or "자동" in out


def test_stage_label_distinct_from_omd():
    """⑤ oms 레이블(STAGE(paper))이 omd(STAGE(docs))·omha(ROUTE)와 달라
    화면 구분 가능. 한 화면에 omha ROUTE + 도메인 STAGE 가 같이 떠도
    헷갈리지 않도록. (이모지 없이 텍스트 레이블만으로 구분.)"""
    out = context_of(run_hook({"prompt": "논문"}))
    assert "STAGE(paper)" in out      # oms 전용 레이블
    assert "STAGE(docs)" not in out   # omd 레이블과 충돌 없음
    assert "ROUTE →" not in out       # omha 레인 레이블과 충돌 없음
    # 이모지 미사용 확인 (사용자 요청: 이모지 출력 안 함)
    assert "📑" not in out and "📄" not in out and "🧭" not in out


def test_stdlib_only_no_third_party_imports():
    """⑥ stdlib only — 외부 의존 없이 import 성공 가능."""
    src = HOOK.read_text()
    assert "import json" in src and "import sys" in src
    assert "import a2a" not in src and "import requests" not in src


def test_fail_open_on_bad_input():
    """⑦ fail-open: 잘못된 입력에도 exit 0, 세션 안 막음."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json at all", capture_output=True, text=True,
    )
    assert proc.returncode == 0


def test_context_states_oms_mandatory_no_skip():
    """⑨ oms 강제(skip 금지): 논문 작업이면 직접 수행하거나 OMC 병렬로 때우지
    말고 *반드시* oms STAGE 를 경유하라는 강제 문구가 contract 에 박혀야.

    배경(사용자 요청 2026-06-02): omha 가 도메인 우선으로 oms 를 1순위 진입시키는
    것과 짝을 이뤄, oms 자신의 라우팅 hook 도 '논문인데 oms 안 쓰고 직접 처리'를
    명시적으로 금지한다. citation 무결성 가드가 oms 안에만 있으므로, oms 를
    건너뛰면 그 가드도 건너뛰는 셈 — 이 인과를 contract 가 밝혀야 한다.
    SSOT: workspace .sp/specs/2026-06-02-oms-wiki-and-domain-routing-design.md §3.5."""
    out = context_of(run_hook({"prompt": "이 논문 introduction 초안 써줘"}))
    assert "반드시" in out                      # 강제 톤
    # 직접 수행/skip 금지 의미가 명시돼야
    assert ("직접 수행" in out or "직접 처리" in out or "건너뛰" in out)
    # oms 를 건너뛰면 citation 가드도 건너뛴다는 인과 (왜 강제인지)
    assert ("무결성" in out or "가드" in out)


def test_oms_mandatory_does_not_block_session():
    """⑨-b 강제 문구는 advisory(주입)일 뿐 fail-open 을 깨지 않아야 — exit 0 유지."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"prompt": "논문 verify"}),
        capture_output=True, text=True,
    )
    assert proc.returncode == 0


def test_context_states_knowledge_ssot_first_rule():
    """⑧ 지식 SSOT 우선 규율: 양식·구조 판단 시 소스/일반론/기억보다
    프로젝트의 `.hq/community/posts/` (`hq query --ascend`) 와 references/ 를 먼저 읽으라는 contract.

    회귀 배경: 양식(가로 전면 그림 허용 여부) 질문에 .cls 부재만 보고
    '신뢰할 출처 없음'으로 단정한 뒤에야 .oms/wiki 양식 카드를 뒤늦게 찾은
    사고. r7(2026-08-30)에서 wiki 페이지트리가 post 스토어로 전환됐지만
    (`hq post`/`hq query --ascend`), 규율 자체는 그대로다: 스토어에 답이
    있는데 일반론으로 추측·단정하는 것을 결함으로 명시하고, 스토어 확인
    전에는 '출처 없음' 선언조차 금지하도록 contract 에 못박는다."""
    out = context_of(run_hook({"prompt": "이 논문 양식에 가로로 긴 그림 전면 배치 되나?"}))
    assert ".hq/community/posts/" in out
    assert "--ascend" in out
    assert "references/" in out
    assert "먼저" in out   # 소스/일반론보다 스토어를 '먼저'
    assert "결함" in out   # 스토어 두고 일반론 단정 = 결함 명시


# --- R3 #22: relevance gate (is_paper_related) ---------------------------

def test_non_paper_prompt_is_silent():
    """⑩ 논문과 무관한 프롬프트는 침묵 — injection tax 0."""
    assert run_hook({"prompt": "hello"}).strip() == ""


def test_git_housekeeping_is_silent():
    """⑩-b git 정리 같은 일상 작업 요청도 무관하면 침묵."""
    assert run_hook({"prompt": "git 커밋 정리해줘"}).strip() == ""


def test_word_boundary_no_false_positive():
    """⑩-c 단어 경계 오탐 금지 — "oms"/"tex" 가 "atoms"/"context" 안에서
    발동하면 안 된다."""
    assert run_hook({"prompt": "look at the atoms in this context"}).strip() == ""


def test_missing_prompt_key_injects():
    """⑩-d prompt 키 자체가 없으면 fail-toward-inject — 전체 CHECKPOINT 주입."""
    out = context_of(run_hook({}))
    assert "STAGE(paper) →" in out
    assert "누락 금지" in out


def test_paper_prompt_still_injects_full_checkpoint():
    """⑩-e 논문 관련 프롬프트는 여전히 전체 CHECKPOINT 를 그대로 주입한다
    (byte-identity 는 이 파일의 기존 literal-lock 스위트 전체가 증명)."""
    out = context_of(run_hook({"prompt": "이 논문 introduction 초안 써줘"}))
    assert "STAGE(paper) →" in out
    assert "누락 금지" in out


def test_bare_read_and_discuss_words_do_not_trigger():
    """⑩-f R5 T3: bare 토큰 'read'/'discuss' 는 relevance-gate 키워드가 아니다 —
    scholar-read/scholar-discuss 의 Triggers 는 다단어 구문만(`deep read`,
    `discuss this idea` 등). 일상 프롬프트에 그 단어가 섞여도 4KB CHECKPOINT
    injection tax 가 붙으면 안 된다."""
    assert run_hook({"prompt": "please read the attached file and summarize it"}).strip() == ""
    assert run_hook({"prompt": "let's discuss dinner plans for tonight"}).strip() == ""


def test_phrase_triggers_do_inject():
    """⑩-g R5 T3: scholar-read/scholar-discuss 의 다단어 Trigger 구문은 실제로
    injection 을 발동시켜야 (⑩-f 의 대조 확인 — 게이트가 죽은 게 아니라 선택적)."""
    assert run_hook({"prompt": "can you deep read this for me"}).strip() != ""
    assert run_hook({"prompt": "I want to discuss this idea with you"}).strip() != ""
    assert run_hook({"prompt": "be my devil's advocate here"}).strip() != ""
