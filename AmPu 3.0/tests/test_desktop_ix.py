"""Menús, preferencias y asistente: verificables en QWidget offscreen sin WebEngine."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture
def ventana(tmp_path):
    from ampu.ui.main_window import VentanaPrincipal

    app = QApplication.instance() or QApplication([])
    ajustes = QSettings(str(tmp_path / "ajustes.ini"), QSettings.IniFormat)
    ventana = VentanaPrincipal(ajustes)
    ventana.show()
    app.processEvents()
    yield ventana
    ventana.close()
    app.processEvents()


def test_menus_y_atajos_descubribles_sin_resultado(ventana):
    menus = [accion.text().replace("&", "") for accion in ventana.menuBar().actions()]
    assert menus == ["Archivo", "Edición", "Ver", "Ventana", "Ayuda"]
    assert ventana.acciones_exportar["excel"].shortcut().toString()
    assert all(not a.isEnabled() for a in ventana.acciones_exportar.values())
    assert ventana.boton_exportar.menu().actions() == list(ventana.acciones_exportar.values())
    assert not ventana.boton_exportar.isEnabled()
    assert ventana.minimumWidth() <= 900 and ventana.minimumHeight() <= 600
    assert ventana.divisor_principal.count() == 2
    ventana.accion_sidebar.trigger()
    assert not ventana.sidebar.isVisible()
    ventana.accion_sidebar.trigger()
    assert ventana.sidebar.isVisible()


def test_feedback_no_deja_estado_de_calculo_antiguo(ventana):
    from PySide6.QtCore import QElapsedTimer

    reloj = QElapsedTimer()
    reloj.start()
    while any(v._ocupado for v in ventana.vistas.values()) and reloj.elapsed() < 15_000:
        QApplication.instance().processEvents()
    assert not any(v._ocupado for v in ventana.vistas.values())
    ventana.statusBar().showMessage("Ejecutando simulación en segundo plano…")
    ventana.vistas["simulacion"].trabajo_finalizado.emit()
    assert "terminados" in ventana.statusBar().currentMessage()


def test_asistente_se_separa_si_el_zoom_y_la_ventana_recortarian_el_analisis(ventana):
    ventana.resize(900, 600)
    ventana.calculadora()
    ventana.escalar_texto(1.0)
    QApplication.instance().processEvents()
    assert ventana.panel_asistente.isFloating()
    assert ventana.divisor_principal.width() >= 890
    assert not ventana.sidebar.isVisible()
    ventana._sesion_guardada()
    ventana.close()
    assert not ventana.panel_asistente.isVisible()  # sin ventana auxiliar huérfana.


def test_asistente_no_modal_traza_error_copia_y_codigo_editable(ventana, monkeypatch):
    from ampu.ui.widgets.calculadora import Calculadora

    ventana.calculadora()
    asistente = ventana.asistente
    assert ventana.isEnabled() and ventana.panel_asistente.isVisible()
    asistente.entrada.setText("sqrt(2)+sin(pi/2)")
    asistente._evaluar()
    assert "Resultado final: 2.41421" in asistente.respuesta.text()
    assert "Entrada interpretada: sqrt(2) + sin(pi / 2)" == asistente.interpretacion.text()
    assert "radianes" in asistente.pasos.toPlainText()
    assert "1.41421356237" in asistente.pasos.toPlainText()  # resultado del AST
    asistente.copiar_resultado()
    assert QApplication.clipboard().text() == str(asistente._resultado)
    asistente.entrada.setText("1/0")
    asistente._evaluar()
    assert "Error:" in asistente.respuesta.text()
    assert asistente.entrada.text() == "1/0"  # recuperación sin borrado automático
    monkeypatch.setattr(Calculadora, "_iniciar_vista", lambda _: None)  # Chromium requiere NSS en el sandbox.
    asistente.pestanas.setCurrentIndex(1)
    asistente.insertar_plantilla(r"\frac{a}{b}", "a")
    assert asistente.latex.textCursor().selectedText() == "a"
    asistente.latex.textCursor().insertText("x")
    assert asistente.latex.toPlainText() == r"\frac{x}{b}"
    asistente.copiar_latex()
    assert QApplication.clipboard().text() == r"\frac{x}{b}"
    guardado = asistente.estado()
    asistente.restaurar(guardado)
    assert asistente.latex.toPlainText() == guardado["latex"]
    assert asistente.entrada.text() == "1/0"
    assert asistente._resultado is None  # no evalúa silenciosamente al restaurar


def test_contraste_escalado_y_preferencias_entre_ventanas(ventana):
    ventana.aplicar_tema("contraste", persistir=True)
    assert ventana.tema_actual == "contraste" and ventana.acciones_tema["contraste"].isChecked()
    assert "#FFDF00" in QApplication.instance().styleSheet()
    ventana.escalar_texto(.3)
    assert ventana.escala_fuente == 1.3
    assert ventana.vistas["distribuciones"].grafico._escala == 1.3
    ventana.resize(1030, 750)
    ajustes = ventana.preferencias
    ventana.close()
    assert ajustes.value("ventana/geometria") is not None
    assert ajustes.value("ventana/paneles") is not None
    from ampu.ui.main_window import VentanaPrincipal
    nueva = VentanaPrincipal(ajustes)
    nueva.show()
    assert nueva.modo_tema == "contraste" and nueva.escala_fuente == 1.3
    nueva.escalar_texto(.7)
    QApplication.instance().processEvents()
    assert nueva.escala_fuente == 2.0
    assert not nueva.boton_guardar.isVisible()  # la misma acción sigue en Archivo.
    assert nueva.vista._cuerpo_adaptable.direction().name == "TopToBottom"
    nueva.resize(900, 600)
    for clave in ("distribuciones", "muestreo", "descriptiva", "probabilidad", "inferencia", "simulacion"):
        nueva.cambiar(clave)
        QApplication.instance().processEvents()
        assert nueva.contenedores[clave].horizontalScrollBar().maximum() == 0, clave
    from PySide6.QtWidgets import QFormLayout
    nueva.cambiar("distribuciones")
    QApplication.instance().processEvents()
    formulario = nueva.vistas["distribuciones"].formulario
    assert formulario.formulario.rowWrapPolicy() == QFormLayout.WrapAllRows
    assert formulario.height() >= formulario.sizeHint().height()
    assert all(c.height() >= c.minimumHeight() for c in formulario.controles.values())
    nueva.close()


def test_exportacion_se_bloquea_si_las_entradas_no_corresponden_al_grafico(ventana):
    from PySide6.QtCore import QEventLoop, QTimer

    vista = ventana.vistas["distribuciones"]
    if vista.ultimo is None:
        vista.calcular()
    limite = QTimer()
    limite.setSingleShot(True)
    ciclo = QEventLoop()
    limite.timeout.connect(ciclo.quit)
    limite.start(12_000)

    def terminado():
        if vista.ultimo is not None and not vista._ocupado:
            ciclo.quit()
        else:
            QTimer.singleShot(30, terminado)

    QTimer.singleShot(30, terminado)
    ciclo.exec()
    limite.stop()
    assert vista.ultimo is not None and not vista._ocupado
    ventana._actualizar_acciones()
    assert ventana.acciones_exportar["excel"].isEnabled()
    vista.evento.setText("6")
    assert vista._desactualizado
    assert not ventana.acciones_exportar["excel"].isEnabled()
    vista.calcular()
    limite.start(12_000)
    QTimer.singleShot(30, terminado)
    ciclo.exec()
    limite.stop()
    assert not vista._desactualizado and ventana.acciones_exportar["excel"].isEnabled()


def test_guardar_y_reabrir_con_entrada_parcial_sin_perder_datos(ventana, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from ampu.io.sesion import cargar_sesion

    archivo = tmp_path / "incompleta.json"
    vista = ventana.vistas["distribuciones"]
    vista.selector.setCurrentIndex(vista.selector.findData("multinomial"))
    vista.formulario.controles["p"].setText("0.1, pendiente, 0.9")
    ventana.asistente.latex.setPlainText(r"\frac{a}{b}")
    assert ventana.isWindowModified()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(archivo), ""))
    assert ventana.guardar_sesion()
    assert not ventana.isWindowModified()
    estado = cargar_sesion(archivo)
    assert estado["vistas"]["distribuciones"]["parametros"]["p"] == "0.1, pendiente, 0.9"
    assert estado["asistente"]["latex"] == r"\frac{a}{b}"
    ventana.asistente.latex.setPlainText("alterada")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: (str(archivo), ""))
    assert ventana.abrir_sesion()
    assert ventana.asistente.latex.toPlainText() == r"\frac{a}{b}"
    assert not ventana.isWindowModified()


def test_cierre_cancelado_no_descarta_sesion(ventana, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    ventana.asistente.entrada.setText("1+2")
    assert ventana.isWindowModified()
    monkeypatch.setattr(QApplication, "platformName", staticmethod(lambda: "xcb"))
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.Cancel)
    assert not ventana._permitir_descartar("Cerrar")
    from PySide6.QtGui import QCloseEvent
    evento = QCloseEvent()
    ventana.closeEvent(evento)
    assert not evento.isAccepted() and ventana.isVisible()
    assert ventana.isWindowModified()
    ventana._sesion_guardada()  # cierre automático de la fixture sin nuevo modal.


def test_carga_fallida_revierte_tema_y_entrada_sin_borrar_trabajo(ventana, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from ampu.io.sesion import guardar_sesion

    ventana.asistente.entrada.setText("2+2")
    assert ventana.isWindowModified()
    vista = ventana.vistas["distribuciones"]
    ruta = guardar_sesion({"modulo": "distribuciones", "tema": "oscuro",
                            "asistente": {"entrada": "9+9"},
                            "vistas": {"distribuciones": vista.estado()}}, tmp_path / "prueba.json")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(ruta), ""))
    monkeypatch.setattr(ventana, "_permitir_descartar", lambda _: True)
    errores = []
    monkeypatch.setattr(ventana, "_error", errores.append)
    original = vista.restaurar
    intentos = []

    def restaurar(datos):
        intentos.append(True)
        if len(intentos) == 1:
            raise ValueError("vista dañada")
        return original(datos)

    monkeypatch.setattr(vista, "restaurar", restaurar)
    tema_anterior = ventana.modo_tema
    assert not ventana.abrir_sesion()
    assert len(intentos) == 2 and errores
    assert ventana.modo_tema == tema_anterior
    assert ventana.asistente.entrada.text() == "2+2" and ventana.isWindowModified()


def test_salir_cancelado_no_cierra_ninguna_de_dos_ventanas(ventana, monkeypatch):
    from ampu.ui.main_window import VentanaPrincipal

    segunda = VentanaPrincipal(ventana.preferencias)
    segunda.show()
    QApplication.instance().processEvents()
    monkeypatch.setattr(ventana, "_permitir_descartar", lambda _: True)
    monkeypatch.setattr(segunda, "_permitir_descartar", lambda _: False)
    ventana._salir()
    assert ventana.isVisible() and segunda.isVisible()
    monkeypatch.setattr(segunda, "_permitir_descartar", lambda _: True)
    segunda.close()


def test_deshacer_tabla_despues_de_guardar_vuelve_a_marcar_sesion(ventana):
    import pandas as pd

    tabla = ventana.vistas["distribuciones"].tabla
    tabla.mostrar(pd.DataFrame({"Valor": [1.0]}))
    tabla.item(0, 0).setText("2")
    assert ventana.isWindowModified()
    ventana._sesion_guardada()
    assert not ventana.isWindowModified()
    tabla.undo()
    assert ventana.isWindowModified()


def test_edicion_menu_delega_undo_al_control_enfocado(ventana):
    ventana.calculadora()
    entrada = ventana.asistente.entrada
    entrada.setText("2")
    entrada.setFocus()
    QApplication.instance().processEvents()
    entrada.insert("+3")
    menu = ventana.menuBar().actions()[1].menu()
    menu.popup(ventana.mapToGlobal(ventana.rect().topLeft()))
    QApplication.instance().processEvents()
    assert ventana.acciones_editar["undo"].isEnabled()
    menu.hide()
    ventana.acciones_editar["undo"].trigger()
    assert entrada.text() == "2"
    ventana.acciones_editar["redo"].trigger()
    assert entrada.text() == "2+3"
