"""Ejecución de operaciones SciPy en hilos sin congelar el hilo de Qt."""

import logging
from collections.abc import Callable

import pandas as pd
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot
from PySide6.QtWidgets import QWidget

from ampu.ui.widgets.tabla import TablaDatos

from ampu.core.errores import ErrorAmPu

REGISTRO = logging.getLogger(__name__)


def tabla_de_sesion(datos: object, original: pd.DataFrame) -> pd.DataFrame:
    """Recupera anotaciones de una tabla sin alterar el resultado calculado.

    Las columnas deben coincidir; las filas pueden variar por pegado/ordenamiento.
    Un esquema ajeno o excesivamente grande no sustituye a la tabla del motor.
    """
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


class Senales(QObject):
    """Notificaciones encoladas para transferir valores al hilo de la UI."""

    resultado = Signal(object)
    error = Signal(str)
    fin = Signal()


class Tarea(QRunnable):
    """Encapsula una única función pura/IO; no toca ningún QWidget."""

    def __init__(self, funcion: Callable, *args, **kwargs):
        """Conserva argumentos hasta que el ejecutor haya terminado."""
        super().__init__()
        self.funcion, self.args, self.kwargs = funcion, args, kwargs
        self.senales = Senales()

    @Slot()
    def run(self):
        """Emite resultado, excepción de dominio o mensaje protegido."""
        try:
            self.senales.resultado.emit(self.funcion(*self.args, **self.kwargs))
        except ErrorAmPu as exc:
            REGISTRO.warning("Entrada no válida: %s", exc)
            self.senales.error.emit(str(exc))
        except Exception:
            REGISTRO.exception("Fallo inesperado en cálculo asíncrono")
            self.senales.error.emit("No se pudo completar la operación. Revisa los datos o consulta el registro de errores.")
        finally:
            self.senales.fin.emit()


class VistaTrabajo(QWidget):
    """Clase base que gestiona un solo cálculo activo y su fin."""

    aviso = Signal(str)
    abrir_teoria = Signal(str)

    def __init__(self, parent=None):
        """Vincula la vista al grupo de hilos global Qt."""
        super().__init__(parent)
        self._tarea: Tarea | None = None
        self._ocupado = False
        self._revision = 0
        self._recalculo_pendiente = False
        self._tabla_pendiente: object = None
        self._hojas_pendientes: dict = {}
        self._hoja_pendiente: str | None = None
        self._hojas_editadas: dict[str, pd.DataFrame] = {}
        self._hoja_visible: str | None = None
        self._inicial: QTimer | None = None

    def calcular_inicial(self, milisegundos: int):
        """Programa el primer cálculo, cancelable si una sesión se abre antes."""
        self._inicial = QTimer(self)
        self._inicial.setSingleShot(True)
        self._inicial.timeout.connect(self.calcular)
        self._inicial.start(milisegundos)

    def recalcular_restaurado(self):
        """Descarta trabajos previos y recalcula incluso si el hilo aún está ocupado."""
        if self._inicial is not None:
            self._inicial.stop()
        self._revision += 1
        self._recalculo_pendiente = True
        self._continuar_restauracion()

    def _continuar_restauracion(self):
        if self._recalculo_pendiente and not self._ocupado:
            self._recalculo_pendiente = False
            QTimer.singleShot(0, self.calcular)

    def limpiar_resultado(self):
        """Restaura una vista guardada sin cálculo; ignora cualquier trabajo anterior."""
        if self._inicial is not None:
            self._inicial.stop()
        self._revision += 1
        self._recalculo_pendiente = False
        self._tabla_pendiente = None
        self._hojas_pendientes = {}
        self._hojas_editadas = {}
        self._hoja_visible = None
        self.ultimo = None
        if hasattr(self, "hojas"):
            self.hojas.clear()
        self.tabla.mostrar(pd.DataFrame())
        self.grafico.vacio()
        for atributo in ("conclusion", "resumen"):
            if hasattr(self, atributo):
                getattr(self, atributo).setText("Aún no hay resultados.")
        if hasattr(self, "indicadores"):
            for etiqueta in self.indicadores.valores:
                etiqueta.setText("—")
                etiqueta.setToolTip("")

    def mostrar_tabla_restaurada(self, widget: TablaDatos, original: pd.DataFrame):
        """Reproduce el cálculo y recupera exclusivamente las ediciones visibles."""
        widget.mostrar(tabla_de_sesion(self._tabla_pendiente, original))
        self._tabla_pendiente = None

    def iniciar_hojas(self, originales: dict[str, pd.DataFrame]):
        """Inicia el conjunto de hojas sin perder ediciones previas de otras pestañas."""
        self._hojas_editadas = {k: tabla_de_sesion(self._hojas_pendientes.get(k), v)
                                for k, v in originales.items()}
        self._hojas_pendientes = {}
        self._hoja_visible = None

    def mostrar_hoja(self, widget: TablaDatos, nombre: str):
        """Guarda la hoja saliente y muestra la nueva, conservando ediciones."""
        self._guardar_hoja(widget)
        if nombre in self._hojas_editadas:
            widget.mostrar(self._hojas_editadas[nombre])
            self._hoja_visible = nombre

    def _guardar_hoja(self, widget: TablaDatos):
        if self._hoja_visible in self._hojas_editadas:
            self._hojas_editadas[self._hoja_visible] = widget.datos()

    def hojas_exportables(self, widget: TablaDatos) -> dict[str, pd.DataFrame]:
        """Entrega todas las hojas tal como quedaron, no las tablas sin editar."""
        self._guardar_hoja(widget)
        return dict(self._hojas_editadas)

    def trabajar(self, funcion: Callable, resultado: Callable, final: Callable | None = None, *args, **kwargs) -> bool:
        """Despacha una función; ignora clics repetidos mientras esté activa."""
        if self._ocupado:
            self.aviso.emit("Ya hay un cálculo en progreso.")
            return False
        self._ocupado = True
        revision = self._revision
        tarea = Tarea(funcion, *args, **kwargs)
        self._tarea = tarea
        tarea.senales.resultado.connect(lambda valor: resultado(valor) if revision == self._revision else None)
        tarea.senales.error.connect(lambda texto: self.aviso.emit(texto) if revision == self._revision else None)

        def terminado():
            self._ocupado = False
            self._tarea = None
            if final:
                final()
            self._continuar_restauracion()

        tarea.senales.fin.connect(terminado)
        QThreadPool.globalInstance().start(tarea)
        return True
