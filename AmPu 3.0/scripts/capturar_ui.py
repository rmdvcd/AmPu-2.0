"""Capturas reales de QWidget final con resultados (requiere entorno gráfico Qt).

En CI headless con bibliotecas gráficas del SO instaladas:
QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 python scripts/capturar_ui.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("QtAgg")
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ampu.ui.main_window import VentanaPrincipal

DESTINO = Path(__file__).resolve().parents[1] / "docs" / "capturas"


def main():
    """Espera trabajos asíncronos y guarda PNG genuinos, sin datos simulados de UI."""
    DESTINO.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv[:1])
    ventana = VentanaPrincipal()
    ventana.resize(1440, 900)
    ventana.show()
    pasos = [("distribuciones", "01_distribuciones_claro.png", "claro"),
             ("muestreo", "02_muestreo_claro.png", "claro"),
             ("inferencia", "03_inferencia_claro.png", "claro"),
             ("distribuciones", "04_distribuciones_oscuro.png", "oscuro")]
    intentos = 0

    def siguiente():
        nonlocal intentos
        if not pasos:
            print("Capturas guardadas en", DESTINO)
            app.quit()
            return
        clave, archivo, tema = pasos[0]
        ventana.aplicar_tema(tema)
        ventana.cambiar(clave)
        vista = ventana.vista
        if clave == "inferencia" and vista.ultimo is None and not vista._ocupado:
            for indice in range(vista.tipo.count()):
                if vista.tipo.itemData(indice)[0] == "t_dos":
                    vista.tipo.setCurrentIndex(indice)
                    break
            vista.calcular()
        if vista._ocupado or vista.ultimo is None:
            intentos += 1
            if intentos > 90:
                raise RuntimeError(f"No terminó el cálculo para {clave}.")
            QTimer.singleShot(150, siguiente)
            return
        intentos = 0
        # Un turno más para que Qt pinte el lienzo tras recibir la señal.
        pasos.pop(0)
        def capturar():
            destino = DESTINO / archivo
            if not ventana.grab().save(str(destino), "PNG"):
                raise RuntimeError(f"No se pudo guardar {destino}.")
            print(destino.name, destino.stat().st_size, "bytes")
            QTimer.singleShot(150, siguiente)
        QTimer.singleShot(220, capturar)

    QTimer.singleShot(200, siguiente)
    QTimer.singleShot(30_000, app.quit)  # evita quedar bloqueado en un plugin Qt defectuoso
    codigo = app.exec()
    if pasos:
        raise TimeoutError(f"No se pudieron obtener {len(pasos)} capturas.")
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
