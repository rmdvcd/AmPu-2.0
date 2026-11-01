"""Preferencias visuales del sistema sin dependencias específicas de plataforma."""


def factor_fuente_sistema(puntos: float, macos: bool = False) -> float:
    """Relación prudente entre la fuente Qt actual y el tamaño normal del SO."""
    referencia = 13.0 if macos else 9.0
    if not 0 < puntos < 100:
        return 1.0
    return max(.9, min(2.0, puntos / referencia))
