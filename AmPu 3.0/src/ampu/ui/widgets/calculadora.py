"""Asistente matemático no modal: aritmética explicada y LaTeX editable."""

import re

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication, QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPlainTextEdit, QPushButton, QStackedWidget,
    QTabWidget, QVBoxLayout, QWidget,
)

from ampu.core.errores import ParametroInvalidoError
from ampu.core.estadistica.calculadora import explicar
from ampu.docs.expresiones import RECURSOS, previsualizar_latex
from ampu.ui.widgets.editor_matematico import EditorLatex

_PALETA = {
    "Álgebra": [("Fracción", r"\frac{a}{b}", "a"), ("Raíz", r"\sqrt{x}", "x"),
                 ("Potencia", "x^{n}", "n")],
    "Cálculo": [("Integral", r"\int_{a}^{b} f(x)\,dx", "f(x)"),
                ("Sumatoria", r"\sum_{i=1}^{n} x_i", "x_i")],
    "Matrices": [("Matriz 2×2", r"\begin{pmatrix}a&b\\c&d\end{pmatrix}", "a")],
    "Griego": [("Alfa", r"\alpha", None), ("Sigma", r"\sigma", None),
               ("Media", r"\mu", None)],
}


class Calculadora(QWidget):
    """Herramienta persistente y acoplable; no promete resolver LaTeX arbitrario."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAccessibleName("Asistente matemático")
        self.tema_actual = "claro"
        self.escala_actual = 1.0
        self._navegador = None
        self._resultado: float | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        self.pestanas = QTabWidget()
        self.pestanas.addTab(self._panel_calculo(), "Cálculo explicado")
        self.pestanas.addTab(self._panel_latex(), "Fórmula LaTeX")
        self.pestanas.currentChanged.connect(self._cambio_pestana)
        root.addWidget(self.pestanas)
        self._debounce = QTimer(self)
        self._debounce.setInterval(220)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._previsualizar)

    def _panel_calculo(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(self._texto("Solo aritmética numérica; sin resolver ecuaciones simbólicas. "
                                    "Trigonometría en radianes, log base 10 y ln natural."))
        self.entrada = QLineEdit()
        self.entrada.setAccessibleName("Expresión aritmética")
        self.entrada.setPlaceholderText("sqrt(2) + sin(pi/2)")
        self.entrada.returnPressed.connect(self._evaluar)
        self.entrada.textEdited.connect(self._limpiar_resultado)
        layout.addWidget(self.entrada)
        acciones = QHBoxLayout()
        boton = QPushButton("Calcular · Intro")
        boton.setObjectName("Primary")
        boton.clicked.connect(self._evaluar)
        acciones.addWidget(boton)
        copiar = QPushButton("Copiar resultado")
        copiar.setObjectName("Secondary")
        copiar.clicked.connect(self.copiar_resultado)
        acciones.addWidget(copiar)
        layout.addLayout(acciones)
        self.respuesta = QLabel("Resultado final: —")
        self.respuesta.setObjectName("H2")
        self.respuesta.setWordWrap(True)
        self.respuesta.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.respuesta.setAccessibleName("Resultado final del cálculo")
        layout.addWidget(self.respuesta)
        self.interpretacion = self._texto("Entrada interpretada: —")
        layout.addWidget(self.interpretacion)
        layout.addWidget(self._texto("Pasos reales del motor (sustituciones numéricas, no álgebra simbólica):"))
        self.pasos = QPlainTextEdit()
        self.pasos.setReadOnly(True)
        self.pasos.setAccessibleName("Pasos numerados de cálculo y justificaciones")
        self.pasos.setPlaceholderText("Pulsa Calcular para ver cómo se obtuvo el resultado.")
        layout.addWidget(self.pasos, 1)
        layout.addWidget(self._texto("Historial de esta sesión · doble clic o Enter para reutilizar:"))
        self.historial = QListWidget()
        self.historial.setMaximumHeight(120)
        self.historial.setAccessibleName("Historial de expresiones y resultados")
        self.historial.itemActivated.connect(self._reutilizar)
        self.historial.itemDoubleClicked.connect(self._reutilizar)
        layout.addWidget(self.historial)
        teclas = [["7", "8", "9", "/", "sqrt("], ["4", "5", "6", "*", "^"],
                  ["1", "2", "3", "-", "pi"], ["0", ".", "(", ")", "+"],
                  ["sin(", "cos(", "ln(", "log(", "="]]
        grid = QGridLayout()
        for row, fila in enumerate(teclas):
            for col, tecla in enumerate(fila):
                boton = QPushButton(tecla)
                boton.setAccessibleName("Calcular expresión" if tecla == "=" else f"Insertar {tecla}")
                boton.setObjectName("Primary" if tecla == "=" else "Secondary")
                boton.clicked.connect(lambda checked=False, t=tecla: self._pulsar(t))
                grid.addWidget(boton, row, col)
        layout.addLayout(grid)
        return panel

    def _panel_latex(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(self._texto("Escribe o pega LaTeX para visualizar y copiar una fórmula; "
                                    "esta pestaña NO evalúa ni resuelve expresiones."))
        self.latex = EditorLatex()
        self.latex.setAccessibleName("Código de expresión LaTeX editable")
        self.latex.setPlaceholderText(r"\frac{1}{\sqrt{2\pi}}e^{-x^2/2}")
        self.latex.setMaximumHeight(100)
        self.latex.textChanged.connect(self._solicitar_vista)
        layout.addWidget(self.latex)
        herramientas = QHBoxLayout()
        self.categoria = QComboBox()
        self.categoria.setAccessibleName("Categoría de símbolos matemáticos")
        self.categoria.addItems(_PALETA)
        self.categoria.currentTextChanged.connect(self._mostrar_plantillas)
        herramientas.addWidget(self.categoria)
        self.plantillas = QWidget()
        self.fila_plantillas = QHBoxLayout(self.plantillas)
        self.fila_plantillas.setContentsMargins(0, 0, 0, 0)
        herramientas.addWidget(self.plantillas, 1)
        layout.addLayout(herramientas)
        self._mostrar_plantillas()
        acciones = QHBoxLayout()
        copiar = QPushButton("Copiar LaTeX")
        copiar.setObjectName("Secondary")
        copiar.clicked.connect(self.copiar_latex)
        acciones.addWidget(copiar)
        self.copiar_mathml_boton = QPushButton("Copiar MathML")
        self.copiar_mathml_boton.setObjectName("Secondary")
        self.copiar_mathml_boton.setEnabled(False)
        self.copiar_mathml_boton.clicked.connect(self.copiar_mathml)
        acciones.addWidget(self.copiar_mathml_boton)
        layout.addLayout(acciones)
        self.estado_vista = self._texto("Vista previa con MathML accesible cuando QtWebEngine esté disponible.")
        self.estado_vista.setAccessibleName("Estado de la vista matemática")
        layout.addWidget(self.estado_vista)
        self.previsualizacion = QStackedWidget()
        self.alternativa = self._texto("Introduce LaTeX. El código lineal permanece editable y copiable arriba.")
        self.alternativa.setAccessibleName("Alternativa textual a la vista matemática")
        self.previsualizacion.addWidget(self.alternativa)
        layout.addWidget(self.previsualizacion, 1)
        return panel

    @staticmethod
    def _texto(texto: str) -> QLabel:
        etiqueta = QLabel(texto)
        etiqueta.setWordWrap(True)
        return etiqueta

    def _limpiar_resultado(self):
        """No confundir una entrada modificada con un resultado ya actualizado."""
        self._resultado = None
        self.respuesta.setText("Resultado final: pendiente de calcular")
        self.interpretacion.setText("Entrada interpretada: pendiente de calcular")
        self.pasos.clear()

    def _pulsar(self, tecla: str):
        """Botones de precisión insertan texto en la posición del cursor."""
        if tecla == "=":
            self._evaluar()
        else:
            self.entrada.insert(tecla)
            self._limpiar_resultado()
            self.entrada.setFocus()

    def _evaluar(self):
        """Único evaluador: el AST del núcleo devuelve resultado y pasos."""
        try:
            analisis = explicar(self.entrada.text())
        except ParametroInvalidoError as exc:
            self._resultado = None
            self.respuesta.setText(f"Error: {exc}")
            self.interpretacion.setText("Entrada interpretada: revisa la expresión")
            self.pasos.setPlainText("Corrige el fragmento indicado; la entrada sigue editable y Ctrl+Z funciona.")
            posicion = re.search(r"columna (\d+)", str(exc))
            if posicion:
                inicio = min(int(posicion.group(1)) - 1, len(self.entrada.text()))
                if inicio < len(self.entrada.text()):
                    self.entrada.setSelection(inicio, 1)
                else:
                    self.entrada.setCursorPosition(inicio)
            self.entrada.setFocus(Qt.OtherFocusReason)
            return
        self._resultado = analisis.resultado
        self.respuesta.setText(f"Resultado final: {analisis.resultado:.12g}")
        self.respuesta.setToolTip(str(analisis.resultado))
        self.interpretacion.setText(f"Entrada interpretada: {analisis.interpretacion}")
        lineas = [analisis.supuestos]
        lineas += [f"{numero}. {paso.expresion} → {paso.sustitucion} = {paso.resultado:.12g}\n"
                   f"   {paso.justificacion}" for numero, paso in enumerate(analisis.pasos, 1)]
        self.pasos.setPlainText("\n\n".join(lineas))
        if self.historial.count() == 0 or self.historial.item(0).data(Qt.UserRole) != analisis.entrada:
            item = QListWidgetItem(f"{analisis.entrada} = {analisis.resultado:.12g}")
            item.setData(Qt.UserRole, analisis.entrada)
            item.setToolTip("Pulsa Enter para reutilizar y volver a calcular")
            self.historial.insertItem(0, item)
        while self.historial.count() > 30:
            self.historial.takeItem(self.historial.count() - 1)

    def _reutilizar(self, item: QListWidgetItem):
        self.entrada.setText(item.data(Qt.UserRole))
        self._evaluar()
        self.entrada.setFocus()

    def copiar_resultado(self):
        if self._resultado is not None:
            QApplication.clipboard().setText(str(self._resultado))
        else:
            self.respuesta.setText("Primero calcula una expresión válida para copiar el resultado.")

    def copiar_latex(self):
        QApplication.clipboard().setText(self.latex.toPlainText())
        self.estado_vista.setText("Código LaTeX copiado como texto editable.")

    def copiar_mathml(self):
        if self._navegador is None:
            return
        self._navegador.page().runJavaScript(
            "({fuente: document.querySelector('#fuente')?.textContent || '', "
            "math: document.querySelector('#formula math')?.outerHTML || ''})",
            self._mathml_copiado
        )

    def _mathml_copiado(self, dato):
        if not isinstance(dato, dict) or dato.get("fuente") != self.latex.toPlainText():
            self.estado_vista.setText("La vista está desactualizada; espera a la vista previa para copiar MathML.")
        elif dato.get("math"):
            QApplication.clipboard().setText(dato["math"])
            self.estado_vista.setText("MathML estructurado copiado.")
        else:
            self.estado_vista.setText("La fórmula aún no genera MathML; corrige el LaTeX.")

    def _mostrar_plantillas(self):
        while self.fila_plantillas.count():
            item = self.fila_plantillas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for nombre, plantilla, seleccion in _PALETA[self.categoria.currentText()]:
            boton = QPushButton(nombre)
            boton.setObjectName("Quiet")
            boton.setAccessibleName(f"Insertar plantilla LaTeX de {nombre}")
            boton.clicked.connect(lambda checked=False, p=plantilla, s=seleccion: self.insertar_plantilla(p, s))
            self.fila_plantillas.addWidget(boton)

    def insertar_plantilla(self, plantilla: str, seleccion: str | None = None):
        cursor = self.latex.textCursor()
        posicion = cursor.selectionStart()
        cursor.insertText(plantilla)
        if seleccion:
            # Evita seleccionar la «a» del nombre de un comando como \\frac.
            inicio = plantilla.find("{" + seleccion + "}")
            if inicio >= 0:
                inicio += 1
            else:
                despues_de_llave = plantilla.find("}" + seleccion)
                inicio = despues_de_llave + 1 if despues_de_llave >= 0 else plantilla.index(seleccion)
            cursor.setPosition(posicion + inicio)
            cursor.setPosition(posicion + inicio + len(seleccion), QTextCursor.KeepAnchor)
        self.latex.setTextCursor(cursor)
        self.latex.setFocus()

    def _cambio_pestana(self, indice: int):
        if indice == 1:
            self._iniciar_vista()
            self._solicitar_vista()

    def _iniciar_vista(self):
        if self._navegador is not None:
            return
        try:
            from PySide6.QtWebEngineCore import QWebEngineSettings
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from ampu.ui.vistas.teoria import PaginaTeoria

            navegador = QWebEngineView(self.previsualizacion)
            navegador.setPage(PaginaTeoria(navegador))
            navegador.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            navegador.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
            navegador.setAccessibleName("Vista estructurada de la fórmula; MathML con código alternativo")
            navegador.loadFinished.connect(self._vista_lista)
            self.previsualizacion.addWidget(navegador)
            self.previsualizacion.setCurrentWidget(navegador)
            self._navegador = navegador
        except (ImportError, OSError) as exc:
            self.estado_vista.setText(f"Vista matemática no disponible: {exc}. Revisa QtWebEngine en README.")
            self.alternativa.setText("El código LaTeX de arriba sigue siendo editable y copiable; "
                                    "la fórmula estructurada requiere QtWebEngine.")

    def _solicitar_vista(self):
        if self.pestanas.currentIndex() == 1:
            self.copiar_mathml_boton.setEnabled(False)
            self._debounce.start()

    def _previsualizar(self):
        if self._navegador is None:
            return
        try:
            html = previsualizar_latex(self.latex.toPlainText(), self.tema_actual, self.escala_actual)
        except ParametroInvalidoError as exc:
            self.estado_vista.setText(str(exc))
            self._navegador.setHtml(previsualizar_latex("", self.tema_actual, self.escala_actual),
                                    QUrl.fromLocalFile(str(RECURSOS) + "/"))
            return
        self.estado_vista.setText("Actualizando fórmula y alternativa lineal…")
        self._navegador.setHtml(html, QUrl.fromLocalFile(str(RECURSOS) + "/"))

    def _vista_lista(self, correcto: bool):
        if not correcto:
            self.estado_vista.setText("No se cargó la vista matemática local; revisa QtWebEngine.")
            return
        self._navegador.page().runJavaScript(
            "({fuente: document.querySelector('#fuente')?.textContent || '', "
            "math: !!document.querySelector('#formula math'), "
            "error: document.querySelector('#estado')?.textContent || ''})",
            self._estado_mathml
        )

    def _estado_mathml(self, dato):
        if not isinstance(dato, dict) or dato.get("fuente") != self.latex.toPlainText():
            return  # Una respuesta antigua no habilita Copiar MathML para otra entrada.
        listo = bool(dato.get("math"))
        self.copiar_mathml_boton.setEnabled(listo)
        self.estado_vista.setText(dato.get("error") or (
            "Vista estructurada y MathML disponibles; usa tabulador para acceder al código lineal."
            if listo else "Introduce LaTeX para obtener la vista matemática."))

    def actualizar_tema(self, tema: str, escala: float = 1.0):
        self.tema_actual = tema
        self.escala_actual = escala
        if self._navegador is not None:
            self._solicitar_vista()

    def estado(self) -> dict:
        return {"entrada": self.entrada.text(), "latex": self.latex.toPlainText(),
                "pestana": self.pestanas.currentIndex(),
                "historial": [self.historial.item(i).data(Qt.UserRole) for i in range(self.historial.count())]}

    def restaurar(self, datos: dict):
        """Conserva texto e historial; no calcula silenciosamente al cargar JSON."""
        # No truncar una entrada guardada: si supera el límite de evaluación,
        # debe seguir editable y recuperable sin pérdida silenciosa de datos.
        self.entrada.setText(str(datos.get("entrada", "")))
        self._limpiar_resultado()
        self.latex.setPlainText(str(datos.get("latex", "")))
        self.historial.clear()
        historial = datos.get("historial", [])
        if isinstance(historial, list):
            for expresion in historial[:30]:
                if isinstance(expresion, str) and 0 < len(expresion) <= 200:
                    item = QListWidgetItem(expresion)
                    item.setData(Qt.UserRole, expresion)
                    self.historial.addItem(item)
        self.pestanas.setCurrentIndex(1 if datos.get("pestana") == 1 else 0)
