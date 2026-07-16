"""R4 #23/#25 — read-only wiki health-audit CLI over ONE `.oms/wiki/` tree
per invocation (no ascent — `references/wiki/README.md`'s two-layer model;
run once per level, local then global).

Six *mechanical* dimensions, each a pure function over an in-memory
`scan()` inventory (unit-testable without I/O): duplicate section tokens,
dangling cross-refs, empty/orphan categories, frontmatter validity,
INDEX.md drift, and open actionable gaps (`status: open-gap` enumeration). The single opt-in write path is `--write-index`, which
(re)generates `<root>/INDEX.md` via `atomic_write_text` (`hooks/oms_atomic.py:69`)
— a derived artifact, never hand-edited, never "repaired" content.

Two *judgment* dimensions — SSOT-delegation integrity and strength-tag
discipline — require reading meaning and are deliberately NOT here: they
stay card-run (an LLM auditor following a written procedure), documented at
`references/wiki/audit.md`. This script covers only what can be decided
mechanically.
"""
import argparse
import os
import posixpath
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from oms_atomic import atomic_write_text  # noqa: E402

CATEGORIES = ("convention", "pattern", "decision", "reference", "history")
META_FILENAMES = ("README.md", "INDEX.md")
CONFIDENCE_VALUES = {"high", "med", "low"}
# Family wiki-status convention (soft/warn only — oms has no launch boundary to
# refuse at): `open-gap` = an unresolved reviewer/audit finding that must ride
# every summary until closed; `resolved` = terminal. Absent = not actionable.
STATUS_VALUES = {"open-gap", "resolved"}

_H1_RE = re.compile(r'^#(?!#)\s+(.+?)\s*$')
_HEADING_RE = re.compile(r'^#{2,}\s+(\S+)')
_TOKEN_RE = re.compile(r'§?[A-Z][0-9]*[a-z]?')
_WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')
_MDLINK_RE = re.compile(r'(?<!!)\[([^\[\]]*)\]\(([^()\s]+\.md)\)')
_PROSE_SECTION_RE = re.compile(r'([A-Za-z0-9_\-./]+\.md)\s+§([A-Za-z0-9]+)')


# ------------------------------------------------------------------- scan
def _parse_frontmatter(text):
    """Thin, stdlib-only splitter (no PyYAML): lines between leading `---`
    fences, `key: value` split on first colon. Returns `(fm, status)` where
    status is `"ok"`, `"absent"` (no opening `---` fence at all), or
    `"malformed"` (opening fence present but no closing `---` fence found —
    the one malformation this splitter can actually distinguish; a
    colon-less key line inside a well-fenced block is silently skipped, not
    a new status, per T8 scope)."""
    if not text.startswith("---"):
        return {}, "absent"
    end = text.find("\n---", 3)
    if end == -1:
        return {}, "malformed"
    fm = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm, "ok"


def _extract_h1(text):
    for line in text.splitlines():
        m = _H1_RE.match(line)
        if m:
            return m.group(1)
    return None


def _extract_tokens(text):
    """Section-token extraction is `re.fullmatch`, never prefix-match: first
    word of a `^##+ ` heading, strip exactly one trailing '.' or ':', require
    the WHOLE remainder to fullmatch `§?[A-Z][0-9]*[a-z]?`."""
    tokens = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = _HEADING_RE.match(line)
        if not m:
            continue
        candidate = m.group(1)
        if candidate and candidate[-1] in ".:":
            candidate = candidate[:-1]
        if not candidate or not _TOKEN_RE.fullmatch(candidate):
            continue
        token = candidate[1:] if candidate.startswith("§") else candidate
        tokens.append({"token": token, "line_no": i, "line": line.rstrip()})
    return tokens


def _extract_refs(text):
    refs = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in _WIKILINK_RE.finditer(line):
            refs.append({"type": "wikilink", "target": m.group(1), "line_no": i, "raw": m.group(0)})
        for m in _MDLINK_RE.finditer(line):
            refs.append({"type": "mdlink", "target": m.group(2), "line_no": i, "raw": m.group(0)})
        for m in _PROSE_SECTION_RE.finditer(line):
            refs.append({
                "type": "prose_section", "target": m.group(1), "section": m.group(2),
                "line_no": i, "raw": m.group(0),
            })
    return refs


