"""Utilidades compartidas por los scripts de verificación de AmPu 3.0.

Este módulo no forma parte del producto: solo lo usan los scripts de
``verificacion/pruebas``. No importa Qt ni modifica la aplicación.

Convenciones de salida (todas las herramientas escriben el mismo sobre):
    {
      "herramienta": str, "version_esquema": 1, "generado": ISO-8601,
      "entorno": {...}, "opciones": {...},
      "resultados": [ {...}, ... ],
      "metricas": [...],            # serie de mediciones (rendimiento)
      "resumen": {"total": int, "pasan": int, "fallan": int, "omitidas": int,
                  "veredicto": "CORRECTO" | "FALLA" | "INCOMPLETO"}
    }
"""

from __future__ import annotations

import json
import math
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

RAIZ = Path(__file__).resolve().parents[2]  # .../AmPu 3.0


def preparar_import() -> Path:
    """Permite ejecutar los scripts sin instalar el paquete (``src`` en el path)."""
    origen = str(RAIZ / "src")
    if origen not in sys.path:
        sys.path.insert(0, origen)
    return RAIZ


def ahora() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _json_seguro(valor: Any) -> Any:
    """Convierte tipos NumPy/pandas/Path en algo serializable y finito."""
    if valor is None or isinstance(valor, (bool, int, str)):
        return valor
    if isinstance(valor, float):
        return valor if math.isfinite(valor) else ("inf" if valor > 0 else "-inf")
    if isinstance(valor, Path):
        return str(valor)
    if isinstance(valor, dict):
        return {str(k): _json_seguro(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple, set)):
        return [_json_seguro(v) for v in valor]
    conversor = getattr(valor, "tolist", None)  # ndarray, pandas Series, etc.
    if callable(conversor):
        try:
            return _json_seguro(conversor())
        except (TypeError, ValueError):
            pass
    elemento = getattr(valor, "item", None)  # escalares NumPy
    if callable(elemento):
        try:
            return _json_seguro(elemento())
        except (TypeError, ValueError, AttributeError):
            pass
    if hasattr(valor, "isoformat"):  # fechas y horas
        return valor.isoformat()
    return str(valor)


def guardar_json(destino: str | os.PathLike, datos: dict) -> Path:
    """Escribe JSON UTF-8 legible por humanos y por la consolidación."""
    ruta = Path(destino)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(_json_seguro(datos), indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta


def memoria_mb() -> dict:
    """Memoria del proceso sin dependencias externas (Windows usa psapi)."""
    datos = {"rss_mb": None, "pico_mb": None, "metodo": "no disponible"}
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t),
                            ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]

            contadores = PMC()
            contadores.cb = ctypes.sizeof(PMC)
            proceso = ctypes.windll.kernel32.GetCurrentProcess()
            if ctypes.windll.psapi.GetProcessMemoryInfo(proceso, ctypes.byref(contadores), contadores.cb):
                datos = {"rss_mb": round(contadores.WorkingSetSize / 2**20, 1),
                         "pico_mb": round(contadores.PeakWorkingSetSize / 2**20, 1),
                         "metodo": "psapi.GetProcessMemoryInfo"}
        else:
            import resource

            pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            factor = 2**20 if sys.platform == "darwin" else 2**10
            datos = {"rss_mb": None, "pico_mb": round(pico / factor, 1),
                     "metodo": "resource.ru_maxrss"}
    except Exception as exc:  # pragma: no cover - diagnóstico best effort
        datos["metodo"] = f"error: {exc}"
    return datos


def _memoria_total_mb() -> float | None:
    """RAM instalada, sin dependencias externas."""
    try:
        if os.name == "nt":
            import ctypes

            class MemStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

            estado = MemStatus()
            estado.dwLength = ctypes.sizeof(MemStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado)):
                return round(estado.ullTotalPhys / 2**20, 0)
            return None
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**20, 0)
    except Exception:
        return None


