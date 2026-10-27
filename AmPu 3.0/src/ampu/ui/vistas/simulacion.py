"""Monte Carlo, muestras sintéticas, ajuste y QQ-plot reproducibles."""

import secrets

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from ampu.core.distribuciones import catalogo, obtener
from ampu.core.errores import ParametroInvalidoError
from ampu.core.estadistica.descriptiva import resumir
from ampu.core.simulacion.montecarlo import (
    ajustar_distribucion, curva_ajustada, familias_ajustables,
    generar_muestra, integral_cuadrado, puntos_pi, qq_plot, simular_pi,
)
from ampu.ui.widgets.comunes import campo_semilla, encabezado, etiqueta, marco, numeros
from ampu.ui.widgets.formulario import FormularioDistribucion
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


def _simular(tipo: str, clave: str, params: dict, n: int, seed: int, texto: str) -> dict:
    """Opera en un hilo secundario, devuelve datos y especificación del gráfico."""
    if tipo == "pi":
        estimacion = simular_pi(n, seed)
        puntos, mascara = puntos_pi(min(n, 1000), seed)
        tabla = pd.DataFrame({"Indicador": ["Estimación π", "Error estándar", "IC inferior", "IC superior", "Simulaciones", "Semilla"],
                              "Valor": [estimacion.valor, estimacion.error_estandar, *estimacion.intervalo, n, seed]})
        return {"tabla": tabla, "resumen": f"π ≈ {estimacion.valor:.6g}; IC de simulación 95 %: {estimacion.intervalo[0]:.5g} a {estimacion.intervalo[1]:.5g}. No se infiere incertidumbre de un modelo externo.",
                "grafico": ("pi", puntos, mascara), "valor": estimacion.valor, "error": estimacion.error_estandar}
    if tipo == "integral":
        est, referencia = integral_cuadrado(n, seed)
        tabla = pd.DataFrame({"Indicador": ["Integral estimada", "Error estándar", "IC inferior", "IC superior", "Simulaciones", "Semilla"],
                              "Valor": [est.valor, est.error_estandar, *est.intervalo, n, seed]})
        return {"tabla": tabla, "resumen": f"Integral ∫₀¹ x² dx ≈ {est.valor:.6g}; error de simulación {est.error_estandar:.4g}.",
                "grafico": ("barras", ["Integral estimada", "Referencia exacta"], [est.valor, referencia]),
                "valor": est.valor, "error": est.error_estandar}
    if tipo == "muestra":
        datos = generar_muestra(clave, params, n, seed)
        if datos.ndim != 1:
            raise ParametroInvalidoError("Selecciona un modelo univariante para esta vista.")
        estadisticos = resumir(datos)
        tabla = pd.DataFrame({"Índice": np.arange(1, n+1), "Observación": datos, "Semilla": [seed]*n})
        return {"tabla": tabla, "resumen": f"{n} observaciones de {obtener(clave).nombre} con semilla {seed}. Media empírica {estadisticos.media:.5g}.",
                "grafico": ("histograma", datos), "valor": estadisticos.media, "error": estadisticos.desviacion}
    x = numeros(texto, minimo=5 if tipo == "ajuste" else 2)
    if tipo == "ajuste":
        fit = ajustar_distribucion(x, clave, seed)
        xs, ys = curva_ajustada(fit, x)
        tabla = pd.DataFrame({"Parámetro": [*fit.parametros, "AIC", "Estadístico KS", "p KS exploratoria"],
                              "Estimación": [*fit.parametros.values(), fit.aic, fit.ks, fit.p_ks]})
        resumen = f"Ajuste {clave}: AIC={fit.aic:.5g}, KS={fit.ks:.5g}. La p de KS ({fit.p_ks:.4g}) NO está corregida por estimar parámetros; es exploratoria."
        return {"tabla": tabla, "resumen": resumen, "grafico": ("ajuste", x, xs, ys), "valor": fit.aic, "error": fit.ks}
    if tipo == "qq":
        teorico, observado = qq_plot(x, clave, params)
        descriptivos = resumir(observado)
        return {"tabla": pd.DataFrame({"Cuantil teórico": teorico, "Dato ordenado": observado}),
                "resumen": f"QQ-plot de {len(x)} datos frente a {obtener(clave).nombre}; una recta aproximada sugiere concordancia visual, no un contraste formal.",
                "grafico": ("qq", teorico, observado), "valor": descriptivos.mediana, "error": descriptivos.desviacion}
    raise ParametroInvalidoError("Simulación no registrada.")


