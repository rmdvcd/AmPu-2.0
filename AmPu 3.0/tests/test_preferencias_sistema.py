"""La selección del sistema no presupone APIs de otras plataformas."""

import math

from ampu.ui.preferencias_sistema import alto_contraste_windows, factor_fuente_sistema


def test_factor_de_fuente_nativa_acotado():
    assert factor_fuente_sistema(9) == 1
    assert factor_fuente_sistema(13, macos=True) == 1
    assert factor_fuente_sistema(18) == 2
    assert factor_fuente_sistema(6) == .9
    assert factor_fuente_sistema(math.nan) == 1
    assert factor_fuente_sistema(-2) == 1


def test_alto_contraste_no_invoca_win32_en_linux():
    import sys
    if sys.platform != "win32":
        assert alto_contraste_windows() is None
