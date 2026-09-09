"""Configuration manager for loading, persisting, and modifying project settings."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import threading
from pathlib import Path
from typing import List, Optional

from src.config.models import AppConfig, ProjectConfig, ProjectMode
from src.utils.logger import log_event


def get_default_config_path() -> Path:
    """Resolve permanent local machine configuration path in Windows AppData."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "GH-BOT-REPOS" / "projects.json"
    return Path.home() / ".gh_bot_repos" / "projects.json"


class ConfigManager:
    """Thread-safe manager for projects.json configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        self._local_backup_path = (
            Path(__file__).resolve().parent.parent.parent / "config" / "projects.json"
        )
        if config_path is None:
            self.config_path = get_default_config_path()
        else:
            self.config_path = Path(config_path).resolve()

        self._lock = threading.RLock()
        self._config = AppConfig()
        self.load()

    @property
    def config(self) -> AppConfig:
        with self._lock:
            return self._config

    def load(self) -> AppConfig:
        """Load configuration from JSON file or create a default one."""
        with self._lock:
            if not self.config_path.exists():
                # If AppData config doesn't exist yet but local workspace backup exists, migrate it
                if self._local_backup_path.exists() and self._local_backup_path != self.config_path:
                    try:
                        self.config_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(self._local_backup_path, self.config_path)
                        log_event("SYSTEM", f"Migrated local config to persistent path: {self.config_path}")
                    except Exception:
                        pass

            if not self.config_path.exists():
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                self._config = AppConfig()
                self.save()
                return self._config

            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = AppConfig.from_dict(data)
                log_event("SYSTEM", f"Config loaded: {len(self._config.projects)} projects from {self.config_path}")
            except Exception as ex:
                log_event("ERROR", f"Failed to load config from {self.config_path}: {ex}")
                self._config = AppConfig()
            return self._config

    def save(self) -> bool:
        """Persist configuration to disk atomically."""
        with self._lock:
            try:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                data = self._config.to_dict()

                # Atomic write via temporary file
                tmp_fd, tmp_path = tempfile.mkstemp(
                    dir=self.config_path.parent,
                    prefix="projects_tmp_",
                    suffix=".json",
                )
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                shutil.move(tmp_path, self.config_path)

                # Mirror backup to local repo directory if it exists
                if self._local_backup_path.parent.exists() and self._local_backup_path != self.config_path:
                    try:
                        shutil.copy2(self.config_path, self._local_backup_path)
                    except Exception:
                        pass

                return True
            except Exception as ex:
                log_event("ERROR", f"Failed to save config to {self.config_path}: {ex}")
                return False

    def get_projects(self) -> List[ProjectConfig]:
        with self._lock:
            return list(self._config.projects)

    def get_project_by_path(self, path: str) -> Optional[ProjectConfig]:
        with self._lock:
            norm_target = str(Path(path).resolve())
            for p in self._config.projects:
                if str(Path(p.path).resolve()) == norm_target:
                    return p
            return None

    def get_project_by_name(self, name: str) -> Optional[ProjectConfig]:
        with self._lock:
            for p in self._config.projects:
                if p.name.lower() == name.lower():
                    return p
            return None

    def add_project(self, project: ProjectConfig) -> bool:
        with self._lock:
            if self.get_project_by_path(project.path):
                log_event("PROJECT", f"Project path already exists: {project.path}")
                return False
            self._config.projects.append(project)
            saved = self.save()
            if saved:
                log_event("PROJECT", f"Added project: {project.name} ({project.path})")
            return saved

    def update_project(self, project: ProjectConfig) -> bool:
        with self._lock:
            norm_target = str(Path(project.path).resolve())
            for idx, p in enumerate(self._config.projects):
                if str(Path(p.path).resolve()) == norm_target:
                    self._config.projects[idx] = project
                    saved = self.save()
                    if saved:
                        log_event("PROJECT", f"Updated project: {project.name}")
                    return saved
            return False

    def remove_project(self, path: str) -> bool:
        with self._lock:
            norm_target = str(Path(path).resolve())
            initial_count = len(self._config.projects)
            self._config.projects = [
                p for p in self._config.projects if str(Path(p.path).resolve()) != norm_target
            ]
            if len(self._config.projects) < initial_count:
                saved = self.save()
                if saved:
                    log_event("PROJECT", f"Removed project at: {path}")
                return saved
            return False

    def set_project_mode(self, path: str, mode: ProjectMode) -> bool:
        with self._lock:
            project = self.get_project_by_path(path)
            if project:
                project.mode = mode
                return self.update_project(project)
            return False
