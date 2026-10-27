"""Verificación de los recursos incorporados también al ejecutable."""

from ampu.diagnostico import verificar_recursos


def test_autoprueba_recursos_exportadores_y_sesion():
    reporte = verificar_recursos()
    assert reporte["lecciones"] == 57
    assert reporte["imagenes"] == 31
    assert reporte["formatos"] == ["xlsx", "csv", "png", "pdf", "json"]
