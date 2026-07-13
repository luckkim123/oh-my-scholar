"""Tests for plugin.json integrity — skills 필드가 실제 skills/ 디렉토리와 1:1.

scholar-init 도입 시 발견: plugin.json 의 skills 리스트가 명시적이라, 새 스킬
디렉토리를 만들어도 여기 등록 안 하면 배포 시 로드 안 된다(scholar-deepen·
scholar-learn 도 한때 누락돼 있었다). 이 테스트가 그 드리프트를 막는다."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
SKILLS_DIR = ROOT / "skills"


def load_plugin() -> dict:
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))


def registered_skills() -> set:
    """plugin.json skills 필드의 디렉토리 이름 집합.

    Path(s).name 으로 추출 — str.strip("./") 는 *문자 집합* strip 이라 이름이
    './' 문자로 끝나면 잘못 깎인다(거짓 no-drift 위험). Path.name 은 후행
    슬래시 유무·상대 prefix 와 무관하게 항상 마지막 세그먼트만 준다."""
    return {Path(s).name for s in load_plugin()["skills"]}


def actual_skill_dirs() -> set:
    """skills/ 하위 실제 디렉토리(SKILL.md 보유) 집합."""
    return {
        d.name for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    }


def test_plugin_json_is_valid():
    """① plugin.json 이 유효한 JSON 이고 필수 키를 갖는다."""
    d = load_plugin()
    for key in ("name", "description", "skills", "hooks"):
        assert key in d, f"plugin.json 필수 키 '{key}' 누락"


def test_registered_skills_match_directories():
    """② skills 필드 == 실제 skills/ 디렉토리 (드리프트 0).

    누락(디렉토리는 있는데 미등록 → 배포 시 로드 안 됨)도,
    잉여(등록했는데 디렉토리 없음 → 로드 에러)도 없어야."""
    reg = registered_skills()
    actual = actual_skill_dirs()
    missing = actual - reg
    extra = reg - actual
    assert not missing, f"미등록 스킬(배포 시 로드 안 됨): {missing}"
    assert not extra, f"잉여 등록(디렉토리 없음): {extra}"


def test_scholar_init_registered():
    """③ scholar-init 이 등록돼 있다 (이번 도입의 핵심 산출물)."""
    assert "scholar-init" in registered_skills()
    assert (SKILLS_DIR / "scholar-init" / "SKILL.md").is_file()


def test_route_hook_registered():
    """④ scholar_route_emit hook 이 UserPromptSubmit 에 등록돼 있다."""
    hooks = load_plugin()["hooks"]
    ups = json.dumps(hooks.get("UserPromptSubmit", []))
    assert "scholar_route_emit.py" in ups


def test_cite_guard_registered():
    """⑤ scholar_cite_guard hook 이 PreToolUse 에 등록돼 있다 (R1 #1)."""
    hooks = load_plugin()["hooks"]
    pre = json.dumps(hooks.get("PreToolUse", []))
    assert "scholar_cite_guard.py" in pre


def test_stop_guard_registered():
    """⑥ scholar_stop_guard hook 이 Stop 에 등록돼 있다 (R2 #8)."""
    hooks = load_plugin()["hooks"]
    stop = json.dumps(hooks.get("Stop", []))
    assert "scholar_stop_guard.py" in stop


def test_resume_emit_registered():
    """⑦ scholar_resume_emit hook 이 SessionStart 에 등록돼 있다 (R2 #9+#13),
    compact matcher 포함 — #13(post-compaction Priority-Context 재주입) 이
    실제로 compact 소스에서 트리거되려면 matcher 에 compact 가 있어야 한다."""
    hooks = load_plugin()["hooks"]
    session_start = json.dumps(hooks.get("SessionStart", []))
    assert "scholar_resume_emit.py" in session_start
    assert "compact" in session_start
