"""Componentes visuales y parsing de entradas sin cálculo estadístico."""

import re

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QSpinBox, QVBoxLayout, QWidget,
)

from ampu.core.errores import ParametroInvalidoError


def marco(nombre: str = "Card", margen: int = 19) -> tuple[QFrame, QVBoxLayout]:
    """Crea una tarjeta con márgenes uniformes y borde QSS."""
    tarjeta = QFrame()
    tarjeta.setObjectName(nombre)
    layout = QVBoxLayout(tarjeta)
    layout.setContentsMargins(margen, margen, margen, margen)
    layout.setSpacing(12)
    return tarjeta, layout


def encabezado(codigo: str, titulo: str, descripcion: str) -> QWidget:
    """Jerarquía tipográfica y contexto editorial de una vista."""
    widget = QWidget()
    v = QVBoxLayout(widget)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)
    for texto, estilo in ((codigo, "Eyebrow"), (titulo, "H1"), (descripcion, "Muted")):
        label = QLabel(texto)
        label.setObjectName(estilo)
        label.setWordWrap(True)
        v.addWidget(label)
    return widget


def etiqueta(texto: str, estilo: str = "Muted") -> QLabel:
    """Construye etiqueta con ajuste de línea y nombre de tema."""
    salida = QLabel(texto)
    salida.setObjectName(estilo)
    salida.setWordWrap(True)
    return salida


def campo_semilla() -> QSpinBox:
    """Semilla entera de usuario suficiente para el generador local."""
    control = QSpinBox()
    control.setRange(0, 2_147_483_647)
    control.setValue(42)
    control.setToolTip("Misma semilla → misma muestra. No modifica la aleatoriedad global.")
    return control


def numeros(texto: str, minimo: int = 2) -> np.ndarray:
    """Lee números separados por coma, espacio, punto y coma o saltos.

    Se usa punto decimal; la coma es separador de elementos.
    """
    try:
        valores = [float(fragmento) for fragmento in re.split(r"[,;\s]+", texto.strip()) if fragmento]
        salida = np.asarray(valores, dtype=float)
    except ValueError as exc:
        raise ParametroInvalidoError("Usa números separados por comas o espacios y punto decimal.") from exc
    if len(salida) < minimo or not np.all(np.isfinite(salida)):
        raise ParametroInvalidoError(f"Introduce al menos {minimo} valores numéricos finitos.")
    return salida


def matriz(texto: str) -> np.ndarray:
    """Lee matriz: cada fila en una línea (o ';'), columnas separadas por coma."""
    filas = [fila for fila in re.split(r"[;\n]+", texto.strip()) if fila.strip()]
    try:
        datos = np.asarray([numeros(fila, minimo=1) for fila in filas], dtype=float)
    except (ValueError, TypeError) as exc:
        raise ParametroInvalidoError("Cada fila debe tener el mismo número de columnas numéricas.") from exc
    if datos.ndim != 2 or not np.all(np.isfinite(datos)):
        raise ParametroInvalidoError("La matriz debe ser rectangular y finita.")
    return datos


def grupos(texto: str) -> list[np.ndarray]:
    """Una fila/grupo por línea o punto y coma."""
    return [numeros(fila) for fila in re.split(r"[;\n]+", texto.strip()) if fila.strip()]


def filas_estratos(texto: str) -> list[tuple[str, int, float, float]]:
    """Lee nombre, Nh, Sh y coste por fila, con validación de formato."""
    salida = []
    for linea in texto.strip().splitlines():
        if not linea.strip():
            continue
        partes = [fragmento.strip() for fragmento in linea.split(",")]
        if len(partes) not in (2, 3, 4):
            raise ParametroInvalidoError("Cada fila debe ser: nombre, tamaño, desviación, coste.")
        try:
            nombre, N = partes[:2]
            salida.append((nombre, int(N), float(partes[2]) if len(partes) > 2 else 1.,
                           float(partes[3]) if len(partes) > 3 else 1.))
        except ValueError as exc:
            raise ParametroInvalidoError("Tamaño, desviación y coste deben ser numéricos.") from exc
    if not salida:
        raise ParametroInvalidoError("Agrega al menos un estrato.")
    return salida


class KPIs(QWidget):
    """Indicadores compactos reutilizables de resultados escalares."""

    def __init__(self, titulos: list[str], parent=None):
        """Crea una banda de tarjetas con etiquetas y valores."""
        super().__init__(parent)
        self.valores: list[QLabel] = []
        self.tarjetas: list[QFrame] = []
        self.rejilla = QGridLayout(self)
        self.rejilla.setContentsMargins(0, 0, 0, 0)
        self.rejilla.setSpacing(10)
        for titulo in titulos:
            contenedor, v = marco("KpiCard", 13)
            leyenda = QLabel(titulo.upper())
            leyenda.setObjectName("KpiLabel")
            numero = QLabel("—")
            numero.setObjectName("KpiNumber")
            numero.setTextInteractionFlags(Qt.TextSelectableByMouse)
            numero.setMinimumWidth(65)
            v.addWidget(leyenda)
            v.addWidget(numero)
            self.rejilla.addWidget(contenedor, 0, len(self.tarjetas))
            self.tarjetas.append(contenedor)
            self.valores.append(numero)
        self._columnas = len(self.tarjetas)

    def ajustar_escala(self, escala: float):
        """Con texto grande, dos tarjetas por fila para evitar scroll horizontal."""
        columnas = 2 if escala >= 1.4 else len(self.tarjetas)
        if columnas == self._columnas:
            return
        self._columnas = columnas
        for indice, tarjeta in enumerate(self.tarjetas):
            self.rejilla.removeWidget(tarjeta)
            self.rejilla.addWidget(tarjeta, indice // columnas, indice % columnas)

    def actualizar(self, *valores: object):
        """Muestra escalares sin redondear los cálculos subyacentes."""
        for widget, valor in zip(self.valores, valores):
            a = np.asarray(valor)
            if a.ndim:
                texto = ", ".join(f"{v:.5g}" for v in a.ravel())
            elif not np.isfinite(float(a)):
                texto = "Indefinido" if np.isnan(float(a)) else "∞"
            else:
                texto = f"{float(a):.6g}"
            widget.setText(texto)
            widget.setToolTip(str(valor))
