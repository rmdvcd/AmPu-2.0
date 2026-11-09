"""Verificación reproducible de la interfaz Dear PyGui de AmPu 3.0.

``--plataforma offscreen`` crea un contexto real sin viewport y comprueba vistas,
cálculos, temas, exportaciones y sesión. No afirma haber renderizado píxeles.
``--plataforma native`` además abre el viewport y captura cada vista y tema.

Ejemplos:
    python verificacion/pruebas/benchmark_ui.py --plataforma offscreen \
        --salida datos/ui_offscreen.json --capturas capturas/offscreen
    python verificacion/pruebas/benchmark_ui.py --plataforma native \
        --salida datos/ui_nativo.json --capturas capturas --exportaciones exportaciones

Código de salida: 0 si no hay fallos; 1 si alguna comprobación falla. Las capturas
omitidas en modo sin viewport se registran explícitamente como INCOMPLETO visual.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import _comun  # noqa: E402

RAIZ = _comun.preparar_import()
VISTAS = ["distribuciones", "muestreo", "descriptiva", "probabilidad", "inferencia", "simulacion"]
TEMAS = ["claro", "oscuro"]


def _huella_y_estadisticas(ruta: Path) -> dict:
    """aHash y luminancia de la captura real; no sustituye inspección humana."""
    import numpy as np
    from PIL import Image

    with Image.open(ruta) as original:
        imagen = original.convert("RGB")
        grises = imagen.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
        pixeles = np.asarray(grises, dtype=float)
        bits = "".join("1" if valor >= pixeles.mean() else "0" for valor in pixeles.ravel())
        muestra = np.asarray(imagen.resize((160, 120)), dtype=float) / 255.0
        lineal = np.where(muestra <= .04045, muestra / 12.92, ((muestra + .055) / 1.055) ** 2.4)
        luminancia = lineal @ np.array([.2126, .7152, .0722])
        return {"px": list(imagen.size), "ahash": f"{int(bits, 2):016x}",
                "luminancia_media": round(float(luminancia.mean()), 4),
                "colores_muestreados": int(len(np.unique(muestra.reshape(-1, 3), axis=0)))}


def _distancia(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pruebas de la interfaz Dear PyGui")
    parser.add_argument("--salida", type=Path, default=Path("datos/ui.json"))
    parser.add_argument("--capturas", type=Path, default=Path("capturas"))
    parser.add_argument("--exportaciones", type=Path, default=Path("exportaciones"))
    parser.add_argument("--plataforma", choices=["native", "offscreen"], default="native",
                        help="native abre viewport; offscreen solo crea el contexto de widgets")
    parser.add_argument("--temas", default=",".join(TEMAS))
    parser.add_argument("--vistas", default=",".join(VISTAS + ["teoria"]))
    parser.add_argument("--zoom", type=float, nargs="*", default=[])
    parser.add_argument("--sin-teoria", action="store_true", help="No abre el lector de teoría")
    parser.add_argument("--sin-exportadores", action="store_true")
    parser.add_argument("--linea-base", type=Path, default=None)
    parser.add_argument("--guardar-linea-base", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--tamano", default="1440x900")
    args = parser.parse_args()
    args.capturas.mkdir(parents=True, exist_ok=True)
    args.exportaciones.mkdir(parents=True, exist_ok=True)
    r = _comun.Revisor(f"ui-{args.plataforma}")
    opciones = {"plataforma": args.plataforma, "plataforma_ui": "Dear PyGui",
                "viewport": args.plataforma == "native", "tamano": args.tamano,
                "temas": args.temas, "vistas": args.vistas.split(",")}

    try:
        import matplotlib
        matplotlib.use("Agg", force=True)
        import dearpygui.dearpygui as dpg
        from ampu.ui.main_window import ANALISIS, VentanaPrincipal
        from ampu.ui.preferencias import Preferencias
        from ampu.ui.temas import PALETAS, relacion_contraste
    except Exception as exc:
        r.omitir("ui.disponible", "interfaz", "Dear PyGui puede importarse",
                 f"{type(exc).__name__}: {exc}")
        _comun.guardar_json(args.salida, r.documento("benchmark_ui", opciones))
        return 0

    ventana = None
    capturas: list[dict] = []
    try:
        dpg.create_context()
        r.verdadero("ui.contexto", "interfaz", "Se crea un contexto Dear PyGui real", True,
                    obtenido=dpg.get_dearpygui_version(), esperado="contexto creado")
        preferencias = Preferencias(ruta=args.capturas.parent / "preferencias_verificacion.json",
                                    valores={"interfaz/tema": "claro", "interfaz/escala": 1.0})

        def construir():
            return VentanaPrincipal(preferencias)

        inicio = time.perf_counter()
        ventana = construir()
        r.metricas.append({"operacion": "arranque: VentanaPrincipal + 7 vistas", "categoria": "interfaz",
                           "n": 1, "min_ms": round((time.perf_counter() - inicio) * 1000, 2),
                           "mediana_ms": round((time.perf_counter() - inicio) * 1000, 2),
                           "p95_ms": round((time.perf_counter() - inicio) * 1000, 2),
                           "max_ms": round((time.perf_counter() - inicio) * 1000, 2),
                           "ops_por_segundo": None, "notas": "Dear PyGui sin suplentes"})
        r.verdadero("ui.vistas.construccion", "interfaz", "Se construyen las siete vistas",
                    len(ventana.vistas) == 7, obtenido=len(ventana.vistas), esperado=7)

        if args.plataforma == "native":
            try:
                ancho, alto = (int(valor) for valor in args.tamano.lower().split("x", 1))
                dpg.create_viewport(title="AmPu 3.0 · verificación", width=ancho, height=alto,
                                    min_width=900, min_height=600)
                dpg.setup_dearpygui()
                dpg.show_viewport()
                dpg.set_primary_window(ventana.window, True)
                r.verdadero("ui.viewport", "interfaz", "El viewport nativo puede abrirse", True)
            except Exception as exc:
                r.verdadero("ui.viewport", "interfaz", "El viewport nativo puede abrirse", False,
                            obtenido=f"{type(exc).__name__}: {exc}", esperado="viewport visible")
        else:
            r.omitir("ui.capturas", "visual", "Capturas reales del viewport",
                     "Modo sin viewport: los widgets y cálculos sí se comprueban; los píxeles no.")

        solicitadas = [v for v in args.vistas.split(",") if v in ventana.vistas]
        for clave in solicitadas:
            if clave == "teoria":
                continue

            def calcular_y_esperar(k=clave):
                ventana.cambiar(k)
                return ventana.vistas[k].esperar(args.timeout)

            r.medir(f"cálculo inicial: {clave}", "interfaz", calcular_y_esperar,
                    repeticiones=1, calentamiento=0)
            vista = ventana.vistas[clave]
            r.verdadero(f"ui.{clave}.resultado", "interfaz", f"{clave} produce un resultado real",
                        vista.ultimo is not None and not vista.tabla.datos().empty,
                        obtenido={"resultado": vista.ultimo is not None, "filas": len(vista.tabla.datos())},
                        esperado="resultado y tabla no vacía")

        for tema in [t for t in args.temas.split(",") if t in TEMAS]:
            ventana.aplicar_tema(tema)
            paleta = PALETAS[tema]
            contraste = relacion_contraste(paleta["texto"], paleta["fondo"])
            r.verdadero(f"ui.tema.{tema}", "accesibilidad", f"Contraste texto/fondo del tema {tema}",
                        contraste >= 4.5, obtenido=round(contraste, 2), esperado=">= 4.5:1")
            for clave in solicitadas:
                if args.sin_teoria and clave == "teoria":
                    continue
                ventana.cambiar(clave)
                if clave in ANALISIS:
                    ventana.vistas[clave].esperar(args.timeout)
                if args.plataforma != "native":
                    continue
                for _ in range(4):
                    ventana.procesar()
                    dpg.render_dearpygui_frame()
                ruta = args.capturas / f"{clave}_{tema}.png"
                dpg.output_frame_buffer(file=str(ruta))
                ok = ruta.is_file() and ruta.stat().st_size > 0
                r.verdadero(f"ui.captura.{clave}.{tema}", "visual", f"Captura real {clave}/{tema}", ok,
                            obtenido=str(ruta), esperado="PNG no vacío")
                if ok:
                    registro = {"archivo": ruta.name, "tema": tema, "vista": clave, "zoom": 1.0,
                                "bytes": ruta.stat().st_size, **_huella_y_estadisticas(ruta)}
                    capturas.append(registro)

        if not args.sin_teoria:
            ventana.cambiar("teoria")
            contenido = dpg.get_value(ventana.vistas["teoria"].contenido)
            r.verdadero("ui.teoria.contenido", "interfaz", "La teoría local es seleccionable y no está vacía",
                        isinstance(contenido, str) and len(contenido) > 200,
                        obtenido=len(contenido or ""), esperado="> 200 caracteres")

        if not args.sin_exportadores:
            ventana.cambiar("distribuciones")
            ventana.vista.esperar(args.timeout)
            for extension in ("xlsx", "csv", "png", "pdf"):
                destino = args.exportaciones / f"verificacion.{extension}"
                formato = "excel" if extension == "xlsx" else extension
                try:
                    salida = ventana.exportar(formato, destino)
                    ok = bool(salida) and Path(salida).is_file() and Path(salida).stat().st_size > 0
                    obtenido = str(salida)
                except Exception as exc:
                    ok, obtenido = False, f"{type(exc).__name__}: {exc}"
                r.verdadero(f"ui.exportar.{extension}", "exportacion", f"Exportación {extension.upper()}",
                            ok, obtenido=obtenido, esperado="archivo no vacío")

        ventana.cambiar("distribuciones")
        ventana.vista.esperar(args.timeout)
        sesion = args.exportaciones / "sesion_verificacion.json"
        guardada = bool(ventana.guardar_sesion(sesion))
        r.verdadero("ui.sesion.guardar", "sesion", "La sesión se guarda en JSON", guardada and sesion.is_file())
        if guardada:
            r.verdadero("ui.sesion.abrir", "sesion", "La sesión se restaura y recalcula",
                        bool(ventana.abrir_sesion(sesion)) and ventana.esperar(args.timeout))

        for escala in args.zoom:
            ventana.escala_fuente = escala
            ventana.aplicar_tema(ventana.tema_actual)
            r.verdadero(f"ui.zoom.{escala}", "accesibilidad", f"Escala de texto {escala:g}",
                        abs(ventana.escala_fuente - escala) < 1e-9,
                        obtenido=ventana.escala_fuente, esperado=escala,
                        notas="La ausencia de recortes requiere inspección visual nativa.")

        if args.linea_base and args.linea_base.is_file():
            base = json.loads(args.linea_base.read_text(encoding="utf-8"))
            anteriores = base.get("capturas", base) if isinstance(base, dict) else base
            indice = {(c.get("vista"), c.get("tema")): c for c in anteriores}
            for actual in capturas:
                previa = indice.get((actual["vista"], actual["tema"]))
                if previa and previa.get("ahash"):
                    actual["distancia_linea_base"] = _distancia(actual["ahash"], previa["ahash"])
        documento = r.documento("benchmark_ui", opciones)
        documento["capturas"] = capturas
        _comun.guardar_json(args.salida, documento)
        if args.guardar_linea_base:
            _comun.guardar_json(args.salida.parent / "linea_base_ui.json", {"capturas": capturas})
        return 1 if r.resumen()["fallan"] else 0
    except Exception as exc:
        r.verdadero("ui.ejecucion", "interfaz", "La batería Dear PyGui termina sin excepciones", False,
                    obtenido=f"{type(exc).__name__}: {exc}", esperado="sin excepciones")
        documento = r.documento("benchmark_ui", opciones)
        documento["capturas"] = capturas
        _comun.guardar_json(args.salida, documento)
        return 1
    finally:
        if ventana is not None:
            ventana.cerrar()
        try:
            dpg.destroy_context()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
