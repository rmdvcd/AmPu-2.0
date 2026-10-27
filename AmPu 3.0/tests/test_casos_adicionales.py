"""Rutas de error y funciones ampliadas para el objetivo de cobertura 85 %."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.distribuciones import catalogo, obtener
from ampu.core.distribuciones.tabla import analizar
from ampu.core.errores import CalculoNoConvergenteError, ParametroInvalidoError, SoporteError
from ampu.core.estadistica import inferencia as i, probabilidad as p, regresion as r
from ampu.core.simulacion.montecarlo import (
    ajustar_distribucion, curva_ajustada, familias_ajustables, integral_cuadrado,
    integrar, puntos_pi, qq_plot,
)


def test_multivariadas_escalares_matrices_errores():
    assert len(catalogo("continuas")) == 18
    assert len(catalogo()) == 26
    with pytest.raises(KeyError):
        catalogo("inexistente")
    with pytest.raises(KeyError):
        obtener("inexistente")
    multi = obtener("multinomial")
    params = dict(n=5, p=[.2, .3, .5])
    matriz = [[1, 2, 2], [3, 1, 1], [0, 0, 5], [1.5, 1.5, 2]]
    np.testing.assert_allclose(multi.pmf(matriz, **params), [stats.multinomial.pmf(fila, 5, params["p"]) for fila in matriz[:3]] + [0])
    assert multi.cdf(matriz, **params).shape == (4, 3)
    with pytest.raises(SoporteError):
        multi.pdf([1, 2, 2], **params)
    with pytest.raises(ParametroInvalidoError):
        multi.ppf([.2, .3], **params)
    normal = obtener("normal_bivariada")
    xs = [[0, 0], [1, 1]]
    assert normal.pdf(xs).shape == (2,)
    assert normal.cdf(xs).shape == (2,)
    assert normal.ppf([.25, .75]).shape == (2,)
    with pytest.raises(SoporteError):
        normal.pdf([1,2,3])
    with pytest.raises(SoporteError):
        normal.pmf([0,0])
    with pytest.raises(ParametroInvalidoError):
        normal.ppf([.25, .5, .75])
    diri = obtener("dirichlet")
    assert diri.pdf([[.2,.3,.5], [.1,.3,.6], [.1,.1,.1]]).shape == (3,)
    assert diri.pdf([0, 0, 0]) == 0
    assert diri.cdf([[.2,.3,.5], [.1,.3,.6]]).shape == (2,3)
    assert diri.ppf([.1,.5,.9]).shape == (3,)
    with pytest.raises(SoporteError):
        diri.pdf([.5,.5])
    with pytest.raises(SoporteError):
        diri.pmf([.2,.3,.5])
    with pytest.raises(ParametroInvalidoError):
        diri.ppf([.1,.5])


def test_grafico_marginal_casos_limite_y_soporte():
    for clave, x in (("dirichlet", [.2,.3,.5]), ("normal_bivariada", [0,0])):
        res = analizar(clave, {}, x)
        assert res.marginal
        assert res.tabla.shape[0] == 1
    res = analizar("poisson", {"tasa": 0}, 0)
    assert res.respuesta["probabilidad_o_densidad"] == 1
    assert len(res.x) < 401
    res = analizar("cauchy", {}, 0)
    assert np.isnan(res.respuesta["media"])
    assert len(res.x) == 161
    with pytest.raises(ParametroInvalidoError):
        analizar("normal", {}, [1, 2])
    with pytest.raises(ParametroInvalidoError):
        analizar("normal", {}, float("inf"))
    with pytest.raises(ParametroInvalidoError):
        analizar("normal", {}, 1, puntos=5)


def test_inferencia_ramas_alternativas_y_datos_invalidos():
    a, b = [1,2,3,5,8], [2,4,6,7,9]
    assert i.z_una_muestra(a, 2, 2, alternativa="less").p_valor == pytest.approx(stats.norm.cdf((np.mean(a)-2)/(2/np.sqrt(5))))
    assert i.z_una_muestra(a, 2, 2, alternativa="greater").p_valor > 0
    assert i.t_una_muestra(a, 2, alternativa="less").p_valor == pytest.approx(stats.ttest_1samp(a, 2, alternative="less").pvalue)
    assert i.t_dos_muestras(a, b, alternativa="greater").p_valor == pytest.approx(stats.ttest_ind(a,b,equal_var=False,alternative="greater").pvalue)
    assert i.chi_bondad([11,22,30,37], [10,20,30,40], parametros_estimados=1).gl == 2
    assert i.chi_bondad([1,1], [1,1]).detalles["advertencia"]
    assert i.chi_independencia([[2,3],[3,2]]).detalles["advertencia"]
    assert "No se rechaza" in i.t_una_muestra(a, np.mean(a)).conclusion
    assert i.intervalo_media(a, sigma=2)[0] < np.mean(a)
    for llamada in (
        lambda: i.t_una_muestra(a, 2, alternativa="invalida"),
        lambda: i.intervalo_media(a, confianza=1),
        lambda: i.intervalo_media(a, sigma=-2),
        lambda: i.proporcion_una(-1, 10, .5),
        lambda: i.proporcion_una(2, 10, 0),
        lambda: i.proporcion_dos(0, 10, 0, 10),
        lambda: i.chi_bondad([1, 2], [2, 2]),
        lambda: i.chi_bondad([1, 1], [1, 1], parametros_estimados=1),
        lambda: i.anova([a]),
        lambda: i.correlacion(a, b[:-1]),
        lambda: i.correlacion(a, b, metodo="inventado"),
        lambda: i.wilcoxon(a, a),
    ):
        with pytest.raises((ParametroInvalidoError, CalculoNoConvergenteError)):
            llamada()
    with pytest.raises(CalculoNoConvergenteError):
        i.kruskal([[1,1], [1,1]])
    assert i.proporcion_dos(30, 100, 35, 100).intervalo is not None


def test_regresion_y_probabilidad_ramas():
    with pytest.raises(ParametroInvalidoError):
        p.independientes(.1, .2, .5)
    with pytest.raises(ParametroInvalidoError):
        p.probabilidad_total([.2,.3], [.2,.3])
    with pytest.raises(ParametroInvalidoError):
        p.bayes(0, [.4,.6], [0,0])
    with pytest.raises(ParametroInvalidoError):
        p.esperanza([0,1], [.6,.6])
    x = np.arange(1., 12.)
    y = 1 + 2*x + np.sin(x)
    mod = r.lineal_simple(x, y)
    with pytest.raises(ParametroInvalidoError):
        mod.predecir([[1,2]])
    with pytest.raises(ParametroInvalidoError):
        r.lineal_multiple([[1,2],[3,4]], [1,2])
    with pytest.raises(ParametroInvalidoError):
        r.lineal_multiple(np.column_stack([x,x**2]), y, nombres=["x"])
    with pytest.raises(ParametroInvalidoError):
        r.lineal_simple(x, y[:-1])
    with pytest.raises(CalculoNoConvergenteError):
        r.lineal_simple([1,1,1], [1,2,3])
    with pytest.raises(CalculoNoConvergenteError):
        r.lineal_multiple(np.column_stack([x,x**2]), np.ones(11))


@pytest.mark.parametrize("clave,dist", [
    ("exponencial", stats.expon(scale=2)), ("gamma", stats.gamma(2.5,scale=2)),
    ("weibull", stats.weibull_min(1.5,scale=2)), ("lognormal", stats.lognorm(.5)),
    ("beta", stats.beta(2,5)),
])
def test_ajuste_extra(clave, dist):
    datos = dist.rvs(size=55, random_state=np.random.default_rng(4))
    fit = ajustar_distribucion(datos, clave, seed=2)
    grid, pdf = curva_ajustada(fit, datos)
    assert grid.shape == pdf.shape == (220,)
    assert np.all(np.isfinite(pdf))
    assert clave in familias_ajustables()


def test_simulacion_errores_y_espacios():
    est, exacto = integral_cuadrado(1000, seed=15)
    assert exacto == pytest.approx(1/3)
    assert est.valor == pytest.approx(exacto, abs=.06)
    assert np.array_equal(puntos_pi(10, seed=1)[0], puntos_pi(10, seed=1)[0])
    with pytest.raises(CalculoNoConvergenteError):
        integrar(lambda xx: np.ones(2), 0, 1, n=10)
    with pytest.raises(ParametroInvalidoError):
        ajustar_distribucion([-1, 1, 2, 3, 4], "exponencial")
    with pytest.raises(ParametroInvalidoError):
        ajustar_distribucion([0, .2, .3, .5, .7], "beta")
    with pytest.raises(ParametroInvalidoError):
        qq_plot([1,2,3], "dirichlet", {})
