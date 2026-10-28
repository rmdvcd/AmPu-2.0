"""LaTeX editable offline: MathML semántico y sin interpretar HTML del usuario."""

import pytest

from ampu.core.errores import ParametroInvalidoError
from ampu.docs.expresiones import previsualizar_latex


def test_previsualizacion_latex_escapa_entrada_y_ofrece_mathml():
    html = previsualizar_latex(r"\frac{a}{b} <script>alert(1)</script>")
    assert "output: 'htmlAndMathml'" in html
    assert "trust: false" in html and "throwOnError: true" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert 'id="alternativa"' in html and 'role="status"' in html
    assert 'src="katex.min.js"' in html and "https://" not in html
    assert 'data-tema="contraste"' in previsualizar_latex("x^2", "contraste")


def test_previsualizacion_acepta_codigo_estructurado_sin_evaluarlo():
    html = previsualizar_latex(r"\int_0^1 x^2\,dx")
    assert r"\int_0^1 x^2\,dx" in html
    with pytest.raises(ParametroInvalidoError):
        previsualizar_latex("x" * 2001)
    with pytest.raises(ParametroInvalidoError):
        previsualizar_latex("x", "arbitrario")
