"""Análisis descriptivo con datos pegados, frecuencias y tres gráficos."""

from dataclasses import asdict

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QPlainTextEdit, QProgressBar, QPushButton,
    QSplitter, QVBoxLayout, QWidget,
)

from ampu.core.estadistica.descriptiva import frecuencias, resumir
from ampu.core.estadistica.inferencia import correlacion
from ampu.core.errores import ParametroInvalidoError
from ampu.ui.widgets.comunes import KPIs, encabezado, etiqueta, marco, numeros
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


def _resumir_datos(texto_x: str, texto_y: str):
    """Analiza entradas fuera del hilo principal; sin operaciones en widgets."""
    x = numeros(texto_x)
    y = numeros(texto_y) if texto_y.strip() else None
    if y is not None and len(x) != len(y):
        raise ParametroInvalidoError("X e Y deben contener igual número de observaciones.")
    r = resumir(x)
    corr = correlacion(x, y).estadistico if y is not None and len(x) >= 3 else None
    tabla = pd.DataFrame([{"Estadístico": clave.replace("_", " ").capitalize(), "Resultado": str(valor) if isinstance(valor, tuple) else valor}
                          for clave, valor in asdict(r).items()])
    originales = pd.DataFrame({"X": x, **({"Y": y} if y is not None else {})})
    return r, corr, {"Frecuencias": frecuencias(x), "Resumen": tabla, "Datos": originales}, x, y


