"""Shared directory-ascent helper for oms hooks (R2/R-debt unification).

Three call sites each walked `start`/`cwd` up its ancestor chain looking for a
different marker (`.oms/state` dir, `.oms/state` dir OR `.oms/notepad.md`, a
specific `.oms/state/verified-citations.json` file) with slightly different
stop conditions (inclusive-of-start vs exclusive). `nearest_ancestor` is the
one walk, parameterized by a per-call-site predicate — each call site keeps
its own exact marker check and its own return value, only the ascent loop is
shared.
"""
from pathlib import Path


def nearest_ancestor(start: Path, predicate, include_start: bool = True):
    """Return the first ancestor directory of `start` for which
    `predicate(candidate)` is truthy, else None.

    `include_start=True` checks `start` itself first (then parents);
    `include_start=False` starts the walk at `start`'s parent. Stops at the
    first hit — never looks past it.
    """
    candidates = (start, *start.parents) if include_start else start.parents
    for candidate in candidates:
        if predicate(candidate):
            return candidate
    return None
