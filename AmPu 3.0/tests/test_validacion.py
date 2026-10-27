"""Validadores centrales y errores legibles."""

import numpy as np
import pytest

from ampu.core.errores import ParametroInvalidoError, SoporteError
from ampu.core.validacion import (
    Parametro, exigir, validar_evento, validar_muestra, validar_nivel,
    validar_parametros, validar_probabilidades, validar_semilla, validar_tamano,
)


def test_metadatos_escalares_y_vectores():
    a = Parametro("p", "real", 0, 1, "Probabilidad", .5)
    n = Parametro("n", "entero", 0, None, "Ensayos", 10)
    v = Parametro("p", "vector_real", 0, 1, "Vector", (.2,.8))
    assert validar_parametros([a, n], {}) == {"p": .5, "n": 10}
    assert v.validar([0,1]) == (0., 1.)
    with pytest.raises(ParametroInvalidoError):
        n.validar(1.5)
    with pytest.raises(ParametroInvalidoError):
        a.validar(True)
    with pytest.raises(ParametroInvalidoError):
        a.validar(float("nan"))
    with pytest.raises(ParametroInvalidoError):
        v.validar([.2])
    with pytest.raises(ParametroInvalidoError):
        validar_parametros([n], {"desconocido": 2})
    with pytest.raises(ParametroInvalidoError):
        exigir(False, "Incoherente")


def test_restricciones_de_q_seed_tamano_y_muestras():
    assert validar_probabilidades([0, 1]).tolist() == [0,1]
    assert validar_semilla(0) == 0
    assert validar_semilla(None) is None
    assert validar_tamano(1_000_000) == 1_000_000
    assert validar_nivel(.95) == .95
    assert validar_evento(float("inf")) == float("inf")
    assert np.array_equal(validar_muestra([1,2]), [1,2])
    for f, bad in [(validar_probabilidades, -1), (validar_probabilidades, float("nan")),
                   (validar_semilla, -1), (validar_semilla, True), (validar_tamano, 0),
                   (validar_nivel, 1), (validar_muestra, [float("inf"),1]),
                   (validar_evento, [float("nan")])]:
        with pytest.raises(ParametroInvalidoError):
            f(bad)
