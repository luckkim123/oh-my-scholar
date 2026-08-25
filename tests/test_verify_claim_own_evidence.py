"""verify 의 claim↔자기근거 WARN 축이 세 층에 배선돼 있는지 (2026-08-25 신설).

카드에 규칙만 쓰고 verifier·rubric 에 안 배선하면 아무도 안 돌린다 — 이 저장소가
전에 밟은 함정이다(규칙 있음 ≠ 발동됨). 그리고 계측 안 된 게이트는 초록불이
아무 의미가 없으므로 calibration_status 라벨이 붙어 있어야 한다.

2026-08-25 계측: 두 클래스가 갈렸다. verb_exceeds_anchor 는 recall 4/4 · 오탐 0/9
(hard negative 5개 전부 통과)로 CALIBRATED. unanchored 는 0/4 인데 채점기 잘못이
아니라 규칙이 앵커를 "문단까지" 찾게 해서 실제 결과 절에서 발화 불가였다. 문구는
고쳤으나 그 수정은 버그를 찾아낸 바로 그 코퍼스에서 유도됐으므로 아직 미검증 —
그래서 이 클래스만 NOT_CALIBRATED 로 남는다. 라벨의 숫자는 score.py 가 정답표와
runs/ 에서 다시 계산해 대조한다(아래 test_label_numbers_match_the_runs).
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
VERIFIER = ROOT / "agents" / "scholar-verifier.md"
RUBRIC = ROOT / "references" / "rubrics" / "paper-eval.md"


def test_verifier_declares_the_axis():
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"[Cc]laim ↔ own evidence", body), "verifier 체크 목록에 축 누락"
    assert "7.6" in body, "verifier 절차에 7.6 단계 누락"
    assert re.search(r"\|\s*claim ↔ own evidence\s*\|", body), "verifier 요약표에 행 누락"


def test_axis_is_warn_not_fail():
    """정적 탐지를 hard-FAIL 로 걸면 문맥상 정당한 문장이 게이트를 막는다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"claim ↔ own evidence.*WARN", body, re.S | re.I)
    assert re.search(r"claim ↔ own evidence, uncited claims", body), \
        "WARN 요약 문장에 새 축이 안 실렸다 — 요약이 본문보다 오래 산다"


def test_axis_carries_a_per_class_calibration_label():
    """클래스별로 결과가 갈렸으므로 라벨도 갈려 있어야 한다. 한쪽의 4/4 로 다른 쪽의
    침묵까지 초록불 처리하는 것이 정확히 이 라벨이 막으려는 오독이다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert "calibration_status" in body, "calibration_status 라벨 누락"
    assert "CALIBRATED" in body and "NOT_CALIBRATED" in body, \
        "두 클래스가 갈렸는데 라벨이 한쪽만 말한다"
    assert "verb_exceeds_anchor" in body and "unanchored" in body, \
        "라벨이 어느 클래스가 계측됐는지 특정하지 않는다"


def test_label_numbers_match_the_runs():
    """라벨의 recall·오탐 수치는 정답표와 runs/ 에서 다시 계산돼야 한다. 코퍼스나
    채점 기록을 고치고 라벨을 안 고치면 요약이 본문보다 오래 사는 그 실패다."""
    import json

    fx = ROOT / "tests" / "fixtures" / "claim_own_evidence"
    gt = json.loads((fx / "ground_truth.json").read_text(encoding="utf-8"))["items"]
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((fx / "runs").glob("*.json"))]
    assert runs, "runs/ 가 비었다 — 라벨의 근거가 사라졌다"

    verb = {k for k, v in gt.items() if v.get("class") == "verb_exceeds_anchor"}
    negatives = {k for k, v in gt.items() if v["label"] == "negative"}
    for r in runs:
        fl = set(r["flagged"])
        assert verb <= fl, f"grader {r['grader']} 가 verb 클래스를 다 못 잡았다 — 라벨의 4/4 가 거짓"
        assert not (fl & negatives), f"grader {r['grader']} 오탐 — 라벨의 0/9 가 거짓"

    body = VERIFIER.read_text(encoding="utf-8")
    assert f"recall {len(verb)}/{len(verb)}" in body, "라벨의 recall 이 정답표와 안 맞는다"
    assert f"false positives 0/{len(negatives)}" in body, "라벨의 오탐 분모가 정답표와 안 맞는다"


def test_axis_does_not_overlap_citation_faithfulness():
    """두 축이 왜 다른지가 본문에 있어야 한다. 없으면 다음 사람이 중복으로 보고 지운다."""
    body = VERIFIER.read_text(encoding="utf-8")
    assert re.search(r"no.{0,4}\*{0,2}\\\\cite|carry \*\*no\*\* `\\cite`|without one", body), \
        "claim-faithfulness 와의 차이(=\\cite 없는 문장) 설명 누락"


def test_rubric_registers_the_axis():
    body = RUBRIC.read_text(encoding="utf-8")
    assert re.search(r"claim ↔ own evidence \(WARN\)", body), "paper-eval verify 축 표에 미등재"
    assert "writing-craft.md §3" in body, "rubric 이 규칙 SSOT 를 안 가리킨다"
