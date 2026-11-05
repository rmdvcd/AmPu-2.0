"""Explorador de distribuciones con controles nativos Dear PyGui."""

from __future__ import annotations

import secrets

import dearpygui.dearpygui as dpg
import numpy as np

from ampu.core.distribuciones import catalogo, obtener
from ampu.core.distribuciones.tabla import ResultadoDistribucion, analizar
from ampu.core.errores import ParametroInvalidoError
from ampu.ui.vistas.base import botones_accion, disposicion
from ampu.ui.widgets.comunes import KPIs, Selector, campo_semilla, establecer, habilitar, texto, valor
from ampu.ui.widgets.formulario import FormularioDistribucion
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


class VistaDistribuciones(VistaTrabajo):
    """PMF/PDF/CDF, cuantiles, tabla y exportación sin fórmulas en la UI."""

    def __init__(self, parent: int | str):
        super().__init__()
        self._valido = False
        self._restaurando = True
        _, izquierda, derecha = disposicion(
            parent, "01  /  EXPLORADOR ESTADÍSTICO", "Distribuciones",
            "Del modelo a la probabilidad: parámetros, cuantiles y visualización en un solo lugar.")
        dpg.add_text("CONFIGURA TU MODELO", parent=izquierda)
        self.buscar = dpg.add_input_text(parent=izquierda, hint="Buscar por nombre…",
                                         width=-1, callback=self._filtrar)
        self.categoria = Selector(izquierda, [("Todas las familias", "todas"),
            ("Discretas", "discretas"), ("Continuas", "continuas"),
            ("Multivariadas", "multivariadas")], callback=self._filtrar)
        self.selector = Selector(izquierda, [], callback=self._seleccionada)
        dpg.add_separator(parent=izquierda)
        dpg.add_text("PARÁMETROS", parent=izquierda)
        self.formulario = FormularioDistribucion(izquierda, cambiado=self._cambio_formulario)
        dpg.add_text("x · valor a evaluar", parent=izquierda)
        self.evento = dpg.add_input_text(parent=izquierda, default_value="5", width=-1,
                                         callback=self._cambio_evento)
        self.cuantil = dpg.add_input_double(parent=izquierda, label="Cuantil q",
            default_value=.5, min_value=0, max_value=1, format="%.5f",
            step=.05, width=-1, callback=self._marcar_entradas)
        dpg.add_text("Semilla reproducible", parent=izquierda)
        self.semilla = campo_semilla(izquierda, self._marcar_entradas)
        with dpg.group(parent=izquierda, horizontal=True):
            dpg.add_button(label="Misma semilla", callback=lambda: self.calcular())
            dpg.add_button(label="Nueva semilla", callback=self._nueva_semilla)
        self.mensaje = dpg.add_text("Parámetros listos para calcular.", parent=izquierda, wrap=285)
        self.calcular_boton = botones_accion(izquierda, "Calcular y visualizar",
                                             self.calcular, lambda: self.abrir_teoria(self.clave_teoria()))

        self.indicadores = KPIs(derecha, ["P(X=x) / f(x)", "Acumulada F(x)", "Media", "Desviación"], oscuro=self.tema_actual == "oscuro")
        self.grafico_tipo = Selector(derecha, [("Masa / densidad", "densidad"),
            ("Distribución acumulada · CDF", "cdf")], callback=self._grafico_actual, width=260)
        self.grafico = Grafico(derecha)
        dpg.add_text("TABLA DE VALORES · editable, paginada y copiable", parent=derecha)
        self.tabla = TablaDatos(derecha, modificado=lambda: self.entrada_modificada())
        self._filtrar()
        self.selector.establecer("binomial")
        self._seleccionada()
        self._restaurando = False

    def _cambio_formulario(self, *_args) -> None:
        self._validar()
        self._marcar_entradas()

    def _cambio_evento(self, *_args) -> None:
        self._validar()
        self._marcar_entradas()

    def _filtrar(self, *_args) -> None:
        previo = self.selector.valor
        busqueda = texto(self.buscar).casefold()
        modelos = [m for m in catalogo(self.categoria.valor) if busqueda in m.nombre.casefold()]
        self.selector.reemplazar([(m.nombre, m.clave) for m in modelos], previo)
        self._seleccionada()

    def _seleccionada(self, *_args) -> None:
        clave = self.selector.valor
        if clave is None:
            self._valido = False
            habilitar(self.calcular_boton, False)
            dpg.set_value(self.mensaje, "No hay distribuciones que coincidan con la búsqueda.")
            return
        modelo = obtener(clave)
        self.formulario.usar(modelo)
        if modelo.dimensionalidad != "univariante":
            x = modelo.rvs(1, seed=42)[0] if clave == "multinomial" else modelo.media()
            establecer(self.evento, ", ".join(f"{v:.5g}" for v in np.asarray(x)))
        else:
            establecer(self.evento, f"{modelo.ppf(.5):.6g}")
        self._validar()
        self._marcar_entradas()

    def _evento(self):
        try:
            if obtener(self.selector.valor).dimensionalidad == "univariante":
                return float(texto(self.evento).strip())
            return [float(a.strip()) for a in texto(self.evento).split(",")]
        except (ValueError, TypeError) as exc:
            raise ParametroInvalidoError("Escribe x como número o vector separado por comas.") from exc

    def _validar(self) -> None:
        try:
            self.formulario.valores()
            x = self._evento()
            if not np.all(np.isfinite(x)):
                raise ParametroInvalidoError("El valor x dibujado debe ser finito.")
            self._valido = True
            dpg.set_value(self.mensaje, "Parámetros listos para calcular.")
        except (ParametroInvalidoError, ValueError, KeyError) as exc:
            self._valido = False
            dpg.set_value(self.mensaje, str(exc))
        habilitar(self.calcular_boton, self._valido and not self._ocupado)

    def _nueva_semilla(self) -> None:
        establecer(self.semilla, secrets.randbelow(2_147_483_648))
        self.calcular()

    def calcular(self) -> None:
        if self._ocupado:
            return
        if not self._valido:
            self.notificar("Revisa los parámetros antes de calcular.")
            return
        try:
            clave = self.selector.valor
            parametros = self.formulario.valores()
            evento = self._evento()
        except (ParametroInvalidoError, ValueError) as exc:
            self.notificar(str(exc))
            return
        habilitar(self.calcular_boton, False)
        self.notificar(f"Calculando {obtener(clave).nombre}…")
        self.trabajar(analizar, self._recibir, self._terminar, clave, parametros,
                      evento, valor(self.cuantil), valor(self.semilla))

    def _terminar(self) -> None:
        self._validar()

    def _recibir(self, salida: ResultadoDistribucion) -> None:
        self.ultimo = salida
        r = salida.respuesta
        self.indicadores.actualizar(r["probabilidad_o_densidad"], r["acumulada"],
                                    r["media"], r["desviacion"])
        self.mostrar_tabla_restaurada(self.tabla, salida.tabla)
        self._grafico_actual()
        self.notificar(f"Modelo {self.selector.etiqueta}: {len(salida.tabla)} filas calculadas.")

    def _grafico_actual(self, *_args) -> None:
        if self.ultimo is not None:
            self.grafico.distribucion(self.ultimo, self.grafico_tipo.valor)

    def estado(self) -> dict:
        return {"clave": self.selector.valor, "categoria": self.categoria.valor,
                "parametros": self.formulario.estado(), "evento": texto(self.evento),
                "q": valor(self.cuantil), "semilla": valor(self.semilla),
                "grafico": self.grafico_tipo.valor,
                "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo is not None else self._tabla_pendiente}

    def restaurar(self, estado: dict) -> None:
        self._restaurando = True
        try:
            self.categoria.establecer(estado.get("categoria", "todas"))
            self._filtrar()
            if self.selector.valor != estado.get("clave"):
                self.categoria.establecer("todas")
                self._filtrar()
            self.selector.establecer(estado.get("clave", "binomial"))
            self._seleccionada()
            self.formulario.restaurar(estado.get("parametros", {}))
            establecer(self.evento, str(estado.get("evento", "0")))
            establecer(self.cuantil, float(estado.get("q", .5)))
            establecer(self.semilla, int(estado.get("semilla", 42)))
            self.grafico_tipo.establecer(estado.get("grafico", "densidad"))
            self._inicial_consumido = True
            self.limpiar_resultado()
            self._tabla_pendiente = estado.get("tabla")
        finally:
            self._restaurando = False
        self.recalcular_restaurado()

    def ajustar_escala(self, escala: float) -> None:
        super().ajustar_escala(escala)

    def tablas_exportables(self) -> dict:
        return {self.selector.etiqueta or "Distribución": self.tabla.datos()} if self.ultimo is not None else {}

    def resumen_exportable(self) -> str:
        if self.ultimo is None:
            return "Aún no hay resultados."
        r = self.ultimo.respuesta
        return (f"Distribución {self.selector.etiqueta}, x={texto(self.evento)}, q={valor(self.cuantil):g}. "
                f"CDF={r['acumulada']}; media={r['media']}; varianza={r['varianza']}. "
                f"Semilla {valor(self.semilla)}. "
                + ("CDF/PPF marginales para las componentes." if self.ultimo.marginal else ""))

    def clave_teoria(self) -> str:
        return self.selector.valor or "binomial"
