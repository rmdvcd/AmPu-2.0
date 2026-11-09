"""Tabla editable Dear PyGui con paginación, portapapeles TSV e historial."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg

from ampu.ui.entradas import texto_numero


class TablaDatos:
    """Mantiene el DataFrame completo y crea widgets solo para la página visible.

    Las celdas editadas son anotaciones: nunca se devuelven al motor estadístico.
    Cada hoja tiene historiales independientes de hasta veinte operaciones.
    Editar una celda no reconstruye la página: evita perder el foco y el coste
    de recrear cientos de widgets por pulsación.
    """

    def __init__(self, parent: int | str | None = None, *,
                 modificado: Callable[[], None] | None = None,
                 filas_por_pagina: int = 40):
        self._datos = pd.DataFrame()
        self._clave = ""
        self._historiales: dict[str, tuple[list[pd.DataFrame], list[pd.DataFrame]]] = {}
        self._pagina = 0
        self.filas_por_pagina = max(5, min(200, filas_por_pagina))
        self._pintando = False
        self.modificado = modificado
        self.editado: Callable[[], None] | None = None
        self.tag = self._pagina_tag = self._contenedor = self._tabla_tag = None
        self._celdas: dict[tuple[int, int], int | str] = {}
        self._alto = 280
        if parent is not None:
            self.montar(parent)

    def montar(self, parent: int | str) -> None:
        with dpg.group(parent=parent) as self.tag:
            with dpg.group(horizontal=True):
                dpg.add_button(label="Deshacer", callback=lambda: self.undo(), small=True)
                dpg.add_button(label="Rehacer", callback=lambda: self.redo(), small=True)
                dpg.add_button(label="Copiar página", callback=lambda: self.copiar(), small=True)
                dpg.add_button(label="Pegar TSV", callback=lambda: self.pegar(self._inicio_pagina, 0), small=True)
                dpg.add_button(label="Anterior", callback=lambda: self.cambiar_pagina(-1), small=True)
                self._pagina_tag = dpg.add_text("0 filas")
                dpg.add_button(label="Siguiente", callback=lambda: self.cambiar_pagina(1), small=True)
            self._contenedor = dpg.add_child_window(height=self._alto, border=False,
                                                    horizontal_scrollbar=True)
        self._pintar()

    def ajustar_escala(self, escala: float) -> None:
        if self._contenedor is None:
            return
        self._alto = int(280 * min(1.8, max(1.0, escala)))
        dpg.configure_item(self._contenedor, height=self._alto)

    @property
    def _inicio_pagina(self) -> int:
        return self._pagina * self.filas_por_pagina

    @property
    def _total_paginas(self) -> int:
        return max(1, (len(self._datos) + self.filas_por_pagina - 1) // self.filas_por_pagina)

    def reiniciar_historial(self) -> None:
        self._historiales.clear()

    def mostrar(self, tabla: pd.DataFrame, identificador: str | None = None) -> None:
        if identificador is None:
            self.reiniciar_historial()
            self._clave = ""
        else:
            self._clave = identificador
        self._datos = tabla.copy(deep=True).reset_index(drop=True)
        self._pagina = min(self._pagina, self._total_paginas - 1)
        self._pintar()
        if self.editado is not None:
            self.editado()

    def _restablecer(self, tabla: pd.DataFrame) -> None:
        self._datos = tabla.copy(deep=True).reset_index(drop=True)
        self._pagina = min(self._pagina, self._total_paginas - 1)
        self._pintar()

    def _pintar(self) -> None:
        if self._contenedor is None:
            return
        self._pintando = True
        self._celdas = {}
        try:
            dpg.delete_item(self._contenedor, children_only=True, slot=1)
            total = len(self._datos)
            inicio = self._inicio_pagina
            fin = min(total, inicio + self.filas_por_pagina)
            dpg.set_value(self._pagina_tag,
                          f"{total} filas · página {self._pagina + 1}/{self._total_paginas}"
                          if total else "0 filas")
            if not len(self._datos.columns):
                dpg.add_text("La tabla aparecerá después del cálculo.", parent=self._contenedor)
                return
            with dpg.table(parent=self._contenedor, header_row=True, resizable=True,
                           row_background=True, borders_innerH=True, borders_outerH=True,
                           borders_innerV=True, borders_outerV=True, scrollX=True,
                           policy=dpg.mvTable_SizingFixedFit) as self._tabla_tag:
                for columna in self._datos.columns:
                    dpg.add_table_column(label=str(columna), init_width_or_weight=125,
                                         width_fixed=True)
                for fila in range(inicio, fin):
                    with dpg.table_row():
                        for columna in range(len(self._datos.columns)):
                            contenido = self._datos.iat[fila, columna]
                            tag = dpg.add_input_text(default_value=texto_numero(contenido), width=118,
                                                     callback=self._celda_cambiada,
                                                     user_data=(fila, columna))
                            self._celdas[(fila, columna)] = tag
        finally:
            self._pintando = False

    def _celda_cambiada(self, _sender, app_data, user_data) -> None:
        if not self._pintando:
            self.editar_celda(user_data[0], user_data[1], app_data, repintar=False)

    @staticmethod
    def _convertir(texto: str, anterior: object) -> object:
        if texto.strip() in ("", "—"):
            return None
        try:
            numero = float(texto)
            if isinstance(anterior, (int, np.integer)) and not isinstance(anterior, (bool, np.bool_)) and numero.is_integer():
                return int(numero)
            return numero
        except ValueError:
            return texto

    @staticmethod
    def _asignar(tabla: pd.DataFrame, fila: int, columna: int, contenido: object) -> None:
        """pandas 3 no promueve automáticamente una columna numérica a texto."""
        try:
            tabla.iat[fila, columna] = contenido
        except (TypeError, ValueError):
            nombre = tabla.columns[columna]
            tabla[nombre] = tabla[nombre].astype(object)
            tabla.iat[fila, columna] = contenido

    def editar_celda(self, fila: int, columna: int, contenido: object, *,
                     repintar: bool = True) -> None:
        """Edita una celda por coordenadas absolutas; útil también para pruebas."""
        if not (0 <= fila < len(self._datos) and 0 <= columna < len(self._datos.columns)):
            return
        anterior = self._datos.copy(deep=True)
        viejo = self._datos.iat[fila, columna]
        self._asignar(self._datos, fila, columna, self._convertir(str(contenido), viejo))
        tag = self._celdas.get((fila, columna))
        if tag is not None and dpg.does_item_exist(tag) and not self._pintando:
            mostrado = texto_numero(self._datos.iat[fila, columna])
            if dpg.get_value(tag) != mostrado and repintar:
                dpg.set_value(tag, mostrado)
        self._apilar(anterior, self._datos, repintar=repintar)

    def _pila(self) -> tuple[list[pd.DataFrame], list[pd.DataFrame]]:
        if self._clave not in self._historiales:
            self._historiales[self._clave] = ([], [])
        return self._historiales[self._clave]

    def _apilar(self, antes: pd.DataFrame, despues: pd.DataFrame, *,
                repintar: bool = True) -> None:
        if antes.equals(despues):
            return
        deshacer, rehacer = self._pila()
        deshacer.append(antes.copy(deep=True))
        del deshacer[:-20]
        rehacer.clear()
        if repintar:
            self._pintar()
        if self.editado is not None:
            self.editado()
        self._notificar()

    def _notificar(self) -> None:
        if self.modificado is not None:
            self.modificado()

    def undo(self) -> None:
        deshacer, rehacer = self._pila()
        if deshacer:
            rehacer.append(self._datos.copy(deep=True))
            self._restablecer(deshacer.pop())
            self._notificar()

    def redo(self) -> None:
        deshacer, rehacer = self._pila()
        if rehacer:
            deshacer.append(self._datos.copy(deep=True))
            self._restablecer(rehacer.pop())
            self._notificar()

    def puede_deshacer(self) -> bool:
        return bool(self._pila()[0])

    def puede_rehacer(self) -> bool:
        return bool(self._pila()[1])

    def cambiar_pagina(self, delta: int) -> None:
        pagina = max(0, min(self._total_paginas - 1, self._pagina + delta))
        if pagina != self._pagina:
            self._pagina = pagina
            self._pintar()

    def ordenar(self, columna: str, ascendente: bool = True) -> None:
        if columna in self._datos.columns:
            self._datos = self._datos.sort_values(columna, ascending=ascendente,
                                                  kind="stable").reset_index(drop=True)
            self._pintar()
            self._notificar()

    def datos(self) -> pd.DataFrame:
        return self._datos.copy(deep=True)

    def rowCount(self) -> int:
        return len(self._datos)

    def columnCount(self) -> int:
        return len(self._datos.columns)

    def copiar(self) -> str:
        inicio, fin = self._inicio_pagina, min(len(self._datos), self._inicio_pagina + self.filas_por_pagina)
        contenido = self._datos.iloc[inicio:fin].to_csv(sep="\t", index=False, header=False)
        dpg.set_clipboard_text(contenido)
        return contenido

    def pegar(self, fila: int = 0, columna: int = 0, contenido: str | None = None) -> None:
        """Pega un bloque TSV como una sola operación reversible."""
        contenido = dpg.get_clipboard_text() if contenido is None else contenido
        if not contenido or not len(self._datos.columns):
            return
        filas = [linea.split("\t") for linea in contenido.rstrip("\n").splitlines()]
        anterior = self._datos.copy(deep=True)
        necesarias = fila + len(filas)
        if necesarias > len(self._datos):
            extension = pd.DataFrame([[None] * len(self._datos.columns)
                                      for _ in range(necesarias - len(self._datos))],
                                     columns=self._datos.columns)
            self._datos = pd.concat([self._datos, extension], ignore_index=True)
        for df, valores in enumerate(filas):
            for dc, celda in enumerate(valores):
                if 0 <= fila + df and columna + dc < len(self._datos.columns):
                    viejo = self._datos.iat[fila + df, columna + dc]
                    self._asignar(self._datos, fila + df, columna + dc,
                                  self._convertir(celda, viejo))
        self._apilar(anterior, self._datos, repintar=True)
