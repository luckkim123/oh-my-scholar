"""Re-entry lint (om* store-unification P2/P4, store-spec.md §9.5): no new
code may hardcode EITHER root string literal — the legacy `.oms` or the
unified `.hq` — outside `hooks/oms_paths.py`, the ONE allowed declaration
site (`LEGACY_ROOT` / `HQ_ROOT`). P2 moved every existing inline `.oms`/...
computation behind named helpers in that module; this test is the guard that
stops the literal from creeping back in.

P4 widened this from one literal to two. Guarding only the legacy root would
have left the new root free to spread through the hooks during the very
refactor that exists to prevent exactly that — the cutover is when a root
string is most likely to be re-typed, not least.

Exact rule (from the P2 contract, unchanged in shape by the P4 widening):
- Parse each target `.py` with `ast`; inspect every `ast.Constant` whose
  value is `str` (this also walks `JoinedStr`/f-string literal pieces, since
  `ast.walk` descends into them).
- VIOLATION = the string contains a root literal (`.oms` or `.hq`) AND
  contains no whitespace character. A path never has a space; prose always
  does (".omp/STRUCTURE.md·rules.json 갱신은 " has a space -> not a violation;
  ".oms/state/verified-citations.json" has none -> violation).
- Docstrings are excluded explicitly: the first statement of a Module,
  FunctionDef, AsyncFunctionDef, or ClassDef, when it is `Expr(Constant(str))`.
  Comments are never in the AST, so they're excluded automatically.

Scan scope: every `.py` file in the repo except —
  - `tests/**`            -- fixtures/docstrings need the literal.
                             Measured 2026-08-28: 46 violations across 18 files.
  - `references/**`       -- copied into user projects; can't import hooks/.
                             Measured 2026-08-28: 0 violations (0 .py files at all).
  - `hooks/oms_paths.py`  -- the one allowed declaration site.
  - `.claude/worktrees/**` -- NOT in the contract's named exclusion list, added
                             here: per this repo's own `.gitignore` comment
                             ("Claude Code linked worktrees — checkouts of this
                             repo, never repo content"), these are gitignored
                             duplicate mirrors of files already linted at their
                             real path, not independent repo content.
                             Measured 2026-08-28: 254 violations across 117 files.
  (oms has no `.phase0-scratch/` — that exclusion is omo-only per the contract.)
"""
import ast
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEGACY_ROOT = ".oms"
HQ_ROOT = ".hq"
ROOT_LITERALS = (LEGACY_ROOT, HQ_ROOT)
PATHS_MODULE = ROOT / "hooks" / "oms_paths.py"
EXCLUDE_TOP_DIRS = {"tests", "references", ".claude", "__pycache__", ".git"}


def _target_files(root: Path = ROOT):
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in EXCLUDE_TOP_DIRS:
            continue
        if p == PATHS_MODULE:
            continue
        yield p


def _docstring_node_ids(tree: ast.AST) -> set:
    """id() of every Constant node that IS a docstring (Module/FunctionDef/
    AsyncFunctionDef/ClassDef's first statement, when Expr(Constant(str)))."""
    ids = set()
    candidates = [tree] + [
        n for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    for node in candidates:
        body = getattr(node, "body", None)
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            ids.add(id(body[0].value))
    return ids


def _is_violation(value: str) -> bool:
    return any(r in value for r in ROOT_LITERALS) and not any(ch.isspace() for ch in value)


def _violations_in_source(text: str, filename: str = "<string>"):
    """Return [(lineno, string)] violations in `text`. Raises SyntaxError on bad source."""
    tree = ast.parse(text, filename=filename)
    doc_ids = _docstring_node_ids(tree)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in doc_ids:
                continue
            s = node.value
            if _is_violation(s):
                out.append((node.lineno, s))
    return out


def _violations_in_file(path: Path):
    return [(path, ln, s) for ln, s in _violations_in_source(path.read_text(encoding="utf-8"), str(path))]


# --- live check -------------------------------------------------------------

def test_scan_targets_exist():
    # T1: a vacuous pass is impossible — a broken ROOT/glob must fail here,
    # not silently pass the lint below with zero files scanned.
    assert list(_target_files()), f"no .py files found to scan under {ROOT}"


def test_no_legacy_root_reentry():
    violations = []
    for f in _target_files():
        violations.extend(_violations_in_file(f))
    assert not violations, (
        f"root literal ({' or '.join(repr(r) for r in ROOT_LITERALS)}) re-entry outside "
        "hooks/oms_paths.py:\n" + "\n".join(f"{p}:{ln}: {s!r}" for p, ln, s in violations)
    )


# --- meta-tests: the rule must actually bite, and must not false-positive ---

def test_meta_bare_literal_bites():
    v = _violations_in_source('P = ".oms"\n')
    assert v and v[0][1] == ".oms"


def test_meta_computed_path_literal_bites():
    v = _violations_in_source('P = base / ".oms" / "state" / "verified-citations.json"\n')
    assert any(s == ".oms" for _, s in v)


def test_meta_fstring_piece_bites():
    v = _violations_in_source('x = f"{root}/.oms/wiki/{cat}"\n')
    assert v, "f-string constant piece containing the literal must be caught"


def test_meta_module_docstring_is_excluded():
    v = _violations_in_source('""".oms/state/foo.json"""\nimport os\n')
    assert v == []


def test_meta_function_docstring_is_excluded():
    src = 'def f():\n    """.oms/state/foo.json"""\n    return 1\n'
    assert _violations_in_source(src) == []


def test_meta_prose_with_space_is_not_a_violation():
    v = _violations_in_source('MSG = "records into .oms/state/verified-citations.json (records)"\n')
    assert v == []


def test_meta_hq_literal_bites():
    v = _violations_in_source('X = ".hq/config/scholar/learned.md"\n')
    assert len(v) == 1 and v[0][1] == ".hq/config/scholar/learned.md"


def test_meta_hq_prose_with_space_is_not_a_violation():
    v = _violations_in_source('MSG = "이 앵커는 .hq 루트를 가리킨다"\n')
    assert v == []
