"""Tests for the DOI/retraction pre-gate (R1 #2). Network is always faked —
verdict logic must be fully testable offline; --record writes the allowlist
atomically and refuses non-VERIFIED."""
import importlib.util
import json
import urllib.error
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "verify_bib_entry.py"
spec = importlib.util.spec_from_file_location("verify_bib_entry", SCRIPT)
vbe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vbe)

CROSSREF_OK = {"message": {"title": ["Deep Learning for Sonar"], "author": [{"family": "Smith"}], "update-to": []}}
CROSSREF_RETRACTED = {"message": {"title": ["Bad Paper"], "author": [], "update-to": [{"type": "retraction"}]}}
OPENALEX_OK = {"display_name": "Deep Learning for Sonar", "is_retracted": False}


def test_verified_by_crossref():
    v = vbe.verify("smith2024", "10.1/x", "Deep Learning for Sonar", "Smith", fetch=lambda url: CROSSREF_OK)
    assert v.verdict == "VERIFIED" and v.source == "crossref"


def test_title_mismatch():
    v = vbe.verify("smith2024", "10.1/x", "Completely Different Topic Entirely", None, fetch=lambda url: CROSSREF_OK)
    assert v.verdict == "MISMATCH"


def test_retraction_detected():
    v = vbe.verify("bad2020", "10.1/y", None, None, fetch=lambda url: CROSSREF_RETRACTED)
    assert v.verdict == "RETRACTED"


def test_openalex_fallback():
    def fetch(url):
        if "crossref" in url:
            raise urllib.error.HTTPError(url, 404, "nf", None, None)
        return OPENALEX_OK
    v = vbe.verify("smith2024", "10.1/x", "Deep Learning for Sonar", None, fetch=fetch)
    assert v.verdict == "VERIFIED" and v.source == "openalex"


def test_not_found_anywhere():
    def fetch(url):
        raise urllib.error.HTTPError(url, 404, "nf", None, None)
    assert vbe.verify("ghost", "10.1/z", None, None, fetch=fetch).verdict == "NOT_FOUND"


def test_network_error_is_not_a_verdict():
    def fetch(url):
        raise urllib.error.URLError("offline")
    assert vbe.verify("k", "10.1/x", None, None, fetch=fetch).verdict == "NETWORK_ERROR"


def test_record_writes_allowlist(tmp_path):
    v = vbe.Verdict("VERIFIED", "crossref", "ok", doi="10.1/x", title="T")
    vbe.record("smith2024", v, state_dir=tmp_path)
    data = json.loads((tmp_path / "verified-citations.json").read_text())
    assert data["keys"]["smith2024"]["doi"] == "10.1/x"
    vbe.record("kim2023", vbe.Verdict("VERIFIED", "openalex", "ok", doi="10.2/y", title="U"), state_dir=tmp_path)
    data = json.loads((tmp_path / "verified-citations.json").read_text())
    assert set(data["keys"]) == {"smith2024", "kim2023"}  # merge, not overwrite


def test_record_refuses_unverified(tmp_path):
    try:
        vbe.record("ghost", vbe.Verdict("NOT_FOUND", "crossref", "nf"), state_dir=tmp_path)
        assert False, "must raise"
    except ValueError:
        pass
    assert not (tmp_path / "verified-citations.json").exists()


def test_never_touches_bib_and_stdlib_only():
    src = SCRIPT.read_text()
    assert "NEVER writes .bib" in src  # docstring contract line (guard intent)
    assert "import requests" not in src and "import a2a" not in src  # stdlib only
    assert "atomic_write_json" in src  # allowlist write goes through oms_atomic


# --- _verify_by_title: no-DOI bibliographic-search fallback ---

CROSSREF_SEARCH_MATCH = {
    "message": {
        "items": [
            {"title": ["Attention Is All You Need"], "DOI": "10.1/attn", "author": [{"family": "Vaswani"}]},
        ]
    }
}
CROSSREF_SEARCH_LOW_SIMILARITY = {
    "message": {
        "items": [
            {"title": ["A Completely Unrelated Survey On Gardening"], "DOI": "10.1/other", "author": []},
        ]
    }
}
CROSSREF_SEARCH_AUTHOR_MISMATCH = {
    "message": {
        "items": [
            {"title": ["Attention Is All You Need"], "DOI": "10.1/attn", "author": [{"family": "Smith"}]},
        ]
    }
}


def test_verify_by_title_confident_match_verified():
    v = vbe.verify("vaswani2017", None, "Attention Is All You Need", "Vaswani", fetch=lambda url: CROSSREF_SEARCH_MATCH)
    assert v.verdict == "VERIFIED" and v.doi == "10.1/attn"


def test_verify_by_title_low_similarity_not_found():
    v = vbe.verify("ghost", None, "Attention Is All You Need", None, fetch=lambda url: CROSSREF_SEARCH_LOW_SIMILARITY)
    assert v.verdict == "NOT_FOUND"


def test_verify_by_title_author_mismatch_not_found():
    v = vbe.verify("fake2017", None, "Attention Is All You Need", "Vaswani", fetch=lambda url: CROSSREF_SEARCH_AUTHOR_MISMATCH)
    assert v.verdict == "NOT_FOUND" and "author does not match" in v.detail


# --- _verify_by_doi exception fallback (Crossref -> OpenAlex) ---


def test_doi_urlerror_short_circuits_without_openalex_retry():
    calls = []

    def fetch(url):
        calls.append(url)
        raise urllib.error.URLError("offline")

    v = vbe.verify("k", "10.1/x", "t", "a", fetch=fetch)
    assert v.verdict == "NETWORK_ERROR" and v.source == "crossref"
    assert len(calls) == 1 and "crossref" in calls[0]  # openalex never attempted


def test_doi_httperror_then_openalex_urlerror_is_network_error():
    def fetch(url):
        if "crossref" in url:
            raise urllib.error.HTTPError(url, 404, "nf", None, None)
        raise urllib.error.URLError("offline")

    v = vbe.verify("k", "10.1/x", "t", "a", fetch=fetch)
    assert v.verdict == "NETWORK_ERROR" and v.source == "openalex"


# --- main(): verdict -> process exit code mapping ---


@pytest.mark.parametrize(
    "verdict,expected_code",
    [("VERIFIED", 0), ("MISMATCH", 1), ("RETRACTED", 1), ("NOT_FOUND", 1), ("NETWORK_ERROR", 2)],
)
def test_main_maps_verdict_to_exit_code(monkeypatch, verdict, expected_code):
    monkeypatch.setattr(vbe, "verify", lambda *a, **kw: vbe.Verdict(verdict, "crossref", "x", doi="10.1/x"))
    assert vbe.main(["--key", "k", "--doi", "10.1/x"]) == expected_code
