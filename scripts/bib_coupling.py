"""R6 U3 (#37) — bibliographic coupling over per-paper `.bib` reference lists.

Input contract (E3): each input `.bib` file is ONE paper's own reference
list (exported from a publisher/Zotero/OpenAlex `referenced_works` dump) —
NOT that paper's citation-entry file. Two papers are "coupled" when their
reference lists overlap; clusters are connected components over pairs whose
overlap meets `--min-shared`. Output is an advisory, mechanical seed for
`scholar-research`'s landscape map (`skill-bodies/scholar-research/SKILL.md`
Step 2) — never a citation source, never network, never embeddings.

Parsing idioms (read-only reuse, never edits the originals):
- `ENTRY_RE` re-derives `hooks/scholar_cite_guard.py:25` (entry-key regex).
- `_norm()` re-derives `verify_bib_entry.py:36` (title normalization).
- Per-entry DOI/title field extraction is new parsing work (no existing
  idiom covers it) — a small balanced-brace/quoted-string scanner, stdlib
  only, zero network.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s{}]+)\s*,")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _extract_field(entry: str, field: str) -> str:
    m = re.search(rf"{field}\s*=\s*", entry, re.IGNORECASE)
    if not m:
        return None
    rest = entry[m.end():]
    if rest.startswith("{"):
        depth = 0
        for i, ch in enumerate(rest):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return rest[1:i]
        return None
    if rest.startswith('"'):
        end = rest.find('"', 1)
        return rest[1:end] if end != -1 else None
    m2 = re.match(r"([^,\n}]+)", rest)
    return m2.group(1).strip() if m2 else None


def split_entries(text: str) -> list:
    matches = list(ENTRY_RE.finditer(text))
    spans = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        spans.append(text[m.start():end])
    return spans


def identity_key(doi: str, title: str) -> str:
    if doi:
        return doi.strip().lower()
    return _norm(title)


def parse_bib_refs(path: Path) -> set:
    text = path.read_text(encoding="utf-8")
    refs = set()
    for entry in split_entries(text):
        key = identity_key(_extract_field(entry, "doi"), _extract_field(entry, "title"))
        if key:
            refs.add(key)
    return refs


def connected_components(items, edges) -> list:
    parent = {i: i for i in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    groups = {}
    for i in items:
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def _err(message) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Bibliographic coupling over per-paper .bib reference lists "
        "(stdlib only, zero network, zero embeddings — advisory seed, not a citation source)."
    )
    ap.add_argument("bibs", nargs="+", metavar="BIB", help="one .bib file per paper's reference list")
    ap.add_argument("--min-shared", type=int, default=2, help="minimum shared references to link two papers (default: 2)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of the human report")
    args = ap.parse_args(argv)

    papers = {}
    for raw in args.bibs:
        path = Path(raw)
        if not path.is_file():
            return _err(f"not a file: {raw!r}")
        papers[path.stem] = parse_bib_refs(path)

    names = sorted(papers)
    pairs = []
    shared_of = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            shared = papers[a] & papers[b]
            if len(shared) >= args.min_shared:
                pairs.append((a, b))
                shared_of[(a, b)] = sorted(shared)

    clusters = sorted((sorted(c) for c in connected_components(names, pairs)), key=lambda c: (-len(c), c))

    if args.json:
        print(json.dumps({
            "min_shared": args.min_shared,
            "clusters": clusters,
            "pairs": [{"a": a, "b": b, "shared": shared_of[(a, b)]} for a, b in pairs],
        }, indent=2))
        return 0

    print(f"Bibliographic coupling — {len(names)} paper(s), --min-shared={args.min_shared}")
    for idx, cluster in enumerate(clusters, 1):
        label = "cluster" if len(cluster) > 1 else "singleton"
        print(f"\n[{label} {idx}] {', '.join(cluster)}")
        for a, b in pairs:
            if a in cluster and b in cluster:
                print(f"    {a} <-> {b}: {len(shared_of[(a, b)])} shared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
