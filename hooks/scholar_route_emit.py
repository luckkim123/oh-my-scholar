"""oms UserPromptSubmit hook: inject a paper-stage routing checkpoint.

Stdlib only (a test enforces this). Mirrors OMD's route_emit.py: the hook does
NOT decide anything itself — it injects a one-line checkpoint that reminds the
session LLM, when a paper request is detected, to declare which paper STAGE it
is in before acting. The actual stage logic lives in skills/scholar-*/SKILL.md
(single source of truth); this hook never embeds that knowledge inline, so
there is no drift.

Layering: omha (the meta-harness) picks the LANE (superpowers / oh-my-claudecode
/ handle-directly). oms is a DOMAIN handler (academic paper), so this hook never
picks a lane — it only picks the STAGE within the paper domain, and emits it on
the line right after omha's ROUTE line. The two do not conflict.

Why a STAGE line (not a lane line): the user wants the per-turn skill selection
made visible, exactly like omha's 🧭 ROUTE line. Citation-bound work makes the
stage especially worth surfacing (draft vs verify is a safety-relevant split).

MVP: static checkpoint text (no keyword parsing). Fail-open: any error returns 0
so the session is never blocked.

R3 #22: two additive changes (the CHECKPOINT text above stays byte-identical).
(a) A relevance gate (`is_paper_related`) — prompts unrelated to paper work are
silent, no injection tax; a missing/unparseable prompt still fails toward
injection. (b) env DISABLE_OMS (1/true/on/yes, case/whitespace-insensitive) is
the umbrella kill switch shared by all 5 registered oms hooks, checked first,
before reading stdin (mirrors OMC's DISABLE_OMC) — never advertised in any
injected text.
"""
import json
import os
import re
import sys

CJK_TOKENS = (
    "논문", "학위", "초안", "원고", "관련연구", "선행연구", "문헌", "인용",
    "참고문헌", "서지", "투고", "게재", "심사", "리비전", "초록", "목차",
    "아웃라인", "저널", "학회", "모의심사",
)
ASCII_TOKENS = (
    "paper", "thesis", "dissertation", "manuscript", "latex", "tex", "bib",
    "bibtex", "citation", "cite", "venue", "survey", "outline", "draft",
    "journal", "conference", "arxiv", "doi", "review", "reviewer", "rebuttal",
    "revise", "verify", "abstract", "scholar", "oms", "ideate", "related",
)
DOT_TOKENS = (".tex", ".bib")
PHRASE_TOKENS = (
    "deep read", "reading note", "read this paper", "논문 읽어", "이 논문 정리", "딥리드", "리딩노트",
    "discuss this idea", "devil's advocate", "argue with me", "challenge my idea",
    "토론하자", "아이디어 논의", "반론해줘", "디스커션",
)
_ASCII_RE = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in ASCII_TOKENS) + r")\b")

