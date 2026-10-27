"""Regresiones de precisión, edición y sesiones en Qt sin display (si está disponible)."""

import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError,
                                 reason="Qt requiere bibliotecas gráficas del sistema")
from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def esperar(condicion, milisegundos=12_000):
    """Espera eventos Qt con límite; no bloquea el hilo de la interfaz."""
    ciclo = QEventLoop()
    agotado = False

    def vencido():
        nonlocal agotado
        agotado = True
        ciclo.quit()

    limite = QTimer()
    limite.setSingleShot(True)
    limite.timeout.connect(vencido)
    limite.start(milisegundos)

    def comprobar():
        if condicion():
            ciclo.quit()
        else:
            QTimer.singleShot(20, comprobar)

    QTimer.singleShot(0, comprobar)
    ciclo.exec()
    limite.stop()
    assert not agotado, "El cálculo/restablecimiento de la sesión tardó demasiado"


def test_precision_numerica_y_orden_tras_editar(app):
    from ampu.ui.widgets.tabla import TablaDatos

    tabla = TablaDatos()
    valores = pd.DataFrame({"probabilidad": [0.12345678912345678, 0.9876543219876543],
                            "id": [2**53 + 1, 2**53 + 2]})
    tabla.mostrar(valores)
    assert tabla.datos().equals(valores)
    tabla.item(0, 0).setText("0.999")
    assert tabla.item(0, 0).toolTip() == "0.999"
    tabla.sortItems(0)
    assert tabla.datos().iloc[-1, 0] == 0.999
    assert tabla.datos().iloc[0, 0] == valores.iloc[1, 0]
    tabla.close()


def test_sesion_restaurada_con_ediciones_en_todas_las_vistas(app, tmp_path):
    from ampu.io.sesion import cargar_sesion, guardar_sesion
    from ampu.ui.main_window import VentanaPrincipal

    origen = VentanaPrincipal()
    origen.show()
    origen.vistas["probabilidad"].calcular()
    origen.vistas["inferencia"].calcular()
    muestreo = origen.vistas["muestreo"]
    muestreo.metodo.setCurrentIndex(muestreo.metodo.findData("proporcional"))
    muestreo.calcular()
    esperar(lambda: all(v.ultimo is not None and not v._ocupado for v in origen.vistas.values()))
    claves = list(origen.vistas)
    for clave, vista in origen.vistas.items():
        if clave in ("muestreo", "descriptiva"):
            nombres = [vista.hojas.itemText(j) for j in range(vista.hojas.count())]
            assert len(nombres) >= 2
            for nombre in nombres[:2]:
                vista.hojas.setCurrentText(nombre)
                assert vista.tabla.rowCount() > 0
                vista.tabla.item(0, 0).setText(f"editado:{clave}:{nombre}")
            vista.hojas.setCurrentText(nombres[0])
        else:
            assert vista.tabla.rowCount() > 0
            vista.tabla.item(0, 0).setText(f"editado:{clave}")
    estado = {"tema": "oscuro", "modulo": "muestreo", "vistas": {
        clave: vista.estado() for clave, vista in origen.vistas.items()}}
    archivo = guardar_sesion(estado, tmp_path / "prueba.json")
    copia = cargar_sesion(archivo)

    # Se restaura inmediatamente, mientras aún pueden estar arrancando las tareas
    # iniciales: ningún resultado viejo debe sobreescribir las tablas cargadas.
    destino = VentanaPrincipal()
    destino.show()
    destino.aplicar_tema(copia["tema"])
    for clave in claves:
        destino.vistas[clave].restaurar(copia["vistas"][clave])
    # Guardar inmediatamente después de abrir no debe descartar las tablas en cola.
    for clave in claves:
        pendiente = destino.vistas[clave].estado()
        if clave in ("muestreo", "descriptiva"):
            assert pendiente["tablas"] == copia["vistas"][clave]["tablas"]
        else:
            assert pendiente["tabla"] == copia["vistas"][clave]["tabla"]
    destino.cambiar(copia["modulo"])
    esperar(lambda: all(v.ultimo is not None and not v._ocupado and not v._recalculo_pendiente
                        and v._tabla_pendiente is None and not v._hojas_pendientes
                        for v in destino.vistas.values()))
    assert destino.tema_actual == "oscuro"
    assert destino.actual == "muestreo"
    for clave, vista in destino.vistas.items():
        if clave in ("muestreo", "descriptiva"):
            originales = copia["vistas"][clave]["tablas"]
            for nombre in list(originales)[:2]:
                vista.hojas.setCurrentText(nombre)
                assert vista.tabla.item(0, 0).text() == f"editado:{clave}:{nombre}"
                assert vista.tablas_exportables()[nombre].iloc[0, 0] == f"editado:{clave}:{nombre}"
        else:
            assert vista.tabla.item(0, 0).text() == f"editado:{clave}"
            assert next(iter(vista.tablas_exportables().values())).iloc[0, 0] == f"editado:{clave}"
    destino.close()
    origen.close()
    app.processEvents()


