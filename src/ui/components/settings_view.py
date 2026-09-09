"""Settings view for GitHub authentication, Windows startup, and preferences."""

from __future__ import annotations

import customtkinter as ctk
from typing import Callable

from src.core.startup import WindowsStartup
from src.git.credentials import GitHubCredentials
from src.ui.theme import Theme
from src.utils.logger import log_event


class SettingsView(ctk.CTkScrollableFrame):
    """Configuration and credentials management interface."""

    def __init__(
        self,
        master,
        on_auth_changed: Callable[[], None],
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_MAIN,
            corner_radius=0,
            **kwargs,
        )
        self.on_auth_changed = on_auth_changed
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Configuración General",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title.pack(anchor="w", padx=20, pady=(20, 5))

        desc = ctk.CTkLabel(
            self,
            text="Gestiona credenciales seguras de GitHub y la integración nativa con Windows.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED,
        )
        desc.pack(anchor="w", padx=20, pady=(0, 20))

        # 1. GitHub Authentication Card
        auth_card = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER,
        )
        auth_card.pack(fill="x", padx=20, pady=10)

        auth_title = ctk.CTkLabel(
            auth_card,
            text="Autenticación con GitHub (Windows Credential Manager)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        auth_title.pack(anchor="w", padx=16, pady=(16, 5))

        auth_desc = ctk.CTkLabel(
            auth_card,
            text="Los tokens se encriptan con las APIs del sistema operativo. Nunca se guardan en archivos ni logs.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        auth_desc.pack(anchor="w", padx=16, pady=(0, 15))

        # Token input row
        self.token_frame = ctk.CTkFrame(auth_card, fg_color="transparent")
        self.token_frame.pack(fill="x", padx=16, pady=5)

        self.token_entry = ctk.CTkEntry(
            self.token_frame,
            placeholder_text="Ingresa tu Personal Access Token (ghp_...)",
            show="•",
            fg_color=Theme.BG_MAIN,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            height=34,
        )
        self.token_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.connect_btn = ctk.CTkButton(
            self.token_frame,
            text="Conectar GitHub",
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            height=34,
            command=self._on_connect_github,
        )
        self.connect_btn.pack(side="right")

        # Disconnect button & Account details row
        self.account_frame = ctk.CTkFrame(auth_card, fg_color="transparent")

        self.account_lbl = ctk.CTkLabel(
            self.account_frame,
            text="",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=Theme.SUCCESS,
        )
        self.account_lbl.pack(side="left")

        self.disconnect_btn = ctk.CTkButton(
            self.account_frame,
            text="Desconectar GitHub",
            fg_color="transparent",
            hover_color=Theme.BG_MAIN,
            text_color=Theme.ERROR,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            height=32,
            command=self._on_disconnect_github,
        )
        self.disconnect_btn.pack(side="right")

        self.auth_feedback_lbl = ctk.CTkLabel(
            auth_card,
            text="",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        self.auth_feedback_lbl.pack(anchor="w", padx=16, pady=(5, 14))

        # 2. Windows System Integration Card
        sys_card = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER,
        )
        sys_card.pack(fill="x", padx=20, pady=15)

        sys_title = ctk.CTkLabel(
            sys_card,
            text="Integración con Windows",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        sys_title.pack(anchor="w", padx=16, pady=(16, 12))

        # Startup Switch
        self.startup_switch = ctk.CTkSwitch(
            sys_card,
            text="Iniciar GH-BOT-REPOS automáticamente con Windows (Usuario actual)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.PRIMARY,
            command=self._on_startup_toggle,
        )
        self.startup_switch.pack(anchor="w", padx=16, pady=8)

        # Minimize to Tray description
        tray_note = ctk.CTkLabel(
            sys_card,
            text="• Al presionar la 'X' en la ventana, GH-BOT-REPOS se oculta al System Tray y sigue sincronizando.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED,
        )
        tray_note.pack(anchor="w", padx=16, pady=(10, 16))

    def refresh(self) -> None:
        """Inspect current credentials and startup state."""
        # Check GitHub token
        token = GitHubCredentials.get_token()
        if token:
            valid, user_info, err = GitHubCredentials.validate_token(token)
            if valid:
                username = user_info.get("login", "Usuario")
                self.account_lbl.configure(text=f"● Conectado como @{username}")
                self.token_frame.pack_forget()
                self.account_frame.pack(fill="x", padx=16, pady=10)
                self.auth_feedback_lbl.configure(
                    text="Token válido y verificado en la API de GitHub.",
                    text_color=Theme.SUCCESS,
                )
            else:
                self.token_frame.pack(fill="x", padx=16, pady=5)
                self.account_frame.pack_forget()
                self.auth_feedback_lbl.configure(
                    text=f"Token existente no válido: {err}",
                    text_color=Theme.WARNING,
                )
        else:
            self.token_frame.pack(fill="x", padx=16, pady=5)
            self.account_frame.pack_forget()
            self.auth_feedback_lbl.configure(
                text="Ningún token configurado. Añade un Personal Access Token para sincronizar repositorios privados.",
                text_color=Theme.TEXT_MUTED,
            )

        # Check Windows Startup
        if WindowsStartup.is_startup_enabled():
            self.startup_switch.select()
        else:
            self.startup_switch.deselect()

    def _on_connect_github(self) -> None:
        token = self.token_entry.get().strip()
        if not token:
            self.auth_feedback_lbl.configure(
                text="Por favor escribe o pega un Personal Access Token.",
                text_color=Theme.ERROR,
            )
            return

        self.auth_feedback_lbl.configure(text="Validando token con GitHub...", text_color=Theme.PRIMARY)
        valid, user_info, err = GitHubCredentials.validate_token(token)
        if valid:
            username = user_info.get("login", "")
            GitHubCredentials.store_token(token, username)
            self.token_entry.delete(0, "end")
            self.refresh()
            self.on_auth_changed()
            log_event("SYSTEM", f"GitHub account connected: @{username}")
        else:
            self.auth_feedback_lbl.configure(text=f"Error al validar: {err}", text_color=Theme.ERROR)

    def _on_disconnect_github(self) -> None:
        GitHubCredentials.delete_token()
        self.refresh()
        self.on_auth_changed()
        log_event("SYSTEM", "GitHub account disconnected")

    def _on_startup_toggle(self) -> None:
        if self.startup_switch.get():
            WindowsStartup.enable_startup()
        else:
            WindowsStartup.disable_startup()