CHECKPOINT = (
    "<oms-routing>\n"
    "논문 작업 요청(.tex/.bib 작성·검토·검증, 관련연구 조사, 개념 정리)이면, 행동 전에 한 줄로 판정하라:\n"
    "- 0단계(부트스트랩): init(새 논문 시작 — 폴더 위치·venue·주제를 대화로 잡고 디렉토리 scaffold + "
    ".hq/ 초기화 + 상위 .hq/ 전역 posts 씨앗 참조 — `hq query --ascend`). 이미 .hq/work/scholar/<slug>/ 있으면 init 아님.\n"
    "- 단계(.md 레이어): research(관련연구·gap) / deepen(주장 모호성 게이트, 정성) / "
    "ideate(개념 .md) / outline(섹션·story arc)\n"
    "- 단계(.tex 레이어): draft(초안 생성) / inspect(형성적 비평·코치) / "
    "mock-review(venue reviewer 입장 심판 — 점수+venue-native 판정(컨퍼런스 accept/reject·letter / "
    "저널 minor·major revision), inspect와 다른 축) / "
    "verify(총괄 게이트) / revise(통과까지 루프), 또는 scholar-pilot(통째).\n"
    "- 보조 단계(입력 확장·논의, 온디맨드): read(외부 논문 딥리드 → .hq/community/reading/ 리딩노트, 단일 dispatch, "
    ".bib 미기록) / discuss(아이디어 토론 — Contrarian/Simplifier/Ontologist, subagent dispatch 없음, "
    "outline 변경은 제안만 — 자동 적용 금지).\n"
    "- 메타 단계: learn(관찰→venue 기본값 승격, 사람 게이트) — 운영 중 .hq/config/scholar/learned.md 에 쌓인 "
    "관찰을 venue 강제 기본값으로 굳힐 때만. 자동 발동 아님(heavy=사람 게이트).\n"
    "단일 단계면 그 스킬 직접, 브리프→완성이면 scholar-pilot.\n"
    "⚠️ oms 강제(skip 금지): 논문 작업이면 직접 수행하거나 OMC 병렬로 때우지 말고 "
    "*반드시* oms 의 한 STAGE 를 경유하라. citation 무결성 가드(인용 날조 금지·임베딩 "
    "검색 금지·draft 단일신중)가 oms 스킬 안에만 있으므로, oms 를 건너뛰면 그 가드도 "
    "건너뛰는 셈이다 — 그래서 '간단해 보여서 직접' 이 곧 안전장치 우회가 된다.\n"
    "⚠️ citation 안전: 생성(draft)은 단일·신중, 인용 날조·자동 .bib 수정 금지. citation/.bib 는 "
    "learn 승격 대상 아님(영구 금지).\n"
    "⚠️ 지식 SSOT 우선(작성·답변 전 필독): 양식·구조·명명·인용서식 등 '이 논문은 어떻게 쓰나'를 "
    "묻거나 판단해야 하면, 소스 코드(.cls/.sty)·일반 관행·내 기억보다 먼저 이 프로젝트의 "
    ".hq/community/posts/ 와 references/ 를 SSOT 로 읽어라 — `hq query --keyword <말> --ascend --topic convention` "
    "(topic: convention·pattern·decision·reference·history). ⚠️ `--ascend` 를 빼면 최근접 "
    "앵커만 본다. 스토어에 답이 있는데 일반론으로 추측·단정하는 것은 결함이다. 거기에 없을 때만 "
    "'신뢰할 출처 없음'을 선언하라 — 스토어를 확인하기 전에는 그 선언도 금지.\n\n"
    "논문 작업이면, 판정을 응답 맨 앞 omha ROUTE 줄 바로 다음에 이 한 줄로 출력하라(누락 금지):\n"
    "STAGE(paper) → <init|research|deepen|ideate|outline|draft|inspect|mock-review|verify|revise|learn|read|discuss|scholar-pilot> · <한 줄 근거>\n"
    "논문 작업이 아니면 이 블록 전체 무시(STAGE 줄도 출력하지 말 것).\n"
    "</oms-routing>"
)


def is_paper_related(prompt) -> bool:
    """True when prompt is missing/not-a-string (fail-toward-inject) or any
    paper-domain token matches. Never raises -- an internal error also fails
    toward injection."""
    try:
        if not isinstance(prompt, str):
            return True
        lowered = prompt.lower()
        if any(tok in lowered for tok in CJK_TOKENS):
            return True
        if any(tok in lowered for tok in DOT_TOKENS):
            return True
        if any(tok.lower() in lowered for tok in PHRASE_TOKENS):
            return True
        return bool(_ASCII_RE.search(lowered))
    except Exception:
        return True  # gate exception -> inject


def _disable_oms() -> bool:
    try:
        return os.environ.get("DISABLE_OMS", "").strip().lower() in ("1", "true", "on", "yes")
    except Exception:
        return False  # env-read exception -> proceed as if unset


def main() -> int:
    if _disable_oms():
        return 0
    try:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = None
        prompt = payload.get("prompt") if isinstance(payload, dict) else None
        if not is_paper_related(prompt):
            return 0
        out = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": CHECKPOINT,
            }
        }
        print(json.dumps(out))
    except Exception:
        return 0  # fail-open — never block the session
    return 0


if __name__ == "__main__":
    sys.exit(main())
