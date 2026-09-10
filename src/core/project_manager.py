
from __future__ import annotations

import datetime
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from src.config.models import ProjectConfig, ProjectMode, ProjectStatus
from src.core.retry_queue import RetryQueue
from src.core.safety_guard import SafetyCheckResult, SafetyGuard
from src.git.credentials import GitHubCredentials
from src.git.manager import GitCommitInfo, GitErrorKind, GitManager, GitResult
from src.utils.logger import log_event
from src.watcher.debounce import DebounceController

@dataclass
class SyncHistoryEntry:
    timestamp: str
    status: str
    detail: str
    commit_hash: Optional[str] = None

class ProjectManager:

    def __init__(
        self,
        config: ProjectConfig,
        git_manager: GitManager,
        retry_queue: RetryQueue,
        on_status_change: Optional[Callable[[str, ProjectStatus], None]] = None,
        on_notify: Optional[Callable[[str, str, str], None]] = None,
    ):
        self.config = config
        self.git = git_manager
        self.retry_queue = retry_queue
        self.on_status_change = on_status_change
        self.on_notify = on_notify

        self.status = ProjectStatus.IDLE
        self.history: List[SyncHistoryEntry] = []
        self.stats = {
            "commits": 0,
            "pushes": 0,
            "failed_pushes": 0,
            "files_changed": 0,
        }

        self._op_lock = threading.Lock()
        self.safety_guard = SafetyGuard(
            enabled=config.safety_guard_enabled,
            max_changed_files=config.max_changed_files_threshold,
            max_deleted_lines=config.max_deleted_lines_threshold,
        )

        self.debounce = DebounceController(
            project_name=config.name,
            debounce_seconds=config.debounce_seconds,
            on_trigger=self._on_debounce_completed,
        )

    def set_status(self, new_status: ProjectStatus) -> None:
        self.status = new_status
        if self.on_status_change:
            self.on_status_change(self.config.path, new_status)

    def handle_filesystem_change(self, event_type: str, file_path: str) -> None:
        if self.config.mode == ProjectMode.PAUSED or not self.config.enabled:
            return

        self.set_status(ProjectStatus.DEBOUNCING)
        self.debounce.notify_change()

    def _on_debounce_completed(self) -> None:
        self.sync()

    def sync_now(self) -> None:
        self.debounce.trigger_now()

    def sync(self, dry_run: Optional[bool] = None) -> None:
        if not self._op_lock.acquire(blocking=False):
            log_event("PROJECT", f"{self.config.name}: Sync already in progress, skipping.")
            return

        try:
            self._do_sync(dry_run)
        finally:
            self._op_lock.release()

    def _do_sync(self, dry_run: Optional[bool] = None) -> None:
        repo_path = self.config.path
        is_dry_run = dry_run if dry_run is not None else self.config.dry_run

        if not self.git.is_repo(repo_path):
            self.set_status(ProjectStatus.ERROR)
            self.config.last_error = "Directory is not a Git repository"
            log_event("ERROR", f"{self.config.name}: Not a Git repo at {repo_path}")
            return

        self.set_status(ProjectStatus.SYNCING)

        status = self.git.get_status(repo_path)
        if status.is_clean:
            log_event("GIT", f"{self.config.name}: No hay cambios para sincronizar.")
            self.set_status(ProjectStatus.WATCHING)
            return

        log_event(
            "GIT",
            f"{self.config.name}: Changes detected ({status.total_changed_files} files changed).",
        )
        self.stats["files_changed"] += status.total_changed_files

        safety_res = self.safety_guard.evaluate(status)
        if not safety_res.passed:
            self.set_status(ProjectStatus.ERROR)
            self.config.last_error = safety_res.message
            if self.on_notify:
                self.on_notify("danger", self.config.name, safety_res.message)
            self._add_history("⚠ Bloqueado por Safety Guard", safety_res.message)
            return

        if is_dry_run:
            log_event("SYSTEM", f"[DRY RUN] {self.config.name}: Would stage {status.total_changed_files} files, commit and push.")
            self._add_history("🔍 DRY RUN", f"Simulados {status.total_changed_files} cambios")
            self.set_status(ProjectStatus.WATCHING)
            return

        stage_res = self.git.stage_all(repo_path)
        if not stage_res.success:
            self.set_status(ProjectStatus.ERROR)
            self.config.last_error = f"Stage error: {stage_res.stderr}"
            self._add_history("❌ Error al preparar cambios", stage_res.stderr)
            return

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"auto: sync {status.total_changed_files} files [{now_str}]"
        commit_res = self.git.commit(repo_path, commit_msg)
        if not commit_res.success:
            self.set_status(ProjectStatus.ERROR)
            self.config.last_error = f"Commit error: {commit_res.stderr}"
            self._add_history("❌ Error al crear commit", commit_res.stderr)
            return

        last_commit = self.git.get_last_commit(repo_path)
        commit_hash = last_commit.short_hash if last_commit else "unknown"
        self.stats["commits"] += 1
        self.config.last_commit_hash = commit_hash
        self.config.last_commit_message = commit_msg
        self.config.last_sync_time = now_str
        log_event("COMMIT", f"{self.config.name}: Commit created [{commit_hash}]")

        if self.config.mode == ProjectMode.COMMIT_ONLY:
            log_event("PROJECT", f"{self.config.name}: Mode is COMMIT_ONLY, push skipped.")
            self._add_history("✓ Commit creado", commit_msg, commit_hash)
            self.set_status(ProjectStatus.WATCHING)
            if self.on_notify:
                self.on_notify("success", self.config.name, "Commit creado correctamente.")
            return

        token = GitHubCredentials.get_token()
        remote = self.config.remote or "origin"
        branch = self.config.branch or self.git.get_current_branch(repo_path)

        push_res = self.git.push(
            repo_path,
            remote=remote,
            branch=branch,
            set_upstream=True,
            auth_token=token,
        )

        if not push_res.success:
            err_lower = push_res.stderr.lower()
            if (
                push_res.error_kind == GitErrorKind.REJECTED_NON_FAST_FORWARD
                or "fetch first" in err_lower
                or "non-fast-forward" in err_lower
            ):
                log_event("GIT", f"{self.config.name}: Remote is ahead, reconciling with pull --rebase...")
                pull_res = self.git.pull_rebase(repo_path, remote=remote, branch=branch, auth_token=token)
                if pull_res.success:
                    log_event("GIT", f"{self.config.name}: Rebase successful, retrying push...")
                    push_res = self.git.push(
                        repo_path,
                        remote=remote,
                        branch=branch,
                        set_upstream=True,
                        auth_token=token,
                    )

        if push_res.success:
            self.stats["pushes"] += 1
            self.retry_queue.remove(self.config.path)
            log_event("PUSH", f"{self.config.name}: Push successful to {remote}/{branch}")
            self._add_history("✓ Commit + Push", f"{commit_hash} -> {remote}/{branch}", commit_hash)
            self.set_status(ProjectStatus.WATCHING)
            if self.on_notify:
                self.on_notify("success", self.config.name, "Sincronizado correctamente con GitHub.")
        else:
            self.stats["failed_pushes"] += 1
            self.retry_queue.add_or_update(
                project_path=self.config.path,
                project_name=self.config.name,
                remote=remote,
                branch=branch,
                error=push_res.stderr,
            )
            log_event("ERROR", f"{self.config.name}: Push failed: {push_res.stderr}")
            self._add_history("⚠ Push fallido (Encolado para reintento)", push_res.stderr, commit_hash)
            self.set_status(ProjectStatus.ERROR)
            if self.on_notify:
                self.on_notify("warning", self.config.name, f"Push fallido: {push_res.stderr}")

    def _add_history(self, status: str, detail: str, commit_hash: Optional[str] = None) -> None:
        entry = SyncHistoryEntry(
            timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
            status=status,
            detail=detail,
            commit_hash=commit_hash,
        )
        self.history.insert(0, entry)
        if len(self.history) > 50:
            self.history.pop()
