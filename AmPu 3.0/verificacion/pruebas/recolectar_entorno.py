"""Huella reproducible del equipo y del árbol de código verificado.

Uso:
    python verificacion/pruebas/recolectar_entorno.py --salida datos/entorno.json
    python ... --gui          # además abre QGuiApplication para leer pantallas/DPI/tema

No modifica nada del proyecto ni la configuración del usuario.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import _comun  # noqa: E402  (mismo directorio)


def _git(raiz: Path, *args: str) -> str:
    try:
        salida = subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True,
                                timeout=30, check=False)
        return salida.stdout.strip() or salida.stderr.strip()[:300]
    except Exception as exc:
        return f"no disponible: {exc}"


def _hash_arbol(raiz: Path, limite: int = 4000) -> dict:
    """SHA-256 del conjunto de fuentes y su tamaño (detecta ediciones locales)."""
    digest = hashlib.sha256()
    contados = 0
    bytes_total = 0
    for ruta in sorted((raiz / "src").rglob("*")):
        if ruta.is_file() and ruta.suffix in {".py", ".qss", ".md", ".js", ".css", ".html"}:
            datos = ruta.read_bytes()
            digest.update(ruta.relative_to(raiz).as_posix().encode("utf-8"))
            digest.update(datos)
            contados += 1
            bytes_total += len(datos)
            if contados >= limite:
                break
    return {"archivos_fuente": contados, "bytes_fuente": bytes_total,
            "sha256_fuentes": digest.hexdigest()}


def _pantallas() -> dict:
    """Lee pantallas reales; devuelve el motivo si Qt no puede inicializarse."""
    try:
        from PySide6.QtGui import QGuiApplication

        app = QGuiApplication.instance() or QGuiApplication(sys.argv[:1])
        pantallas = []
        for pantalla in app.screens():
            geometria = pantalla.geometry()
            pantallas.append({
                "nombre": pantalla.name(),
                "tamano_px": [geometria.width(), geometria.height()],
                "dpi_logico": round(pantalla.logicalDotsPerInch(), 1),
                "dpi_fisico": round(pantalla.physicalDotsPerInch(), 1),
                "escala": round(pantalla.devicePixelRatio(), 2),
                "frecuencia_hz": round(pantalla.refreshRate(), 1),
            })
        return {"plataforma_qt": app.platformName(), "tema_so": str(app.styleHints().colorScheme()),
                "pantallas": pantallas, "fuente_sistema": app.font().toString()}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Huella de entorno para el reporte de AmPu 3.0")
    parser.add_argument("--salida", type=Path, default=Path("datos/entorno.json"))
    parser.add_argument("--gui", action="store_true", help="Lee pantallas/DPI (requiere escritorio)")
    args = parser.parse_args()

    raiz = _comun.preparar_import()
    info = _comun.entorno()
    info["raiz_proyecto"] = str(raiz)
    info["git"] = {
        "commit": _git(raiz, "rev-parse", "HEAD"),
        "rama": _git(raiz, "rev-parse", "--abbrev-ref", "HEAD"),
        "estado": _git(raiz, "status", "--porcelain") or "limpio",
        "ultimo_commit": _git(raiz, "log", "-1", "--pretty=%ad | %s", "--date=iso"),
    }
    info["huella_fuentes"] = _hash_arbol(raiz)
    if args.gui:
        info["pantalla"] = _pantallas()
    info["discos"] = {}
    try:
        import shutil

        uso = shutil.disk_usage(raiz)
        info["discos"]["proyecto"] = {"total_gb": round(uso.total / 2**30, 1),
                                      "libre_gb": round(uso.free / 2**30, 1)}
    except Exception:
        pass
    _comun.guardar_json(args.salida, {"herramienta": "recolectar_entorno",
                                      "version_esquema": 1, "generado": _comun.ahora(),
                                      "resultados": [], "metricas": [],
                                      "entorno": info,
                                      "resumen": {"total": 0, "pasan": 0, "fallan": 0,
                                                  "omitidas": 0, "veredicto": "CORRECTO"}})
    print(json.dumps({k: info[k] for k in ("so", "python", "ampu", "librerias", "git")},
                     indent=2, ensure_ascii=False))
    print(f"Entorno guardado en {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
