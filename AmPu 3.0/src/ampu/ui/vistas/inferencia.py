"""Pruebas, intervalos, correlación y regresión con interpretación en español."""

from dataclasses import asdict

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout,
    QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSpinBox,
    QSplitter, QVBoxLayout, QWidget,
)

from ampu.core.estadistica import inferencia as i, regresion as r
from ampu.ui.widgets.comunes import KPIs, encabezado, etiqueta, grupos, marco, matriz, numeros
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


OPCIONES = [
    ("z · una media", "z_una", "prueba_z_una"), ("z · dos medias", "z_dos", "prueba_z_dos"),
    ("t · una media", "t_una", "prueba_t_una"), ("t de Welch · dos medias", "t_dos", "prueba_t_dos"),
    ("z · una proporción", "prop_una", "prueba_proporcion_una"), ("z · dos proporciones", "prop_dos", "prueba_proporcion_dos"),
    ("χ² · bondad de ajuste", "chi_bondad", "chi_bondad"), ("χ² · independencia", "chi_independencia", "chi_independencia"),
    ("ANOVA · una vía", "anova", "anova"), ("Correlación · Pearson", "pearson", "correlacion"),
    ("Correlación · Spearman", "spearman", "correlacion"), ("Regresión · simple", "reg_simple", "regresion"),
    ("Regresión · múltiple", "reg_multiple", "regresion"), ("Mann–Whitney U", "mann", "mann_whitney"),
    ("Wilcoxon pareado", "wilcoxon", "wilcoxon"), ("Kruskal–Wallis", "kruskal", "kruskal"),
]

EJEMPLOS = {
    "chi_bondad": ("12, 15, 23", "15, 15, 20", "X = observadas; Y = esperadas (totales iguales)."),
    "chi_independencia": ("18, 12\n10, 20", "", "X = matriz de contingencia (una fila por línea)."),
    "anova": ("2, 3, 4, 5\n9, 10, 11, 12\n5, 6, 7, 8", "", "X = un grupo por línea; cada grupo con dos o más datos."),
    "kruskal": ("1, 2, 3, 4\n4, 5, 6, 7\n2, 3, 4, 5", "", "X = un grupo por línea."),
    "reg_multiple": ("1, 1\n2, 4\n3, 9\n4, 16\n5, 25\n6, 36\n7, 49", "4, 6, 8, 10, 12, 14, 16", "X = matriz filas×predictores; Y = respuesta."),
}


