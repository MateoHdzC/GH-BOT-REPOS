
import os
import shutil
import subprocess
import sys
from pathlib import Path

def build():
    root_dir = Path(__file__).resolve().parent.parent
    assets_dir = root_dir / "assets"
    icon_path = assets_dir / "icon.ico"

    print("=" * 60)
    print("GH-BOT-REPOS — GENERADOR DE EJECUTABLE WINDOWS")
    print("=" * 60)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--icon={icon_path}",
        f"--name=GH-BOT-REPOS",
        f"--add-data={assets_dir};assets",
        "--hidden-import=customtkinter",
        "--hidden-import=pystray",
        "--hidden-import=keyring",
        "--hidden-import=keyring.backends.Windows",
        "--hidden-import=PIL",
        "--hidden-import=watchdog",
        "--hidden-import=watchdog.observers",
        "--hidden-import=watchdog.observers.read_directory_changes",
        "main.py",
    ]

    print(f"Ejecutando: {' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=str(root_dir))

    if res.returncode == 0:
        exe_path = root_dir / "dist" / "GH-BOT-REPOS" / "GH-BOT-REPOS.exe"
        print("\n" + "=" * 60)
        print("COMPILACIÓN EXITOSA")
        print(f"Ejecutable generado en: {exe_path}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(f"ERROR EN LA COMPILACIÓN: Código de salida {res.returncode}")
        print("=" * 60)
        sys.exit(res.returncode)

if __name__ == "__main__":
    build()
