"""Ventana principal: navegación, tema, sesiones y exportación unificada."""

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QMessageBox, QPushButton, QStackedWidget, QStatusBar,
    QToolButton, QVBoxLayout, QWidget,
)

from ampu.docs.teoria import extraer_formula
from ampu.io import ServicioExportacion as io
from ampu.ui.vistas.descriptiva import VistaDescriptiva
from ampu.ui.vistas.distribuciones import VistaDistribuciones
from ampu.ui.vistas.inferencia import VistaInferencia
from ampu.ui.vistas.muestreo import VistaMuestreo
from ampu.ui.vistas.probabilidad import VistaProbabilidad
from ampu.ui.vistas.simulacion import VistaSimulacion
from ampu.ui.widgets.calculadora import Calculadora

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
    """Menú lateral por módulos, informes y mensajes sin tracebacks en pantalla."""

    def __init__(self):
        """Arranca con distribuciones, carga WebEngine solo al consultar teoría."""
        super().__init__()
        self.setWindowTitle("AmPu 3.0 · Laboratorio de estadística")
        self.setWindowIcon(QIcon(str(ICONO)))
        self.resize(1450, 900)
        self.setMinimumSize(1030, 680)
        self.tema_actual = "claro"
        self.actual = "distribuciones"
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("AmPu 3.0 · Listo para explorar", 6000)
        raiz = QWidget()
        raiz.setObjectName("Raiz")
        self.setCentralWidget(raiz)
        fila = QHBoxLayout(raiz)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(218)
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
        calculadora = QPushButton("⌗   Calculadora")
        calculadora.setObjectName("NavButton")
        calculadora.clicked.connect(self.calculadora)
        nav.addWidget(calculadora)
        fila.addWidget(sidebar)

        columna = QWidget()
        contenido = QVBoxLayout(columna)
        contenido.setContentsMargins(0, 0, 0, 0)
        contenido.setSpacing(0)
        fila.addWidget(columna, 1)
        topbar = QWidget()
        topbar.setMinimumHeight(57)
        top = QHBoxLayout(topbar)
        top.setContentsMargins(25, 8, 25, 8)
        top.addWidget(self._top_label("LABORATORIO  /  AMPU 3.0"))
        top.addStretch()
        self.boton_tema = QPushButton("☾  Tema oscuro")
        self.boton_tema.setObjectName("Secondary")
        self.boton_tema.clicked.connect(self.alternar_tema)
        top.addWidget(self.boton_tema)
        btn_guardar = QPushButton("Guardar sesión")
        btn_guardar.setObjectName("Secondary")
        btn_guardar.clicked.connect(self.guardar_sesion)
        top.addWidget(btn_guardar)
        btn_abrir = QPushButton("Abrir")
        btn_abrir.setObjectName("Quiet")
        btn_abrir.clicked.connect(self.abrir_sesion)
        top.addWidget(btn_abrir)
        btn_exportar = QToolButton()
        btn_exportar.setText("Exportar  ▾")
        btn_exportar.setObjectName("Primary")
        btn_exportar.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(btn_exportar)
        for etiqueta, formato in (("Excel · todas las tablas", "excel"), ("CSV · tabla visible", "csv"),
                                  ("PNG · gráfico actual", "png"), ("PDF · informe completo", "pdf")):
            accion = menu.addAction(etiqueta)
            accion.triggered.connect(lambda checked=False, fmt=formato: self.exportar(fmt))
        btn_exportar.setMenu(menu)
        top.addWidget(btn_exportar)
        contenido.addWidget(topbar)
        self.pila = QStackedWidget()
        contenido.addWidget(self.pila, 1)
        self.vistas: dict[str, QWidget] = {
            "distribuciones": VistaDistribuciones(), "muestreo": VistaMuestreo(),
            "descriptiva": VistaDescriptiva(), "probabilidad": VistaProbabilidad(),
            "inferencia": VistaInferencia(), "simulacion": VistaSimulacion(),
        }
        for vista in self.vistas.values():
            self.pila.addWidget(vista)
            vista.aviso.connect(self.mensaje)
            vista.abrir_teoria.connect(self.abrir_teoria)
        self._atajos()
        self.aplicar_tema("claro")
        self.cambiar("distribuciones")

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

    def _atajos(self):
        """Atajos documentados para navegación y E/S."""
        for j, (clave, _, _) in enumerate(PAGINAS, 1):
            QShortcut(QKeySequence(f"Ctrl+{j}"), self, activated=lambda k=clave: self.cambiar(k))
        for texto, funcion in (("Ctrl+S", self.guardar_sesion), ("Ctrl+O", self.abrir_sesion),
                               ("Ctrl+E", lambda: self.exportar("excel")), ("Ctrl+P", lambda: self.exportar("pdf")),
                               ("Ctrl+Shift+T", self.alternar_tema), ("Ctrl+L", self.calculadora),
                               ("F1", lambda: self.abrir_teoria(self.vista.clave_teoria() if hasattr(self.vista, "clave_teoria") else "binomial"))):
            QShortcut(QKeySequence(texto), self, activated=funcion)

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
                self.pila.addWidget(self.vistas[clave])
            except Exception:
                LOG.exception("No se pudo iniciar QtWebEngine")
                self._error("No se pudo abrir Teoría. Instala las bibliotecas nativas de QtWebEngine "
                            "(NSS, X11, OpenGL) indicadas en el README.")
                return False
        if clave not in self.vistas:
            return False
        self.actual = clave
        self.pila.setCurrentWidget(self.vistas[clave])
        for nombre, boton in self.botones.items():
            boton.setObjectName("NavActive" if nombre == clave else "NavButton")
            boton.style().unpolish(boton)
            boton.style().polish(boton)
        self.mensaje(f"{next(t for k, _, t in PAGINAS if k == clave)} · AmPu 3.0")
        return True

    def abrir_teoria(self, clave: str):
        """Navega a la lección de un módulo sin depender de HTML heredado."""
        try:
            if self.cambiar("teoria"):
                self.vistas["teoria"].seleccionar(clave)
        except Exception:
            LOG.exception("No se pudo cargar teoría %s", clave)
            self._error("La lección no se pudo abrir. Consulta el registro de errores.")

    def mensaje(self, texto: str):
        """Muestra estado transitorio sin bloquear con diálogos."""
        self.statusBar().showMessage(texto, 9000)

    def aplicar_tema(self, tema: str):
        """Sincroniza QSS, Matplotlib y el WebEngine de las lecciones."""
        self.tema_actual = tema
        QApplication.instance().setStyleSheet((ESTILOS / f"{tema}.qss").read_text(encoding="utf-8"))
        self.boton_tema.setText("☀  Tema claro" if tema == "oscuro" else "☾  Tema oscuro")
        for vista in self.vistas.values():
            if hasattr(vista, "grafico"):
                vista.grafico.tema(tema == "oscuro")
        if "teoria" in self.vistas:
            self.vistas["teoria"].tema(tema)
        self.mensaje(f"Tema {tema} activado.")

    def alternar_tema(self):
        """Conmuta entre paletas de contraste AA."""
        self.aplicar_tema("oscuro" if self.tema_actual == "claro" else "claro")

    def calculadora(self):
        """Abre herramienta científica interna, sin ejecutar aplicaciones del SO."""
        Calculadora(self).exec()

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
                ruta = io.pdf(destino, f"AmPu 3.0 · {self.actual.title()}", vista.resumen_exportable(),
                              tablas, vista.grafico.figura, extraer_formula(vista.clave_teoria()))
            self.mensaje(f"Exportación completada: {ruta}")
        except Exception:
            LOG.exception("Error al exportar %s", formato)
            self._error("No se pudo exportar. Verifica el destino y consulta el registro de errores.")

    def guardar_sesion(self):
        """Persiste parámetros, semillas, entradas, tablas y tema en JSON."""
        destino, _ = QFileDialog.getSaveFileName(self, "Guardar sesión", "sesion_ampu.json", "Sesiones AmPu (*.json)")
        if not destino:
            return
        try:
            estado = {"modulo": self.actual, "tema": self.tema_actual,
                      "vistas": {clave: vista.estado() for clave, vista in self.vistas.items()}}
            ruta = io.guardar(estado, destino)
            self.mensaje(f"Sesión guardada: {ruta}")
        except Exception:
            LOG.exception("Error al guardar sesión")
            self._error("No se pudo guardar la sesión. Revisa los campos y el destino.")

    def abrir_sesion(self):
        """Carga un esquema conocido y reconstruye cada vista con su semilla."""
        origen, _ = QFileDialog.getOpenFileName(self, "Abrir sesión", "", "Sesiones AmPu (*.json)")
        if not origen:
            return
        try:
            estado = io.cargar(origen)
            vistas = estado.get("vistas", {})
            if (estado.get("tema", "claro") not in ("claro", "oscuro")
                    or not isinstance(vistas, dict)
                    or any(not isinstance(datos, dict) for datos in vistas.values())
                    or not isinstance(estado.get("modulo", "distribuciones"), str)):
                raise ValueError("El contenido de la sesión no sigue el esquema de la interfaz.")
            self.aplicar_tema(estado.get("tema", "claro"))
            for clave, datos in vistas.items():
                if clave == "teoria" and clave not in self.vistas:
                    self.cambiar("teoria")
                if clave in self.vistas:
                    self.vistas[clave].restaurar(datos)
            self.cambiar(estado.get("modulo", "distribuciones"))
            self.mensaje(f"Sesión restaurada: {origen}")
        except Exception:
            LOG.exception("No se pudo abrir sesión")
            self._error("El archivo no es una sesión válida o contiene datos incompatibles.")
