"""Main Application Window for GH-BOT-REPOS using CustomTkinter."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List, Optional

import customtkinter as ctk

from src.config.manager import ConfigManager
from src.config.models import ProjectConfig, ProjectMode, ProjectStatus
from src.core.engine import Engine
from src.core.project_manager import ProjectManager
from src.git.credentials import GitHubCredentials
from src.ui.components.dashboard_view import DashboardView
from src.ui.components.logs_view import LogsView
from src.ui.components.modal_add_project import ModalAddProject
from src.ui.components.modal_history import ModalProjectHistory
from src.ui.components.project_card import ProjectCard
from src.ui.components.settings_view import SettingsView
from src.ui.components.sidebar import Sidebar
from src.ui.theme import Theme
from src.ui.tray import SystemTrayManager
from src.utils.logger import log_event
from src.utils.notifier import WindowsNotifier


class MainApplication(ctk.CTk):
    """Primary application frame and lifecycle controller."""

    def __init__(self, engine: Engine, config_manager: ConfigManager):
        super().__init__()
        self.engine = engine
        self.config_manager = config_manager

        # Appearance configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("GH-BOT-REPOS — Windows")
        self.geometry("1100x720")
        self.minsize(940, 620)
        self.configure(fg_color=Theme.BG_MAIN)

        # Set Window Icon
        self.assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        ico_path = self.assets_dir / "icon.ico"
        if ico_path.exists():
            try:
                self.iconbitmap(str(ico_path))
            except Exception:
                pass

        self._active_view_key = "todos"
        self._project_cards: Dict[str, ProjectCard] = {}

        # Intercept window close button (X) to minimize to System Tray
        self.protocol("WM_DELETE_WINDOW", self.on_close_to_tray)

        # Setup System Tray
        self.tray = SystemTrayManager(
            engine=self.engine,
            on_show_window=self.show_window_from_tray,
            on_exit_app=self.quit_app,
        )
        self.tray.start()

        self._build_layout()

        # Start Engine
        self.engine.start()

        # Connect notifications dispatch
        self.engine.on_notify = self._dispatch_notification

        # Periodic refresh cycle
        self.after(1000, self._periodic_ui_refresh)

    def _build_layout(self) -> None:
        # 1. Left Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self._on_navigate,
            on_exit=self.quit_app,
        )
        self.sidebar.pack(side="left", fill="y")

        # 2. Main Container
        self.main_container = ctk.CTkFrame(self, fg_color=Theme.BG_MAIN, corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        # Top Bar (Title + Action Buttons)
        self.top_bar = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_MAIN, height=60, corner_radius=0)
        self.top_bar.pack(fill="x", padx=25, pady=(20, 10))

        self.view_title_lbl = ctk.CTkLabel(
            self.top_bar,
            text="Todos los Proyectos",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.view_title_lbl.pack(side="left")

        # Action Buttons on Top Bar
        self.add_btn = ctk.CTkButton(
            self.top_bar,
            text="+ Añadir Proyecto",
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            height=34,
            width=130,
            corner_radius=6,
            border_width=0,
            command=self._open_add_project_modal,
        )
        self.add_btn.pack(side="right", padx=(10, 0))

        self.sync_all_btn = ctk.CTkButton(
            self.top_bar,
            text="⚡ Subir Todos",
            fg_color=Theme.BG_CARD,
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            height=34,
            width=110,
            corner_radius=6,
            border_width=0,
            command=self._sync_all_projects,
        )
        self.sync_all_btn.pack(side="right")

        # Content Area
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_MAIN, corner_radius=0)
        self.content_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # 3. Views Initialization
        self.projects_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color=Theme.BG_MAIN, corner_radius=0)
        self.dashboard_view = DashboardView(self.content_frame, self.engine)
        logs_path = Path(__file__).resolve().parent.parent.parent / "logs" / "app.log"
        self.logs_view = LogsView(self.content_frame, logs_path)
        self.settings_view = SettingsView(self.content_frame, on_auth_changed=self._on_auth_changed)

        # Initially display projects list
        self._switch_view("todos")
        self._render_project_cards()
        self._update_sidebar_stats()

    def _on_navigate(self, view_key: str) -> None:
        self._switch_view(view_key)

    def _switch_view(self, view_key: str) -> None:
        self._active_view_key = view_key

        # Hide all views
        self.projects_scroll.pack_forget()
        self.dashboard_view.pack_forget()
        self.logs_view.pack_forget()
        self.settings_view.pack_forget()

        # Update Top Bar visibility & title
        if view_key in ("todos", "activos", "pausados"):
            self.top_bar.pack(fill="x", padx=25, pady=(20, 10))
            self.add_btn.pack(side="right", padx=(10, 0))
            self.sync_all_btn.pack(side="right")

            titles = {
                "todos": "Todos los Proyectos",
                "activos": "Proyectos Activos",
                "pausados": "Proyectos Pausados",
            }
            self.view_title_lbl.configure(text=titles[view_key])
            self.projects_scroll.pack(fill="both", expand=True)
            self._render_project_cards()

        elif view_key == "dashboard":
            self.top_bar.pack_forget()
            self.dashboard_view.refresh()
            self.dashboard_view.pack(fill="both", expand=True)

        elif view_key == "logs":
            self.top_bar.pack_forget()
            self.logs_view.pack(fill="both", expand=True)

        elif view_key == "configuracion":
            self.top_bar.pack_forget()
            self.settings_view.refresh()
            self.settings_view.pack(fill="both", expand=True)

    def _render_project_cards(self) -> None:
        # Clear existing card widgets
        for widget in self.projects_scroll.winfo_children():
            widget.destroy()
        self._project_cards.clear()

        managers = self.engine.get_all_managers()

        # Filter by selected tab
        if self._active_view_key == "activos":
            filtered = [m for m in managers if m.config.mode != ProjectMode.PAUSED and m.config.enabled]
        elif self._active_view_key == "pausados":
            filtered = [m for m in managers if m.config.mode == ProjectMode.PAUSED or not m.config.enabled]
        else:
            filtered = managers

        if not filtered:
            empty_box = ctk.CTkFrame(self.projects_scroll, fg_color=Theme.BG_CARD, corner_radius=10)
            empty_box.pack(fill="x", pady=40, padx=20)
            empty_lbl = ctk.CTkLabel(
                empty_box,
                text="No hay proyectos en esta categoría.\nPresiona '+ Añadir Proyecto' para comenzar a vigilar una carpeta.",
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13),
                text_color=Theme.TEXT_MUTED,
                justify="center",
            )
            empty_lbl.pack(pady=30)
            return

        for pm in filtered:
            card = ProjectCard(
                self.projects_scroll,
                manager=pm,
                on_mode_change=self._on_project_mode_change,
                on_sync_now=self._on_project_sync_now,
                on_delete=self._on_project_delete,
                on_view_history=self._on_view_project_history,
            )
            card.pack(fill="x", pady=8)
            self._project_cards[pm.config.path] = card

    def _open_add_project_modal(self) -> None:
        ModalAddProject(self, self.engine.git, on_project_added=self._on_project_added)

    def _on_project_added(self, project: ProjectConfig) -> None:
        if self.engine.add_project(project):
            self._render_project_cards()
            self._update_sidebar_stats()
            self.tray.update_menu()
            WindowsNotifier.notify(project.name, "Proyecto añadido y vigilancia activada.", "success")

    def _on_project_mode_change(self, path: str, mode: ProjectMode) -> None:
        self.engine.set_project_mode(path, mode)
        self._render_project_cards()
        self._update_sidebar_stats()
        self.tray.update_menu()

    def _on_project_sync_now(self, path: str) -> None:
        self.engine.sync_project_now(path)

    def _sync_all_projects(self) -> None:
        self.engine.sync_all_now()

    def _on_project_delete(self, path: str) -> None:
        pm = self.engine.get_manager(path)
        name = pm.config.name if pm else path
        confirm = messagebox.askyesno(
            "Eliminar Proyecto",
            f"¿Deseas dejar de vigilar el proyecto '{name}'?\n\n(No se eliminarán tus archivos ni tu repositorio Git local).",
        )
        if confirm:
            self.engine.remove_project(path)
            self._render_project_cards()
            self._update_sidebar_stats()
            self.tray.update_menu()

    def _on_view_project_history(self, manager: ProjectManager) -> None:
        ModalProjectHistory(self, manager)

    def _on_auth_changed(self) -> None:
        self._update_sidebar_stats()

    def _periodic_ui_refresh(self) -> None:
        """Periodic background refresh for cards and stats."""
        for card in self._project_cards.values():
            card.refresh()
        self._update_sidebar_stats()
        self.after(2000, self._periodic_ui_refresh)

    def _update_sidebar_stats(self) -> None:
        stats = self.engine.get_dashboard_stats()
        self.sidebar.update_counts(
            total=stats["total_projects"],
            active=stats["active_projects"],
            paused=stats["paused_projects"],
        )
        # GitHub Status
        token = GitHubCredentials.get_token()
        username = GitHubCredentials.get_username() or ""
        self.sidebar.update_system_status(
            github_connected=bool(token),
            github_user=username,
            engine_running=self.engine.is_running,
        )

    def _dispatch_notification(self, level: str, title: str, message: str) -> None:
        WindowsNotifier.notify(title, message, level)

    def on_close_to_tray(self) -> None:
        """Minimize window to System Tray instead of terminating the engine."""
        self.withdraw()
        WindowsNotifier.notify(
            "Segundo Plano",
            "GH-BOT-REPOS sigue activo vigilando tus proyectos desde la bandeja del sistema.",
            "info",
        )

    def show_window_from_tray(self) -> None:
        """Restore window from System Tray."""
        self.after(0, self._restore_window)

    def _restore_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self) -> None:
        """Cleanly terminate the application and all background processes."""
        log_event("SYSTEM", "User requested application shutdown.")
        self.tray.stop()
        self.engine.stop()
        self.destroy()
        sys.exit(0)
