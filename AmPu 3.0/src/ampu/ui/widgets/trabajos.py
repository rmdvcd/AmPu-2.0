"""Ejecución de operaciones SciPy en hilos sin congelar el hilo de Qt."""

import logging
from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import QWidget

from ampu.core.errores import ErrorAmPu

REGISTRO = logging.getLogger(__name__)


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

    def trabajar(self, funcion: Callable, resultado: Callable, final: Callable | None = None, *args, **kwargs) -> bool:
        """Despacha una función; ignora clics repetidos mientras esté activa."""
        if self._ocupado:
            self.aviso.emit("Ya hay un cálculo en progreso.")
            return False
        self._ocupado = True
        tarea = Tarea(funcion, *args, **kwargs)
        self._tarea = tarea
        tarea.senales.resultado.connect(resultado)
        tarea.senales.error.connect(lambda texto: self.aviso.emit(texto))

        def terminado():
            self._ocupado = False
            self._tarea = None
            if final:
                final()

        tarea.senales.fin.connect(terminado)
        QThreadPool.globalInstance().start(tarea)
        return True
