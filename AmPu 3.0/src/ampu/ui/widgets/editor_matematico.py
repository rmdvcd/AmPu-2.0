"""Edición LaTeX por teclado con completado local y sin ejecución de comandos."""

import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QCompleter, QPlainTextEdit


PLANTILLAS = {
    r"\frac": (r"\frac{a}{b}", "a"),
    r"\sqrt": (r"\sqrt{x}", "x"),
    r"\int": (r"\int_{a}^{b} f(x)\,dx", "f(x)"),
    r"\sum": (r"\sum_{i=1}^{n} x_i", "x_i"),
    r"\alpha": (r"\alpha", None),
    r"\beta": (r"\beta", None),
    r"\sigma": (r"\sigma", None),
    r"\mu": (r"\mu", None),
    r"\pi": (r"\pi", None),
    r"\infty": (r"\infty", None),
    r"\cdot": (r"\cdot", None),
    r"\leq": (r"\leq", None),
    r"\geq": (r"\geq", None),
}


class EditorLatex(QPlainTextEdit):
    """Tab navega como en Qt; las sugerencias se aceptan con Enter o clic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.completador = QCompleter(sorted(PLANTILLAS), self)
        self.completador.setWidget(self)
        self.completador.setCompletionMode(QCompleter.PopupCompletion)
        self.completador.setCaseSensitivity(Qt.CaseSensitive)
        self.completador.popup().setAccessibleName("Sugerencias de comandos LaTeX")
        self.completador.activated[str].connect(self._insertar_sugerencia)
        self._prefijo = ""

    def keyPressEvent(self, evento):
        popup = self.completador.popup()
        if popup.isVisible() and evento.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape,
                                                    Qt.Key_Tab, Qt.Key_Backtab):
            evento.ignore()  # El popup acepta o cancela; la expresión nunca se evalúa.
            return
        super().keyPressEvent(evento)
        if evento.text() or evento.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self._mostrar_sugerencias()

    def _mostrar_sugerencias(self):
        linea = self.textCursor().block().text()[:self.textCursor().positionInBlock()]
        coincidencia = re.search(r"\\[A-Za-z]{2,}$", linea)
        self._prefijo = coincidencia.group(0) if coincidencia else ""
        if not self._prefijo:
            self.completador.popup().hide()
            return
        self.completador.setCompletionPrefix(self._prefijo)
        if self.completador.completionCount() == 0:
            self.completador.popup().hide()
            return
        rectangulo = self.cursorRect()
        rectangulo.setWidth(self.completador.popup().sizeHintForColumn(0) +
                            self.completador.popup().verticalScrollBar().sizeHint().width())
        self.completador.complete(rectangulo)

    def _insertar_sugerencia(self, comando: str):
        cursor = self.textCursor()
        inicio = cursor.position() - len(self._prefijo)
        if (comando.startswith(self._prefijo) and inicio >= 0
                and self.toPlainText()[inicio:cursor.position()] == self._prefijo):
            plantilla, seleccion = PLANTILLAS[comando]
            cursor.setPosition(inicio, QTextCursor.MoveAnchor)
            cursor.setPosition(inicio + len(self._prefijo), QTextCursor.KeepAnchor)
            cursor.insertText(plantilla)
            if seleccion is not None:
                # No seleccionar por accidente la «a» del nombre \frac.
                indice = plantilla.find("{" + seleccion + "}")
                if indice >= 0:
                    indice += 1
                else:
                    tras_llave = plantilla.find("}" + seleccion)
                    indice = tras_llave + 1 if tras_llave >= 0 else plantilla.index(seleccion)
                cursor.setPosition(inicio + indice, QTextCursor.MoveAnchor)
                cursor.setPosition(inicio + indice + len(seleccion), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        self.completador.popup().hide()