class VistaDescriptiva(VistaTrabajo):
    """Explora una muestra con resumen, frecuencias, histograma y boxplot."""

    def __init__(self, parent=None):
        """Ofrece entrada de datos directa o pegada desde CSV/Excel."""
        super().__init__(parent)
        self.ultimo = None
        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(25, 24, 25, 22)
        pagina.setSpacing(16)
        pagina.addWidget(encabezado("03  /  EXPLORACIÓN DE DATOS", "Estadística descriptiva", "Pega observaciones, explora su dispersión y exporta frecuencias sin perder datos."))
        fila = QHBoxLayout()
        fila.setSpacing(17)
        pagina.addLayout(fila, 1)
        left, l = marco("FormCard", 17)
        left.setFixedWidth(315)
        fila.addWidget(left)
        l.addWidget(etiqueta("DATOS · VARIABLE X", "Eyebrow"))
        l.addWidget(etiqueta("Separa números por comas, espacios o saltos. Usa punto decimal.", "Muted"))
        self.x = QPlainTextEdit("12, 15, 18, 21, 18, 20, 23, 22, 17, 19, 16, 24, 21, 18")
        self.x.setPlaceholderText("12, 15, 18, 21, …")
        l.addWidget(self.x, 1)
        l.addWidget(etiqueta("VARIABLE Y · OPCIONAL", "Eyebrow"))
        l.addWidget(etiqueta("Parejas para dispersión y correlación.", "Muted"))
        self.y = QPlainTextEdit()
        self.y.setPlaceholderText("13, 15, 19, 22, …")
        self.y.setFixedHeight(78)
        l.addWidget(self.y)
        l.addWidget(etiqueta("VISUALIZACIÓN", "Eyebrow"))
        self.modo = QComboBox()
        self.modo.addItems(["Histograma", "Boxplot", "Dispersión"])
        self.modo.currentTextChanged.connect(self._dibujar)
        l.addWidget(self.modo)
        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        l.addWidget(self.progreso)
        self.boton = QPushButton("Analizar datos  →")
        self.boton.setObjectName("Primary")
        self.boton.clicked.connect(self.calcular)
        l.addWidget(self.boton)
        teoria = QPushButton("Teoría descriptiva")
        teoria.setObjectName("Secondary")
        teoria.clicked.connect(lambda: self.abrir_teoria.emit("descriptiva"))
        l.addWidget(teoria)
        right = QWidget()
        r = QVBoxLayout(right)
        r.setContentsMargins(0, 0, 0, 0)
        r.setSpacing(10)
        fila.addWidget(right, 1)
        self.indicadores = KPIs(["Media", "Mediana", "Desv. muestral", "CV"])
        r.addWidget(self.indicadores)
        self.nota = etiqueta("La varianza se calcula con denominador n − 1.", "Note")
        r.addWidget(self.nota)
        split = QSplitter(Qt.Vertical)
        split.setChildrenCollapsible(False)
        r.addWidget(split, 1)
        card, cl = marco("ChartCard", 12)
        cl.addWidget(etiqueta("PERFIL DE LA MUESTRA", "Eyebrow"))
        self.grafico = Grafico()
        cl.addWidget(self.grafico, 1)
        split.addWidget(card)
        card, tl = marco("Card", 12)
        titulo = QHBoxLayout()
        titulo.addWidget(etiqueta("TABLAS DEL ANÁLISIS", "Eyebrow"))
        titulo.addStretch()
        self.hojas = QComboBox()
        self.hojas.currentTextChanged.connect(self._tabla)
        titulo.addWidget(self.hojas)
        tl.addLayout(titulo)
        self.tabla = TablaDatos()
        tl.addWidget(self.tabla)
        split.addWidget(card)
        split.setSizes([410, 230])
        QTimer.singleShot(260, self.calcular)

    def calcular(self):
        """Despacha la carga de datos a un hilo de trabajo."""
        if self._ocupado:
            return
        self.progreso.setRange(0, 0)
        self.progreso.show()
        self.boton.setEnabled(False)
        self.trabajar(_resumir_datos, self._recibir, self._fin, self.x.toPlainText(), self.y.toPlainText())
        self.aviso.emit("Calculando resumen, frecuencias y correlación…")

    def _fin(self):
        """Restablece los controles tras éxito o error."""
        self.progreso.hide()
        self.boton.setEnabled(True)

    def _recibir(self, resultado):
        """Muestra tablas y gráficos sin volver a calcular estadísticas."""
        self.ultimo = resultado
        resumen, corr, tablas, x, y = resultado
        self.indicadores.actualizar(resumen.media, resumen.mediana, resumen.desviacion,
                                    resumen.coeficiente_variacion if resumen.coeficiente_variacion is not None else float("nan"))
        self.nota.setText(f"{resumen.n} observaciones · cuartiles {resumen.q1:g} y {resumen.q3:g}"
                          + (f" · Pearson r = {corr:.4g}" if corr is not None else " · agrega Y para un diagrama de dispersión."))
        self.hojas.blockSignals(True)
        self.hojas.clear()
        self.hojas.addItems(tablas)
        self.hojas.blockSignals(False)
        self._tabla()
        self._dibujar()
        self.aviso.emit(f"{resumen.n} observaciones analizadas y disponibles para exportar.")

    def _tabla(self):
        """Alterna hojas de la misma operación."""
        if self.ultimo and self.hojas.currentText() in self.ultimo[2]:
            self.tabla.mostrar(self.ultimo[2][self.hojas.currentText()])

    def _dibujar(self):
        """Dibuja serie elegida cuando existen datos."""
        if self.ultimo:
            modo = self.modo.currentText()
            x, y = self.ultimo[3:5]
            if modo == "Dispersión" and y is None:
                modo = "Histograma"
            self.grafico.histograma(x, modo, y)

    def tablas_exportables(self) -> dict:
        """Incluye datos originales, resumen y frecuencias."""
        if not self.ultimo:
            return {}
        tablas = dict(self.ultimo[2])
        if self.hojas.currentText():
            tablas[self.hojas.currentText()] = self.tabla.datos()
        return tablas

    def resumen_exportable(self) -> str:
        """Lectura no causal y concisa para el reporte."""
        if not self.ultimo:
            return "Sin resultados."
        r = self.ultimo[0]
        return f"n={r.n}, media={r.media:.6g}, mediana={r.mediana:.6g}, s={r.desviacion:.6g}, CV={r.coeficiente_variacion}. " + self.nota.text()

    def clave_teoria(self) -> str:
        """Lección vinculada."""
        return "descriptiva"

    def estado(self) -> dict:
        """Datos pegados y gráficos seleccionados en la sesión."""
        return {"x": self.x.toPlainText(), "y": self.y.toPlainText(), "modo": self.modo.currentText(),
                "tablas": {k: v.to_dict(orient="list") for k, v in self.tablas_exportables().items()}}

    def restaurar(self, d: dict):
        """Restaura entradas y regenera resultados."""
        self.x.setPlainText(d.get("x", ""))
        self.y.setPlainText(d.get("y", ""))
        self.modo.setCurrentText(d.get("modo", "Histograma"))
        QTimer.singleShot(200, self.calcular)
