"""Combinatoria, probabilidad condicional, Bayes y momentos con Dear PyGui."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from ampu.ui.logica import _resolver_probabilidad
from ampu.ui.vistas.base import botones_accion, disposicion
from ampu.ui.widgets.comunes import Selector, establecer, texto, valor, visible
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo

OPERACIONES = [("Combinatoria exacta", "combinatoria"),
    ("Probabilidad condicional", "condicional"), ("Bayes y probabilidad total", "bayes"),
    ("E, Var y MGF discretas", "momentos")]


class VistaProbabilidad(VistaTrabajo):
    def __init__(self, parent: int | str):
        super().__init__()
        self.tema_actual = "claro"
        self._restaurando = True
        _, izquierda, derecha = disposicion(parent, "04  /  FUNDAMENTOS",
            "Probabilidad básica", "Factoriales exactos, Bayes, independencia y momentos de variables finitas.")
        dpg.add_text("OPERACIÓN", parent=izquierda)
        self.tipo = Selector(izquierda, OPERACIONES, callback=self._configurar)
        with dpg.group(parent=izquierda) as self.grupo_combinatoria:
            self.n = dpg.add_input_int(label="n · elementos", default_value=10, min_value=0,
                max_value=100, width=-1, callback=self._marcar_entradas)
            self.k = dpg.add_input_int(label="k · elegidos", default_value=3, min_value=0,
                max_value=100, width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_condicional:
            self.a = dpg.add_input_double(label="P(A∩B)", default_value=.2, min_value=0,
                max_value=1, format="%.5f", width=-1, callback=self._marcar_entradas)
            self.b = dpg.add_input_double(label="P(B)", default_value=.4, min_value=0,
                max_value=1, format="%.5f", width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_listas:
            dpg.add_text("LISTA 1 · previas o soporte X")
            self.priores = dpg.add_input_text(default_value="0.4, 0.6", width=-1,
                                              callback=self._marcar_entradas)
            dpg.add_text("LISTA 2 · verosimilitudes o masas")
            self.verosimilitudes = dpg.add_input_text(default_value="0.5, 0.1", width=-1,
                                                      callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_mgf:
            self.t = dpg.add_input_double(label="Argumento MGF: t", default_value=.5,
                min_value=-20, max_value=20, width=-1, callback=self._marcar_entradas)
        self.boton = botones_accion(izquierda, "Resolver", self.calcular,
                                    lambda: self.abrir_teoria(self.clave_teoria()))
        self.conclusion = dpg.add_text("Configura y resuelve una identidad o consulta.",
                                       parent=derecha, wrap=800)
        self.grafico = Grafico(derecha)
        dpg.add_text("RESULTADO NUMÉRICO", parent=derecha)
        self.tabla = TablaDatos(derecha, modificado=lambda: self.entrada_modificada())
        self._configurar()
        self._restaurando = False

    def _configurar(self, *_args) -> None:
        tipo = self.tipo.valor
        visible(self.grupo_combinatoria, tipo == "combinatoria")
        visible(self.grupo_condicional, tipo == "condicional")
        visible(self.grupo_listas, tipo in ("bayes", "momentos"))
        visible(self.grupo_mgf, tipo == "momentos")
        self._marcar_entradas()

    def calcular(self) -> None:
        if self._ocupado:
            return
        self.trabajar(_resolver_probabilidad, self._recibir, lambda: None,
            self.tipo.valor, valor(self.n), valor(self.k), valor(self.a), valor(self.b),
            texto(self.priores), texto(self.verosimilitudes), valor(self.t))
        self.notificar("Resolviendo probabilidad…")

    def _recibir(self, salida) -> None:
        self.ultimo = salida
        dpg.set_value(self.conclusion, salida[0])
        self.mostrar_tabla_restaurada(self.tabla, salida[1])
        self.grafico.serie(salida[2], salida[3], self.tipo.etiqueta)
        self.notificar("Resultado disponible para Excel, CSV y PDF.")

    def tablas_exportables(self) -> dict:
        return {self.tipo.etiqueta: self.tabla.datos()} if self.ultimo else {}

    def resumen_exportable(self) -> str:
        return str(dpg.get_value(self.conclusion))

    def clave_teoria(self) -> str:
        return {"combinatoria": "combinatoria", "condicional": "bayes",
                "bayes": "bayes", "momentos": "combinatoria"}[self.tipo.valor]

    def estado(self) -> dict:
        return {"tipo": self.tipo.valor, "n": valor(self.n), "k": valor(self.k),
            "a": valor(self.a), "b": valor(self.b), "priori": texto(self.priores),
            "ver": texto(self.verosimilitudes), "t": valor(self.t),
            "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo else self._tabla_pendiente}

    def restaurar(self, datos: dict) -> None:
        self._restaurando = True
        try:
            self.tipo.establecer(datos.get("tipo", "combinatoria"))
            self._configurar()
            for campo in ("n", "k", "a", "b", "t"):
                establecer(getattr(self, campo), datos.get(campo, valor(getattr(self, campo))))
            establecer(self.priores, datos.get("priori", "0.4, 0.6"))
            establecer(self.verosimilitudes, datos.get("ver", "0.5, 0.1"))
            self._inicial_consumido = True
            self.limpiar_resultado()
            self._tabla_pendiente = datos.get("tabla")
            if self._tabla_pendiente is None:
                dpg.set_value(self.conclusion, "Configura y resuelve una identidad o consulta.")
        finally:
            self._restaurando = False
        if self._tabla_pendiente is not None:
            self.recalcular_restaurado()
