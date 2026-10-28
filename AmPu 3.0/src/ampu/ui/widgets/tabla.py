"""Tabla ordenable, copiable y editable con deshacer/rehacer por hoja."""

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QUndoCommand, QUndoStack
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableWidget, QTableWidgetItem


class Celda(QTableWidgetItem):
    """Ordena números por magnitud y texto por orden natural vigente."""

    def __lt__(self, otro):
        a, b = TablaDatos._valor(self), TablaDatos._valor(otro)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a < b
        return self.text().casefold() < otro.text().casefold()


class _CambioTabla(QUndoCommand):
    """Instantánea acotada: conserva también pegados y precisión de los datos."""

    def __init__(self, tabla: "TablaDatos", anterior: pd.DataFrame, siguiente: pd.DataFrame, nombre: str):
        super().__init__(nombre)
        self.tabla = tabla
        self.anterior = anterior.copy(deep=True)
        self.siguiente = siguiente.copy(deep=True)
        self.inicial = True

    def undo(self):
        self.tabla._restablecer(self.anterior)

    def redo(self):
        if self.inicial:  # QUndoStack llama redo al agregar; la UI ya muestra el cambio.
            self.inicial = False
        else:
            self.tabla._restablecer(self.siguiente)


class TablaDatos(QTableWidget):
    """QTableWidget con portapapeles TSV y historial por hoja de hasta 20 cambios."""

    editado = Signal()
    modificado = Signal()  # Solo operaciones del usuario, no repintado de resultados.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName("Tabla de resultados editable y ordenable")
        self.setAccessibleDescription("Doble clic para editar; Ctrl+C, Ctrl+V, Ctrl+Z y Ctrl+Shift+Z. "
                                      "Las ediciones no recalculan estadísticas.")
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(False)
        self._pintando = False
        self._clave = ""
        self._historiales: dict[str, QUndoStack] = {}
        self._anterior = pd.DataFrame()
        self.itemChanged.connect(self._registrar_cambio)
        self.model().layoutChanged.connect(self._orden_cambiado)

    def _historial(self) -> QUndoStack:
        if self._clave not in self._historiales:
            pila = QUndoStack(self)
            pila.setUndoLimit(20)
            self._historiales[self._clave] = pila
        return self._historiales[self._clave]

    def reiniciar_historial(self):
        """Un recálculo crea resultados nuevos; evita deshacer sobre otro modelo."""
        for pila in self._historiales.values():
            pila.clear()

    def mostrar(self, tabla: pd.DataFrame, identificador: str | None = None):
        """Puebla una hoja, conservando su propia pila de edición al alternar."""
        if identificador is None:
            self.reiniciar_historial()
            self._clave = ""
        else:
            self._clave = identificador
        self._restablecer(tabla)

    def _restablecer(self, tabla: pd.DataFrame):
        self._pintando = True
        try:
            self.setSortingEnabled(False)
            self.clear()
            self.setRowCount(len(tabla))
            self.setColumnCount(len(tabla.columns))
            self.setHorizontalHeaderLabels(list(map(str, tabla.columns)))
            for row, valores in enumerate(tabla.itertuples(index=False, name=None)):
                for col, valor in enumerate(valores):
                    if isinstance(valor, (int, np.integer)) and not isinstance(valor, (bool, np.bool_)):
                        numero, texto = int(valor), str(int(valor))
                    elif isinstance(valor, (float, np.floating)):
                        numero = float(valor)
                        texto = "—" if np.isnan(numero) else ("∞" if numero == float("inf") else
                                    "−∞" if numero == float("-inf") else f"{numero:.8g}")
                    elif valor is None:
                        texto, numero = "—", None
                    else:
                        texto, numero = str(valor), None
                    item = Celda(texto)
                    if numero is not None and not (isinstance(numero, float) and np.isnan(numero)):
                        item.setData(Qt.UserRole, numero)
                        item.setData(Qt.UserRole + 1, texto)
                        item.setToolTip(str(valor))
                    self.setItem(row, col, item)
            self.setSortingEnabled(True)
            self.resizeColumnsToContents()
            for col in range(self.columnCount()):
                self.setColumnWidth(col, max(88, min(self.columnWidth(col) + 14, 220)))
            self._anterior = self.datos()
        finally:
            self._pintando = False
        self.editado.emit()

    def _orden_cambiado(self, *args):
        if not self._pintando:
            self._anterior = self.datos()

    def _registrar_cambio(self, item: QTableWidgetItem):
        if self._pintando:
            return
        if item.data(Qt.UserRole + 1) is not None and item.text() != item.data(Qt.UserRole + 1):
            self._pintando = True
            try:
                item.setToolTip(item.text())
            finally:
                self._pintando = False
        nuevo = self.datos()
        self._apilar(self._anterior, nuevo, "Editar celda")

    def _apilar(self, antes: pd.DataFrame, despues: pd.DataFrame, nombre: str):
        if not antes.equals(despues):
            self._historial().push(_CambioTabla(self, antes, despues, nombre))
            self._anterior = despues
            self.editado.emit()
            self.modificado.emit()

    def undo(self):
        pila = self._historial()
        if pila.canUndo():
            pila.undo()
            self.modificado.emit()

    def redo(self):
        pila = self._historial()
        if pila.canRedo():
            pila.redo()
            self.modificado.emit()

    def puede_deshacer(self) -> bool:
        return self._historial().canUndo()

    def puede_rehacer(self) -> bool:
        return self._historial().canRedo()

    def datos(self) -> pd.DataFrame:
        """Lee el orden y los valores exactos, no solo su texto abreviado."""
        return pd.DataFrame([
            [self._valor(self.item(fila, col)) for col in range(self.columnCount())]
            for fila in range(self.rowCount())
        ], columns=[self.horizontalHeaderItem(col).text() for col in range(self.columnCount())])

    @staticmethod
    def _valor(item: QTableWidgetItem | None) -> object:
        if item is None:
            return None
        if item.data(Qt.UserRole + 1) == item.text() and item.data(Qt.UserRole) is not None:
            return item.data(Qt.UserRole)
        if item.text() == "—":
            return None
        try:
            return float(item.text())
        except ValueError:
            return item.text()

    def copiar(self):
        indices = self.selectedIndexes()
        if indices:
            filas = sorted({i.row() for i in indices})
            columnas = sorted({i.column() for i in indices})
            texto = "\n".join("\t".join(self.item(r, c).text() if self.item(r, c) else "" for c in columnas)
                                for r in filas)
            QApplication.clipboard().setText(texto)

    def pegar(self):
        """Importar el bloque TSV cuenta como una única edición reversible."""
        inicio = self.currentIndex()
        texto = QApplication.clipboard().text()
        if inicio.isValid() and texto:
            filas_pegadas = [linea.split("\t") for linea in texto.rstrip("\n").splitlines()]
            if not filas_pegadas:
                return
            anterior = self.datos()
            self._pintando = True
            try:
                self.setSortingEnabled(False)
                self.setRowCount(max(self.rowCount(), inicio.row() + len(filas_pegadas)))
                for dr, fila in enumerate(filas_pegadas):
                    for dc, celda in enumerate(fila):
                        if inicio.column() + dc < self.columnCount():
                            self.setItem(inicio.row() + dr, inicio.column() + dc, Celda(celda))
                self.setSortingEnabled(True)
            finally:
                self._pintando = False
            self._apilar(anterior, self.datos(), "Pegar celdas")

    def keyPressEvent(self, event):
        """Usa las teclas estándar de cada sistema (Cmd en macOS)."""
        if event.matches(QKeySequence.Undo):
            self.undo()
        elif event.matches(QKeySequence.Redo):
            self.redo()
        elif event.matches(QKeySequence.Copy):
            self.copiar()
        elif event.matches(QKeySequence.Paste):
            self.pegar()
        else:
            super().keyPressEvent(event)
            return
        event.accept()
