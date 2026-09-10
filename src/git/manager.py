
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.utils.logger import log_event

class GitErrorKind(str, Enum):
    NONE = "NONE"
    NOT_A_REPO = "NOT_A_REPO"
    AUTH_FAILED = "AUTH_FAILED"
    NETWORK_ERROR = "NETWORK_ERROR"
    UPSTREAM_MISSING = "UPSTREAM_MISSING"
    REJECTED_NON_FAST_FORWARD = "REJECTED_NON_FAST_FORWARD"
    CONFLICT = "CONFLICT"
    NOTHING_TO_COMMIT = "NOTHING_TO_COMMIT"
    LOCK_EXIST = "LOCK_EXIST"
    UNKNOWN = "UNKNOWN"

@dataclass
class GitResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int
    error_kind: GitErrorKind = GitErrorKind.NONE

@dataclass
class GitStatusInfo:
    is_clean: bool
    staged_files: List[str]
    unstaged_files: List[str]
    untracked_files: List[str]
    total_changed_files: int
    deleted_lines_est: int = 0

@dataclass
class GitCommitInfo:
    hash: str
    short_hash: str
    author: str
    date: str
    message: str

class GitManager:

    def __init__(self, git_binary: str = "git"):
        self.git_binary = git_binary

    def run_command(
        self,
        repo_path: Path | str,
        args: List[str],
        timeout: int = 45,
        env: Optional[Dict[str, str]] = None,
    ) -> GitResult:
        forbidden = [
            ("--force", "Force push forbidden"),
            ("-f", "Force flag forbidden"),
            ("--hard", "Hard reset forbidden"),
        ]
        lower_args = [a.lower() for a in args]
        for flag, reason in forbidden:
            if flag in lower_args:
                log_event("SECURITY", f"Blocked forbidden git command: {' '.join(args)} ({reason})")
                return GitResult(
                    success=False,
                    stdout="",
                    stderr=f"Security violation: {reason}",
                    returncode=-1,
                    error_kind=GitErrorKind.UNKNOWN,
                )

        cwd = Path(repo_path).resolve()
        if not cwd.exists():
            return GitResult(
                success=False,
                stdout="",
                stderr="Directory does not exist",
                returncode=-1,
                error_kind=GitErrorKind.NOT_A_REPO,
            )

        cmd = [self.git_binary] + args
        cmd_env = os.environ.copy()
        cmd_env["GIT_TERMINAL_PROMPT"] = "0"
        cmd_env["GCM_INTERACTIVE"] = "never"
        if env:
            cmd_env.update(env)

        try:
            process = subprocess.run(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=cmd_env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            success = process.returncode == 0
            err_kind = self._classify_error(process.returncode, process.stderr, process.stdout)
            return GitResult(
                success=success,
                stdout=process.stdout.strip(),
                stderr=process.stderr.strip(),
                returncode=process.returncode,
                error_kind=err_kind,
            )
        except subprocess.TimeoutExpired:
            return GitResult(
                success=False,
                stdout="",
                stderr=f"Git command timed out after {timeout} seconds",
                returncode=-2,
                error_kind=GitErrorKind.NETWORK_ERROR,
            )
        except FileNotFoundError:
            return GitResult(
                success=False,
                stdout="",
                stderr="Git executable not found in PATH",
                returncode=-3,
                error_kind=GitErrorKind.UNKNOWN,
            )
        except Exception as ex:
            return GitResult(
                success=False,
                stdout="",
                stderr=str(ex),
                returncode=-4,
                error_kind=GitErrorKind.UNKNOWN,
            )

    def _classify_error(self, code: int, stderr: str, stdout: str) -> GitErrorKind:
        if code == 0:
            return GitErrorKind.NONE
        combined = f"{stderr} {stdout}".lower()
        if "not a git repository" in combined:
            return GitErrorKind.NOT_A_REPO
        if "authentication failed" in combined or "permission denied" in combined or "could not read username" in combined:
            return GitErrorKind.AUTH_FAILED
        if "could not resolve host" in combined or "failed to connect" in combined or "connection timed out" in combined:
            return GitErrorKind.NETWORK_ERROR
        if "has no upstream branch" in combined or "no tracking information" in combined:
            return GitErrorKind.UPSTREAM_MISSING
        if "non-fast-forward" in combined or "fetch first" in combined:
            return GitErrorKind.REJECTED_NON_FAST_FORWARD
        if "conflict" in combined or "merge conflict" in combined:
            return GitErrorKind.CONFLICT
        if "nothing to commit" in combined or "clean" in combined:
            return GitErrorKind.NOTHING_TO_COMMIT
        if "index.lock" in combined:
            return GitErrorKind.LOCK_EXIST
        return GitErrorKind.UNKNOWN

    def is_repo(self, path: Path | str) -> bool:
        res = self.run_command(path, ["rev-parse", "--is-inside-work-tree"])
        return res.success and res.stdout.strip() == "true"

    def init_repo(self, path: Path | str, initial_branch: str = "main") -> GitResult:
        res = self.run_command(path, ["init", "-b", initial_branch])
        if not res.success:
            res = self.run_command(path, ["init"])
            if res.success:
                self.run_command(path, ["checkout", "-b", initial_branch])
        if res.success:
            log_event("GIT", f"Initialized Git repository at {path}")
        return res

    def get_current_branch(self, path: Path | str) -> str:
        res = self.run_command(path, ["branch", "--show-current"])
        if res.success and res.stdout:
            return res.stdout.strip()
        res2 = self.run_command(path, ["symbolic-ref", "--short", "HEAD"])
        if res2.success and res2.stdout:
            return res2.stdout.strip()
        return "main"

    def get_remote_url(self, path: Path | str, remote: str = "origin") -> Optional[str]:
        res = self.run_command(path, ["remote", "get-url", remote])
        if res.success and res.stdout:
            return res.stdout.strip()
        return None

    def set_or_add_remote(self, path: Path | str, remote_url: str, remote: str = "origin") -> GitResult:
        existing = self.get_remote_url(path, remote)
        if existing:
            return self.run_command(path, ["remote", "set-url", remote, remote_url])
        return self.run_command(path, ["remote", "add", remote, remote_url])

    def get_status(self, path: Path | str) -> GitStatusInfo:
        res = self.run_command(path, ["status", "--porcelain=v1"])
        if not res.success:
            return GitStatusInfo(
                is_clean=True,
                staged_files=[],
                unstaged_files=[],
                untracked_files=[],
                total_changed_files=0,
            )

        staged: List[str] = []
        unstaged: List[str] = []
        untracked: List[str] = []

        for line in res.stdout.splitlines():
            if len(line) < 3:
                continue
            index_status = line[0]
            worktree_status = line[1]
            file_name = line[3:].strip()

            if index_status in ("M", "A", "D", "R", "C"):
                staged.append(file_name)
            if worktree_status in ("M", "D"):
                unstaged.append(file_name)
            if index_status == "?" and worktree_status == "?":
                untracked.append(file_name)

        all_unique = set(staged + unstaged + untracked)

        deleted_lines = 0
        diff_stat = self.run_command(path, ["diff", "--numstat"])
        if diff_stat.success and diff_stat.stdout:
            for row in diff_stat.stdout.splitlines():
                parts = row.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    deleted_lines += int(parts[1])

        return GitStatusInfo(
            is_clean=len(all_unique) == 0,
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            total_changed_files=len(all_unique),
            deleted_lines_est=deleted_lines,
        )

    def has_unpushed_commits(
        self,
        path: Path | str,
        remote: str = "origin",
        branch: Optional[str] = None,
    ) -> bool:
        if not self.get_remote_url(path, remote):
            return False
        if not branch:
            branch = self.get_current_branch(path)
        status_res = self.run_command(path, ["status", "--porcelain=v1", "-b"])
        if status_res.success and status_res.stdout:
            first_line = status_res.stdout.splitlines()[0] if status_res.stdout.splitlines() else ""
            if "ahead" in first_line:
                return True
        rev_remote = self.run_command(path, ["rev-parse", "--verify", f"{remote}/{branch}"])
        if not rev_remote.success:
            rev_local = self.run_command(path, ["rev-parse", "--verify", "HEAD"])
            return rev_local.success
        log_res = self.run_command(path, ["log", f"{remote}/{branch}..HEAD", "--oneline"])
        return log_res.success and bool(log_res.stdout.strip())

    def stage_all(self, path: Path | str) -> GitResult:
        return self.run_command(path, ["add", "-A"])

    def commit(self, path: Path | str, message: str) -> GitResult:
        clean_msg = message.strip()
        if not clean_msg:
            clean_msg = "auto: update files via GH-BOT-REPOS"
        return self.run_command(path, ["commit", "-m", clean_msg])

    def push(
        self,
        path: Path | str,
        remote: str = "origin",
        branch: Optional[str] = None,
        set_upstream: bool = True,
        auth_token: Optional[str] = None,
    ) -> GitResult:
        if not branch:
            branch = self.get_current_branch(path)

        args = ["push"]
        if set_upstream:
            args.extend(["-u", remote, branch])
        else:
            args.extend([remote, branch])

        env = {}
        if auth_token:
            import base64
            auth_b64 = base64.b64encode(f"x-access-token:{auth_token}".encode("ascii")).decode("ascii")
            args = [
                "-c",
                "credential.helper=",
                "-c",
                f"http.extraHeader=Authorization: Basic {auth_b64}",
            ] + args

        return self.run_command(path, args, timeout=60, env=env)

    def pull_rebase(
        self,
        path: Path | str,
        remote: str = "origin",
        branch: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> GitResult:
        if not branch:
            branch = self.get_current_branch(path)

        args = ["pull", "--rebase", remote, branch]
        env = {}
        if auth_token:
            import base64
            auth_b64 = base64.b64encode(f"x-access-token:{auth_token}".encode("ascii")).decode("ascii")
            args = [
                "-c",
                "credential.helper=",
                "-c",
                f"http.extraHeader=Authorization: Basic {auth_b64}",
            ] + args

        return self.run_command(path, args, timeout=60, env=env)

    def get_last_commit(self, path: Path | str) -> Optional[GitCommitInfo]:
        res = self.run_command(path, ["log", "-1", "--pretty=format:%H%x1f%h%x1f%an%x1f%ad%x1f%s"])
        if res.success and res.stdout:
            parts = res.stdout.split("\x1f")
            if len(parts) >= 5:
                return GitCommitInfo(
                    hash=parts[0],
                    short_hash=parts[1],
                    author=parts[2],
                    date=parts[3],
                    message=parts[4],
                )
        return None
