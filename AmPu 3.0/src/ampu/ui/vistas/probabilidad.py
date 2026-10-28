"""Combinatoria, condicional, Bayes y momentos de variables discretas."""

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QPushButton, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from ampu.core.estadistica import combinatoria as c, probabilidad as p
from ampu.core.errores import ParametroInvalidoError
from ampu.ui.widgets.comunes import encabezado, etiqueta, marco, numeros
from ampu.ui.widgets.grafico import Grafico
from ampu.ui.widgets.tabla import TablaDatos
from ampu.ui.widgets.trabajos import VistaTrabajo


def _resolver_probabilidad(tipo: str, n: int, k: int, a: float, b: float,
                           pri: str, ver: str, t: float):
    """Resuelve consultas discretas sin usar Qt en el hilo de cálculo."""
    if tipo == "combinatoria":
        datos = {"Factorial n!": c.factorial(n), "Permutaciones P(n,k)": c.permutaciones(n, k),
                 "Combinaciones C(n,k)": c.combinaciones(n, k)}
        tabla = pd.DataFrame({"Operación": list(datos), "Resultado exacto": [str(x) for x in datos.values()]})
        return f"C({n},{k}) = {datos['Combinaciones C(n,k)']} elecciones sin orden.", tabla, ["n!", "P(n,k)", "C(n,k)"], [float(v) for v in datos.values()]
    if tipo == "condicional":
        cond = p.condicional(a, b)
        tabla = pd.DataFrame({"Magnitud": ["P(A∩B)", "P(B)", "P(A|B)"], "Valor": [a, b, cond]})
        return f"P(A|B) = {cond:.6g}. La independencia necesita además P(A).", tabla, ["Conjunta", "Condicional"], [a, cond]
    priores, condiciones = numeros(pri), numeros(ver)
    if tipo == "bayes":
        if len(priores) != len(condiciones):
            raise ParametroInvalidoError("Las listas previas y verosimilitudes deben tener la misma longitud.")
        total = p.probabilidad_total(priores.tolist(), condiciones.tolist())
        if total == 0:
            raise ParametroInvalidoError("No se define Bayes para evidencia de probabilidad cero.")
        posteriores = [p.bayes(j, priores.tolist(), condiciones.tolist()) for j in range(len(priores))]
        tabla = pd.DataFrame({"Hipótesis": [f"B{j+1}" for j in range(len(priores))], "Priori": priores,
                              "Verosimilitud": condiciones, "Posterior": posteriores})
        return (f"P(evidencia) = {total:.6g}; posterior de B1 = {posteriores[0]:.6g}.", tabla,
                [f"B{j+1}" for j in range(len(priores))], posteriores)
    if len(priores) != len(condiciones):
        raise ParametroInvalidoError("Soporte y masas deben tener igual longitud.")
    media = p.esperanza(priores, condiciones)
    var = p.varianza(priores, condiciones)
    mgf = p.generadora_momentos(t, priores, condiciones)
    tabla = pd.DataFrame({"x": priores, "P(X=x)": condiciones})
    return (f"E(X)={media:.6g}, Var(X)={var:.6g}, M_X({t:g})={mgf:.6g}.", tabla,
            [str(v) for v in priores], list(condiciones))


