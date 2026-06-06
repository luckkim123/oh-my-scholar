"""Atomic JSON write for .oms/ state files. stdlib only, cross-platform.

oms never moves *citation-bound sources* (.tex/.bib) into .oms/, yet it had no
equivalent write-safety for writes to its *own state files* (scholar-init's
venue-config/meta, future index files). If a state file is corrupted by a crash
mid-write, bootstrap breaks — so write to a temp file first, fsync, then atomic
rename.

os.replace() guarantees an atomic same-volume rename on both POSIX and Windows
(Python 3.3+) — a partial-write state is never exposed at the target. No
third-party dependency. (Same pattern as omp's hooks/omp_atomic.py, ported into
the oms context.)
"""
import json
import os
import tempfile
from pathlib import Path


def atomic_write_json(target, data) -> None:
    """Atomically write `data` (JSON-serializable) to the `target` path.

    Creates parent directories as needed (supports nested paths like .oms/<slug>/).
    Preserves non-ASCII (e.g. Korean) without escaping (.oms notes are often Korean).
    """
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Initialize tmp to None: if mkstemp itself fails, tmp is never bound, so this
    # prevents an UnboundLocalError in the except block from masking the original
    # exception (disk full, permissions, etc.).
    tmp = None
    try:
        # The temp file must live in the same directory so os.replace is a
        # same-volume atomic rename.
        fd, tmp = tempfile.mkstemp(
            dir=str(target.parent), prefix=".oms-tmp-", suffix=".json"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)  # atomic — a partial-write state is never exposed
    except BaseException:
        # On failure, leave no temp file behind. Re-raise the original exception.
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise
