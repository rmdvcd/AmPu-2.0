"""La selección del sistema no presupone APIs de otras plataformas."""

import math

from ampu.ui.preferencias_sistema import apariencia_sistema, factor_fuente_sistema


def test_factor_de_fuente_nativa_acotado():
    assert factor_fuente_sistema(9) == 1
    assert factor_fuente_sistema(13, macos=True) == 1
    assert factor_fuente_sistema(18) == 2
    assert factor_fuente_sistema(6) == .9
    assert factor_fuente_sistema(math.nan) == 1
    assert factor_fuente_sistema(-2) == 1


def test_apariencia_sistema_devuelve_claro_u_oscuro():
    assert apariencia_sistema() in {"claro", "oscuro"}
