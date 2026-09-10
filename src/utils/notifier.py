
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import threading
from typing import Optional

from src.utils.logger import log_event

_ACTIVE_TRAY_ICON = None

def register_tray_icon(icon) -> None:
    global _ACTIVE_TRAY_ICON
    _ACTIVE_TRAY_ICON = icon

def ensure_start_menu_shortcut() -> None:
    if os.name != "nt":
        return
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return
    shortcut_path = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "GH-BOT-REPOS.lnk"
    if not shortcut_path.exists():
        try:
            exe_path = Path(sys.executable) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent.parent / "dist" / "GH-BOT-REPOS" / "GH-BOT-REPOS.exe"
            work_dir = exe_path.parent
            ico_path = work_dir / "assets" / "icon.ico"
            ps_cmd = f'$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); $Shortcut.TargetPath = "{exe_path}"; $Shortcut.WorkingDirectory = "{work_dir}"; $Shortcut.IconLocation = "{ico_path}"; $Shortcut.Save()'
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=5,
            )
        except Exception:
            pass

class WindowsNotifier:

    @classmethod
    def notify(cls, title: str, message: str, level: str = "info") -> None:
        threading.Thread(
            target=cls._dispatch,
            args=(title, message, level),
            daemon=True,
        ).start()

    @classmethod
    def _dispatch(cls, title: str, message: str, level: str) -> None:
        prefix = "✓ " if level == "success" else ("⚠ " if level == "warning" else ("🚨 " if level == "danger" else ""))
        full_title = f"{prefix}GH-BOT-REPOS — {title}"

        if os.name == "nt":
            ensure_start_menu_shortcut()

            base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent.parent
            icon_candidate = base_dir / "assets" / "icon.ico"
            icon_path = str(icon_candidate) if icon_candidate.exists() else ""

            try:
                from winotify import Notification, audio
                toast = Notification(
                    app_id="GH-BOT-REPOS",
                    title=full_title,
                    msg=message,
                    icon=icon_path if icon_path else None,
                )
                sound = audio.Default if level == "success" else (audio.Hand if level in ("warning", "danger") else audio.Mail)
                toast.set_audio(sound, loop=False)
                toast.show()
                return
            except Exception as ex:
                log_event("WARNING", f"winotify failed, falling back to powershell toast: {ex}")

            try:
                esc_title = full_title.replace('"', '`"')
                esc_msg = message.replace('"', '`"')
                app_id = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe"
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $textNodes = $template.GetElementsByTagName('text')
                $textNodes.Item(0).AppendChild($template.CreateTextNode("{esc_title}")) > $null
                $textNodes.Item(1).AppendChild($template.CreateTextNode("{esc_msg}")) > $null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{app_id}").Show($toast)
                """
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=5,
                )
            except Exception as ex:
                log_event("ERROR", f"Failed to deliver Windows notification: {ex}")
