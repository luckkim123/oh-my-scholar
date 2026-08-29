"""Tests for the knowledge-store audit procedure card (R4 #23, rewired r7 2026-08-30)
— references/knowledge/audit.md.

Background: the wiki page-tree form was retired (r7, user decision: "wiki 는 아예
없애는 걸로. Wiki 폴더 안만들게"), and `scripts/oms_wiki_audit.py` (the script this
card's old §1 pointed at) was deleted with it — verified by running it: from any live
anchor it exits non-zero with `--root '.../community/wiki' does not exist`. The card's
§1 (mechanical half) is rewritten to point at `hq lint`/`hq query --ascend` instead of
the retired script's `--root`/`--write-index` flags. §2-§4 (SSOT-delegation integrity,
strength-tag discipline, the calibration lesson) are judgment dimensions that never
described page-tree shape — they survive close to verbatim, just with `references/wiki/`
path pointers updated to `references/knowledge/`.

House convention (see test_writing_craft_card.py): plain asserts on file text,
content-token locks.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CARD = ROOT / "references" / "knowledge" / "audit.md"


def _body():
    return CARD.read_text(encoding="utf-8")


def test_card_exists():
    assert CARD.exists(), "references/knowledge/audit.md missing — knowledge-store audit procedure card"


def test_old_card_location_gone():
    assert not (ROOT / "references" / "wiki").exists(), \
        "references/wiki/ must be gone — the store retired the page-tree form (git mv to references/knowledge/)"


def test_title_line():
    """Line 1 matches house card title convention: `# <Title> — <subtitle>`."""
    lines = _body().splitlines()
    assert lines[0].startswith("# Knowledge Store Audit — "), f"line 1 must match '^# Knowledge Store Audit — ', got: {lines[0]!r}"


def test_consumer_blockquote():
    """Line 2 is a `> ` blockquote stating what the card is and who consumes it."""
    lines = _body().splitlines()
    assert lines[1].startswith("> "), f"line 2 must be a '> ' consumer blockquote, got: {lines[1]!r}"


# --------------------------------------------------------- §1: mechanical half rewired to hq verbs
def test_section1_no_longer_names_the_retired_script():
    """The retired script must not be named as a live instruction — it's `git rm`'d.
    `--root` may still appear in prose explaining the change (e.g. "unlike the retired
    script's --root, hq owns ascent"), so this only locks the *command fence* — the
    actual run instructions — never invokes the retired script or its flags."""
    body = _body()
    assert "oms_wiki_audit.py" not in body, \
        "scripts/oms_wiki_audit.py was git rm'd (r7) — the card must not instruct running it"
    fence = re.search(r"```\n(.*?)```", body, re.S).group(1)
    assert "--root" not in fence, "the command fence must not instruct the retired --root flag"
    assert "--write-index" not in fence, \
        "the command fence must not instruct the retired --write-index flag"


def test_section1_points_to_hq_lint_and_query():
    """§1 gives real run instructions for the mechanical verbs that replaced the script."""
    body = _body()
    assert "hq lint" in body
    assert "hq query" in body
    assert "--ascend" in body


def test_section1_index_is_automatic():
    body = _body()
    assert re.search(r"INDEX\.md.{0,60}automatic", body, re.I | re.S) or \
        re.search(r"automatic.{0,60}INDEX\.md", body, re.I | re.S)


# --------------------------------------------------------- §2: SSOT-delegation (survives)
def test_section2_ssot_delegation_dimension():
    """§2 — SSOT-delegation integrity: broken + cyclic delegation, ported
    from the source workflow prompt (quote the delegating sentence, verify
    the target owns the topic, never flag healthy one-directional delegation)."""
    body = _body()
    assert "SSOT-delegation" in body
    assert re.search(r"broken delegation", body, re.I)
    assert re.search(r"cyclic delegation", body, re.I)
    assert re.search(r"never flag.*healthy|healthy.*never flag|do not flag.*healthy", body, re.I), \
        "must preserve 'do not flag a healthy one-directional delegation' guidance"


# --------------------------------------------------------- §3: strength-tag discipline (survives)
def test_section3_strength_tag_calibration_exact_wording_governs():
    """§3 — strength-tag discipline WITH the calibration block ported
    verbatim in substance: the rule's exact wording governs."""
    body = _body()
    assert "strength-tag" in body
    assert re.search(r"exact wording governs", body, re.I), \
        "calibration rule 'the rule's exact wording governs' must be preserved"
    assert "[N편공통]" in body, "quoted Korean rule text must stay verbatim (quotes the rule's own wording)"
    assert "1편에서만 본 걸 공통이라 쓰지 않는다" in body or "1편에서만 본 걸 \"공통\"이라 쓰지 않는다" in body


def test_section3_naming_two_papers_passes_without_inline_quotes():
    """A tag NAMING 2+ distinct papers passes even without inline quotes —
    the naming attests the multi-paper observation."""
    body = _body()
    assert re.search(r"2\+?\s*(distinct )?papers?.{0,40}pass", body, re.I) or \
        re.search(r"names?.{0,20}2\+?\s*(distinct )?papers?.{0,60}(pass|satisf)", body, re.I), \
        "must state a tag naming 2+ distinct papers PASSES (even without inline quotes)"


def test_section3_defect_is_only_count_exceeds_named_sources():
    """A defect is ONLY tagged-count > named-or-quoted distinct sources."""
    body = _body()
    assert re.search(r"tagged.count.{0,40}exceed", body, re.I) or \
        re.search(r"exceed.{0,60}named.or.quoted", body, re.I), \
        "must state the defect condition: tagged count exceeds named-or-quoted distinct sources"


def test_section3_one_reminder_per_file_not_per_tag():
    """At most one independence-cluster reminder per file, not one per tag."""
    body = _body()
    assert re.search(r"one.{0,20}reminder per file", body, re.I)
    assert re.search(r"not (one )?per tag", body, re.I)


# --------------------------------------------------------- §4: calibration lesson (survives)
def test_section4_calibration_lesson_generalized():
    """§4 — the generalized calibration lesson: when a dimension's findings
    diverge from expectation, audit the criteria first, then the corpus."""
    body = _body()
    assert re.search(r"audit the criteria", body, re.I)
    assert "2026-06-02" in body, "must cite the 2026-06-02 incident as the worked example"


# --------------------------------------------------------- §5: detection-only (rewired: "wiki" -> "post store")
def test_section5_detection_only_discipline():
    """§5 — the audit NEVER edits the post store; findings ranked high/medium/low
    with file:line evidence."""
    body = _body()
    assert re.search(r"never edits the post store", body, re.I)
    assert re.search(r"high\s*/\s*medium\s*/\s*low|high/medium/low", body, re.I)
    assert "file:line" in body


def test_no_duplicate_embedding_of_retirement_explanation():
    """House discipline: point to references/knowledge/README.md for the form-change
    explanation instead of re-narrating it here."""
    body = _body()
    assert "references/knowledge/README.md" in body


def test_section_numbers_present_in_order():
    body = _body()
    tokens = re.findall(r"^##\s*§(\d)", body, re.M)
    assert tokens == sorted(tokens), f"§-numbered sections out of order: {tokens}"
    assert set(tokens) >= {"1", "2", "3", "4", "5"}, f"missing §-numbered sections, found: {tokens}"