class VistaProbabilidad(VistaTrabajo):
    """Herramientas de combinatoria y probabilidad elemental en una vista."""

    def __init__(self, parent=None):
        """Construye formularios y resultados de probabilidad elemental."""
        super().__init__(parent)
        self.ultimo = None
        root = QVBoxLayout(self)
        root.setContentsMargins(25, 24, 25, 22)
        root.setSpacing(16)
        root.addWidget(encabezado("04  /  FUNDAMENTOS", "Probabilidad básica", "Factoriales exactos, Bayes, independencia y momentos de variables finitas."))
        fila = QHBoxLayout()
        fila.setSpacing(17)
        root.addLayout(fila, 1)
        form_card, l = marco("FormCard", 17)
        form_card.setFixedWidth(315)
        fila.addWidget(form_card)
        l.addWidget(etiqueta("OPERACIÓN", "Eyebrow"))
        self.tipo = QComboBox()
        self.tipo.setAccessibleName("Operación de probabilidad")
        for nombre, clave in (("Combinatoria exacta", "combinatoria"), ("Probabilidad condicional", "condicional"),
                              ("Bayes y probabilidad total", "bayes"), ("E, Var y MGF discretas", "momentos")):
            self.tipo.addItem(nombre, clave)
        self.tipo.currentIndexChanged.connect(self._configurar)
        l.addWidget(self.tipo)
        fr = QFormLayout()
        self.n = QSpinBox()
        self.n.setAccessibleName("Número total de elementos n")
        self.n.setRange(0, 100)
        self.n.setValue(10)
        fr.addRow("n", self.n)
        self.k = QSpinBox()
        self.k.setAccessibleName("Número de elementos elegidos k")
        self.k.setRange(0, 100)
        self.k.setValue(3)
        fr.addRow("k", self.k)
        self.a = QDoubleSpinBox()
        self.a.setAccessibleName("Probabilidad de A e intersección B")
        self.a.setRange(0, 1)
        self.a.setDecimals(5)
        self.a.setValue(.2)
        fr.addRow("P(A∩B)", self.a)
        self.b = QDoubleSpinBox()
        self.b.setAccessibleName("Probabilidad del evento B")
        self.b.setRange(0, 1)
        self.b.setDecimals(5)
        self.b.setValue(.4)
        fr.addRow("P(B)", self.b)
        l.addLayout(fr)
        l.addWidget(etiqueta("LISTA 1 · previas o soporte X", "Eyebrow"))
        self.priores = QLineEdit("0.4, 0.6")
        self.priores.setAccessibleName("Lista de probabilidades previas o soporte X")
        l.addWidget(self.priores)
        l.addWidget(etiqueta("LISTA 2 · verosimilitudes o masas", "Eyebrow"))
        self.verosimilitudes = QLineEdit("0.5, 0.1")
        self.verosimilitudes.setAccessibleName("Lista de verosimilitudes o masas")
        l.addWidget(self.verosimilitudes)
        col = QHBoxLayout()
        col.addWidget(etiqueta("Argumento MGF: t", "Muted"))
        self.t = QDoubleSpinBox()
        self.t.setAccessibleName("Argumento t de la función generadora")
        self.t.setRange(-20, 20)
        self.t.setValue(.5)
        col.addWidget(self.t)
        l.addLayout(col)
        self.progreso = QProgressBar()
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        l.addWidget(self.progreso)
        self.boton = QPushButton("Resolver  →")
        self.boton.setObjectName("Primary")
        self.boton.clicked.connect(self.calcular)
        l.addWidget(self.boton)
        self.teoria_boton = QPushButton("Abrir teoría")
        self.teoria_boton.setObjectName("Secondary")
        self.teoria_boton.clicked.connect(lambda: self.abrir_teoria.emit(self.clave_teoria()))
        l.addWidget(self.teoria_boton)
        l.addStretch()
        rcard, r = marco("Card", 15)
        fila.addWidget(rcard, 1)
        self.configurar_adaptacion(fila, form_card)
        self.conclusion = etiqueta("Configura y resuelve una identidad o consulta.", "H2")
        r.addWidget(self.conclusion)
        divisor = QSplitter(Qt.Vertical)
        r.addWidget(divisor, 1)
        graph_card, gc = marco("ChartCard", 10)
        self.grafico = Grafico()
        gc.addWidget(self.grafico)
        divisor.addWidget(graph_card)
        table_card, tc = marco("Card", 10)
        self.tabla = TablaDatos()
        tc.addWidget(self.tabla)
        divisor.addWidget(table_card)
        divisor.setSizes([440, 220])
        self._configurar()
        self.vigilar_entradas()

    def _configurar(self):
        """Muestra la pertinencia de cada grupo de entradas."""
        tipo = self.tipo.currentData()
        for w in (self.n, self.k):
            w.setEnabled(tipo == "combinatoria")
        for w in (self.a, self.b):
            w.setEnabled(tipo == "condicional")
        for w in (self.priores, self.verosimilitudes):
            w.setEnabled(tipo in ("bayes", "momentos"))
        self.t.setEnabled(tipo == "momentos")

    def calcular(self):
        """Usa solo funciones del core, fuera del hilo principal."""
        if self._ocupado:
            return
        self.progreso.setRange(0, 0)
        self.progreso.show()
        self.boton.setEnabled(False)
        self.trabajar(_resolver_probabilidad, self._recibir, self._fin,
                      self.tipo.currentData(), self.n.value(), self.k.value(),
                      self.a.value(), self.b.value(), self.priores.text(), self.verosimilitudes.text(), self.t.value())
        self.aviso.emit("Resolviendo probabilidad…")

    def _fin(self):
        """Restablece estado tras calcular."""
        self.progreso.hide()
        self.boton.setEnabled(True)

    def _recibir(self, salida):
        """Actualiza tabla, resultado y gráfico."""
        self.ultimo = salida
        self.conclusion.setText(salida[0])
        self.mostrar_tabla_restaurada(self.tabla, salida[1])
        self.grafico.serie(salida[2], salida[3], self.tipo.currentText())
        self.aviso.emit("Resultado disponible para Excel, CSV y PDF.")

    def tablas_exportables(self) -> dict:
        """Tabla visible en orden actual."""
        return {self.tipo.currentText(): self.tabla.datos()} if self.ultimo else {}

    def resumen_exportable(self) -> str:
        """Resumen textual para PDF."""
        return self.conclusion.text()

    def clave_teoria(self) -> str:
        """Lección principal del cálculo."""
        return {"combinatoria":"combinatoria", "condicional":"bayes", "bayes":"bayes", "momentos":"combinatoria"}[self.tipo.currentData()]

    def estado(self) -> dict:
        """Valores de consulta y tabla para restauración."""
        return {"tipo": self.tipo.currentData(), "n": self.n.value(), "k": self.k.value(),
                "a": self.a.value(), "b": self.b.value(), "priori": self.priores.text(),
                "ver": self.verosimilitudes.text(), "t": self.t.value(),
                "tabla": self.tabla.datos().to_dict(orient="list") if self.ultimo else self._tabla_pendiente}

    def restaurar(self, d: dict):
        """Reconstruye formulario de probabilidad."""
        self.tipo.setCurrentIndex(max(0, self.tipo.findData(d.get("tipo", "combinatoria"))))
        for campo in ("n", "k", "a", "b", "t"):
            getattr(self, campo).setValue(d.get(campo, getattr(self, campo).value()))
        self.priores.setText(d.get("priori", "0.4, 0.6"))
        self.verosimilitudes.setText(d.get("ver", "0.5, 0.1"))
        if d.get("tabla") is not None:
            self.limpiar_resultado()
            self._tabla_pendiente = d["tabla"]
            self.recalcular_restaurado()
        else:
            self.limpiar_resultado()
            self.conclusion.setText("Configura y resuelve una identidad o consulta.")
