"""Calculadora científica integrada: sustituye calc.exe y OSK de Windows."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ampu.core.estadistica.calculadora import calcular
from ampu.core.errores import ParametroInvalidoError


class Calculadora(QDialog):
    """Entrada de teclado nativo + botones matemáticos propios, sin SO externo."""

    def __init__(self, parent=None):
        """Muestra teclado matemático y campo con resultado seleccionable."""
        super().__init__(parent)
        self.setWindowTitle("Calculadora científica · AmPu")
        self.setMinimumWidth(330)
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Funciones trigonométricas en radianes · Enter para calcular"))
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText("sqrt(2) + sin(pi/2)")
        self.entrada.returnPressed.connect(self._evaluar)
        root.addWidget(self.entrada)
        self.respuesta = QLabel("—")
        self.respuesta.setObjectName("H2")
        self.respuesta.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self.respuesta)
        teclas = [
            ["7", "8", "9", "/", "sqrt("], ["4", "5", "6", "*", "^"],
            ["1", "2", "3", "-", "pi"], ["0", ".", "(", ")", "+"],
            ["sin(", "cos(", "ln(", "log(", "="],
        ]
        grid = QGridLayout()
        for row, fila in enumerate(teclas):
            for col, tecla in enumerate(fila):
                boton = QPushButton(tecla)
                boton.setObjectName("Primary" if tecla == "=" else "Secondary")
                boton.clicked.connect(lambda checked=False, t=tecla: self._pulsar(t))
                grid.addWidget(boton, row, col)
        root.addLayout(grid)
        limpiar = QPushButton("Borrar todo")
        limpiar.setObjectName("Quiet")
        limpiar.clicked.connect(lambda: (self.entrada.clear(), self.respuesta.setText("—")))
        root.addWidget(limpiar)

    def _pulsar(self, tecla: str):
        """Inserta en la posición del cursor o evalúa."""
        if tecla == "=":
            self._evaluar()
        else:
            self.entrada.insert(tecla)
            self.entrada.setFocus()

    def _evaluar(self):
        """La lógica segura está íntegramente en core.estadistica.calculadora."""
        try:
            self.respuesta.setText(f"= {calcular(self.entrada.text()):.12g}")
        except ParametroInvalidoError as exc:
            self.respuesta.setText(str(exc))
