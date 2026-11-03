"""Asistente matemático no modal implementado íntegramente con Dear PyGui."""

from __future__ import annotations

from collections.abc import Callable

import dearpygui.dearpygui as dpg
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from ampu.core.errores import ParametroInvalidoError
from ampu.core.estadistica.calculadora import explicar
from ampu.ui.widgets.comunes import Selector, establecer, texto

PALETA = {
    "Álgebra": [("Fracción", r"\frac{a}{b}"), ("Raíz", r"\sqrt{x}"), ("Potencia", "x^{n}")],
    "Cálculo": [("Integral", r"\int_{a}^{b} f(x)\,dx"), ("Sumatoria", r"\sum_{i=1}^{n} x_i")],
    "Matrices": [("Matriz 2×2", r"\begin{pmatrix}a&b\\c&d\end{pmatrix}")],
    "Griego": [("Alfa", r"\alpha"), ("Sigma", r"\sigma"), ("Media", r"\mu")],
}


class Calculadora:
    """Aritmética explicada y LaTeX editable, sin ejecutar código arbitrario."""

    def __init__(self):
        self._resultado: float | None = None
        self._historial: list[str] = []
        self.tema_actual = "claro"
        self.escala_actual = 1.0
        self.pestana_actual = 0
        self.entrada_modificada: Callable[[], None] = lambda: None
        self.window = dpg.add_window(label="Asistente matemático · AmPu 3.0", width=490,
            height=710, show=False, pos=[720, 80], on_close=lambda: dpg.hide_item(self.window))
        with dpg.tab_bar(parent=self.window, callback=self._cambio_pestana) as self.pestanas:
            with dpg.tab(label="Cálculo explicado", tag="asistente_calculo"):
                self._panel_calculo()
            with dpg.tab(label="Fórmula LaTeX", tag="asistente_latex"):
                self._panel_latex()
        self._figura = Figure(figsize=(4.2, 1.2), dpi=100)
        self._lienzo = FigureCanvasAgg(self._figura)
        self._textura = self._imagen = None
        self._actualizar_historial()

    def _cambio(self, *_args) -> None:
        self.entrada_modificada()

    def _panel_calculo(self) -> None:
        dpg.add_text("Aritmética numérica; no resuelve ecuaciones simbólicas.\n"
                     "Trigonometría en radianes, log base 10 y ln natural.", wrap=450)
        self.entrada = dpg.add_input_text(hint="sqrt(2) + sin(pi/2)", width=-1,
            on_enter=True, callback=self._entrada_cambiada)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Calcular", callback=self._evaluar)
            dpg.add_button(label="Copiar resultado", callback=self.copiar_resultado)
        self.respuesta = dpg.add_text("Resultado final: —", wrap=450)
        self.interpretacion = dpg.add_text("Entrada interpretada: —", wrap=450)
        dpg.add_text("Sustituciones reales del motor:")
        self.pasos = dpg.add_input_text(multiline=True, readonly=True, width=-1, height=145)
        dpg.add_text("Historial · selecciona para reutilizar")
        self.historial = dpg.add_listbox([], width=-1, num_items=4, callback=self._reutilizar)
        teclas = [["7", "8", "9", "/", "sqrt("], ["4", "5", "6", "*", "^"],
                  ["1", "2", "3", "-", "pi"], ["0", ".", "(", ")", "+"],
                  ["sin(", "cos(", "ln(", "log(", "="]]
        for fila in teclas:
            with dpg.group(horizontal=True):
                for tecla in fila:
                    dpg.add_button(label=tecla, width=78,
                                   callback=lambda _s, _a, t=tecla: self._pulsar(t))

    def _panel_latex(self) -> None:
        dpg.add_text("LaTeX para visualizar/copiar; esta pestaña NO calcula.", wrap=450)
        self.latex = dpg.add_input_text(multiline=True, width=-1, height=80,
            hint=r"\frac{1}{\sqrt{2\pi}}e^{-x^2/2}", callback=self._latex_cambiado)
        self.categoria = Selector(dpg.last_container(), list(PALETA), callback=self._mostrar_plantillas)
        self.grupo_plantillas = dpg.add_group(horizontal=True)
        self._mostrar_plantillas()
        dpg.add_button(label="Copiar LaTeX", callback=self.copiar_latex)
        self.estado_vista = dpg.add_text("Vista previa local con MathText; el código lineal siempre permanece disponible.", wrap=450)
        self.grupo_formula = dpg.add_group()

    def _cambio_pestana(self, _sender, app_data, _user_data) -> None:
        self.pestana_actual = 1 if app_data == "asistente_latex" else 0
        if self.pestana_actual:
            self._previsualizar()

    def _entrada_cambiada(self, *_args) -> None:
        self._limpiar_resultado()
        self._cambio()

    def _latex_cambiado(self, *_args) -> None:
        self._previsualizar()
        self._cambio()

    def _limpiar_resultado(self) -> None:
        self._resultado = None
        dpg.set_value(self.respuesta, "Resultado final: pendiente de calcular")
        dpg.set_value(self.interpretacion, "Entrada interpretada: pendiente de calcular")
        dpg.set_value(self.pasos, "")

    def _pulsar(self, tecla: str) -> None:
        if tecla == "=":
            self._evaluar()
        else:
            establecer(self.entrada, texto(self.entrada) + tecla)
            self._limpiar_resultado()
            self._cambio()
            dpg.focus_item(self.entrada)

    def _evaluar(self, *_args) -> None:
        try:
            analisis = explicar(texto(self.entrada))
        except ParametroInvalidoError as exc:
            self._resultado = None
            dpg.set_value(self.respuesta, f"Error: {exc}")
            dpg.set_value(self.interpretacion, "Entrada interpretada: revisa la expresión")
            dpg.set_value(self.pasos, "Corrige el fragmento indicado; la entrada sigue editable.")
            dpg.focus_item(self.entrada)
            return
        self._resultado = analisis.resultado
        dpg.set_value(self.respuesta, f"Resultado final: {analisis.resultado:.12g}")
        dpg.set_value(self.interpretacion, f"Entrada interpretada: {analisis.interpretacion}")
        lineas = [analisis.supuestos]
        lineas += [f"{n}. {p.expresion} → {p.sustitucion} = {p.resultado:.12g}\n   {p.justificacion}"
                   for n, p in enumerate(analisis.pasos, 1)]
        dpg.set_value(self.pasos, "\n\n".join(lineas))
        if not self._historial or self._historial[0] != analisis.entrada:
            self._historial.insert(0, analisis.entrada)
            del self._historial[30:]
        self._actualizar_historial()

    def _actualizar_historial(self) -> None:
        self._historial_etiquetas = [f"{e} = {explicar(e).resultado:.8g}" if self._es_segura_historial(e) else e
                                     for e in self._historial]
        dpg.configure_item(self.historial, items=self._historial_etiquetas)

    @staticmethod
    def _es_segura_historial(expresion: str) -> bool:
        try:
            explicar(expresion)
            return True
        except (ParametroInvalidoError, ValueError, TypeError):
            return False

    def _reutilizar(self, _sender, app_data, _user_data) -> None:
        indice = self._historial_etiquetas.index(app_data)
        establecer(self.entrada, self._historial[indice])
        self._evaluar()

    def copiar_resultado(self) -> None:
        if self._resultado is not None:
            dpg.set_clipboard_text(str(self._resultado))
        else:
            dpg.set_value(self.respuesta, "Primero calcula una expresión válida para copiar el resultado.")

    def copiar_latex(self) -> None:
        dpg.set_clipboard_text(texto(self.latex))
        dpg.set_value(self.estado_vista, "Código LaTeX copiado como texto editable.")

    def _mostrar_plantillas(self, *_args) -> None:
        dpg.delete_item(self.grupo_plantillas, children_only=True, slot=1)
        for nombre, plantilla in PALETA[self.categoria.valor]:
            dpg.add_button(parent=self.grupo_plantillas, label=nombre, small=True,
                           callback=lambda _s, _a, p=plantilla: self.insertar_plantilla(p))

    def insertar_plantilla(self, plantilla: str, _seleccion: str | None = None) -> None:
        establecer(self.latex, texto(self.latex) + plantilla)
        self._previsualizar()
        self._cambio()
        dpg.focus_item(self.latex)

    def _previsualizar(self) -> None:
        if not hasattr(self, "_figura"):
            return
        codigo = texto(self.latex)
        self._figura.clear()
        fondo = "#19283B" if self.tema_actual == "oscuro" else "#FFFFFF"
        tinta = "#F2F5F9" if self.tema_actual == "oscuro" else "#172B45"
        self._figura.set_facecolor(fondo)
        try:
            if len(codigo) > 2000:
                raise ParametroInvalidoError("La fórmula LaTeX debe tener hasta 2000 caracteres.")
            if codigo.strip():
                self._figura.text(.5, .5, f"${codigo}$", ha="center", va="center",
                                  fontsize=15 * self.escala_actual, color=tinta)
            self._lienzo.draw()
            dpg.set_value(self.estado_vista, "Vista MathText actualizada; LaTeX no se evalúa como cálculo.")
        except (ValueError, RuntimeError, ParametroInvalidoError) as exc:
            self._figura.clear()
            self._figura.set_facecolor(fondo)
            dpg.set_value(self.estado_vista, f"No se pudo previsualizar: {exc}")
            return
        rgba = np.asarray(self._lienzo.buffer_rgba(), dtype=np.float32).copy() / 255.0
        valores = rgba.reshape(-1).tolist()
        if not dpg.does_item_exist("ampu_texturas"):
            dpg.add_texture_registry(tag="ampu_texturas")
        if self._textura is None:
            self._textura = dpg.add_dynamic_texture(420, 120, valores, parent="ampu_texturas")
            self._imagen = dpg.add_image(self._textura, parent=self.grupo_formula,
                                         width=420, height=120)
        else:
            dpg.set_value(self._textura, valores)

    def actualizar_tema(self, tema: str, escala: float = 1.0) -> None:
        self.tema_actual = tema
        self.escala_actual = escala
        if hasattr(self, "_figura"):
            self._previsualizar()

    def mostrar(self) -> None:
        dpg.show_item(self.window)
        dpg.focus_item(self.window)

    def estado(self) -> dict:
        return {"entrada": texto(self.entrada), "latex": texto(self.latex),
                "pestana": self.pestana_actual, "historial": list(self._historial)}

    def restaurar(self, datos: dict) -> None:
        establecer(self.entrada, str(datos.get("entrada", "")))
        self._limpiar_resultado()
        establecer(self.latex, str(datos.get("latex", "")))
        historial = datos.get("historial", [])
        self._historial = [e for e in historial[:30] if isinstance(e, str) and 0 < len(e) <= 200] if isinstance(historial, list) else []
        self._actualizar_historial()
        self.pestana_actual = 1 if datos.get("pestana") == 1 else 0
        dpg.set_value(self.pestanas, "asistente_latex" if self.pestana_actual else "asistente_calculo")
        self._previsualizar()
