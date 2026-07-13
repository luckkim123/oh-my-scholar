"""R4 #23/#25 — tests for `scripts/oms_wiki_audit.py` (read-only wiki
health-audit CLI: mechanical dimensions + INDEX generation).

Driven mostly through `main()` + capsys (house convention: CLI-level text
assertions), matching `tests/test_oms_state.py`'s import-under-test idiom.
"""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "oms_wiki_audit.py"
spec = importlib.util.spec_from_file_location("oms_wiki_audit", SCRIPT)
owa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owa)


def _write(base, rel, content):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _fm(confidence="high", sightings=1):
    return f"---\nconfidence: {confidence}\nsightings: {sightings}\n---\n"


def _lines_with(out, *needles):
    return [l for l in out.splitlines() if all(n in l for n in needles)]


def test_healthy_tree_passes(tmp_path, capsys):
    for cat, slug, title in [
        ("convention", "note-a", "Note A"),
        ("pattern", "note-b", "Note B"),
        ("decision", "note-c", "Note C"),
        ("reference", "note-d", "Note D"),
        ("history", "note-e", "Note E"),
    ]:
        _write(tmp_path, f"{cat}/{slug}.md", _fm() + f"# {title}\n\nBody text.\n")
    _write(tmp_path, "README.md",
           "# Wiki\n\nLinks: [[note-a]] [[note-b]] [[note-c]] [[note-d]] [[note-e]]\n")

    assert owa.main(["--root", str(tmp_path), "--write-index"]) == 0
    capsys.readouterr()
    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "FAIL" not in out
    assert "WARN" not in out


def test_missing_root_exits_2(tmp_path, capsys):
    missing = tmp_path / "nope"
    assert owa.main(["--root", str(missing)]) == 2
    err = capsys.readouterr().err
    assert "error" in err and "not exist" in err