def test_abrir_sesion_sin_resultados_limpia_pantallas_y_tareas(app):
    import time
    from ampu.ui.main_window import VentanaPrincipal

    ventana = VentanaPrincipal()
    ventana.show()
    for clave in ("probabilidad", "inferencia"):
        vista = ventana.vistas[clave]
        vista.calcular()
        esperar(lambda: vista.ultimo is not None and not vista._ocupado)
        estado = vista.estado()
        vista.restaurar({**estado, "tabla": None})
        assert vista.ultimo is None
        assert vista.tabla.rowCount() == 0
        assert vista.tablas_exportables() == {}

    vista = ventana.vistas["probabilidad"]
    marcadores = []
    vista.trabajar(lambda: (time.sleep(.15), 42)[1], marcadores.append)
    vista.limpiar_resultado()
    esperar(lambda: not vista._ocupado)
    assert not marcadores  # Un resultado iniciado antes de restaurar no reaparece.

    simulacion = ventana.vistas["simulacion"]
    simulacion.restaurar({**simulacion.estado(), "tabla": None})
    esperar(lambda: not simulacion._ocupado and not simulacion._inicial.isActive())
    assert simulacion.ultimo is None
    ventana.close()
    app.processEvents()


def test_apertura_rechaza_estado_invalido_sin_alterar_tema(app, tmp_path, monkeypatch):
    from ampu.io.sesion import guardar_sesion
    from ampu.ui.main_window import VentanaPrincipal

    ventana = VentanaPrincipal()
    archivo = guardar_sesion({"tema": "desconocido", "vistas": []}, tmp_path / "invalida.json")
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", lambda *args: (str(archivo), ""))
    avisos = []
    monkeypatch.setattr(ventana, "_error", avisos.append)
    ventana.abrir_sesion()
    assert avisos and ventana.tema_actual == "claro"
    assert ventana.actual == "distribuciones"
    esperar(lambda: all(not v._ocupado and not (v._inicial and v._inicial.isActive())
                        for v in ventana.vistas.values()))
    ventana.close()
    app.processEvents()


def test_teoria_sin_bibliotecas_nativas_no_rompe_la_navegacion(app, monkeypatch):
    import sys
    from ampu.ui.main_window import VentanaPrincipal

    ventana = VentanaPrincipal()
    errores = []
    monkeypatch.setattr(ventana, "_error", errores.append)
    monkeypatch.setitem(sys.modules, "ampu.ui.vistas.teoria", None)
    assert ventana.cambiar("teoria") is False
    assert ventana.actual == "distribuciones"
    assert len(errores) == 1 and "QtWebEngine" in errores[0]
    assert "teoria" not in ventana.vistas
    esperar(lambda: all(not v._ocupado and not (v._inicial and v._inicial.isActive())
                        for v in ventana.vistas.values()))
    ventana.close()
    app.processEvents()


def test_tabla_de_sesion_rechaza_esquema_distinto(app):
    from ampu.ui.widgets.trabajos import tabla_de_sesion

    original = pd.DataFrame({"media": [1.5]})
    assert tabla_de_sesion({"media": [2.5]}, original).iloc[0, 0] == 2.5
    assert tabla_de_sesion({"otra": [2.5]}, original) is original
    assert tabla_de_sesion({"media": [1, 2], "otra": [2]}, original) is original
