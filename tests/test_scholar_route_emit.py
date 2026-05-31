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
    """③ 11개 단계가 contract 에 모두 열거돼야 (skill 과 정합).

    deepen 은 scholar-deepen 스킬(research↔ideate 사이 모호성 게이트)이
    실재하므로 STAGE 카탈로그에 포함돼야 한다 (T14 에서 추가).
    learn 은 scholar-learn 스킬(관찰→venue 기본값 승격, 사람 게이트)이
    실재하므로 메타 단계로 포함돼야 한다 (H9 에서 추가).
    init 은 scholar-init 스킬(0단계 부트스트랩 — 새 논문 시작)이 실재하므로
    포함돼야 한다 (scholar-init 도입에서 추가)."""
    out = context_of(run_hook({"prompt": "논문 작업"}))
    for stage in ("init", "research", "deepen", "ideate", "outline", "draft",
                  "inspect", "verify", "revise", "learn", "scholar-pilot"):
        assert stage in out, f"stage '{stage}' missing from contract"


def test_init_stage_is_bootstrap_zero():
    """③-d init 0단계가 STAGE 토큰 줄과 안내문에 명시돼야 (scholar-init).

    새 논문 시작 = 부트스트랩이라는 의미와, 이미 .oms/<slug>/ 가 있으면
    init 이 아니라는 멱등성 단서가 라우팅에 박혀야 한다."""
    out = context_of(run_hook({"prompt": "새 논문 쓸래 폴더 만들어줘"}))
    assert "init" in out
    assert "부트스트랩" in out          # 0단계 의미
    assert ".oms/" in out               # 전역/로컬 .oms 언급
    # 이미 초기화된 폴더면 init 아님 (멱등성 단서)
    assert "있으면 init 아님" in out


def test_learn_stage_in_routing_token_line():
    """③-b learn 메타 단계가 STAGE 토큰 줄에 명시돼야 (H9)."""
    out = context_of(run_hook({"prompt": "이 관찰 규칙으로 굳혀줘"}))
    assert "learn" in out
    # learn 은 메타 단계 — 자동 발동 아님(사람 게이트)이 명시돼야
    assert "사람 게이트" in out


def test_learn_routing_keeps_citation_guard():
    """③-c learn 추가가 citation 안전 가드를 깨지 않아야 (H9·§6.F)."""
    out = context_of(run_hook({"prompt": "promote observation"}))
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
