"""Prueba el punto de entrada real en un proceso Qt aislado y sin pantalla."""

import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError,
                    reason="Qt requiere bibliotecas gráficas del sistema")


def test_python_m_ampu_abre_ventana_y_dibuja_resultados_iniciales(tmp_path):
    # sitecustomize prepara el temporizador antes de ejecutar exactamente -m ampu.
    # El proceso termina solo después de mostrar la ventana y dibujar los resultados.
    (tmp_path / "sitecustomize.py").write_text(textwrap.dedent("""\
        import traceback
        from PySide6.QtCore import QSettings, QTimer
        from PySide6.QtWidgets import QApplication

        QSettings.setDefaultFormat(QSettings.IniFormat)
        app = QApplication([])
        intentos = 0

        def comprobar():
            global intentos
            try:
                from ampu.ui.main_window import VentanaPrincipal
                ventanas = [w for w in app.topLevelWidgets()
                            if isinstance(w, VentanaPrincipal) and w.isVisible()]
                if not ventanas:
                    raise RuntimeError("No se mostró la ventana principal")
                ventana = ventanas[0]
                claves = ("distribuciones", "muestreo", "descriptiva", "simulacion")
                if all(ventana.vistas[k].ultimo is not None
                       and not ventana.vistas[k]._ocupado
                       and ventana.vistas[k].grafico._ultimo is not None for k in claves):
                    print("ARRANQUE_CORRECTO", flush=True)
                    ventana.close()
                    app.quit()
                elif intentos >= 200:
                    raise RuntimeError("No se completaron los gráficos iniciales")
                else:
                    intentos += 1
                    QTimer.singleShot(100, comprobar)
            except Exception:
                traceback.print_exc()
                app.exit(1)

        QTimer.singleShot(1200, comprobar)
    """), encoding="utf-8")
    raiz = Path(__file__).resolve().parents[1]
    entorno = os.environ.copy()
    entorno.update({
        "QT_QPA_PLATFORM": "offscreen",
        "QTWEBENGINE_DISABLE_SANDBOX": "1",
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "XDG_DATA_HOME": str(tmp_path / "datos"),
        "APPDATA": str(tmp_path / "datos"),
        "LOCALAPPDATA": str(tmp_path / "local"),
        "MPLCONFIGDIR": str(tmp_path / "matplotlib"),
        "PYTHONPATH": os.pathsep.join((str(tmp_path), str(raiz / "src"), entorno.get("PYTHONPATH", ""))),
    })
    proceso = subprocess.run([sys.executable, "-m", "ampu"], cwd=raiz, env=entorno,
                            text=True, capture_output=True, timeout=60)
    assert proceso.returncode == 0, proceso.stdout + proceso.stderr
    assert "ARRANQUE_CORRECTO" in proceso.stdout
    assert "Traceback" not in proceso.stderr
