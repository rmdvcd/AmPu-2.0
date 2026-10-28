"""Contraste de pares de texto explícitos (no sustituye pruebas visuales de SO)."""

from pathlib import Path

ESTILOS = Path(__file__).resolve().parents[1] / "src" / "ampu" / "ui" / "estilos"


def _luminancia(hexadecimal: str) -> float:
    canales = [int(hexadecimal[i:i+2], 16) / 255 for i in (1, 3, 5)]
    lineales = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in canales]
    return sum(a * b for a, b in zip(lineales, (.2126, .7152, .0722)))


def _relacion(a: str, b: str) -> float:
    claro, oscuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + .05) / (oscuro + .05)


def test_pares_principales_cumplen_wcag_aa():
    for tema, pares in {
        "claro": [("#087E73", "#FFFFFF"), ("#61778C", "#FFFFFF"),
                  ("#BDD0DC", "#152741")],
        "oscuro": [("#087E73", "#FFFFFF"), ("#ECF2FA", "#101A2B"),
                   ("#BED2DF", "#0C1625")],
        "contraste": [("#FFDF00", "#000000"), ("#FFFFFF", "#000000")],
    }.items():
        hoja = (ESTILOS / f"{tema}.qss").read_text(encoding="utf-8")
        for primer_color, segundo_color in pares:
            assert primer_color in hoja and segundo_color in hoja
            assert _relacion(primer_color, segundo_color) >= 4.5, (tema, primer_color, segundo_color)
        assert ":focus" in hoja
