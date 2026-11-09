"""Modelos multivariados: PMF/PDF conjuntas y cuantiles marginales."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.distribuciones import DISTRIBUCIONES, catalogo, obtener
from ampu.core.distribuciones.tabla import analizar
from ampu.core.errores import ParametroInvalidoError, SoporteError


def test_registro_y_metadatos():
    assert len(DISTRIBUCIONES) == len(set(DISTRIBUCIONES)) == 26
    assert len(catalogo("multivariadas")) == 3
    assert len(catalogo("discretas")) == 8
    for clave, modelo in DISTRIBUCIONES.items():
        assert modelo.clave == clave
        assert all(p.default is not None and p.descripcion for p in modelo.parametros)
        assert isinstance(modelo.rvs(2, seed=42), np.ndarray)


def test_multinomial_conteos_y_marginales():
    d = obtener("multinomial")
    params = {"n": 5, "p": (0.2, 0.3, 0.5)}
    x = [1, 2, 2]
    assert d.pmf(x, **params) == pytest.approx(stats.multinomial.pmf(x, 5, params["p"]), rel=1e-10)
    assert d.pmf([1, 1, 1], **params) == 0
    assert d.pmf([-1, 3, 3], **params) == 0
    assert d.pmf([1.5, 1.5, 2], **params) == 0
    np.testing.assert_allclose(d.cdf(x, **params), stats.binom.cdf(x, 5, params["p"]), rtol=1e-10)
    np.testing.assert_allclose(d.ppf(.8, **params), stats.binom.ppf(.8, 5, params["p"]), rtol=1e-10)
    np.testing.assert_allclose(d.media(**params), stats.multinomial.mean(5, params["p"]), rtol=1e-10)
    np.testing.assert_allclose(d.varianza(**params), np.diag(stats.multinomial.cov(5, params["p"])), rtol=1e-10)
    assert np.array_equal(d.rvs(5, seed=22, **params), d.rvs(5, seed=22, **params))
    assert np.all(d.rvs(5, seed=22, **params).sum(axis=1) == 5)
    with pytest.raises(ParametroInvalidoError):
        d.pmf(x, n=5, p=[0.2, 0.2, 0.2])
    with pytest.raises(SoporteError):
        d.pmf([1, 2], **params)
    assert analizar("multinomial", params, x).marginal


def test_normal_bivariada():
    d = obtener("normal_bivariada")
    params = {"mu_x": 1, "mu_y": -1, "sigma_x": 2, "sigma_y": 3, "rho": .2}
    ref = stats.multivariate_normal([1, -1], [[4, 1.2], [1.2, 9]])
    x = [0.3, -0.4]
    assert d.pdf(x, **params) == pytest.approx(ref.pdf(x), rel=1e-10)
    assert d.cdf(x, **params) == pytest.approx(ref.cdf(x), rel=1e-10)
    np.testing.assert_allclose(d.ppf(.5, **params), [1, -1], rtol=1e-10)
    assert d.rvs(2, seed=1, **params).shape == (2, 2)
    with pytest.raises(ParametroInvalidoError):
        d.pdf(x, **(params | {"rho": 1}))


def test_dirichlet():
    d = obtener("dirichlet")
    alpha = {"alpha": [2, 3, 4]}
    x = [0.2, 0.3, 0.5]
    assert d.pdf(x, **alpha) == pytest.approx(stats.dirichlet.pdf(x, alpha["alpha"]), rel=1e-10)
    assert d.pdf([0.2, 0.3, 0.3], **alpha) == 0
    np.testing.assert_allclose(d.cdf(x, **alpha), stats.beta.cdf(x, [2,3,4], [7,6,5]), rtol=1e-10)
    np.testing.assert_allclose(d.varianza(**alpha), stats.dirichlet.var(alpha["alpha"]), rtol=1e-10)
    assert d.rvs(5, seed=9, **alpha).sum(axis=1) == pytest.approx(np.ones(5))
    with pytest.raises(ParametroInvalidoError):
        d.pdf(x, alpha=[1, 0, 2])
