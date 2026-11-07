"""Ventana principal Dear PyGui: navegación, temas, sesiones y exportación."""

from __future__ import annotations

import logging
from pathlib import Path

import dearpygui.dearpygui as dpg

from ampu.docs.teoria import extraer_formula
from ampu.io import ServicioExportacion as io
from ampu.ui.preferencias import Preferencias
from ampu.ui.temas import PALETAS, rgba
from ampu.ui.vistas.descriptiva import VistaDescriptiva
from ampu.ui.vistas.distribuciones import VistaDistribuciones
from ampu.ui.vistas.inferencia import VistaInferencia
from ampu.ui.vistas.muestreo import VistaMuestreo
from ampu.ui.vistas.probabilidad import VistaProbabilidad
from ampu.ui.vistas.simulacion import VistaSimulacion
from ampu.ui.vistas.teoria import VistaTeoria
from ampu.ui.widgets.calculadora import Calculadora
from ampu.ui.widgets.comunes import habilitar

LOG = logging.getLogger(__name__)
ICONO = Path(__file__).resolve().parent / "recursos" / "icono.svg"
PAGINAS = [("distribuciones", "Distribuciones"), ("muestreo", "Muestreo"),
    ("descriptiva", "Descriptiva"), ("probabilidad", "Probabilidad"),
    ("inferencia", "Inferencia"), ("simulacion", "Simulación"), ("teoria", "Teoría")]
ANALISIS = tuple(clave for clave, _ in PAGINAS if clave != "teoria")
FORMATOS = {"excel": ("Excel · todas las hojas", "xlsx"),
    "csv": ("CSV · tabla visible", "csv"), "png": ("PNG · gráfico actual", "png"),
    "pdf": ("PDF · informe completo", "pdf")}


