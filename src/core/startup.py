
from __future__ import annotations

import os
import sys
import winreg
from pathlib import Path

from src.utils.logger import log_event

REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "GH-BOT-REPOS"

class WindowsStartup:

    @staticmethod
    def get_executable_command() -> str:
        if getattr(sys, "frozen", False):
            exe_path = sys.executable
            return f'"{exe_path}" --tray'
        else:
            python_exe = sys.executable
            main_script = Path(__file__).resolve().parent.parent.parent / "main.py"
            return f'"{python_exe}" "{main_script}" --tray'

    @classmethod
    def is_startup_enabled(cls) -> bool:
        if os.name != "nt":
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, APP_REG_NAME)
                return True
        except FileNotFoundError:
            return False
        except Exception as ex:
            log_event("ERROR", f"Error checking startup registry: {ex}")
            return False

    @classmethod
    def enable_startup(cls) -> bool:
        if os.name != "nt":
            return False
        try:
            cmd = cls.get_executable_command()
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)
            log_event("SYSTEM", f"Enabled startup with Windows: {cmd}")
            return True
        except Exception as ex:
            log_event("ERROR", f"Failed to enable startup: {ex}")
            return False

    @classmethod
    def disable_startup(cls) -> bool:
        if os.name != "nt":
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, APP_REG_NAME)
            log_event("SYSTEM", "Disabled startup with Windows")
            return True
        except FileNotFoundError:
            return True
        except Exception as ex:
            log_event("ERROR", f"Failed to disable startup: {ex}")
            return False
