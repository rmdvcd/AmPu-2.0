"""Asistente no modal Dear PyGui: AST seguro, LaTeX editable y recuperación."""

import dearpygui.dearpygui as dpg


def test_calculo_explicado_copia_y_error_recuperable(ventana):
    asistente = ventana.asistente
    ventana.calculadora()
    assert dpg.get_item_configuration(asistente.window)["show"]
    dpg.set_value(asistente.entrada, "sqrt(2)+sin(pi/2)")
    asistente._evaluar()
    assert "2.41421" in dpg.get_value(asistente.respuesta)
    assert "radianes" in dpg.get_value(asistente.pasos)
    asistente.copiar_resultado()
    assert dpg.get_clipboard_text() == str(asistente._resultado)
    dpg.set_value(asistente.entrada, "1/0")
    asistente._evaluar()
    assert "Error:" in dpg.get_value(asistente.respuesta)
    assert dpg.get_value(asistente.entrada) == "1/0"


def test_latex_no_se_evalua_y_sesion_no_calcula_al_restaurar(ventana):
    asistente = ventana.asistente
    asistente.insertar_plantilla(r"\frac{a}{b}")
    asistente.copiar_latex()
    assert dpg.get_clipboard_text() == r"\frac{a}{b}"
    dpg.set_value(asistente.entrada, "1/0")
    guardado = asistente.estado()
    asistente.restaurar(guardado)
    assert dpg.get_value(asistente.latex) == r"\frac{a}{b}"
    assert dpg.get_value(asistente.entrada) == "1/0"
    assert asistente._resultado is None