def scan(root) -> dict:
    """Walk the tree once, skipping dot-directories entirely (`.omc`, `.git`
    and kin are not wiki content — a stray `.omc/state/` must not surface).
    Returns `{"root": Path, "files": [file-record, ...]}`."""
    root = Path(root)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for fname in sorted(filenames):
            if not fname.endswith(".md"):
                continue
            fpath = Path(dirpath) / fname
            relpath = fpath.relative_to(root).as_posix()
            text = fpath.read_text(encoding="utf-8")
            frontmatter, frontmatter_status = _parse_frontmatter(text)
            files.append({
                "relpath": relpath,
                "name": fname,
                "text": text,
                "frontmatter": frontmatter,
                "frontmatter_status": frontmatter_status,
                "h1": _extract_h1(text),
                "tokens": _extract_tokens(text),
                "refs": _extract_refs(text),
            })
    return {"root": root, "files": files}


# --------------------------------------------------------- ref resolution
def _resolve_ref_file(ref, source_relpath, by_relpath, by_stem):
    """Resolve a ref's TARGET FILE (ignoring §-token existence). Returns the
    file record or None."""
    if ref["type"] == "wikilink":
        cands = by_stem.get(ref["target"])
        return cands[0] if cands else None
    target = ref["target"]
    resolved_rel = posixpath.normpath(posixpath.join(posixpath.dirname(source_relpath), target))
    if resolved_rel in by_relpath:
        return by_relpath[resolved_rel]
    if "/" not in target:
        cands = by_stem.get(posixpath.splitext(target)[0])
        if cands:
            return cands[0]
    return None


def _build_lookups(files):
    by_relpath = {f["relpath"]: f for f in files}
    by_stem = {}
    for f in files:
        by_stem.setdefault(posixpath.splitext(f["relpath"])[0].rsplit("/", 1)[-1], []).append(f)
    return by_relpath, by_stem


# --------------------------------------------------------- check_duplicate_tokens
def check_duplicate_tokens(inv) -> list:
    """Same token twice in ONE file -> FAIL per duplicate, quoting all
    occurrences with line numbers. `F1` vs `F1b` are distinct tokens."""
    rows = []
    for f in inv["files"]:
        by_token = {}
        for t in f["tokens"]:
            by_token.setdefault(t["token"], []).append(t)
        for token, occurrences in sorted(by_token.items()):
            if len(occurrences) < 2:
                continue
            quotes = "; ".join(f'{f["relpath"]}:{o["line_no"]} "{o["line"]}"' for o in occurrences)
            rows.append({
                "status": "FAIL",
                "message": f"duplicate section token {token!r} in {f['relpath']}: {quotes}",
            })
    return rows


# --------------------------------------------------------- check_dangling_refs
def check_dangling_refs(inv) -> list:
    """`[[slug]]` resolves iff some file's stem equals the slug anywhere in
    the tree; `[text](x.md)` resolves relative to the source file's
    directory (plus tree-wide stem fallback for bare names); `file.md §S`
    resolves iff the file exists AND has token `S`. INDEX.md is excluded as
    a *source* (generated)."""
    files = inv["files"]
    by_relpath, by_stem = _build_lookups(files)
    tokens_by_relpath = {f["relpath"]: {t["token"] for t in f["tokens"]} for f in files}

    rows = []
    for f in files:
        if f["name"] == "INDEX.md":
            continue
        for ref in f["refs"]:
            target_file = _resolve_ref_file(ref, f["relpath"], by_relpath, by_stem)
            if target_file is None:
                kind = {"wikilink": "wikilink", "mdlink": "mdlink", "prose_section": "prose §-ref"}[ref["type"]]
                rows.append({
                    "status": "FAIL",
                    "message": f'{kind} dangling: {f["relpath"]}:{ref["line_no"]} -> {ref["raw"]}',
                })
                continue
            if ref["type"] == "prose_section" and ref["section"] not in tokens_by_relpath[target_file["relpath"]]:
                rows.append({
                    "status": "FAIL",
                    "message": (
                        f'prose §-ref dangling (file has no token {ref["section"]!r}): '
                        f'{f["relpath"]}:{ref["line_no"]} -> {ref["raw"]}'
                    ),
                })
    return rows


