
import os
import tempfile
from pathlib import Path
import pytest

from src.git.manager import GitErrorKind, GitManager

@pytest.fixture
def git_manager():
    return GitManager()

@pytest.fixture
def temp_repo(git_manager):
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        git_manager.init_repo(repo_path, initial_branch="main")
        git_manager.run_command(repo_path, ["config", "user.name", "GH Bot Test"])
        git_manager.run_command(repo_path, ["config", "user.email", "bot@test.local"])
        yield repo_path

def test_is_repo(git_manager, temp_repo):
    assert git_manager.is_repo(temp_repo) is True
    assert git_manager.is_repo(temp_repo / "nonexistent") is False

def test_git_status_and_commit(git_manager, temp_repo):
    status_empty = git_manager.get_status(temp_repo)
    assert status_empty.is_clean is True

    test_file = temp_repo / "hello.txt"
    test_file.write_text("Hello World\n", encoding="utf-8")

    status_untracked = git_manager.get_status(temp_repo)
    assert status_untracked.is_clean is False
    assert "hello.txt" in status_untracked.untracked_files

    stage_res = git_manager.stage_all(temp_repo)
    assert stage_res.success is True

    status_staged = git_manager.get_status(temp_repo)
    assert "hello.txt" in status_staged.staged_files

    commit_res = git_manager.commit(temp_repo, "feat: initial test commit")
    assert commit_res.success is True

    info = git_manager.get_last_commit(temp_repo)
    assert info is not None
    assert info.message == "feat: initial test commit"
    assert len(info.short_hash) >= 7

    status_after = git_manager.get_status(temp_repo)
    assert status_after.is_clean is True

def test_forbidden_commands_blocked(git_manager, temp_repo):
    res_force = git_manager.run_command(temp_repo, ["push", "--force", "origin", "main"])
    assert res_force.success is False
    assert "Security violation" in res_force.stderr

    res_hard = git_manager.run_command(temp_repo, ["reset", "--hard", "HEAD"])
    assert res_hard.success is False
    assert "Security violation" in res_hard.stderr
