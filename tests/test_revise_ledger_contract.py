"""R2 #7 — the 3-strike and max-rounds guards become countable artifacts:
scholar-revise runs oms_state.py verbs instead of self-counting."""
import re

from conftest import skill_md

REVISE = skill_md("scholar-revise")


def test_loop_start_and_end_are_wired():
    assert "revise-start" in REVISE and "revise-end" in REVISE
    assert re.search(r"every exit path|all exit paths|each exit path", REVISE, re.I)


def test_strike_is_mechanical():
    assert re.search(r"strike --defect-id", REVISE)  # the CLI invocation itself, not a stray mention
    assert "third_strike" in REVISE
    assert re.search(r"not self-report|countable|mechanical", REVISE, re.I)


def test_rounds_are_mechanical():
    assert "revise-round" in REVISE and re.search(r"exceeded", REVISE)


def test_citation_defects_never_striked():
    idx = REVISE.index("strike --")  # anchor on the invocation token, not any prose 'strike'
    assert re.search(r"fixable_by_llm=false|citation.{0,80}never", REVISE[max(0, idx - 500):idx + 800], re.I | re.S)
