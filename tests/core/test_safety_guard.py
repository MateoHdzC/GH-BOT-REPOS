
from src.core.safety_guard import SafetyGuard
from src.git.manager import GitStatusInfo

def test_safety_guard_blocks_secret_files():
    sg = SafetyGuard(enabled=True)

    status_with_env = GitStatusInfo(
        is_clean=False,
        staged_files=[".env"],
        unstaged_files=[],
        untracked_files=[],
        total_changed_files=1,
    )
    res = sg.evaluate(status_with_env)
    assert res.passed is False
    assert ".env" in res.dangerous_files

    status_with_pem = GitStatusInfo(
        is_clean=False,
        staged_files=["certs/server.pem"],
        unstaged_files=[],
        untracked_files=[],
        total_changed_files=1,
    )
    res2 = sg.evaluate(status_with_pem)
    assert res2.passed is False

def test_safety_guard_blocks_excessive_changes():
    sg = SafetyGuard(enabled=True, max_changed_files=10, max_deleted_lines=100)

    status_ok = GitStatusInfo(
        is_clean=False,
        staged_files=[f"file_{i}.txt" for i in range(5)],
        unstaged_files=[],
        untracked_files=[],
        total_changed_files=5,
        deleted_lines_est=20,
    )
    assert sg.evaluate(status_ok).passed is True

    status_too_many_files = GitStatusInfo(
        is_clean=False,
        staged_files=[f"file_{i}.txt" for i in range(15)],
        unstaged_files=[],
        untracked_files=[],
        total_changed_files=15,
        deleted_lines_est=10,
    )
    res_files = sg.evaluate(status_too_many_files)
    assert res_files.passed is False
    assert "Large change detected" in res_files.message

    status_too_many_deletions = GitStatusInfo(
        is_clean=False,
        staged_files=["big_delete.py"],
        unstaged_files=[],
        untracked_files=[],
        total_changed_files=1,
        deleted_lines_est=150,
    )
    res_del = sg.evaluate(status_too_many_deletions)
    assert res_del.passed is False
