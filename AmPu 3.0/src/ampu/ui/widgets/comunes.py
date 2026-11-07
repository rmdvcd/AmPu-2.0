"""Componentes Dear PyGui compartidos por las vistas de AmPu."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import dearpygui.dearpygui as dpg
from ampu.ui.entradas import texto_escalar
from ampu.ui.temas import PALETAS, rgba

Callback = Callable[..., Any]


def valor(control: int | str) -> Any:
    return dpg.get_value(control)


def texto(control: int | str) -> str:
    return str(dpg.get_value(control) or "")


def establecer(control: int | str, contenido: Any) -> None:
    if dpg.does_item_exist(control):
        dpg.set_value(control, contenido)


def visible(control: int | str, mostrar: bool) -> None:
    if dpg.does_item_exist(control):
        dpg.configure_item(control, show=mostrar)


def habilitar(control: int | str, activo: bool) -> None:
    if dpg.does_item_exist(control):
        dpg.configure_item(control, enabled=activo)
def _color_texto_tema(oscuro: bool) -> tuple[int, int, int, int]:
        p = PALETAS["oscuro" if oscuro else "claro"]
        return rgba(p["texto"])


def etiqueta(contenido: str, parent: int | str, *, wrap: int = -1,
             oscuro: bool = False, color: tuple[int, int, int, int] | None = None) -> int | str:
    opciones: dict[str, Any] = {"parent": parent, "wrap": wrap}
    if color is None:
        color = _color_texto_tema(oscuro)
    if color is not None:
        opciones["color"] = color
    return dpg.add_text(contenido, **opciones)

def encabezado(parent: int | str, codigo: str, titulo: str, descripcion: str, oscuro: bool = False) -> int | str:
    """Cabecera editorial uniforme de cada módulo."""
    with dpg.group(parent=parent) as grupo:
        dpg.add_text(codigo, color=_color_texto_tema(oscuro))
        dpg.add_text(titulo, color=_color_texto_tema(oscuro))
        dpg.add_text(descripcion, wrap=920)
        dpg.add_spacer(height=5)
    return grupo



def marco(parent: int | str, *, width: int = -1, height: int = -1,
          border: bool = True) -> int | str:
    return dpg.add_child_window(parent=parent, width=width, height=height, border=border,
                                horizontal_scrollbar=True)


def campo_semilla(parent: int | str, callback: Callback | None = None) -> int | str:
    return dpg.add_input_int(parent=parent, default_value=42, min_value=0,
                             max_value=2_147_483_647, min_clamped=True,
                             max_clamped=True, step=1, width=145, callback=callback)


class Selector:
    """Combo con valores de dominio estables y etiquetas traducibles."""

    def __init__(self, parent: int | str, opciones: Iterable[tuple[str, Any]] | Iterable[str],
                 *, callback: Callback | None = None, default: Any = None,
                 width: int = -1, label: str = ""):
        pares = list(opciones)
        self.opciones = [(str(p[0]), p[1]) for p in pares] if pares and isinstance(pares[0], tuple) else [(str(p), str(p)) for p in pares]
        self._claves = {etiqueta_: clave for etiqueta_, clave in self.opciones}
        inicial = next((e for e, c in self.opciones if c == default), self.opciones[0][0] if self.opciones else "")
        self.tag = dpg.add_combo([e for e, _ in self.opciones], parent=parent,
                                 default_value=inicial, callback=callback, width=width, label=label)

    @property
    def valor(self) -> Any:
        return self._claves.get(str(dpg.get_value(self.tag)))

    @property
    def etiqueta(self) -> str:
        return str(dpg.get_value(self.tag) or "")

    @property
    def etiquetas(self) -> list[str]:
        return [e for e, _ in self.opciones]

    def establecer(self, clave: Any) -> None:
        etiqueta_ = next((e for e, c in self.opciones if c == clave), None)
        if etiqueta_ is None and str(clave) in self._claves:
            etiqueta_ = str(clave)
        if etiqueta_ is not None:
            dpg.set_value(self.tag, etiqueta_)

    def reemplazar(self, opciones: Iterable[tuple[str, Any]], preferido: Any = None) -> None:
        self.opciones = list(opciones)
        self._claves = {e: c for e, c in self.opciones}
        inicial = next((e for e, c in self.opciones if c == preferido), self.opciones[0][0] if self.opciones else "")
        dpg.configure_item(self.tag, items=[e for e, _ in self.opciones])
        dpg.set_value(self.tag, inicial)

    def habilitar(self, activo: bool) -> None:
        habilitar(self.tag, activo)

    def mostrar(self, mostrar: bool) -> None:
        visible(self.tag, mostrar)


class KPIs:
    """Banda de indicadores escalares creada con grupos Dear PyGui."""

    def __init__(self, parent: int | str, titulos: list[str], oscuro: bool = False):
        self.valores: list[int | str] = []
        with dpg.group(parent=parent, horizontal=True, horizontal_spacing=8):
            for titulo in titulos:
                with dpg.child_window(width=180, height=65, border=True):
                    dpg.add_text(titulo.upper(), wrap=170, color=_color_texto_tema(oscuro))
                    self.valores.append(dpg.add_text("—", wrap=170))

    def actualizar(self, *valores: object) -> None:
        for control, contenido in zip(self.valores, valores):
            dpg.set_value(control, texto_escalar(contenido))

    def limpiar(self) -> None:
        for control in self.valores:
            dpg.set_value(control, "—")
