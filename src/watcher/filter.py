
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import List, Optional

from src.config.models import DEFAULT_EXCLUSIONS

IGNORED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "logs",
    ".pytest_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
}

IGNORED_FILE_PATTERNS = {
    ".DS_Store",
    ".env*",
    "*.pem",
    "*.key",
    "*.cert",
    "*.crt",
    "secrets*",
    "credentials*",
    "*.pyc",
    "*.pyo",
    "*.swp",
    "*.swo",
    "*~",
}

SENSITIVE_FILE_PATTERNS = {
    ".env*",
    "*.pem",
    "*.key",
    "*.cert",
    "*.crt",
    "secrets*",
    "credentials*",
}

class PathFilter:

    def __init__(
        self,
        custom_exclusions: Optional[List[str]] = None,
        allow_sensitive_files: bool = False,
    ):
        self.ignored_dirs = set(IGNORED_DIR_NAMES)
        self.ignored_patterns = set(IGNORED_FILE_PATTERNS)
        if allow_sensitive_files:
            self.ignored_patterns -= SENSITIVE_FILE_PATTERNS
        if custom_exclusions:
            for item in custom_exclusions:
                clean = item.strip().replace("\\", "/").rstrip("/")
                if "/" in clean:
                    self.ignored_patterns.add(clean)
                else:
                    self.ignored_dirs.add(clean)
                    self.ignored_patterns.add(clean)

    def should_ignore(self, path: Path | str, base_dir: Optional[Path | str] = None) -> bool:
        target = Path(path).resolve()
        if base_dir:
            try:
                rel_path = target.relative_to(Path(base_dir).resolve())
            except ValueError:
                rel_path = target
        else:
            rel_path = target

        parts = set(rel_path.parts)
        if any(d in parts for d in self.ignored_dirs):
            return True

        filename = target.name
        if filename in self.ignored_patterns:
            return True

        for pat in self.ignored_patterns:
            if fnmatch.fnmatch(filename, pat) or fnmatch.fnmatch(rel_path.as_posix(), pat):
                return True

        return False
