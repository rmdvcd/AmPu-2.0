"""Casos de FuncionesTest.java (original intacto) y divergencias corregidas.

Los resultados Java se redondeaban con Math.rint(x*10000)/10000. Se replican
los casos matemáticamente correctos y se explicitan los que contenían fallos.
"""

import pytest
from scipy import stats

from ampu.core.distribuciones import obtener
from ampu.core.muestreo import asignacion_estratos, tamano_proporcion


def redondear(x):
    """Emula el redondeo a cuatro decimales de los tests históricos."""
    return round(x, 4)


def test_binomial_y_binomial_negativa():
    b = obtener("binomial")
    assert redondear(b.pmf(5, n=10, p=.5)) == .2461
    assert redondear(b.cdf(5, n=10, p=.5)) == .623
    assert redondear(b.cola_inclusiva(5, n=10, p=.5)) == .623
    assert b.media(n=10, p=.5) == 5
    assert b.varianza(n=10, p=.5) == 2.5
    nb = obtener("binomial_negativa")
    assert nb.pmf(3, r=2, p=.5) == pytest.approx(.125)
    assert nb.media(r=2, p=.5) == 2
    assert nb.varianza(r=2, p=.5) == 4


def test_geometrica_hipergeometrica_poisson():
    g = obtener("geometrica")
    assert redondear(g.pmf(5, p=.5)) == .0312
    assert g.media(p=.5) == 2 and g.varianza(p=.5) == 2
    h = obtener("hipergeometrica")
    kwargs = dict(N=6, n=3, K=2)
    assert redondear(h.pmf(2, **kwargs)) == .2
    assert h.cdf(2, **kwargs) == 1
    assert h.cola_inclusiva(2, **kwargs) == pytest.approx(.2)
    assert h.media(**kwargs) == 1 and h.varianza(**kwargs) == pytest.approx(.4)
    pois = obtener("poisson")
    assert redondear(pois.pmf(5, tasa=1)) == .0031
    assert redondear(pois.cdf(5, tasa=1)) == .9994
    assert redondear(pois.cola_inclusiva(5, tasa=1)) == .0037


def test_continuas_originales_correctas():
    assert obtener("uniforme").pdf(2, a=1, b=5) == .25
    assert obtener("uniforme").cdf(3, a=1, b=3) == 1
    assert obtener("uniforme").media(a=1, b=5) == 3
    assert redondear(obtener("normal_estandar").cdf(2)) == .9772
    assert obtener("normal_estandar").ppf(.5) == 0
    assert redondear(obtener("exponencial").cola_inclusiva(4, tasa=1)) == .0183
    assert redondear(1 - obtener("exponencial").ppf(.5, tasa=1)) == .3069
    assert redondear(stats.chi2.sf(1, 1)) == .3173


def test_errores_historicos_no_se_reproducen():
    # UniformeDes utilizaba a+b en lugar de b−a: Java esperaba 1.7321.
    assert redondear(obtener("uniforme").desviacion(a=1, b=5)) == 1.1547
    # JiBiseccion Java devolvía ~0.4553; el cuantil exacto es ~0.4549.
    assert obtener("chi_cuadrado").ppf(.5, gl=1) == pytest.approx(stats.chi2.ppf(.5, 1), rel=1e-10)
    # TstudentVp truncaba nodos a int y sumaba una constante; Java ~0.9836.
    assert obtener("t_student").cdf(1, gl=1) == pytest.approx(.75)
    assert obtener("t_student").ppf(.5, gl=1) == pytest.approx(0)
    # Fisher hacía cuadratura truncada con constantes hardcodeadas.
    assert obtener("f_fisher").cola_inclusiva(1, gl1=1, gl2=5) == pytest.approx(.363217467649)
    assert obtener("f_fisher").cola_inclusiva(1, gl1=5, gl2=5) == pytest.approx(.5)
    assert obtener("f_fisher").ppf(.5, gl1=1, gl2=5) == pytest.approx(.528073768953)
    # n es un mínimo: se redondea hacia arriba, no al entero más cercano.
    assert tamano_proporcion(.3, .1, .5, N=10) == 6
    assert tamano_proporcion(.3, .2, .5) == 3
    assert asignacion_estratos({"A": 5}, 2) == {"A": 2}
