"""Trabajos en segundo plano con publicación segura en el hilo Dear PyGui."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

import dearpygui.dearpygui as dpg
import pandas as pd

from ampu.core.errores import ErrorAmPu
from ampu.ui.widgets.comunes import habilitar
from ampu.ui.widgets.tabla import TablaDatos

REGISTRO = logging.getLogger(__name__)
EJECUTOR = ThreadPoolExecutor(max_workers=min(4, (os.cpu_count() or 2) + 1),
                              thread_name_prefix="ampu-calculo")


def tabla_de_sesion(datos: object, original: pd.DataFrame) -> pd.DataFrame:
    """Recupera anotaciones solo si el esquema corresponde al resultado recalculado."""
    if not isinstance(datos, dict):
        return original
    try:
        tabla = pd.DataFrame(datos)
    except (TypeError, ValueError):
        return original
    if list(tabla.columns) != list(map(str, original.columns)) or len(tabla) > 100_000:
        REGISTRO.warning("Se ignoró una tabla de sesión con columnas o tamaño incompatibles")
        return original
    return tabla


class VistaTrabajo:
    """Base no gráfica: un trabajo activo, revisión y restauración cancelable."""

    def __init__(self):
        self.ultimo = None
        self._futuro: Future | None = None
        self._ocupado = False
        self._revision = 0
        self._recalculo_pendiente = False
        self._tabla_pendiente: object = None
        self._hojas_pendientes: dict = {}
        self._hoja_pendiente: str | None = None
        self._hojas_editadas: dict[str, pd.DataFrame] = {}
        self._hoja_visible: str | None = None
        self._desactualizado = False
        self._cambio_durante_calculo = False
        self._restaurando = False
        self._inicial_consumido = False
        self.aviso: Callable[[str], None] = lambda _texto: None
        self.estado_cambiado: Callable[[], None] = lambda: None
        self.entrada_modificada: Callable[[], None] = lambda: None
        self.trabajo_finalizado: Callable[[], None] = lambda: None
        self.abrir_teoria: Callable[[str], None] = lambda _clave: None

    def notificar(self, texto: str) -> None:
        self.aviso(texto)

    def _marcar_entradas(self, *_args) -> None:
        if self._restaurando:
            return
        self.entrada_modificada()
        if self._ocupado:
            self._cambio_durante_calculo = True
        if self.ultimo is not None and not self._desactualizado:
            self._desactualizado = True
            self.estado_cambiado()
            self.notificar("Entradas modificadas: recalcula antes de exportar. El gráfico anterior es de referencia.")

    def calcular_inicial(self) -> None:
        """Calcula al abrir el módulo por primera vez, no todas las vistas al arrancar."""
        if not self._inicial_consumido:
            self._inicial_consumido = True
            self.calcular()

    def recalcular_restaurado(self) -> None:
        self._revision += 1
        self._recalculo_pendiente = True
        self._continuar_restauracion()

    def _continuar_restauracion(self) -> None:
        if self._recalculo_pendiente and not self._ocupado:
            self._recalculo_pendiente = False
            self.calcular()

    def limpiar_resultado(self) -> None:
        self._revision += 1
        self._recalculo_pendiente = False
        self._desactualizado = False
        self._cambio_durante_calculo = False
        self._tabla_pendiente = None
        self._hojas_pendientes = {}
        self._hojas_editadas = {}
        self._hoja_visible = None
        self.ultimo = None
        if hasattr(self, "hojas"):
            self.hojas.reemplazar([])
        self.tabla.mostrar(pd.DataFrame())
        self.grafico.vacio()
        self.estado_cambiado()
        for atributo in ("conclusion", "resumen", "nota", "mensaje"):
            if hasattr(self, atributo):
                control = getattr(self, atributo)
                if isinstance(control, (str, int)):
                    dpg.set_value(control, "Aún no hay resultados.")
        if hasattr(self, "indicadores"):
            self.indicadores.limpiar()

    def mostrar_tabla_restaurada(self, widget: TablaDatos, original: pd.DataFrame) -> None:
        widget.mostrar(tabla_de_sesion(self._tabla_pendiente, original))
        self._tabla_pendiente = None

    def iniciar_hojas(self, originales: dict[str, pd.DataFrame]) -> None:
        self.tabla.reiniciar_historial()
        self._hojas_editadas = {k: tabla_de_sesion(self._hojas_pendientes.get(k), v)
                                for k, v in originales.items()}
        self._hojas_pendientes = {}
        self._hoja_visible = None

    def mostrar_hoja(self, widget: TablaDatos, nombre: str) -> None:
        self._guardar_hoja(widget)
        if nombre in self._hojas_editadas:
            widget.mostrar(self._hojas_editadas[nombre], identificador=nombre)
            self._hoja_visible = nombre

    def _guardar_hoja(self, widget: TablaDatos) -> None:
        if self._hoja_visible in self._hojas_editadas:
            self._hojas_editadas[self._hoja_visible] = widget.datos()

    def hojas_exportables(self, widget: TablaDatos) -> dict[str, pd.DataFrame]:
        self._guardar_hoja(widget)
        return dict(self._hojas_editadas)

    def trabajar(self, funcion: Callable, resultado: Callable,
                 final: Callable | None = None, *args, **kwargs) -> bool:
        """Envía una función pura; ``procesar`` publica su Future en la UI."""
        if self._ocupado:
            self.notificar("Ya hay un cálculo en progreso.")
            return False
        self._ocupado = True
        self._cambio_durante_calculo = False
        revision = self._revision
        self._futuro = EJECUTOR.submit(funcion, *args, **kwargs)
        self._resultado_callback = resultado
        self._final_callback = final
        self._revision_futuro = revision
        return True

    def procesar(self) -> bool:
        """Aplica como máximo un Future terminado; llamar solo desde el hilo gráfico."""
        futuro = self._futuro
        if futuro is None or not futuro.done():
            return False
        self._futuro = None
        self._ocupado = False
        revision_valida = self._revision_futuro == self._revision
        try:
            salida = futuro.result()
        except ErrorAmPu as exc:
            REGISTRO.warning("Entrada no válida: %s", exc)
            if revision_valida:
                self.notificar(str(exc))
        except Exception:
            REGISTRO.exception("Fallo inesperado en cálculo asíncrono")
            if revision_valida:
                self.notificar("No se pudo completar la operación. Revisa los datos o consulta el registro de errores.")
        else:
            if revision_valida:
                self._resultado_callback(salida)
                self._desactualizado = self._cambio_durante_calculo
                self.estado_cambiado()
                if self._desactualizado:
                    self.notificar("El cálculo corresponde a entradas anteriores; recalcula para exportar.")
        finally:
            if self._final_callback is not None:
                self._final_callback()
            self._continuar_restauracion()
            self.trabajo_finalizado()
        return True

    def ajustar_escala(self, escala: float) -> None:
        if hasattr(self, "grafico"):
            self.grafico.escalar_texto(escala)

    def esperar(self, limite: float = 15.0) -> bool:
        """Espera cooperativa para autopruebas, sin renderizar ni abrir viewport."""
        import time
        vencimiento = time.monotonic() + limite
        while time.monotonic() < vencimiento:
            self.procesar()
            if not self._ocupado and not self._recalculo_pendiente:
                return True
            time.sleep(.005)
        return False
