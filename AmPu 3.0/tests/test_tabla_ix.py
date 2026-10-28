"""Edición de hojas con historial y pegado reversible (Qt offscreen opcional)."""

import os

import pandas as pd
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
from PySide6.QtCore import QEvent, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


def test_pegado_multicelda_es_una_accion_reversible():
    from ampu.ui.widgets.tabla import TablaDatos

    app = QApplication.instance() or QApplication([])
    tabla = TablaDatos()
    tabla.mostrar(pd.DataFrame({"Valor": [1.12345678912345], "Etiqueta": ["a"]}))
    cambios = []
    tabla.modificado.connect(lambda: cambios.append(True))
    tabla.setCurrentCell(0, 0)
    QApplication.clipboard().setText("3\tb\n4\tc")
    tabla.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_V, Qt.ControlModifier))
    assert tabla.datos().to_dict(orient="list") == {"Valor": [3., 4.], "Etiqueta": ["b", "c"]}
    assert tabla.puede_deshacer()
    tabla.undo()
    assert tabla.datos().iloc[0, 0] == 1.12345678912345
    assert tabla.rowCount() == 1
    tabla.redo()
    assert tabla.rowCount() == 2 and tabla.item(1, 1).text() == "c"
    assert len(cambios) == 3  # pegar, deshacer y rehacer cambian la sesión.
    tabla.close()
    app.processEvents()


def test_historias_independientes_al_cambiar_hoja():
    from ampu.ui.widgets.tabla import TablaDatos

    app = QApplication.instance() or QApplication([])
    tabla = TablaDatos()
    tabla.mostrar(pd.DataFrame({"A": [1.0]}), identificador="Primera")
    tabla.item(0, 0).setText("10")
    primera = tabla.datos()
    tabla.mostrar(pd.DataFrame({"B": [2.0]}), identificador="Segunda")
    tabla.item(0, 0).setText("20")
    segunda = tabla.datos()
    tabla.mostrar(primera, identificador="Primera")
    assert tabla.puede_deshacer()
    tabla.undo()
    assert tabla.datos().iloc[0, 0] == 1.0
    tabla.mostrar(segunda, identificador="Segunda")
    assert tabla.puede_deshacer()
    tabla.undo()
    assert tabla.datos().iloc[0, 0] == 2.0
    tabla.close()
    app.processEvents()
