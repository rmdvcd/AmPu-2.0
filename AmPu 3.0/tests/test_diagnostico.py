"""Verificación de los recursos incorporados también al ejecutable."""

from ampu.diagnostico import verificar_recursos


def test_autoprueba_recursos_exportadores_y_sesion():
    reporte = verificar_recursos()
    assert reporte["lecciones"] == 57
    assert reporte["imagenes"] == 31
    assert reporte["formatos"] == ["xlsx", "csv", "png", "pdf", "json"]
    assert reporte["ui"] == "Dear PyGui"


def test_autoprueba_de_interfaz_dearpygui(ventana):
    from ampu.diagnostico import verificar_interfaz
    reporte = verificar_interfaz(ventana)
    assert reporte["modulos"] == 6
    assert reporte["interfaz"] == "Dear PyGui correcta"
