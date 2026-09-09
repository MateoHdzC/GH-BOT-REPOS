"""Core Engine: Orchestrates multi-project monitoring, retries, and background execution."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.config.manager import ConfigManager
from src.config.models import ProjectConfig, ProjectMode, ProjectStatus
from src.core.project_manager import ProjectManager
from src.core.retry_queue import PendingPush, RetryQueue
from src.git.credentials import GitHubCredentials
from src.git.manager import GitManager
from src.utils.logger import log_event
from src.watcher.filter import PathFilter
from src.watcher.service import WatcherService


class Engine:
    """Central application engine coordinating watchers, projects, and sync cycles."""

    def __init__(
        self,
        config_manager: ConfigManager,
        on_status_change: Optional[Callable[[str, ProjectStatus], None]] = None,
        on_notify: Optional[Callable[[str, str, str], None]] = None,
    ):
        self.config_manager = config_manager
        self.on_status_change = on_status_change
        self.on_notify = on_notify

        self.git = GitManager()
        self.watcher = WatcherService()
        self.retry_queue = RetryQueue()

        self._managers: Dict[str, ProjectManager] = {}
        self._lock = threading.RLock()
        self._is_running = False
        self._worker_thread: Optional[threading.Thread] = None

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._is_running

    def start(self) -> None:
        """Initialize engine and start monitoring all configured projects."""
        with self._lock:
            if self._is_running:
                return
            self._is_running = True

            log_event("SYSTEM", "Engine starting up...")
            self._load_projects()

            # Start background maintenance thread (retry queue processor)
            self._worker_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
            self._worker_thread.start()
            log_event("SYSTEM", "Engine running successfully.")

    def stop(self) -> None:
        """Stop all project watchers and background loops cleanly."""
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False
            log_event("SYSTEM", "Stopping engine and active watchers...")

            self.watcher.stop_all()

            for pm in self._managers.values():
                pm.debounce.cancel()
                pm.set_status(ProjectStatus.IDLE)

            self._managers.clear()
            log_event("SYSTEM", "Engine stopped cleanly.")

    def _load_projects(self) -> None:
        """Register and start watchers for all projects in configuration."""
        projects = self.config_manager.get_projects()
        for p in projects:
            self._register_project(p)

    def _register_project(self, project: ProjectConfig) -> None:
        norm_path = str(Path(project.path).resolve())
        pm = ProjectManager(
            config=project,
            git_manager=self.git,
            retry_queue=self.retry_queue,
            on_status_change=self.on_status_change,
            on_notify=self.on_notify,
        )
        self._managers[norm_path] = pm

        if project.enabled and project.mode != ProjectMode.PAUSED:
            pm.set_status(ProjectStatus.WATCHING)
            if self._is_running:
                path_filter = PathFilter(project.custom_exclusions)
                self.watcher.start_watching(
                    project_path=project.path,
                    project_name=project.name,
                    on_change_callback=pm.handle_filesystem_change,
                    path_filter=path_filter,
                )
        else:
            pm.set_status(ProjectStatus.PAUSED)

    def add_project(self, project: ProjectConfig) -> bool:
        """Add a project to config and launch watcher."""
        with self._lock:
            if self.config_manager.add_project(project):
                self._register_project(project)
                return True
            return False

    def remove_project(self, path: str) -> bool:
        """Remove a project from config and stop its watcher."""
        with self._lock:
            norm = str(Path(path).resolve())
            self.watcher.stop_watching(norm)
            pm = self._managers.pop(norm, None)
            if pm:
                pm.debounce.cancel()
            return self.config_manager.remove_project(path)

    def set_project_mode(self, path: str, mode: ProjectMode) -> bool:
        """Update project mode and adjust watcher accordingly."""
        with self._lock:
            norm = str(Path(path).resolve())
            if self.config_manager.set_project_mode(path, mode):
                pm = self._managers.get(norm)
                if pm:
                    pm.config.mode = mode
                    if mode == ProjectMode.PAUSED:
                        self.watcher.stop_watching(norm)
                        pm.debounce.cancel()
                        pm.set_status(ProjectStatus.PAUSED)
                    else:
                        pm.set_status(ProjectStatus.WATCHING)
                        path_filter = PathFilter(pm.config.custom_exclusions)
                        self.watcher.start_watching(
                            project_path=pm.config.path,
                            project_name=pm.config.name,
                            on_change_callback=pm.handle_filesystem_change,
                            path_filter=path_filter,
                        )
                return True
            return False

    def get_manager(self, path: str) -> Optional[ProjectManager]:
        with self._lock:
            return self._managers.get(str(Path(path).resolve()))

    def get_all_managers(self) -> List[ProjectManager]:
        with self._lock:
            return list(self._managers.values())

    def sync_project_now(self, path: str) -> None:
        """Trigger immediate sync for a specific project."""
        pm = self.get_manager(path)
        if pm:
            threading.Thread(target=pm.sync_now, daemon=True).start()

    def sync_all_now(self) -> None:
        """Trigger immediate sync for all active projects."""
        with self._lock:
            for pm in self._managers.values():
                if pm.config.mode != ProjectMode.PAUSED and pm.config.enabled:
                    threading.Thread(target=pm.sync_now, daemon=True).start()

    def pause_all(self) -> None:
        """Pause all projects."""
        with self._lock:
            for pm in self._managers.values():
                self.set_project_mode(pm.config.path, ProjectMode.PAUSED)

    def resume_all(self) -> None:
        """Resume all projects to AUTO."""
        with self._lock:
            for pm in self._managers.values():
                self.set_project_mode(pm.config.path, ProjectMode.AUTO)

    def get_dashboard_stats(self) -> dict:
        """Aggregate live statistics across all projects."""
        with self._lock:
            total = len(self._managers)
            active = sum(1 for m in self._managers.values() if m.config.mode != ProjectMode.PAUSED and m.config.enabled)
            paused = sum(1 for m in self._managers.values() if m.config.mode == ProjectMode.PAUSED or not m.config.enabled)
            commits = sum(m.stats["commits"] for m in self._managers.values())
            pushes = sum(m.stats["pushes"] for m in self._managers.values())
            failed_pushes = sum(m.stats["failed_pushes"] for m in self._managers.values())
            files_changed = sum(m.stats["files_changed"] for m in self._managers.values())

            return {
                "total_projects": total,
                "active_projects": active,
                "paused_projects": paused,
                "total_commits": commits,
                "total_pushes": pushes,
                "failed_pushes": failed_pushes,
                "total_files_changed": files_changed,
                "engine_running": self._is_running,
            }

    def _maintenance_loop(self) -> None:
        """Background thread handling push retry queues."""
        while self._is_running:
            time.sleep(5)
            due_items = self.retry_queue.get_due_items()
            for item in due_items:
                pm = self.get_manager(item.project_path)
                if pm and pm.config.mode == ProjectMode.AUTO:
                    log_event("PUSH", f"Retrying failed push for {pm.config.name}...")
                    token = GitHubCredentials.get_token()
                    res = self.git.push(
                        pm.config.path,
                        remote=item.remote,
                        branch=item.branch,
                        set_upstream=True,
                        auth_token=token,
                    )
                    if res.success:
                        self.retry_queue.remove(item.project_path)
                        pm.stats["pushes"] += 1
                        pm.set_status(ProjectStatus.WATCHING)
                        pm._add_history("✓ Push exitoso (Reintento)", f"Enviado a {item.remote}/{item.branch}")
                        log_event("PUSH", f"Retry succeeded for {pm.config.name}!")
                        if self.on_notify:
                            self.on_notify("success", pm.config.name, "Push completado en reintento.")
                    else:
                        self.retry_queue.add_or_update(
                            project_path=item.project_path,
                            project_name=item.project_name,
                            remote=item.remote,
                            branch=item.branch,
                            error=res.stderr,
                        )
