"""Lectura y validación de entradas textuales, independiente del toolkit gráfico."""

from __future__ import annotations

import re

import numpy as np

from ampu.core.errores import ParametroInvalidoError


def numeros(texto: str, minimo: int = 2) -> np.ndarray:
    """Lee números separados por coma, espacio, punto y coma o saltos de línea."""
    try:
        valores = [float(fragmento) for fragmento in re.split(r"[,;\s]+", texto.strip()) if fragmento]
        salida = np.asarray(valores, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ParametroInvalidoError("Usa números separados por comas o espacios y punto decimal.") from exc
    if len(salida) < minimo or not np.all(np.isfinite(salida)):
        raise ParametroInvalidoError(f"Introduce al menos {minimo} valores numéricos finitos.")
    return salida


def matriz(texto: str) -> np.ndarray:
    """Lee una matriz rectangular: una fila por línea o punto y coma."""
    filas = [fila for fila in re.split(r"[;\n]+", texto.strip()) if fila.strip()]
    try:
        datos = np.asarray([numeros(fila, minimo=1) for fila in filas], dtype=float)
    except (ValueError, TypeError) as exc:
        raise ParametroInvalidoError("Cada fila debe tener el mismo número de columnas numéricas.") from exc
    if datos.ndim != 2 or not np.all(np.isfinite(datos)):
        raise ParametroInvalidoError("La matriz debe ser rectangular y finita.")
    return datos


def grupos(texto: str) -> list[np.ndarray]:
    """Devuelve un grupo numérico por línea o punto y coma."""
    return [numeros(fila) for fila in re.split(r"[;\n]+", texto.strip()) if fila.strip()]


def filas_estratos(texto: str) -> list[tuple[str, int, float, float]]:
    """Lee ``nombre, Nh, desviación, coste`` por fila."""
    salida: list[tuple[str, int, float, float]] = []
    for linea in texto.strip().splitlines():
        if not linea.strip():
            continue
        partes = [fragmento.strip() for fragmento in linea.split(",")]
        if len(partes) not in (2, 3, 4):
            raise ParametroInvalidoError("Cada fila debe ser: nombre, tamaño, desviación, coste.")
        try:
            nombre, tamaño = partes[:2]
            salida.append((nombre, int(tamaño), float(partes[2]) if len(partes) > 2 else 1.0,
                           float(partes[3]) if len(partes) > 3 else 1.0))
        except ValueError as exc:
            raise ParametroInvalidoError("Tamaño, desviación y coste deben ser numéricos.") from exc
    if not salida:
        raise ParametroInvalidoError("Agrega al menos un estrato.")
    return salida


def texto_numero(valor: object) -> str:
    """Formato de celda sin sacrificar la precisión almacenada en el DataFrame."""
    if valor is None:
        return "—"
    if isinstance(valor, (float, np.floating)):
        numero = float(valor)
        if np.isnan(numero):
            return "—"
        if np.isposinf(numero):
            return "∞"
        if np.isneginf(numero):
            return "−∞"
        return f"{numero:.12g}"
    return str(valor)


def texto_escalar(valor: object) -> str:
    """Representa un escalar/vector para indicadores y resúmenes."""
    arreglo = np.asarray(valor)
    if arreglo.ndim:
        return ", ".join(f"{v:.6g}" for v in arreglo.ravel())
    numero = float(arreglo)
    if np.isnan(numero):
        return "Indefinido"
    if np.isinf(numero):
        return "∞" if numero > 0 else "−∞"
    return f"{numero:.6g}"
