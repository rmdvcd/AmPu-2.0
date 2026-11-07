"""Contrastes, intervalos y regresión con widgets Dear PyGui."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from ampu.ui.logica import EJEMPLOS, OPCIONES, _evaluar
from ampu.ui.vistas.base import botones_accion, disposicion
from ampu.ui.widgets.comunes import KPIs, Selector, establecer, texto, valor, visible
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


class VistaInferencia(VistaTrabajo):
    def __init__(self, parent: int | str):
        super().__init__()
        self.tema_actual = "claro"
        self._restaurando = True
        _, izquierda, derecha = disposicion(parent, "05  /  DECISIONES BASADAS EN DATOS",
            "Inferencia", "Contrastes, intervalos, correlación y regresión con conclusiones responsables.")
        dpg.add_text("TÉCNICA", parent=izquierda)
        self.tipo = Selector(izquierda, [(n, (c, t)) for n, c, t in OPCIONES], callback=self._opcion)
        self.ayuda = dpg.add_text("", parent=izquierda, wrap=285)
        with dpg.group(parent=izquierda) as self.grupo_datos:
            dpg.add_text("DATOS X / TABLA")
            self.x = dpg.add_input_text(multiline=True, width=-1, height=90,
                default_value="7, 8, 9, 10, 11, 12, 13", callback=self._marcar_entradas)
            dpg.add_text("DATOS Y / ESPERADAS")
            self.y = dpg.add_input_text(multiline=True, width=-1, height=70,
                default_value="4, 5, 6, 7, 8, 9, 10", callback=self._marcar_entradas)
        self.alfa = dpg.add_input_double(parent=izquierda, label="Significación α",
            default_value=.05, min_value=.001, max_value=.99, format="%.3f", width=-1,
            callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_mu:
            self.mu0 = dpg.add_input_double(label="Hipótesis μ₀", default_value=8,
                min_value=-1e8, max_value=1e8, width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_sigma1:
            self.sigma1 = dpg.add_input_double(label="Desv. σ₁", default_value=2,
                min_value=.001, max_value=1e8, width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_sigma2:
            self.sigma2 = dpg.add_input_double(label="Desv. σ₂", default_value=3,
                min_value=.001, max_value=1e8, width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_p0:
            self.p0 = dpg.add_input_double(label="Proporción p₀", default_value=.5,
                min_value=.001, max_value=.999, format="%.3f", width=-1,
                callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_proporciones:
            self.x1 = dpg.add_input_int(label="Éxitos x₁", default_value=40, min_value=0,
                max_value=1_000_000, width=-1, callback=self._marcar_entradas)
            self.n1 = dpg.add_input_int(label="Ensayos n₁", default_value=100, min_value=1,
                max_value=1_000_000, width=-1, callback=self._marcar_entradas)
            self.x2 = dpg.add_input_int(label="Éxitos x₂", default_value=20, min_value=0,
                max_value=1_000_000, width=-1, callback=self._marcar_entradas)
            self.n2 = dpg.add_input_int(label="Ensayos n₂", default_value=100, min_value=1,
                max_value=1_000_000, width=-1, callback=self._marcar_entradas)
        self.boton = botones_accion(izquierda, "Contrastar y explicar", self.calcular,
                                    lambda: self.abrir_teoria(self.clave_teoria()))
        self.indicadores = KPIs(derecha, ["Estadístico / R²", "p-valor", "IC inferior", "IC superior"], oscuro=self.tema_actual == "oscuro")
        self.conclusion = dpg.add_text("Elige una técnica para ver su interpretación.",
                                       parent=derecha, wrap=800)
        dpg.add_text("EVIDENCIA VISUAL", parent=derecha)
        self.grafico = Grafico(derecha)
        dpg.add_text("INFORME NUMÉRICO", parent=derecha)
        self.tabla = TablaDatos(derecha, modificado=lambda: self.entrada_modificada())
        self._opcion()
        self._restaurando = False

    def _opcion(self, *_args) -> None:
        clave = self.tipo.valor[0]
        usa_y = clave in ("z_dos", "t_dos", "chi_bondad", "pearson", "spearman",
                          "reg_simple", "reg_multiple", "mann", "wilcoxon")
        proporciona = clave in ("prop_una", "prop_dos")
        visible(self.grupo_datos, not proporciona)
        dpg.configure_item(self.y, enabled=usa_y)
        visible(self.grupo_mu, clave in ("z_una", "t_una"))
        visible(self.grupo_sigma1, clave in ("z_una", "z_dos"))
        visible(self.grupo_sigma2, clave == "z_dos")
        visible(self.grupo_p0, clave == "prop_una")
        visible(self.grupo_proporciones, proporciona)
        dpg.configure_item(self.x2, enabled=clave == "prop_dos")
        dpg.configure_item(self.n2, enabled=clave == "prop_dos")
        if clave in EJEMPLOS:
            xx, yy, ayuda = EJEMPLOS[clave]
        else:
            xx, yy = "7, 8, 9, 10, 11, 12, 13", "4, 5, 6, 7, 8, 9, 10"
            ayuda = ("Valores X e Y separados por comas; usa punto decimal." if usa_y else
                     "Valores X separados por comas o saltos; usa punto decimal.")
            if clave in ("anova", "kruskal", "chi_independencia", "reg_multiple"):
                ayuda = "Una fila por grupo (o por observación para regresión múltiple)."
            if proporciona:
                ayuda = "Usa los campos de éxitos y ensayos; X e Y no son necesarios."
        establecer(self.x, xx)
        establecer(self.y, yy)
        dpg.set_value(self.ayuda, ayuda)
        self._marcar_entradas()

    def calcular(self) -> None:
        if self._ocupado:
            return
        self.trabajar(_evaluar, self._recibir, lambda: None,
            self.tipo.valor[0], texto(self.x), texto(self.y), valor(self.alfa), valor(self.mu0),
            valor(self.sigma1), valor(self.sigma2), valor(self.p0), valor(self.x1),
            valor(self.n1), valor(self.x2), valor(self.n2))
        self.notificar("Calculando contraste e intervalos…")

    def _recibir(self, salida: dict) -> None:
        self.ultimo = salida
        dpg.set_value(self.conclusion, salida["resumen"])
        a, b = salida["intervalo"] if salida["intervalo"] is not None else (float("nan"), float("nan"))
        self.indicadores.actualizar(salida["estadistico"], salida["p"], a, b)
        self.mostrar_tabla_restaurada(self.tabla, salida["tabla"])
        tipo, *datos = salida["grafico"]
        if tipo == "barras":
            self.grafico.serie(*datos, self.tipo.etiqueta)
        elif tipo == "histograma":
            self.grafico.histograma(datos[0])
        else:
            self.grafico.dispersion(*datos)
        self.notificar("Prueba finalizada; interpreta el p-valor junto con las condiciones del modelo.")

    def tablas_exportables(self) -> dict:
        return {self.tipo.etiqueta: self.tabla.datos()} if self.ultimo else {}

    def resumen_exportable(self) -> str:
        return str(dpg.get_value(self.conclusion))

    def clave_teoria(self) -> str:
        return self.tipo.valor[1]

    def estado(self) -> dict:
        return {"tipo": self.tipo.valor[0], "x": texto(self.x), "y": texto(self.y),
            **{k: valor(getattr(self, k)) for k in ("alfa", "mu0", "sigma1", "sigma2", "p0", "x1", "n1", "x2", "n2")},
            "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo else self._tabla_pendiente}

    def restaurar(self, datos: dict) -> None:
        self._restaurando = True
        try:
            clave = datos.get("tipo", "z_una")
            opcion = next((v for v in self.tipo._claves.values() if v[0] == clave), self.tipo.valor)
            self.tipo.establecer(opcion)
            self._opcion()
            establecer(self.x, datos.get("x", ""))
            establecer(self.y, datos.get("y", ""))
            for k in ("alfa", "mu0", "sigma1", "sigma2", "p0", "x1", "n1", "x2", "n2"):
                if k in datos:
                    establecer(getattr(self, k), datos[k])
            self._inicial_consumido = True
            self.limpiar_resultado()
            self._tabla_pendiente = datos.get("tabla")
            if self._tabla_pendiente is None:
                dpg.set_value(self.conclusion, "Elige una técnica para ver su interpretación.")
        finally:
            self._restaurando = False
        if self._tabla_pendiente is not None:
            self.recalcular_restaurado()
