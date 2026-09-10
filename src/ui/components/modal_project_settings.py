from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from src.config.models import ProjectConfig, ProjectMode
from src.core.project_manager import ProjectManager
from src.ui.theme import Theme

DEBOUNCE_OPTIONS = {
    "1 minuto (60s)": 60,
    "2 minutos (120s)": 120,
    "4 minutos (240s)": 240,
    "5 minutos (300s)": 300,
    "10 minutos (600s)": 600,
    "30 minutos (1800s)": 1800,
    "1 hora (3600s)": 3600,
}

class ModalProjectSettings(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        manager: ProjectManager,
        on_settings_saved: Callable[[ProjectConfig], None],
    ):
        super().__init__(parent)
        self.manager = manager
        self.on_settings_saved = on_settings_saved
        self.cfg = manager.config

        self.title(f"Configuración — {self.cfg.name}")
        self.geometry("580x600")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_MAIN)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.after(50, lambda: self.grab_set() if self.winfo_exists() else None)

        self._build_ui()

    def _build_ui(self) -> None:
        title_lbl = ctk.CTkLabel(
            self,
            text=f"Ajustes del Proyecto: {self.cfg.name}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w", padx=25, pady=(20, 5))

        path_lbl = ctk.CTkLabel(
            self,
            text=self.cfg.path,
            font=ctk.CTkFont(family=Theme.FONT_MONO, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        path_lbl.pack(anchor="w", padx=25, pady=(0, 15))

        container = ctk.CTkScrollableFrame(self, fg_color=Theme.BG_MAIN, corner_radius=0)
        container.pack(fill="both", expand=True, padx=25, pady=5)

        self._add_label(container, "Repositorio Remoto (GitHub URL):")
        self.remote_entry = ctk.CTkEntry(
            container,
            placeholder_text="https://github.com/usuario/proyecto.git",
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=6,
            height=34,
        )
        self.remote_entry.insert(0, self.cfg.remote or "")
        self.remote_entry.pack(fill="x", pady=(2, 10))

        branch_mode_row = ctk.CTkFrame(container, fg_color=Theme.BG_MAIN, corner_radius=0)
        branch_mode_row.pack(fill="x", pady=5)
        branch_mode_row.columnconfigure(0, weight=1)
        branch_mode_row.columnconfigure(1, weight=1)

        col0 = ctk.CTkFrame(branch_mode_row, fg_color=Theme.BG_MAIN, corner_radius=0)
        col0.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._add_label(col0, "Rama (Branch):")
        self.branch_entry = ctk.CTkEntry(
            col0,
            placeholder_text="main",
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=6,
            height=34,
        )
        self.branch_entry.insert(0, self.cfg.branch or "main")
        self.branch_entry.pack(fill="x", pady=(2, 0))

        col1 = ctk.CTkFrame(branch_mode_row, fg_color=Theme.BG_MAIN, corner_radius=0)
        col1.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._add_label(col1, "Modo de Sincronización:")
        self.mode_menu = ctk.CTkOptionMenu(
            col1,
            values=["AUTO", "COMMIT_ONLY", "PAUSED"],
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_HOVER,
            corner_radius=6,
            height=34,
        )
        self.mode_menu.set(self.cfg.mode.value if isinstance(self.cfg.mode, ProjectMode) else str(self.cfg.mode))
        self.mode_menu.pack(fill="x", pady=(2, 0))

        self._add_label(container, "Tiempo de Espera (Debounce):")
        current_debounce_label = "5 minutos (300s)"
        for label, val in DEBOUNCE_OPTIONS.items():
            if val == self.cfg.debounce_seconds:
                current_debounce_label = label
                break

        self.debounce_menu = ctk.CTkOptionMenu(
            container,
            values=list(DEBOUNCE_OPTIONS.keys()),
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            button_color=Theme.PRIMARY,
            button_hover_color=Theme.PRIMARY_HOVER,
            corner_radius=6,
            height=34,
        )
        self.debounce_menu.set(current_debounce_label)
        self.debounce_menu.pack(fill="x", pady=(2, 12))

        options_frame = ctk.CTkFrame(
            container,
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            corner_radius=8,
            border_width=1,
            border_color=Theme.BORDER,
        )
        options_frame.pack(fill="x", pady=10)

        self.safety_chk = ctk.CTkCheckBox(
            options_frame,
            text="Safety Guard activo (bloqueo / alerta de seguridad)",
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.PRIMARY_HOVER,
        )
        if self.cfg.safety_guard_enabled:
            self.safety_chk.select()
        else:
            self.safety_chk.deselect()
        self.safety_chk.pack(anchor="w", padx=14, pady=(12, 6))

        self.allow_sensitive_chk = ctk.CTkCheckBox(
            options_frame,
            text="Permitir archivos sensibles (.env, certificados, claves de prueba)",
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.PRIMARY_HOVER,
        )
        if getattr(self.cfg, "allow_sensitive_files", False):
            self.allow_sensitive_chk.select()
        else:
            self.allow_sensitive_chk.deselect()
        self.allow_sensitive_chk.pack(anchor="w", padx=14, pady=(6, 6))

        self.dry_run_chk = ctk.CTkCheckBox(
            options_frame,
            text="Modo DRY RUN (simula cambios sin commitear ni pushear)",
            text_color=Theme.TEXT_SECONDARY,
            fg_color=Theme.WARNING,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.WARNING,
        )
        if self.cfg.dry_run:
            self.dry_run_chk.select()
        else:
            self.dry_run_chk.deselect()
        self.dry_run_chk.pack(anchor="w", padx=14, pady=(6, 12))

        self.error_label = ctk.CTkLabel(
            container,
            text="",
            text_color=Theme.ERROR,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
        )
        self.error_label.pack(anchor="w", pady=5)

        btn_row = ctk.CTkFrame(self, fg_color=Theme.BG_MAIN, corner_radius=0)
        btn_row.pack(side="bottom", fill="x", padx=25, pady=20)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancelar",
            fg_color=Theme.BTN_SECONDARY,
            bg_color=Theme.BG_MAIN,
            hover_color=Theme.BTN_SECONDARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            height=36,
            width=100,
            corner_radius=6,
            border_width=0,
            command=self._on_cancel,
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_row,
            text="Guardar Cambios",
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_MAIN,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            height=36,
            width=130,
            corner_radius=6,
            border_width=0,
            command=self._on_save,
        )
        save_btn.pack(side="right")

    def _add_label(self, parent, text: str) -> None:
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=Theme.TEXT_SECONDARY,
        )
        lbl.pack(anchor="w", pady=(8, 2))

    def _on_cancel(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _on_save(self) -> None:
        remote_str = self.remote_entry.get().strip()
        branch_str = self.branch_entry.get().strip() or "main"
        mode_str = self.mode_menu.get()

        try:
            debounce_secs = DEBOUNCE_OPTIONS.get(self.debounce_menu.get(), 300)
            mode = ProjectMode(mode_str)

            self.cfg.remote = remote_str
            self.cfg.branch = branch_str
            self.cfg.mode = mode
            self.cfg.debounce_seconds = debounce_secs
            self.cfg.safety_guard_enabled = bool(self.safety_chk.get())
            self.cfg.allow_sensitive_files = bool(self.allow_sensitive_chk.get())
            self.cfg.dry_run = bool(self.dry_run_chk.get())

            self.manager.debounce.debounce_seconds = debounce_secs
            self.manager.safety_guard.enabled = self.cfg.safety_guard_enabled
            self.manager.safety_guard.allow_sensitive_files = self.cfg.allow_sensitive_files

            saved_cfg = self.cfg
            parent_widget = self.master

            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

            if self.on_settings_saved and parent_widget:
                parent_widget.after(10, lambda: self.on_settings_saved(saved_cfg))
        except Exception as ex:
            self.error_label.configure(text=f"Error al guardar: {ex}")
