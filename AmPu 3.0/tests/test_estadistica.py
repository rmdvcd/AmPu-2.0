"""Descriptiva, inferencia, combinatoria, probabilidad y regresión."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.errores import CalculoNoConvergenteError, ParametroInvalidoError
from ampu.core.estadistica import combinatoria as c, descriptiva as d, inferencia as i, probabilidad as p, regresion as r


def test_descriptiva_y_frecuencias():
    datos = [1, 2, 2, 4, 5]
    a = d.resumir(datos)
    assert a.n == 5 and a.media == pytest.approx(2.8)
    assert a.mediana == 2 and a.modas == (2.,)
    assert a.q1 == 2 and a.q3 == 4
    assert a.varianza == pytest.approx(np.var(datos, ddof=1))
    assert a.coeficiente_variacion == pytest.approx(a.desviacion / 2.8)
    assert d.percentil(datos, .5) == 2
    tabla = d.frecuencias(datos)
    assert tabla["Frecuencia"].sum() == 5
    assert tabla["Relativa acumulada"].iloc[-1] == 1
    assert d.resumir([-1, 1]).coeficiente_variacion is None


def test_combinatoria_y_probabilidad():
    assert c.factorial(0) == 1 and c.factorial(5) == 120
    assert c.combinaciones(10, 3) == 120
    assert c.permutaciones(5, 3) == 60
    assert c.permutaciones_repetidas([2, 2, 1]) == 30
    with pytest.raises(ParametroInvalidoError):
        c.combinaciones(2, 3)
    assert p.condicional(.2, .4) == pytest.approx(.5)
    assert p.independientes(.5, .5, .25)
    assert p.probabilidad_total([.4, .6], [.5, .1]) == pytest.approx(.26)
    assert p.bayes(0, [.4, .6], [.5, .1]) == pytest.approx(.2/.26)
    assert p.esperanza([0, 1], [.6, .4]) == pytest.approx(.4)
    assert p.varianza([0, 1], [.6, .4]) == pytest.approx(.24)
    assert p.generadora_momentos(0, [0, 1], [.6, .4]) == 1
    with pytest.raises(ParametroInvalidoError):
        p.condicional(.3, .2)
    with pytest.raises(CalculoNoConvergenteError):
        p.generadora_momentos(1000, [0, 1], [.6, .4])


def test_intervalos_y_pruebas_parametricas():
    x = np.array([7., 8, 9, 10, 11, 12, 13])
    y = np.array([4., 5, 6, 7, 8, 9, 10])
    t1 = i.t_una_muestra(x, 8)
    ref = stats.ttest_1samp(x, 8)
    assert t1.estadistico == pytest.approx(ref.statistic, rel=1e-10)
    assert t1.p_valor == pytest.approx(ref.pvalue, rel=1e-10)
    assert t1.intervalo[0] < x.mean() < t1.intervalo[1]
    assert "rechaza" in t1.conclusion
    z1 = i.z_una_muestra(x, 8, 2)
    assert z1.p_valor == pytest.approx(2*stats.norm.sf(abs((x.mean()-8)/(2/np.sqrt(len(x))))))
    t2 = i.t_dos_muestras(x, y)
    assert t2.p_valor == pytest.approx(stats.ttest_ind(x, y, equal_var=False).pvalue, rel=1e-10)
    assert i.z_dos_muestras(x, y, 2, 3).intervalo[0] < 3 < i.z_dos_muestras(x, y, 2, 3).intervalo[1]
    assert i.intervalo_media(x)[0] < np.mean(x) < i.intervalo_media(x)[1]
    with pytest.raises(CalculoNoConvergenteError):
        i.t_una_muestra([1, 1, 1], 2)


def test_proporciones_chi_anova_y_correlacion():
    p1 = i.proporcion_una(50, 100, .3)
    assert p1.p_valor == pytest.approx(2*stats.norm.sf(abs((.5-.3)/np.sqrt(.3*.7/100))))
    assert i.intervalo_proporcion(0, 10)[0] == 0
    assert i.intervalo_proporcion(10, 10)[1] == 1
    assert i.proporcion_dos(40, 100, 20, 100).p_valor < .05
    obs = [12, 15, 23]
    esp = [15, 15, 20]
    assert i.chi_bondad(obs, esp).p_valor == pytest.approx(stats.chisquare(obs, esp).pvalue, rel=1e-10)
    t = [[18, 12], [10, 20]]
    assert i.chi_independencia(t).p_valor == pytest.approx(stats.chi2_contingency(t, correction=False).pvalue, rel=1e-10)
    grupos = [[2, 3, 4, 5], [9, 10, 11, 12], [5, 6, 7, 8]]
    assert i.anova(grupos).p_valor == pytest.approx(stats.f_oneway(*grupos).pvalue, rel=1e-10)
    assert i.correlacion([1,2,3,4,5], [2,4,5,8,9]).p_valor == pytest.approx(stats.pearsonr([1,2,3,4,5], [2,4,5,8,9]).pvalue)
    assert i.correlacion([1,2,3,4,5], [5,3,4,1,2], "spearman").metodo.endswith("Spearman")
    with pytest.raises(ParametroInvalidoError):
        i.chi_independencia([[0,0], [1,2]])


def test_no_parametricas_y_errores():
    a, b = [1, 2, 3, 4], [4, 5, 6, 7]
    assert i.mann_whitney(a, b).p_valor == pytest.approx(stats.mannwhitneyu(a, b).pvalue)
    assert i.wilcoxon(a, b).p_valor == pytest.approx(stats.wilcoxon(a, b).pvalue)
    assert i.kruskal([a, b, [2, 3, 4, 5]]).p_valor == pytest.approx(stats.kruskal(a, b, [2,3,4,5]).pvalue)
    assert i.error_absoluto(12, 10) == 2 and i.error_relativo(12, 10) == .2
    with pytest.raises(ParametroInvalidoError):
        i.error_relativo(1, 0)


def test_regresiones():
    x = np.arange(1., 12.)
    y = 2 + 3*x + np.array([.1,-.1,.2,-.2,0,.1,-.1,.2,-.2,0,0])
    modelo = r.lineal_simple(x, y)
    ref = stats.linregress(x, y)
    assert modelo.coeficientes[0] == pytest.approx(ref.intercept, rel=1e-10)
    assert modelo.coeficientes[1] == pytest.approx(ref.slope, rel=1e-10)
    assert modelo.r_cuadrado == pytest.approx(ref.rvalue**2, rel=1e-10)
    assert modelo.predecir([[3]])[0] == pytest.approx(modelo.coeficientes[0] + 3*modelo.coeficientes[1])
    X = np.column_stack([x, x**2])
    m = r.lineal_multiple(X, y)
    assert len(m.coeficientes) == 3
    assert m.r_cuadrado > .99
    with pytest.raises(CalculoNoConvergenteError):
        r.lineal_multiple(np.column_stack([x, x]), y)