def test_duplicate_token_fails(tmp_path, capsys):
    _write(tmp_path, "convention/dupe.md",
           _fm() + "# Title\n\n### F2 First\nbody\n\n### F2 Second\nbody\n")
    _write(tmp_path, "convention/ok.md",
           _fm() + "# Title2\n\n### F1 A\nbody\n\n### F1b B\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    dup_lines = _lines_with(out, "duplicate section token")
    f2_lines = [l for l in dup_lines if "F2" in l]
    assert f2_lines, dup_lines
    f2_line = f2_lines[0]
    assert f2_line.count(":") >= 2  # both source:line occurrences quoted
    assert "First" in f2_line and "Second" in f2_line
    assert not any("ok.md" in l for l in dup_lines)  # F1 vs F1b distinct -> no finding


def test_hyphenated_suffix_heading_not_a_token(tmp_path, capsys):
    """Mirrors the real live-corpus pair `H.` / `H-contrast.` — locks
    fullmatch (not prefix-match) grammar for section-token extraction."""
    _write(tmp_path, "convention/heading-pair.md",
           _fm() + "# Title\n\n## H. Title\nbody\n\n### H-contrast. Title\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert not _lines_with(out, "duplicate section token")


def test_dot_directories_skipped(tmp_path, capsys):
    _write(tmp_path, ".omc/state/foo.json", "{}")
    _write(tmp_path, ".omc/whatever.md", "# Should not be scanned\n\n[[dangling-target]]\n")
    _write(tmp_path, "convention/real.md", _fm() + "# Real\n\nbody\n")

    # If dot-dirs were NOT skipped, the dangling wikilink inside .omc/whatever.md
    # would surface as a FAIL and flip the exit code to 1.
    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert ".omc" not in out
    assert "dangling-target" not in out


def test_dangling_wikilink_fails(tmp_path, capsys):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\nSee [[ghost-slug]] and [[b]].\n")
    _write(tmp_path, "convention/b.md", _fm() + "# B\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert _lines_with(out, "FAIL", "ghost-slug")
    assert not _lines_with(out, "FAIL", "[[b]]")


def test_dangling_mdlink_fails(tmp_path, capsys):
    _write(tmp_path, "convention/a.md",
           _fm() + "# A\n\nSee [ghost](ghost.md) and [ok](b.md).\n")
    _write(tmp_path, "convention/b.md", _fm() + "# B\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert _lines_with(out, "FAIL", "ghost.md")
    assert not _lines_with(out, "FAIL", "(b.md)")


def test_prose_section_ref_missing_token_fails(tmp_path, capsys):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\nSee b.md §Z9 and b.md §F1.\n")
    _write(tmp_path, "convention/b.md", _fm() + "# B\n\n### F1 Only\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert _lines_with(out, "FAIL", "Z9")
    assert not _lines_with(out, "FAIL", "§F1")


def test_silently_empty_category_warns(tmp_path, capsys):
    _write(tmp_path, "convention/only.md", _fm() + "# Only\n\nbody\n")
    # `decision/` deliberately never created — a missing category dir has
    # "no content .md" too, so it must be treated the same as an empty one.

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "decision", "WARN", "empty")


def test_documented_empty_category_passes(tmp_path, capsys):
    _write(tmp_path, "convention/only.md", _fm() + "# Only\n\nbody\n")
    (tmp_path / "decision").mkdir()
    (tmp_path / "decision" / ".gitkeep").write_text("", encoding="utf-8")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "decision", "PASS", "documented empty")
    assert not _lines_with(out, "decision", "WARN")


def test_orphan_file_warns(tmp_path, capsys):
    _write(tmp_path, "convention/lonely.md", _fm() + "# Lonely\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "lonely.md", "orphan", "WARN")

    _write(tmp_path, "README.md", "# Wiki\n\nSee convention/lonely.md for details.\n")
    assert owa.main(["--root", str(tmp_path)]) == 0
    out2 = capsys.readouterr().out
    assert not _lines_with(out2, "lonely.md", "orphan")


def test_missing_frontmatter_warns(tmp_path, capsys):
    _write(tmp_path, "convention/nofm.md", "# No Frontmatter\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "nofm.md", "WARN", "no frontmatter")


def test_bad_confidence_warns(tmp_path, capsys):
    _write(tmp_path, "convention/bad.md",
           "---\nconfidence: super-high\nsightings: 1\n---\n# Bad\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "bad.md", "WARN", "confidence")


def test_bad_sightings_warns(tmp_path, capsys):
    _write(tmp_path, "convention/bad.md",
           "---\nconfidence: high\nsightings: many\n---\n# Bad\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "bad.md", "WARN", "sightings")


def test_index_absent_warns(tmp_path, capsys):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\nbody\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "INDEX.md", "WARN", "--write-index")


def test_index_stale_warns(tmp_path, capsys):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\nbody\n")
    _write(tmp_path, "INDEX.md", "# stale content\n")

    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert _lines_with(out, "INDEX.md", "WARN", "stale")


def test_write_index_then_clean(tmp_path, capsys):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\nbody\n")
    _write(tmp_path, "decision/b.md", _fm() + "# B\n\nbody\n")
    _write(tmp_path, "README.md", "# Wiki\n\n[[a]] [[b]]\n")

    assert owa.main(["--root", str(tmp_path), "--write-index"]) == 0
    first_bytes = (tmp_path / "INDEX.md").read_bytes()

    # determinism: two consecutive --write-index runs are byte-identical
    assert owa.main(["--root", str(tmp_path), "--write-index"]) == 0
    second_bytes = (tmp_path / "INDEX.md").read_bytes()
    assert first_bytes == second_bytes

    inv = owa.scan(tmp_path)
    assert first_bytes.decode("utf-8") == owa.render_index(inv)

    capsys.readouterr()
    assert owa.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert not _lines_with(out, "index", "WARN")
    assert not _lines_with(out, "index", "FAIL")


def test_read_only_without_flag(tmp_path):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\nbody\n")
    _write(tmp_path, "decision/b.md", "# B (no frontmatter)\n\nbody\n")  # -> WARN
    _write(tmp_path, "README.md", "# Wiki\n\n[[missing-target]]\n")  # -> FAIL

    def snapshot():
        return {
            str(p.relative_to(tmp_path)): p.read_bytes()
            for p in sorted(tmp_path.rglob("*")) if p.is_file()
        }

    before = snapshot()
    owa.main(["--root", str(tmp_path)])  # no --write-index
    after = snapshot()
    assert before == after


def test_exit_1_on_fail(tmp_path):
    _write(tmp_path, "convention/a.md", _fm() + "# A\n\n[[ghost]]\n")
    assert owa.main(["--root", str(tmp_path)]) == 1
