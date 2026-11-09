"""Capturas genuinas del viewport Dear PyGui (requiere entorno gráfico)."""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg", force=True)
import dearpygui.dearpygui as dpg

from ampu.ui.main_window import VentanaPrincipal
from ampu.ui.preferencias import Preferencias

DESTINO = Path(__file__).resolve().parents[1] / "docs" / "capturas"


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    dpg.create_context()
    try:
        ventana = VentanaPrincipal(Preferencias(valores={"interfaz/tema": "claro"}))
        dpg.create_viewport(title="AmPu 3.0", width=1440, height=900,
                            min_width=900, min_height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(ventana.window, True)
        pasos = [("distribuciones", "01_distribuciones_claro.png", "claro"),
                 ("muestreo", "02_muestreo_claro.png", "claro"),
                 ("inferencia", "03_inferencia_claro.png", "claro"),
                 ("distribuciones", "04_distribuciones_oscuro.png", "oscuro")]
        for clave, archivo, tema in pasos:
            ventana.aplicar_tema(tema)
            ventana.cambiar(clave)
            vencimiento = time.monotonic() + 30
            while (ventana.vista._ocupado or ventana.vista.ultimo is None) and time.monotonic() < vencimiento:
                ventana.procesar()
                dpg.render_dearpygui_frame()
            if ventana.vista.ultimo is None:
                raise TimeoutError(f"No terminó el cálculo para {clave}")
            for _ in range(4):
                ventana.procesar()
                dpg.render_dearpygui_frame()
            ruta = DESTINO / archivo
            dpg.output_frame_buffer(file=str(ruta))
            if not ruta.is_file() or not ruta.stat().st_size:
                raise RuntimeError(f"No se pudo capturar {ruta}")
            print(ruta.name, ruta.stat().st_size, "bytes")
        return 0
    finally:
        if "ventana" in locals():
            ventana.cerrar()
        dpg.destroy_context()


if __name__ == "__main__":
    raise SystemExit(main())
