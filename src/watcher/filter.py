
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import List, Optional

from src.config.models import DEFAULT_EXCLUSIONS

class PathFilter:

    def __init__(self, custom_exclusions: Optional[List[str]] = None):
        self.exclusions = list(DEFAULT_EXCLUSIONS)
        if custom_exclusions:
            self.exclusions.extend(custom_exclusions)

    def should_ignore(self, path: Path | str, base_dir: Optional[Path | str] = None) -> bool:
        target = Path(path).resolve()
        if base_dir:
            try:
                rel_path = target.relative_to(Path(base_dir).resolve())
            except ValueError:
                rel_path = target
        else:
            rel_path = target

        posix_rel = rel_path.as_posix()
        name = target.name

        parts = rel_path.parts
        if ".git" in parts or any(p.startswith(".git") for p in parts):
            return True

        for pattern in self.exclusions:
            clean_pat = pattern.replace("\\", "/").rstrip("/")
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(posix_rel, pattern):
                return True
            if fnmatch.fnmatch(name, clean_pat) or fnmatch.fnmatch(posix_rel, clean_pat):
                return True
            for part in parts:
                if fnmatch.fnmatch(part, clean_pat):
                    return True

        return False