def _evaluar(tipo: str, x_txt: str, y_txt: str, alfa: float, mu0: float, s1: float,
             s2: float, p0: float, x1: int, n1: int, x2: int, n2: int) -> dict:
    """Despacha todas las pruebas a ``core.estadistica`` en un hilo de fondo."""
    grafico = None
    if tipo in ("prop_una", "prop_dos"):
        prueba = i.proporcion_una(x1, n1, p0, alfa) if tipo == "prop_una" else i.proporcion_dos(x1, n1, x2, n2, alfa)
        grafico = ("barras", ["Grupo A", "Grupo B"] if tipo == "prop_dos" else ["Éxitos", "Fracasos"],
                   list(prueba.detalles["proporciones_observadas"]) if tipo == "prop_dos" else
                   [prueba.detalles["proporcion_observada"], prueba.detalles["proporcion_fallos"]])
    elif tipo == "chi_independencia":
        muestra = matriz(x_txt)
        prueba = i.chi_independencia(muestra, alfa)
        grafico = ("barras", [f"Fila {j+1}" for j in range(muestra.shape[0])],
                   prueba.detalles["totales_fila"])
    elif tipo in ("anova", "kruskal"):
        muestras = grupos(x_txt)
        prueba = i.anova(muestras, alfa) if tipo == "anova" else i.kruskal(muestras, alfa)
        grafico = ("barras", [f"Grupo {j+1}" for j in range(len(muestras))],
                   prueba.detalles["medias"] if tipo == "anova" else prueba.detalles["medias_descriptivas"])
    elif tipo == "reg_multiple":
        X, y = matriz(x_txt), numeros(y_txt)
        modelo = r.lineal_multiple(X, y, confianza=1-alfa)
        tabla = pd.DataFrame({"Coeficiente": modelo.nombres, "Estimación": modelo.coeficientes,
                              "p-valor": modelo.p_valores, "IC inferior": modelo.intervalos[:, 0], "IC superior": modelo.intervalos[:, 1]})
        return {"tabla": tabla, "resumen": modelo.conclusion, "estadistico": modelo.r_cuadrado,
                "p": float(modelo.p_valores[1:].min()), "intervalo": None,
                "grafico": ("dispersion", y, modelo.predecir(X), None, "Observado vs predicho"), "regresion": True}
    elif tipo == "chi_bondad":
        a, b = numeros(x_txt), numeros(y_txt)
        prueba = i.chi_bondad(a, b, alfa)
        grafico = ("barras", [f"Clase {j+1}" for j in range(len(a))], list(a))
    else:
        x = numeros(x_txt)
        y = numeros(y_txt) if tipo in ("z_dos", "t_dos", "pearson", "spearman", "reg_simple", "mann", "wilcoxon") else None
        if tipo == "z_una":
            prueba = i.z_una_muestra(x, mu0, s1, alfa)
        elif tipo == "z_dos":
            prueba = i.z_dos_muestras(x, y, s1, s2, alfa)
        elif tipo == "t_una":
            prueba = i.t_una_muestra(x, mu0, alfa)
        elif tipo == "t_dos":
            prueba = i.t_dos_muestras(x, y, alfa)
        elif tipo in ("pearson", "spearman"):
            prueba = i.correlacion(x, y, tipo, alfa)
        elif tipo == "reg_simple":
            modelo = r.lineal_simple(x, y, confianza=1-alfa)
            tabla = pd.DataFrame({"Coeficiente": modelo.nombres, "Estimación": modelo.coeficientes,
                                  "p-valor": modelo.p_valores, "IC inferior": modelo.intervalos[:, 0], "IC superior": modelo.intervalos[:, 1]})
            return {"tabla": tabla, "resumen": modelo.conclusion, "estadistico": modelo.r_cuadrado,
                    "p": float(modelo.p_valores[1]), "intervalo": tuple(modelo.intervalos[1]),
                    "grafico": ("dispersion", x, y, modelo.predecir(x[:, None]), "Regresión lineal simple"), "regresion": True}
        elif tipo == "mann":
            prueba = i.mann_whitney(x, y, alfa)
        elif tipo == "wilcoxon":
            prueba = i.wilcoxon(x, y, alfa)
        else:
            raise ValueError("Prueba no registrada.")
        grafico = ("dispersion", x, y, None, "Datos pareados") if tipo in ("pearson", "spearman") else ("histograma", x)
    resumen = prueba.conclusion
    if prueba.detalles.get("advertencia"):
        resumen += " " + prueba.detalles["advertencia"]
    contenido = [("Método", prueba.metodo), ("Estadístico", prueba.estadistico),
                 ("p-valor", prueba.p_valor), ("α", prueba.alfa), ("Grados de libertad", prueba.gl),
                 ("IC inferior", prueba.intervalo[0] if prueba.intervalo else None),
                 ("IC superior", prueba.intervalo[1] if prueba.intervalo else None),
                 ("Conclusión", resumen)]
    return {"tabla": pd.DataFrame(contenido, columns=["Resultado", "Valor"]),
            "resumen": resumen, "estadistico": prueba.estadistico,
            "p": prueba.p_valor, "intervalo": prueba.intervalo,
            "grafico": grafico, "regresion": False}


