
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from src.git.manager import GitStatusInfo
from src.utils.logger import log_event

DANGEROUS_FILE_PATTERNS = [
    re.compile(r"^\.env(\..+)?$", re.IGNORECASE),
    re.compile(r".*\.pem$", re.IGNORECASE),
    re.compile(r".*\.key$", re.IGNORECASE),
    re.compile(r".*id_rsa.*", re.IGNORECASE),
    re.compile(r".*credentials\.json$", re.IGNORECASE),
    re.compile(r".*service[-_]account.*\.json$", re.IGNORECASE),
]

@dataclass
class SafetyCheckResult:
    passed: bool
    warning: bool = False
    message: str = ""
    files_count: int = 0
    deletions_count: int = 0
    dangerous_files: List[str] = field(default_factory=list)

class SafetyGuard:

    def __init__(
        self,
        enabled: bool = True,
        max_changed_files: int = 50,
        max_deleted_lines: int = 500,
        allow_sensitive_files: bool = False,
    ):
        self.enabled = enabled
        self.max_changed_files = max_changed_files
        self.max_deleted_lines = max_deleted_lines
        self.allow_sensitive_files = allow_sensitive_files

    def evaluate(self, status: GitStatusInfo) -> SafetyCheckResult:
        if not self.enabled:
            return SafetyCheckResult(passed=True, message="Safety guard is disabled")

        if not self.allow_sensitive_files:
            dangerous: List[str] = []
            all_changed_files = status.staged_files + status.unstaged_files + status.untracked_files

            for file_path in all_changed_files:
                file_name = Path(file_path).name
                for pat in DANGEROUS_FILE_PATTERNS:
                    if pat.match(file_name):
                        dangerous.append(file_path)
                        break

            if dangerous:
                msg = f"Potential secret or sensitive file detected: {', '.join(dangerous)}"
                log_event("SECURITY", f"Commit blocked! {msg}")
                return SafetyCheckResult(
                    passed=False,
                    warning=True,
                    message=msg,
                    files_count=status.total_changed_files,
                    deletions_count=status.deleted_lines_est,
                    dangerous_files=dangerous,
                )

        is_large_files = status.total_changed_files > self.max_changed_files
        is_large_deletions = status.deleted_lines_est > self.max_deleted_lines

        if is_large_files or is_large_deletions:
            msg = (
                f"Large change detected: {status.total_changed_files} files "
                f"(max {self.max_changed_files}), {status.deleted_lines_est} deletions "
                f"(max {self.max_deleted_lines})"
            )
            log_event("SECURITY", f"Warning: {msg}")
            return SafetyCheckResult(
                passed=False,
                warning=True,
                message=msg,
                files_count=status.total_changed_files,
                deletions_count=status.deleted_lines_est,
            )

        return SafetyCheckResult(
            passed=True,
            message="Safety check passed",
            files_count=status.total_changed_files,
            deletions_count=status.deleted_lines_est,
        )
