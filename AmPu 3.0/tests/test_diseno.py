"""Orquestación de todas las modalidades: tablas, semilla, límites y auto n."""

import numpy as np
import pytest

from ampu.core.errores import ParametroInvalidoError
from ampu.core.muestreo.diseno import ejecutar_diseno


@pytest.mark.parametrize("metodo", ["finito", "infinito", "sistematico"])
def test_disenos_simples(metodo):
    a = ejecutar_diseno(metodo, 30, 6, seed=7)
    b = ejecutar_diseno(metodo, 30, 6, seed=7)
    assert a.tablas["Selección"].equals(b.tablas["Selección"])
    assert len(a.tablas["Selección"]) == 6
    assert a.etiquetas == ["Total"]
    assert a.poblacion == [30]
    assert a.seleccion == [6]
    assert a.semilla == 7
    if metodo != "infinito":
        assert a.tablas["Selección"]["Selección"].nunique() == 6


def test_disenos_auto_e_ids():
    a = ejecutar_diseno("finito", 20, 4, seed=8, auto=True, error=.2)
    assert 1 <= len(a.tablas["Selección"]) <= 20
    b = ejecutar_diseno("infinito", 3, 2, seed=8, auto=True, error=.2)
    assert len(b.tablas["Selección"]) > 0
    c = ejecutar_diseno("sistematico", 3, 2, seed=3, poblacion=["a", "b", "c"])
    assert set(c.tablas["Selección"]["Selección"]).issubset({"a", "b", "c"})
    with pytest.raises(ParametroInvalidoError):
        ejecutar_diseno("finito", 5, 2, poblacion=["a"])


@pytest.mark.parametrize("metodo", ["proporcional", "neyman", "optimo"])
def test_disenos_estratificados_y_limites(metodo):
    filas = [("A", 12, 2., 1.), ("B", 20, 1., 3.), ("C", 8, 4., 2.)]
    a = ejecutar_diseno(metodo, 40, 12, seed=99, estratos=filas)
    b = ejecutar_diseno(metodo, 40, 12, seed=99, estratos=filas)
    assert a.tablas["Asignación"].equals(b.tablas["Asignación"])
    assert a.tablas["Selección"].equals(b.tablas["Selección"])
    assert a.tablas["Asignación"]["nh"].sum() == 12
    assert len(a.tablas["Selección"]) == 12
    auto = ejecutar_diseno(metodo, 40, 2, seed=1, auto=True, error=.2, estratos=filas)
    assert auto.tablas["Asignación"]["nh"].sum() >= 1


def test_conglomerados_una_y_dos_etapas():
    filas = [("A", 12, 2., 1.), ("B", 20, 1., 3.), ("C", 8, 4., 2.)]
    a = ejecutar_diseno("conglomerados", 40, 2, seed=10, estratos=filas)
    assert a.tablas["Selección"]["Conglomerado"].nunique() == 2
    b = ejecutar_diseno("conglomerados", 40, 2, seed=10, estratos=filas, n_por_grupo=2)
    assert len(b.tablas["Selección"]) == 4
    assert b.etiquetas == ["A", "B", "C"]
    assert len(b.seleccion) == 3


@pytest.mark.parametrize("args", [
    dict(metodo="desconocido", N=2, n=1),
    dict(metodo="finito", N=-1, n=1),
    dict(metodo="sistematico", N=5, n=9),
    dict(metodo="neyman", N=1, n=2),
    dict(metodo="conglomerados", N=1, n=1, estratos=[("A", 0, 1., 1.)]),
    dict(metodo="proporcional", N=1, n=2, estratos=[("A", 3, 1., 1.), ("A", 3, 1., 1.)]),
])
def test_disenos_rechazan_entradas(args):
    with pytest.raises(ParametroInvalidoError):
        ejecutar_diseno(**args)
