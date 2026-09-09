
from __future__ import annotations

import customtkinter as ctk
from typing import Callable
from src.ui.theme import Theme

class Sidebar(ctk.CTkFrame):

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        on_exit: Callable[[], None],
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_SIDEBAR,
            corner_radius=0,
            width=220,
            **kwargs,
        )
        self.on_navigate = on_navigate
        self.on_exit = on_exit

        self._current_view = "todos"
        self._nav_buttons = {}

        self._build_ui()

    def _build_ui(self) -> None:
        title_frame = ctk.CTkFrame(self, fg_color=Theme.BG_SIDEBAR, corner_radius=0)
        title_frame.pack(fill="x", padx=20, pady=(25, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="GH-BOT-REPOS",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        sub_label = ctk.CTkLabel(
            title_frame,
            text="Windows Edition",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        sub_label.pack(anchor="w")

        sep1 = ctk.CTkFrame(self, fg_color=Theme.BORDER, height=1, corner_radius=0, border_width=0)
        sep1.pack(fill="x", padx=15, pady=5)

        nav_container = ctk.CTkFrame(self, fg_color=Theme.BG_SIDEBAR, corner_radius=0)
        nav_container.pack(fill="x", padx=10, pady=10)

        self._create_nav_btn(nav_container, "todos", "📁 Todos", count="0")
        self._create_nav_btn(nav_container, "activos", "🟢 Activos", count="0")
        self._create_nav_btn(nav_container, "pausados", "⏸ Pausados", count="0")
        self._create_nav_btn(nav_container, "dashboard", "📊 Dashboard")
        self._create_nav_btn(nav_container, "logs", "📝 Actividad / Logs")
        self._create_nav_btn(nav_container, "configuracion", "⚙ Configuración")

        bottom_frame = ctk.CTkFrame(self, fg_color=Theme.BG_SIDEBAR, corner_radius=0)
        bottom_frame.pack(side="bottom", fill="x", padx=15, pady=20)

        sep2 = ctk.CTkFrame(bottom_frame, fg_color=Theme.BORDER, height=1, corner_radius=0, border_width=0)
        sep2.pack(fill="x", pady=(0, 15))

        self.github_status_lbl = ctk.CTkLabel(
            bottom_frame,
            text="GitHub: ○ Desconectado",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        self.github_status_lbl.pack(fill="x", pady=2)

        self.engine_status_lbl = ctk.CTkLabel(
            bottom_frame,
            text="Engine: ● Running",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.SUCCESS,
            anchor="w",
        )
        self.engine_status_lbl.pack(fill="x", pady=2)

        exit_btn = ctk.CTkButton(
            bottom_frame,
            text="Salir",
            fg_color=Theme.BTN_SECONDARY,
            bg_color=Theme.BG_SIDEBAR,
            hover_color=Theme.ERROR,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            command=self.on_exit,
            height=32,
            corner_radius=6,
            border_width=0,
        )
        exit_btn.pack(fill="x", pady=(15, 0))

    def _create_nav_btn(self, parent, view_key: str, label: str, count: str = "") -> None:
        btn_frame = ctk.CTkFrame(parent, fg_color=Theme.BG_SIDEBAR, corner_radius=0, height=38)
        btn_frame.pack(fill="x", pady=2)

        is_selected = (view_key == self._current_view)
        btn = ctk.CTkButton(
            btn_frame,
            text=label,
            fg_color=Theme.PRIMARY if is_selected else Theme.BG_SIDEBAR,
            bg_color=Theme.BG_SIDEBAR,
            text_color=Theme.TEXT_PRIMARY if is_selected else Theme.TEXT_SECONDARY,
            hover_color=Theme.PRIMARY_HOVER if is_selected else Theme.BG_CARD_HOVER,
            anchor="w",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13),
            command=lambda: self._select_view(view_key),
            height=36,
            corner_radius=6,
            border_width=0,
        )
        btn.pack(side="left", fill="x", expand=True)

        badge = None
        if count != "":
            badge = ctk.CTkLabel(
                btn_frame,
                text=count,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
                text_color=Theme.TEXT_MUTED,
                width=24,
            )
            badge.pack(side="right", padx=5)

        self._nav_buttons[view_key] = {"btn": btn, "badge": badge}

    def _select_view(self, view_key: str) -> None:
        self._current_view = view_key
        for k, v in self._nav_buttons.items():
            if k == view_key:
                v["btn"].configure(
                    fg_color=Theme.PRIMARY,
                    text_color=Theme.TEXT_PRIMARY,
                    hover_color=Theme.PRIMARY_HOVER,
                )
            else:
                v["btn"].configure(
                    fg_color=Theme.BG_SIDEBAR,
                    text_color=Theme.TEXT_SECONDARY,
                    hover_color=Theme.BG_CARD_HOVER,
                )
        self.on_navigate(view_key)

    def update_counts(self, total: int, active: int, paused: int) -> None:
        if "todos" in self._nav_buttons and self._nav_buttons["todos"]["badge"]:
            self._nav_buttons["todos"]["badge"].configure(text=str(total))
        if "activos" in self._nav_buttons and self._nav_buttons["activos"]["badge"]:
            self._nav_buttons["activos"]["badge"].configure(text=str(active))
        if "pausados" in self._nav_buttons and self._nav_buttons["pausados"]["badge"]:
            self._nav_buttons["pausados"]["badge"].configure(text=str(paused))

    def update_system_status(self, github_connected: bool, github_user: str = "", engine_running: bool = True) -> None:
        if github_connected:
            user_text = f" ({github_user})" if github_user else ""
            self.github_status_lbl.configure(text=f"GitHub: ● Conectado{user_text}", text_color=Theme.SUCCESS)
        else:
            self.github_status_lbl.configure(text="GitHub: ○ Desconectado", text_color=Theme.TEXT_MUTED)

        if engine_running:
            self.engine_status_lbl.configure(text="Engine: ● Running", text_color=Theme.SUCCESS)
        else:
            self.engine_status_lbl.configure(text="Engine: ○ Stopped", text_color=Theme.WARNING)
