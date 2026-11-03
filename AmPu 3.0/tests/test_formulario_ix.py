"""Formularios Dear PyGui generados por metadatos y entradas recuperables."""

import dearpygui.dearpygui as dpg


def test_campos_antiguos_se_eliminan_al_cambiar_modelo(contexto_dpg):
    from ampu.core.distribuciones import obtener
    from ampu.ui.widgets.formulario import FormularioDistribucion

    with dpg.window():
        formulario = FormularioDistribucion(dpg.last_container())
        formulario.usar(obtener("binomial"))
        antiguos = list(formulario.controles.values())
        formulario.usar(obtener("normal"))
        assert all(not dpg.does_item_exist(control) for control in antiguos)
        assert set(formulario.controles) == {"mu", "sigma"}


def test_formulario_conserva_entrada_vectorial_invalida(contexto_dpg):
    from ampu.core.distribuciones import obtener
    from ampu.ui.widgets.formulario import FormularioDistribucion

    with dpg.window():
        formulario = FormularioDistribucion(dpg.last_container())
        formulario.usar(obtener("multinomial"))
        dpg.set_value(formulario.controles["p"], "0.1, pendiente, 0.9")
        estado = formulario.estado()
        assert estado["p"] == "0.1, pendiente, 0.9"
        formulario.restaurar(estado)
        assert dpg.get_value(formulario.controles["p"]) == "0.1, pendiente, 0.9"