class VistaInferencia(VistaTrabajo):
    """Panel de 16 contrastes y modelos, con interpretación no causal."""

    def __init__(self, parent=None):
        """Une datos libres, metadatos de prueba y salidas reportables."""
        super().__init__(parent)
        self.ultimo = None
        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(25, 24, 25, 22)
        pagina.setSpacing(16)
        pagina.addWidget(encabezado("05  /  DECISIONES BASADAS EN DATOS", "Inferencia", "Contrastes, intervalos, correlación y regresión con conclusiones responsables."))
        fila = QHBoxLayout()
        fila.setSpacing(17)
        pagina.addLayout(fila, 1)
        card, l = marco("FormCard", 16)
        card.setFixedWidth(315)
        fila.addWidget(card)
        l.addWidget(etiqueta("TÉCNICA", "Eyebrow"))
        self.tipo = QComboBox()
        self.tipo.setAccessibleName("Técnica de inferencia seleccionada")
        for nombre, clave, teoria in OPCIONES:
            self.tipo.addItem(nombre, (clave, teoria))
        self.tipo.currentIndexChanged.connect(self._opcion)
        l.addWidget(self.tipo)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        l.addWidget(scroll, 1)
        contenido = QWidget()
        form = QVBoxLayout(contenido)
        form.setContentsMargins(0, 5, 5, 0)
        form.setSpacing(8)
        self.ayuda = etiqueta("X = datos de una muestra; Y = datos de la segunda (opcional).", "Note")
        form.addWidget(self.ayuda)
        form.addWidget(etiqueta("DATOS X / TABLA", "Eyebrow"))
        self.x = QPlainTextEdit("7, 8, 9, 10, 11, 12, 13")
        self.x.setAccessibleName("Datos de la muestra X o tabla")
        self.x.setFixedHeight(92)
        form.addWidget(self.x)
        form.addWidget(etiqueta("DATOS Y / ESPERADAS", "Eyebrow"))
        self.y = QPlainTextEdit("4, 5, 6, 7, 8, 9, 10")
        self.y.setAccessibleName("Datos de muestra Y o esperadas")
        self.y.setFixedHeight(75)
        form.addWidget(self.y)
        campos = QFormLayout()
        self.alfa = QDoubleSpinBox()
        self.alfa.setAccessibleName("Nivel de significación alfa")
        self.alfa.setRange(.001, .99)
        self.alfa.setDecimals(3)
        self.alfa.setSingleStep(.01)
        self.alfa.setValue(.05)
        campos.addRow("Significación α", self.alfa)
        self.mu0 = QDoubleSpinBox()
        self.mu0.setAccessibleName("Hipótesis de media mu cero")
        self.mu0.setRange(-1e8, 1e8)
        self.mu0.setValue(8)
        campos.addRow("Hipótesis μ₀", self.mu0)
        self.sigma1 = QDoubleSpinBox()
        self.sigma1.setAccessibleName("Desviación sigma uno")
        self.sigma1.setRange(.001, 1e8)
        self.sigma1.setValue(2)
        campos.addRow("Desv. σ₁", self.sigma1)
        self.sigma2 = QDoubleSpinBox()
        self.sigma2.setAccessibleName("Desviación sigma dos")
        self.sigma2.setRange(.001, 1e8)
        self.sigma2.setValue(3)
        campos.addRow("Desv. σ₂", self.sigma2)
        self.p0 = QDoubleSpinBox()
        self.p0.setAccessibleName("Proporción nula p cero")
        self.p0.setRange(.001, .999)
        self.p0.setDecimals(3)
        self.p0.setValue(.5)
        campos.addRow("Proporción p₀", self.p0)
        for nombre, attr, inicial in (("Éxitos x₁", "x1", 40), ("Ensayos n₁", "n1", 100),
                                       ("Éxitos x₂", "x2", 20), ("Ensayos n₂", "n2", 100)):
            spin = QSpinBox()
            spin.setRange(0 if attr.startswith("x") else 1, 1_000_000)
            spin.setValue(inicial)
            setattr(self, attr, spin)
            campos.addRow(nombre, spin)
        form.addLayout(campos)
        form.addStretch()
        scroll.setWidget(contenido)
        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        l.addWidget(self.progreso)
        self.boton = QPushButton("Contrastar y explicar  →")
        self.boton.setObjectName("Primary")
        self.boton.clicked.connect(self.calcular)
        l.addWidget(self.boton)
        btn = QPushButton("Teoría de esta prueba")
        btn.setObjectName("Secondary")
        btn.clicked.connect(lambda: self.abrir_teoria.emit(self.clave_teoria()))
        l.addWidget(btn)

        right = QWidget()
        rlayout = QVBoxLayout(right)
        rlayout.setContentsMargins(0, 0, 0, 0)
        rlayout.setSpacing(10)
        fila.addWidget(right, 1)
        self.configurar_adaptacion(fila, card)
        self.indicadores = KPIs(["Estadístico / R²", "p-valor", "IC inferior", "IC superior"])
        rlayout.addWidget(self.indicadores)
        self.conclusion = etiqueta("Elige una técnica para ver su interpretación.", "Note")
        rlayout.addWidget(self.conclusion)
        split = QSplitter(Qt.Vertical)
        split.setChildrenCollapsible(False)
        rlayout.addWidget(split, 1)
        gc, gl = marco("ChartCard", 12)
        gl.addWidget(etiqueta("EVIDENCIA VISUAL", "Eyebrow"))
        self.grafico = Grafico()
        gl.addWidget(self.grafico, 1)
        split.addWidget(gc)
        tc, tl = marco("Card", 12)
        tl.addWidget(etiqueta("INFORME NUMÉRICO", "Eyebrow"))
        self.tabla = TablaDatos()
        tl.addWidget(self.tabla, 1)
        split.addWidget(tc)
        split.setSizes([400, 240])
        self._opcion()
        self.vigilar_entradas()

    def _opcion(self):
        """Orienta al usuario y habilita solo entradas relevantes."""
        clave = self.tipo.currentData()[0]
        grupos_multiple = clave in ("anova", "kruskal", "chi_independencia", "reg_multiple")
        usa_y = clave in ("z_dos", "t_dos", "chi_bondad", "pearson", "spearman", "reg_simple", "reg_multiple", "mann", "wilcoxon")
        proporciona = clave in ("prop_una", "prop_dos")
        self.x.setEnabled(not proporciona)
        self.y.setEnabled(usa_y)
        self.mu0.setEnabled(clave in ("z_una", "t_una"))
        self.sigma1.setEnabled(clave in ("z_una", "z_dos"))
        self.sigma2.setEnabled(clave == "z_dos")
        self.p0.setEnabled(clave == "prop_una")
        for campo in ("x1", "n1", "x2", "n2"):
            getattr(self, campo).setEnabled(proporciona and (campo.endswith("1") or clave == "prop_dos"))
        if clave in EJEMPLOS:
            xx, yy, ayuda = EJEMPLOS[clave]
            self.x.setPlainText(xx)
            self.y.setPlainText(yy)
        else:
            ayuda = ("Valores X e Y separados por comas; usa punto decimal."
                     if usa_y else "Valores X separados por comas o saltos; usa punto decimal.")
            if grupos_multiple:
                ayuda = "Una fila por grupo (o por observación para regresión múltiple)."
            if proporciona:
                ayuda = "Usa campos de éxitos y ensayos de abajo; X e Y no son necesarios."
            self.x.setPlainText("7, 8, 9, 10, 11, 12, 13")
            self.y.setPlainText("4, 5, 6, 7, 8, 9, 10")
        self.ayuda.setText(ayuda)

    def calcular(self):
        """Despacha prueba de SciPy sin bloquear Qt."""
        if self._ocupado:
            return
        self.progreso.setRange(0, 0)
        self.progreso.show()
        self.boton.setEnabled(False)
        self.trabajar(_evaluar, self._recibir, self._fin,
                      self.tipo.currentData()[0], self.x.toPlainText(), self.y.toPlainText(), self.alfa.value(),
                      self.mu0.value(), self.sigma1.value(), self.sigma2.value(), self.p0.value(),
                      self.x1.value(), self.n1.value(), self.x2.value(), self.n2.value())
        self.aviso.emit("Calculando contraste e intervalos…")

    def _fin(self):
        """Desactiva indicador de progreso."""
        self.progreso.hide()
        self.boton.setEnabled(True)

    def _recibir(self, salida: dict):
        """Consume resultados precomputados sin recalcular fórmulas."""
        self.ultimo = salida
        self.conclusion.setText(salida["resumen"])
        a, b = salida["intervalo"] if salida["intervalo"] is not None else (float("nan"), float("nan"))
        self.indicadores.actualizar(salida["estadistico"], salida["p"], a, b)
        self.mostrar_tabla_restaurada(self.tabla, salida["tabla"])
        tipo, *datos = salida["grafico"]
        if tipo == "barras":
            self.grafico.serie(*datos, self.tipo.currentText())
        elif tipo == "histograma":
            self.grafico.histograma(datos[0])
        else:
            self.grafico.dispersion(*datos)
        self.aviso.emit("Prueba finalizada; interpreta el p-valor junto con las condiciones del modelo.")

    def tablas_exportables(self) -> dict:
        """Exporta informe visible, incluidas ediciones."""
        return {self.tipo.currentText(): self.tabla.datos()} if self.ultimo else {}

    def resumen_exportable(self) -> str:
        """Conclusión cautelosa para informe."""
        return self.conclusion.text()

    def clave_teoria(self) -> str:
        """Vínculo de la técnica a su Markdown."""
        return self.tipo.currentData()[1]

    def estado(self) -> dict:
        """Incluye datos, opciones, hipótesis y últimos resultados."""
        return {"tipo": self.tipo.currentData()[0], "x": self.x.toPlainText(), "y": self.y.toPlainText(),
                **{k: getattr(self, k).value() for k in ("alfa", "mu0", "sigma1", "sigma2", "p0", "x1", "n1", "x2", "n2")},
                "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo else self._tabla_pendiente}

    def restaurar(self, datos: dict):
        """Carga parámetros y reproduce el contraste si había resultados."""
        for j in range(self.tipo.count()):
            if self.tipo.itemData(j)[0] == datos.get("tipo"):
                self.tipo.setCurrentIndex(j)
                break
        self.x.setPlainText(datos.get("x", ""))
        self.y.setPlainText(datos.get("y", ""))
        for k in ("alfa", "mu0", "sigma1", "sigma2", "p0", "x1", "n1", "x2", "n2"):
            if k in datos:
                getattr(self, k).setValue(datos[k])
        if datos.get("tabla") is not None:
            self.limpiar_resultado()
            self._tabla_pendiente = datos["tabla"]
            self.recalcular_restaurado()
        else:
            self.limpiar_resultado()
            self.conclusion.setText("Elige una técnica para ver su interpretación.")
