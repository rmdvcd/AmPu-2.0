"""Empaqueta AmPu 3.0 con PyInstaller en el SO en que se ejecuta.

Windows -> dist/AmPu3.exe; Linux -> dist/AmPu3; macOS -> dist/AmPu3.app.
El recurso QtWebEngineProcess debe ir incluido por los hooks de PyInstaller.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
ASSETS = SRC / "ampu"


def comando(onefile: bool = True) -> list[str]:
    """Construye argumentos sin rutas absolutas escritas en archivos/versiones."""
    if sys.version_info < (3, 12):
        raise RuntimeError("El empaquetado requiere Python 3.12 o posterior.")
    if not (ASSETS / "docs" / "render" / "katex.min.js").exists():
        raise RuntimeError("Faltan recursos KaTeX offline.")
    piezas = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
              "--name", "AmPu3", "--distpath", str(RAIZ / "dist"),
              "--workpath", str(RAIZ / "build"), "--specpath", str(RAIZ / "build"),
              "--paths", str(SRC), "--hidden-import", "PySide6.QtWebEngineWidgets",
              "--hidden-import", "PySide6.QtWebEngineCore",
              "--exclude-module", "pytest", "--exclude-module", "tests",
              "--exclude-module", "tkinter", "--exclude-module", "IPython"]
    for carpeta in ("docs", "ui/estilos", "ui/recursos"):
        origen = ASSETS / carpeta
        # PyInstaller utiliza os.pathsep como separador en --add-data.
        piezas += ["--add-data", f"{origen}{os.pathsep}ampu/{carpeta}"]
    if sys.platform == "darwin":
        # En macOS un .app en directorio permite a QtWebEngine lanzar su helper.
        piezas += ["--onedir", "--windowed"]
    else:
        piezas += ["--onefile" if onefile else "--onedir"]
        if sys.platform == "win32":
            piezas += ["--windowed"]
            icono = ASSETS / "ui" / "recursos" / "icono.ico"
            if icono.exists():
                piezas += ["--icon", str(icono)]
    piezas += [str(RAIZ / "scripts" / "launcher.py")]
    return piezas


def main():
    """Invoca PyInstaller y comprueba la existencia del artefacto resultante."""
    parser = argparse.ArgumentParser(description="Construye un ejecutable nativo de AmPu 3.0")
    parser.add_argument("--onedir", action="store_true", help="Carpeta portable en lugar de archivo único (Linux/Windows)")
    args = parser.parse_args()
    invocacion = comando(onefile=not args.onedir)
    print("Empaquetando en", sys.platform, "· Python", sys.version.split()[0], flush=True)
    subprocess.run(invocacion, cwd=RAIZ, check=True)
    resultado = RAIZ / "dist" / ("AmPu3.exe" if sys.platform == "win32" else "AmPu3.app" if sys.platform == "darwin" else "AmPu3")
    if not resultado.exists():
        raise RuntimeError(f"PyInstaller terminó sin producir {resultado}.")
    print("Artefacto creado:", resultado)


if __name__ == "__main__":
    main()
