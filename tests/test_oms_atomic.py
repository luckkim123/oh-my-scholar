"""Tests for the atomic JSON write helper (oms).

oms 의 .oms/ 상태 파일(scholar-init venue-config·meta 등)은 쓰기 중 크래시 시
손상되면 부트스트랩이 깨진다. atomic write 가 그 무결성 보험이다. stdlib only,
cross-platform (os.replace 는 POSIX·Windows 동일 볼륨 atomic rename 보장, py3.3+).
omp 의 test_omp_atomic.py 를 oms 맥락으로 미러."""
import json
from pathlib import Path

import pytest

from hooks.oms_atomic import atomic_write_json


def test_atomic_write_replaces_intact(tmp_path):
    """기본: dict 를 JSON 으로 쓰고 그대로 다시 읽힌다."""
    target = tmp_path / "venue-config.json"
    atomic_write_json(target, {"v": 1})
    assert json.loads(target.read_text(encoding="utf-8"))["v"] == 1


def test_atomic_write_no_partial_leftover(tmp_path):
    """덮어쓰기 후 임시파일 잔재가 없고 target 만 최종값을 갖는다."""
    target = tmp_path / "venue-config.json"
    atomic_write_json(target, {"v": 1})
    atomic_write_json(target, {"v": 2})
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "venue-config.json"]
    assert leftovers == [], f"임시파일 잔재: {leftovers}"
    assert json.loads(target.read_text(encoding="utf-8"))["v"] == 2


def test_atomic_write_creates_parent_dirs(tmp_path):
    """.oms/<slug>/ 처럼 없는 상위 디렉토리도 만들어 쓴다."""
    target = tmp_path / ".oms" / "2026-05-31_abc-paper" / "meta.json"
    atomic_write_json(target, {"venue": "IROS"})
    assert target.is_file()
    assert json.loads(target.read_text(encoding="utf-8"))["venue"] == "IROS"


def test_atomic_write_preserves_unicode(tmp_path):
    """ensure_ascii=False — 한글·비ASCII 가 이스케이프 없이 보존된다(.oms 는 한국어 다수)."""
    target = tmp_path / "meta.json"
    atomic_write_json(target, {"주제": "수중 로봇 측위"})
    raw = target.read_text(encoding="utf-8")
    assert "주제" in raw and "\\u" not in raw


def test_atomic_write_accepts_str_path(tmp_path):
    """Path 와 str 경로 모두 받는다."""
    target = str(tmp_path / "meta.json")
    atomic_write_json(target, {"ok": 1})
    assert Path(target).is_file()


def test_atomic_write_cleans_up_on_failure(tmp_path):
    """실패 경로: 직렬화 불가 객체로 json.dump 가 raise 하면 — 임시파일 잔재 0,
    target 미생성, 원래 예외(TypeError) 그대로 전파(UnboundLocalError 로 안 덮임)."""
    target = tmp_path / "meta.json"
    with pytest.raises(TypeError):
        atomic_write_json(target, object())  # JSON 직렬화 불가 → json.dump raise
    leftovers = list(tmp_path.glob(".oms-tmp-*.json"))
    assert leftovers == [], f"실패 시 임시파일 미정리: {leftovers}"
    assert not target.exists(), "실패인데 target 이 생성됨"


def test_atomic_write_stdlib_only():
    """경량 제약: 헬퍼가 third-party import 없이 stdlib 만 쓴다."""
    src = (Path(__file__).parent.parent / "hooks" / "oms_atomic.py").read_text()
    assert "import requests" not in src and "import yaml" not in src
    assert "os.replace" in src  # atomic rename 의 핵심 — 회귀 방지
