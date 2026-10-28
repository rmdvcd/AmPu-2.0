"""Los parámetros dinámicos no quedan dibujados fuera del formulario."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
from PySide6.QtWidgets import QApplication, QFormLayout  # noqa: E402


def test_parametros_antiguos_ocultos_y_editores_legibles_a_200_por_ciento():
    from ampu.core.distribuciones import obtener
    from ampu.ui.widgets.formulario import FormularioDistribucion

    app = QApplication.instance() or QApplication([])
    formulario = FormularioDistribucion()
    formulario.usar(obtener("binomial"))
    antiguos = list(formulario.controles.values())
    formulario.usar(obtener("normal"))
    assert all(not control.isVisible() for control in antiguos)
    formulario.ajustar_escala(2.0)
    formulario.show()
    app.processEvents()
    assert formulario.formulario.rowWrapPolicy() == QFormLayout.WrapAllRows
    assert formulario.height() >= formulario.sizeHint().height()
    assert all(control.height() >= 70 for control in formulario.controles.values())
    formulario.close()
