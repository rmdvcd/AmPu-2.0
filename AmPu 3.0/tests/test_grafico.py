"""Regresiones del gráfico QtAgg y su animación de aparición."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError,
                    reason="Qt requiere bibliotecas gráficas del sistema")
from PySide6.QtCore import QPropertyAnimation  # noqa: E402
from PySide6.QtWidgets import QApplication, QGraphicsOpacityEffect  # noqa: E402


@pytest.fixture
def grafico():
    from ampu.ui.widgets.grafico import Grafico

    app = QApplication.instance() or QApplication([])
    widget = Grafico()
    yield widget
    widget.close()
    app.processEvents()


def terminar_aparicion(grafico):
    efecto = grafico.lienzo.graphicsEffect()
    animacion = grafico._animacion
    assert isinstance(efecto, QGraphicsOpacityEffect)
    assert isinstance(animacion, QPropertyAnimation)
    assert animacion.targetObject() is efecto
    assert animacion.propertyName() == b"opacity"
    assert animacion.duration() > 0
    animacion.setCurrentTime(animacion.duration())
    assert efecto.opacity() == pytest.approx(1.0)
    return efecto


def test_grafico_inicializa_su_aparicion(grafico):
    assert "Sin resultados" in grafico.descripcion.text()
    terminar_aparicion(grafico)


def test_aparicion_se_reinicia_al_redibujar_y_cambiar_tema(grafico):
    efecto = terminar_aparicion(grafico)
    grafico.serie(["A", "B"], [1.0, 2.0], "Ejemplo")
    assert terminar_aparicion(grafico) is efecto
    grafico.tema(True)
    assert terminar_aparicion(grafico) is efecto
    grafico.escalar_texto(1.2)
    assert terminar_aparicion(grafico) is efecto
    assert "Ejemplo" in grafico.descripcion.text()
