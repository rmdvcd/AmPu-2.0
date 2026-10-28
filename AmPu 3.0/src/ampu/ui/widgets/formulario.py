"""Formulario generado desde metadatos; no duplica reglas estadísticas."""

import math

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QLineEdit, QSpinBox, QWidget

from ampu.core.distribuciones.base import Distribucion
from ampu.core.errores import ParametroInvalidoError


class FormularioDistribucion(QWidget):
    """Controles creados/reemplazados al cambiar la distribución registrada."""

    cambiado = Signal()

    def __init__(self, parent=None):
        """Comienza sin distribución, a la espera de la elección del usuario."""
        super().__init__(parent)
        self.formulario = QFormLayout(self)
        self.formulario.setContentsMargins(0, 0, 0, 0)
        self.formulario.setSpacing(10)
        self.controles: dict[str, QWidget] = {}
        self.modelo: Distribucion | None = None
        self._escala = 1.0

    def ajustar_escala(self, escala: float):
        """Evita que el scroll comprima editores por debajo de su tamaño útil."""
        self._escala = escala
        self.formulario.setRowWrapPolicy(QFormLayout.WrapAllRows if escala >= 1.4
                                         else QFormLayout.DontWrapRows)
        self._ajustar_altura()

    def _ajustar_altura(self):
        for control in self.controles.values():
            control.setMinimumHeight(max(34, round(28 * self._escala) + 14))
        self.formulario.invalidate()
        self.setMinimumHeight(self.sizeHint().height())

    def usar(self, modelo: Distribucion):
        """Crea controles para cada ``Parametro`` del modelo elegido."""
        while self.formulario.count():
            elemento = self.formulario.takeAt(0)
            if elemento.widget():
                # deleteLater espera al bucle Qt; ocultar ya evita campos
                # fantasma al cambiar rápidamente de distribución.
                elemento.widget().hide()
                elemento.widget().deleteLater()
        self.controles.clear()
        self.modelo = modelo
        for campo in modelo.parametros:
            if campo.tipo.startswith("vector_"):
                widget = QLineEdit(", ".join(map(str, campo.default)))
                widget.setPlaceholderText("Valores separados por comas")
                widget.textChanged.connect(self.cambiado)
            elif campo.tipo == "entero":
                widget = QSpinBox()
                minimo = math.ceil(campo.minimo) if campo.minimo is not None else -1_000_000
                maximo = math.floor(campo.maximo) if campo.maximo is not None else 1_000_000
                widget.setRange(max(-1_000_000, minimo), min(1_000_000, maximo))
                widget.setValue(int(campo.default))
                widget.valueChanged.connect(self.cambiado)
            else:
                widget = QDoubleSpinBox()
                widget.setDecimals(10)
                widget.setRange(max(-1e12, campo.minimo if campo.minimo is not None else -1e12),
                                min(1e12, campo.maximo if campo.maximo is not None else 1e12))
                widget.setSingleStep(.1 if campo.minimo is not None and campo.maximo is not None else .5)
                widget.setValue(float(campo.default))
                widget.valueChanged.connect(self.cambiado)
            widget.setToolTip(campo.descripcion)
            widget.setAccessibleName(f"Parámetro {campo.nombre.replace('_', ' ')}")
            widget.setAccessibleDescription(campo.descripcion)
            widget.setMinimumHeight(34)
            self.formulario.addRow(campo.nombre.replace("_", " ") + "  ·", widget)
            self.controles[campo.nombre] = widget
        self._ajustar_altura()
        self.cambiado.emit()

    def valores(self) -> dict:
        """Lee campos y delega validación de rango/coherencia al modelo."""
        if self.modelo is None:
            raise ParametroInvalidoError("Selecciona una distribución.")
        salida = {}
        for campo in self.modelo.parametros:
            widget = self.controles[campo.nombre]
            if isinstance(widget, QLineEdit):
                try:
                    salida[campo.nombre] = [float(x.strip()) for x in widget.text().split(",")]
                except ValueError as exc:
                    raise ParametroInvalidoError(f"{campo.nombre}: separa números con comas y usa punto decimal.") from exc
            else:
                salida[campo.nombre] = widget.value()
        return self.modelo.validar(**salida)

    def estado(self) -> dict:
        """Captura entradas aun si son incompletas: guardar jamás las pierde."""
        salida = {}
        for nombre, widget in self.controles.items():
            if isinstance(widget, QLineEdit):
                try:
                    salida[nombre] = [float(parte.strip()) for parte in widget.text().split(",")]
                except ValueError:
                    salida[nombre] = widget.text()
            else:
                salida[nombre] = widget.value()
        return salida

    def restaurar(self, valores: dict):
        """Carga valores previos en los controles actualmente construidos."""
        for nombre, valor in valores.items():
            if nombre not in self.controles:
                continue
            control = self.controles[nombre]
            if isinstance(control, QLineEdit):
                control.setText(valor if isinstance(valor, str) else ", ".join(map(str, valor)))
            else:
                control.setValue(valor)
        self.cambiado.emit()
