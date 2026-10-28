"""Ejecución de operaciones SciPy en hilos sin congelar el hilo de Qt."""

import logging
from collections.abc import Callable

import pandas as pd
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot
from PySide6.QtWidgets import (QAbstractSpinBox, QBoxLayout, QCheckBox, QComboBox,
                               QLineEdit, QPlainTextEdit, QWidget)

from ampu.ui.widgets.comunes import KPIs
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

    def _emitir(self, nombre: str, *argumentos):
        """Al cerrar la aplicación, una señal Qt puede haberse destruido."""
        try:
            getattr(self.senales, nombre).emit(*argumentos)
        except RuntimeError:
            REGISTRO.debug("Se ignoró %s de una tarea al cerrar la interfaz", nombre)

    @Slot()
    def run(self):
        """Emite resultado, excepción de dominio o mensaje protegido."""
        try:
            valor = self.funcion(*self.args, **self.kwargs)
        except ErrorAmPu as exc:
            REGISTRO.warning("Entrada no válida: %s", exc)
            self._emitir("error", str(exc))
        except Exception:
            REGISTRO.exception("Fallo inesperado en cálculo asíncrono")
            self._emitir("error", "No se pudo completar la operación. Revisa los datos o consulta el registro de errores.")
        else:
            self._emitir("resultado", valor)
        finally:
            self._emitir("fin")


class VistaTrabajo(QWidget):
    """Clase base que gestiona un solo cálculo activo y su fin."""

    aviso = Signal(str)
    estado_cambiado = Signal()
    entrada_modificada = Signal()
    trabajo_finalizado = Signal()
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
        self._cuerpo_adaptable: QBoxLayout | None = None
        self._form_adaptable: QWidget | None = None
        self._escala_interfaz = 1.0
        self._desactualizado = False
        self._cambio_durante_calculo = False

    def vigilar_entradas(self):
        """Si se editan entradas, no exportar el resultado anterior como si fuera nuevo."""
        excluidos = {getattr(self, clave) for clave in ("hojas", "grafico_tipo", "modo", "buscar")
                     if hasattr(self, clave)}
        for widget in self.findChildren(QWidget):
            if widget in excluidos:
                continue  # Cambiar hoja o representación redibuja el mismo resultado.
            senal = None
            if isinstance(widget, (QLineEdit, QPlainTextEdit)):
                senal = widget.textChanged
            elif isinstance(widget, QComboBox):
                senal = widget.currentIndexChanged
            elif isinstance(widget, QCheckBox):
                senal = widget.toggled
            elif isinstance(widget, QAbstractSpinBox):
                senal = widget.valueChanged if hasattr(widget, "valueChanged") else widget.editingFinished
            if senal is not None:
                senal.connect(self._marcar_entradas)
        if hasattr(self, "formulario") and hasattr(self.formulario, "cambiado"):
            self.formulario.cambiado.connect(self._marcar_entradas)  # campos dinámicos.

    def _marcar_entradas(self, *_):
        self.entrada_modificada.emit()
        if self._ocupado:
            self._cambio_durante_calculo = True
        if self.ultimo is not None and not self._desactualizado:
            self._desactualizado = True
            self.estado_cambiado.emit()
            self.aviso.emit("Entradas modificadas: recalcula antes de exportar. El gráfico anterior es de referencia.")

    def configurar_adaptacion(self, cuerpo: QBoxLayout, formulario: QWidget):
        """Refluye formulario/resultados en pantallas pequeñas o texto ampliado."""
        self._cuerpo_adaptable = cuerpo
        self._form_adaptable = formulario
        self._ajustar_diseno()

    def ajustar_escala(self, escala: float):
        self._escala_interfaz = escala
        margen = (10, 10, 10, 10) if escala >= 1.4 else (25, 24, 25, 22)
        self.layout().setContentsMargins(*margen)
        if hasattr(self, "formulario") and hasattr(self.formulario, "ajustar_escala"):
            self.formulario.ajustar_escala(escala)
        self._ajustar_diseno()
        for indicadores in self.findChildren(KPIs):
            indicadores.ajustar_escala(escala)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self._ajustar_diseno()

    def _ajustar_diseno(self):
        if self._cuerpo_adaptable is None or self._form_adaptable is None:
            return
        compacto = self.width() < 900 or self._escala_interfaz >= 1.4
        orientacion = QBoxLayout.TopToBottom if compacto else QBoxLayout.LeftToRight
        if self._cuerpo_adaptable.direction() == orientacion:
            return
        self._cuerpo_adaptable.setDirection(orientacion)
        if compacto:
            self._form_adaptable.setMinimumWidth(0)
            self._form_adaptable.setMaximumWidth(16_777_215)
        else:
            self._form_adaptable.setFixedWidth(315)

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
        self._desactualizado = False
        self._cambio_durante_calculo = False
        self._tabla_pendiente = None
        self._hojas_pendientes = {}
        self._hojas_editadas = {}
        self._hoja_visible = None
        self.ultimo = None
        if hasattr(self, "hojas"):
            self.hojas.clear()
        self.tabla.mostrar(pd.DataFrame())
        self.grafico.vacio()
        self.estado_cambiado.emit()
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
        self.tabla.reiniciar_historial()  # Un cálculo nuevo invalida el historial anterior.
        self._hojas_editadas = {k: tabla_de_sesion(self._hojas_pendientes.get(k), v)
                                for k, v in originales.items()}
        self._hojas_pendientes = {}
        self._hoja_visible = None

    def mostrar_hoja(self, widget: TablaDatos, nombre: str):
        """Guarda la hoja saliente y muestra la nueva, conservando ediciones."""
        self._guardar_hoja(widget)
        if nombre in self._hojas_editadas:
            widget.mostrar(self._hojas_editadas[nombre], identificador=nombre)
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
        self._cambio_durante_calculo = False
        revision = self._revision
        tarea = Tarea(funcion, *args, **kwargs)
        self._tarea = tarea

        def publicar(valor):
            if revision == self._revision:
                resultado(valor)
                self._desactualizado = self._cambio_durante_calculo
                self.estado_cambiado.emit()
                if self._desactualizado:
                    self.aviso.emit("El cálculo corresponde a entradas anteriores; recalcula para exportar.")

        tarea.senales.resultado.connect(publicar)
        tarea.senales.error.connect(lambda texto: self.aviso.emit(texto) if revision == self._revision else None)

        def terminado():
            self._ocupado = False
            self._tarea = None
            if final:
                final()
            self._continuar_restauracion()
            self.trabajo_finalizado.emit()

        tarea.senales.fin.connect(terminado)
        QThreadPool.globalInstance().start(tarea)
        return True
