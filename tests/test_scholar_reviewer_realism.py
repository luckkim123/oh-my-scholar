"""Tests for the R5 #32 reviewer realism pack — measurably-less-generic lenses + a
calibrated Area Chair, with zero invented calibration data (D4).

Background: `agents/scholar-reviewer.md` gains (1) an aspect-checklist-first step in
lens mode (Reviewer2 pattern — judge each venue-form aspect `strong|adequate|weak|n/a`
BEFORE deriving strengths/weaknesses, rather than writing S/W first and back-filling),
(2) a concession-threshold rule in AC mode (never lower a weakness's severity or raise a
score without concrete anchored evidence — never on rhetorical concession, author
confidence, or repetition; also stated as one line in `scholar-mock-review`'s Step 3 AC
synthesis), and (3) an optional, off-by-default ensemble-variance move (AC may request
one extra independent sample of a single borderline lens and report agreement/divergence
instead of silently averaging). `references/rubrics/venue-review-forms.md` gains a
per-form "Score bands" slot (empty band/meaning/source template — never prefilled
numbers), with a one-line pointer from `references/venues.md`. `references/wiki/README.md`
documents a `reference/venue-review-examples-<venue>.md` few-shot convention that lens
mode reads via the existing 2-tier `wiki_query` contract (no new mechanism).

⚠️ Deliberate phrasing constraint (plan acceptance criterion): `git grep -i "score band"`
must hit only the rubrics card, venues.md's pointer, and tests — NOT
`agents/scholar-reviewer.md` (which refers to the same concept as "calibration table" to
keep the literal phrase scoped to the SSOT + its one pointer). One discriminance test
below locks this scoping directly.

House convention (see test_scholar_mock_review_skill.py / test_wiki_spec_docs.py): plain
substring asserts over whole-file text, a `section()`-style extractor scoped to the
`### Score bands` blocks for the "no numeric data" discriminance check."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
REVIEWER_AGENT = (ROOT / "agents" / "scholar-reviewer.md").read_text(encoding="utf-8")
RUBRICS = (ROOT / "references" / "rubrics" / "venue-review-forms.md").read_text(encoding="utf-8")
VENUES = (ROOT / "references" / "venues.md").read_text(encoding="utf-8")
WIKI_README = (ROOT / "references" / "wiki" / "README.md").read_text(encoding="utf-8")

UNCALIBRATED_DISCLAIMER = "no calibration data — uncalibrated venue-scale estimate"
# Matches the disclaimer even when line-wrapped (a literal newline instead of a space
# between "uncalibrated" and "venue-scale estimate" in prose, same as the rubrics doc).
UNCALIBRATED_DISCLAIMER_RE = re.compile(r"no calibration data\s*—\s*uncalibrated\s+venue-scale estimate")


# --------------------------------------------------------- lens mode: aspect-checklist-first
def test_reviewer_agent_aspect_checklist_step_named():
    assert "Aspect checklist first" in REVIEWER_AGENT
    assert "Reviewer2 pattern" in REVIEWER_AGENT
    assert "per-aspect: strong|adequate|weak|n/a" in REVIEWER_AGENT


def test_reviewer_agent_aspect_checklist_precedes_sw_derivation():
    """The checklist step must come BEFORE the 'Derive per-lens findings' step, and that
    step must explicitly say S/W is derived FROM the checklist (not written independently)."""
    idx_checklist = REVIEWER_AGENT.index("Aspect checklist first")
    idx_derive = REVIEWER_AGENT.index("Derive per-lens findings")
    assert idx_checklist < idx_derive
    derive_window = REVIEWER_AGENT[idx_derive: idx_derive + 300]
    assert "derived from the aspect" in derive_window


def test_reviewer_agent_output_format_has_aspect_checklist_block():
    assert "### Aspect checklist" in REVIEWER_AGENT
    idx_block = REVIEWER_AGENT.index("### Aspect checklist")
    idx_strengths = REVIEWER_AGENT.index("### Strengths (each location-anchored)")
    assert idx_block < idx_strengths


# --------------------------------------------------------- AC mode: concession-threshold
def test_reviewer_agent_concession_threshold_rule():
    assert "Concession-threshold" in REVIEWER_AGENT
    sec = REVIEWER_AGENT[REVIEWER_AGENT.index("Concession-threshold"):]
    sec = sec[: sec.index("A8)")]
    for phrase in ("concrete anchored", "rhetorical concession", "author confidence", "repetition"):
        assert phrase in sec, f"missing phrase in concession-threshold rule: {phrase}"


def test_reviewer_agent_final_checklist_has_concession_threshold_item():
    assert "concession-threshold test" in REVIEWER_AGENT


def test_mock_review_skill_body_has_concession_threshold_one_liner():
    body = (ROOT / "skill-bodies" / "scholar-mock-review" / "SKILL.md").read_text(encoding="utf-8")
    idx3 = body.index("3. **Area Chair synthesis")
    idx4 = body.index("4. **Verdict-history append")
    sec3 = body[idx3:idx4]
    assert "Concession-threshold" in sec3
    assert "rhetorical concession" in sec3


# --------------------------------------------------------- AC mode: ensemble variance (optional)
def test_reviewer_agent_ensemble_variance_optional_off_by_default():
    assert "Ensemble variance" in REVIEWER_AGENT
    idx = REVIEWER_AGENT.index("Ensemble variance")
    window = REVIEWER_AGENT[idx: idx + 400]
    assert "optional, off by default" in window or "off by default" in window
    assert "N=2" in window
    assert "### Ensemble check" in REVIEWER_AGENT


# --------------------------------------------------------- uncalibrated disclaimer (never guess)
def test_reviewer_agent_uncalibrated_disclaimer_present_in_ac_mode():
    """AC step A4, the AC output format, and the Final_Checklist each say the disclaimer
    verbatim (lens mode never issues a number, so it only notes the table's populated/empty
    state without repeating the numeric-scale disclaimer — see the aspect-checklist test)."""
    hits = UNCALIBRATED_DISCLAIMER_RE.findall(REVIEWER_AGENT)
    assert len(hits) >= 3, f"expected the disclaimer in AC step A4 + output format + checklist, found {len(hits)}"


def test_reviewer_agent_never_says_literal_score_band_phrase():
    """Discriminance lock for the plan's acceptance criterion: `git grep -i "score band"`
    must hit only the rubrics card + venues.md pointer + tests — this agent file paraphrases
    the same concept as 'calibration table' instead."""
    assert not re.search(r"score\s+bands?", REVIEWER_AGENT, re.I), (
        "agents/scholar-reviewer.md must not contain the literal phrase 'score band(s)' — "
        "paraphrase as 'calibration table' (plan T5 acceptance criterion)"
    )
    assert "calibration table" in REVIEWER_AGENT


# --------------------------------------------------------- few-shot review examples (wiki reference/)
def test_reviewer_agent_reads_few_shot_wiki_reference_note():
    assert 'venue-review-examples-<venue>.md' in REVIEWER_AGENT
    assert 'wiki_query(category="reference")' in REVIEWER_AGENT


def test_wiki_readme_documents_few_shot_review_examples_slot():
    assert "venue-review-examples-<venue>.md" in WIKI_README
    assert "private" in WIKI_README
    idx = WIKI_README.index("venue-review-examples-<venue>.md")
    window = WIKI_README[idx: idx + 400]
    assert "never shipped" in window
    assert "wiki_query" in window


# --------------------------------------------------------- rubrics doc: Score bands template
def _score_band_sections():
    """Return the text of each '### Score bands ...' block up to the next heading/rule."""
    sections = []
    for m in re.finditer(r"### Score bands.*?(?=\n---|\n## )", RUBRICS, re.S):
        sections.append(m.group(0))
    return sections


def test_rubrics_score_bands_heading_present_per_form():
    heading = "Score bands (populate from public venue stats — keep a source URL per row; never guess)"
    assert RUBRICS.count(heading) == 4, "expected one Score bands block per Form (1-4)"


def test_rubrics_score_bands_never_guess_phrase():
    assert "never guess" in RUBRICS


def test_rubrics_score_bands_empty_template_columns():
    sections = _score_band_sections()
    assert len(sections) == 4
    for sec in sections:
        assert "Band | Meaning | Source" in sec or "| Band | Meaning | Source |" in sec
        assert "empty" in sec.lower()


def test_rubrics_score_bands_contain_no_numeric_data():
    """D4 / acceptance: no invented calibration numbers anywhere in the Score bands slots
    (the venue scale numbers like '1-4'/'1-10' elsewhere in the doc are a different thing —
    scoped strictly to the Score bands blocks here)."""
    sections = _score_band_sections()
    assert len(sections) == 4
    for sec in sections:
        assert not re.search(r"\d", sec), f"Score bands block must carry no numeric data, found digits in: {sec!r}"


def test_rubrics_score_bands_read_by_reviewer_when_populated():
    assert UNCALIBRATED_DISCLAIMER_RE.search(RUBRICS)


# --------------------------------------------------------- venues.md: one-line pointer
def test_venues_meta_pointer_to_score_bands():
    assert re.search(r"score\s+bands?", VENUES, re.I)
    assert "venue-review-forms.md" in VENUES
    assert "no score data lands here" in VENUES or "no score data lands" in VENUES


def test_venues_pointer_does_not_duplicate_band_template():
    """SSOT discipline: venues.md points at the rubrics card, it does not restate the
    band/meaning/source table."""
    assert "Band | Meaning | Source" not in VENUES


# --------------------------------------------------------- acceptance: phrase scoping (repo-wide)
def test_score_band_phrase_scoped_to_rubrics_and_venues_only():
    """Acceptance criterion from the plan: `git grep -i "score band"` hits the rubrics
    card + venues.md pointer + tests only. Scan the plugin source surfaces (not docs/ or
    tests/, which are allowed / out of scope) and assert no other file leaked the phrase."""
    scan_dirs = ["agents", "skill-bodies", "skills", "references", "scripts", "hooks"]
    hits = []
    for d in scan_dirs:
        for path in (ROOT / d).rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if re.search(r"score\s+bands?", text, re.I):
                hits.append(str(path.relative_to(ROOT)))
    for path in (ROOT / "scripts").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"score\s+bands?", text, re.I):
            hits.append(str(path.relative_to(ROOT)))
    allowed = {
        "references/rubrics/venue-review-forms.md",
        "references/venues.md",
    }
    unexpected = sorted(set(hits) - allowed)
    assert not unexpected, f"'score band' leaked outside rubrics card / venues.md pointer: {unexpected}"
