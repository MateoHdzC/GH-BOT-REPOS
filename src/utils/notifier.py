"""Windows native notification system with Tray and PowerShell WinRT fallbacks."""

from __future__ import annotations

import os
import subprocess
import threading
from typing import Optional

from src.utils.logger import log_event

_ACTIVE_TRAY_ICON = None


def register_tray_icon(icon) -> None:
    """Register active pystray icon for toast dispatching."""
    global _ACTIVE_TRAY_ICON
    _ACTIVE_TRAY_ICON = icon


class WindowsNotifier:
    """Dispatches system notifications on Windows 10 and 11."""

    @classmethod
    def notify(cls, title: str, message: str, level: str = "info") -> None:
        """Send notification asynchronously."""
        threading.Thread(
            target=cls._dispatch,
            args=(title, message, level),
            daemon=True,
        ).start()

    @classmethod
    def _dispatch(cls, title: str, message: str, level: str) -> None:
        prefix = "✓ " if level == "success" else ("⚠ " if level == "warning" else ("🚨 " if level == "danger" else ""))
        full_title = f"{prefix}GH-BOT-REPOS — {title}"

        # 1. Try active pystray icon notification
        global _ACTIVE_TRAY_ICON
        if _ACTIVE_TRAY_ICON is not None:
            try:
                _ACTIVE_TRAY_ICON.notify(message, full_title)
                return
            except Exception:
                pass

        # 2. Windows PowerShell Toast fallback
        if os.name == "nt":
            try:
                # Escape double quotes
                esc_title = full_title.replace('"', '`"')
                esc_msg = message.replace('"', '`"')
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $textNodes = $template.GetElementsByTagName('text')
                $textNodes.Item(0).AppendChild($template.CreateTextNode("{esc_title}")) > $null
                $textNodes.Item(1).AppendChild($template.CreateTextNode("{esc_msg}")) > $null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("GH-BOT-REPOS").Show($toast)
                """
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=5,
                )
            except Exception as ex:
                log_event("ERROR", f"Failed to deliver Windows notification: {ex}")
