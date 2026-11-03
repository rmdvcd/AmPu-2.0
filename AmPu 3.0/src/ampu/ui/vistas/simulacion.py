"""Monte Carlo, muestras, ajuste y QQ-plot en Dear PyGui."""

from __future__ import annotations

import secrets

import dearpygui.dearpygui as dpg

from ampu.core.distribuciones import catalogo, obtener
from ampu.core.errores import ParametroInvalidoError
from ampu.core.simulacion.montecarlo import familias_ajustables
from ampu.ui.logica import _simular
from ampu.ui.vistas.base import botones_accion, disposicion
from ampu.ui.widgets.comunes import Selector, campo_semilla, establecer, habilitar, texto, valor
from ampu.ui.widgets.formulario import FormularioDistribucion
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo

EXPERIMENTOS = [("Estimar π", "pi"), ("Integral de x² en [0,1]", "integral"),
    ("Generar muestra", "muestra"), ("Ajustar distribución", "ajuste"),
    ("QQ-plot de datos", "qq")]


class VistaSimulacion(VistaTrabajo):
    def __init__(self, parent: int | str):
        super().__init__()
        self._restaurando = True
        _, izquierda, derecha = disposicion(parent, "06  /  EXPERIMENTAR Y COMPARAR",
            "Simulación y ajuste", "Repite el experimento, compara modelos con datos y comunica incertidumbre.")
        dpg.add_text("EXPERIMENTO", parent=izquierda)
        self.tipo = Selector(izquierda, EXPERIMENTOS, callback=self._tipo)
        self.n = dpg.add_input_int(parent=izquierda, label="Simulaciones n", default_value=10_000,
            min_value=2, max_value=1_000_000, width=-1, callback=self._marcar_entradas)
        dpg.add_text("Semilla", parent=izquierda)
        self.semilla = campo_semilla(izquierda, self._marcar_entradas)
        with dpg.group(parent=izquierda, horizontal=True):
            dpg.add_button(label="Misma", callback=lambda: self.calcular())
            dpg.add_button(label="Nueva semilla", callback=self._nueva)
        dpg.add_text("DISTRIBUCIÓN", parent=izquierda)
        self.modelo = Selector(izquierda, [], callback=self._cambiar_modelo)
        self.formulario = FormularioDistribucion(izquierda, cambiado=self._marcar_entradas)
        dpg.add_text("DATOS PARA AJUSTE / QQ-PLOT", parent=izquierda)
        self.datos = dpg.add_input_text(parent=izquierda, multiline=True, width=-1, height=85,
            default_value="1.2, 2.0, 0.4, 1.1, 0.7, 2.5, 1.3, 0.9, 1.8, 2.1, 1.5, 0.6",
            callback=self._marcar_entradas)
        self.boton = botones_accion(izquierda, "Ejecutar experimento", self.calcular,
                                    lambda: self.abrir_teoria(self.clave_teoria()))
        self.resumen = dpg.add_text("Selecciona un experimento y ejecútalo con una semilla reproducible.",
                                    parent=derecha, wrap=800)
        dpg.add_text("EXPERIMENTO VISUAL", parent=derecha)
        self.grafico = Grafico(derecha)
        dpg.add_text("RESULTADOS Y DATOS REPRODUCIBLES", parent=derecha)
        self.tabla = TablaDatos(derecha, modificado=lambda: self.entrada_modificada())
        self._tipo()
        self._restaurando = False

    def _tipo(self, *_args) -> None:
        tipo = self.tipo.valor
        previo = self.modelo.valor
        modelos = [d for d in catalogo() if d.dimensionalidad == "univariante"]
        if tipo == "ajuste":
            modelos = [d for d in modelos if d.clave in familias_ajustables()]
        self.modelo.reemplazar([(d.nombre, d.clave) for d in modelos], previo or "normal")
        self._cambiar_modelo()
        self.modelo.habilitar(tipo in ("muestra", "ajuste", "qq"))
        self.formulario.habilitar(tipo in ("muestra", "qq"))
        habilitar(self.datos, tipo in ("ajuste", "qq"))
        habilitar(self.n, tipo in ("pi", "integral", "muestra"))
        self._marcar_entradas()

    def _cambiar_modelo(self, *_args) -> None:
        if self.modelo.valor:
            self.formulario.usar(obtener(self.modelo.valor))
        self._marcar_entradas()

    def _nueva(self) -> None:
        establecer(self.semilla, secrets.randbelow(2_147_483_648))
        self.calcular()

    def calcular(self) -> None:
        if self._ocupado:
            return
        try:
            params = self.formulario.valores() if self.tipo.valor in ("muestra", "qq") else {}
        except (ParametroInvalidoError, ValueError) as exc:
            self.notificar(str(exc))
            return
        self.trabajar(_simular, self._recibir, lambda: None, self.tipo.valor,
                      self.modelo.valor, params, valor(self.n), valor(self.semilla), texto(self.datos))
        self.notificar("Ejecutando simulación en segundo plano…")

    def _recibir(self, salida: dict) -> None:
        self.ultimo = salida
        dpg.set_value(self.resumen, salida["resumen"])
        self.mostrar_tabla_restaurada(self.tabla, salida["tabla"])
        tipo, *datos = salida["grafico"]
        if tipo == "pi":
            self.grafico.puntos_pi(*datos)
        elif tipo == "barras":
            self.grafico.serie(*datos, "Estimación Monte Carlo")
        elif tipo == "histograma":
            self.grafico.histograma(datos[0])
        elif tipo == "ajuste":
            self.grafico.comparar(*datos)
        else:
            self.grafico.qq(*datos)
        self.notificar("Experimento terminado; usa la misma semilla para reproducirlo.")

    def tablas_exportables(self) -> dict:
        return {self.tipo.etiqueta: self.tabla.datos()} if self.ultimo else {}

    def resumen_exportable(self) -> str:
        return str(dpg.get_value(self.resumen))

    def clave_teoria(self) -> str:
        return {"pi": "montecarlo", "integral": "montecarlo",
                "muestra": self.modelo.valor or "normal",
                "ajuste": "ajuste_distribuciones", "qq": "qq_plot"}[self.tipo.valor]

    def estado(self) -> dict:
        return {"tipo": self.tipo.valor, "modelo": self.modelo.valor,
            "parametros": self.formulario.estado() if self.modelo.valor else {},
            "n": valor(self.n), "semilla": valor(self.semilla), "datos": texto(self.datos),
            "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo else self._tabla_pendiente}

    def restaurar(self, datos: dict) -> None:
        self._restaurando = True
        try:
            self.tipo.establecer(datos.get("tipo", "pi"))
            self._tipo()
            self.modelo.establecer(datos.get("modelo", "normal"))
            self._cambiar_modelo()
            self.formulario.restaurar(datos.get("parametros", {}))
            establecer(self.n, int(datos.get("n", 10_000)))
            establecer(self.semilla, int(datos.get("semilla", 42)))
            establecer(self.datos, datos.get("datos", ""))
            self._inicial_consumido = True
            self.limpiar_resultado()
            self._tabla_pendiente = datos.get("tabla")
            if self._tabla_pendiente is None:
                dpg.set_value(self.resumen, "Selecciona un experimento y ejecútalo con una semilla reproducible.")
        finally:
            self._restaurando = False
        if self._tabla_pendiente is not None:
            self.recalcular_restaurado()
