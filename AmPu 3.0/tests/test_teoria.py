"""Cobertura editorial y render HTML/KaTeX offline de todas las lecciones."""

import re
from pathlib import Path

import pytest

from ampu.core.distribuciones import DISTRIBUCIONES
from ampu.docs.teoria import DOCUMENTOS, PLANTILLA, extraer_formula, leer_teoria, listar_teoria, renderizar


@pytest.mark.parametrize("clave", list(DISTRIBUCIONES))
def test_leccion_de_cada_distribucion(clave):
    texto = leer_teoria(clave)
    for seccion in ("# ", "## Definición formal", "## Parámetros y rango", "## Función de",
                    "## Función de distribución acumulada (CDF)", "## Media, varianza y desviación estándar",
                    "## Propiedades y casos especiales", "## Ejemplo resuelto", "## Referencias", "Figura 1"):
        assert seccion in texto, f"Falta {seccion} en {clave}"
    assert len(re.findall(r"^\$\$", texto, re.M)) >= 8
    assert len(re.findall(r"(?<!\$)\$[^$\n]+\$(?!\$)", texto)) >= 1
    assert extraer_formula(clave)
    for imagen in re.findall(r"!\[[^]]*\]\(([^)]*)\)", texto):
        assert (DOCUMENTOS / imagen).exists(), (clave, imagen)


def test_todas_las_tecnicas_y_plantilla():
    assert len(listar_teoria()) == 57
    for clave, _ in listar_teoria():
        texto = leer_teoria(clave)
        assert "## Ejemplo resuelto" in texto
        assert "## Referencias" in texto
        assert "![" in texto
        assert not any(ord(c) < 32 and c != "\n" for c in texto), clave
    for tema in ("claro", "oscuro"):
        html = renderizar("binomial", tema)
        assert f'data-tema="{tema}"' in html
        assert "auto-render.min.js" in html and "katex.min.js" in html
        assert "<nav" in html or 'class="toc"' in html
        assert "formula-bloque" in html
        assert "AMPUBLOCKTOKEN" not in html
        assert "AMPUINLINETOKEN" not in html
        assert 'src="../imagenes/binomial.png"' in html
        assert len(html) > 5_000
    for nombre in ("katex.min.js", "katex.min.css", "auto-render.min.js", "fonts/KaTeX_Main-Regular.woff2", "fonts/stix-two-math-latin-400-normal.woff2", "LICENSE.katex", "LICENSE.stix"):
        assert (PLANTILLA.parent / nombre).exists()
    assert "https://cdn" not in PLANTILLA.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        leer_teoria("../src/Clases/Funciones")
