"""Las paletas claras y oscuras conservan contraste legible en controles clave."""

from pathlib import Path

ESTILOS = Path(__file__).resolve().parents[1] / "src" / "ampu" / "ui" / "estilos"


def _luminancia(hexadecimal: str) -> float:
    canales = [int(hexadecimal[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineales = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in canales]
    return sum(a * b for a, b in zip(lineales, (.2126, .7152, .0722)))


def _relacion(a: str, b: str) -> float:
    claro, oscuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + .05) / (oscuro + .05)


def test_pares_principales_cumplen_wcag_aa_y_no_hay_tema_extra():
    paletas = {
        "claro": [("#FFFFFF", "#087568"), ("#52657A", "#FFFFFF"),
                  ("#FFFFFF", "#176A72"), ("#A55700", "#FFFFFF")],
        "oscuro": [("#F2F5F9", "#101827"), ("#C0CCD9", "#19283B"),
                   ("#67D8CA", "#19283B"), ("#FFAAAA", "#19283B")],
    }
    for tema, pares in paletas.items():
        hoja = (ESTILOS / f"{tema}.qss").read_text(encoding="utf-8").upper()
        for primer_color, segundo_color in pares:
            assert primer_color in hoja and segundo_color in hoja
            assert _relacion(primer_color, segundo_color) >= 4.5, (tema, primer_color, segundo_color)
        assert ":FOCUS" in hoja
    assert {p.name for p in ESTILOS.glob("*.qss")} == {"claro.qss", "oscuro.qss"}
