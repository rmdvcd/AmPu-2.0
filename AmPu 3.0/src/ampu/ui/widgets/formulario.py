"""Formulario Dear PyGui generado desde los metadatos del registro."""

from __future__ import annotations

import math
from collections.abc import Callable

import dearpygui.dearpygui as dpg

from ampu.core.distribuciones.base import Distribucion
from ampu.core.errores import ParametroInvalidoError


class FormularioDistribucion:
    """Crea editores Dear PyGui sin duplicar reglas estadísticas."""

    def __init__(self, parent: int | str | None = None,
                 cambiado: Callable[..., None] | None = None):
        self.modelo: Distribucion | None = None
        self.controles: dict[str, int | str] = {}
        self._tipos: dict[str, str] = {}
        self.cambiado = cambiado
        self.tag = dpg.add_group(parent=parent) if parent is not None else None

    def montar(self, parent: int | str) -> None:
        if self.tag is None:
            self.tag = dpg.add_group(parent=parent)

    def _cambio(self, *_args) -> None:
        if self.cambiado is not None:
            self.cambiado()

    def usar(self, modelo: Distribucion) -> None:
        """Reemplaza los campos al cambiar de distribución."""
        if self.tag is None:
            raise RuntimeError("Monta el formulario en un contenedor Dear PyGui primero.")
        dpg.delete_item(self.tag, children_only=True, slot=1)
        self.controles.clear()
        self._tipos.clear()
        self.modelo = modelo
        for campo in modelo.parametros:
            nombre = campo.nombre
            etiqueta = nombre.replace("_", " ")
            if campo.tipo.startswith("vector_"):
                inicial = ", ".join(map(str, campo.default))
                control = dpg.add_input_text(parent=self.tag, label=etiqueta, default_value=inicial,
                                             hint="Valores separados por comas", width=275,
                                             callback=self._cambio)
            elif campo.tipo == "entero":
                minimo = math.ceil(campo.minimo) if campo.minimo is not None else -1_000_000
                maximo = math.floor(campo.maximo) if campo.maximo is not None else 1_000_000
                control = dpg.add_input_int(parent=self.tag, label=etiqueta,
                                            default_value=int(campo.default),
                                            min_value=max(-1_000_000, minimo),
                                            max_value=min(1_000_000, maximo), width=275,
                                            callback=self._cambio)
            else:
                minimo = campo.minimo if campo.minimo is not None else -1e12
                maximo = campo.maximo if campo.maximo is not None else 1e12
                control = dpg.add_input_double(parent=self.tag, label=etiqueta,
                                               default_value=float(campo.default),
                                               min_value=max(-1e12, minimo),
                                               max_value=min(1e12, maximo), format="%.10g",
                                               step=.1, width=275, callback=self._cambio)
            with dpg.tooltip(control):
                dpg.add_text(campo.descripcion, wrap=330)
            self.controles[nombre] = control
            self._tipos[nombre] = campo.tipo
        self._cambio()

    def valores(self) -> dict:
        if self.modelo is None:
            raise ParametroInvalidoError("Selecciona una distribución.")
        salida: dict[str, object] = {}
        for campo in self.modelo.parametros:
            control = self.controles[campo.nombre]
            if campo.tipo.startswith("vector_"):
                try:
                    salida[campo.nombre] = [float(x.strip()) for x in str(dpg.get_value(control)).split(",")]
                except ValueError as exc:
                    raise ParametroInvalidoError(
                        f"{campo.nombre}: separa números con comas y usa punto decimal.") from exc
            else:
                salida[campo.nombre] = dpg.get_value(control)
        return self.modelo.validar(**salida)

    def estado(self) -> dict:
        """Conserva incluso una lista vectorial parcialmente escrita."""
        salida: dict[str, object] = {}
        for nombre, control in self.controles.items():
            actual = dpg.get_value(control)
            if self._tipos[nombre].startswith("vector_"):
                try:
                    salida[nombre] = [float(parte.strip()) for parte in str(actual).split(",")]
                except ValueError:
                    salida[nombre] = str(actual)
            else:
                salida[nombre] = actual
        return salida

    def restaurar(self, valores: dict) -> None:
        for nombre, contenido in valores.items():
            if nombre not in self.controles:
                continue
            if self._tipos[nombre].startswith("vector_") and not isinstance(contenido, str):
                contenido = ", ".join(map(str, contenido))
            dpg.set_value(self.controles[nombre], contenido)
        self._cambio()

    def habilitar(self, activo: bool) -> None:
        for control in self.controles.values():
            dpg.configure_item(control, enabled=activo)
