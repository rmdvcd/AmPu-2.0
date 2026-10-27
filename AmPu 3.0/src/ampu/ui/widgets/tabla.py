"""Tabla ordenable, copiable y editable por pegado de hojas de cálculo."""

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableWidget, QTableWidgetItem


class Celda(QTableWidgetItem):
    """Ordena números por magnitud y texto por orden natural."""

    def __lt__(self, otro):
        """Preserva ordenamiento numérico después de mostrar texto formateado."""
        a, b = self.data(Qt.UserRole), otro.data(Qt.UserRole)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a < b
        return self.text().casefold() < otro.text().casefold()


class TablaDatos(QTableWidget):
    """Exhibe un DataFrame, Ctrl+C copia TSV y Ctrl+V pega celdas."""

    editado = Signal()

    def __init__(self, parent=None):
        """Activa selección rectangular y filas alternas."""
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(False)

    def mostrar(self, tabla: pd.DataFrame):
        """Puebla la tabla completa sin perder ordenamiento posterior."""
        self.setSortingEnabled(False)
        self.clear()
        self.setRowCount(len(tabla))
        self.setColumnCount(len(tabla.columns))
        self.setHorizontalHeaderLabels(list(map(str, tabla.columns)))
        for row, valores in enumerate(tabla.itertuples(index=False, name=None)):
            for col, valor in enumerate(valores):
                if isinstance(valor, (int, float, np.number)):
                    v = float(valor)
                    texto = "—" if np.isnan(v) else ("∞" if np.isinf(v) else f"{v:.8g}")
                elif valor is None:
                    texto = "—"
                    v = None
                else:
                    texto = str(valor)
                    v = None
                item = Celda(texto)
                if v is not None and np.isfinite(v):
                    item.setData(Qt.UserRole, v)
                    item.setToolTip(str(valor))
                self.setItem(row, col, item)
        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
        for col in range(self.columnCount()):
            self.setColumnWidth(col, max(88, min(self.columnWidth(col)+14, 220)))

    def datos(self) -> pd.DataFrame:
        """Lee el orden y las modificaciones visibles para exportar lo presentado."""
        return pd.DataFrame([
            [self._valor(self.item(fila, col)) for col in range(self.columnCount())]
            for fila in range(self.rowCount())
        ], columns=[self.horizontalHeaderItem(col).text() for col in range(self.columnCount())])

    @staticmethod
    def _valor(item: QTableWidgetItem | None) -> object:
        """Interpreta valores editados como números cuando es posible."""
        if item is None or item.text() == "—":
            return None
        try:
            return float(item.text())
        except ValueError:
            return item.text()

    def keyPressEvent(self, event):
        """Exporta/importa selección rectangular al portapapeles del SO."""
        if event.matches(QKeySequence.Copy):
            indices = self.selectedIndexes()
            if indices:
                filas = sorted({i.row() for i in indices})
                columnas = sorted({i.column() for i in indices})
                texto = "\n".join("\t".join(self.item(r, c).text() if self.item(r, c) else "" for c in columnas)
                                    for r in filas)
                QApplication.clipboard().setText(texto)
            event.accept()
            return
        if event.matches(QKeySequence.Paste):
            inicio = self.currentIndex()
            if inicio.isValid():
                tabla = [linea.split("\t") for linea in QApplication.clipboard().text().rstrip("\n").splitlines()]
                self.setSortingEnabled(False)
                self.setRowCount(max(self.rowCount(), inicio.row() + len(tabla)))
                for dr, fila in enumerate(tabla):
                    for dc, texto in enumerate(fila):
                        if inicio.column() + dc < self.columnCount():
                            self.setItem(inicio.row()+dr, inicio.column()+dc, Celda(texto))
                self.setSortingEnabled(True)
                self.editado.emit()
            event.accept()
            return
        super().keyPressEvent(event)
