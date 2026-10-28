"""Preferencias de accesibilidad del sistema, sin dependencias adicionales.

Qt expone la paleta claro/oscuro y la fuente. Windows también ofrece una API
estable para el indicador de alto contraste. La selección manual siempre gana.
"""

import sys


def alto_contraste_windows() -> bool | None:
    """Consulta SPI_GETHIGHCONTRAST si existe; ``None`` si no es comprobable."""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class HIGHCONTRASTW(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.UINT), ("dwFlags", wintypes.DWORD),
                        ("lpszDefaultScheme", wintypes.LPWSTR)]

        datos = HIGHCONTRASTW()
        datos.cbSize = ctypes.sizeof(HIGHCONTRASTW)
        if ctypes.windll.user32.SystemParametersInfoW(0x0042, datos.cbSize,
                                                       ctypes.byref(datos), 0):
            return bool(datos.dwFlags & 0x00000001)  # HCF_HIGHCONTRASTON
    except (AttributeError, OSError, ValueError):
        return None
    return None


def factor_fuente_sistema(puntos: float, macos: bool = False) -> float:
    """Relación prudente entre la fuente Qt actual y el tamaño normal del SO."""
    referencia = 13.0 if macos else 9.0
    if not 0 < puntos < 100:
        return 1.0
    return max(.9, min(2.0, puntos / referencia))
