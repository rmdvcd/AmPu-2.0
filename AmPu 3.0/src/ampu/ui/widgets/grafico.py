"""Gráficos embebidos con QtAgg, zoom/pan y tooltip de coordenadas."""

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ampu.core.distribuciones.tabla import ResultadoDistribucion


class Grafico(QWidget):
    """Contenedor Matplotlib reutilizado para todas las vistas."""

    def __init__(self, parent=None):
        """Construye una sola Figure y sus controles nativos de navegación."""
        super().__init__(parent)
        self.figura = Figure(figsize=(7, 3.6), dpi=105)
        self.lienzo = FigureCanvasQTAgg(self.figura)
        self.barra = NavigationToolbar2QT(self.lienzo, self)
        self.pie = QLabel("Arrastra para explorar · usa la lupa para ampliar")
        self.pie.setObjectName("Muted")
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(3)
        v.addWidget(self.barra)
        v.addWidget(self.lienzo, 1)
        v.addWidget(self.pie)
        self.oscuro = False
        self._ultimo: tuple | None = None
        self.lienzo.mpl_connect("motion_notify_event", self._mover)
        self.vacio()

    def _mover(self, evento):
        """Muestra coordenadas sin bloquear ni repintar a cada movimiento."""
        if evento.inaxes and evento.xdata is not None and evento.ydata is not None:
            self.lienzo.setToolTip(f"x = {evento.xdata:.5g} · y = {evento.ydata:.5g}")

    def tema(self, oscuro: bool):
        """Redibuja la última serie al cambiar de tema."""
        self.oscuro = oscuro
        # Matplotlib consulta la paleta nativa, no QSS, para invertir sus iconos SVG.
        paleta = self.barra.palette()
        paleta.setColor(self.barra.backgroundRole(), QColor("#1B2A40" if oscuro else "#FFFFFF"))
        self.barra.setPalette(paleta)
        self.barra.update()
        if self._ultimo:
            funcion, args, kwargs = self._ultimo
            getattr(self, funcion)(*args, **kwargs)
        else:
            self.vacio()

    def _ejes(self):
        """Reinicia ejes y paleta compatibles con fondo claro u oscuro."""
        fondo = "#1B2A40" if self.oscuro else "#FFFFFF"
        tinta = "#DCEBF4" if self.oscuro else "#243D56"
        self.figura.clear()
        self.figura.set_facecolor(fondo)
        ax = self.figura.add_subplot(111)
        ax.set_facecolor(fondo)
        ax.tick_params(colors=tinta, labelsize=9)
        for lado in ax.spines.values():
            lado.set_color("#496076" if self.oscuro else "#D8E4ED")
        ax.xaxis.label.set_color(tinta)
        ax.yaxis.label.set_color(tinta)
        ax.title.set_color(tinta)
        ax.grid(axis="y", alpha=.16, color=tinta)
        return ax

    def _fin(self):
        """Dibuja fuera del hilo de cálculo, únicamente en el hilo principal."""
        self.figura.tight_layout(pad=1.6)
        self.lienzo.draw_idle()

    def vacio(self):
        """Representa estado inicial ligero, sin muestras inventadas."""
        ax = self._ejes()
        ax.text(.5, .5, "Los resultados aparecerán aquí", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="#7894A8")
        ax.set_axis_off()
        self._fin()

    def distribucion(self, resultado: ResultadoDistribucion, modo: str = "densidad"):
        """Dibuja masa/densidad sombreada o CDF sin confundir CDF con área."""
        self._ultimo = ("distribucion", (resultado, modo), {})
        ax = self._ejes()
        x, y, cdf = resultado.x, resultado.y, resultado.acumulada
        color = "#4FD1BE" if self.oscuro else "#138F87"
        gris = "#7593A8" if self.oscuro else "#A9BAC6"
        if modo == "cdf":
            if resultado.discreta:
                ax.step(x, cdf, where="post", color=color, lw=2.3)
            else:
                ax.plot(x, cdf, color=color, lw=2.3)
            if x.min() <= resultado.evento <= x.max() and not resultado.marginal:
                ax.scatter([resultado.evento], [float(resultado.respuesta["acumulada"])], s=65, color="#F0A96B", zorder=5)
                ax.axvline(resultado.evento, color="#F0A96B", ls="--", lw=1)
            ax.set(ylabel="F(x)", ylim=(-.03, 1.06), title="Función de distribución acumulada" + (" · marginal empírica" if resultado.marginal else ""))
        else:
            if resultado.discreta:
                ax.bar(x, y, color=np.where(x <= resultado.evento, color, gris), alpha=.86, width=.8)
            else:
                ax.plot(x, y, lw=2.3, color=color)
                ax.fill_between(x, y, where=(x <= resultado.evento), interpolate=True, color="#39B9AD", alpha=.29)
            ax.set(ylabel="P(X = x)" if resultado.discreta else "f(x)",
                   title=("Masa de probabilidad" if resultado.discreta else "Densidad de probabilidad")
                   + (" · marginal simulada" if resultado.marginal else ""))
            ax.set_ylim(bottom=0)
        ax.set_xlabel("x" if not resultado.marginal else "Primera componente")
        self.pie.setText("Punto marcado = CDF(x); el área sombreada representa P(X ≤ x)." if not resultado.marginal else
                         "Gráfico de la primera marginal simulada; consulta conjunta en la tabla.")
        self._fin()

    def barras(self, etiquetas: list[str], poblacion: list[int], seleccion: list[int]):
        """Compara tamaños de grupos originales y unidades seleccionadas."""
        self._ultimo = ("barras", (etiquetas, poblacion, seleccion), {})
        ax = self._ejes()
        posicion = np.arange(len(etiquetas))
        ax.bar(posicion-.19, poblacion, width=.38, label="Población", color="#7494A9")
        ax.bar(posicion+.19, seleccion, width=.38, label="Muestra", color="#2FC0AC")
        ax.set_xticks(posicion, etiquetas)
        ax.set_ylabel("Unidades")
        ax.set_title("Diseño muestral")
        ax.legend(frameon=False, labelcolor="#BED8E3" if self.oscuro else "#304B5B")
        self.pie.setText("Las barras reflejan el diseño exportable, no una estimación adicional.")
        self._fin()

    def serie(self, etiquetas: list[str], valores: list[float], titulo: str):
        """Representa resultados categóricos no muestrales."""
        self._ultimo = ("serie", (etiquetas, valores, titulo), {})
        ax = self._ejes()
        ax.bar(etiquetas, valores, color="#27BDAE", alpha=.85)
        ax.set(title=titulo, ylabel="Valor")
        self.pie.setText("Altura de cada barra calculada por el motor estadístico.")
        self._fin()

    def histograma(self, datos: np.ndarray, modo: str = "Histograma", y: np.ndarray | None = None):
        """Grafica datos observados como histograma, boxplot o dispersión."""
        self._ultimo = ("histograma", (datos, modo, y), {})
        ax = self._ejes()
        if modo == "Boxplot":
            ax.boxplot(datos, vert=False, patch_artist=True,
                       boxprops={"facecolor":"#35B7AC", "edgecolor":"#70CFC5"},
                       medianprops={"color":"#F3AA74", "linewidth":2})
            ax.set_xlabel("Observación")
        elif modo == "Dispersión" and y is not None:
            ax.scatter(datos, y, s=40, color="#27BDAE", alpha=.8, edgecolors="white", linewidths=.4)
            ax.set(xlabel="X", ylabel="Y")
        else:
            ax.hist(datos, bins="auto", color="#27BDAE", edgecolor="#EAF4F4", alpha=.9)
            ax.set(xlabel="Observación", ylabel="Frecuencia")
        ax.set_title(modo if modo != "Dispersión" or y is not None else "Histograma")
        self.pie.setText("Selecciona, amplía o guarda el gráfico con la barra superior.")
        self._fin()

    def dispersion(self, x: np.ndarray, y: np.ndarray, ajuste: np.ndarray | None = None, titulo: str = "Datos pareados"):
        """Dispersión y, si existe, línea ya predicha por el motor."""
        self._ultimo = ("dispersion", (x, y, ajuste, titulo), {})
        ax = self._ejes()
        ax.scatter(x, y, color="#32BDAB", s=35, alpha=.8, label="Observaciones")
        if ajuste is not None:
            orden = np.argsort(x)
            ax.plot(x[orden], ajuste[orden], color="#E29B72", lw=2.2, label="Ajuste")
            ax.legend(frameon=False, labelcolor="#BED8E3" if self.oscuro else "#304B5B")
        ax.set(xlabel="X", ylabel="Y", title=titulo)
        self.pie.setText("Las predicciones de la línea proceden del motor de regresión.")
        self._fin()

    def puntos_pi(self, puntos: np.ndarray, dentro: np.ndarray):
        """Ilustra clasificación de puntos devuelta por el motor Monte Carlo."""
        self._ultimo = ("puntos_pi", (puntos, dentro), {})
        ax = self._ejes()
        ax.scatter(puntos[dentro, 0], puntos[dentro, 1], s=8, color="#30BFAA", alpha=.65, label="Dentro")
        ax.scatter(puntos[~dentro, 0], puntos[~dentro, 1], s=8, color="#F4A773", alpha=.65, label="Fuera")
        ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="Coordenada U", ylabel="Coordenada V", title="El área del cuarto de círculo")
        ax.set_aspect("equal", adjustable="box")
        ax.legend(frameon=False, labelcolor="#BED8E3" if self.oscuro else "#304B5B")
        self.pie.setText("Verde: dentro · naranja: fuera. Semilla y tamaño reproducibles.")
        self._fin()

    def comparar(self, datos: np.ndarray, grid: np.ndarray, densidad: np.ndarray):
        """Contrasta histograma de la muestra con PDF devuelta por SciPy."""
        self._ultimo = ("comparar", (datos, grid, densidad), {})
        ax = self._ejes()
        ax.hist(datos, bins="auto", density=True, color="#26B8AA", alpha=.55, label="Datos")
        ax.plot(grid, densidad, lw=2.6, color="#F3AC77", label="Ajuste")
        ax.set(title="Datos reales frente a densidad ajustada", xlabel="Valor", ylabel="Densidad")
        ax.legend(frameon=False, labelcolor="#BED8E3" if self.oscuro else "#304B5B")
        self.pie.setText("Compara forma y colas; la p de KS posterior al ajuste es exploratoria.")
        self._fin()

    def qq(self, teorico: np.ndarray, muestra: np.ndarray):
        """Compara cuantiles teóricos calculados por el motor con datos reales."""
        self._ultimo = ("qq", (teorico, muestra), {})
        ax = self._ejes()
        ax.scatter(teorico, muestra, color="#27BDAE", alpha=.78)
        ax.plot([teorico.min(), teorico.max()], [muestra.min(), muestra.max()], ls="--", color="#E49C72")
        ax.set(xlabel="Cuantil teórico", ylabel="Cuantil empírico", title="QQ-plot · datos frente al modelo")
        self.pie.setText("Una curva sistemática o colas apartadas sugieren desajuste.")
        self._fin()