# --------------------------------------------------------- check_empty_and_orphan
def check_empty_and_orphan(inv, root) -> list:
    """Category universe = the fixed five names directly under root. A
    category dir with no content `.md` -> WARN unless `.gitkeep`/README
    documents it -> PASS. A content file with zero inbound refs AND no
    mention in any README/INDEX -> WARN candidate orphan. README.md/INDEX.md
    themselves are exempt from orphan checks."""
    root = Path(root)
    files = inv["files"]
    rows = []

    for cat in CATEGORIES:
        cat_files = [
            f for f in files
            if f["relpath"].split("/")[0] == cat and f["name"] not in META_FILENAMES
        ]
        if cat_files:
            continue
        documented = (root / cat / ".gitkeep").is_file() or (root / cat / "README.md").is_file()
        if documented:
            rows.append({"status": "PASS", "message": f"{cat}/: documented empty"})
        else:
            rows.append({
                "status": "WARN",
                "message": f"{cat}/: silently empty (no content .md, no .gitkeep/README placeholder)",
            })

    by_relpath, by_stem = _build_lookups(files)
    inbound = set()
    for f in files:
        for ref in f["refs"]:
            target_file = _resolve_ref_file(ref, f["relpath"], by_relpath, by_stem)
            # A file linking to itself is not an "OTHER file" referrer (spec:
            # "zero inbound refs from any OTHER file") -- exclude self-refs.
            if target_file is not None and target_file["relpath"] != f["relpath"]:
                inbound.add(target_file["relpath"])

    mention_text = "\n".join(f["text"] for f in files if f["name"] in META_FILENAMES)
    for f in files:
        if f["name"] in META_FILENAMES:
            continue
        if f["relpath"] in inbound:
            continue
        # Exact-name match, not substring: plain `in` would let "b.md" match
        # inside "web.md". `\b` alone doesn't fix this either, since '-' is a
        # regex word-boundary character too (e.g. "web.md" still matches
        # "b.md" right after a hyphen) -- use an explicit non-filename-char
        # lookaround instead.
        name_pattern = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(f["name"]) + r"(?![A-Za-z0-9_-])")
        if name_pattern.search(mention_text):
            continue
        rows.append({
            "status": "WARN",
            "message": f'{f["relpath"]}: candidate orphan (no inbound refs, no README/INDEX mention)',
        })

    return rows


# --------------------------------------------------------- check_frontmatter
def check_frontmatter(inv) -> list:
    """Content file with no opening `---` fence -> WARN "no frontmatter";
    opening fence with no closing fence -> WARN "malformed frontmatter"
    (T8 #2 split — the two are distinguishable, unlike a colon-less key line
    inside a well-fenced block, which is out of scope). `confidence` outside
    {high,med,low} or `sightings` non-integer -> WARN. Never FAIL (#24
    non-blocking philosophy). README.md/INDEX.md exempt."""
    rows = []
    for f in inv["files"]:
        if f["name"] in META_FILENAMES:
            continue
        status = f["frontmatter_status"]
        if status == "absent":
            rows.append({"status": "WARN", "message": f'{f["relpath"]}: no frontmatter'})
            continue
        if status == "malformed":
            rows.append({
                "status": "WARN",
                "message": f'{f["relpath"]}: malformed frontmatter (opening --- fence with no closing --- fence)',
            })
            continue
        fm = f["frontmatter"]
        if "confidence" in fm and fm["confidence"] not in CONFIDENCE_VALUES:
            rows.append({
                "status": "WARN",
                "message": f'{f["relpath"]}: confidence {fm["confidence"]!r} not in {sorted(CONFIDENCE_VALUES)}',
            })
        if "sightings" in fm:
            try:
                int(fm["sightings"])
            except ValueError:
                rows.append({
                    "status": "WARN",
                    "message": f'{f["relpath"]}: sightings {fm["sightings"]!r} is not an integer',
                })
        if "status" in fm and fm["status"] not in STATUS_VALUES:
            # a typo'd status silently exits open-gap enumeration -> WARN it.
            rows.append({
                "status": "WARN",
                "message": f'{f["relpath"]}: status {fm["status"]!r} not in {sorted(STATUS_VALUES)}',
            })
    return rows


