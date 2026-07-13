"""R1 #0 — the measured hallucination numbers live in README §citation-safety
as the load-bearing "why" (pure documentation, zero mechanism)."""
import re
from pathlib import Path

README = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")


def test_readme_cites_measured_rates():
    assert re.search(r"78[–-]90\s*%", README), "OpenScholar 합성 인용 오류율 누락"
    assert re.search(r"14[–-]95\s*%", README), "GhostCite 모델별 범위 누락"
    assert re.search(r"NeurIPS 2025", README), "인간 리뷰 미검출 사례 누락"


def test_readme_evidence_has_sources():
    assert "2411.14199" in README, "OpenScholar arXiv id 누락"
    assert "2602.06718" in README, "GhostCite arXiv id 누락"


def test_readme_names_the_interlock():
    assert "scholar_cite_guard" in README
    assert "verify_bib_entry" in README
