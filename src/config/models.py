
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

class ProjectMode(str, Enum):
    AUTO = "AUTO"
    COMMIT_ONLY = "COMMIT_ONLY"
    PAUSED = "PAUSED"

class ProjectStatus(str, Enum):
    WATCHING = "Watching"
    DEBOUNCING = "Debouncing"
    SYNCING = "Syncing"
    PAUSED = "Paused"
    ERROR = "Error"
    IDLE = "Idle"

DEFAULT_EXCLUSIONS: List[str] = [
    ".git",
    ".git/*",
    ".gitignore",
    ".env",
    ".env.*",
    "*.secret",
    "*.key",
    "*.pem",
    "__pycache__",
    "__pycache__/*",
    "*.pyc",
    ".venv",
    ".venv/*",
    "venv",
    "venv/*",
    "node_modules",
    "node_modules/*",
    "dist",
    "dist/*",
    "build",
    "build/*",
    "*.tmp",
    "*.temp",
    "~$*",
    "Thumbs.db",
    "Desktop.ini",
    ".DS_Store",
    ".pytest_cache",
    ".pytest_cache/*",
]

@dataclass
class ProjectConfig:
    name: str
    path: str
    remote: str = ""
    branch: str = "main"
    mode: ProjectMode = ProjectMode.AUTO
    debounce_seconds: int = 300
    enabled: bool = True
    dry_run: bool = False
    safety_guard_enabled: bool = True
    allow_sensitive_files: bool = False
    max_changed_files_threshold: int = 50
    max_deleted_lines_threshold: int = 500
    custom_exclusions: List[str] = field(default_factory=list)

    last_sync_time: Optional[str] = None
    last_commit_hash: Optional[str] = None
    last_commit_message: Optional[str] = None
    last_error: Optional[str] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["mode"] = self.mode.value if isinstance(self.mode, ProjectMode) else str(self.mode)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> ProjectConfig:
        raw_mode = data.get("mode", ProjectMode.AUTO.value)
        try:
            mode = ProjectMode(raw_mode)
        except ValueError:
            mode = ProjectMode.AUTO

        return cls(
            name=data["name"],
            path=str(Path(data["path"]).resolve()),
            remote=data.get("remote", ""),
            branch=data.get("branch", "main"),
            mode=mode,
            debounce_seconds=int(data.get("debounce_seconds", 300)),
            enabled=bool(data.get("enabled", True)),
            dry_run=bool(data.get("dry_run", False)),
            safety_guard_enabled=bool(data.get("safety_guard_enabled", True)),
            allow_sensitive_files=bool(data.get("allow_sensitive_files", False)),
            max_changed_files_threshold=int(data.get("max_changed_files_threshold", 50)),
            max_deleted_lines_threshold=int(data.get("max_deleted_lines_threshold", 500)),
            custom_exclusions=list(data.get("custom_exclusions", [])),
            last_sync_time=data.get("last_sync_time"),
            last_commit_hash=data.get("last_commit_hash"),
            last_commit_message=data.get("last_commit_message"),
            last_error=data.get("last_error"),
        )

@dataclass
class AppConfig:
    projects: List[ProjectConfig] = field(default_factory=list)
    start_with_windows: bool = True
    minimize_to_tray: bool = True
    notifications_enabled: bool = True
    global_dry_run: bool = False

    def to_dict(self) -> dict:
        return {
            "projects": [p.to_dict() for p in self.projects],
            "start_with_windows": self.start_with_windows,
            "minimize_to_tray": self.minimize_to_tray,
            "notifications_enabled": self.notifications_enabled,
            "global_dry_run": self.global_dry_run,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AppConfig:
        projects_data = data.get("projects", [])
        projects = [ProjectConfig.from_dict(p) for p in projects_data if isinstance(p, dict) and "name" in p and "path" in p]
        return cls(
            projects=projects,
            start_with_windows=bool(data.get("start_with_windows", True)),
            minimize_to_tray=bool(data.get("minimize_to_tray", True)),
            notifications_enabled=bool(data.get("notifications_enabled", True)),
            global_dry_run=bool(data.get("global_dry_run", False)),
        )
