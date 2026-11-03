"""Huella reproducible del equipo y del árbol de código verificado.

Uso:
    python verificacion/pruebas/recolectar_entorno.py --salida datos/entorno.json
    python ... --gui          # además comprueba un contexto Dear PyGui real

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
        if ruta.is_file() and ruta.suffix in {".py", ".md", ".js", ".css", ".html"}:
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
    """Comprueba Dear PyGui sin afirmar haber medido pantalla o DPI."""
    try:
        import dearpygui.dearpygui as dpg

        dpg.create_context()
        try:
            return {
                "plataforma_ui": "Dear PyGui",
                "version_dpg": dpg.get_dearpygui_version(),
                "pantallas": [],
                "fuente_sistema": "no consultada: Dear PyGui no expone una API portable",
                "nota": "Contexto real sin viewport; la medición de DPI requiere revisión nativa.",
            }
        finally:
            dpg.destroy_context()
    except Exception as exc:
        return {"plataforma_ui": "Dear PyGui", "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Huella de entorno para el reporte de AmPu 3.0")
    parser.add_argument("--salida", type=Path, default=Path("datos/entorno.json"))
    parser.add_argument("--gui", action="store_true", help="Comprueba el contexto Dear PyGui")
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
