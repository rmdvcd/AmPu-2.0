"""Edición, portapapeles, historial y paginación de tablas Dear PyGui."""

import dearpygui.dearpygui as dpg
import pandas as pd


def _tabla(datos):
    with dpg.window():
        tabla = dpg.add_group()
        from ampu.ui.widgets.tabla import TablaDatos
        return TablaDatos(tabla, filas_por_pagina=40)


def test_precision_edicion_y_deshacer(contexto_dpg):
    from ampu.ui.widgets.tabla import TablaDatos
    tabla = _tabla(None)
    valores = pd.DataFrame({"probabilidad": [0.12345678912345678, 0.9876543219876543],
                            "id": [2**53 + 1, 2**53 + 2]})
    tabla.mostrar(valores)
    assert tabla.datos().equals(valores)
    tabla.editar_celda(0, 0, "0.999")
    assert tabla.datos().iloc[0, 0] == 0.999
    assert tabla.puede_deshacer()
    tabla.undo()
    assert tabla.datos().equals(valores)
    assert tabla.puede_rehacer()
    tabla.redo()
    tabla.ordenar("probabilidad")
    assert tabla.datos().iloc[0, 0] == valores.iloc[1, 0]


def test_pegado_multicelda_es_una_accion_reversible(contexto_dpg):
    cambios = []
    with dpg.window():
        from ampu.ui.widgets.tabla import TablaDatos
        tabla = TablaDatos(dpg.last_container(), modificado=lambda: cambios.append(True))
    tabla.mostrar(pd.DataFrame({"Valor": [1.12345678912345], "Etiqueta": ["a"]}))
    tabla.pegar(0, 0, "3\tb\n4\tc")
    assert tabla.datos().to_dict(orient="list") == {"Valor": [3.0, 4.0], "Etiqueta": ["b", "c"]}
    tabla.undo()
    assert tabla.rowCount() == 1
    assert tabla.datos().iloc[0, 0] == 1.12345678912345
    tabla.redo()
    assert tabla.rowCount() == 2 and tabla.datos().iloc[1, 1] == "c"
    assert len(cambios) == 3


def test_historias_independientes_y_paginacion(contexto_dpg):
    from ampu.ui.widgets.tabla import TablaDatos
    tabla = _tabla(None)
    tabla.mostrar(pd.DataFrame({"A": [1.0]}), identificador="Primera")
    tabla.editar_celda(0, 0, "10")
    tabla.mostrar(pd.DataFrame({"B": [2.0]}), identificador="Segunda")
    tabla.editar_celda(0, 0, "20")
    tabla.mostrar(pd.DataFrame({"A": [10.0]}), identificador="Primera")
    tabla.undo()
    assert tabla.datos().iloc[0, 0] == 1.0
    tabla.mostrar(pd.DataFrame({"B": [20.0]}), identificador="Segunda")
    tabla.undo()
    assert tabla.datos().iloc[0, 0] == 2.0
    tabla.mostrar(pd.DataFrame({"n": range(95)}))
    assert tabla.rowCount() == 95
    tabla.cambiar_pagina(1)
    tabla.cambiar_pagina(1)
    assert "3/3" in dpg.get_value(tabla._pagina_tag)
