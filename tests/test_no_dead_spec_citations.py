"""`docs/specs/` left the tree in 1940cc6 (2026-06-06, "[정리] 문서 영어화 + spec 산출물
삭제"). Six citations to it survived the deletion for eleven weeks -- two of them in
*deployed* files (agents/scholar-reviewer.md, references/rubrics/venue-review-forms.md),
where they sent an agent to a path that does not exist. A dangling pointer in a shipped
card is worse than a missing one: the reader has no reason to doubt it.

The fix was to keep every citation but attach the recovery command, so the pointer still
resolves on any clone. This test locks that: a bare `docs/specs/` path is a failure.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
RECOVERY = "1940cc6"
WINDOW = 220  # chars either side -- `git show 1940cc6^:docs/specs/...` puts the
              # marker *before* the path, prose footnotes put it after


def _tracked_text_files():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "*.md", "*.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [ROOT / p for p in out.split("\0") if p]


def test_docs_specs_dir_is_really_gone():
    """If someone restores it, this test's premise dies and it should be deleted."""
    assert not (ROOT / "docs" / "specs").exists()


def test_every_docs_specs_citation_carries_its_recovery_command():
    dangling = []
    for f in _tracked_text_files():
        if f.name == Path(__file__).name:
            continue
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"docs/specs/", text):
            near = text[max(0, m.start() - WINDOW): m.start() + WINDOW]
            if RECOVERY not in near:
                line = text.count("\n", 0, m.start()) + 1
                dangling.append(f"{f.relative_to(ROOT)}:{line}")
    assert not dangling, (
        "bare docs/specs/ citation(s) -- attach `git show 1940cc6^:<path>`: " + ", ".join(dangling)
    )