class VentanaPrincipal:
    """Aplicación de escritorio nativa Dear PyGui; no contiene objetos Qt."""

    def __init__(self, preferencias: Preferencias | dict | None = None):
        self.preferencias = (preferencias if isinstance(preferencias, Preferencias)
                             else Preferencias(valores=preferencias) if isinstance(preferencias, dict)
                             else Preferencias())
        self.modo_tema = str(self.preferencias.get("interfaz/tema", "sistema"))
        if self.modo_tema not in ("sistema", "claro", "oscuro"):
            self.modo_tema = "sistema"
        self.escala_fuente = float(self.preferencias.get("interfaz/escala", 1.0))
        self.tema_actual = "claro"
        self.actual = "distribuciones"
        self._cambios_sin_guardar = False
        self._abriendo_sesion = False
        self._dialogo_mensaje = None
        self._cerrado = False
        dpg.add_texture_registry(tag="ampu_texturas")
        self._temas = {"claro": self._crear_tema(False), "oscuro": self._crear_tema(True)}
        self.window = dpg.add_window(tag="ampu_principal", label="AmPu 3.0 · Laboratorio de estadística",
            width=1420, height=850, min_size=[900, 600], no_saved_settings=True)
        self._crear_menus()
        with dpg.group(parent=self.window, horizontal=True) as barra:
            self.top_etiqueta = dpg.add_text("LABORATORIO  /  AMPU 3.0  ·  DEAR PYGUI")
            self.boton_tema = dpg.add_button(label="Tema oscuro", callback=self.alternar_tema)
            self.boton_guardar = dpg.add_button(label="Guardar sesión", callback=lambda: self.guardar_sesion())
            self.boton_abrir = dpg.add_button(label="Abrir", callback=lambda: self.abrir_sesion())
            self.boton_exportar = dpg.add_button(label="Exportar", callback=self._mostrar_exportacion)
            dpg.add_button(label="Asistente", callback=self.calculadora)
        self.estado = dpg.add_text("AmPu 3.0 · Listo para explorar", parent=self.window)
        dpg.add_separator(parent=self.window)
        with dpg.group(parent=self.window, horizontal=True):
            with dpg.child_window(width=195, height=-1, border=True) as self.sidebar:
                dpg.add_text("AmPu")
                dpg.add_text("VERSIÓN 3.0")
                dpg.add_separator()
                dpg.add_text("EXPLORAR")
                self.botones = {}
                for clave, titulo in PAGINAS:
                    self.botones[clave] = dpg.add_button(label=titulo, width=-1, height=34,
                        callback=lambda _s, _a, k=clave: self.cambiar(k))
                dpg.add_separator()
                dpg.add_text("57 lecciones · 26 modelos\nAnálisis local sin conexión", wrap=170)
            self.contenido = dpg.add_child_window(width=-1, height=-1, border=False)
        self.contenedores = {clave: dpg.add_group(parent=self.contenido, show=False)
                             for clave, _ in PAGINAS}
        self.vistas = {
            "distribuciones": VistaDistribuciones(self.contenedores["distribuciones"]),
            "muestreo": VistaMuestreo(self.contenedores["muestreo"]),
            "descriptiva": VistaDescriptiva(self.contenedores["descriptiva"]),
            "probabilidad": VistaProbabilidad(self.contenedores["probabilidad"]),
            "inferencia": VistaInferencia(self.contenedores["inferencia"]),
            "simulacion": VistaSimulacion(self.contenedores["simulacion"]),
        }
        for vista in self.vistas.values():
            vista.aviso = self.mensaje
            vista.estado_cambiado = self._actualizar_acciones
            vista.entrada_modificada = self._marcar_sesion
            vista.trabajo_finalizado = self._trabajo_finalizado
            vista.abrir_teoria = self.abrir_teoria
        self.vistas["teoria"] = VistaTeoria(self.contenedores["teoria"])
        self.asistente = Calculadora()
        self.asistente.entrada_modificada = self._marcar_sesion
        self._crear_atajos()
        self.aplicar_tema(self.modo_tema)
        self.cambiar("distribuciones")

    @property
    def vista(self):
        return self.vistas[self.actual]

    @staticmethod
    def _crear_tema(oscuro: bool) -> int | str:
        p = PALETAS["oscuro" if oscuro else "claro"]
        fondo, superficie = rgba(p["fondo"]), rgba(p["superficie"])
        tinta, acento, borde = rgba(p["texto"]), rgba(p["acento"]), rgba(p["borde"])
        with dpg.theme() as tema:
            with dpg.theme_component(dpg.mvAll):
                for objetivo, color in ((dpg.mvThemeCol_Text, tinta),
                    (dpg.mvThemeCol_WindowBg, fondo), (dpg.mvThemeCol_ChildBg, superficie),
                    (dpg.mvThemeCol_PopupBg, superficie), (dpg.mvThemeCol_MenuBarBg, superficie),
                    (dpg.mvThemeCol_FrameBg, rgba(p["campo"])),
                    (dpg.mvThemeCol_Button, acento), (dpg.mvThemeCol_ButtonHovered, acento), (dpg.mvThemeCol_ButtonActive, acento), (dpg.mvThemeCol_Header, acento),
                    (dpg.mvThemeCol_HeaderHovered, acento), (dpg.mvThemeCol_CheckMark, acento),
                    (dpg.mvThemeCol_TabSelected, acento), (dpg.mvThemeCol_Border, borde)):
                    dpg.add_theme_color(objetivo, color, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 7, category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Text, rgba(p["texto_boton"]), category=dpg.mvThemeCat_Core)
        return tema

    def _crear_menus(self) -> None:
        with dpg.menu_bar(parent=self.window):
            with dpg.menu(label="Archivo"):
                dpg.add_menu_item(label="Abrir sesión…", shortcut="Ctrl+O", callback=lambda: self.abrir_sesion())
                dpg.add_menu_item(label="Guardar sesión…", shortcut="Ctrl+S", callback=lambda: self.guardar_sesion())
                with dpg.menu(label="Exportar"):
                    self.acciones_exportar = {}
                    for formato, (titulo, _extension) in FORMATOS.items():
                        self.acciones_exportar[formato] = dpg.add_menu_item(label=titulo,
                            callback=lambda _s, _a, f=formato: self.exportar(f))
                dpg.add_menu_item(label="Salir", shortcut="Alt+F4", callback=self._salir)
            with dpg.menu(label="Ver"):
                for numero, (clave, titulo) in enumerate(PAGINAS, 1):
                    dpg.add_menu_item(label=titulo, shortcut=f"Ctrl+{numero}",
                                      callback=lambda _s, _a, k=clave: self.cambiar(k))
                dpg.add_menu_item(label="Alternar claro/oscuro", callback=self.alternar_tema)
                dpg.add_menu_item(label="Seguir apariencia del sistema", callback=lambda: self.aplicar_tema("sistema", persistir=True))
                dpg.add_menu_item(label="Tema claro", callback=lambda: self.aplicar_tema("claro", persistir=True))
                dpg.add_menu_item(label="Tema oscuro", callback=lambda: self.aplicar_tema("oscuro", persistir=True))
                dpg.add_menu_item(label="Aumentar texto", shortcut="Ctrl++", callback=lambda: self.escalar_texto(.1))
                dpg.add_menu_item(label="Reducir texto", shortcut="Ctrl+-", callback=lambda: self.escalar_texto(-.1))
                dpg.add_menu_item(label="Restablecer texto", shortcut="Ctrl+0", callback=lambda: self.escalar_texto(0, restablecer=True))
                dpg.add_menu_item(label="Asistente matemático", shortcut="Ctrl+L", callback=self.calculadora)
            with dpg.menu(label="Ayuda"):
                dpg.add_menu_item(label="Teoría de esta técnica", shortcut="F1", callback=self._teoria_actual)
                dpg.add_menu_item(label="Atajos de teclado", shortcut="F2", callback=self._mostrar_atajos)
                dpg.add_menu_item(label="Acerca de AmPu", callback=self._acerca_de)

    def _crear_atajos(self) -> None:
        with dpg.handler_registry():
            acciones = {dpg.mvKey_S: lambda: self.guardar_sesion(), dpg.mvKey_O: lambda: self.abrir_sesion(),
                        dpg.mvKey_E: lambda: self.exportar("excel"), dpg.mvKey_L: self.calculadora,
                        dpg.mvKey_0: lambda: self.escalar_texto(0, restablecer=True),
                        dpg.mvKey_Add: lambda: self.escalar_texto(.1),
                        dpg.mvKey_Minus: lambda: self.escalar_texto(-.1)}
            for tecla, accion in acciones.items():
                dpg.add_key_press_handler(tecla, callback=lambda _s, _a, a=accion: self._atajo_ctrl(a))
            for numero, (clave, _titulo) in enumerate(PAGINAS, 1):
                dpg.add_key_press_handler(getattr(dpg, f"mvKey_{numero}"),
                    callback=lambda _s, _a, k=clave: self._atajo_ctrl(lambda: self.cambiar(k)))
            dpg.add_key_press_handler(dpg.mvKey_F1, callback=self._teoria_actual)
            dpg.add_key_press_handler(dpg.mvKey_F2, callback=self._mostrar_atajos)

    def _atajo_ctrl(self, accion) -> None:
        if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
            accion()

    def cambiar(self, clave: str) -> bool:
        if clave not in self.vistas:
            return False
        self.actual = clave
        for nombre, contenedor in self.contenedores.items():
            dpg.configure_item(contenedor, show=nombre == clave)
        if clave in ANALISIS and not self._abriendo_sesion:
            self.vistas[clave].calcular_inicial()
        self._actualizar_acciones()
        return True

    def abrir_teoria(self, clave: str) -> None:
        try:
            self.vistas["teoria"].seleccionar(clave)
            self.cambiar("teoria")
        except (ValueError, OSError) as exc:
            self._error(f"No se pudo abrir la lección: {exc}")

    def _teoria_actual(self, *_args) -> None:
        if self.actual == "teoria":
            return
        self.abrir_teoria(self.vista.clave_teoria())

    def mensaje(self, contenido: str) -> None:
        dpg.set_value(self.estado, str(contenido))

    def _error(self, contenido: str) -> None:
        self.mensaje(contenido)
        self._mensaje_modal("AmPu 3.0 · Aviso", contenido)

    def _mensaje_modal(self, titulo: str, contenido: str) -> None:
        if self._dialogo_mensaje is not None and dpg.does_item_exist(self._dialogo_mensaje):
            dpg.delete_item(self._dialogo_mensaje)
        self._dialogo_mensaje = dpg.add_window(label=titulo, modal=True, width=600,
            height=220, pos=[430, 250])
        dpg.add_text(str(contenido), parent=self._dialogo_mensaje, wrap=560)
        dpg.add_button(label="Aceptar", parent=self._dialogo_mensaje, width=120,
                       callback=lambda: dpg.delete_item(self._dialogo_mensaje))

    def _mostrar_atajos(self, *_args) -> None:
        self._mensaje_modal("Atajos de teclado",
            "Ctrl+1…7: cambiar de módulo\nCtrl+S / Ctrl+O: guardar / abrir sesión\n"
            "Ctrl+E: exportar Excel\nCtrl+L: asistente matemático\nF1: teoría de la técnica\nF2: esta ayuda")

    def _acerca_de(self, *_args) -> None:
        self._mensaje_modal("Acerca de AmPu 3.0",
            "Laboratorio educativo de probabilidad y estadística.\n"
            "UI: Dear PyGui · Motor: NumPy, SciPy y pandas.\n"
            "Funciona sin conexión y no evalúa código introducido por el usuario.")

    def _mostrar_exportacion(self, *_args) -> None:
        if self.actual == "teoria" or not self.vista.tablas_exportables():
            self._error("Primero calcula un resultado en un módulo de análisis.")
            return
        self._mensaje_modal("Exportar resultados",
            "Usa Archivo → Exportar o los atajos para elegir Excel, CSV, PNG o PDF.")

    def _trabajo_finalizado(self) -> None:
        if not any(self.vistas[c]._ocupado for c in ANALISIS):
            self.mensaje("Cálculos terminados · AmPu listo.")
        self._actualizar_acciones()

    def _actualizar_acciones(self) -> None:
        disponible = (self.actual in ANALISIS and self.vista.ultimo is not None
                      and not self.vista._desactualizado and bool(self.vista.tablas_exportables()))
        for control in self.acciones_exportar.values():
            habilitar(control, disponible)
        habilitar(self.boton_exportar, disponible)

    def _marcar_sesion(self) -> None:
        if not self._abriendo_sesion:
            self._cambios_sin_guardar = True
            dpg.configure_item(self.window, label="AmPu 3.0 · Laboratorio de estadística *")

    def _sesion_guardada(self) -> None:
        self._cambios_sin_guardar = False
        dpg.configure_item(self.window, label="AmPu 3.0 · Laboratorio de estadística")

    def aplicar_tema(self, tema: str, persistir: bool = False) -> None:
        if tema not in ("sistema", "claro", "oscuro"):
            tema = "sistema"
        self.modo_tema = tema
        self.tema_actual = "oscuro" if tema == "oscuro" else "claro"
        dpg.bind_theme(self._temas[self.tema_actual])
        dpg.set_global_font_scale(self.escala_fuente)
        dpg.configure_item(self.boton_tema,
                           label="Tema claro" if self.tema_actual == "oscuro" else "Tema oscuro")
        for clave in ANALISIS:
            vista = self.vistas[clave]
            vista.grafico.tema(self.tema_actual == "oscuro")
            vista.ajustar_escala(self.escala_fuente)
        self.vistas["teoria"].tema(self.tema_actual)
        self.asistente.actualizar_tema(self.tema_actual, self.escala_fuente)
        if persistir:
            self.preferencias.set("interfaz/tema", tema)
            self.preferencias.set("interfaz/escala", self.escala_fuente)
            self.preferencias.guardar()
        self.mensaje(f"Apariencia {tema} activada; texto al {round(self.escala_fuente * 100)} %.")

    def alternar_tema(self, *_args) -> None:
        self.aplicar_tema("oscuro" if self.tema_actual == "claro" else "claro", persistir=True)

    def escalar_texto(self, paso: float, *, restablecer: bool = False) -> None:
        self.escala_fuente = 1.0 if restablecer else max(.9, min(2.0, round(self.escala_fuente + paso, 2)))
        self.aplicar_tema(self.modo_tema, persistir=True)

    def calculadora(self, *_args) -> None:
        self.asistente.mostrar()

    def _dialogo_archivo(self, titulo: str, nombre: str, extension: str,
                         guardar: bool, accion) -> None:
        etiqueta = "dialogo_archivo_ampu"
        if dpg.does_item_exist(etiqueta):
            dpg.delete_item(etiqueta)
        def recibir(_sender, app_data):
            ruta = app_data.get("file_path_name") if isinstance(app_data, dict) else None
            if ruta:
                accion(Path(ruta))
        with dpg.file_dialog(tag=etiqueta, label=titulo, width=760, height=430,
                             default_filename=nombre, callback=recibir, modal=True,
                             show=True, directory_selector=False, file_count=1):
            dpg.add_file_extension(f".{extension}", custom_text=f"[.{extension}]")
            dpg.add_file_extension(".*")
        if not guardar:
            dpg.configure_item(etiqueta, default_path="")

    def exportar(self, formato: str, destino: str | Path | None = None):
        if formato not in FORMATOS:
            self._error("Formato de exportación no reconocido.")
            return False
        if destino is None:
            self._dialogo_archivo("Exportar resultados", f"AmPu3_{self.actual}.{FORMATOS[formato][1]}",
                                  FORMATOS[formato][1], True, lambda r: self.exportar(formato, r))
            return None
        if self.actual == "teoria":
            self._error("Regresa a un módulo de análisis para exportar resultados.")
            return False
        vista = self.vista
        if vista._desactualizado:
            self._error("Las entradas cambiaron desde el último resultado. Recalcula antes de exportar.")
            return False
        tablas = vista.tablas_exportables()
        if not tablas:
            self._error("Primero calcula un resultado para exportar.")
            return False
        try:
            if formato == "excel":
                ruta = io.excel(tablas, destino)
            elif formato == "csv":
                ruta = io.csv(vista.tabla.datos(), destino)
            elif formato == "png":
                ruta = io.png(vista.grafico.figura, destino)
            else:
                resumen = vista.resumen_exportable() + "\nDescripción gráfica: " + vista.grafico.descripcion
                ruta = io.pdf(destino, f"AmPu 3.0 · {self.actual.title()}", resumen,
                              tablas, vista.grafico.figura, extraer_formula(vista.clave_teoria()))
            self.mensaje(f"Exportación completada: {ruta}")
            return ruta
        except Exception:
            LOG.exception("Error al exportar %s", formato)
            self._error("No se pudo exportar. Verifica el destino y consulta el registro de errores.")
            return False

    def _estado_sesion(self) -> dict:
        return {"interfaz": "Dear PyGui", "modulo": self.actual, "tema": self.modo_tema,
                "asistente": self.asistente.estado(),
                "vistas": {clave: vista.estado() for clave, vista in self.vistas.items()}}

    def guardar_sesion(self, destino: str | Path | None = None):
        if destino is None:
            self._dialogo_archivo("Guardar sesión", "sesion_ampu.json", "json", True,
                                  lambda r: self.guardar_sesion(r))
            return None
        try:
            ruta = io.guardar(self._estado_sesion(), destino)
            self._sesion_guardada()
            self.mensaje(f"Sesión guardada: {ruta}")
            return True
        except Exception:
            LOG.exception("Error al guardar sesión")
            self._error("No se pudo guardar la sesión. Revisa los campos y el destino.")
            return False

    def abrir_sesion(self, origen: str | Path | None = None):
        if origen is None:
            self._dialogo_archivo("Abrir sesión", "sesion_ampu.json", "json", False,
                                  lambda r: self.abrir_sesion(r))
            return None
        anterior = self._estado_sesion()
        vistas: dict = {}
        try:
            estado = io.cargar(origen)
            vistas = estado.get("vistas", {})
            modulo = estado.get("modulo", "distribuciones")
            tema = estado.get("tema", "sistema")
            if tema == "contraste":
                tema = "sistema"
            if (tema not in ("claro", "oscuro", "sistema") or not isinstance(vistas, dict)
                    or modulo not in self.vistas or any(not isinstance(v, dict) for v in vistas.values())
                    or any(clave not in self.vistas for clave in vistas)
                    or not isinstance(estado.get("asistente", {}), dict)):
                raise ValueError("El contenido de la sesión no sigue el esquema de la interfaz.")
            self._abriendo_sesion = True
            self.aplicar_tema(tema)
            self.asistente.restaurar(estado.get("asistente", {}))
            for clave, datos in vistas.items():
                self.vistas[clave].restaurar(datos)
            self.cambiar(modulo)
            self._sesion_guardada()
            self.mensaje(f"Sesión restaurada: {origen}")
            return True
        except Exception:
            LOG.exception("No se pudo abrir sesión")
            try:
                self.aplicar_tema(anterior["tema"])
                self.asistente.restaurar(anterior["asistente"])
                for clave, datos in anterior["vistas"].items():
                    if clave in vistas:
                        self.vistas[clave].restaurar(datos)
                self.cambiar(anterior["modulo"])
            except Exception:
                LOG.exception("La reversión de la sesión falló")
            self._error("El archivo no es una sesión válida o contiene datos incompatibles.")
            return False
        finally:
            self._abriendo_sesion = False

    def procesar(self) -> None:
        for clave in ANALISIS:
            self.vistas[clave].procesar()

    def esperar(self, limite: float = 20.0) -> bool:
        """Espera todas las tareas en autopruebas sin crear viewport."""
        import time
        vencimiento = time.monotonic() + limite
        while time.monotonic() < vencimiento:
            self.procesar()
            if all(not self.vistas[c]._ocupado and not self.vistas[c]._recalculo_pendiente for c in ANALISIS):
                return True
            time.sleep(.005)
        return False

    def _salir(self, *_args) -> None:
        if self._cambios_sin_guardar:
            self._mensaje_modal("Cambios sin guardar",
                "Guarda la sesión desde Archivo antes de salir, o vuelve a elegir Salir para descartar los cambios.")
            self._sesion_guardada()  # La segunda elección explícita de Salir descarta.
            return
        dpg.stop_dearpygui()

    def cerrar(self) -> None:
        if self._cerrado:
            return
        self._cerrado = True
        self.preferencias.set("interfaz/tema", self.modo_tema)
        self.preferencias.set("interfaz/escala", self.escala_fuente)
        try:
            self.preferencias.guardar()
        except OSError:
            LOG.exception("No se pudieron guardar las preferencias")
        dpg.hide_item(self.asistente.window)

    def ejecutar(self) -> int:
        """Crea viewport y bombea Futures antes de cada frame Dear PyGui."""
        dpg.create_viewport(title="AmPu 3.0 · Laboratorio de estadística", width=1450,
                            height=900, min_width=900, min_height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.window, True)
        try:
            while dpg.is_dearpygui_running():
                self.procesar()
                dpg.render_dearpygui_frame()
        finally:
            self.cerrar()
        return 0
