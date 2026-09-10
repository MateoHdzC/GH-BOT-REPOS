
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import threading
from typing import Optional

from src.utils.logger import log_event

_ACTIVE_TRAY_ICON = None
_AUMID_REGISTERED = False

def register_tray_icon(icon) -> None:
    global _ACTIVE_TRAY_ICON
    _ACTIVE_TRAY_ICON = icon

def ensure_windows_registration() -> None:
    global _AUMID_REGISTERED
    if _AUMID_REGISTERED or os.name != "nt":
        return
    _AUMID_REGISTERED = True
    try:
        import winreg
        base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent.parent
        ico_path = base_dir / "assets" / "icon.ico"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\AppUserModelId\GH-BOT-REPOS")
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "GH-BOT-REPOS")
        if ico_path.exists():
            winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, str(ico_path))
        winreg.CloseKey(key)
    except Exception:
        pass

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
            ensure_windows_registration()

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
                log_event("WARNING", f"winotify failed with AUMID, trying powershell: {ex}")

            try:
                from winotify import Notification, audio
                toast = Notification(
                    app_id="{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe",
                    title=full_title,
                    msg=message,
                )
                sound = audio.Default if level == "success" else (audio.Hand if level in ("warning", "danger") else audio.Mail)
                toast.set_audio(sound, loop=False)
                toast.show()
                return
            except Exception as ex:
                log_event("ERROR", f"Failed to deliver Windows notification: {ex}")
