"""Contraste exhaustivo de distribuciones discretas contra SciPy."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.distribuciones import obtener
from ampu.core.distribuciones.tabla import analizar
from ampu.core.errores import ParametroInvalidoError, SoporteError


@pytest.mark.parametrize("clave,parametros,referencia,x", [
    ("bernoulli", {"p": 0.3}, stats.bernoulli(0.3), [0, 1, 2]),
    ("binomial", {"n": 10, "p": 0.5}, stats.binom(10, 0.5), [-1, 0, 5, 10, 11]),
    ("binomial_negativa", {"r": 3, "p": 0.6}, stats.nbinom(3, 0.6), [-1, 0, 2, 10]),
    ("geometrica", {"p": 0.4}, stats.geom(0.4), [0, 1, 2, 10]),
    ("hipergeometrica", {"N": 20, "K": 7, "n": 6}, stats.hypergeom(20, 7, 6), [-1, 0, 3, 6, 7]),
    ("poisson", {"tasa": 2.5}, stats.poisson(2.5), [-1, 0, 2, 9]),
    ("uniforme_discreta", {"a": -2, "b": 2}, stats.randint(-2, 3), [-3, -2, 0, 2, 3]),
])
def test_contra_scipy(clave, parametros, referencia, x):
    modelo = obtener(clave)
    np.testing.assert_allclose(modelo.pmf(x, **parametros), referencia.pmf(x), rtol=1e-10, atol=1e-14)
    np.testing.assert_allclose(modelo.cdf(x, **parametros), referencia.cdf(x), rtol=1e-10, atol=1e-14)
    np.testing.assert_allclose(modelo.ppf([0.1, 0.5, 0.9], **parametros), referencia.ppf([0.1, 0.5, 0.9]), rtol=1e-10)
    assert modelo.media(**parametros) == pytest.approx(referencia.mean(), rel=1e-10)
    assert modelo.varianza(**parametros) == pytest.approx(referencia.var(), rel=1e-10)
    np.testing.assert_allclose(modelo.cola_inclusiva(x, **parametros), referencia.sf(np.ceil(x)-1), rtol=1e-10, atol=1e-14)
    assert np.array_equal(modelo.rvs(12, seed=7, **parametros), modelo.rvs(12, seed=7, **parametros))
    assert modelo.soporte(**parametros) == referencia.support()
    with pytest.raises(SoporteError):
        modelo.pdf(2, **parametros)


@pytest.mark.parametrize("p", [0, 1])
def test_extremos_binomial_bernoulli(p):
    for clave, kwargs in (("binomial", {"n": 8, "p": p}), ("bernoulli", {"p": p})):
        modelo = obtener(clave)
        assert modelo.pmf(8 if clave == "binomial" else 1, **kwargs) == pytest.approx(p)
        assert modelo.cdf(-1, **kwargs) == 0
        assert modelo.cdf(100, **kwargs) == 1
        assert modelo.ppf(1, **kwargs) <= 8


def test_parametros_invalidos_y_salida_tabla():
    modelo = obtener("hipergeometrica")
    with pytest.raises(ParametroInvalidoError):
        modelo.pmf(1, N=10, K=11, n=4)
    with pytest.raises(ParametroInvalidoError):
        obtener("geometrica").pmf(2, p=0)
    with pytest.raises(ParametroInvalidoError):
        obtener("binomial").ppf(1.1)
    with pytest.raises(ParametroInvalidoError):
        obtener("poisson").pmf(0, tasa=1, otros=3)
    salida = analizar("binomial", {"n": 10, "p": 0.5}, 5)
    assert {"x", "n", "p", "P(X=x)", "P(X≤x)", "P(X≥x)", "Media", "Varianza"}.issubset(salida.tabla.columns)
    assert salida.respuesta["probabilidad_o_densidad"] == pytest.approx(0.24609375)
    assert salida.tabla["P(X=x)"].sum() == pytest.approx(1, abs=1e-12)
