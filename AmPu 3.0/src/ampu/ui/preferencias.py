"""Preferencias locales pequeñas en JSON, independientes del toolkit."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def ruta_preferencias() -> Path:
    """Ubicación escribible por plataforma; nunca dentro del paquete instalado."""
    if os.name == "nt" and os.environ.get("APPDATA"):
        base = Path(os.environ["APPDATA"])
    elif os.sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "AmPu" / "ampu3.json"


class Preferencias:
    """Diccionario persistente y tolerante a preferencias antiguas/incompletas."""

    def __init__(self, ruta: str | Path | None = None, valores: dict[str, Any] | None = None):
        self.ruta = Path(ruta) if ruta is not None else ruta_preferencias()
        self.valores: dict[str, Any] = dict(valores or {})
        if valores is None:
            self._cargar()
        tema = self.valores.get("interfaz/tema", "sistema")
        if tema not in ("sistema", "claro", "oscuro"):
            self.valores["interfaz/tema"] = "sistema"
        try:
            escala = float(self.valores.get("interfaz/escala", 1.0))
        except (TypeError, ValueError):
            escala = 1.0
        self.valores["interfaz/escala"] = max(0.9, min(2.0, escala))

    def _cargar(self) -> None:
        try:
            if self.ruta.is_file() and self.ruta.stat().st_size <= 1_000_000:
                datos = json.loads(self.ruta.read_text(encoding="utf-8"))
                if isinstance(datos, dict):
                    self.valores = datos
        except (OSError, ValueError, TypeError):
            # Una preferencia dañada no debe impedir abrir el laboratorio.
            self.valores = {}

    def get(self, clave: str, defecto: Any = None) -> Any:
        return self.valores.get(clave, defecto)

    def set(self, clave: str, valor: Any) -> None:
        self.valores[clave] = valor

    def guardar(self) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal: str | None = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.ruta.parent,
                                             prefix=".ampu-prefs-", suffix=".tmp", delete=False) as archivo:
                temporal = archivo.name
                json.dump(self.valores, archivo, ensure_ascii=False, indent=2, allow_nan=False)
            os.replace(temporal, self.ruta)
        finally:
            if temporal is not None and os.path.exists(temporal):
                os.unlink(temporal)
