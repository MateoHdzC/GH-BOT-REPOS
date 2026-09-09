"""Real-time log viewer component for GH-BOT-REPOS."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List

import customtkinter as ctk
from src.ui.theme import Theme
from src.utils.logger import get_ui_stream_handler


class LogsView(ctk.CTkFrame):
    """Component for monitoring live operational logs and events."""

    def __init__(self, master, log_file_path: Path, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_MAIN,
            corner_radius=0,
            **kwargs,
        )
        self.log_file_path = log_file_path
        self._filter_cat = "TODOS"
        self._raw_logs: List[str] = []

        self._build_ui()
        self._attach_listener()
        self._load_existing_logs()

    def _build_ui(self) -> None:
        # Header & Controls
        header = ctk.CTkFrame(self, fg_color=Theme.BG_MAIN, corner_radius=0)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="Actividad y Logs en Tiempo Real",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title.pack(side="left")

        # Action Buttons
        open_btn = ctk.CTkButton(
            header,
            text="Abrir app.log",
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            width=90,
            height=30,
            corner_radius=6,
            border_width=0,
            command=self._open_log_file,
        )
        open_btn.pack(side="right", padx=(6, 0))

        clear_btn = ctk.CTkButton(
            header,
            text="Limpiar",
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            width=70,
            height=30,
            corner_radius=6,
            border_width=0,
            command=self._clear_logs,
        )
        clear_btn.pack(side="right", padx=6)

        # Category Filter
        filter_box = ctk.CTkOptionMenu(
            header,
            values=[
                "TODOS",
                "[SYSTEM]",
                "[PROJECT]",
                "[WATCHER]",
                "[GIT]",
                "[COMMIT]",
                "[PUSH]",
                "[ERROR]",
                "[SECURITY]",
            ],
            command=self._on_filter_changed,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            fg_color=Theme.BG_CARD,
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_HOVER,
            corner_radius=6,
            width=120,
            height=30,
        )
        filter_box.set("TODOS")
        filter_box.pack(side="right", padx=6)

        # Text Console
        self.text_box = ctk.CTkTextbox(
            self,
            fg_color=Theme.BG_CARD,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_MONO, size=11),
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER,
            wrap="none",
        )
        self.text_box.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    def _attach_listener(self) -> None:
        handler = get_ui_stream_handler()
        handler.callback = self._on_new_log

    def _load_existing_logs(self) -> None:
        handler = get_ui_stream_handler()
        self._raw_logs = list(handler.history)
        self._render_logs()

    def _on_new_log(self, message: str) -> None:
        self._raw_logs.append(message)
        if len(self._raw_logs) > 1000:
            self._raw_logs.pop(0)

        # Check if matches current filter
        if self._filter_cat == "TODOS" or self._filter_cat in message:
            self.text_box.configure(state="normal")
            self.text_box.insert("end", message + "\n")
            self.text_box.see("end")
            self.text_box.configure(state="disabled")

    def _render_logs(self) -> None:
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        for line in self._raw_logs:
            if self._filter_cat == "TODOS" or self._filter_cat in line:
                self.text_box.insert("end", line + "\n")
        self.text_box.see("end")
        self.text_box.configure(state="disabled")

    def _on_filter_changed(self, choice: str) -> None:
        self._filter_cat = choice
        self._render_logs()

    def _clear_logs(self) -> None:
        self._raw_logs.clear()
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.configure(state="disabled")

    def _open_log_file(self) -> None:
        if self.log_file_path.exists():
            try:
                os.startfile(str(self.log_file_path))
            except Exception:
                subprocess.Popen(["notepad.exe", str(self.log_file_path)])
