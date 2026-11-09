"""Disposición común de formulario y resultados en Dear PyGui."""

from __future__ import annotations

from collections.abc import Callable

import dearpygui.dearpygui as dpg

from ampu.ui.temas import marcar_primario
from ampu.ui.widgets.comunes import encabezado


def disposicion(parent: int | str, codigo: str, titulo: str,
                descripcion: str) -> tuple[int | str, int | str, int | str]:
    with dpg.group(parent=parent) as raiz:
        encabezado(raiz, codigo, titulo, descripcion)
        with dpg.group(horizontal=True, horizontal_spacing=12):
            izquierda = dpg.add_child_window(width=300, height=-1, border=True,
                                             horizontal_scrollbar=True)
            derecha = dpg.add_child_window(width=-1, height=-1, border=False,
                                           horizontal_scrollbar=True)
    return raiz, izquierda, derecha


def botones_accion(parent: int | str, texto: str, calcular: Callable,
                   teoria: Callable[[], None]) -> int | str:
    boton = dpg.add_button(parent=parent, label=texto, width=-1, height=36,
                           callback=lambda: calcular())
    marcar_primario(boton)
    dpg.add_button(parent=parent, label="Abrir teoría y fórmulas", width=-1,
                   callback=lambda: teoria())
    return boton