def entorno() -> dict:
    """Huella del equipo: imprescindible para comparar dos reportes."""
    info = {
        "fecha_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "so": platform.platform(),
        "sistema": platform.system(),
        "version_so": platform.version(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", ""),
        "nucleos_logicos": os.cpu_count(),
        "python": sys.version.split()[0],
        "python_implementacion": platform.python_implementation(),
        "ejecutable_python": sys.executable,
        "cwd": os.getcwd(),
        "entorno_virtual": os.environ.get("VIRTUAL_ENV", ""),
        "variables_qt": {k: os.environ.get(k, "") for k in
                         ("QT_QPA_PLATFORM", "QTWEBENGINE_DISABLE_SANDBOX", "QT_SCALE_FACTOR",
                          "QT_ENABLE_HIGHDPI_SCALING", "QT_SCREEN_SCALE_FACTORS")},
        "memoria_total_mb": _memoria_total_mb(),
        "librerias": {},
    }
    for modulo in ("numpy", "scipy", "pandas", "matplotlib", "PySide6", "openpyxl", "reportlab", "markdown"):
        try:
            import importlib

            paquete = importlib.import_module(modulo)
            info["librerias"][modulo] = getattr(paquete, "__version__", "desconocida")
        except Exception:
            info["librerias"][modulo] = "ausente"
    try:
        import ampu

        info["ampu"] = getattr(ampu, "__version__", "desconocida")
    except Exception as exc:
        info["ampu"] = f"no importable: {exc}"
    try:  # información de la pantalla solo si ya existe una QApplication
        from PySide6.QtGui import QGuiApplication

        app = QGuiApplication.instance()
        if app is not None:
            pantallas = []
            for pantalla in app.screens():
                geometria = pantalla.geometry()
                pantallas.append({"nombre": pantalla.name(),
                                  "tamano_px": [geometria.width(), geometria.height()],
                                  "dpi_logico": round(pantalla.logicalDotsPerInch(), 1),
                                  "dpi_fisico": round(pantalla.physicalDotsPerInch(), 1),
                                  "escala": round(pantalla.devicePixelRatio(), 2),
                                  "frecuencia_hz": round(pantalla.refreshRate(), 1)})
            info["pantallas"] = pantallas
            info["plataforma_qt"] = app.platformName()
            info["tema_so"] = str(app.styleHints().colorScheme())
    except Exception:
        pass
    return info


class Revisor:
    """Acumula comprobaciones con su tolerancia y su veredicto."""

    def __init__(self, perfil: str = "completo") -> None:
        self.perfil = perfil
        self.resultados: list[dict] = []
        self.metricas: list[dict] = []
        self.inicio = time.perf_counter()

    # ------------------------------------------------------------------ checks
    def registrar(self, identificador: str, categoria: str, descripcion: str, *,
                  pasa: bool, obtenido: Any = None, esperado: Any = None,
                  tolerancia: Any = None, unidad: str | None = None,
                  notas: str = "", omitida: bool = False) -> bool:
        self.resultados.append({
            "id": identificador, "categoria": categoria, "descripcion": descripcion,
            "estado": "OMITIDA" if omitida else ("PASA" if pasa else "FALLA"),
            "obtenido": obtenido, "esperado": esperado, "tolerancia": tolerancia,
            "unidad": unidad, "notas": notas,
        })
        if not pasa and not omitida:
            print(f"  [FALLA] {identificador}: {descripcion} -> obtenido={obtenido!r} "
                  f"esperado={esperado!r} tol={tolerancia!r}")
        return pasa

    def cerca(self, identificador: str, categoria: str, descripcion: str,
              obtenido: Any, esperado: Any, rtol: float = 1e-9, atol: float = 1e-12,
              notas: str = "", unidad: str | None = None) -> bool:
        """Compara de forma numérica tolerante (escalar o vector)."""
        try:
            a = float(obtenido) if not hasattr(obtenido, "__len__") else list(map(float, obtenido))
            b = float(esperado) if not hasattr(esperado, "__len__") else list(map(float, esperado))
        except (TypeError, ValueError):
            return self.registrar(identificador, categoria, descripcion, pasa=obtenido == esperado,
                                  obtenido=obtenido, esperado=esperado, tolerancia=f"rtol={rtol}",
                                  notas=notas, unidad=unidad)
        if isinstance(a, list) or isinstance(b, list):
            a, b = (a if isinstance(a, list) else [a]), (b if isinstance(b, list) else [b])
            if len(a) != len(b):
                return self.registrar(identificador, categoria, descripcion, pasa=False,
                                      obtenido=obtenido, esperado=esperado,
                                      tolerancia=f"rtol={rtol}, atol={atol}", notas=notas, unidad=unidad)
            pasa = all(self._casi(x, y, rtol, atol) for x, y in zip(a, b))
            error = max((abs(x - y) for x, y in zip(a, b) if math.isfinite(x) and math.isfinite(y)), default=0.0)
        else:
            pasa = self._casi(a, b, rtol, atol)
            error = abs(a - b) if math.isfinite(a) and math.isfinite(b) else 0.0
        return self.registrar(identificador, categoria, descripcion, pasa=pasa,
                              obtenido=obtenido, esperado=esperado,
                              tolerancia={"rtol": rtol, "atol": atol, "error_absoluto": error},
                              notas=notas, unidad=unidad)

    @staticmethod
    def _casi(a: float, b: float, rtol: float, atol: float) -> bool:
        if math.isnan(a) and math.isnan(b):
            return True
        if math.isinf(a) or math.isinf(b):
            return a == b
        return abs(a - b) <= atol + rtol * abs(b)

    def verdadero(self, identificador: str, categoria: str, descripcion: str,
                  condicion: Any, notas: str = "", **extra: Any) -> bool:
        return self.registrar(identificador, categoria, descripcion, pasa=bool(condicion),
                              notas=notas, **extra)

    def lanza(self, identificador: str, categoria: str, descripcion: str,
              funcion: Callable[[], Any], excepcion: type[BaseException] | tuple = Exception,
              notas: str = "") -> bool:
        """Comprueba que una entrada inválida se rechaza con un error de dominio."""
        try:
            funcion()
        except excepcion as exc:
            return self.registrar(identificador, categoria, descripcion, pasa=True,
                                  obtenido=type(exc).__name__, esperado=getattr(excepcion, "__name__", str(excepcion)),
                                  notas=notas or str(exc)[:160])
        except Exception as exc:
            return self.registrar(identificador, categoria, descripcion, pasa=False,
                                  obtenido=f"{type(exc).__name__}: {exc}"[:200],
                                  esperado=getattr(excepcion, "__name__", str(excepcion)),
                                  notas="Se lanzó un tipo de excepción no previsto")
        return self.registrar(identificador, categoria, descripcion, pasa=False,
                              obtenido="sin excepción", esperado=getattr(excepcion, "__name__", str(excepcion)),
                              notas=notas)

    def omitir(self, identificador: str, categoria: str, descripcion: str, motivo: str) -> None:
        self.registrar(identificador, categoria, descripcion, pasa=True, omitida=True, notas=motivo)

    # ------------------------------------------------------------- mediciones
    def medir(self, nombre: str, categoria: str, funcion: Callable[[], Any],
              repeticiones: int = 5, calentamiento: int = 1, notas: str = "") -> float:
        """Cronometra con ``perf_counter_ns``; devuelve la mediana en milisegundos."""
        for _ in range(max(0, calentamiento)):
            funcion()
        muestras: list[float] = []
        for _ in range(max(1, repeticiones)):
            inicio = time.perf_counter_ns()
            funcion()
            muestras.append((time.perf_counter_ns() - inicio) / 1e6)
        ordenadas = sorted(muestras)
        metrica = {
            "operacion": nombre, "categoria": categoria, "n": len(muestras),
            "min_ms": round(ordenadas[0], 3),
            "mediana_ms": round(statistics.median(ordenadas), 3),
            "p95_ms": round(ordenadas[min(len(ordenadas) - 1, int(round(0.95 * (len(ordenadas) - 1))))], 3),
            "max_ms": round(ordenadas[-1], 3),
            "ops_por_segundo": round(1000.0 / statistics.median(ordenadas), 1) if statistics.median(ordenadas) else None,
            "notas": notas,
        }
        self.metricas.append(metrica)
        print(f"  [tiempo] {nombre:<52} mediana {metrica['mediana_ms']:>9.2f} ms  p95 {metrica['p95_ms']:>9.2f} ms")
        return metrica["mediana_ms"]

    # ---------------------------------------------------------------- cierre
    def resumen(self) -> dict:
        total = len(self.resultados)
        pasan = sum(1 for r in self.resultados if r["estado"] == "PASA")
        fallan = sum(1 for r in self.resultados if r["estado"] == "FALLA")
        omitidas = sum(1 for r in self.resultados if r["estado"] == "OMITIDA")
        return {"total": total, "pasan": pasan, "fallan": fallan, "omitidas": omitidas,
                "veredicto": "FALLA" if fallan else ("INCOMPLETO" if omitidas else "CORRECTO"),
                "duracion_s": round(time.perf_counter() - self.inicio, 2)}

    def documento(self, herramienta: str, opciones: dict | None = None) -> dict:
        resumen = self.resumen()
        print(f"\n{herramienta}: {resumen['pasan']} pasan · {resumen['fallan']} fallan · "
              f"{resumen['omitidas']} omitidas en {resumen['duracion_s']} s")
        return {"herramienta": herramienta, "version_esquema": 1, "generado": ahora(),
                "perfil": self.perfil, "entorno": entorno(), "opciones": opciones or {},
                "resultados": self.resultados, "metricas": self.metricas,
                "memoria": memoria_mb(), "resumen": resumen}


def buscar_arbol(raiz: Path, patrones: Sequence[str]) -> list[Path]:
    """Devuelve archivos que cumplen alguno de los globs, ordenados."""
    encontrados: list[Path] = []
    for patron in patrones:
        encontrados.extend(sorted(raiz.glob(patron)))
    return encontrados
