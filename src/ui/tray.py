
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Callable, List, Optional

import pystray
from PIL import Image

from src.core.engine import Engine
from src.utils.logger import log_event
from src.utils.notifier import register_tray_icon

class SystemTrayManager:

    def __init__(
        self,
        engine: Engine,
        on_show_window: Callable[[], None],
        on_exit_app: Callable[[], None],
        icon_path: Optional[Path] = None,
    ):
        self.engine = engine
        self.on_show_window = on_show_window
        self.on_exit_app = on_exit_app

        if icon_path is None:
            icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.png"
        self.icon_path = icon_path

        self._tray_icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._tray_icon is not None:
            return

        try:
            image = Image.open(str(self.icon_path))
        except Exception:
            image = Image.new("RGBA", (64, 64), (10, 132, 255, 255))

        self._tray_icon = pystray.Icon(
            "GH-BOT-REPOS",
            image,
            "GH-BOT-REPOS",
            menu=self._create_menu(),
        )

        register_tray_icon(self._tray_icon)

        self._thread = threading.Thread(target=self._run_tray, daemon=True)
        self._thread.start()
        log_event("SYSTEM", "System Tray icon initialized.")

    def _run_tray(self) -> None:
        if self._tray_icon:
            self._tray_icon.run()

    def _create_menu(self) -> pystray.Menu:
        managers = self.engine.get_all_managers()
        project_items = []
        for pm in managers:
            status_text = pm.status.value
            mode_text = pm.config.mode.value
            label = f"{pm.config.name} ({mode_text} - {status_text})"
            project_items.append(
                pystray.MenuItem(label, self._make_project_click_handler(pm.config.path))
            )

        if not project_items:
            project_items.append(pystray.MenuItem("Sin proyectos configurados", None, enabled=False))

        return pystray.Menu(
            pystray.MenuItem("GH-BOT-REPOS", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Abrir", self._handle_open, default=True),
            pystray.MenuItem("Proyectos", pystray.Menu(*project_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚡ Subir todos", self._handle_sync_all),
            pystray.MenuItem("⏸ Pausar todos", self._handle_pause_all),
            pystray.MenuItem("▶ Reanudar todos", self._handle_resume_all),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self._handle_exit),
        )

    def _make_project_click_handler(self, path: str):
        def handler(icon, item):
            self.on_show_window()
        return handler

    def _handle_open(self, icon, item) -> None:
        self.on_show_window()

    def _handle_sync_all(self, icon, item) -> None:
        self.engine.sync_all_now()

    def _handle_pause_all(self, icon, item) -> None:
        self.engine.pause_all()
        self.update_menu()

    def _handle_resume_all(self, icon, item) -> None:
        self.engine.resume_all()
        self.update_menu()

    def _handle_exit(self, icon, item) -> None:
        self.stop()
        self.on_exit_app()

    def update_menu(self) -> None:
        if self._tray_icon:
            threading.Thread(target=self._safe_update_menu, daemon=True).start()

    def _safe_update_menu(self) -> None:
        try:
            if self._tray_icon:
                self._tray_icon.menu = self._create_menu()
        except Exception:
            pass

    def stop(self) -> None:
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
            register_tray_icon(None)
