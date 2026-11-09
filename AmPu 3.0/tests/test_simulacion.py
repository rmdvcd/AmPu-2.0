"""Monte Carlo, muestras y QQ-plot con semillas locales."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.errores import ParametroInvalidoError
from ampu.core.simulacion import ajustar_distribucion, generar_muestra, integrar, qq_plot, simular_pi


def test_simulacion_y_muestras():
    a = simular_pi(10_000, seed=123)
    assert a == simular_pi(10_000, seed=123)
    assert a.valor == pytest.approx(np.pi, abs=.1)
    assert a.intervalo[0] < a.valor < a.intervalo[1]
    cuadrado = integrar(lambda x: x**2, 0, 1, 15_000, seed=123)
    assert cuadrado.valor == pytest.approx(1/3, abs=.015)
    assert np.array_equal(generar_muestra("normal", {}, 5, seed=12), generar_muestra("normal", {}, 5, seed=12))
    with pytest.raises(ParametroInvalidoError):
        integrar(lambda x: x, 1, 0)


def test_qq_plot_y_fit():
    rng = np.random.default_rng(4)
    datos = rng.normal(2, .7, 45)
    teoricos, observados = qq_plot(datos, "normal", {"mu": 2, "sigma": .7})
    np.testing.assert_allclose(teoricos, stats.norm.ppf((np.arange(1,46)-.5)/45, 2, .7), rtol=1e-10)
    assert np.array_equal(observados, np.sort(datos))
    ajuste = ajustar_distribucion(datos, "normal", seed=1)
    assert ajuste.parametros["loc"] == pytest.approx(np.mean(datos), abs=.03)
    assert ajuste.parametros["scale"] == pytest.approx(np.std(datos), abs=.03)
    assert ajuste.aic > 0 and 0 <= ajuste.p_ks <= 1
    with pytest.raises(ParametroInvalidoError):
        ajustar_distribucion(datos, "f_fisher")
