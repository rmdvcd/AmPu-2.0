"""Análisis descriptivo con entradas multilínea Dear PyGui."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from ampu.ui.logica import _resumir_datos
from ampu.ui.vistas.base import botones_accion, disposicion
from ampu.ui.widgets.comunes import KPIs, Selector, establecer, texto
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


class VistaDescriptiva(VistaTrabajo):
    def __init__(self, parent: int | str):
        super().__init__()
        self._restaurando = True
        _, izquierda, derecha = disposicion(parent, "03  /  EXPLORACIÓN DE DATOS",
            "Estadística descriptiva", "Pega observaciones, explora su dispersión y exporta frecuencias sin perder datos.")
        dpg.add_text("DATOS · VARIABLE X", parent=izquierda)
        dpg.add_text("Comas, espacios o saltos; usa punto decimal.", parent=izquierda, wrap=285)
        self.x = dpg.add_input_text(parent=izquierda, multiline=True, width=-1, height=145,
            default_value="12, 15, 18, 21, 18, 20, 23, 22, 17, 19, 16, 24, 21, 18",
            callback=self._marcar_entradas)
        dpg.add_text("VARIABLE Y · OPCIONAL", parent=izquierda)
        self.y = dpg.add_input_text(parent=izquierda, multiline=True, width=-1, height=85,
                                    hint="Parejas para dispersión y correlación",
                                    callback=self._marcar_entradas)
        dpg.add_text("VISUALIZACIÓN", parent=izquierda)
        self.modo = Selector(izquierda, ["Histograma", "Boxplot", "Dispersión"], callback=self._dibujar)
        self.boton = botones_accion(izquierda, "Analizar datos", self.calcular,
                                    lambda: self.abrir_teoria("descriptiva"))
        self.indicadores = KPIs(derecha, ["Media", "Mediana", "Desv. muestral", "CV"], oscuro=self.tema_actual == "oscuro")
        self.nota = dpg.add_text("La varianza se calcula con denominador n − 1.",
                                 parent=derecha, wrap=800)
        dpg.add_text("PERFIL DE LA MUESTRA", parent=derecha)
        self.grafico = Grafico(derecha)
        self.hojas = Selector(derecha, [], callback=self._tabla, width=260)
        self.tabla = TablaDatos(derecha, modificado=lambda: self.entrada_modificada())
        self._restaurando = False

    def calcular(self) -> None:
        if self._ocupado:
            return
        self.trabajar(_resumir_datos, self._recibir, lambda: None,
                      texto(self.x), texto(self.y))
        self.notificar("Calculando resumen, frecuencias y correlación…")

    def _recibir(self, resultado) -> None:
        self.ultimo = resultado
        resumen, corr, tablas, _x, _y = resultado
        self.indicadores.actualizar(resumen.media, resumen.mediana, resumen.desviacion,
            resumen.coeficiente_variacion if resumen.coeficiente_variacion is not None else float("nan"))
        dpg.set_value(self.nota, f"{resumen.n} observaciones · cuartiles {resumen.q1:g} y {resumen.q3:g}"
                      + (f" · Pearson r = {corr:.4g}" if corr is not None else " · agrega Y para un diagrama de dispersión."))
        self.iniciar_hojas(tablas)
        self.hojas.reemplazar([(nombre, nombre) for nombre in tablas], self._hoja_pendiente)
        self._hoja_pendiente = None
        self._tabla()
        self._dibujar()
        self.notificar(f"{resumen.n} observaciones analizadas y disponibles para exportar.")

    def _tabla(self, *_args) -> None:
        if self.ultimo:
            self.mostrar_hoja(self.tabla, self.hojas.etiqueta)

    def _dibujar(self, *_args) -> None:
        if self.ultimo:
            modo = self.modo.valor
            x, y = self.ultimo[3:5]
            if modo == "Dispersión" and y is None:
                modo = "Histograma"
            self.grafico.histograma(x, modo, y)

    def tablas_exportables(self) -> dict:
        return self.hojas_exportables(self.tabla) if self.ultimo else {}

    def resumen_exportable(self) -> str:
        if not self.ultimo:
            return "Sin resultados."
        r = self.ultimo[0]
        return (f"n={r.n}, media={r.media:.6g}, mediana={r.mediana:.6g}, "
                f"s={r.desviacion:.6g}, CV={r.coeficiente_variacion}. " + str(dpg.get_value(self.nota)))

    def clave_teoria(self) -> str:
        return "descriptiva"

    def estado(self) -> dict:
        tablas = ({k: v.to_dict(orient="list") for k, v in self.tablas_exportables().items()}
                  if self.ultimo else self._hojas_pendientes)
        return {"x": texto(self.x), "y": texto(self.y), "modo": self.modo.valor,
                "hoja": self.hojas.etiqueta or self._hoja_pendiente, "tablas": tablas}

    def restaurar(self, datos: dict) -> None:
        self._restaurando = True
        try:
            establecer(self.x, datos.get("x", ""))
            establecer(self.y, datos.get("y", ""))
            self.modo.establecer(datos.get("modo", "Histograma"))
            self._inicial_consumido = True
            self.limpiar_resultado()
            self._hojas_pendientes = datos.get("tablas") if isinstance(datos.get("tablas"), dict) else {}
            self._hoja_pendiente = datos.get("hoja")
        finally:
            self._restaurando = False
        self.recalcular_restaurado()
