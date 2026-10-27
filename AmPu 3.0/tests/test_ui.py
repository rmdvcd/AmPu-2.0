"""Prueba mínima de integración Qt (omite si faltan bibliotecas gráficas del SO)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
QtWidgets = pytest.importorskip("PySide6.QtWidgets", reason="Faltan bibliotecas compartidas gráficas del entorno de pruebas", exc_type=ImportError)
from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402


def test_ventana_y_registro_dinamico():
    from ampu.core.distribuciones import DISTRIBUCIONES
    from ampu.ui.main_window import VentanaPrincipal

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    ventana = VentanaPrincipal()
    ventana.show()
    vista = ventana.vistas["distribuciones"]
    assert vista.selector.count() == len(DISTRIBUCIONES)
    pos = vista.selector.findData("erlang")
    vista.selector.setCurrentIndex(pos)
    assert set(vista.formulario.controles) == {"k", "tasa"}
    ventana.aplicar_tema("oscuro")
    assert ventana.tema_actual == "oscuro"
    ventana.cambiar("probabilidad")
    assert ventana.actual == "probabilidad"
    evento = QEventLoop()
    QTimer.singleShot(1200, evento.quit)
    evento.exec()
    ventana.close()
    app.processEvents()


def test_vistas_con_calculos_y_tablas_exportables():
    """Ejercita las seis pantallas y sus hilos sin usar fórmulas en Qt."""
    from ampu.ui.main_window import VentanaPrincipal

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    ventana = VentanaPrincipal()
    ventana.show()
    ventana.vistas["probabilidad"].calcular()
    ventana.vistas["inferencia"].calcular()
    ventana.vistas["descriptiva"].calcular()
    for clave in ("muestreo", "descriptiva", "probabilidad", "inferencia", "simulacion"):
        ventana.cambiar(clave)
        assert ventana.actual == clave
    evento = QEventLoop()
    pasos = 0

    def comprobar():
        nonlocal pasos
        pasos += 1
        if all(v.ultimo is not None and not v._ocupado for v in ventana.vistas.values()) or pasos > 180:
            evento.quit()
        else:
            QTimer.singleShot(50, comprobar)

    QTimer.singleShot(50, comprobar)
    evento.exec()
    assert pasos <= 180
    for clave, vista in ventana.vistas.items():
        assert vista.ultimo is not None, clave
        assert vista.tabla.rowCount() > 0, clave
        assert vista.tablas_exportables(), clave
        assert vista.estado(), clave
    ventana.close()
    app.processEvents()
