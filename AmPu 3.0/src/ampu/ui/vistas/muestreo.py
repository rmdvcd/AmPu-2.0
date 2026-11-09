"""Diseños muestrales reproducibles en una vista Dear PyGui."""

from __future__ import annotations

import secrets

import dearpygui.dearpygui as dpg

from ampu.core.muestreo.diseno import ResultadoDiseno, ejecutar_diseno
from ampu.ui.entradas import filas_estratos
from ampu.ui.vistas.base import botones_accion, disposicion
from ampu.ui.widgets.comunes import Selector, campo_semilla, establecer, texto, valor, visible
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo

METODOS = [("Aleatorio simple · finito", "finito"),
    ("Aleatorio · con reemplazo", "infinito"), ("Sistemático", "sistematico"),
    ("Estratificado proporcional", "proporcional"), ("Estratificado Neyman", "neyman"),
    ("Estratificado óptimo", "optimo"), ("Por conglomerados", "conglomerados")]


class VistaMuestreo(VistaTrabajo):
    def __init__(self, parent: int | str):
        super().__init__()
        self.tema_actual = "claro"
        self._restaurando = True
        _, izquierda, derecha = disposicion(parent, "02  /  DISEÑO MUESTRAL", "Muestreo",
            "Planea el tamaño, elige unidades y reproduce cualquier sorteo con una semilla.")
        dpg.add_text("TIPO DE SELECCIÓN", parent=izquierda)
        self.metodo = Selector(izquierda, METODOS, callback=self._metodo_cambiado)
        self.N = dpg.add_input_int(parent=izquierda, label="Población N", default_value=400,
            min_value=1, max_value=1_000_000, width=-1, callback=self._marcar_entradas)
        self.n = dpg.add_input_int(parent=izquierda, label="Tamaño n", default_value=40,
            min_value=1, max_value=1_000_000, width=-1, callback=self._marcar_entradas)
        self.auto = dpg.add_checkbox(parent=izquierda, label="Calcular n a partir del margen",
                                     callback=self._marcar_entradas)
        self.confianza = dpg.add_input_double(parent=izquierda, label="Confianza", default_value=.95,
            min_value=.00001, max_value=.99999, format="%.5f", width=-1, callback=self._marcar_entradas)
        self.p = dpg.add_input_double(parent=izquierda, label="Proporción", default_value=.5,
            min_value=.00001, max_value=.99999, format="%.5f", width=-1, callback=self._marcar_entradas)
        self.error = dpg.add_input_double(parent=izquierda, label="Error d", default_value=.05,
            min_value=.00001, max_value=.99999, format="%.5f", width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_estratos:
            dpg.add_text("ESTRATOS / CONGLOMERADOS")
            dpg.add_text("Una fila: nombre, Nh, desviación, coste", wrap=285)
            self.estratos = dpg.add_input_text(multiline=True, width=-1, height=90,
                default_value="Norte,120,8,1\nCentro,200,5,2\nSur,80,10,1",
                callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_ids:
            dpg.add_text("IDENTIFICADORES OPCIONALES")
            self.poblacion = dpg.add_input_text(hint="ID-1, ID-2, … (N elementos)",
                                                width=-1, callback=self._marcar_entradas)
        with dpg.group(parent=izquierda) as self.grupo_por_grupo:
            self.por_grupo = dpg.add_input_int(label="Unidades por conglomerado (0 = completo)",
                default_value=0, min_value=0, max_value=1_000_000, width=-1,
                callback=self._marcar_entradas)
        dpg.add_text("Semilla reproducible", parent=izquierda)
        self.semilla = campo_semilla(izquierda, self._marcar_entradas)
        with dpg.group(parent=izquierda, horizontal=True):
            dpg.add_button(label="Misma", callback=lambda: self.calcular())
            dpg.add_button(label="Nueva semilla", callback=self._nueva)
        self.boton = botones_accion(izquierda, "Diseñar y seleccionar", self.calcular,
                                    lambda: self.abrir_teoria(self.clave_teoria()))
        self.resumen = dpg.add_text("Configura el diseño y pulsa «Diseñar y seleccionar».",
                                    parent=derecha, wrap=800)
        dpg.add_text("POBLACIÓN Y MUESTRA", parent=derecha)
        self.grafico = Grafico(derecha)
        self.hojas = Selector(derecha, [], callback=self._mostrar_tabla, width=260)
        self.tabla = TablaDatos(derecha, modificado=lambda: self.entrada_modificada())
        self._metodo_cambiado()
        self._restaurando = False

    def _metodo_cambiado(self, *_args) -> None:
        clave = self.metodo.valor
        estratificado = clave in ("proporcional", "neyman", "optimo", "conglomerados")
        visible(self.grupo_estratos, estratificado)
        visible(self.grupo_ids, not estratificado)
        visible(self.grupo_por_grupo, clave == "conglomerados")
        if clave == "conglomerados" and valor(self.n) > 2:
            establecer(self.n, 2)
        self._marcar_entradas()

    def _nueva(self) -> None:
        establecer(self.semilla, secrets.randbelow(2_147_483_648))
        self.calcular()

    def calcular(self) -> None:
        if self._ocupado:
            return
        try:
            clave = self.metodo.valor
            estratos = filas_estratos(texto(self.estratos)) if clave in (
                "proporcional", "neyman", "optimo", "conglomerados") else None
            ids = ([v.strip() for v in texto(self.poblacion).split(",") if v.strip()]
                   if texto(self.poblacion).strip() else None)
        except ValueError as exc:
            self.notificar(str(exc))
            return
        self.trabajar(ejecutar_diseno, self._recibir, lambda: None,
                      clave, valor(self.N), valor(self.n), valor(self.semilla), estratos,
                      valor(self.auto), valor(self.p), valor(self.error), valor(self.confianza),
                      ids, valor(self.por_grupo) or None)
        self.notificar("Seleccionando unidades con semilla reproducible…")

    def _recibir(self, salida: ResultadoDiseno) -> None:
        self.ultimo = salida
        dpg.set_value(self.resumen, salida.resumen)
        self.grafico.barras(salida.etiquetas, salida.poblacion, salida.seleccion)
        self.iniciar_hojas(salida.tablas)
        preferida = self._hoja_pendiente if self._hoja_pendiente in salida.tablas else "Selección"
        self.hojas.reemplazar([(nombre, nombre) for nombre in salida.tablas], preferida)
        self._hoja_pendiente = None
        self._mostrar_tabla()
        self.notificar(f"Muestreo completado · {salida.resumen}")

    def _mostrar_tabla(self, *_args) -> None:
        if self.ultimo is not None:
            self.mostrar_hoja(self.tabla, self.hojas.etiqueta)

    def tablas_exportables(self) -> dict:
        return self.hojas_exportables(self.tabla) if self.ultimo is not None else {}

    def resumen_exportable(self) -> str:
        return self.ultimo.resumen if self.ultimo else "Sin diseño aún."

    def clave_teoria(self) -> str:
        return {"finito": "muestreo_finito", "infinito": "muestreo_infinito",
            "sistematico": "muestreo_sistematico", "proporcional": "muestreo_estratificado",
            "neyman": "muestreo_neyman", "optimo": "muestreo_optimo",
            "conglomerados": "muestreo_conglomerados"}[self.metodo.valor]

    def estado(self) -> dict:
        tablas = ({k: v.to_dict(orient="list") for k, v in self.tablas_exportables().items()}
                  if self.ultimo else self._hojas_pendientes)
        return {"metodo": self.metodo.valor, "N": valor(self.N), "n": valor(self.n),
            "semilla": valor(self.semilla), "estratos": texto(self.estratos),
            "poblacion": texto(self.poblacion), "n_por_grupo": valor(self.por_grupo),
            "auto": valor(self.auto), "p": valor(self.p), "error": valor(self.error),
            "confianza": valor(self.confianza), "hoja": self.hojas.etiqueta or self._hoja_pendiente,
            "tablas": tablas}

    def restaurar(self, datos: dict) -> None:
        self._restaurando = True
        try:
            self.metodo.establecer(datos.get("metodo", "finito"))
            self._metodo_cambiado()
            for campo, clave in (("N", "N"), ("n", "n"), ("semilla", "semilla"),
                                 ("por_grupo", "n_por_grupo")):
                if clave in datos and datos[clave] is not None:
                    establecer(getattr(self, campo), int(datos[clave]))
            establecer(self.estratos, datos.get("estratos", ""))
            establecer(self.poblacion, datos.get("poblacion", ""))
            for campo in ("p", "error", "confianza"):
                establecer(getattr(self, campo), float(datos.get(campo, valor(getattr(self, campo)))))
            establecer(self.auto, bool(datos.get("auto", False)))
            self._inicial_consumido = True
            self.limpiar_resultado()
            self._hojas_pendientes = datos.get("tablas") if isinstance(datos.get("tablas"), dict) else {}
            self._hoja_pendiente = datos.get("hoja")
        finally:
            self._restaurando = False
        self.recalcular_restaurado()
