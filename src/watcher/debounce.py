"""Thread-safe debouncing timer for Git synchronization triggers."""

from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from src.utils.logger import log_event


class DebounceController:
    """Manages a reset-capable countdown timer per project."""

    def __init__(
        self,
        project_name: str,
        debounce_seconds: int,
        on_trigger: Callable[[], None],
    ):
        self.project_name = project_name
        self.debounce_seconds = max(1, debounce_seconds)
        self.on_trigger = on_trigger

        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None
        self._last_event_time: float = 0.0
        self._is_active: bool = False

    @property
    def is_pending(self) -> bool:
        with self._lock:
            return self._timer is not None and self._timer.is_alive()

    @property
    def remaining_seconds(self) -> int:
        with self._lock:
            if not self.is_pending:
                return 0
            elapsed = time.time() - self._last_event_time
            remaining = self.debounce_seconds - elapsed
            return max(0, int(remaining))

    def notify_change(self) -> None:
        """Register a filesystem change. Starts or restarts the debounce timer."""
        with self._lock:
            self._last_event_time = time.time()
            if self._timer and self._timer.is_alive():
                self._timer.cancel()

            self._timer = threading.Timer(float(self.debounce_seconds), self._execute)
            self._timer.daemon = True
            self._timer.start()
            log_event(
                "WATCHER",
                f"{self.project_name}: Change registered. Debounce timer set to {self.debounce_seconds}s.",
            )

    def trigger_now(self) -> None:
        """Cancel any running timer and invoke the synchronization callback immediately."""
        with self._lock:
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
            self._timer = None

        log_event("WATCHER", f"{self.project_name}: Manual immediate trigger (⚡ Subir ahora).")
        self._execute()

    def cancel(self) -> None:
        """Cancel any scheduled debounce countdown."""
        with self._lock:
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
            self._timer = None

    def update_debounce_time(self, new_seconds: int) -> None:
        """Update debounce interval."""
        with self._lock:
            self.debounce_seconds = max(1, new_seconds)

    def _execute(self) -> None:
        """Trigger target action safely in a separate thread."""
        with self._lock:
            self._timer = None

        try:
            self.on_trigger()
        except Exception as ex:
            log_event("ERROR", f"{self.project_name}: Debounce trigger execution error: {ex}")
