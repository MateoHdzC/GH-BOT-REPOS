
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, Optional

from watchdog.events import (
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from src.utils.logger import log_event
from src.watcher.filter import PathFilter

class ProjectEventHandler(FileSystemEventHandler):

    def __init__(
        self,
        project_name: str,
        project_dir: Path,
        on_change: Callable[[str, str], None],
        path_filter: PathFilter,
    ):
        super().__init__()
        self.project_name = project_name
        self.project_dir = project_dir
        self.on_change = on_change
        self.filter = path_filter

    def _process_event(self, event_type: str, src_path: str, dest_path: Optional[str] = None) -> None:
        target_path = dest_path if (event_type == "MOVED" and dest_path) else src_path
        if self.filter.should_ignore(target_path, self.project_dir):
            return

        rel_path = os.path.relpath(target_path, self.project_dir)
        log_event("WATCHER", f"{self.project_name}: {event_type} on {rel_path}")
        self.on_change(event_type, target_path)

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._process_event("CREATED", event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._process_event("MODIFIED", event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._process_event("DELETED", event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        dest = getattr(event, "dest_path", None)
        self._process_event("MOVED", event.src_path, dest)

class WatcherService:

    def __init__(self):
        self._observers: Dict[str, Observer] = {}

    def start_watching(
        self,
        project_path: str,
        project_name: str,
        on_change_callback: Callable[[str, str], None],
        path_filter: Optional[PathFilter] = None,
    ) -> bool:
        resolved = str(Path(project_path).resolve())
        if resolved in self._observers:
            log_event("WATCHER", f"Already watching: {project_name} ({resolved})")
            return True

        target_dir = Path(resolved)
        if not target_dir.exists() or not target_dir.is_dir():
            log_event("ERROR", f"Cannot watch non-existent directory: {resolved}")
            return False

        if path_filter is None:
            path_filter = PathFilter()

        handler = ProjectEventHandler(
            project_name=project_name,
            project_dir=target_dir,
            on_change=on_change_callback,
            path_filter=path_filter,
        )

        try:
            observer = Observer()
            observer.schedule(handler, str(target_dir), recursive=True)
            observer.daemon = True
            observer.start()
            self._observers[resolved] = observer
            log_event("WATCHER", f"Started observer for {project_name} at {resolved}")
            return True
        except Exception as ex:
            log_event("ERROR", f"Failed to start watcher for {project_name}: {ex}")
            return False

    def stop_watching(self, project_path: str) -> bool:
        resolved = str(Path(project_path).resolve())
        observer = self._observers.pop(resolved, None)
        if observer:
            try:
                observer.stop()
                observer.join(timeout=2.0)
                log_event("WATCHER", f"Stopped observer for {resolved}")
                return True
            except Exception as ex:
                log_event("ERROR", f"Error stopping observer for {resolved}: {ex}")
        return False

    def stop_all(self) -> None:
        paths = list(self._observers.keys())
        for path in paths:
            self.stop_watching(path)

    def is_watching(self, project_path: str) -> bool:
        resolved = str(Path(project_path).resolve())
        obs = self._observers.get(resolved)
        return obs is not None and obs.is_alive()
