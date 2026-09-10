
from __future__ import annotations

from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional

import customtkinter as ctk

from src.config.models import ProjectConfig, ProjectMode
from src.git.manager import GitManager
from src.ui.theme import Theme

DEBOUNCE_OPTIONS = {
    "1 minuto (60s)": 60,
    "4 minutos (240s)": 240,
    "5 minutos (300s)": 300,
    "10 minutos (600s)": 600,
    "30 minutos (1800s)": 1800,
    "1 hora (3600s)": 3600,
    "2 horas": 7200,
    "4 horas": 14400,
    "8 horas": 28800,
    "24 horas": 86400,
}

class ModalAddProject(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        git_manager: GitManager,
        on_project_added: Callable[[ProjectConfig], None],
    ):
        super().__init__(parent)
        self.git = git_manager
        self.on_project_added = on_project_added

        self.title("Añadir Proyecto a GH-BOT-REPOS")
        self.geometry("640x680")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_MAIN)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self) -> None:
        title_lbl = ctk.CTkLabel(
            self,
            text="Configurar Nuevo Proyecto",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w", padx=25, pady=(20, 5))

        desc_lbl = ctk.CTkLabel(
            self,
            text="Selecciona cualquier carpeta en tu PC. Si no es repositorio Git, podrás inicializarlo.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        desc_lbl.pack(anchor="w", padx=25, pady=(0, 15))

        container = ctk.CTkScrollableFrame(self, fg_color=Theme.BG_MAIN, corner_radius=0)
        container.pack(fill="both", expand=True, padx=25, pady=5)

        self._add_label(container, "Carpeta del Proyecto:")
        folder_row = ctk.CTkFrame(container, fg_color=Theme.BG_MAIN, corner_radius=0)
        folder_row.pack(fill="x", pady=(2, 8))

        self.path_entry = ctk.CTkEntry(
            folder_row,
            placeholder_text="C:\\Users\\...\\MiProyecto",
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=6,
            height=34,
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            folder_row,
            text="Explorar...",
            width=90,
            height=34,
            corner_radius=6,
            border_width=0,
            fg_color=Theme.BTN_SECONDARY,
            bg_color=Theme.BG_MAIN,
            hover_color=Theme.BTN_SECONDARY_HOVER,
            command=self._on_browse,
        )
        browse_btn.pack(side="right")

        self.git_alert_frame = ctk.CTkFrame(
            container,
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            corner_radius=6,
            border_width=1,
            border_color=Theme.BORDER,
        )
        self.git_alert_lbl = ctk.CTkLabel(
            self.git_alert_frame,
            text="",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.WARNING,
        )
        self.git_alert_lbl.pack(side="left", padx=12, pady=8)

        self.init_git_btn = ctk.CTkButton(
            self.git_alert_frame,
            text="Inicializar Git",
            width=110,
            height=26,
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._on_init_git,
        )

        self._add_label(container, "Nombre del Proyecto:")
        self.name_entry = ctk.CTkEntry(
            container,
            placeholder_text="MiProyecto",
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=6,
            height=34,
        )
        self.name_entry.pack(fill="x", pady=(2, 12))

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
        self.remote_entry.pack(fill="x", pady=(2, 12))

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
        self.branch_entry.insert(0, "main")
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
        self.mode_menu.set("AUTO")
        self.mode_menu.pack(fill="x", pady=(2, 0))

        self._add_label(container, "Tiempo de Espera (Debounce):")
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
        self.debounce_menu.set("5 minutos (300s)")
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
            text="Safety Guard activo (protege contra secretos y eliminaciones masivas)",
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.PRIMARY_HOVER,
        )
        self.safety_chk.select()
        self.safety_chk.pack(anchor="w", padx=14, pady=(12, 6))

        self.dry_run_chk = ctk.CTkCheckBox(
            options_frame,
            text="Modo DRY RUN (simula commits y pushes sin alterar Git ni GitHub)",
            text_color=Theme.TEXT_SECONDARY,
            fg_color=Theme.WARNING,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.WARNING,
        )
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
            command=self.destroy,
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_row,
            text="Añadir Proyecto",
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

    def _on_browse(self) -> None:
        self.grab_release()
        try:
            selected_dir = filedialog.askdirectory(title="Seleccionar carpeta del proyecto", parent=self)
        finally:
            self.grab_set()
        if selected_dir:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, selected_dir)
            p = Path(selected_dir)
            if not self.name_entry.get():
                self.name_entry.insert(0, p.name)

            self._inspect_directory(p)

    def _inspect_directory(self, path: Path) -> None:
        if not self.git.is_repo(path):
            self.git_alert_lbl.configure(text="⚠ Esta carpeta todavía no es un repositorio Git.")
            self.init_git_btn.pack(side="right", padx=10, pady=6)
            self.git_alert_frame.pack(fill="x", pady=6)
        else:
            self.git_alert_frame.pack_forget()
            branch = self.git.get_current_branch(path)
            self.branch_entry.delete(0, "end")
            self.branch_entry.insert(0, branch)
            remote = self.git.get_remote_url(path)
            if remote:
                self.remote_entry.delete(0, "end")
                self.remote_entry.insert(0, remote)

    def _on_init_git(self) -> None:
        path_str = self.path_entry.get().strip()
        if not path_str:
            return
        res = self.git.init_repo(path_str, initial_branch="main")
        if res.success:
            self.git_alert_lbl.configure(
                text="✓ Repositorio Git inicializado correctamente.",
                text_color=Theme.SUCCESS,
            )
            self.init_git_btn.pack_forget()
            self.branch_entry.delete(0, "end")
            self.branch_entry.insert(0, "main")
        else:
            self.git_alert_lbl.configure(
                text=f"Error al inicializar Git: {res.stderr}",
                text_color=Theme.ERROR,
            )

    def _on_save(self) -> None:
        path_str = self.path_entry.get().strip()
        name_str = self.name_entry.get().strip()
        remote_str = self.remote_entry.get().strip()
        branch_str = self.branch_entry.get().strip() or "main"
        mode_str = self.mode_menu.get()

        if not path_str:
            self.error_label.configure(text="Por favor selecciona la carpeta del proyecto.")
            return
        if not name_str:
            self.error_label.configure(text="Por favor ingresa un nombre para el proyecto.")
            return

        target_path = Path(path_str)
        if not target_path.exists():
            self.error_label.configure(text="La carpeta especificada no existe.")
            return

        if not self.git.is_repo(target_path):
            self.error_label.configure(
                text="La carpeta no es un repositorio Git. Presiona 'Inicializar Git' primero."
            )
            return

        try:
            if remote_str:
                self.git.set_or_add_remote(target_path, remote_str)

            debounce_secs = DEBOUNCE_OPTIONS.get(self.debounce_menu.get(), 300)
            mode = ProjectMode(mode_str)

            new_project = ProjectConfig(
                name=name_str,
                path=str(target_path.resolve()),
                remote=remote_str,
                branch=branch_str,
                mode=mode,
                debounce_seconds=debounce_secs,
                enabled=True,
                dry_run=bool(self.dry_run_chk.get()),
                safety_guard_enabled=bool(self.safety_chk.get()),
            )

            self.on_project_added(new_project)
            self.destroy()
        except Exception as ex:
            self.error_label.configure(text=f"Error al guardar proyecto: {ex}")
