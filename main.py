
import argparse
import os
import sys
from pathlib import Path

if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config.manager import ConfigManager
from src.core.engine import Engine
from src.ui.app import MainApplication
from src.utils.logger import log_event, setup_logger

def main():
    parser = argparse.ArgumentParser(description="GH-BOT-REPOS — Windows Repository Sync Bot")
    parser.add_argument("--tray", action="store_true", help="Start minimized to the system tray")
    args = parser.parse_args()

    log_dir = BASE_DIR / "logs"
    setup_logger(log_dir)

    log_event("SYSTEM", "Starting GH-BOT-REPOS application...")

    config_mgr = ConfigManager()

    engine = Engine(config_mgr)

    app = MainApplication(engine, config_mgr)

    if args.tray:
        app.withdraw()
        log_event("SYSTEM", "Application started minimized in System Tray")

    app.mainloop()

if __name__ == "__main__":
    main()
