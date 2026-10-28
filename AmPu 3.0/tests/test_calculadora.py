"""Calculadora interna sin evaluación arbitraria ni rutas Windows."""

import math

import pytest

from ampu.core.errores import ParametroInvalidoError
from ampu.core.estadistica.calculadora import calcular, explicar


def test_operaciones_cientificas():
    assert calcular("sqrt(2) + sin(pi/2)") == pytest.approx(math.sqrt(2)+1)
    assert calcular("2^3 + factorial(4)") == 32
    assert calcular("log(100) + ln(e)") == pytest.approx(3)
    assert calcular("-3 * 2 + abs(-5)") == -1


def test_factorial_excesivo_se_rechaza_antes_de_bloquear_la_ui():
    with pytest.raises(ParametroInvalidoError, match="entre 0 y 170"):
        calcular("factorial(10000000)")
    assert calcular("factorial(5)") == 120


def test_traza_didactica_corresponde_al_mismo_motor():
    """La vista nunca inventa transformaciones simbólicas ni recalcula resultados."""
    analisis = explicar("sqrt(2) + sin(pi/2)")
    assert analisis.interpretacion == "sqrt(2) + sin(pi / 2)"
    assert [p.justificacion for p in analisis.pasos] == [
        "Raíz principal (argumento ≥ 0)", "División", "Seno en radianes", "Suma"]
    assert analisis.pasos[-1].resultado == calcular(analisis.entrada)
    assert "radianes" in analisis.supuestos and "sin resolución simbólica" in analisis.supuestos
    assert explicar("pi").pasos[0].justificacion == "Valor de entrada o constante"


def test_sintaxis_invalida_indica_ubicacion():
    with pytest.raises(ParametroInvalidoError, match="columna 3"):
        explicar("2+")
    with pytest.raises(ParametroInvalidoError, match="columna 1"):
        explicar("a.__class__")


@pytest.mark.parametrize("expresion", ["__import__('os').system('whoami')", "(1).__class__", "open('x')", "1/0", "sqrt(-1)", "10^101", "[1,2]", "True + 1", "pi[0]"])
def test_no_ejecuta_codigo_ni_dominios_invalidos(expresion):
    with pytest.raises(ParametroInvalidoError):
        calcular(expresion)
