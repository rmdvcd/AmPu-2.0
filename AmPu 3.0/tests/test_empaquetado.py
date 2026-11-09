"""Empaquetado Dear PyGui sin arrastrar Qt ni depender de compilación en CI."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_exe.py"
spec = importlib.util.spec_from_file_location("ampu_build_exe", SCRIPT)
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)


def test_comando_incluye_dearpygui_y_recursos_sin_qt():
    orden = modulo.comando(onefile=True)
    assert orden[0] and orden[1:3] == ["-m", "PyInstaller"]
    assert "dearpygui.dearpygui" in orden
    assert "PySide6.QtWebEngineWidgets" not in orden
    assert all("QtWebEngine" not in argumento for argumento in orden)
    for excluido in ("PySide6", "PyQt6", "PyQt5"):
        assert excluido in orden
    for carpeta in ("ampu/docs", "ampu/ui/recursos"):
        assert any(carpeta in argumento for argumento in orden)
    assert "--onedir" in modulo.comando(onefile=False)
    if modulo.sys.platform in ("win32", "darwin"):
        assert "--icon" in orden
        assert Path(orden[orden.index("--icon") + 1]).is_file()
    else:
        assert "--onefile" in orden
