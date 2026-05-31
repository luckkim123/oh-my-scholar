"""Atomic JSON write for .oms/ state files. stdlib only, cross-platform.

oms 가 *citation-bound 소스*(.tex/.bib)는 절대 .oms/ 로 옮기지 않으면서도,
*자기 상태 파일*(scholar-init 의 venue-config·meta, 향후 인덱스류) 쓰기엔 동등한
write-safety 가 없었다. 쓰기 중 크래시 시 상태 파일이 손상되면 부트스트랩이 깨지므로,
임시파일에 먼저 쓰고 fsync 후 atomic rename 한다.

os.replace() 는 POSIX 와 Windows 모두 동일 볼륨 내 atomic rename 을 보장한다
(Python 3.3+) — 부분쓰기 상태가 target 에 노출되지 않는다. third-party 의존 없음.
(omp 의 hooks/omp_atomic.py 와 동일 패턴을 oms 맥락으로 이식.)
"""
import json
import os
import tempfile
from pathlib import Path


def atomic_write_json(target, data) -> None:
    """`data`(JSON 직렬화 가능)를 `target` 경로에 원자적으로 쓴다.

    상위 디렉토리는 필요 시 생성한다(.oms/<slug>/ 같은 중첩 경로 지원).
    한글 등 비ASCII 는 이스케이프 없이 보존한다(.oms 메모는 한국어 다수).
    """
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    # mkstemp 자체가 실패하면 tmp 가 bind 안 되므로 None 으로 초기화 — except 에서
    # UnboundLocalError 가 원래 예외(디스크 풀·권한 등)를 덮는 것을 막는다.
    tmp = None
    try:
        # 같은 디렉토리에 임시파일을 만들어야 os.replace 가 같은 볼륨 atomic rename 이 된다.
        fd, tmp = tempfile.mkstemp(
            dir=str(target.parent), prefix=".oms-tmp-", suffix=".json"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)  # atomic — 부분쓰기 상태가 노출되지 않음
    except BaseException:
        # 실패 시 임시파일을 남기지 않는다(잔재 방지). 원래 예외는 그대로 전파.
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise
