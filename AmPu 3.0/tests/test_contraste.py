"""Contraste de la fuente única de colores Dear PyGui/Matplotlib."""

from ampu.ui.temas import PALETAS, relacion_contraste, rgba


def test_pares_principales_cumplen_wcag_aa_y_no_hay_tema_extra():
    assert set(PALETAS) == {"claro", "oscuro"}
    for tema, p in PALETAS.items():
        pares = [(p["texto"], p["fondo"]), (p["texto"], p["superficie"]),
                 (p["secundario"], p["superficie"]), (p["texto_boton"], p["acento"]),
                 (p["error"], p["superficie"])]
        for texto, fondo in pares:
            assert relacion_contraste(texto, fondo) >= 4.5, (tema, texto, fondo)
        assert relacion_contraste(p["acento"], p["superficie"]) >= 3.0


def test_conversion_rgba_no_modifica_los_colores():
    assert rgba("#087568") == (8, 117, 104, 255)
    assert rgba("#67D8CA") == (103, 216, 202, 255)
