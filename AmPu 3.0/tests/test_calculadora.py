"""Calculadora interna sin evaluación arbitraria ni rutas Windows."""

import math

import pytest

from ampu.core.errores import ParametroInvalidoError
from ampu.core.estadistica.calculadora import calcular


def test_operaciones_cientificas():
    assert calcular("sqrt(2) + sin(pi/2)") == pytest.approx(math.sqrt(2)+1)
    assert calcular("2^3 + factorial(4)") == 32
    assert calcular("log(100) + ln(e)") == pytest.approx(3)
    assert calcular("-3 * 2 + abs(-5)") == -1


@pytest.mark.parametrize("expresion", ["__import__('os').system('whoami')", "(1).__class__", "open('x')", "1/0", "sqrt(-1)", "10^101", "[1,2]", "True + 1", "pi[0]"])
def test_no_ejecuta_codigo_ni_dominios_invalidos(expresion):
    with pytest.raises(ParametroInvalidoError):
        calcular(expresion)
