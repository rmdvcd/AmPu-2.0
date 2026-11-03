"""Sesiones versionadas y trabajos antiguos en la interfaz Dear PyGui."""

import time

import dearpygui.dearpygui as dpg
import pandas as pd


def _calcular_todas(ventana):
    for clave in ("distribuciones", "muestreo", "descriptiva", "probabilidad", "inferencia", "simulacion"):
        ventana.cambiar(clave)
        assert ventana.vistas[clave].esperar(30), clave


def test_sesion_restaura_ediciones_en_todas_las_vistas(ventana, tmp_path):
    _calcular_todas(ventana)
    for clave, vista in ventana.vistas.items():
        if clave == "teoria":
            continue
        if clave in ("muestreo", "descriptiva"):
            for nombre in vista.hojas.etiquetas[:2]:
                vista.hojas.establecer(nombre)
                vista._mostrar_tabla() if clave == "muestreo" else vista._tabla()
                vista.tabla.editar_celda(0, 0, f"editado:{clave}:{nombre}")
            vista.hojas.establecer(vista.hojas.etiquetas[0])
            vista._mostrar_tabla() if clave == "muestreo" else vista._tabla()
        else:
            vista.tabla.editar_celda(0, 0, f"editado:{clave}")
    archivo = tmp_path / "sesion.json"
    assert ventana.guardar_sesion(archivo)
    ventana.cambiar("distribuciones")
    assert ventana.abrir_sesion(archivo)
    assert ventana.esperar(40)
    for clave, vista in ventana.vistas.items():
        if clave == "teoria":
            continue
        if clave in ("muestreo", "descriptiva"):
            for nombre in vista.hojas.etiquetas[:2]:
                vista.hojas.establecer(nombre)
                vista._mostrar_tabla() if clave == "muestreo" else vista._tabla()
                assert vista.tabla.datos().iloc[0, 0] == f"editado:{clave}:{nombre}"
        else:
            assert vista.tabla.datos().iloc[0, 0] == f"editado:{clave}"


def test_restaurar_sin_resultados_descarta_trabajo_anterior(ventana):
    vista = ventana.vistas["probabilidad"]
    ventana.cambiar("probabilidad")
    assert vista.esperar(30)
    estado = vista.estado()
    vista.restaurar({**estado, "tabla": None})
    assert vista.ultimo is None
    assert vista.tabla.rowCount() == 0
    assert vista.tablas_exportables() == {}
    marcadores = []
    vista.trabajar(lambda: (time.sleep(.1), 42)[1], marcadores.append)
    vista.limpiar_resultado()
    assert vista.esperar(10)
    assert not marcadores


def test_tabla_de_sesion_rechaza_esquema_distinto():
    from ampu.ui.widgets.trabajos import tabla_de_sesion
    original = pd.DataFrame({"media": [1.5]})
    assert tabla_de_sesion({"media": [2.5]}, original).iloc[0, 0] == 2.5
    assert tabla_de_sesion({"otra": [2.5]}, original) is original
    assert tabla_de_sesion({"media": [1, 2], "otra": [2]}, original) is original


def test_exportadores_desde_la_ui_generan_archivos_reales(ventana, tmp_path):
    assert ventana.esperar(30)
    for formato in ("excel", "csv", "png", "pdf"):
        ruta = ventana.exportar(formato, tmp_path / f"resultado.{formato if formato != 'excel' else 'xlsx'}")
        assert ruta.is_file() and ruta.stat().st_size > 0, formato
