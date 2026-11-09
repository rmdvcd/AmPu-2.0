"""Preferencias, estado de exportación y sesiones de la ventana Dear PyGui."""

import json

import dearpygui.dearpygui as dpg


def test_preferencia_antigua_de_contraste_migra(tmp_path):
    from ampu.ui.preferencias import Preferencias
    preferencias = Preferencias(tmp_path / "prefs.json", valores={"interfaz/tema": "contraste", "interfaz/escala": 99})
    assert preferencias.get("interfaz/tema") == "sistema"
    assert preferencias.get("interfaz/escala") == 2.0


def test_tema_escala_y_preferencias_persistentes(ventana, tmp_path):
    ventana.aplicar_tema("oscuro", persistir=True)
    ventana.escalar_texto(.3)
    assert ventana.tema_actual == "oscuro"
    assert ventana.escala_fuente == 1.3
    assert ventana.vistas["distribuciones"].grafico._escala == 1.3
    ventana.escalar_texto(.7)
    assert ventana.escala_fuente == 2.0
    ventana.cerrar()
    datos = json.loads(ventana.preferencias.ruta.read_text(encoding="utf-8"))
    assert datos["interfaz/tema"] == "oscuro"
    assert datos["interfaz/escala"] == 2.0


def test_exportacion_se_bloquea_con_entradas_desactualizadas(ventana):
    assert ventana.esperar(30)
    vista = ventana.vistas["distribuciones"]
    assert dpg.is_item_enabled(ventana.acciones_exportar["excel"])
    dpg.set_value(vista.evento, "6")
    vista._cambio_evento()
    assert vista._desactualizado
    assert not dpg.is_item_enabled(ventana.acciones_exportar["excel"])
    vista.calcular()
    assert ventana.esperar(30)
    assert not vista._desactualizado
    assert dpg.is_item_enabled(ventana.acciones_exportar["excel"])


def test_guardar_y_reabrir_con_entrada_parcial(ventana, tmp_path):
    from ampu.io.sesion import cargar_sesion
    vista = ventana.vistas["distribuciones"]
    vista.selector.establecer("multinomial")
    vista._seleccionada()
    dpg.set_value(vista.formulario.controles["p"], "0.1, pendiente, 0.9")
    dpg.set_value(ventana.asistente.latex, r"\frac{a}{b}")
    ventana._marcar_sesion()
    archivo = tmp_path / "incompleta.json"
    assert ventana.guardar_sesion(archivo)
    assert not ventana._cambios_sin_guardar
    estado = cargar_sesion(archivo)
    assert estado["interfaz"] == "Dear PyGui"
    assert estado["vistas"]["distribuciones"]["parametros"]["p"] == "0.1, pendiente, 0.9"
    assert estado["asistente"]["latex"] == r"\frac{a}{b}"
    dpg.set_value(ventana.asistente.latex, "alterada")
    assert ventana.abrir_sesion(archivo)
    assert ventana.esperar(30)
    assert dpg.get_value(ventana.asistente.latex) == r"\frac{a}{b}"
    assert not ventana._cambios_sin_guardar


def test_menus_de_escritorio_incluyen_edicion_y_ventana(ventana):
    assert set(ventana.menus) >= {"Archivo", "Edición", "Ver", "Ventana", "Ayuda"}
    ventana.cambiar("muestreo")
    assert ventana.actual == "muestreo"


def test_apertura_invalida_no_altera_modulo_ni_tema(ventana, tmp_path):
    from ampu.io.sesion import guardar_sesion
    archivo = guardar_sesion({"tema": "desconocido", "vistas": []}, tmp_path / "invalida.json")
    avisos = []
    ventana._error = avisos.append
    assert not ventana.abrir_sesion(archivo)
    assert avisos
    assert ventana.tema_actual == "claro"
    assert ventana.actual == "distribuciones"
