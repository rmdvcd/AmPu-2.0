"""Ventana principal: navegación, tema, sesiones y exportación unificada."""

import logging
import re
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QComboBox, QDialog, QDialogButtonBox,
    QDockWidget, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMessageBox, QPlainTextEdit, QPushButton,
    QScrollArea, QSpinBox, QSplitter, QStackedWidget, QStatusBar,
    QToolButton, QVBoxLayout, QWidget,
)

from ampu.docs.teoria import extraer_formula
from ampu.io import ServicioExportacion as io
from ampu.ui.preferencias_sistema import alto_contraste_windows, factor_fuente_sistema
from ampu.ui.vistas.descriptiva import VistaDescriptiva
from ampu.ui.vistas.distribuciones import VistaDistribuciones
from ampu.ui.vistas.inferencia import VistaInferencia
from ampu.ui.vistas.muestreo import VistaMuestreo
from ampu.ui.vistas.probabilidad import VistaProbabilidad
from ampu.ui.vistas.simulacion import VistaSimulacion
from ampu.ui.widgets.calculadora import Calculadora
from ampu.ui.widgets.tabla import TablaDatos

LOG = logging.getLogger(__name__)
ESTILOS = Path(__file__).resolve().parent / "estilos"
ICONO = Path(__file__).resolve().parent / "recursos" / "icono.svg"

PAGINAS = [
    ("distribuciones", "◉", "Distribuciones"),
    ("muestreo", "▦", "Muestreo"),
    ("descriptiva", "▥", "Descriptiva"),
    ("probabilidad", "◇", "Probabilidad"),
    ("inferencia", "∑", "Inferencia"),
    ("simulacion", "◷", "Simulación"),
    ("teoria", "▤", "Teoría"),
]


