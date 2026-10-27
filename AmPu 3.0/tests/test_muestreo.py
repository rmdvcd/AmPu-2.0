"""Tamaños, diseños, límites y reproducibilidad de muestreo."""

import numpy as np
import pytest
from scipy import stats

from ampu.core.errores import ParametroInvalidoError
from ampu.core.muestreo import (
    asignacion_estratos, muestra_aleatoria, muestra_conglomerados,
    muestra_estratificada, muestra_sistematica, tamano_diferencia_medias,
    tamano_diferencia_proporciones, tamano_media, tamano_proporcion,
)


def test_tamanos_y_correccion_finita():
    z = stats.norm.ppf(.975)
    n0 = (z/.05)**2*.5*.5
    assert tamano_proporcion(.5, .05) == int(np.ceil(n0))
    assert tamano_proporcion(.5, .05, N=100) == int(np.ceil(100*n0/(99+n0)))
    assert tamano_proporcion(.5, 1e-4, N=10) == 10
    assert tamano_media(12, 2) == int(np.ceil((z*12/2)**2))
    assert tamano_diferencia_medias(3, 4, 2) == int(np.ceil((z/2)**2*25))
    assert tamano_diferencia_proporciones(.4, .5, .2) > 0
    with pytest.raises(ParametroInvalidoError):
        tamano_proporcion(0, .1)
    with pytest.raises(ParametroInvalidoError):
        tamano_media(2, 0)


def test_aleatorio_sistematico_semillas():
    pob = np.arange(40)
    assert np.array_equal(muestra_aleatoria(pob, 8, seed=25), muestra_aleatoria(pob, 8, seed=25))
    assert len(set(muestra_aleatoria(pob, 8, seed=25))) == 8
    assert np.array_equal(muestra_sistematica(pob, 9, seed=25), muestra_sistematica(pob, 9, seed=25))
    sistematica = muestra_sistematica(pob, 9, seed=25)
    assert len(set(sistematica)) == 9
    assert np.all(np.diff(sistematica) >= 4)
    assert len(muestra_aleatoria([1, 2], 8, seed=1, reemplazo=True)) == 8
    with pytest.raises(ParametroInvalidoError):
        muestra_aleatoria(pob, 41)
    with pytest.raises(ParametroInvalidoError):
        muestra_sistematica(pob, 41)


def test_asignacion_cotas_y_seleccion():
    tamanos = {"A": 20, "B": 40, "C": 10}
    prop = asignacion_estratos(tamanos, 17)
    assert sum(prop.values()) == 17
    assert all(0 <= prop[k] <= tamanos[k] for k in tamanos)
    assert prop == asignacion_estratos(tamanos, 17)
    d = {"A": 3, "B": 1, "C": 4}
    neyman = asignacion_estratos(tamanos, 17, "neyman", d)
    optimo = asignacion_estratos(tamanos, 17, "optimo", d, {"A": 1, "B": 9, "C": 1})
    assert neyman["A"] > prop["A"]
    assert optimo["B"] < neyman["B"]
    assert asignacion_estratos({"A": 2, "B": 8}, 10) == {"A": 2, "B": 8}
    estratos = {"A": list(range(20)), "B": list(range(20, 60)), "C": list(range(60, 70))}
    a = muestra_estratificada(estratos, prop, seed=88)
    b = muestra_estratificada(estratos, prop, seed=88)
    assert all(np.array_equal(a[k], b[k]) and len(a[k]) == prop[k] for k in prop)
    with pytest.raises(ParametroInvalidoError):
        asignacion_estratos(tamanos, 5, "neyman")
    with pytest.raises(ParametroInvalidoError):
        asignacion_estratos(tamanos, 71)


def test_conglomerados_una_y_dos_etapas():
    grupos = {str(k): list(range(10*k, 10*k+10)) for k in range(5)}
    a = muestra_conglomerados(grupos, 2, seed=2)
    b = muestra_conglomerados(grupos, 2, seed=2)
    assert all(np.array_equal(a[k], b[k]) for k in a)
    assert len(a) == 2 and all(len(v) == 10 for v in a.values())
    assert all(len(v) == 3 for v in muestra_conglomerados(grupos, 2, seed=2, n_por_grupo=3).values())
    with pytest.raises(ParametroInvalidoError):
        muestra_conglomerados(grupos, 6)
