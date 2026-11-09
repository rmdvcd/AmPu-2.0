"""Contexto Dear PyGui real y sin viewport para pruebas de integración."""

import matplotlib
import pytest

matplotlib.use("Agg", force=True)
dpg = pytest.importorskip("dearpygui.dearpygui", reason="Dear PyGui no está instalado")


@pytest.fixture
def contexto_dpg():
    dpg.create_context()
    yield dpg
    dpg.destroy_context()


@pytest.fixture
def ventana(contexto_dpg, tmp_path):
    from ampu.ui.main_window import VentanaPrincipal
    from ampu.ui.preferencias import Preferencias

    preferencias = Preferencias(tmp_path / "preferencias.json",
                                valores={"interfaz/tema": "claro", "interfaz/escala": 1.0})
    instancia = VentanaPrincipal(preferencias)
    yield instancia
    instancia.esperar(30)
    instancia.cerrar()
