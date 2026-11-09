"""Preferencias visuales del sistema sin dependencias específicas de plataforma."""

from __future__ import annotations

import os
import subprocess
import sys


def factor_fuente_sistema(puntos: float, macos: bool = False) -> float:
    """Relación prudente entre la fuente Qt actual y el tamaño normal del SO."""
    referencia = 13.0 if macos else 9.0
    if not 0 < puntos < 100:
        return 1.0
    return max(.9, min(2.0, puntos / referencia))


def apariencia_sistema() -> str:
    """Devuelve ``claro`` u ``oscuro`` según el SO; ante duda, claro."""
    if sys.platform == "darwin":
        try:
            salida = subprocess.check_output(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                stderr=subprocess.DEVNULL, timeout=1)
            return "oscuro" if b"dark" in salida.lower() else "claro"
        except (OSError, subprocess.SubprocessError):
            return "claro"
    if os.name == "nt":
        try:
            import winreg
            clave = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            valor, _tipo = winreg.QueryValueEx(clave, "AppsUseLightTheme")
            return "claro" if valor else "oscuro"
        except OSError:
            return "claro"
    try:
        salida = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            stderr=subprocess.DEVNULL, timeout=1)
        if b"dark" in salida.lower():
            return "oscuro"
    except (OSError, subprocess.SubprocessError):
        pass
    tema = (os.environ.get("GTK_THEME", "")
            + os.environ.get("GTK_APPLICATION_PREFER_DARK_THEME", "")
            + os.environ.get("QT_STYLE_OVERRIDE", "")).lower()
    if "dark" in tema or os.environ.get("GTK_APPLICATION_PREFER_DARK_THEME") == "1":
        return "oscuro"
    return "claro"
