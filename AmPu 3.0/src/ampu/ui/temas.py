"""Paleta única de Dear PyGui y Matplotlib, con contraste revisable."""

from __future__ import annotations

from typing import Any

PALETAS = {
    "claro": {
        "fondo": "#F7FAFC", "superficie": "#FFFFFF", "texto": "#172B45",
        "secundario": "#52657A", "acento": "#087568", "error": "#A32727",
        "texto_boton": "#FFFFFF", "borde": "#D3DDE7", "campo": "#E9F0F5",
        "acento_hover": "#065A50", "acento_activo": "#04463E",
        "header": "#D5F0EC", "header_hover": "#C3E8E2",
        "seleccion": "#B7E4DC", "deshabilitado": "#5C6F82",
        "nav_fondo": "#15253A", "nav_texto": "#E8EDF4", "nav_muted": "#9BB0C3",
        "nav_hover": "#1E3450",
        "boton_suave": "#E9F0F5", "boton_suave_texto": "#172B45",
        "boton_suave_hover": "#D5DEE7",
        "tabla_alt": "#F0F5F8", "campo_hover": "#DDE6EE", "foco": "#087568",
    },
    "oscuro": {
        "fondo": "#19283B", "superficie": "#223246", "texto": "#E8EDF4",
        "secundario": "#C0CCD9", "acento": "#67D8CA", "error": "#FFAAAA",
        "texto_boton": "#19283B", "borde": "#8294A8", "campo": "#304156",
        "acento_hover": "#7EE0D4", "acento_activo": "#8FE7DC",
        "header": "#2A4A58", "header_hover": "#345A68",
        "seleccion": "#2F5A55", "deshabilitado": "#93A4B8",
        "nav_fondo": "#101C2C", "nav_texto": "#E8EDF4", "nav_muted": "#9BB0C3",
        "nav_hover": "#1A2C42",
        "boton_suave": "#304156", "boton_suave_texto": "#E8EDF4",
        "boton_suave_hover": "#3A4D62",
        "tabla_alt": "#1B2C3F", "campo_hover": "#3A4D62", "foco": "#67D8CA",
    },
}

# Botones primarios registrados al construir la UI; se reasignan al cambiar de tema.
_PRIMARIOS: list[Any] = []


def rgba(color: str) -> tuple[int, int, int, int]:
    """Convierte ``#RRGGBB`` al formato de color Dear PyGui."""
    if len(color) != 7 or not color.startswith("#"):
        raise ValueError("Color hexadecimal #RRGGBB esperado")
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def relacion_contraste(primero: str, segundo: str) -> float:
    """Relación WCAG entre dos colores ``#RRGGBB`` (1:1 a 21:1)."""
    def luminancia(color: str) -> float:
        canales = [componente / 255 for componente in rgba(color)[:3]]
        lineales = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
                    for c in canales]
        return .2126 * lineales[0] + .7152 * lineales[1] + .0722 * lineales[2]

    claro, oscuro = sorted((luminancia(primero), luminancia(segundo)), reverse=True)
    return (claro + .05) / (oscuro + .05)


def marcar_primario(tag: int | str) -> int | str:
    """El botón usará la variante de acento (Calcular, Exportar)."""
    _PRIMARIOS.append(tag)
    return tag


def aplicar_botones_primarios(tema_primario: int | str) -> None:
    """Reasigna el tema de acento a los botones que siguen existiendo."""
    import dearpygui.dearpygui as dpg
    vivos: list[Any] = []
    for tag in _PRIMARIOS:
        if dpg.does_item_exist(tag):
            dpg.bind_item_theme(tag, tema_primario)
            vivos.append(tag)
    _PRIMARIOS[:] = vivos


def _const(dpg: Any, *nombres: str) -> Any:
    for nombre in nombres:
        valor = getattr(dpg, nombre, None)
        if valor is not None:
            return valor
    return None