class VentanaPrincipal(QMainWindow):
    """Menús nativos, paneles persistentes y laboratorio estadístico accesible."""

    _instancias: set["VentanaPrincipal"] = set()

    def __init__(self, preferencias: QSettings | None = None):
        """Carga preferencias de interfaz; nunca restaura datos sin petición expresa."""
        super().__init__()
        self._instancias.add(self)
        self.preferencias = preferencias or QSettings("AmPu", "AmPu 3.0")
        self.modo_tema = str(self.preferencias.value("interfaz/tema", "sistema"))
        if self.modo_tema not in ("sistema", "claro", "oscuro", "contraste"):
            self.modo_tema = "sistema"
        try:
            self.escala_fuente = max(.9, min(2.0, float(self.preferencias.value("interfaz/escala", 1.0))))
        except (TypeError, ValueError):
            self.escala_fuente = 1.0
        self.escala_efectiva = self.escala_fuente
        self._sidebar_deseada = self.preferencias.value("interfaz/panel_lateral", True, type=bool)
        self._sidebar_fijada = self.preferencias.value("interfaz/panel_lateral_forzado", False, type=bool)
        self._foco_previo = None
        self._cambios_sin_guardar = False
        self._abriendo_sesion = False
        self._cierre_confirmado = False
        self.tema_actual = "claro"
        self.actual = "distribuciones"
        self.setWindowTitle("AmPu 3.0 · Laboratorio de estadística[*]")
        self.setWindowIcon(QIcon(str(ICONO)))
        self.resize(1450, 900)
        self.setMinimumSize(900, 600)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("AmPu 3.0 · Listo para explorar", 6000)
        raiz = QWidget()
        raiz.setObjectName("Raiz")
        self.setCentralWidget(raiz)
        fila = QHBoxLayout(raiz)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(0)
        self.divisor_principal = QSplitter(Qt.Horizontal)
        self.divisor_principal.setChildrenCollapsible(True)
        fila.addWidget(self.divisor_principal)
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(185)
        sidebar.setMaximumWidth(275)
        self.sidebar = sidebar
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(17, 23, 17, 17)
        nav.setSpacing(7)
        branding = QHBoxLayout()
        emblema = QLabel()
        emblema.setPixmap(QPixmap(str(ICONO)).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        branding.addWidget(emblema)
        letras = QVBoxLayout()
        letras.setSpacing(0)
        titulo = QLabel("AmPu")
        titulo.setObjectName("Brand")
        letras.addWidget(titulo)
        subtitulo = QLabel("VERSIÓN 3.0")
        subtitulo.setObjectName("BrandSub")
        letras.addWidget(subtitulo)
        branding.addLayout(letras)
        branding.addStretch()
        nav.addLayout(branding)
        nav.addSpacing(30)
        seccion = QLabel("EXPLORAR")
        seccion.setObjectName("SidebarHeading")
        nav.addWidget(seccion)
        self.botones: dict[str, QPushButton] = {}
        for clave, simbolo, texto in PAGINAS:
            btn = QPushButton(f"{simbolo}    {texto}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setAccessibleName(f"Abrir sección {texto}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, id=clave: self.cambiar(id))
            nav.addWidget(btn)
            self.botones[clave] = btn
        nav.addStretch()
        consejo = QFrame()
        consejo.setObjectName("SidebarBottom")
        bloque = QVBoxLayout(consejo)
        bloque.setContentsMargins(12, 14, 12, 14)
        bloque.addWidget(self._sidebar_label("APRENDER HACIENDO"))
        bloque.addWidget(self._sidebar_label("57 lecciones · 26 modelos · análisis sin conexión"))
        nav.addWidget(consejo)
        calculadora = QPushButton("⌗   Asistente")
        calculadora.setObjectName("NavButton")
        calculadora.setAccessibleName("Mostrar asistente matemático no modal")
        calculadora.setToolTip("Mostrar asistente matemático · Ctrl+L")
        calculadora.clicked.connect(self.calculadora)
        nav.addWidget(calculadora)
        self.divisor_principal.addWidget(sidebar)

        columna = QWidget()
        contenido = QVBoxLayout(columna)
        contenido.setContentsMargins(0, 0, 0, 0)
        contenido.setSpacing(0)
        self.divisor_principal.addWidget(columna)
        self.divisor_principal.setStretchFactor(0, 0)
        self.divisor_principal.setStretchFactor(1, 1)
        self.divisor_principal.setSizes([218, 1232])
        topbar = QWidget()
        self.topbar = topbar
        topbar.setMinimumHeight(57)
        top = QHBoxLayout(topbar)
        top.setContentsMargins(25, 8, 25, 8)
        self.top_etiqueta = self._top_label("LABORATORIO  /  AMPU 3.0")
        top.addWidget(self.top_etiqueta)
        top.addStretch()
        self.boton_tema = QPushButton("☾  Tema oscuro")
        self.boton_tema.setObjectName("Secondary")
        self.boton_tema.clicked.connect(self.alternar_tema)
        top.addWidget(self.boton_tema)
        btn_guardar = QPushButton("Guardar sesión")
        btn_guardar.setObjectName("Secondary")
        btn_guardar.clicked.connect(self.guardar_sesion)
        self.boton_guardar = btn_guardar
        top.addWidget(btn_guardar)
        btn_abrir = QPushButton("Abrir")
        btn_abrir.setObjectName("Quiet")
        btn_abrir.clicked.connect(self.abrir_sesion)
        self.boton_abrir = btn_abrir
        top.addWidget(btn_abrir)
        btn_exportar = QToolButton()
        btn_exportar.setText("Exportar  ▾")
        btn_exportar.setObjectName("Primary")
        btn_exportar.setPopupMode(QToolButton.InstantPopup)
        btn_exportar.setMenu(QMenu(btn_exportar))  # Se rellena con las QAction de Archivo.
        btn_exportar.setAccessibleName("Exportar resultados en Excel, CSV, PNG o PDF")
        self.boton_exportar = btn_exportar
        top.addWidget(btn_exportar)
        contenido.addWidget(topbar)
        self.pila = QStackedWidget()
        contenido.addWidget(self.pila, 1)
        self.vistas: dict[str, QWidget] = {
            "distribuciones": VistaDistribuciones(), "muestreo": VistaMuestreo(),
            "descriptiva": VistaDescriptiva(), "probabilidad": VistaProbabilidad(),
            "inferencia": VistaInferencia(), "simulacion": VistaSimulacion(),
        }
        self.contenedores = {}
        for clave, vista in self.vistas.items():
            desplazamiento = QScrollArea()
            desplazamiento.setWidgetResizable(True)
            desplazamiento.setFrameShape(QFrame.NoFrame)
            desplazamiento.setWidget(vista)
            desplazamiento.setAccessibleName(f"Contenido desplazable de {clave}")
            self.pila.addWidget(desplazamiento)
            self.contenedores[clave] = desplazamiento
            vista.aviso.connect(self.mensaje)
            vista.estado_cambiado.connect(self._actualizar_acciones)
            vista.entrada_modificada.connect(self._marcar_sesion)
            vista.trabajo_finalizado.connect(self._trabajo_finalizado)
            vista.tabla.modificado.connect(self._marcar_sesion)
            vista.abrir_teoria.connect(self.abrir_teoria)
        self._crear_asistente()
        self.asistente.entrada.textChanged.connect(self._marcar_sesion)
        self.asistente.latex.textChanged.connect(self._marcar_sesion)
        self._crear_menus()
        QApplication.instance().focusChanged.connect(self._registrar_foco)
        QApplication.instance().fontChanged.connect(self._fuente_sistema_cambiada)
        QApplication.instance().paletteChanged.connect(self._tema_sistema_cambiado)
        try:
            QApplication.instance().styleHints().colorSchemeChanged.connect(self._tema_sistema_cambiado)
        except AttributeError:  # Qt antiguo: sigue disponible la selección manual.
            pass
        self.aplicar_tema(self.modo_tema)
        geometria = self.preferencias.value("ventana/geometria")
        if geometria is not None:
            self.restoreGeometry(geometria)
        disposicion = self.preferencias.value("ventana/paneles")
        if disposicion is not None:
            self.restoreState(disposicion)
        self._actualizar_sidebar()
        self.cambiar("distribuciones")
        QTimer.singleShot(0, lambda: self.vistas["distribuciones"].buscar.setFocus(Qt.TabFocusReason))

    @staticmethod
    def _sidebar_label(texto: str) -> QLabel:
        """Etiqueta de contraste alto dentro de la barra lateral."""
        label = QLabel(texto)
        label.setObjectName("SidebarInfo")
        label.setWordWrap(True)
        return label

    @staticmethod
    def _top_label(texto: str) -> QLabel:
        """Encabezado pequeño de la zona de herramientas."""
        label = QLabel(texto)
        label.setObjectName("Eyebrow")
        return label

    def _crear_asistente(self):
        """Panel persistente y acoplable: nunca interrumpe el análisis con un modal."""
        self.panel_asistente = QDockWidget("Asistente matemático", self)
        self.panel_asistente.setObjectName("PanelAsistente")
        self.panel_asistente.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.panel_asistente.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable |
                                        QDockWidget.DockWidgetClosable)
        self.asistente = Calculadora(self.panel_asistente)
        self.panel_asistente.setWidget(self.asistente)
        self.addDockWidget(Qt.RightDockWidgetArea, self.panel_asistente)
        self.panel_asistente.hide()

    def _accion(self, menu, titulo: str, atajo, funcion, *, rol=None) -> QAction:
        """El menú es fuente única de atajos; nunca duplica QShortcut de Qt."""
        accion = QAction(titulo, self)
        accion.setShortcut(QKeySequence(atajo))
        accion.setShortcutContext(Qt.WindowShortcut)
        if rol is not None:
            accion.setMenuRole(rol)
        accion.triggered.connect(lambda checked=False: funcion())
        menu.addAction(accion)
        return accion

    def _crear_menus(self):
        """Archivo/Edición/Ver/Ventana/Ayuda; Qt crea el menú App nativo en macOS."""
        barra = self.menuBar()
        barra.setNativeMenuBar(sys.platform == "darwin")
        archivo = barra.addMenu("&Archivo")
        nueva = self._accion(archivo, "Nueva ventana", QKeySequence.StandardKey.New, self.nueva_ventana)
        archivo.addSeparator()
        self._accion(archivo, "Abrir sesión…", QKeySequence.StandardKey.Open, self.abrir_sesion)
        self._accion(archivo, "Guardar sesión…", QKeySequence.StandardKey.Save, self.guardar_sesion)
        exportar = archivo.addMenu("Exportar")
        self.acciones_exportar = {}
        for titulo, formato, atajo in (
            ("Excel · todas las hojas…", "excel", "Ctrl+E"),
            ("CSV · tabla visible…", "csv", "Ctrl+Shift+E"),
            ("PNG · gráfico actual…", "png", "Ctrl+Shift+G"),
            ("PDF · informe completo…", "pdf", QKeySequence.StandardKey.Print),
        ):
            self.acciones_exportar[formato] = self._accion(
                exportar, titulo, atajo, lambda f=formato: self.exportar(f))
        # El desplegable y Archivo comparten exactamente las mismas QAction:
        # estado y atajo son iguales, no dos rutas con permisos distintos.
        desplegable = self.boton_exportar.menu()
        desplegable.clear()
        for formato in ("excel", "csv", "png", "pdf"):
            desplegable.addAction(self.acciones_exportar[formato])
        archivo.addSeparator()
        cerrar = self._accion(archivo, "Cerrar ventana", QKeySequence.StandardKey.Close, self.close)
        self._accion(archivo, "Salir de AmPu", QKeySequence.StandardKey.Quit, self._salir,
                     rol=QAction.QuitRole)

        editar = barra.addMenu("&Edición")
        self.acciones_editar = {}
        for titulo, nombre, atajo in (
            ("Deshacer", "undo", QKeySequence.StandardKey.Undo),
            ("Rehacer", "redo", QKeySequence.StandardKey.Redo),
            ("Cortar", "cut", QKeySequence.StandardKey.Cut),
            ("Copiar", "copy", QKeySequence.StandardKey.Copy),
            ("Pegar", "paste", QKeySequence.StandardKey.Paste),
            ("Seleccionar todo", "selectAll", QKeySequence.StandardKey.SelectAll),
        ):
            self.acciones_editar[nombre] = self._accion(
                editar, titulo, atajo, lambda n=nombre: self._editar(n))
        editar.aboutToShow.connect(self._actualizar_acciones)

        ver = barra.addMenu("&Ver")
        for numero, (clave, _, titulo) in enumerate(PAGINAS, 1):
            self._accion(ver, f"{numero}. {titulo}", f"Ctrl+{numero}",
                         lambda k=clave: self.cambiar(k))
        ver.addSeparator()
        self._accion(ver, "Alternar claro/oscuro", "Ctrl+Shift+T", self.alternar_tema)
        grupo = QActionGroup(self)
        grupo.setExclusive(True)
        self.acciones_tema = {}
        for titulo, clave, atajo in (
            ("Seguir apariencia del sistema", "sistema", "Ctrl+F6"),
            ("Tema claro", "claro", "Ctrl+Shift+1"),
            ("Tema oscuro", "oscuro", "Ctrl+Shift+2"),
            ("Alto contraste", "contraste", "Shift+F6"),
        ):
            accion = self._accion(ver, titulo, atajo, lambda modo=clave: self.aplicar_tema(modo, persistir=True))
            accion.setCheckable(True)
            grupo.addAction(accion)
            self.acciones_tema[clave] = accion
        ver.addSeparator()
        self._accion(ver, "Aumentar texto", QKeySequence.StandardKey.ZoomIn, lambda: self.escalar_texto(.1))
        self._accion(ver, "Reducir texto", QKeySequence.StandardKey.ZoomOut, lambda: self.escalar_texto(-.1))
        self._accion(ver, "Restablecer texto", "Ctrl+0", lambda: self.escalar_texto(0, restablecer=True))
        self._accion(ver, "Preferencias de accesibilidad…", "Ctrl+,", self._mostrar_preferencias,
                     rol=QAction.PreferencesRole)
        ver.addSeparator()
        self.accion_sidebar = self._accion(ver, "Panel lateral", "Ctrl+Shift+B", self._alternar_sidebar)
        self.accion_sidebar.setCheckable(True)
        self.accion_sidebar.setChecked(self._sidebar_deseada)
        self.accion_asistente = self._accion(ver, "Asistente matemático", "Ctrl+L", self._alternar_asistente)
        self.accion_asistente.setCheckable(True)
        self.panel_asistente.visibilityChanged.connect(self.accion_asistente.setChecked)
        self.panel_asistente.visibilityChanged.connect(lambda _: self._adaptar_barra())
        self.panel_asistente.topLevelChanged.connect(self._panel_cambiado)

        ventana = barra.addMenu("&Ventana")
        ventana.addAction(nueva)
        self._accion(ventana, "Minimizar", "Ctrl+M", self.showMinimized)
        self._accion(ventana, "Pantalla completa", "F11", self._alternar_pantalla_completa)
        ventana.addAction(cerrar)

        ayuda = barra.addMenu("A&yuda")
        self._accion(ayuda, "Teoría de esta técnica", "F1", self._teoria_actual)
        self._accion(ayuda, "Atajos de teclado…", "F2", self._mostrar_atajos)
        self._accion(ayuda, "Acerca de AmPu…", "Shift+F1", self._acerca_de,
                     rol=QAction.AboutRole)
        archivo.aboutToShow.connect(self._actualizar_acciones)
        self._actualizar_acciones()

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if hasattr(self, "panel_asistente") and hasattr(self, "boton_abrir"):
            self._adaptar_barra()

    def _adaptar_barra(self):
        """Evita que un dock ancho recorte el análisis al ampliar el texto."""
        if self.panel_asistente.isVisible() and not self.panel_asistente.isFloating():
            umbral = max(1500, round(1050 * self.escala_efectiva))
            sobrepasa = (self.panel_asistente.mapToGlobal(QPoint(self.panel_asistente.width(), 0)).x()
                         > self.mapToGlobal(QPoint(self.width(), 0)).x())
            if sobrepasa and self.width() >= umbral:
                self.resizeDocks([self.panel_asistente], [450], Qt.Horizontal)
                sobrepasa = (self.panel_asistente.mapToGlobal(QPoint(self.panel_asistente.width(), 0)).x()
                             > self.mapToGlobal(QPoint(self.width(), 0)).x())
            if self.width() < umbral or sobrepasa:
                self.panel_asistente.setFloating(True)
        ancho = self.width() - (self.sidebar.width() if self.sidebar.isVisible() else 0)
        if self.panel_asistente.isVisible() and not self.panel_asistente.isFloating():
            ancho -= self.panel_asistente.width()
        compacto = ancho < max(850, round(650 * self.escala_efectiva))
        self.top_etiqueta.setText("MENÚS: ARCHIVO · VER" if compacto else "LABORATORIO  /  AMPU 3.0")
        for control in (self.boton_tema, self.boton_guardar, self.boton_abrir):
            control.setVisible(not compacto)

    def _panel_cambiado(self, flotante: bool):
        self.mensaje("Asistente en ventana separada para mantener legible el análisis." if flotante else
                     "Asistente acoplado a la ventana principal.")
        QTimer.singleShot(0, self._adaptar_barra)

    def _es_propio(self, widget):
        """Un dock flotante conserva su documento aunque sea otro top-level."""
        return (widget is not None and (widget is self or self.isAncestorOf(widget)
                or widget is self.panel_asistente or self.panel_asistente.isAncestorOf(widget)))

    def _registrar_foco(self, anterior, actual):
        # La barra de menús no sustituye el control que se estaba editando.
        if actual is not None and not isinstance(actual, QMenu) and actual is not self.menuBar() \
                and self._es_propio(actual):
            self._foco_previo = actual

    def _objetivo_edicion(self):
        widget = QApplication.focusWidget()
        if (widget is None or isinstance(widget, QMenu) or widget is self.menuBar()
                or not self._es_propio(widget)):
            widget = self._foco_previo
        if widget is not None and not (widget.isVisibleTo(self) or
                                       widget.isVisibleTo(self.panel_asistente)):
            return None
        while widget is not None and widget is not self:
            if isinstance(widget, TablaDatos):
                return widget
            if widget.__class__.__name__ == "QWebEngineView":
                return widget
            if all(hasattr(widget, metodo) for metodo in ("copy", "selectAll")):
                return widget
            widget = widget.parentWidget()
        return None

    def _actualizar_acciones(self):
        objetivo = self._objetivo_edicion()
        for nombre, accion in getattr(self, "acciones_editar", {}).items():
            disponible = objetivo is not None and (hasattr(objetivo, nombre) or
                isinstance(objetivo, TablaDatos) and nombre in ("copy", "paste", "selectAll") or
                objetivo.__class__.__name__ == "QWebEngineView" and nombre in ("copy", "paste", "cut", "selectAll"))
            if isinstance(objetivo, TablaDatos):
                if nombre == "undo":
                    disponible = objetivo.puede_deshacer()
                elif nombre == "redo":
                    disponible = objetivo.puede_rehacer()
            elif objetivo is not None:
                if nombre in ("undo", "redo"):
                    if hasattr(objetivo, "isUndoAvailable"):
                        disponible = disponible and (objetivo.isUndoAvailable() if nombre == "undo"
                                                     else objetivo.isRedoAvailable())
                    elif hasattr(objetivo, "document"):
                        documento = objetivo.document()
                        disponible = disponible and (documento.isUndoAvailable() if nombre == "undo"
                                                     else documento.isRedoAvailable())
                if nombre in ("cut", "paste", "undo", "redo") and hasattr(objetivo, "isReadOnly"):
                    disponible = disponible and not objetivo.isReadOnly()
            accion.setEnabled(disponible)
        exportable = (self.actual != "teoria" and self.vista.ultimo is not None
                      and not self.vista._desactualizado)
        for accion in getattr(self, "acciones_exportar", {}).values():
            accion.setEnabled(exportable)
        if hasattr(self, "boton_exportar"):
            self.boton_exportar.setEnabled(exportable)

    def _editar(self, nombre: str):
        objetivo = self._objetivo_edicion()
        if objetivo is None:
            return
        if isinstance(objetivo, TablaDatos):
            if nombre in ("copy", "paste"):
                getattr(objetivo, "copiar" if nombre == "copy" else "pegar")()
            elif nombre in ("undo", "redo", "selectAll"):
                getattr(objetivo, nombre)()
        elif objetivo.__class__.__name__ == "QWebEngineView":
            from PySide6.QtWebEngineCore import QWebEnginePage
            accion = {"cut": QWebEnginePage.Cut, "copy": QWebEnginePage.Copy,
                      "paste": QWebEnginePage.Paste, "selectAll": QWebEnginePage.SelectAll}.get(nombre)
            if accion is not None:
                objetivo.page().triggerAction(accion)
        elif hasattr(objetivo, nombre):
            getattr(objetivo, nombre)()
        self._actualizar_acciones()

    def _teoria_actual(self):
        self.abrir_teoria(self.vista.clave_teoria() if hasattr(self.vista, "clave_teoria") else "binomial")

    def _mostrar_atajos(self):
        QMessageBox.information(self, "Atajos de AmPu",
            "Ctrl+1…7: secciones · F1: teoría · Ctrl+L: asistente\n"
            "Ctrl+S/O: guardar/abrir · Ctrl+E/P: Excel/PDF · Ctrl+Z/Ctrl+Shift+Z: deshacer/rehacer\n"
            "Ctrl++/Ctrl+-/Ctrl+0: tamaño del texto · Shift+F6: alto contraste · F11: pantalla completa.\n"
            "Los menús muestran los atajos nativos de esta plataforma.")

    def _mostrar_preferencias(self):
        """Diálogo breve de preferencias; macOS lo sitúa en el menú App."""
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Preferencias de accesibilidad · AmPu")
        formulario = QFormLayout(dialogo)
        tema = QComboBox()
        for titulo, clave in (("Seguir apariencia del sistema", "sistema"),
                              ("Claro", "claro"), ("Oscuro", "oscuro"),
                              ("Alto contraste", "contraste")):
            tema.addItem(titulo, clave)
        tema.setCurrentIndex(tema.findData(self.modo_tema))
        tema.setAccessibleName("Tema visual de AmPu")
        formulario.addRow("Apariencia", tema)
        tamano = QSpinBox()
        tamano.setRange(90, 200)
        tamano.setSingleStep(10)
        tamano.setSuffix(" %")
        tamano.setValue(round(100 * self.escala_fuente))
        tamano.setAccessibleName("Escala de texto de 90 a 200 por ciento")
        formulario.addRow("Tamaño de texto", tamano)
        info = QLabel("Sin animaciones automáticas; las entradas y gráficas siguen siendo editables.")
        info.setWordWrap(True)
        formulario.addRow("Movimiento", info)
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)
        formulario.addWidget(botones)
        if dialogo.exec() == QDialog.Accepted:
            self.escala_fuente = tamano.value() / 100
            self.preferencias.setValue("interfaz/escala", self.escala_fuente)
            self.aplicar_tema(tema.currentData(), persistir=True)

    def _acerca_de(self):
        QMessageBox.information(self, "Acerca de AmPu", "AmPu 3.0 · Probabilidad y estadística sin conexión.\n"
                                "Motor SciPy/NumPy; teoría KaTeX con MathML. El asistente no es un CAS simbólico.")

    def _alternar_pantalla_completa(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def _actualizar_sidebar(self):
        visible = self._sidebar_deseada and (self.escala_efectiva < 1.4 or self._sidebar_fijada)
        self.sidebar.setVisible(visible)
        self.accion_sidebar.setChecked(visible)
        self.accion_sidebar.setToolTip("En ampliación alta se repliega para dejar espacio; activa para fijarlo.")
        self._adaptar_barra()

    def _alternar_sidebar(self):
        self._sidebar_deseada = not self.sidebar.isVisible()
        self._sidebar_fijada = self._sidebar_deseada
        self._actualizar_sidebar()
        self.preferencias.setValue("interfaz/panel_lateral", self._sidebar_deseada)
        self.preferencias.setValue("interfaz/panel_lateral_forzado", self._sidebar_fijada)

    def nueva_ventana(self):
        nueva = VentanaPrincipal(self.preferencias)
        pantalla = self.screen()
        if pantalla is not None:
            disponible = pantalla.availableGeometry()
            destino = self.pos() + QPoint(32, 32)
            nueva.move(max(disponible.left(), min(destino.x(), disponible.right() - 120)),
                       max(disponible.top(), min(destino.y(), disponible.bottom() - 120)))
        nueva.show()
        nueva.raise_()
        nueva.activateWindow()
        return nueva

    def _salir(self):
        """Confirma TODAS las ventanas antes de cerrar ninguna de ellas."""
        ventanas = list(self._instancias)
        for ventana in ventanas:
            if not ventana._permitir_descartar("Salir de AmPu"):
                return
        for ventana in ventanas:
            ventana._cierre_confirmado = True
        for ventana in ventanas:
            ventana.close()
        QApplication.quit()

    @property
    def vista(self) -> QWidget:
        """Vista actualmente visible (la teoría se crea solo cuando se abre)."""
        return self.vistas[self.actual]

    def cambiar(self, clave: str):
        """Selecciona módulo y destaca su botón en la navegación."""
        if clave == "teoria" and clave not in self.vistas:
            try:
                from ampu.ui.vistas.teoria import VistaTeoria  # WebEngine carga bajo demanda
                self.vistas[clave] = VistaTeoria(self.tema_actual)
                self.vistas[clave].ajustar_escala(self.escala_efectiva)
                self.contenedores[clave] = self.vistas[clave]  # Chromium tiene scroll propio.
                self.pila.addWidget(self.vistas[clave])
            except Exception:
                LOG.exception("No se pudo iniciar QtWebEngine")
                self._error("No se pudo abrir Teoría. Instala las bibliotecas nativas de QtWebEngine "
                            "(NSS, X11, OpenGL) indicadas en el README.")
                return False
        if clave not in self.vistas:
            return False
        self.actual = clave
        self.pila.setCurrentWidget(self.contenedores[clave])
        for nombre, boton in self.botones.items():
            boton.setChecked(nombre == clave)
            boton.setObjectName("NavActive" if nombre == clave else "NavButton")
            boton.style().unpolish(boton)
            boton.style().polish(boton)
        self._actualizar_acciones()
        self.mensaje(f"{next(t for k, _, t in PAGINAS if k == clave)} · AmPu 3.0")
        QTimer.singleShot(0, self._enfocar_actual)
        return True

    def _enfocar_actual(self):
        """Al navegar con menú o atajo, deja el foco en el primer campo útil."""
        vista = self.vista
        for control in vista.findChildren(QWidget):
            if isinstance(control, (QLineEdit, QComboBox, QPlainTextEdit, QAbstractSpinBox)) \
                    and control.isVisible() and control.isEnabled():
                control.setFocus(Qt.ShortcutFocusReason)
                self._foco_previo = control
                return

    def abrir_teoria(self, clave: str):
        """Navega a la lección de un módulo sin depender de HTML heredado."""
        try:
            if self.cambiar("teoria"):
                self.vistas["teoria"].seleccionar(clave)
        except Exception:
            LOG.exception("No se pudo cargar teoría %s", clave)
            self._error("La lección no se pudo abrir. Consulta el registro de errores.")

    def _marcar_sesion(self, *_):
        """No confundir preferencias con datos de la sesión: entradas y tablas sí ensucian."""
        if not self._abriendo_sesion:
            self._cambios_sin_guardar = True
            self.setWindowModified(True)

    def _sesion_guardada(self):
        self._cambios_sin_guardar = False
        self.setWindowModified(False)

    def mensaje(self, texto: str):
        """Comunica el estado sin modal; habilita exportar solo si hay resultados."""
        self.statusBar().showMessage(texto, 9000)
        self._actualizar_acciones()

    def _trabajo_finalizado(self):
        if (not any(vista._ocupado for vista in self.vistas.values() if hasattr(vista, "_ocupado"))
                and self.statusBar().currentMessage().startswith(("Ejecutando", "Calculando"))):
            self.mensaje("Cálculos terminados; resultados y tablas disponibles.")

    def _tema_sistema_cambiado(self, *_):
        if self.modo_tema == "sistema" and self._apariencia_sistema() != self.tema_actual:
            self.aplicar_tema("sistema")

    def _fuente_sistema_cambiada(self, *_):
        nueva = min(2.0, self.escala_fuente * factor_fuente_sistema(
            QApplication.instance().font().pointSizeF(), sys.platform == "darwin"))
        if abs(nueva - self.escala_efectiva) > .01:
            self.aplicar_tema(self.modo_tema)

    @staticmethod
    def _apariencia_sistema():
        """Respeta el alto contraste nativo de Windows y la paleta Qt clara/oscura."""
        if alto_contraste_windows():
            return "contraste"
        try:
            if QApplication.instance().styleHints().colorScheme() == Qt.ColorScheme.Dark:
                return "oscuro"
        except AttributeError:
            pass
        return "claro"

    def aplicar_tema(self, tema: str, *, persistir: bool = False):
        """Sincroniza QSS, gráficos, teoría y fórmula; no anima las transiciones."""
        if tema not in ("sistema", "claro", "oscuro", "contraste"):
            return
        self.modo_tema = tema
        efectivo = self._apariencia_sistema() if tema == "sistema" else tema
        self.tema_actual = efectivo
        self.escala_efectiva = min(2.0, max(.9, self.escala_fuente * factor_fuente_sistema(
            QApplication.instance().font().pointSizeF(), sys.platform == "darwin")))
        base = "oscuro" if efectivo == "contraste" else efectivo
        css = (ESTILOS / f"{base}.qss").read_text(encoding="utf-8")
        if efectivo == "contraste":
            css += "\n" + (ESTILOS / "contraste.qss").read_text(encoding="utf-8")
        css = re.sub(r"(font-size:\s*)(\d+(?:\.\d+)?)px",
                     lambda m: f"{m.group(1)}{max(10, round(float(m.group(2)) * self.escala_efectiva))}px", css)
        QApplication.instance().setStyleSheet(css)
        self.boton_tema.setText("☀  Tema claro" if efectivo == "oscuro" else
                                 "☾  Tema oscuro" if efectivo == "claro" else "◐  Alto contraste")
        self.acciones_tema[tema].setChecked(True)
        self.asistente.actualizar_tema(efectivo, self.escala_efectiva)
        for vista in self.vistas.values():
            if hasattr(vista, "ajustar_escala"):
                vista.ajustar_escala(self.escala_efectiva)
            if hasattr(vista, "grafico"):
                vista.grafico.tema(efectivo != "claro", efectivo == "contraste")
                if vista.grafico._escala != self.escala_efectiva:
                    vista.grafico.escalar_texto(self.escala_efectiva)
        if "teoria" in self.vistas:
            self.vistas["teoria"].tema(efectivo)
        if persistir:
            self.preferencias.setValue("interfaz/tema", tema)
        self._actualizar_sidebar()
        self.mensaje(f"Apariencia {tema} activada; texto al {round(self.escala_fuente * 100)} %.")
        for otra in self._instancias - {self}:
            if otra.modo_tema != tema or otra.escala_fuente != self.escala_fuente:
                otra.escala_fuente = self.escala_fuente
                otra.aplicar_tema(tema)

    def alternar_tema(self):
        self.aplicar_tema("oscuro" if self.tema_actual == "claro" else "claro", persistir=True)

    def escalar_texto(self, paso: float, *, restablecer: bool = False):
        """Escala el QSS y la tipografía de los gráficos sin recargar datos."""
        self.escala_fuente = 1.0 if restablecer else max(.9, min(2.0, round(self.escala_fuente + paso, 2)))
        self.preferencias.setValue("interfaz/escala", self.escala_fuente)
        self.aplicar_tema(self.modo_tema)

    def _alternar_asistente(self):
        if self.panel_asistente.isVisible():
            self.panel_asistente.hide()
        else:
            self.calculadora()

    def calculadora(self):
        """Muestra el panel acoplable existente sin bloquear la ventana principal."""
        self.panel_asistente.show()
        self.panel_asistente.raise_()
        QTimer.singleShot(0, self._adaptar_barra)  # Qt puede relayoutar el dock tras visibilityChanged.
        (self.asistente.latex if self.asistente.pestanas.currentIndex() else self.asistente.entrada).setFocus(
            Qt.ShortcutFocusReason)

    def _permitir_descartar(self, accion: str) -> bool:
        """Confirmación solo al perder trabajo. Offscreen no tiene diálogo interactivo."""
        if not self._cambios_sin_guardar or QApplication.platformName() == "offscreen":
            return True
        eleccion = QMessageBox.warning(
            self, "Cambios de sesión sin guardar",
            f"{accion} puede perder entradas, tablas o fórmulas no guardadas.\n"
            "¿Guardar una sesión antes de continuar?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if eleccion == QMessageBox.Save:
            return self.guardar_sesion()
        return eleccion == QMessageBox.Discard

    def closeEvent(self, event):
        """Pregunta por trabajo sin guardar y solo entonces persiste geometría."""
        if not self._cierre_confirmado and not self._permitir_descartar("Cerrar esta ventana"):
            event.ignore()
            return
        self._cierre_confirmado = False
        self.preferencias.setValue("ventana/geometria", self.saveGeometry())
        self.preferencias.setValue("ventana/paneles", self.saveState())
        self.preferencias.setValue("interfaz/panel_lateral", self._sidebar_deseada)
        self.preferencias.setValue("interfaz/panel_lateral_forzado", self._sidebar_fijada)
        self.preferencias.sync()
        # Un QDockWidget flotante es un top-level; no debe sobrevivir huérfano
        # cuando se cierra la ventana a la que pertenecen sus resultados.
        if self.panel_asistente.isFloating():
            self.panel_asistente.close()
        self._instancias.discard(self)
        super().closeEvent(event)

    def _error(self, mensaje: str):
        """Traduce excepciones para el usuario sin traza visible."""
        self.mensaje(mensaje)
        QMessageBox.warning(self, "AmPu 3.0", mensaje)

    def exportar(self, formato: str):
        """Usa solo la fachada común de E/S para todos los módulos."""
        if self.actual == "teoria":
            self._error("Regresa a un módulo de análisis para exportar resultados.")
            return
        vista = self.vista
        if vista._desactualizado:
            self._error("Las entradas cambiaron desde el último resultado. Recalcula antes de exportar.")
            return
        tablas = vista.tablas_exportables()
        if not tablas:
            self._error("Primero calcula un resultado para exportar.")
            return
        opciones = {"excel": ("Archivos Excel (*.xlsx)", "xlsx"), "csv": ("Archivos CSV (*.csv)", "csv"),
                    "png": ("Imágenes PNG (*.png)", "png"), "pdf": ("Documentos PDF (*.pdf)", "pdf")}
        if formato not in opciones:
            self._error("Formato de exportación no reconocido.")
            return
        filtro, extension = opciones[formato]
        destino, _ = QFileDialog.getSaveFileName(self, "Exportar resultados", f"AmPu3_{self.actual}.{extension}", filtro)
        if not destino:
            return
        try:
            if formato == "excel":
                ruta = io.excel(tablas, destino)
            elif formato == "csv":
                ruta = io.csv(vista.tabla.datos(), destino)
            elif formato == "png":
                ruta = io.png(vista.grafico.figura, destino)
            else:
                resumen = vista.resumen_exportable() + "\nDescripción gráfica: " + vista.grafico.descripcion.text()
                ruta = io.pdf(destino, f"AmPu 3.0 · {self.actual.title()}", resumen,
                              tablas, vista.grafico.figura, extraer_formula(vista.clave_teoria()))
            self.mensaje(f"Exportación completada: {ruta}")
        except Exception:
            LOG.exception("Error al exportar %s", formato)
            self._error("No se pudo exportar. Verifica el destino y consulta el registro de errores.")

    def guardar_sesion(self) -> bool:
        """Persiste entradas aun incompletas; devuelve False si se canceló o falló."""
        destino, _ = QFileDialog.getSaveFileName(self, "Guardar sesión", "sesion_ampu.json", "Sesiones AmPu (*.json)")
        if not destino:
            return False
        try:
            estado = {"modulo": self.actual, "tema": self.modo_tema,
                      "asistente": self.asistente.estado(),
                      "vistas": {clave: vista.estado() for clave, vista in self.vistas.items()}}
            ruta = io.guardar(estado, destino)
            self._sesion_guardada()
            self.mensaje(f"Sesión guardada: {ruta}")
            return True
        except Exception:
            LOG.exception("Error al guardar sesión")
            self._error("No se pudo guardar la sesión. Revisa los campos y el destino.")
            return False

    def abrir_sesion(self) -> bool:
        """Valida JSON, avisa si hay trabajo sin guardar y revierte una carga fallida."""
        origen, _ = QFileDialog.getOpenFileName(self, "Abrir sesión", "", "Sesiones AmPu (*.json)")
        if not origen:
            return False
        anterior = None
        aplicado = False
        try:
            estado = io.cargar(origen)
            vistas = estado.get("vistas", {})
            modulo = estado.get("modulo", "distribuciones")
            if (estado.get("tema", "claro") not in ("claro", "oscuro", "contraste", "sistema")
                    or not isinstance(vistas, dict)
                    or any(not isinstance(datos, dict) for datos in vistas.values())
                    or modulo not in self.vistas and modulo != "teoria"
                    or not isinstance(estado.get("asistente", {}), dict)):
                raise ValueError("El contenido de la sesión no sigue el esquema de la interfaz.")
            if not self._permitir_descartar("Abrir otra sesión"):
                return False
            anterior = {"tema": self.modo_tema, "modulo": self.actual,
                        "asistente": self.asistente.estado(),
                        "vistas": {clave: vista.estado() for clave, vista in self.vistas.items()}}
            self._abriendo_sesion = True
            aplicado = True
            self.aplicar_tema(estado.get("tema", "claro"))
            self.asistente.restaurar(estado.get("asistente", {}))
            for clave, datos in vistas.items():
                if clave == "teoria" and clave not in self.vistas:
                    if not self.cambiar("teoria"):
                        raise RuntimeError("No se pudo abrir la teoría de esta sesión")
                if clave in self.vistas:
                    self.vistas[clave].restaurar(datos)
            if not self.cambiar(modulo):
                raise ValueError("La vista principal de la sesión no está disponible")
            self._sesion_guardada()
            self.mensaje(f"Sesión restaurada: {origen}")
            return True
        except Exception:
            LOG.exception("No se pudo abrir sesión")
            if aplicado and anterior is not None:
                try:
                    self.aplicar_tema(anterior["tema"])
                    self.asistente.restaurar(anterior["asistente"])
                    for clave, datos in anterior["vistas"].items():
                        if clave in self.vistas:
                            self.vistas[clave].restaurar(datos)
                    self.cambiar(anterior["modulo"])
                except Exception:
                    LOG.exception("La reversión de la carga fallida no fue completa")
            self._error("El archivo no es una sesión válida o contiene datos incompatibles. "
                        "El trabajo anterior se mantuvo cuando fue posible.")
            return False
        finally:
            self._abriendo_sesion = False
