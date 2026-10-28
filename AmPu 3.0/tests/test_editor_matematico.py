"""Completado matemático local: edición granular y Escape sin trampas de foco."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


def test_completar_fraccion_y_deshacer_con_teclado():
    from ampu.ui.widgets.editor_matematico import EditorLatex

    app = QApplication.instance() or QApplication([])
    editor = EditorLatex()
    editor.show()
    editor.setFocus()
    QTest.keyClicks(editor, r"\fr")
    app.processEvents()
    assert editor.completador.completionCount() == 1
    editor._insertar_sugerencia(r"\frac")
    assert editor.toPlainText() == r"\frac{a}{b}"
    assert editor.textCursor().selectedText() == "a"
    QTest.keyClicks(editor, "x")
    assert editor.toPlainText() == r"\frac{x}{b}"
    editor.undo()
    assert editor.toPlainText() == r"\frac{a}{b}"
    QTest.keyClick(editor, Qt.Key_Escape)
    editor.close()