def crear_temas(oscuro: bool) -> dict[str, int | str]:
    """Temas global, primario, navegación y barra lateral para un modo."""
    import dearpygui.dearpygui as dpg

    p = PALETAS["oscuro" if oscuro else "claro"]
    core = dpg.mvThemeCat_Core

    def color(objetivo: int | None, valor: str) -> None:
        if objetivo is None:
            return
        dpg.add_theme_color(objetivo, rgba(valor), category=core)

    def estilo(objetivo: int | None, *valores: float) -> None:
        if objetivo is None:
            return
        dpg.add_theme_style(objetivo, *valores, category=core)

    tab_sel = _const(dpg, "mvThemeCol_TabSelected", "mvThemeCol_TabActive")
    nav_hl = _const(dpg, "mvThemeCol_NavHighlight")
    texto_sel = _const(dpg, "mvThemeCol_TextSelectedBg")
    texto_off = _const(dpg, "mvThemeCol_TextDisabled")
    tabla_cab = _const(dpg, "mvThemeCol_TableHeaderBg")
    tabla_alt = _const(dpg, "mvThemeCol_TableRowBgAlt")
    tabla_row = _const(dpg, "mvThemeCol_TableRowBg")
    tabla_b1 = _const(dpg, "mvThemeCol_TableBorderStrong")
    tabla_b2 = _const(dpg, "mvThemeCol_TableBorderLight")

    with dpg.theme() as tema_global:
        with dpg.theme_component(dpg.mvAll):
            color(dpg.mvThemeCol_Text, p["texto"])
            color(dpg.mvThemeCol_WindowBg, p["fondo"])
            color(dpg.mvThemeCol_ChildBg, p["superficie"])
            color(dpg.mvThemeCol_PopupBg, p["superficie"])
            color(dpg.mvThemeCol_MenuBarBg, p["superficie"])
            color(dpg.mvThemeCol_FrameBg, p["campo"])
            color(dpg.mvThemeCol_FrameBgHovered, p["campo_hover"])
            color(dpg.mvThemeCol_FrameBgActive, p["header"])
            color(dpg.mvThemeCol_Border, p["borde"])
            color(dpg.mvThemeCol_Separator, p["borde"])
            color(dpg.mvThemeCol_ScrollbarBg, p["fondo"])
            color(dpg.mvThemeCol_ScrollbarGrab, p["borde"])
            color(dpg.mvThemeCol_CheckMark, p["acento"])
            color(dpg.mvThemeCol_SliderGrab, p["acento"])
            color(dpg.mvThemeCol_SliderGrabActive, p["acento_hover"])
            color(dpg.mvThemeCol_Header, p["header"])
            color(dpg.mvThemeCol_HeaderHovered, p["header_hover"])
            color(dpg.mvThemeCol_HeaderActive, p["header_hover"])
            color(dpg.mvThemeCol_Button, p["boton_suave"])
            color(dpg.mvThemeCol_ButtonHovered, p["boton_suave_hover"])
            color(dpg.mvThemeCol_ButtonActive, p["header"])
            color(dpg.mvThemeCol_Tab, p["campo"])
            color(dpg.mvThemeCol_TabHovered, p["header_hover"])
            if tab_sel is not None:
                color(tab_sel, p["header"])
            if nav_hl is not None:
                color(nav_hl, p["foco"])
            if texto_sel is not None:
                color(texto_sel, p["seleccion"])
            if texto_off is not None:
                color(texto_off, p["deshabilitado"])
            if tabla_cab is not None:
                color(tabla_cab, p["campo"])
            if tabla_row is not None:
                color(tabla_row, p["superficie"])
            if tabla_alt is not None:
                color(tabla_alt, p["tabla_alt"])
            if tabla_b1 is not None:
                color(tabla_b1, p["borde"])
            if tabla_b2 is not None:
                color(tabla_b2, p["borde"])
            estilo(dpg.mvStyleVar_FrameRounding, 6)
            estilo(dpg.mvStyleVar_ChildRounding, 8)
            estilo(_const(dpg, "mvStyleVar_WindowRounding"), 8)
            estilo(dpg.mvStyleVar_GrabRounding, 4)
            estilo(_const(dpg, "mvStyleVar_TabRounding"), 6)
            estilo(_const(dpg, "mvStyleVar_ScrollbarRounding"), 8)
            estilo(_const(dpg, "mvStyleVar_PopupRounding"), 8)
            estilo(dpg.mvStyleVar_FramePadding, 10, 6)
            estilo(dpg.mvStyleVar_ItemSpacing, 10, 8)
            estilo(dpg.mvStyleVar_ItemInnerSpacing, 6, 4)
            estilo(dpg.mvStyleVar_WindowPadding, 10, 8)
            estilo(_const(dpg, "mvStyleVar_CellPadding"), 8, 5)
            estilo(_const(dpg, "mvStyleVar_ScrollbarSize"), 14)
            estilo(_const(dpg, "mvStyleVar_GrabMinSize"), 12)
            estilo(_const(dpg, "mvStyleVar_FrameBorderSize"), 0)
        with dpg.theme_component(dpg.mvButton):
            color(dpg.mvThemeCol_Text, p["boton_suave_texto"])
            color(dpg.mvThemeCol_Button, p["boton_suave"])
            color(dpg.mvThemeCol_ButtonHovered, p["boton_suave_hover"])
            color(dpg.mvThemeCol_ButtonActive, p["header"])
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            color(dpg.mvThemeCol_Text, p["deshabilitado"])
            color(dpg.mvThemeCol_Button, p["campo"])
            color(dpg.mvThemeCol_ButtonHovered, p["campo"])
            color(dpg.mvThemeCol_ButtonActive, p["campo"])

    with dpg.theme() as tema_primario:
        with dpg.theme_component(dpg.mvButton):
            color(dpg.mvThemeCol_Text, p["texto_boton"])
            color(dpg.mvThemeCol_Button, p["acento"])
            color(dpg.mvThemeCol_ButtonHovered, p["acento_hover"])
            color(dpg.mvThemeCol_ButtonActive, p["acento_activo"])
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            color(dpg.mvThemeCol_Text, p["deshabilitado"])
            color(dpg.mvThemeCol_Button, p["campo"])

    with dpg.theme() as tema_nav:
        with dpg.theme_component(dpg.mvButton):
            color(dpg.mvThemeCol_Text, p["nav_texto"])
            color(dpg.mvThemeCol_Button, p["nav_fondo"])
            color(dpg.mvThemeCol_ButtonHovered, p["nav_hover"])
            color(dpg.mvThemeCol_ButtonActive, p["acento"])
        with dpg.theme_component(dpg.mvAll):
            color(dpg.mvThemeCol_Text, p["nav_texto"])

    with dpg.theme() as tema_nav_activo:
        with dpg.theme_component(dpg.mvButton):
            color(dpg.mvThemeCol_Text, p["texto_boton"])
            color(dpg.mvThemeCol_Button, p["acento"])
            color(dpg.mvThemeCol_ButtonHovered, p["acento_hover"])
            color(dpg.mvThemeCol_ButtonActive, p["acento_activo"])

    with dpg.theme() as tema_sidebar:
        with dpg.theme_component(dpg.mvAll):
            color(dpg.mvThemeCol_ChildBg, p["nav_fondo"])
            color(dpg.mvThemeCol_Border, p["nav_fondo"])
            color(dpg.mvThemeCol_Text, p["nav_texto"])
            color(dpg.mvThemeCol_Separator, p["nav_hover"])
            estilo(dpg.mvStyleVar_ChildRounding, 0)
            estilo(dpg.mvStyleVar_WindowPadding, 16, 16)
            estilo(dpg.mvStyleVar_ItemSpacing, 8, 6)
        tipo_hijo = getattr(dpg, "mvChildWindow", None)
        if tipo_hijo is not None:
            with dpg.theme_component(tipo_hijo):
                color(dpg.mvThemeCol_ChildBg, p["nav_fondo"])
                color(dpg.mvThemeCol_Border, p["nav_fondo"])

    return {"global": tema_global, "primario": tema_primario, "nav": tema_nav,
            "nav_activo": tema_nav_activo, "sidebar": tema_sidebar}
