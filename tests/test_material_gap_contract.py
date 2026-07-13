"""R1 #4 — when grounding material is absent the drafter emits a greppable
`% [MATERIAL GAP: …]` token instead of inferring (clean-room ARS mechanism);
verify FAILs leftover MATERIAL GAP tokens (placeholder class) and WARNs on
claim-shaped sentences with no adjacent \\cite."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DRAFTER = (ROOT / "agents" / "scholar-drafter.md").read_text(encoding="utf-8")
VERIFIER = (ROOT / "agents" / "scholar-verifier.md").read_text(encoding="utf-8")
DRAFT_SKILL = (ROOT / "skills" / "scholar-draft" / "SKILL.md").read_text(encoding="utf-8")
VERIFY_SKILL = (ROOT / "skills" / "scholar-verify" / "SKILL.md").read_text(encoding="utf-8")


def test_drafter_material_gap_contract():
    assert "MATERIAL GAP" in DRAFTER
    assert re.search(r"instead of inferring|never.*infer|inferring", DRAFTER, re.I), \
        "근거 부재 시 추론 대신 토큰 방출 계약 누락"


def test_drafter_surfaces_gaps_in_output():
    assert re.search(r"MATERIAL GAP", DRAFTER[DRAFTER.index("<Output_Format>"):]), \
        "Output_Format 의 gap 목록 누락"


def test_verifier_fails_leftover_material_gap():
    assert "MATERIAL GAP" in VERIFIER
    idx = VERIFIER.index("Placeholder check") if "Placeholder check" in VERIFIER else VERIFIER.index("MATERIAL GAP")
    assert re.search(r"MATERIAL GAP", VERIFIER[idx:idx + 800]), "placeholder 토큰 목록에 MATERIAL GAP 누락"


def test_verifier_uncited_claim_scan_is_warn():
    assert re.search(r"uncited[- ]claim", VERIFIER, re.I)
    block = VERIFIER[re.search(r"uncited[- ]claim", VERIFIER, re.I).start():]
    assert "WARN" in block[:600], "uncited-claim 스캔은 WARN 급이어야"


def test_skills_carry_both_contracts():
    assert "MATERIAL GAP" in DRAFT_SKILL
    assert re.search(r"uncited[- ]claim|MATERIAL GAP", VERIFY_SKILL)
