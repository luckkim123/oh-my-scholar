"""R6 U3 (#37) — tests for `scripts/bib_coupling.py` (stdlib, zero-network,
zero-embeddings bibliographic coupling over per-paper `.bib` reference lists).

Import-under-test idiom matches `tests/test_oms_wiki_audit.py` (importlib
loader off the file path, not a package import).
"""
import importlib.util
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "bib_coupling.py"
spec = importlib.util.spec_from_file_location("bib_coupling", SCRIPT)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)


def _bib(tmp_path, name, entries):
    """entries: list of (doi_or_None, title) tuples -> writes tmp_path/name.bib"""
    lines = []
    for i, (doi, title) in enumerate(entries):
        lines.append(f"@article{{key{i},")
        lines.append(f"  title = {{{title}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        lines.append("}")
    path = tmp_path / name
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def test_doi_keyed_intersection(tmp_path):
    a = _bib(tmp_path, "a.bib", [("10.1000/xyz1", "A Great Paper"), ("10.1000/xyz2", "Another Paper")])
    b = _bib(tmp_path, "b.bib", [("10.1000/XYZ1", "A Great Paper (Copy)"), ("10.1000/xyz3", "Third Paper")])
    refs_a = bc.parse_bib_refs(a)
    refs_b = bc.parse_bib_refs(b)
    assert refs_a & refs_b == {"10.1000/xyz1"}  # DOI matched case-insensitively despite differing titles


def test_title_fallback_normalization_braces_case_punct(tmp_path):
    c = _bib(tmp_path, "c.bib", [(None, "Robust {SLAM} for Underwater Vehicles")])
    d = _bib(tmp_path, "d.bib", [(None, "Robust SLAM, for underwater vehicles!")])
    refs_c = bc.parse_bib_refs(c)
    refs_d = bc.parse_bib_refs(d)
    assert refs_c == refs_d
    assert refs_c == {"robustslamforunderwatervehicles"}


def test_threshold_behavior_min_shared(tmp_path, capsys):
    a = _bib(tmp_path, "a.bib", [("10.1/x", "P")])
    b = _bib(tmp_path, "b.bib", [("10.1/x", "Q")])
    assert bc.main([str(a), str(b)]) == 0  # default --min-shared=2, only 1 shared ref
    out = capsys.readouterr().out
    assert "[singleton" in out and "[cluster" not in out

    assert bc.main([str(a), str(b), "--min-shared", "1"]) == 0
    out = capsys.readouterr().out
    assert "[cluster 1] a, b" in out


def test_connected_component_merging(tmp_path, capsys):
    a = _bib(tmp_path, "a.bib", [("10.1/s1", "s1"), ("10.1/s2", "s2")])
    b = _bib(tmp_path, "b.bib", [("10.1/s1", "s1"), ("10.1/s2", "s2"), ("10.1/s3", "s3"), ("10.1/s4", "s4")])
    c = _bib(tmp_path, "c.bib", [("10.1/s3", "s3"), ("10.1/s4", "s4")])
    assert bc.main([str(a), str(b), str(c)]) == 0  # default --min-shared=2: a-b share 2, b-c share 2, a-c share 0
    out = capsys.readouterr().out
    assert "[cluster 1] a, b, c" in out  # union-find merges through the shared middle paper b


def test_singleton_isolation(tmp_path, capsys):
    a = _bib(tmp_path, "a.bib", [("10.1/x", "X"), ("10.1/y", "Y")])
    b = _bib(tmp_path, "b.bib", [("10.1/x", "X"), ("10.1/y", "Y")])
    e = _bib(tmp_path, "e.bib", [("10.1/nomatch", "Unrelated")])
    assert bc.main([str(a), str(b), str(e)]) == 0
    out = capsys.readouterr().out
    assert "[cluster 1] a, b" in out
    assert "[singleton 2] e" in out


def test_json_shape(tmp_path, capsys):
    a = _bib(tmp_path, "a.bib", [("10.1/x", "X"), ("10.1/y", "Y")])
    b = _bib(tmp_path, "b.bib", [("10.1/x", "X"), ("10.1/y", "Y")])
    assert bc.main([str(a), str(b), "--json"]) == 0
    out = capsys.readouterr().out
    import json
    data = json.loads(out)
    assert set(data.keys()) == {"min_shared", "clusters", "pairs"}
    assert data["clusters"] == [["a", "b"]]
    assert data["pairs"] == [{"a": "a", "b": "b", "shared": ["10.1/x", "10.1/y"]}]


def test_usage_error_exit_2_missing_args():
    with pytest.raises(SystemExit) as exc:
        bc.main([])
    assert exc.value.code == 2


def test_usage_error_exit_2_missing_file(tmp_path, capsys):
    missing = tmp_path / "nope.bib"
    assert bc.main([str(missing)]) == 2
    err = capsys.readouterr().err
    assert "error" in err


def test_zero_network_guarantee():
    source = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"\burllib\b", source), "bib_coupling.py must stay zero-network (E3)"
    assert not re.search(r"\bsocket\b", source), "bib_coupling.py must stay zero-network (E3)"


def test_entry_re_matches_cite_guard_pattern():
    """Read-only reuse lock: ENTRY_RE re-derives hooks/scholar_cite_guard.py:25 (never edit hooks/)."""
    guard = (Path(__file__).parent.parent / "hooks" / "scholar_cite_guard.py").read_text(encoding="utf-8")
    m = re.search(r"ENTRY_RE = re\.compile\((.+)\)", guard)
    assert m, "hooks/scholar_cite_guard.py ENTRY_RE pattern not found"
    assert bc.ENTRY_RE.pattern == eval(m.group(1))


def test_title_field_not_matched_inside_booktitle():
    """M1 regression: `booktitle` before `title` (or alone) must never be read as the title."""
    entry = '@inproceedings{k1,\n  booktitle = {Proc of ICRA},\n  title = {Real Title},\n}'
    assert bc._extract_field(entry, "title") == "Real Title"
    only_book = '@inproceedings{k2,\n  booktitle = {Proc of ICRA},\n}'
    assert bc._extract_field(only_book, "title") is None


def test_identity_key_strips_doi_url_prefix():
    """M2 regression: 10.1/x must couple with its https://doi.org/ (and dx.doi.org) URL form."""
    bare = bc.identity_key("10.1/X", "")
    assert bare == "10.1/x"
    assert bc.identity_key("https://doi.org/10.1/X", "") == bare
    assert bc.identity_key("http://dx.doi.org/10.1/x", "") == bare
