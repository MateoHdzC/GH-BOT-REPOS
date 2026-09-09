"""Dashboard view displaying live metrics, synchronization statistics, and system health."""

from __future__ import annotations

import customtkinter as ctk
from src.core.engine import Engine
from src.git.credentials import GitHubCredentials
from src.ui.theme import Theme


class DashboardView(ctk.CTkScrollableFrame):
    """Real-time statistical dashboard."""

    def __init__(self, master, engine: Engine, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_MAIN,
            corner_radius=0,
            **kwargs,
        )
        self.engine = engine
        self._stat_cards = {}
        self._build_ui()

    def _build_ui(self) -> None:
        # Title
        title_lbl = ctk.CTkLabel(
            self,
            text="Dashboard de Monitoreo",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w", padx=20, pady=(20, 5))

        desc_lbl = ctk.CTkLabel(
            self,
            text="Métricas en vivo de repositorios, sincronización automática y estado del sistema.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED,
        )
        desc_lbl.pack(anchor="w", padx=20, pady=(0, 20))

        # Metrics Grid (2 rows x 4 cols)
        metrics_grid = ctk.CTkFrame(self, fg_color="transparent")
        metrics_grid.pack(fill="x", padx=20, pady=5)
        for col in range(4):
            metrics_grid.columnconfigure(col, weight=1)

        self._create_stat_card(metrics_grid, 0, 0, "Proyectos Totales", "0", Theme.PRIMARY)
        self._create_stat_card(metrics_grid, 0, 1, "Proyectos Activos", "0", Theme.SUCCESS)
        self._create_stat_card(metrics_grid, 0, 2, "Proyectos Pausados", "0", Theme.WARNING)
        self._create_stat_card(metrics_grid, 0, 3, "Archivos Modificados", "0", Theme.TEXT_PRIMARY)

        self._create_stat_card(metrics_grid, 1, 0, "Commits Creados", "0", Theme.SUCCESS)
        self._create_stat_card(metrics_grid, 1, 1, "Pushes Exitosos", "0", Theme.PRIMARY)
        self._create_stat_card(metrics_grid, 1, 2, "Pushes Fallidos", "0", Theme.ERROR)
        self._create_stat_card(metrics_grid, 1, 3, "Reintentos en Cola", "0", Theme.WARNING)

        # System Details Section
        sys_lbl = ctk.CTkLabel(
            self,
            text="Diagnóstico del Sistema Windows",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        )
        sys_lbl.pack(anchor="w", padx=20, pady=(30, 15))

        sys_box = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=8,
            border_width=0,
        )
        sys_box.pack(fill="x", padx=20, pady=5)

        self._add_system_row(sys_box, "Watcher Engine:", "Activo (watchdog nativo)")
        self._add_system_row(sys_box, "Git Engine:", "Operativo (subprocess seguro)")
        self._add_system_row(sys_box, "Almacenamiento Seguro:", "Windows Credential Manager")
        self._add_system_row(sys_box, "Modo de Ejecución:", "Segundo plano / System Tray activo")

        self.refresh()

    def _create_stat_card(self, parent, row: int, col: int, label: str, init_val: str, accent_color: str) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.BG_CARD,
            corner_radius=8,
            border_width=0,
        )
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        title = ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_SECONDARY,
        )
        title.pack(anchor="w", padx=14, pady=(12, 4))

        val_lbl = ctk.CTkLabel(
            card,
            text=init_val,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=accent_color,
        )
        val_lbl.pack(anchor="w", padx=14, pady=(0, 12))

        self._stat_cards[label] = val_lbl

    def _add_system_row(self, parent, label: str, value: str) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=8)

        lbl = ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=Theme.TEXT_SECONDARY,
            width=180,
            anchor="w",
        )
        lbl.pack(side="left")

        val = ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.SUCCESS,
            anchor="w",
        )
        val.pack(side="left")

    def refresh(self) -> None:
        """Update metrics from engine stats."""
        stats = self.engine.get_dashboard_stats()
        queue_count = len(self.engine.retry_queue.get_all())

        mapping = {
            "Proyectos Totales": str(stats["total_projects"]),
            "Proyectos Activos": str(stats["active_projects"]),
            "Proyectos Pausados": str(stats["paused_projects"]),
            "Archivos Modificados": str(stats["total_files_changed"]),
            "Commits Creados": str(stats["total_commits"]),
            "Pushes Exitosos": str(stats["total_pushes"]),
            "Pushes Fallidos": str(stats["failed_pushes"]),
            "Reintentos en Cola": str(queue_count),
        }

        for k, v in mapping.items():
            if k in self._stat_cards:
                self._stat_cards[k].configure(text=v)
