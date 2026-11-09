"""Biblioteca offline en Dear PyGui, sin navegador incrustado."""

from __future__ import annotations

import re
from pathlib import Path

import dearpygui.dearpygui as dpg

from ampu.docs.teoria import DOCUMENTOS, leer_teoria, listar_teoria
from ampu.ui.widgets.comunes import Selector, encabezado, texto

IMAGENES = DOCUMENTOS.parent / "imagenes"


def texto_legible(markdown: str) -> str:
    """Conserva LaTeX y Markdown esencial en una representación copiable."""
    texto = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"[Figura: \1]", markdown)
    texto = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", texto)
    texto = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", texto)
    return texto.replace("\r\n", "\n").strip()


class VistaTeoria:
    def __init__(self, parent: int | str, tema: str = "claro"):
        self.tema_actual = tema
        self._textura = self._imagen = None
        self._figuras: dict[str, tuple[int | str, int, int]] = {}
        self._lecciones = listar_teoria()
        with dpg.group(parent=parent) as raiz:
            encabezado(raiz, "07  /  BIBLIOTECA OFFLINE", "Teoría y fórmulas",
                "57 lecciones en texto seleccionable · LaTeX original, búsqueda y figuras locales.")
            with dpg.group(parent=raiz, horizontal=True) as barra:
                dpg.add_text("Filtrar:")
                self.filtro = dpg.add_input_text(width=240, callback=self._filtrar,
                                                 hint="Nombre de la lección…")
                self.selector = Selector(barra, [], callback=self._cargar, width=330)
                dpg.add_text("Buscar dentro:")
                self.busqueda = dpg.add_input_text(width=210, callback=self.buscar,
                                                   on_enter=True)
            self.estado_busqueda = dpg.add_text("", parent=raiz)
            with dpg.group(parent=raiz, horizontal=True):
                self.grupo_imagen = dpg.add_group(width=390)
                self.contenido = dpg.add_input_text(multiline=True, readonly=True,
                    width=-1, height=565, no_horizontal_scroll=False)
        self._filtrar()
        self.seleccionar("binomial")

    def _filtrar(self, *_args) -> None:
        previo = self.selector.valor if hasattr(self, "selector") else None
        filtro = texto(self.filtro).casefold()
        opciones = [(titulo, clave) for clave, titulo in self._lecciones
                    if filtro in titulo.casefold() or filtro in clave.casefold()]
        self.selector.reemplazar(opciones, previo)
        self._cargar()

    def _cargar(self, *_args) -> None:
        clave = self.selector.valor
        if not clave:
            dpg.set_value(self.contenido, "No hay lecciones que coincidan con el filtro.")
            return
        fuente = leer_teoria(clave)
        dpg.set_value(self.contenido, texto_legible(fuente))
        self._cargar_imagen(fuente)
        self.buscar()

    def _cargar_imagen(self, fuente: str) -> None:
        if self._imagen is not None and dpg.does_item_exist(self._imagen):
            dpg.delete_item(self._imagen)
        self._imagen = None
        referencia = re.search(r"!\[([^]]*)\]\((?:\.\./)?(?:imagenes/)?([a-z0-9_-]+\.png)\)", fuente, re.I)
        if not referencia:
            self._textura = None
            return
        ruta = IMAGENES / referencia.group(2)
        if not ruta.is_file() or ruta.parent.resolve() != IMAGENES.resolve():
            self._textura = None
            return
        clave = str(ruta.resolve())
        if not dpg.does_item_exist("ampu_texturas"):
            dpg.add_texture_registry(tag="ampu_texturas")
        try:
            if clave in self._figuras and dpg.does_item_exist(self._figuras[clave][0]):
                textura, ancho, alto = self._figuras[clave]
            else:
                ancho, alto, _canales, datos = dpg.load_image(str(ruta))
                textura = dpg.add_static_texture(ancho, alto, datos, parent="ampu_texturas")
                self._figuras[clave] = (textura, ancho, alto)
            self._textura = textura
            mostrar_ancho = min(370, ancho)
            self._imagen = dpg.add_image(self._textura, parent=self.grupo_imagen,
                width=mostrar_ancho, height=round(alto * mostrar_ancho / ancho))
        except (OSError, RuntimeError, ValueError):
            # El texto y su alternativa siguen disponibles aunque una figura falle.
            self._imagen = self._textura = None

    def seleccionar(self, clave: str) -> None:
        if clave not in dict(self._lecciones):
            raise ValueError(f"No hay una lección para {clave}.")
        if not any(valor == clave for valor in self.selector._claves.values()):
            dpg.set_value(self.filtro, "")
            self._filtrar()
        self.selector.establecer(clave)
        self._cargar()

    def buscar(self, *_args) -> None:
        consulta = texto(self.busqueda).casefold()
        contenido = texto(self.contenido)
        if not consulta:
            dpg.set_value(self.estado_busqueda, "Texto y código LaTeX disponibles para seleccionar y copiar.")
            return
        posicion = contenido.casefold().find(consulta)
        total = contenido.casefold().count(consulta)
        if posicion < 0:
            dpg.set_value(self.estado_busqueda, "Sin coincidencias en esta lección.")
            return
        inicio, fin = max(0, posicion - 70), min(len(contenido), posicion + len(consulta) + 100)
        dpg.set_value(self.estado_busqueda,
                      f"{total} coincidencia(s). Primera: …{contenido[inicio:fin].strip()}…")

    def tema(self, valor: str) -> None:
        self.tema_actual = valor

    def ajustar_escala(self, _escala: float) -> None:
        pass  # La escala global de Dear PyGui también afecta esta vista.

    def estado(self) -> dict:
        return {"clave": self.selector.valor or "binomial"}

    def restaurar(self, datos: dict) -> None:
        self.seleccionar(datos.get("clave", "binomial"))
