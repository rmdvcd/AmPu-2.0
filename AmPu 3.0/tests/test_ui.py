"""Integración Dear PyGui: navegación, registro dinámico y cálculos reales."""


def test_fabrica_de_temas_expone_variantes(contexto_dpg):
    from ampu.ui.temas import crear_temas
    pack = crear_temas(True)
    assert set(pack) >= {"global", "primario", "nav", "nav_activo", "sidebar"}


def test_ventana_y_registro_dinamico(ventana, contexto_dpg):
    from ampu.core.distribuciones import DISTRIBUCIONES

    vista = ventana.vistas["distribuciones"]
    assert len(vista.selector.opciones) == len(DISTRIBUCIONES)
    vista.selector.establecer("erlang")
    vista._seleccionada()
    assert set(vista.formulario.controles) == {"k", "tasa"}
    ventana.aplicar_tema("oscuro")
    assert ventana.tema_actual == "oscuro"
    assert ventana.cambiar("probabilidad")
    assert ventana.actual == "probabilidad"
    assert contexto_dpg.does_item_exist(ventana.window)


def test_seis_vistas_calculan_tablas_y_graficos_exportables(ventana):
    for clave in ("distribuciones", "muestreo", "descriptiva", "probabilidad", "inferencia", "simulacion"):
        assert ventana.cambiar(clave)
        assert ventana.esperar(30), clave
        vista = ventana.vistas[clave]
        assert vista.ultimo is not None, clave
        assert vista.tabla.rowCount() > 0, clave
        assert vista.tablas_exportables(), clave
        assert vista.estado(), clave
        assert vista.grafico.figura.axes, clave
        assert vista.grafico.descripcion, clave
