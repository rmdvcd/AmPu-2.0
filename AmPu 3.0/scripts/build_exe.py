"""Empaqueta AmPu 3.0/Dear PyGui con PyInstaller en el SO anfitrión."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
ASSETS = SRC / "ampu"


def comando(onefile: bool = True) -> list[str]:
    """Construye argumentos reproducibles; la validación de Python vive en main."""
    if not (ASSETS / "docs" / "teoria" / "binomial.md").exists():
        raise RuntimeError("Faltan lecciones offline.")
    piezas = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
              "--name", "AmPu3", "--distpath", str(RAIZ / "dist"),
              "--workpath", str(RAIZ / "build"), "--specpath", str(RAIZ / "build"),
              "--paths", str(SRC), "--hidden-import", "dearpygui.dearpygui",
              "--exclude-module", "pytest", "--exclude-module", "tests",
              "--exclude-module", "tkinter", "--exclude-module", "IPython",
              "--exclude-module", "PySide6", "--exclude-module", "PyQt6",
              "--exclude-module", "PyQt5"]
    for carpeta in ("docs", "ui/recursos"):
        origen = ASSETS / carpeta
        piezas += ["--add-data", f"{origen}{os.pathsep}ampu/{carpeta}"]
    if sys.platform == "darwin":
        piezas += ["--onedir", "--windowed"]
        icono = ASSETS / "ui" / "recursos" / "icono.icns"
    else:
        piezas += ["--onefile" if onefile else "--onedir"]
        icono = ASSETS / "ui" / "recursos" / "icono.ico" if sys.platform == "win32" else None
        if sys.platform == "win32":
            piezas += ["--windowed"]
    if icono is not None:
        if not icono.is_file():
            raise RuntimeError(f"Falta el icono nativo: {icono}")
        piezas += ["--icon", str(icono)]
    piezas += [str(RAIZ / "scripts" / "launcher.py")]
    return piezas


def main():
    parser = argparse.ArgumentParser(description="Construye un ejecutable nativo de AmPu 3.0")
    parser.add_argument("--onedir", action="store_true", help="Carpeta portable en lugar de archivo único")
    parser.add_argument("--gui-self-test", "--ui-self-test", action="store_true",
                        help="Ejecuta la autoprueba Dear PyGui del artefacto, sin viewport")
    args = parser.parse_args()
    if sys.version_info < (3, 12):
        raise RuntimeError("El empaquetado requiere Python 3.12 o posterior.")
    invocacion = comando(onefile=not args.onedir)
    print("Empaquetando en", sys.platform, "· Python", sys.version.split()[0], flush=True)
    subprocess.run(invocacion, cwd=RAIZ, check=True)
    dist = RAIZ / "dist"
    nombre = "AmPu3.exe" if sys.platform == "win32" else "AmPu3"
    if sys.platform == "darwin":
        resultado = dist / "AmPu3.app"
        ejecutable = resultado / "Contents" / "MacOS" / nombre
    elif args.onedir:
        resultado = dist / "AmPu3"
        ejecutable = resultado / nombre
    else:
        resultado = ejecutable = dist / nombre
    if not resultado.exists() or not ejecutable.is_file():
        raise RuntimeError(f"PyInstaller terminó sin producir {ejecutable}.")
    print("Artefacto creado:", resultado, flush=True)
    for argumento in ("--version", "--verify-resources"):
        subprocess.run([str(ejecutable), argumento], cwd=RAIZ, check=True, timeout=180)
    print("Versión, lecciones, recursos y exportaciones verificados en el artefacto.", flush=True)
    if args.gui_self_test:
        subprocess.run([str(ejecutable), "--self-test"], cwd=RAIZ, check=True, timeout=180)
        print("Dear PyGui, módulos, teoría y asistente verificados.", flush=True)


if __name__ == "__main__":
    main()
