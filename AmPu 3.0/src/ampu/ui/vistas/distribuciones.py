"""Laboratorio de distribuciones auto-generado a partir del registro."""

import secrets

import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QPushButton, QScrollArea, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from ampu.core.distribuciones import catalogo, obtener
from ampu.core.distribuciones.tabla import ResultadoDistribucion, analizar
from ampu.core.errores import ParametroInvalidoError
from ampu.ui.widgets.comunes import KPIs, campo_semilla, encabezado, etiqueta, marco
from ampu.ui.widgets.formulario import FormularioDistribucion
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


class VistaDistribuciones(VistaTrabajo):
    """PMF/PDF/CDF, probabilidades, cuantiles, tabla y exportación."""

    def __init__(self, parent=None):
        """Compone controles dinámicos, gráfico QtAgg y tabla ordenable."""
        super().__init__(parent)
        self.ultimo: ResultadoDistribucion | None = None
        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(25, 24, 25, 22)
        pagina.setSpacing(17)
        pagina.addWidget(encabezado("01  /  EXPLORADOR ESTADÍSTICO", "Distribuciones", "Del modelo a la probabilidad: parámetros, cuantiles y visualización en un solo lugar."))
        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(17)
        pagina.addLayout(cuerpo, 1)

        izquierda, panel = marco("FormCard", 17)
        izquierda.setFixedWidth(315)
        cuerpo.addWidget(izquierda)
        panel.addWidget(etiqueta("CONFIGURA TU MODELO", "Eyebrow"))
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por nombre…")
        self.buscar.textChanged.connect(self._filtrar)
        panel.addWidget(self.buscar)
        self.categoria = QComboBox()
        for texto, clave in (("Todas las familias", "todas"), ("Discretas", "discretas"),
                             ("Continuas", "continuas"), ("Multivariadas", "multivariadas")):
            self.categoria.addItem(texto, clave)
        self.categoria.currentIndexChanged.connect(self._filtrar)
        panel.addWidget(self.categoria)
        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(self._seleccionada)
        panel.addWidget(self.selector)
        panel.addWidget(etiqueta("PARÁMETROS", "Eyebrow"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.formulario = FormularioDistribucion()
        self.formulario.cambiado.connect(self._validar)
        scroll.setWidget(self.formulario)
        panel.addWidget(scroll, 1)
        panel.addWidget(etiqueta("x  ·  valor a evaluar", "Muted"))
        self.evento = QLineEdit("5")
        self.evento.setToolTip("En modelos multidimensionales escribe una coordenada por componente, separadas por coma.")
        self.evento.textChanged.connect(self._validar)
        panel.addWidget(self.evento)
        linea = QHBoxLayout()
        columna_q = QVBoxLayout()
        columna_q.addWidget(etiqueta("Cuantil q", "Muted"))
        self.cuantil = QDoubleSpinBox()
        self.cuantil.setRange(0, 1)
        self.cuantil.setDecimals(5)
        self.cuantil.setSingleStep(.05)
        self.cuantil.setValue(.5)
        self.cuantil.valueChanged.connect(self._validar)
        columna_q.addWidget(self.cuantil)
        linea.addLayout(columna_q, 1)
        columna_seed = QVBoxLayout()
        columna_seed.addWidget(etiqueta("Semilla", "Muted"))
        self.semilla = campo_semilla()
        columna_seed.addWidget(self.semilla)
        linea.addLayout(columna_seed, 1)
        panel.addLayout(linea)
        linea_accion = QHBoxLayout()
        self.boton_reproducir = QPushButton("↻  Misma semilla")
        self.boton_reproducir.setObjectName("Quiet")
        self.boton_reproducir.setToolTip("Reproduce exactamente la misma simulación/consulta.")
        self.boton_reproducir.clicked.connect(self.calcular)
        linea_accion.addWidget(self.boton_reproducir)
        self.boton_nueva = QPushButton("✦  Nueva")
        self.boton_nueva.setObjectName("Quiet")
        self.boton_nueva.setToolTip("Obtén una semilla nueva y regenera la muestra marginal.")
        self.boton_nueva.clicked.connect(self._nueva_semilla)
        linea_accion.addWidget(self.boton_nueva)
        panel.addLayout(linea_accion)
        self.mensaje = etiqueta("Parámetros listos para calcular.", "Success")
        panel.addWidget(self.mensaje)
        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        panel.addWidget(self.progreso)
        self.calcular_boton = QPushButton("Calcular y visualizar  →")
        self.calcular_boton.setObjectName("Primary")
        self.calcular_boton.clicked.connect(self.calcular)
        panel.addWidget(self.calcular_boton)
        self.teoria_boton = QPushButton("Abrir teoría y fórmulas")
        self.teoria_boton.setObjectName("Secondary")
        self.teoria_boton.clicked.connect(lambda: self.abrir_teoria.emit(self.selector.currentData()))
        panel.addWidget(self.teoria_boton)

        derecha = QWidget()
        right = QVBoxLayout(derecha)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(12)
        cuerpo.addWidget(derecha, 1)
        self.indicadores = KPIs(["P(X=x) / f(x)", "Acumulada F(x)", "Media", "Desviación"])
        right.addWidget(self.indicadores)
        self.separador = QSplitter(Qt.Vertical)
        self.separador.setChildrenCollapsible(False)
        right.addWidget(self.separador, 1)
        chart_card, chart_layout = marco("ChartCard", 13)
        self.grafico_tipo = QComboBox()
        self.grafico_tipo.addItem("Masa / densidad", "densidad")
        self.grafico_tipo.addItem("Distribución acumulada · CDF", "cdf")
        self.grafico_tipo.currentIndexChanged.connect(self._grafico_actual)
        cabecera_grafico = QHBoxLayout()
        cabecera_grafico.addWidget(etiqueta("VISUALIZACIÓN", "Eyebrow"))
        cabecera_grafico.addStretch()
        cabecera_grafico.addWidget(self.grafico_tipo)
        chart_layout.addLayout(cabecera_grafico)
        self.grafico = Grafico()
        chart_layout.addWidget(self.grafico, 1)
        self.separador.addWidget(chart_card)
        tabla_card, tabla_layout = marco("Card", 12)
        subtitulo = QHBoxLayout()
        subtitulo.addWidget(etiqueta("TABLA DE VALORES", "Eyebrow"))
        subtitulo.addStretch()
        subtitulo.addWidget(etiqueta("Doble clic para editar · Ctrl+C / Ctrl+V", "Muted"))
        tabla_layout.addLayout(subtitulo)
        self.tabla = TablaDatos()
        tabla_layout.addWidget(self.tabla)
        self.separador.addWidget(tabla_card)
        self.separador.setSizes([440, 215])
        self._filtrar()
        self.selector.setCurrentIndex(self.selector.findData("binomial"))
        QTimer.singleShot(150, self.calcular)

    def _filtrar(self):
        """Filtra el catálogo; modelos nuevos aparecen sin tocar esta vista."""
        previo = self.selector.currentData()
        busqueda = self.buscar.text().casefold()
        modelos = [m for m in catalogo(self.categoria.currentData()) if busqueda in m.nombre.casefold()]
        self.selector.blockSignals(True)
        self.selector.clear()
        for modelo in modelos:
            self.selector.addItem(modelo.nombre, modelo.clave)
        pos = self.selector.findData(previo)
        if pos >= 0:
            self.selector.setCurrentIndex(pos)
        self.selector.blockSignals(False)
        self._seleccionada()

    def _seleccionada(self):
        """Reconstruye campos y sugiere un evento válido del propio modelo."""
        clave = self.selector.currentData()
        self.calcular_boton.setEnabled(clave is not None)
        if clave is None:
            self.mensaje.setText("No hay distribuciones que coincidan con la búsqueda.")
            return
        modelo = obtener(clave)
        self.formulario.usar(modelo)
        if modelo.dimensionalidad != "univariante":
            x = (modelo.rvs(1, seed=42)[0] if clave == "multinomial" else modelo.media())
            self.evento.setText(", ".join(f"{valor:.5g}" for valor in np.asarray(x)))
        else:
            self.evento.setText(f"{modelo.ppf(.5):.6g}")
        self._validar()

    def _evento(self):
        """Convierte entrada textual a un escalar o vector de coordenadas."""
        try:
            if obtener(self.selector.currentData()).dimensionalidad == "univariante":
                return float(self.evento.text().strip())
            return [float(a.strip()) for a in self.evento.text().split(",")]
        except (ValueError, TypeError) as exc:
            raise ParametroInvalidoError("Escribe x como número o vector separado por comas.") from exc

    def _validar(self):
        """Informa errores antes de enviar trabajo al hilo de cálculo."""
        try:
            self.formulario.valores()
            x = self._evento()
            if not np.all(np.isfinite(x)):
                raise ParametroInvalidoError("El valor x dibujado debe ser finito.")
            self.mensaje.setObjectName("Success")
            self.mensaje.setText("Parámetros listos para calcular.")
            self.calcular_boton.setEnabled(True)
        except (ParametroInvalidoError, ValueError, KeyError) as exc:
            self.mensaje.setObjectName("Error")
            self.mensaje.setText(str(exc))
            self.calcular_boton.setEnabled(False)
        self.mensaje.style().unpolish(self.mensaje)
        self.mensaje.style().polish(self.mensaje)

    def _nueva_semilla(self):
        """Distingue nueva simulación de repetición con la misma semilla."""
        self.semilla.setValue(secrets.randbelow(2_147_483_648))
        self.calcular()

    def calcular(self):
        """Consulta el motor en QThread; la UI solo dibuja el resultado."""
        if self._ocupado or not self.calcular_boton.isEnabled():
            return
        try:
            clave = self.selector.currentData()
            parametros = self.formulario.valores()
            x = self._evento()
        except (ParametroInvalidoError, ValueError) as exc:
            self.aviso.emit(str(exc))
            return
        self.progreso.setRange(0, 0)
        self.progreso.show()
        self.calcular_boton.setEnabled(False)
        self.aviso.emit(f"Calculando {obtener(clave).nombre}…")
        self.trabajar(analizar, self._recibir, self._terminar, clave, parametros, x, self.cuantil.value(), self.semilla.value())

    def _terminar(self):
        """Devuelve los controles a estado interactivo."""
        self.progreso.hide()
        self._validar()

    def _recibir(self, salida: ResultadoDistribucion):
        """Puebla KPIs/tabla/gráfico exclusivamente desde datos del motor."""
        self.ultimo = salida
        r = salida.respuesta
        self.indicadores.actualizar(r["probabilidad_o_densidad"], r["acumulada"], r["media"], r["desviacion"])
        self.tabla.mostrar(salida.tabla)
        self._grafico_actual()
        self.aviso.emit(f"Modelo {self.selector.currentText()}: {len(salida.tabla)} filas calculadas.")

    def _grafico_actual(self):
        """Alterna representación de curva y CDF sin recalcular números."""
        if self.ultimo is not None:
            self.grafico.distribucion(self.ultimo, self.grafico_tipo.currentData())

    def estado(self) -> dict:
        """Datos completos necesarios para reconstruir esta vista."""
        return {"clave": self.selector.currentData(), "categoria": self.categoria.currentData(),
                "parametros": self.formulario.valores(), "evento": self.evento.text(),
                "q": self.cuantil.value(), "semilla": self.semilla.value(), "grafico": self.grafico_tipo.currentData(),
                "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo is not None else None}

    def restaurar(self, estado: dict):
        """Aplica estado guardado y reproduce con la misma semilla."""
        posicion = self.categoria.findData(estado.get("categoria", "todas"))
        self.categoria.setCurrentIndex(max(0, posicion))
        clave = estado.get("clave")
        if self.selector.findData(clave) < 0:
            self.categoria.setCurrentIndex(0)
        posicion = self.selector.findData(clave)
        if posicion >= 0:
            self.selector.setCurrentIndex(posicion)
        self.formulario.restaurar(estado.get("parametros", {}))
        self.evento.setText(str(estado.get("evento", "0")))
        self.cuantil.setValue(float(estado.get("q", .5)))
        self.semilla.setValue(int(estado.get("semilla", 42)))
        self.grafico_tipo.setCurrentIndex(max(0, self.grafico_tipo.findData(estado.get("grafico", "densidad"))))
        QTimer.singleShot(200, self.calcular)

    def tablas_exportables(self) -> dict:
        """Tablas exactamente como se ven, incluidas ediciones/ordenamiento."""
        return {self.selector.currentText() or "Distribución": self.tabla.datos()} if self.ultimo is not None else {}

    def resumen_exportable(self) -> str:
        """Resumen del análisis para el servicio PDF."""
        if self.ultimo is None:
            return "Aún no hay resultados."
        r = self.ultimo.respuesta
        return (f"Distribución {self.selector.currentText()}, x={self.evento.text()}, q={self.cuantil.value():g}. "
                f"CDF={r['acumulada']}; media={r['media']}; varianza={r['varianza']}. "
                f"Semilla {self.semilla.value()}. "
                + ("CDF/PPF marginales para las componentes." if self.ultimo.marginal else ""))

    def clave_teoria(self) -> str:
        """Vincula reportes y lecciones del catálogo."""
        return self.selector.currentData() or "binomial"
