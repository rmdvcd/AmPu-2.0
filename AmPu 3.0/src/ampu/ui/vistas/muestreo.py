"""Diseños muestrales y estimación de tamaño reproducible."""

import secrets

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout, QLineEdit, QPlainTextEdit,
    QProgressBar, QPushButton, QScrollArea, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from ampu.core.muestreo.diseno import ResultadoDiseno, ejecutar_diseno
from ampu.ui.widgets.comunes import campo_semilla, encabezado, etiqueta, filas_estratos, marco
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


class VistaMuestreo(VistaTrabajo):
    """MAS finito/infinito, sistemático, estratos, Neyman y conglomerados."""

    def __init__(self, parent=None):
        """Proporciona un único flujo: diseño → sorteo → tabla → exportación."""
        super().__init__(parent)
        self.ultimo: ResultadoDiseno | None = None
        pagina = QVBoxLayout(self)
        pagina.setContentsMargins(25, 24, 25, 22)
        pagina.setSpacing(16)
        pagina.addWidget(encabezado("02  /  DISEÑO MUESTRAL", "Muestreo", "Planea el tamaño, elige unidades y reproduce cualquier sorteo con una semilla."))
        fila = QHBoxLayout()
        fila.setSpacing(17)
        pagina.addLayout(fila, 1)
        left, form = marco("FormCard", 17)
        left.setFixedWidth(315)
        fila.addWidget(left)
        form.addWidget(etiqueta("TIPO DE SELECCIÓN", "Eyebrow"))
        self.metodo = QComboBox()
        for nombre, clave in (("Aleatorio simple · finito", "finito"), ("Aleatorio · con reemplazo", "infinito"),
                              ("Sistemático", "sistematico"), ("Estratificado proporcional", "proporcional"),
                              ("Estratificado Neyman", "neyman"), ("Estratificado óptimo", "optimo"),
                              ("Por conglomerados", "conglomerados")):
            self.metodo.addItem(nombre, clave)
        self.metodo.currentIndexChanged.connect(self._metodo_cambiado)
        form.addWidget(self.metodo)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        campos = QWidget()
        entradas = QVBoxLayout(campos)
        entradas.setContentsMargins(0, 0, 5, 0)
        entradas.setSpacing(8)
        scroll.setWidget(campos)
        form.addWidget(scroll, 1)
        vals = QHBoxLayout()
        n_col = QVBoxLayout()
        n_col.addWidget(etiqueta("Población N", "Muted"))
        self.N = QSpinBox()
        self.N.setRange(1, 1_000_000)
        self.N.setMinimumHeight(34)
        self.N.setValue(400)
        n_col.addWidget(self.N)
        vals.addLayout(n_col)
        tam_col = QVBoxLayout()
        tam_col.addWidget(etiqueta("Tamaño n", "Muted"))
        self.n = QSpinBox()
        self.n.setRange(1, 1_000_000)
        self.n.setMinimumHeight(34)
        self.n.setValue(40)
        tam_col.addWidget(self.n)
        vals.addLayout(tam_col)
        entradas.addLayout(vals)
        self.auto = QCheckBox("Calcular n a partir del margen")
        self.auto.setToolTip("Activa tamaño recomendado para proporción con corrección finita si procede.")
        entradas.addWidget(self.auto)
        linea = QHBoxLayout()
        linea.setSpacing(4)
        for titulo, attr, inicial, paso in (("Confianza", "confianza", .95, .01),
                                            ("Proporción", "p", .5, .05), ("Error d", "error", .05, .01)):
            col = QVBoxLayout()
            col.addWidget(etiqueta(titulo, "Muted"))
            spin = QDoubleSpinBox()
            spin.setRange(.00001, .99999)
            spin.setMinimumHeight(34)
            spin.setMaximumWidth(89)
            spin.setDecimals(5)
            spin.setSingleStep(paso)
            spin.setValue(inicial)
            setattr(self, attr, spin)
            col.addWidget(spin)
            linea.addLayout(col)
        entradas.addLayout(linea)
        self.rotulo_estratos = etiqueta("ESTRATOS / CONGLOMERADOS", "Eyebrow")
        entradas.addWidget(self.rotulo_estratos)
        self.ayuda_estratos = etiqueta("Una fila por grupo: nombre, Nh, desviación, coste", "Muted")
        entradas.addWidget(self.ayuda_estratos)
        self.estratos = QPlainTextEdit("Norte,120,8,1\nCentro,200,5,2\nSur,80,10,1")
        self.estratos.setFixedHeight(90)
        entradas.addWidget(self.estratos)
        self.rotulo_ids = etiqueta("IDENTIFICADORES OPCIONALES", "Eyebrow")
        entradas.addWidget(self.rotulo_ids)
        self.poblacion = QLineEdit()
        self.poblacion.setPlaceholderText("ID-1, ID-2, … (N elementos)")
        self.poblacion.setToolTip("Solo para métodos simples; si vacío, se generan IDs de 1 a N.")
        entradas.addWidget(self.poblacion)
        self.rotulo_por_grupo = etiqueta("Unidades por conglomerado (0 = completo)", "Muted")
        entradas.addWidget(self.rotulo_por_grupo)
        self.por_grupo = QSpinBox()
        self.por_grupo.setRange(0, 1_000_000)
        self.por_grupo.setMinimumHeight(34)
        self.por_grupo.setValue(0)
        entradas.addWidget(self.por_grupo)
        entradas.addStretch()
        linea_seed = QHBoxLayout()
        linea_seed.addWidget(etiqueta("Semilla reproducible", "Muted"))
        self.semilla = campo_semilla()
        linea_seed.addWidget(self.semilla)
        form.addLayout(linea_seed)
        acciones = QHBoxLayout()
        repetir = QPushButton("↻ Misma")
        repetir.setObjectName("Quiet")
        repetir.clicked.connect(self.calcular)
        acciones.addWidget(repetir)
        nueva = QPushButton("✦ Nueva semilla")
        nueva.setObjectName("Quiet")
        nueva.clicked.connect(self._nueva)
        acciones.addWidget(nueva)
        form.addLayout(acciones)
        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        form.addWidget(self.progreso)
        self.boton = QPushButton("Diseñar y seleccionar  →")
        self.boton.setObjectName("Primary")
        self.boton.clicked.connect(self.calcular)
        form.addWidget(self.boton)
        teoria = QPushButton("Abrir teoría de muestreo")
        teoria.setObjectName("Secondary")
        teoria.clicked.connect(lambda: self.abrir_teoria.emit(self.clave_teoria()))
        form.addWidget(teoria)
        form.addStretch()

        right = QWidget()
        r = QVBoxLayout(right)
        r.setContentsMargins(0, 0, 0, 0)
        r.setSpacing(11)
        fila.addWidget(right, 1)
        self.resumen = etiqueta("Configura el diseño y pulsa «Diseñar y seleccionar».", "Note")
        r.addWidget(self.resumen)
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)
        r.addWidget(splitter, 1)
        chart_card, chart_l = marco("ChartCard", 12)
        chart_l.addWidget(etiqueta("POBLACIÓN Y MUESTRA", "Eyebrow"))
        self.grafico = Grafico()
        chart_l.addWidget(self.grafico, 1)
        splitter.addWidget(chart_card)
        table_card, table_l = marco("Card", 12)
        top = QHBoxLayout()
        top.addWidget(etiqueta("RESULTADO EXPORTABLE", "Eyebrow"))
        top.addStretch()
        self.hojas = QComboBox()
        self.hojas.currentTextChanged.connect(self._mostrar_tabla)
        top.addWidget(self.hojas)
        table_l.addLayout(top)
        self.tabla = TablaDatos()
        table_l.addWidget(self.tabla)
        splitter.addWidget(table_card)
        splitter.setSizes([410, 240])
        self._metodo_cambiado()
        self.calcular_inicial(200)

    def _metodo_cambiado(self):
        """Muestra entradas pertinentes sin alterar las fórmulas del motor."""
        clave = self.metodo.currentData()
        estratificado = clave in ("proporcional", "neyman", "optimo", "conglomerados")
        for widget in (self.rotulo_estratos, self.ayuda_estratos, self.estratos):
            widget.setVisible(estratificado)
        for widget in (self.rotulo_ids, self.poblacion):
            widget.setVisible(not estratificado)
        for widget in (self.rotulo_por_grupo, self.por_grupo):
            widget.setVisible(clave == "conglomerados")
        if clave == "conglomerados":
            self.n.setValue(min(self.n.value(), 2))

    def _nueva(self):
        """Genera nueva semilla criptográficamente aleatoria y vuelve a sortear."""
        self.semilla.setValue(secrets.randbelow(2_147_483_648))
        self.calcular()

    def calcular(self):
        """Ejecuta selección potencialmente grande sin bloquear el event loop."""
        if self._ocupado:
            return
        try:
            fila = (filas_estratos(self.estratos.toPlainText())
                    if self.metodo.currentData() in ("proporcional", "neyman", "optimo", "conglomerados") else None)
            ids = ([v.strip() for v in self.poblacion.text().split(",") if v.strip()]
                   if self.poblacion.text().strip() else None)
        except ValueError as exc:
            self.aviso.emit(str(exc))
            return
        self.progreso.setRange(0, 0)
        self.progreso.show()
        self.boton.setEnabled(False)
        self.trabajar(ejecutar_diseno, self._recibir, self._fin,
                      self.metodo.currentData(), self.N.value(), self.n.value(), self.semilla.value(),
                      fila, self.auto.isChecked(), self.p.value(), self.error.value(),
                      self.confianza.value(), ids, self.por_grupo.value() or None)
        self.aviso.emit("Seleccionando unidades con semilla reproducible…")

    def _fin(self):
        """Restablece el botón de cálculo."""
        self.progreso.hide()
        self.boton.setEnabled(True)

    def _recibir(self, salida: ResultadoDiseno):
        """Presenta el mismo diseño exportable que devolvió el motor."""
        self.ultimo = salida
        self.resumen.setText(salida.resumen)
        self.grafico.barras(salida.etiquetas, salida.poblacion, salida.seleccion)
        self.iniciar_hojas(salida.tablas)
        self.hojas.blockSignals(True)
        self.hojas.clear()
        self.hojas.addItems(salida.tablas)
        hoja = self._hoja_pendiente if self._hoja_pendiente in salida.tablas else "Selección"
        if hoja in salida.tablas:
            self.hojas.setCurrentText(hoja)
        self._hoja_pendiente = None
        self.hojas.blockSignals(False)
        self._mostrar_tabla()
        self.aviso.emit(f"Muestreo completado · {salida.resumen}")

    def _mostrar_tabla(self):
        """Alterna entre hoja de asignaciones y hoja de unidades."""
        if self.ultimo is not None:
            self.mostrar_hoja(self.tabla, self.hojas.currentText())

    def tablas_exportables(self) -> dict:
        """Conserva todas las hojas y las ediciones de la hoja visible."""
        if self.ultimo is None:
            return {}
        return self.hojas_exportables(self.tabla)

    def resumen_exportable(self) -> str:
        """Texto para el informe PDF del diseño."""
        return self.ultimo.resumen if self.ultimo else "Sin diseño aún."

    def clave_teoria(self) -> str:
        """Lección ligada al método seleccionado."""
        return {"finito":"muestreo_finito", "infinito":"muestreo_infinito", "sistematico":"muestreo_sistematico",
                "proporcional":"muestreo_estratificado", "neyman":"muestreo_neyman", "optimo":"muestreo_optimo",
                "conglomerados":"muestreo_conglomerados"}[self.metodo.currentData()]

    def estado(self) -> dict:
        """Serializa diseño, entradas, semilla y todas las tablas."""
        tablas = ({k: v.to_dict(orient="list") for k, v in self.tablas_exportables().items()}
                  if self.ultimo else self._hojas_pendientes)
        return {"metodo": self.metodo.currentData(), "N": self.N.value(), "n": self.n.value(),
                "semilla": self.semilla.value(), "estratos": self.estratos.toPlainText(),
                "poblacion": self.poblacion.text(), "n_por_grupo": self.por_grupo.value(),
                "auto": self.auto.isChecked(), "p": self.p.value(), "error": self.error.value(),
                "confianza": self.confianza.value(), "hoja": self.hojas.currentText() or self._hoja_pendiente,
                "tablas": tablas}

    def restaurar(self, d: dict):
        """Restaura controles y reproduce el sorteo guardado."""
        pos = self.metodo.findData(d.get("metodo", "finito"))
        self.metodo.setCurrentIndex(max(0, pos))
        for campo in ("N", "n", "semilla", "por_grupo"):
            valor = d.get("n_por_grupo" if campo == "por_grupo" else campo)
            if valor is not None:
                getattr(self, campo).setValue(int(valor))
        for campo in ("estratos", "poblacion"):
            control = getattr(self, campo)
            (control.setPlainText if isinstance(control, QPlainTextEdit) else control.setText)(d.get(campo, ""))
        for campo in ("p", "error", "confianza"):
            getattr(self, campo).setValue(float(d.get(campo, getattr(self, campo).value())))
        self.auto.setChecked(bool(d.get("auto", False)))
        self.limpiar_resultado()
        self._hojas_pendientes = d.get("tablas") if isinstance(d.get("tablas"), dict) else {}
        self._hoja_pendiente = d.get("hoja")
        self.recalcular_restaurado()
