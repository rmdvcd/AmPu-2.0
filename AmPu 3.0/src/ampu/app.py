"""Punto de entrada multiplataforma de la aplicación Qt."""

import argparse
import json
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
    parser.add_argument("--verify-resources", action="store_true",
                        help="Comprueba recursos y exportaciones, sin crear ventanas")
    parser.add_argument("--self-test", action="store_true",
                        help="Comprueba QtWebEngine, KaTeX y los temas en un escritorio real")
    parser.add_argument("--capture-theory", metavar="PNG",
                        help="Captura genuina de la teoría al ejecutar --self-test")
    opciones = parser.parse_args(argv)
    if opciones.capture_theory and not opciones.self_test:
        parser.error("--capture-theory requiere --self-test")
    if opciones.verify_resources or opciones.self_test:
        from ampu.diagnostico import verificar_recursos
        try:
            reporte = verificar_recursos()
        except Exception as exc:
            print(f"Autoprueba fallida (recursos): {exc}", file=sys.stderr)
            return 1
        if opciones.verify_resources:
            print(json.dumps(reporte, ensure_ascii=False))
            return 0
    try:
        import matplotlib
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication
        matplotlib.use("QtAgg")
    except ImportError as exc:
        print(f"Faltan bibliotecas gráficas nativas de Qt: {exc}. "
              "Consulta las dependencias Linux del README.", file=sys.stderr)
        return 1
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("AmPu 3.0")
    app.setOrganizationName("AmPu")
    from ampu.ui.main_window import ICONO, VentanaPrincipal
    app.setWindowIcon(QIcon(str(ICONO)))
    configurar_logging()
    if opciones.self_test:
        from ampu.diagnostico import verificar_webengine
        try:
            reporte.update(verificar_webengine(app, opciones.capture_theory))
        except Exception as exc:
            logging.getLogger("ampu").exception("Falló la autoprueba del escritorio")
            print(f"Autoprueba fallida (QtWebEngine): {exc}", file=sys.stderr)
            return 1
        print(json.dumps(reporte, ensure_ascii=False))
        return 0
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec()
