"""Unit tests for ProjectManager lifecycle and operations."""

import tempfile
from pathlib import Path
import pytest

from src.config.models import ProjectConfig, ProjectMode, ProjectStatus
from src.core.project_manager import ProjectManager
from src.core.retry_queue import RetryQueue
from src.git.manager import GitManager


@pytest.fixture
def git_manager():
    return GitManager()


@pytest.fixture
def sample_repo(git_manager):
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        git_manager.init_repo(repo_path, initial_branch="main")
        git_manager.run_command(repo_path, ["config", "user.name", "GH Bot Test"])
        git_manager.run_command(repo_path, ["config", "user.email", "bot@test.local"])
        # Initial commit so repository has a valid HEAD
        (repo_path / "init.txt").write_text("initial", encoding="utf-8")
        git_manager.stage_all(repo_path)
        git_manager.commit(repo_path, "feat: init repo")
        yield repo_path


def test_sync_no_changes_does_not_commit(git_manager, sample_repo):
    config = ProjectConfig(
        name="NoChangeProject",
        path=str(sample_repo),
        mode=ProjectMode.AUTO,
    )
    pm = ProjectManager(config, git_manager, RetryQueue())

    pm.sync()
    assert pm.stats["commits"] == 0
    assert pm.status == ProjectStatus.WATCHING


def test_sync_commit_only_mode(git_manager, sample_repo):
    config = ProjectConfig(
        name="CommitOnlyProject",
        path=str(sample_repo),
        mode=ProjectMode.COMMIT_ONLY,
    )
    pm = ProjectManager(config, git_manager, RetryQueue())

    # Add a real change
    (sample_repo / "new_feature.py").write_text("print('hello')", encoding="utf-8")

    pm.sync()

    assert pm.stats["commits"] == 1
    assert pm.stats["pushes"] == 0
    assert pm.status == ProjectStatus.WATCHING
    assert len(pm.history) == 1
    assert "✓ Commit creado" in pm.history[0].status


def test_sync_dry_run_mode(git_manager, sample_repo):
    config = ProjectConfig(
        name="DryRunProject",
        path=str(sample_repo),
        mode=ProjectMode.AUTO,
        dry_run=True,
    )
    pm = ProjectManager(config, git_manager, RetryQueue())

    # Add a real change
    (sample_repo / "dry_run.txt").write_text("dry run content", encoding="utf-8")

    pm.sync()

    # Dry run should NOT create a real git commit
    assert pm.stats["commits"] == 0
    # The file should remain untracked / unstaged
    status = git_manager.get_status(sample_repo)
    assert status.is_clean is False
    assert len(pm.history) == 1
    assert "DRY RUN" in pm.history[0].status
