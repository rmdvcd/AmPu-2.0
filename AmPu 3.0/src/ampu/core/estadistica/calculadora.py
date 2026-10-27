"""Evaluación de expresiones científicas seguras, sin eval ni procesos SO."""

import ast
import math
import operator

from ampu.core.errores import ParametroInvalidoError

_BINARIAS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
             ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
_FUNCIONES = {"sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log10,
              "ln": math.log, "sqrt": math.sqrt, "exp": math.exp, "abs": abs,
              "factorial": math.factorial}
_CONSTANTES = {"pi": math.pi, "e": math.e}


def calcular(expresion: str) -> float:
    """Interpreta exclusivamente números, operaciones aritméticas y funciones.

    Args:
        expresion: Por ejemplo ``sqrt(2) + sin(pi/2)``. Las funciones
            trigonométricas usan radianes. ``^`` es sinónimo de potencia.

    Raises:
        ParametroInvalidoError: Sintaxis, dominio, desbordamiento o nodo no permitido.
    """
    if not isinstance(expresion, str) or not 0 < len(expresion) <= 200:
        raise ParametroInvalidoError("Introduce una expresión de hasta 200 caracteres.")
    try:
        raiz = ast.parse(expresion.replace("^", "**"), mode="eval").body

        def visitar(nodo, profundidad=0):
            """Desciende por un AST acotado; nunca evalúa código arbitrario."""
            if profundidad > 25:
                raise ParametroInvalidoError("Expresión demasiado profunda.")
            if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
                return nodo.value
            if isinstance(nodo, ast.Name) and nodo.id in _CONSTANTES:
                return _CONSTANTES[nodo.id]
            if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.UAdd, ast.USub)):
                valor = visitar(nodo.operand, profundidad+1)
                return valor if isinstance(nodo.op, ast.UAdd) else -valor
            if isinstance(nodo, ast.BinOp) and type(nodo.op) in _BINARIAS:
                izq, der = visitar(nodo.left, profundidad+1), visitar(nodo.right, profundidad+1)
                if isinstance(nodo.op, ast.Pow) and abs(der) > 100:
                    raise ParametroInvalidoError("El exponente máximo es 100.")
                return _BINARIAS[type(nodo.op)](izq, der)
            if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                    and nodo.func.id in _FUNCIONES and len(nodo.args) == 1 and not nodo.keywords):
                return _FUNCIONES[nodo.func.id](visitar(nodo.args[0], profundidad+1))
            raise ParametroInvalidoError("Solo se permiten números, + − × ÷ ^, paréntesis y funciones conocidas.")

        resultado = float(visitar(raiz))
        if not math.isfinite(resultado):
            raise ParametroInvalidoError("El resultado no es finito.")
        return resultado
    except ParametroInvalidoError:
        raise
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError, TypeError) as exc:
        raise ParametroInvalidoError(f"Expresión no válida: {exc}") from exc
