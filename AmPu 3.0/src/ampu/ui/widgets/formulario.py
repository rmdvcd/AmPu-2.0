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

    def usar(self, modelo: Distribucion):
        """Crea controles para cada ``Parametro`` del modelo elegido."""
        while self.formulario.count():
            elemento = self.formulario.takeAt(0)
            if elemento.widget():
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
            widget.setMinimumHeight(34)
            self.formulario.addRow(campo.nombre.replace("_", " ") + "  ·", widget)
            self.controles[campo.nombre] = widget
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

    def restaurar(self, valores: dict):
        """Carga valores previos en los controles actualmente construidos."""
        for nombre, valor in valores.items():
            if nombre not in self.controles:
                continue
            control = self.controles[nombre]
            if isinstance(control, QLineEdit):
                control.setText(", ".join(map(str, valor)))
            else:
                control.setValue(valor)
        self.cambiado.emit()
