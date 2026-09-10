
from __future__ import annotations

import customtkinter as ctk

from src.core.project_manager import ProjectManager
from src.ui.theme import Theme

class ModalProjectHistory(ctk.CTkToplevel):

    def __init__(self, parent, manager: ProjectManager):
        super().__init__(parent)
        self.manager = manager

        self.title(f"Historial de Sincronización — {manager.config.name}")
        self.geometry("580x480")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_MAIN)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(50, lambda: self.grab_set() if self.winfo_exists() else None)

        self._build_ui()

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(
            self,
            text=f"Historial: {self.manager.config.name}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title.pack(anchor="w", padx=25, pady=(20, 5))

        sub = ctk.CTkLabel(
            self,
            text=f"Ruta: {self.manager.config.path}",
            font=ctk.CTkFont(family=Theme.FONT_MONO, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        sub.pack(anchor="w", padx=25, pady=(0, 15))

        container = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            corner_radius=8,
            border_width=1,
            border_color=Theme.BORDER,
        )
        container.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        if not self.manager.history:
            empty_lbl = ctk.CTkLabel(
                container,
                text="Aún no hay sincronizaciones registradas para este proyecto.",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
                text_color=Theme.TEXT_MUTED,
            )
            empty_lbl.pack(pady=40)
        else:
            for entry in self.manager.history:
                row = ctk.CTkFrame(container, fg_color=Theme.BG_CARD, corner_radius=0)
                row.pack(fill="x", padx=12, pady=8)

                time_lbl = ctk.CTkLabel(
                    row,
                    text=entry.timestamp,
                    font=ctk.CTkFont(family=Theme.FONT_MONO, size=11, weight="bold"),
                    text_color=Theme.TEXT_MUTED,
                    width=70,
                    anchor="w",
                )
                time_lbl.pack(side="left")

                status_color = (
                    Theme.SUCCESS
                    if "✓" in entry.status
                    else (Theme.WARNING if "⚠" in entry.status else Theme.ERROR)
                )
                status_lbl = ctk.CTkLabel(
                    row,
                    text=entry.status,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
                    text_color=status_color,
                    width=150,
                    anchor="w",
                )
                status_lbl.pack(side="left")

                detail_lbl = ctk.CTkLabel(
                    row,
                    text=entry.detail,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w",
                )
                detail_lbl.pack(side="left", fill="x", expand=True)

        close_btn = ctk.CTkButton(
            self,
            text="Cerrar",
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_MAIN,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=6,
            border_width=0,
            height=32,
            width=90,
            command=self._close,
        )
        close_btn.pack(side="right", padx=25, pady=(0, 15))

    def _close(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
