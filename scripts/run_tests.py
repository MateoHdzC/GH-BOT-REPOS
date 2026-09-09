"""Test runner script for GH-BOT-REPOS."""

import sys
import subprocess
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent.parent
    print("=" * 60)
    print("GH-BOT-REPOS — EJECUCIÓN DE SUITE DE PRUEBAS")
    print("=" * 60)

    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    res = subprocess.run(cmd, cwd=str(root_dir))

    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("RESULTADO: OK — Todos los tests pasaron exitosamente.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("RESULTADO: FALLO — Se detectaron errores en las pruebas.")
        print("=" * 60)
        sys.exit(res.returncode)


if __name__ == "__main__":
    main()
