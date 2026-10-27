"""PDF/CDF/PPF y momentos de 16 familias continuas univariadas."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.distribuciones import obtener
from ampu.core.distribuciones.tabla import analizar
from ampu.core.errores import ParametroInvalidoError, SoporteError


@pytest.mark.parametrize("clave,params,ref,x", [
    ("uniforme", {"a": 1, "b": 5}, stats.uniform(1, 4), [0, 1, 2.5, 5, 6]),
    ("normal_estandar", {}, stats.norm(), [-3, 0, 1, 2]),
    ("normal", {"mu": 4, "sigma": 2}, stats.norm(4, 2), [-2, 3, 4, 9]),
    ("chi_cuadrado", {"gl": 3}, stats.chi2(3), [-1, 0.5, 2, 4]),
    ("exponencial", {"tasa": 2}, stats.expon(scale=0.5), [-1, 0, 1, 3]),
    ("t_student", {"gl": 5}, stats.t(5), [-4, 0, 1, 4]),
    ("f_fisher", {"gl1": 6, "gl2": 9}, stats.f(6, 9), [-1, 0.5, 1, 4]),
    ("gamma", {"forma": 2.5, "escala": 3}, stats.gamma(2.5, scale=3), [-1, 0.2, 2, 9]),
    ("erlang", {"k": 3, "tasa": 2}, stats.erlang(3, scale=.5), [-1, 0.4, 2, 5]),
    ("beta", {"alpha": 2, "beta": 5}, stats.beta(2, 5), [-1, 0.1, 0.5, 1.1]),
    ("lognormal", {"mu": 0.5, "sigma": 0.8}, stats.lognorm(.8, scale=np.exp(.5)), [-1, 0.1, 1, 3]),
    ("weibull", {"forma": 1.5, "escala": 2}, stats.weibull_min(1.5, scale=2), [-1, 0.3, 2, 7]),
    ("cauchy", {"centro": 0, "escala": 1}, stats.cauchy(), [-3, 0, 1, 4]),
    ("logistica", {"mu": 0, "escala": 2}, stats.logistic(scale=2), [-3, 0, 1, 4]),
    ("triangular", {"a": 0, "b": 4, "c": 1}, stats.triang(.25, scale=4), [-1, 0, 1, 3, 5]),
    ("pareto", {"alpha": 3, "xmin": 2}, stats.pareto(3, scale=2), [-1, 1, 2.5, 6]),
])
def test_scipy_univariantes(clave, params, ref, x):
    d = obtener(clave)
    np.testing.assert_allclose(d.pdf(x, **params), ref.pdf(x), rtol=1e-10, atol=1e-14)
    np.testing.assert_allclose(d.cdf(x, **params), ref.cdf(x), rtol=1e-10, atol=1e-14)
    np.testing.assert_allclose(d.ppf([.05, .5, .9], **params), ref.ppf([.05, .5, .9]), rtol=1e-10, atol=1e-14)
    np.testing.assert_allclose(d.media(**params), ref.mean(), rtol=1e-10, equal_nan=True)
    np.testing.assert_allclose(d.varianza(**params), ref.var(), rtol=1e-10, equal_nan=True)
    np.testing.assert_allclose(d.desviacion(**params), np.sqrt(ref.var()), rtol=1e-10, equal_nan=True)
    assert np.array_equal(d.rvs(8, seed=19, **params), d.rvs(8, seed=19, **params))
    assert d.soporte(**params) == ref.support()
    with pytest.raises(SoporteError):
        d.pmf(1, **params)


def test_casos_limite_y_coherencia():
    assert obtener("normal").ppf(0) == -np.inf
    assert obtener("normal").ppf(1) == np.inf
    assert obtener("uniforme").pdf(0, a=1, b=5) == 0
    assert obtener("uniforme").varianza(a=1, b=5) == pytest.approx(4/3)
    assert np.isnan(obtener("cauchy").media())
    assert np.isinf(obtener("pareto").media(alpha=1, xmin=1))
    assert np.isinf(obtener("pareto").varianza(alpha=1.5, xmin=1))
    for clave, params in [("uniforme", {"a": 5, "b": 5}), ("triangular", {"a": 0, "b": 1, "c": 2}),
                          ("normal", {"sigma": 0}), ("f_fisher", {"gl2": -1})]:
        with pytest.raises(ParametroInvalidoError):
            obtener(clave).cdf(1, **params)
    res = analizar("normal", {"mu": 1, "sigma": 2}, 2)
    assert len(res.x) == 161
    assert res.respuesta["acumulada"] == pytest.approx(stats.norm(1, 2).cdf(2))
