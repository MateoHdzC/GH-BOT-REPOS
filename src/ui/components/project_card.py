
from __future__ import annotations

import customtkinter as ctk
from typing import Callable, Optional

from src.config.models import ProjectMode, ProjectStatus
from src.core.project_manager import ProjectManager
from src.ui.theme import Theme

class ProjectCard(ctk.CTkFrame):

    def __init__(
        self,
        master,
        manager: ProjectManager,
        on_mode_change: Callable[[str, ProjectMode], None],
        on_sync_now: Callable[[str], None],
        on_delete: Callable[[str], None],
        on_view_history: Callable[[ProjectManager], None],
        on_debounce_change: Optional[Callable[[str, int], None]] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            bg_color=Theme.BG_MAIN,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER,
            **kwargs,
        )
        self.manager = manager
        self.on_mode_change = on_mode_change
        self.on_sync_now = on_sync_now
        self.on_delete = on_delete
        self.on_view_history = on_view_history
        self.on_debounce_change = on_debounce_change

        self._build_ui()

    def _build_ui(self) -> None:
        cfg = self.manager.config

        header_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=0)
        header_frame.pack(fill="x", padx=18, pady=(15, 8))

        name_label = ctk.CTkLabel(
            header_frame,
            text=cfg.name,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        name_label.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            header_frame,
            text=f"● {self.manager.status.value}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=self._get_status_color(self.manager.status),
        )
        self.status_badge.pack(side="right")

        grid_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=0)
        grid_frame.pack(fill="x", padx=18, pady=5)
        grid_frame.columnconfigure(1, weight=1)

        self._add_field(grid_frame, 0, "Path:", cfg.path, is_path=True)
        self._add_field(grid_frame, 1, "Branch:", cfg.branch or "main")
        remote_display = cfg.remote if cfg.remote else "Sin remote configurado"
        self._add_field(grid_frame, 2, "Remote:", remote_display)
        commit_display = cfg.last_commit_message or "Sin commits registrados"
        if cfg.last_commit_hash:
            commit_display = f"[{cfg.last_commit_hash}] {commit_display}"
        self.last_commit_lbl = self._add_field(grid_frame, 3, "Último commit:", commit_display)
        sync_display = cfg.last_sync_time or "Nunca"
        self.last_sync_lbl = self._add_field(grid_frame, 4, "Última sincronización:", sync_display)

        action_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=0)
        action_frame.pack(fill="x", padx=18, pady=(12, 16))

        mode_label = ctk.CTkLabel(
            action_frame,
            text="Modo:",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_SECONDARY,
        )
        mode_label.pack(side="left", padx=(0, 6))

        self.mode_selector = ctk.CTkSegmentedButton(
            action_frame,
            values=["AUTO", "COMMIT_ONLY", "PAUSED"],
            command=self._on_mode_selected,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            selected_color=Theme.PRIMARY,
            selected_hover_color=Theme.PRIMARY_HOVER,
            unselected_color=Theme.BG_INPUT,
            unselected_hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            bg_color=Theme.BG_CARD,
            corner_radius=6,
            border_width=0,
            height=28,
        )
        self.mode_selector.set(cfg.mode.value)
        self.mode_selector.pack(side="left", padx=5)

        wait_label = ctk.CTkLabel(
            action_frame,
            text="Espera:",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_SECONDARY,
        )
        wait_label.pack(side="left", padx=(12, 6))

        self._debounce_options = {
            "1 min": 60,
            "2 min": 120,
            "5 min": 300,
            "10 min": 600,
            "30 min": 1800,
            "1 hora": 3600,
        }
        current_debounce_label = "5 min"
        for label, val in self._debounce_options.items():
            if val == cfg.debounce_seconds:
                current_debounce_label = label
                break

        self.debounce_menu = ctk.CTkOptionMenu(
            action_frame,
            values=list(self._debounce_options.keys()),
            command=self._on_debounce_selected,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_CARD_HOVER,
            button_hover_color=Theme.PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.PRIMARY,
            dropdown_text_color=Theme.TEXT_PRIMARY,
            width=85,
            height=28,
            corner_radius=6,
        )
        self.debounce_menu.set(current_debounce_label)
        self.debounce_menu.pack(side="left", padx=5)

        del_btn = ctk.CTkButton(
            action_frame,
            text="Eliminar",
            fg_color=Theme.BTN_SECONDARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.ERROR,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            width=65,
            height=28,
            corner_radius=6,
            border_width=0,
            command=lambda: self.on_delete(cfg.path),
        )
        del_btn.pack(side="right", padx=(5, 0))

        history_btn = ctk.CTkButton(
            action_frame,
            text="Historial",
            fg_color=Theme.BTN_SECONDARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.BTN_SECONDARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            width=70,
            height=28,
            corner_radius=6,
            border_width=0,
            command=lambda: self.on_view_history(self.manager),
        )
        history_btn.pack(side="right", padx=5)

        sync_btn = ctk.CTkButton(
            action_frame,
            text="⚡ Subir ahora",
            fg_color=Theme.PRIMARY,
            bg_color=Theme.BG_CARD,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            width=100,
            height=28,
            corner_radius=6,
            border_width=0,
            command=lambda: self.on_sync_now(cfg.path),
        )
        sync_btn.pack(side="right", padx=5)

    def _add_field(self, parent, row: int, label: str, value: str, is_path: bool = False) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_MUTED,
            anchor="w",
            width=140,
        )
        lbl.grid(row=row, column=0, sticky="w", pady=2)

        val = ctk.CTkLabel(
            parent,
            text=value,
            font=ctk.CTkFont(
                family=Theme.FONT_MONO if is_path else Theme.FONT_FAMILY,
                size=11,
            ),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        val.grid(row=row, column=1, sticky="w", pady=2)
        return val

    def _on_mode_selected(self, mode_str: str) -> None:
        try:
            mode = ProjectMode(mode_str)
            self.on_mode_change(self.manager.config.path, mode)
        except ValueError:
            pass

    def _on_debounce_selected(self, choice: str) -> None:
        secs = self._debounce_options.get(choice, 300)
        if self.on_debounce_change:
            self.on_debounce_change(self.manager.config.path, secs)

    def refresh(self) -> None:
        cfg = self.manager.config
        self.status_badge.configure(
            text=f"● {self.manager.status.value}",
            text_color=self._get_status_color(self.manager.status),
        )
        commit_display = cfg.last_commit_message or "Sin commits registrados"
        if cfg.last_commit_hash:
            commit_display = f"[{cfg.last_commit_hash}] {commit_display}"
        self.last_commit_lbl.configure(text=commit_display)
        self.last_sync_lbl.configure(text=cfg.last_sync_time or "Nunca")

    def _get_status_color(self, status: ProjectStatus) -> str:
        if status == ProjectStatus.WATCHING:
            return Theme.SUCCESS
        if status == ProjectStatus.DEBOUNCING:
            return Theme.WARNING
        if status == ProjectStatus.SYNCING:
            return Theme.PRIMARY
        if status == ProjectStatus.ERROR:
            return Theme.ERROR
        return Theme.TEXT_MUTED
