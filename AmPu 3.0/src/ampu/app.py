"""Punto de entrada multiplataforma de la aplicación Qt."""

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ampu import __version__


def configurar_logging() -> Path:
    """Usa carpeta de datos del usuario, nunca el directorio del paquete."""
    from PySide6.QtCore import QStandardPaths

    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    carpeta = Path(base) if base else Path.home() / ".ampu3"
    carpeta.mkdir(parents=True, exist_ok=True)
    registro = carpeta / "ampu.log"
    manejador = RotatingFileHandler(registro, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    manejador.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger("ampu").addHandler(manejador)
    logging.getLogger("ampu").setLevel(logging.INFO)
    return registro


def main(argv: list[str] | None = None) -> int:
    """Inicia QtAgg + QMainWindow; ``--version`` funciona sin pantalla."""
    parser = argparse.ArgumentParser(prog="ampu", description="Laboratorio educativo de probabilidad y estadística")
    parser.add_argument("--version", action="version", version=f"AmPu {__version__}")
    parser.parse_args(argv)
    import matplotlib
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    matplotlib.use("QtAgg")
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("AmPu 3.0")
    app.setOrganizationName("AmPu")
    from ampu.ui.main_window import ICONO, VentanaPrincipal
    app.setWindowIcon(QIcon(str(ICONO)))
    configurar_logging()
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec()
