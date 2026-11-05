"""Gráficos Matplotlib ``Agg`` presentados como texturas Dear PyGui.

El mismo ``Figure`` se reutiliza para PNG/PDF; no se carga ningún backend Qt.
"""

from __future__ import annotations

import dearpygui.dearpygui as dpg
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from ampu.core.distribuciones.tabla import ResultadoDistribucion


class Grafico:
    """Lienzo exportable con adaptador opcional a la interfaz Dear PyGui."""

    ANCHO = 720
    ALTO = 270

    def __init__(self, parent: int | str | None = None):
        self.figura = Figure(figsize=(self.ANCHO / 100, self.ALTO / 100), dpi=100)
        self.lienzo = FigureCanvasAgg(self.figura)
        self.oscuro = False
        self._escala = 1.0
        self._ultimo: tuple | None = None
        self._descripcion = "Sin resultados: el gráfico aparecerá después del cálculo."
        self._contenedor = self._textura = self._imagen = None
        self._pie_tag = self._descripcion_tag = None
        if parent is not None:
            self.montar(parent)
        self.vacio()

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def montar(self, parent: int | str) -> None:
        self._contenedor = dpg.add_group(parent=parent)
        self._pie_tag = dpg.add_text("Visualización calculada por el motor estadístico.",
                                     parent=self._contenedor, wrap=800)
        self._descripcion_tag = dpg.add_text(self._descripcion, parent=self._contenedor,
                                             wrap=800, color=self._tinta())

    def _pie(self, contenido: str) -> None:
        if self._pie_tag is not None:
            dpg.set_value(self._pie_tag, contenido)

    def _describir(self, texto: str) -> None:
        if self._ultimo is not None:
            texto += " Las ediciones de la tabla son anotaciones y no actualizan este gráfico."
        self._descripcion = texto
        if self._descripcion_tag is not None:
            dpg.set_value(self._descripcion_tag, texto)

    def tema(self, oscuro: bool) -> None:
        self.oscuro = oscuro
        if self._ultimo:
            funcion, args, kwargs = self._ultimo
            getattr(self, funcion)(*args, **kwargs)
        else:
            self.vacio()

    def escalar_texto(self, factor: float) -> None:
        self._escala = factor
        if self._ultimo:
            funcion, args, kwargs = self._ultimo
            getattr(self, funcion)(*args, **kwargs)
        else:
            self.vacio()

    def _fin(self) -> None:
        for eje in self.figura.axes:
            eje.title.set_fontsize(12 * self._escala)
            eje.xaxis.label.set_fontsize(11 * self._escala)
            eje.yaxis.label.set_fontsize(11 * self._escala)
            if eje.get_legend():
                for texto in eje.get_legend().get_texts():
                    texto.set_fontsize(10 * self._escala)
        self.figura.tight_layout(pad=2.2)
        self.lienzo.draw()
        if self._contenedor is None:
            return
        if self._ultimo is None:
            if self._imagen is not None and dpg.does_item_exist(self._imagen):
                dpg.configure_item(self._imagen, show=False)
            return
        rgba = np.asarray(self.lienzo.buffer_rgba(), dtype=np.float32).copy()
        rgba /= 255.0
        valores = rgba.reshape(-1).tolist()
        if self._textura is None:
            if not dpg.does_item_exist("ampu_texturas"):
                dpg.add_texture_registry(tag="ampu_texturas")
            self._textura = dpg.add_dynamic_texture(self.ANCHO, self.ALTO, valores,
                                                    parent="ampu_texturas")
            self._imagen = dpg.add_image(self._textura, parent=self._contenedor,
                                         before=self._pie_tag, width=self.ANCHO, height=self.ALTO)
        else:
            dpg.set_value(self._textura, valores)
        dpg.configure_item(self._imagen, show=True)

    def _tinta(self) -> str:
        """Color de texto/ticks según el tema activo."""
        return "#E5ECF3" if self.oscuro else "#30445C"

    def _ejes(self):
        """Reinicia ejes y paleta compatibles con fondo claro u oscuro."""
        fondo = "#19283B" if self.oscuro else "#FFFFFF"
        tinta = self._tinta()
        self.figura.clear()
        self.figura.set_facecolor(fondo)
        ax = self.figura.add_subplot(111)
        ax.set_facecolor(fondo)
        ax.tick_params(colors=tinta, labelsize=10 * self._escala)
        for lado in ax.spines.values():
            lado.set_color("#52647A" if self.oscuro else "#D3DDE7")
        ax.xaxis.label.set_color(tinta)
        ax.yaxis.label.set_color(tinta)
        ax.title.set_color(tinta)
        ax.grid(alpha=.14, color=tinta)
        ax.set_axisbelow(True)
        ax.margins(x=.04)
        return ax

    def vacio(self):
        """Representa estado inicial ligero, sin muestras inventadas."""
        self._ultimo = None
        ax = self._ejes()
        ax.text(.5, .5, "Los resultados aparecerán aquí", transform=ax.transAxes,
                ha="center", va="center", fontsize=12, color="#7894A8")
        ax.set_axis_off()
        self._describir("Sin resultados. Al calcular, la descripción textual y la tabla complementarán la figura.")
        self._fin()

    def distribucion(self, resultado: ResultadoDistribucion, modo: str = "densidad"):
        """Dibuja masa/densidad sombreada o CDF sin confundir CDF con área."""
        self._ultimo = ("distribucion", (resultado, modo), {})
        ax = self._ejes()
        x, y, cdf = resultado.x, resultado.y, resultado.acumulada
        color = "#60D8CA" if self.oscuro else "#087568"
        gris = "#8294A8" if self.oscuro else "#A9B7C5"
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
                barras = ax.bar(x, y, color=np.where(x <= resultado.evento, color, gris), alpha=.86, width=.8)
                if len(x) <= 25:
                    ax.bar_label(barras, fmt="%.3g", fontsize=8 * self._escala, color=self._tinta(), padding=2)
                    ax.margins(y=.14)
            else:
                ax.plot(x, y, lw=2.3, color=color)
                ax.fill_between(x, y, where=(x <= resultado.evento), interpolate=True, color="#39B9AD", alpha=.29)
            if x.min() <= resultado.evento <= x.max() and not resultado.marginal:
                y_evento = float(resultado.respuesta["probabilidad_o_densidad"])
                ax.scatter([resultado.evento], [y_evento], s=65, color="#F0A96B", zorder=5)
                ax.axvline(resultado.evento, color="#F0A96B", ls="--", lw=1)
            ax.set(ylabel="P(X = x)" if resultado.discreta else "f(x)",
                   title=("Masa de probabilidad" if resultado.discreta else "Densidad de probabilidad")
                   + (" · marginal simulada" if resultado.marginal else ""))
            ax.set_ylim(bottom=0)
        ax.set_xlabel("x" if not resultado.marginal else "Primera componente")
        self._pie("Punto naranja = evento x; el área sombreada representa P(X ≤ x)." if not resultado.marginal else
                         "Gráfico de la primera marginal simulada; consulta conjunta en la tabla.")
        if resultado.marginal:
            self._describir("Primera marginal simulada, no densidad o masa conjunta. "
                            "Consulta el resultado de la consulta multivariante en la tabla.")
        else:
            tipo = "masa de probabilidad" if resultado.discreta else "densidad de probabilidad"
            descripcion = (("Función de distribución acumulada discreta. " if resultado.discreta else
                            "Función de distribución acumulada continua. ") if modo == "cdf" else
                           f"Gráfico de {tipo} con región hasta el evento marcada. ")
            self._describir(descripcion + f"Para x = {resultado.evento:.6g}, "
                            f"CDF = {float(resultado.respuesta['acumulada']):.6g}. "
                            "La tabla contiene los valores exactos del motor.")
        self._fin()

    def barras(self, etiquetas: list[str], poblacion: list[int], seleccion: list[int]):
        """Compara tamaños de grupos originales y unidades seleccionadas."""
        self._ultimo = ("barras", (etiquetas, poblacion, seleccion), {})
        ax = self._ejes()
        posicion = np.arange(len(etiquetas))
        ax.bar(posicion-.19, poblacion, width=.38, label="Población",
               color="#8294A8" if self.oscuro else "#70869B")
        ax.bar(posicion+.19, seleccion, width=.38, label="Muestra",
               color="#60D8CA" if self.oscuro else "#087568", hatch="//")
        ax.set_xticks(posicion, etiquetas)
        if len(etiquetas) > 5:
            ax.tick_params(axis="x", rotation=28)
            for etiqueta in ax.get_xticklabels():
                etiqueta.set_ha("right")
        ax.set_ylabel("Unidades")
        ax.set_title("Diseño muestral")
        ax.legend(frameon=False, labelcolor="#D5E0EB" if self.oscuro else "#344B62")
        self._pie("Las barras reflejan el diseño exportable, no una estimación adicional.")
        self._describir("Barras comparativas de población y muestra por grupo: " +
                       "; ".join(f"{etiqueta}: población {total}, muestra {elegidos}"
                                 for etiqueta, total, elegidos in list(zip(etiquetas, poblacion, seleccion))[:10]) +
                       ("; hay más grupos en la tabla." if len(etiquetas) > 10 else ". Lee la tabla para copiar los datos."))
        self._fin()

    def serie(self, etiquetas: list[str], valores: list[float], titulo: str):
        """Representa resultados categóricos no muestrales."""
        self._ultimo = ("serie", (etiquetas, valores, titulo), {})
        ax = self._ejes()
        barras = ax.bar(etiquetas, valores, color="#60D8CA" if self.oscuro else "#087568", alpha=.95)
        if len(etiquetas) > 5:
            ax.tick_params(axis="x", rotation=28)
            for etiqueta in ax.get_xticklabels():
                etiqueta.set_ha("right")
        if len(etiquetas) <= 20:
            ax.bar_label(barras, fmt="%.4g", fontsize=8 * self._escala, color=self._tinta(), padding=2)
        ax.margins(y=.12)
        ax.set(title=titulo, ylabel="Valor")
        self._pie("Altura de cada barra calculada por el motor estadístico.")
        self._describir(f"{titulo}: gráfico de barras. " +
                       "; ".join(f"{etiqueta}: {valor:.6g}" for etiqueta, valor in
                                 list(zip(etiquetas, valores))[:10]) +
                       ("; hay más categorías en la tabla." if len(etiquetas) > 10 else ". Datos en la tabla."))
        self._fin()

    def histograma(self, datos: np.ndarray, modo: str = "Histograma", y: np.ndarray | None = None):
        """Grafica datos observados como histograma, boxplot o dispersión."""
        self._ultimo = ("histograma", (datos, modo, y), {})
        ax = self._ejes()
        if modo == "Boxplot":
            ax.boxplot(datos, vert=False, patch_artist=True,
                       boxprops={"facecolor": "#60D8CA" if self.oscuro else "#4CAFA4",
                                 "edgecolor": "#D8F2EE" if self.oscuro else "#075F56"},
                       medianprops={"color": "#142131" if self.oscuro else "#A85219",
                                    "linewidth": 2})
            ax.set_xlabel("Observación")
        elif modo == "Dispersión" and y is not None:
            ax.scatter(datos, y, s=40, color="#60D8CA" if self.oscuro else "#087568",
                       alpha=.9, edgecolors="white", linewidths=.4)
            ax.set(xlabel="X", ylabel="Y")
        else:
            ax.hist(datos, bins="auto", color="#60D8CA" if self.oscuro else "#087568",
                    edgecolor="#25364B" if self.oscuro else "#FFFFFF", alpha=.95)
            ax.set(xlabel="Observación", ylabel="Frecuencia")
        ax.set_title(modo if modo != "Dispersión" or y is not None else "Histograma")
        self._pie("Selecciona, amplía o guarda el gráfico con la barra superior.")
        self._describir((f"Diagrama de dispersión con {len(datos)} pares X e Y." if modo == "Dispersión" and y is not None
                         else f"Diagrama de caja con {len(datos)} observaciones." if modo == "Boxplot"
                         else f"Histograma con {len(datos)} observaciones.") +
                       " La tabla contiene los valores del análisis; no infieras causalidad por la imagen.")
        self._fin()

    def dispersion(self, x: np.ndarray, y: np.ndarray, ajuste: np.ndarray | None = None, titulo: str = "Datos pareados"):
        """Dispersión y, si existe, línea ya predicha por el motor."""
        self._ultimo = ("dispersion", (x, y, ajuste, titulo), {})
        ax = self._ejes()
        ax.scatter(x, y, color="#60D8CA" if self.oscuro else "#087568", s=35, alpha=.9, label="Observaciones")
        if ajuste is not None:
            orden = np.argsort(x)
            ax.plot(x[orden], ajuste[orden], color="#FFB36B" if self.oscuro else "#A85219",
                    lw=2.2, ls="--", label="Ajuste")
            ax.legend(frameon=False, labelcolor="#D5E0EB" if self.oscuro else "#344B62")
        ax.set(xlabel="X", ylabel="Y", title=titulo)
        self._pie("Las predicciones de la línea proceden del motor de regresión.")
        self._describir(f"{titulo}: dispersión de {len(x)} pares observados" +
                       (" con línea de ajuste entregada por el motor." if ajuste is not None else ".") +
                       " Consulta la tabla y la conclusión para interpretar el modelo.")
        self._fin()

    def puntos_pi(self, puntos: np.ndarray, dentro: np.ndarray):
        """Ilustra clasificación de puntos devuelta por el motor Monte Carlo."""
        self._ultimo = ("puntos_pi", (puntos, dentro), {})
        ax = self._ejes()
        ax.scatter(puntos[dentro, 0], puntos[dentro, 1], s=8,
                   color="#60D8CA" if self.oscuro else "#087568", alpha=.85, marker="o", label="Dentro")
        ax.scatter(puntos[~dentro, 0], puntos[~dentro, 1], s=8,
                   color="#FFB36B" if self.oscuro else "#B45419", alpha=.85, marker="x", label="Fuera")
        ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="Coordenada U", ylabel="Coordenada V", title="El área del cuarto de círculo")
        ax.set_aspect("equal", adjustable="box")
        ax.legend(frameon=False, labelcolor="#D5E0EB" if self.oscuro else "#344B62")
        self._pie("Verde: dentro · naranja: fuera. Semilla y tamaño reproducibles.")
        self._describir(f"Simulación visual de {len(puntos)} puntos en un cuadrado unitario: "
                       "verde representa dentro del cuarto de círculo y naranja fuera. "
                       "El resultado y la semilla constan en la tabla.")
        self._fin()

    def comparar(self, datos: np.ndarray, grid: np.ndarray, densidad: np.ndarray):
        """Contrasta histograma de la muestra con PDF devuelta por SciPy."""
        self._ultimo = ("comparar", (datos, grid, densidad), {})
        ax = self._ejes()
        ax.hist(datos, bins="auto", density=True,
                color="#60D8CA" if self.oscuro else "#087568", alpha=.7, label="Datos")
        ax.plot(grid, densidad, lw=2.6, color="#FFB36B" if self.oscuro else "#A85219",
                ls="--", label="Ajuste")
        ax.set(title="Datos reales frente a densidad ajustada", xlabel="Valor", ylabel="Densidad")
        ax.legend(frameon=False, labelcolor="#D5E0EB" if self.oscuro else "#344B62")
        self._pie("Compara forma y colas; la p de KS posterior al ajuste es exploratoria.")
        self._describir(f"Histograma de {len(datos)} datos reales junto a la densidad ajustada "
                       "por el motor. La prueba KS posterior al ajuste es exploratoria; "
                       "valores y advertencias en la tabla.")
        self._fin()

    def qq(self, teorico: np.ndarray, muestra: np.ndarray):
        """Compara cuantiles teóricos calculados por el motor con datos reales."""
        self._ultimo = ("qq", (teorico, muestra), {})
        ax = self._ejes()
        ax.scatter(teorico, muestra, color="#60D8CA" if self.oscuro else "#087568", alpha=.9)
        ax.plot([teorico.min(), teorico.max()], [muestra.min(), muestra.max()], ls="--",
                color="#FFB36B" if self.oscuro else "#A85219")
        ax.set(xlabel="Cuantil teórico", ylabel="Cuantil empírico", title="QQ-plot · datos frente al modelo")
        self._pie("Una curva sistemática o colas apartadas sugieren desajuste.")
        self._describir(f"Gráfico de cuantiles teóricos frente a {len(muestra)} cuantiles "
                       "empíricos y línea de referencia. Revisa la tabla para los valores exactos.")
        self._fin()
