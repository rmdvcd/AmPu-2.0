"""Lecciones Markdown y LaTeX renderizadas con KaTeX local en QWebEngineView."""

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QShortcut, QKeySequence
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from ampu.docs.teoria import DOCUMENTOS, listar_teoria, renderizar
from ampu.ui.widgets.comunes import encabezado, etiqueta, marco


class PaginaTeoria(QWebEnginePage):
    """Abre enlaces externos fuera de la lección y evita navegación local ajena."""

    def acceptNavigationRequest(self, url, tipo, es_marco_principal):
        """Permite anclas y recursos locales, delega enlaces externos al SO."""
        if url.scheme() in ("http", "https") and tipo == QWebEnginePage.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, tipo, es_marco_principal)


class VistaTeoria(QWidget):
    """Índice automático, búsqueda Qt, zoom y sincronización claro/oscuro."""

    def __init__(self, tema: str = "claro", parent=None):
        """Crea WebEngine solo al entrar en Teoría para mantener arranque ágil."""
        super().__init__(parent)
        self.tema_actual = tema
        self.zoom = 1.0
        root = QVBoxLayout(self)
        root.setContentsMargins(25, 24, 25, 20)
        root.setSpacing(12)
        root.addWidget(encabezado("07  /  BIBLIOTECA INTERACTIVA", "Teoría y fórmulas", "57 lecciones sin conexión · Markdown, KaTeX y un índice navegable por secciones."))
        controls, bar = marco("Card", 10)
        linea = QHBoxLayout()
        linea.addWidget(etiqueta("LECCIÓN", "Eyebrow"))
        self.selector = QComboBox()
        for clave, titulo in listar_teoria():
            self.selector.addItem(titulo, clave)
        self.selector.setMinimumWidth(220)
        self.selector.currentIndexChanged.connect(self._cargar)
        linea.addWidget(self.selector, 2)
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar dentro de la lección…  Ctrl+F")
        self.busqueda.returnPressed.connect(self.buscar)
        linea.addWidget(self.busqueda, 1)
        prev = QPushButton("↑")
        prev.setObjectName("Quiet")
        prev.setToolTip("Resultado anterior")
        prev.clicked.connect(self.buscar_anterior)
        linea.addWidget(prev)
        next_ = QPushButton("↓")
        next_.setObjectName("Quiet")
        next_.setToolTip("Resultado siguiente")
        next_.clicked.connect(self.buscar)
        linea.addWidget(next_)
        for texto, paso in (("A−", -.1), ("A+", .1)):
            boton = QPushButton(texto)
            boton.setObjectName("Secondary")
            boton.clicked.connect(lambda checked=False, d=paso: self.zoom_cambiar(d))
            linea.addWidget(boton)
        bar.addLayout(linea)
        root.addWidget(controls)
        self.navegador = QWebEngineView()
        self.navegador.setPage(PaginaTeoria(self.navegador))
        self.navegador.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.navegador.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.navegador.setContextMenuPolicy(Qt.DefaultContextMenu)
        root.addWidget(self.navegador, 1)
        QShortcut(QKeySequence.Find, self, activated=self.busqueda.setFocus)
        QShortcut(QKeySequence.ZoomIn, self, activated=lambda: self.zoom_cambiar(.1))
        QShortcut(QKeySequence.ZoomOut, self, activated=lambda: self.zoom_cambiar(-.1))
        self._cargar()

    def _cargar(self):
        """Convierte Markdown cada vez para reflejar el tema activo."""
        clave = self.selector.currentData()
        if clave:
            self.navegador.setHtml(renderizar(clave, self.tema_actual), QUrl.fromLocalFile(str(DOCUMENTOS) + "/"))

    def seleccionar(self, clave: str):
        """Abre una lección por clave estable, solicitada desde otro módulo."""
        index = self.selector.findData(clave)
        if index < 0:
            raise ValueError(f"No hay una lección para {clave}.")
        if index == self.selector.currentIndex():
            self._cargar()
        else:
            self.selector.setCurrentIndex(index)

    def tema(self, valor: str):
        """Sincroniza la paleta web con el QSS de la ventana principal."""
        if valor != self.tema_actual:
            self.tema_actual = valor
            self._cargar()

    def buscar(self):
        """Busca texto dentro del DOM con API nativa de QWebEngineView."""
        self.navegador.findText(self.busqueda.text())

    def buscar_anterior(self):
        """Busca coincidencia anterior del texto del usuario."""
        self.navegador.findText(self.busqueda.text(), QWebEnginePage.FindFlag.FindBackward)

    def zoom_cambiar(self, delta: float):
        """Zoom persistente dentro de márgenes de legibilidad."""
        self.zoom = max(.65, min(2.0, round(self.zoom + delta, 2)))
        self.navegador.setZoomFactor(self.zoom)

    def estado(self) -> dict:
        """Lección y factor de zoom actual."""
        return {"clave": self.selector.currentData(), "zoom": self.zoom}

    def restaurar(self, d: dict):
        """Carga lección y escala previamente guardadas."""
        self.seleccionar(d.get("clave", "binomial"))
        self.zoom = max(.65, min(2, float(d.get("zoom", 1))))
        self.navegador.setZoomFactor(self.zoom)
