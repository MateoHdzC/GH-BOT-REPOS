
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.utils.logger import log_event

@dataclass
class PendingPush:
    project_path: str
    project_name: str
    remote: str
    branch: str
    attempts: int = 0
    max_attempts: int = 5
    last_attempt_time: float = 0.0
    last_error: str = ""
    next_retry_time: float = 0.0

class RetryQueue:

    def __init__(self):
        self._lock = threading.Lock()
        self._queue: Dict[str, PendingPush] = {}

    def add_or_update(
        self,
        project_path: str,
        project_name: str,
        remote: str,
        branch: str,
        error: str,
    ) -> PendingPush:
        with self._lock:
            now = time.time()
            existing = self._queue.get(project_path)
            if existing:
                existing.attempts += 1
                existing.last_attempt_time = now
                existing.last_error = error
                delay = min(300, 30 * (2 ** (existing.attempts - 1)))
                existing.next_retry_time = now + delay
                item = existing
            else:
                item = PendingPush(
                    project_path=project_path,
                    project_name=project_name,
                    remote=remote,
                    branch=branch,
                    attempts=1,
                    last_attempt_time=now,
                    last_error=error,
                    next_retry_time=now + 30,
                )
                self._queue[project_path] = item

            log_event(
                "PUSH",
                f"{project_name}: Push enqueued for retry (Attempt {item.attempts}, delay={int(item.next_retry_time - now)}s). Reason: {error}",
            )
            return item

    def remove(self, project_path: str) -> None:
        with self._lock:
            if project_path in self._queue:
                item = self._queue.pop(project_path)
                log_event("PUSH", f"{item.project_name}: Removed from retry queue (successful).")

    def get_due_items(self) -> List[PendingPush]:
        with self._lock:
            now = time.time()
            return [
                item for item in self._queue.values()
                if now >= item.next_retry_time and item.attempts < item.max_attempts
            ]

    def get_all(self) -> List[PendingPush]:
        with self._lock:
            return list(self._queue.values())

    def clear(self) -> None:
        with self._lock:
            self._queue.clear()
