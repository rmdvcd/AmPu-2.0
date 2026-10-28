"""Integración REAL de QtWebEngine/KaTeX (no se sustituye por mocks).

Si faltan NSS, OpenGL, D-Bus o X11, se omite SOLO esta prueba; ejecutar
``python -m ampu --self-test`` en un escritorio funcional es requisito de
publicación y falla de forma explícita si WebEngine no puede renderizar.
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError,
                                 reason="No están las bibliotecas nativas de Qt")
pytest.importorskip("PySide6.QtWebEngineWidgets", exc_type=ImportError,
                   reason="No están las bibliotecas nativas de QtWebEngine")


def test_render_chromium_real_offline_claro_y_oscuro():
    from ampu.diagnostico import verificar_webengine

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    reporte = verificar_webengine(app)
    assert reporte["webengine"] == "correcto"
    assert reporte["formulas"] >= 3
    assert reporte["imagenes"] >= 1
    assert reporte["asistente_mathml"] and reporte["asistente_contraste"] == "correcto"
