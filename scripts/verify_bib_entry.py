"""Mechanical DOI/retraction pre-gate (R1 #2).

This script NEVER writes .bib — it verifies against Crossref (retraction
records included) with OpenAlex fallback and, on --record, appends the key
to the cite-guard allowlist. The human gate stays: MISMATCH/RETRACTED/
NOT_FOUND are never recordable.
"""
import argparse
import dataclasses
import difflib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from oms_atomic import atomic_write_json  # noqa: E402

MATCH_THRESHOLD = 0.75
NO_DOI_THRESHOLD = 0.9


@dataclasses.dataclass
class Verdict:
    verdict: str  # VERIFIED | MISMATCH | RETRACTED | NOT_FOUND | NETWORK_ERROR
    source: str
    detail: str
    doi: str = None
    title: str = None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _title_matches(a: str, b: str, threshold: float) -> bool:
    if not a or not b:
        return True  # nothing to compare against — not a mismatch signal
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio() >= threshold


def _author_matches(family: str, authors: list) -> bool:
    if not family:
        return True
    family_l = family.strip().lower()
    return any((a.get("family") or "").strip().lower() == family_l for a in authors or [])


def _mailto_suffix(sep: str = "?") -> str:
    import os

    mailto = os.environ.get("OMS_CROSSREF_MAILTO")
    return f"{sep}mailto={quote(mailto)}" if mailto else ""


def fetch_json(url, timeout=10) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "oms-verify-bib"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _is_retracted(update_to: list) -> bool:
    return any("retract" in (u.get("type") or "").lower() for u in update_to or [])


def _verify_crossref_by_doi(doi, title, author, fetch):
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}" + _mailto_suffix()
    data = fetch(url)
    message = data.get("message", {})
    if _is_retracted(message.get("update-to")):
        return Verdict("RETRACTED", "crossref", "update-to type contains 'retract'", doi=doi)
    msg_titles = message.get("title") or []
    msg_title = msg_titles[0] if msg_titles else None
    if not _title_matches(title, msg_title, MATCH_THRESHOLD):
        return Verdict("MISMATCH", "crossref", f"title mismatch: {msg_title!r} vs {title!r}", doi=doi, title=msg_title)
    if not _author_matches(author, message.get("author")):
        return Verdict("MISMATCH", "crossref", f"author {author!r} not found", doi=doi, title=msg_title)
    return Verdict("VERIFIED", "crossref", "doi/title/author match", doi=doi, title=msg_title)


def _verify_openalex_by_doi(doi, title, author, fetch):
    url = f"https://api.openalex.org/works/doi:{quote(doi, safe='')}"
    data = fetch(url)
    if data.get("is_retracted"):
        return Verdict("RETRACTED", "openalex", "is_retracted=true", doi=doi)
    oa_title = data.get("display_name")
    if not _title_matches(title, oa_title, MATCH_THRESHOLD):
        return Verdict("MISMATCH", "openalex", f"title mismatch: {oa_title!r} vs {title!r}", doi=doi, title=oa_title)
    return Verdict("VERIFIED", "openalex", "doi/title match", doi=doi, title=oa_title)


def _verify_by_doi(doi, title, author, fetch):
    try:
        return _verify_crossref_by_doi(doi, title, author, fetch)
    except urllib.error.HTTPError:
        pass
    except urllib.error.URLError:
        return Verdict("NETWORK_ERROR", "crossref", "network unreachable", doi=doi)
    try:
        return _verify_openalex_by_doi(doi, title, author, fetch)
    except urllib.error.HTTPError:
        return Verdict("NOT_FOUND", "openalex", "not found on crossref or openalex", doi=doi)
    except urllib.error.URLError:
        return Verdict("NETWORK_ERROR", "openalex", "network unreachable", doi=doi)


def _verify_by_title(key, title, author, fetch):
    url = f"https://api.crossref.org/works?query.bibliographic={quote(title)}&rows=5" + _mailto_suffix("&")
    try:
        data = fetch(url)
    except urllib.error.HTTPError:
        return Verdict("NOT_FOUND", "crossref", "no bibliographic search results")
    except urllib.error.URLError:
        return Verdict("NETWORK_ERROR", "crossref", "network unreachable")
    items = data.get("message", {}).get("items", [])
    best = None
    best_ratio = -1.0
    for item in items:
        item_titles = item.get("title") or []
        item_title = item_titles[0] if item_titles else None
        ratio = difflib.SequenceMatcher(None, _norm(title), _norm(item_title)).ratio() if item_title else 0.0
        if ratio > best_ratio:
            best, best_ratio = item, ratio
    if best is None or best_ratio < NO_DOI_THRESHOLD:
        return Verdict("NOT_FOUND", "crossref", "no confident bibliographic match")
    if not _author_matches(author, best.get("author")):
        return Verdict("NOT_FOUND", "crossref", "best title match but author does not match")
    candidate_doi = best.get("DOI")
    candidate_title = (best.get("title") or [None])[0]
    return Verdict("VERIFIED", "crossref", f"candidate-doi:{candidate_doi}", doi=candidate_doi, title=candidate_title)


def verify(key, doi, title, author, fetch=fetch_json) -> Verdict:
    if doi:
        return _verify_by_doi(doi, title, author, fetch)
    if title:
        return _verify_by_title(key, title, author, fetch)
    return Verdict("NOT_FOUND", "none", "no doi or title provided")


def record(key, verdict: Verdict, state_dir) -> None:
    if verdict.verdict != "VERIFIED":
        raise ValueError(f"refusing to record non-VERIFIED verdict ({verdict.verdict}) for key {key!r}")
    target = Path(state_dir) / "verified-citations.json"
    data = {"keys": {}}
    if target.is_file():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {"keys": {}}
    data.setdefault("keys", {})[key] = {
        "doi": verdict.doi,
        "title": verdict.title,
        "source": verdict.source,
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write_json(target, data)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical DOI/retraction pre-gate for cite-guard.")
    parser.add_argument("--key", required=True)
    parser.add_argument("--doi", default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--author", default=None)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--state-dir", default="./.oms/state")
    args = parser.parse_args(argv)

    v = verify(args.key, args.doi, args.title, args.author)
    print(f"VERDICT={v.verdict} key={args.key} source={v.source} detail={v.detail}")

    if args.record and v.verdict == "VERIFIED":
        record(args.key, v, state_dir=args.state_dir)

    if v.verdict == "VERIFIED":
        return 0
    if v.verdict == "NETWORK_ERROR":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
