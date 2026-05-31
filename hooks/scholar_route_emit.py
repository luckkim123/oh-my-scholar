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
"""
import json
import sys

CHECKPOINT = (
    "<oms-routing>\n"
    "논문 작업 요청(.tex/.bib 작성·검토·검증, 관련연구 조사, 개념 정리)이면, 행동 전에 한 줄로 판정하라:\n"
    "- 0단계(부트스트랩): init(새 논문 시작 — 폴더 위치·venue·주제를 대화로 잡고 디렉토리 scaffold + "
    ".oms/ 초기화 + 상위 .oms/ 전역 wiki 씨앗 참조). 이미 .oms/<slug>/ 있으면 init 아님.\n"
    "- 단계(.md 레이어): research(관련연구·gap) / deepen(주장 모호성 게이트, 정성) / "
    "ideate(개념 .md) / outline(섹션·story arc)\n"
    "- 단계(.tex 레이어): draft(초안 생성) / inspect(형성적 비평·코치) / "
    "mock-review(venue reviewer 입장 심판 — 점수+venue-native 판정(컨퍼런스 accept/reject·letter / "
    "저널 minor·major revision), inspect와 다른 축) / "
    "verify(총괄 게이트) / revise(통과까지 루프), 또는 scholar-pilot(통째).\n"
    "- 메타 단계: learn(관찰→venue 기본값 승격, 사람 게이트) — 운영 중 .oms/learned.md 에 쌓인 "
    "관찰을 venue 강제 기본값으로 굳힐 때만. 자동 발동 아님(heavy=사람 게이트).\n"
    "단일 단계면 그 스킬 직접, 브리프→완성이면 scholar-pilot.\n"
    "⚠️ citation 안전: 생성(draft)은 단일·신중, 인용 날조·자동 .bib 수정 금지. citation/.bib 는 "
    "learn 승격 대상 아님(영구 금지).\n\n"
    "논문 작업이면, 판정을 응답 맨 앞 omha ROUTE 줄 바로 다음에 이 한 줄로 출력하라(누락 금지):\n"
    "STAGE(paper) → <init|research|deepen|ideate|outline|draft|inspect|mock-review|verify|revise|learn|scholar-pilot> · <한 줄 근거>\n"
    "논문 작업이 아니면 이 블록 전체 무시(STAGE 줄도 출력하지 말 것).\n"
    "</oms-routing>"
)


def main() -> int:
    try:
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