# --------------------------------------------------------- check_open_gaps
def check_open_gaps(inv) -> list:
    """Enumerate every note flagged `status: open-gap` — keyword-independent by
    construction (walks the whole tree, not a ranked query), so a reviewer/audit
    finding recorded here rides every audit close until it is resolved
    (`status: resolved`) or explicitly deferred in scholar-verify. WARN only:
    oms has no launch boundary to refuse at. `resolved`/absent do not surface."""
    rows = []
    for f in inv["files"]:
        if f["name"] in META_FILENAMES:
            continue
        if f["frontmatter"].get("status") == "open-gap":
            blocked = f["frontmatter"].get("blocked-on")
            suffix = f" (blocked-on: {blocked})" if blocked else ""
            rows.append({
                "status": "WARN",
                "message": f'{f["relpath"]}: open gap{suffix} — carry into scholar-verify or resolve',
            })
    return rows


# --------------------------------------------------------- render_index / check_index
def render_index(inv) -> str:
    """Deterministic: categories sorted, files sorted by name (relpath sort
    achieves both, since relpath = `<category>/<filename>.md`)."""
    content_files = sorted(
        (f for f in inv["files"] if f["name"] not in META_FILENAMES),
        key=lambda f: f["relpath"],
    )
    lines = ["# Wiki INDEX — generated by scripts/oms_wiki_audit.py — do not hand-edit", ""]
    for f in content_files:
        fm = f["frontmatter"]
        title = f["h1"] or "(untitled)"
        confidence = fm.get("confidence", "?")
        sightings = fm.get("sightings", "?")
        lines.append(f"- `{f['relpath']}` — {title} (confidence: {confidence}, sightings: {sightings})")
    return "\n".join(lines) + "\n"


def check_index(inv, root) -> list:
    """INDEX.md absent -> WARN "run --write-index"; present but != render_index
    output -> WARN "stale"."""
    index_path = Path(root) / "INDEX.md"
    if not index_path.is_file():
        return [{"status": "WARN", "message": "INDEX.md missing — run --write-index to generate it"}]
    current = index_path.read_text(encoding="utf-8")
    expected = render_index(inv)
    if current != expected:
        return [{
            "status": "WARN",
            "message": "INDEX.md is stale — content differs from render_index(); run --write-index to regenerate",
        }]
    return []


# ------------------------------------------------------------------- main
def _err(message) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read-only wiki health audit (mechanical dimensions) + INDEX generation.")
    ap.add_argument("--root", default="./.oms/wiki")
    ap.add_argument("--write-index", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        return _err(f"--root {args.root!r} does not exist")

    inv = scan(root)
    if args.write_index:
        atomic_write_text(root / "INDEX.md", render_index(inv))
        inv = scan(root)  # re-scan so the printed report reflects the just-written INDEX

    dimensions = [
        ("duplicate_tokens", check_duplicate_tokens(inv)),
        ("dangling_refs", check_dangling_refs(inv)),
        ("empty_and_orphan", check_empty_and_orphan(inv, root)),
        ("frontmatter", check_frontmatter(inv)),
        ("open_gaps", check_open_gaps(inv)),
        ("index", check_index(inv, root)),
    ]

    any_fail = False
    for name, rows in dimensions:
        for row in rows:
            print(f"[{row['status']}] {name}: {row['message']}")
            if row["status"] == "FAIL":
                any_fail = True
        if not rows:
            print(f"[PASS] {name}: no issues found")
        else:
            worst = "FAIL" if any(r["status"] == "FAIL" for r in rows) else (
                "WARN" if any(r["status"] == "WARN" for r in rows) else "PASS"
            )
            print(f"[{worst}] {name}: {len(rows)} finding(s)")

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
