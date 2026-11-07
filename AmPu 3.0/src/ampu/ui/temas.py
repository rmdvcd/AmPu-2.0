"""Paleta única de Dear PyGui y Matplotlib, con contraste revisable."""

from __future__ import annotations

PALETAS = {
    "claro": {
        "fondo": "#F7FAFC", "superficie": "#FFFFFF", "texto": "#172B45",
        "secundario": "#52657A", "acento": "#087568", "error": "#A32727",
        "texto_boton": "#FFFFFF", "borde": "#D3DDE7", "campo": "#E9F0F5",
    },
    "oscuro": {
        "fondo": "#19283B", "superficie": "#223246", "texto": "#E8EDF4",
        "secundario": "#C0CCD9", "acento": "#67D8CA", "error": "#FFAAAA",
        "texto_boton": "#19283B", "borde": "#8294A8", "campo": "#304156",
    },
}


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