class VistaSimulacion(VistaTrabajo):
    """Simulación, datos reales y análisis visual desde un mismo servicio."""

    def __init__(self, parent=None):
        """Controla semilla, modelo de registro y hojas de resultados."""
        super().__init__(parent)
        self.ultimo = None
        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(25, 24, 25, 22)
        pagina.setSpacing(16)
        pagina.addWidget(encabezado("06  /  EXPERIMENTAR Y COMPARAR", "Simulación y ajuste", "Repite el experimento, compara modelos con datos y comunica incertidumbre."))
        fila = QHBoxLayout()
        fila.setSpacing(17)
        pagina.addLayout(fila, 1)
        card, l = marco("FormCard", 17)
        card.setFixedWidth(315)
        fila.addWidget(card)
        l.addWidget(etiqueta("EXPERIMENTO", "Eyebrow"))
        self.tipo = QComboBox()
        for nombre, clave in (("Estimar π", "pi"), ("Integral de x² en [0,1]", "integral"),
                              ("Generar muestra", "muestra"), ("Ajustar distribución", "ajuste"),
                              ("QQ-plot de datos", "qq")):
            self.tipo.addItem(nombre, clave)
        self.tipo.currentIndexChanged.connect(self._tipo)
        l.addWidget(self.tipo)
        campos = QHBoxLayout()
        col = QVBoxLayout()
        col.addWidget(etiqueta("Simulaciones n", "Muted"))
        self.n = QSpinBox()
        self.n.setRange(2, 1_000_000)
        self.n.setValue(10_000)
        col.addWidget(self.n)
        campos.addLayout(col)
        col = QVBoxLayout()
        col.addWidget(etiqueta("Semilla", "Muted"))
        self.semilla = campo_semilla()
        col.addWidget(self.semilla)
        campos.addLayout(col)
        l.addLayout(campos)
        fila_sem = QHBoxLayout()
        repetir = QPushButton("↻ Misma")
        repetir.setObjectName("Quiet")
        repetir.clicked.connect(self.calcular)
        fila_sem.addWidget(repetir)
        nueva = QPushButton("✦ Nueva semilla")
        nueva.setObjectName("Quiet")
        nueva.clicked.connect(self._nueva)
        fila_sem.addWidget(nueva)
        l.addLayout(fila_sem)
        l.addWidget(etiqueta("DISTRIBUCIÓN", "Eyebrow"))
        self.modelo = QComboBox()
        self.modelo.currentIndexChanged.connect(self._cambiar_modelo)
        l.addWidget(self.modelo)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.NoFrame)
        self.formulario = FormularioDistribucion()
        sc.setWidget(self.formulario)
        l.addWidget(sc, 1)
        l.addWidget(etiqueta("DATOS PARA AJUSTE / QQ-PLOT", "Eyebrow"))
        self.datos = QPlainTextEdit("1.2, 2.0, 0.4, 1.1, 0.7, 2.5, 1.3, 0.9, 1.8, 2.1, 1.5, 0.6")
        self.datos.setFixedHeight(86)
        self.datos.setPlaceholderText("Pega datos separados por comas...")
        l.addWidget(self.datos)
        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        l.addWidget(self.progreso)
        self.boton = QPushButton("Ejecutar experimento  →")
        self.boton.setObjectName("Primary")
        self.boton.clicked.connect(self.calcular)
        l.addWidget(self.boton)
        btn = QPushButton("Teoría del método")
        btn.setObjectName("Secondary")
        btn.clicked.connect(lambda: self.abrir_teoria.emit(self.clave_teoria()))
        l.addWidget(btn)

        derecha = QWidget()
        r = QVBoxLayout(derecha)
        r.setContentsMargins(0, 0, 0, 0)
        r.setSpacing(11)
        fila.addWidget(derecha, 1)
        self.resumen = etiqueta("Selecciona un experimento y ejecuta una simulación reproducible.", "Note")
        r.addWidget(self.resumen)
        separador = QSplitter(Qt.Vertical)
        separador.setChildrenCollapsible(False)
        r.addWidget(separador, 1)
        card, gc = marco("ChartCard", 12)
        gc.addWidget(etiqueta("EXPERIMENTO VISUAL", "Eyebrow"))
        self.grafico = Grafico()
        gc.addWidget(self.grafico, 1)
        separador.addWidget(card)
        card, tc = marco("Card", 12)
        tc.addWidget(etiqueta("RESULTADOS Y DATOS REPRODUCIBLES", "Eyebrow"))
        self.tabla = TablaDatos()
        tc.addWidget(self.tabla)
        separador.addWidget(card)
        separador.setSizes([425, 220])
        self._tipo()
        self.calcular_inicial(260)

    def _tipo(self):
        """Filtra modelos ajustables y bloquea entradas que no corresponden."""
        tipo = self.tipo.currentData()
        previo = self.modelo.currentData()
        catalogo_modelos = [d for d in catalogo() if d.dimensionalidad == "univariante"]
        if tipo == "ajuste":
            catalogo_modelos = [d for d in catalogo_modelos if d.clave in familias_ajustables()]
        self.modelo.blockSignals(True)
        self.modelo.clear()
        for d in catalogo_modelos:
            self.modelo.addItem(d.nombre, d.clave)
        pos = self.modelo.findData(previo)
        self.modelo.setCurrentIndex(pos if pos >= 0 else max(0, self.modelo.findData("normal")))
        self.modelo.blockSignals(False)
        self._cambiar_modelo()
        self.modelo.setEnabled(tipo in ("muestra", "ajuste", "qq"))
        self.formulario.setEnabled(tipo in ("muestra", "qq"))
        self.datos.setEnabled(tipo in ("ajuste", "qq"))
        self.n.setEnabled(tipo in ("pi", "integral", "muestra"))

    def _cambiar_modelo(self):
        """Actualiza campos dinámicos sin duplicar esquemas."""
        if self.modelo.currentData():
            self.formulario.usar(obtener(self.modelo.currentData()))

    def _nueva(self):
        """Regenera con nueva semilla, distinta de «Misma»."""
        self.semilla.setValue(secrets.randbelow(2_147_483_648))
        self.calcular()

    def calcular(self):
        """Despacha SciPy y Monte Carlo al grupo de hilos Qt."""
        if self._ocupado:
            return
        try:
            params = self.formulario.valores() if self.tipo.currentData() in ("muestra", "qq") else {}
        except (ParametroInvalidoError, ValueError) as exc:
            self.aviso.emit(str(exc))
            return
        self.progreso.setRange(0, 0)
        self.progreso.show()
        self.boton.setEnabled(False)
        self.trabajar(_simular, self._recibir, self._fin, self.tipo.currentData(), self.modelo.currentData(),
                      params, self.n.value(), self.semilla.value(), self.datos.toPlainText())
        self.aviso.emit("Ejecutando simulación en segundo plano…")

    def _fin(self):
        """Restablece control después del cálculo."""
        self.progreso.hide()
        self.boton.setEnabled(True)

    def _recibir(self, salida: dict):
        """Muestra valores reportables y figura interactiva."""
        self.ultimo = salida
        self.resumen.setText(salida["resumen"])
        self.mostrar_tabla_restaurada(self.tabla, salida["tabla"])
        tipo, *datos = salida["grafico"]
        if tipo == "pi":
            self.grafico.puntos_pi(*datos)
        elif tipo == "barras":
            self.grafico.serie(*datos, "Estimación Monte Carlo")
        elif tipo == "histograma":
            self.grafico.histograma(datos[0])
        elif tipo == "ajuste":
            self.grafico.comparar(*datos)
        else:
            self.grafico.qq(*datos)
        self.aviso.emit("Experimento terminado; usa la misma semilla para reproducirlo.")

    def tablas_exportables(self) -> dict:
        """Resultados de simulación, incluida la muestra generada completa."""
        return {self.tipo.currentText(): self.tabla.datos()} if self.ultimo else {}

    def resumen_exportable(self) -> str:
        """Conclusión para el reporte."""
        return self.resumen.text()

    def clave_teoria(self) -> str:
        """Markdown asociado al modo activo."""
        return {"pi":"montecarlo", "integral":"montecarlo", "muestra":self.modelo.currentData() or "normal",
                "ajuste":"ajuste_distribuciones", "qq":"qq_plot"}[self.tipo.currentData()]

    def estado(self) -> dict:
        """Conserva entrada, parámetros, resultado y semilla de la experiencia."""
        return {"tipo": self.tipo.currentData(), "modelo": self.modelo.currentData(),
                "parametros": self.formulario.valores() if self.modelo.currentData() else {},
                "n": self.n.value(), "semilla": self.semilla.value(), "datos": self.datos.toPlainText(),
                "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo else self._tabla_pendiente}

    def restaurar(self, d: dict):
        """Restaura los controles y ejecuta de nuevo si había una tabla."""
        self.tipo.setCurrentIndex(max(0, self.tipo.findData(d.get("tipo", "pi"))))
        pos = self.modelo.findData(d.get("modelo"))
        if pos >= 0:
            self.modelo.setCurrentIndex(pos)
        self.formulario.restaurar(d.get("parametros", {}))
        self.n.setValue(int(d.get("n", 10_000)))
        self.semilla.setValue(int(d.get("semilla", 42)))
        self.datos.setPlainText(d.get("datos", ""))
        if d.get("tabla") is not None:
            self.limpiar_resultado()
            self._tabla_pendiente = d["tabla"]
            self.recalcular_restaurado()
        else:
            self.limpiar_resultado()
            self.resumen.setText("Selecciona un experimento y ejecuta una simulación reproducible.")
