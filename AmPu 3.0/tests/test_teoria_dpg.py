"""Biblioteca Dear PyGui offline, buscable y con figura local."""

import dearpygui.dearpygui as dpg


def test_teoria_carga_leccion_figura_y_busqueda(ventana):
    ventana.abrir_teoria("binomial")
    vista = ventana.vistas["teoria"]
    contenido = dpg.get_value(vista.contenido)
    assert "Binomial" in contenido
    assert "Definición formal" in contenido
    assert vista._textura is not None and dpg.does_item_exist(vista._textura)
    dpg.set_value(vista.busqueda, "probabilidad")
    vista.buscar()
    assert "coincidencia" in dpg.get_value(vista.estado_busqueda)


def test_filtro_y_restauracion_de_leccion(ventana):
    vista = ventana.vistas["teoria"]
    assert len(vista._lecciones) == 57
    dpg.set_value(vista.filtro, "muestreo")
    vista._filtrar()
    assert len(vista.selector.opciones) >= 5
    vista.seleccionar("muestreo_finito")
    assert vista.estado()["clave"] == "muestreo_finito"
    vista.restaurar({"clave": "normal"})
    assert vista.estado()["clave"] == "normal"
    assert "Normal" in dpg.get_value(vista.contenido)
