"""Consolida todas las salidas de la verificación en REPORTE.md + resumen.json.

Se ejecuta al final de ``EjecutarVerificacion.ps1`` (o a mano):

    python verificacion/pruebas/consolidar_reporte.py --carpeta salidas/20261030-101500

Lee lo que exista (tolera ausencias), calcula hallazgos priorizados y escribe:
    <carpeta>/REPORTE.md      documento para revisar y compartir
    <carpeta>/resumen.json    números clave para análisis automático
    <carpeta>/reporte.zip     todo el paquete (reporte, datos, logs, capturas)

No inventa resultados: cuando una prueba no se ejecutó, el reporte lo dice.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

# Umbrales de aceptación. Cámbialos aquí si el equipo/curso fija otros.
UMBRALES = {
    "cobertura_core_pct": 85.0,
    "contraste_min": 4.5,
    "accesibilidad_nombres": 0.95,
    "arranque_ventana_ms": 6_000,
    "vista_primera_ms": 5_000,
    "exportacion_ms": 8_000,
    "memoria_mb": 4_096,
    "operacion_core_ms": 10_000,
    "factor_scipy": 20,
    "distancia_visual": 8,
}

AREA_POR_HERRAMIENTA = {
    "pruebas_calculo": "Cálculo numérico",
    "benchmark_calculo": "Rendimiento del núcleo",
    "benchmark_ui": "Interfaz y accesibilidad",
}


# --------------------------------------------------------------------------- #
# Lectura
# --------------------------------------------------------------------------- #
def leer_json(ruta: Path) -> dict | list | None:
    if not ruta.is_file():
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        print(f"Aviso: no se pudo leer {ruta.name}: {exc}", file=sys.stderr)
        return None


def leer_junit(ruta: Path) -> dict:
    datos = {"total": 0, "fallos": 0, "errores": 0, "omitidas": 0,
             "tiempo_s": 0.0, "casos_fallidos": [], "omitidos": []}
    if not ruta.is_file():
        return datos
    try:
        arbol = ET.parse(ruta)
    except ET.ParseError:
        return datos
    for caso in arbol.iter("testcase"):
        datos["total"] += 1
        datos["tiempo_s"] += float(caso.get("time") or 0)
        nombre = f"{caso.get('classname', '')}::{caso.get('name', '')}"
        fallo = caso.find("failure")
        error = caso.find("error")
        omitido = caso.find("skipped")
        if fallo is not None or error is not None:
            nodo = fallo if fallo is not None else error
            if fallo is not None:
                datos["fallos"] += 1
            else:
                datos["errores"] += 1
            datos["casos_fallidos"].append({
                "prueba": nombre,
                "tipo": "fallo" if fallo is not None else "error",
                "mensaje": (nodo.get("message") or (nodo.text or ""))[:400].strip(),
            })
        elif omitido is not None:
            datos["omitidas"] += 1
            datos["omitidos"].append({"prueba": nombre,
                                      "motivo": (omitido.get("message") or "")[:200]})
    return datos


def leer_cobertura(ruta: Path) -> dict:
    datos = {"global_pct": None, "lineas": 0, "cubiertas": 0, "modulos": []}
    if not ruta.is_file():
        return datos
    try:
        arbol = ET.parse(ruta)
    except ET.ParseError:
        return datos
    raiz = arbol.getroot()
    if raiz.get("line-rate"):
        datos["global_pct"] = round(float(raiz.get("line-rate")) * 100, 2)
    for clase in raiz.iter("class"):
        nombre = clase.get("filename", "")
        lineas = list(clase.iter("line"))
        cubiertas = sum(1 for linea in lineas if int(linea.get("hits") or 0) > 0)
        porcentaje = round(cubiertas / len(lineas) * 100, 1) if lineas else 0.0
        datos["lineas"] += len(lineas)
        datos["cubiertas"] += cubiertas
        datos["modulos"].append({"archivo": nombre, "cobertura_pct": porcentaje,
                                 "ramas_pct": round(float(clase.get("branch-rate") or 0) * 100, 1)
                                 if clase.get("branch-rate") else None,
                                 "lineas": len(lineas)})
    if datos["global_pct"] is None and datos["lineas"]:
        datos["global_pct"] = round(datos["cubiertas"] / datos["lineas"] * 100, 2)
    datos["modulos"].sort(key=lambda m: m["cobertura_pct"])
    return datos


# --------------------------------------------------------------------------- #
# Formato
# --------------------------------------------------------------------------- #
def md_tabla(cabeceras: list[str], filas: list[list[Any]]) -> str:
    if not filas:
        return "_Sin datos._\n"
    salida = ["| " + " | ".join(cabeceras) + " |",
              "|" + "|".join(["---"] * len(cabeceras)) + "|"]
    for fila in filas:
        salida.append("| " + " | ".join("" if c is None else str(c).replace("|", "\\|")
                                        for c in fila) + " |")
    return "\n".join(salida) + "\n"


def estado(valor: str) -> str:
    return {"PASA": "OK", "FALLA": "**FALLA**", "OMITIDA": "omitida", "OK": "OK",
            "TIMEOUT": "**TIMEOUT**", "CORRECTO": "OK",
            "INCOMPLETO": "OK (con omitidas)"}.get(str(valor), str(valor))


def fmt_numero(valor, decimales: int = 2, sufijo: str = "") -> str:
    if valor is None:
        return "—"
    if isinstance(valor, (int, float)):
        if isinstance(valor, float) and not valor == valor:
            return "—"
        return f"{valor:,.{decimales}f}{sufijo}"
    return str(valor)


def acortar(texto: Any, limite: int = 160) -> str:
    cadena = str(texto).replace("\n", " ")
    return cadena if len(cadena) <= limite else cadena[:limite - 1] + "…"


# --------------------------------------------------------------------------- #
# Análisis
# --------------------------------------------------------------------------- #
def evaluar(carpeta: Path) -> dict:
    datos_dir = carpeta / "datos"
    info = {
        "carpeta": str(carpeta),
        "pasos": leer_json(carpeta / "pasos.json") or [],
        "entorno": (leer_json(datos_dir / "entorno.json") or {}).get("entorno", {}),
        "junit": leer_junit(datos_dir / "junit.xml"),
        "cobertura": leer_cobertura(datos_dir / "coverage.xml"),
        "scipy": leer_json(datos_dir / "scipy.json"),
        "calculo": leer_json(datos_dir / "calculo.json"),
        "rendimiento": leer_json(datos_dir / "rendimiento.json"),
        "ui_nativo": leer_json(datos_dir / "ui_nativo.json"),
        "ui_offscreen": leer_json(datos_dir / "ui_offscreen.json"),
        "selftest": (carpeta / "logs" / "self_test.log"),
        "verify": (carpeta / "logs" / "verify_resources.log"),
    }
    return info


def recopilar_metricas_ui(documento: dict | None) -> tuple[list[dict], list[dict], dict]:
    """Devuelve (métricas de tiempo, capturas, resumen de contraste/accesibilidad)."""
    if not documento:
        return [], [], {}
    tiempos, capturas = [], documento.get("capturas", [])
    contrastes = {}
    accesibilidad = {}
    for metrica in documento.get("metricas", []):
        if metrica.get("categoria") == "accesibilidad":
            contrastes[metrica["operacion"]] = metrica
        else:
            tiempos.append(metrica)
    for resultado in documento.get("resultados", []):
        if resultado["id"] == "ui.accesibilidad.nombres":
            accesibilidad = resultado
    return tiempos, capturas, {"contrastes": contrastes, "accesibilidad": accesibilidad}


def veredicto_de(info: dict, encontrados: list[dict]) -> str:
    """Veredicto legible; distingue «no se ejecutó» de «sin problemas»."""
    ejecutado = (bool(info["pasos"]) or bool(info["calculo"]) or bool(info["rendimiento"])
                 or bool(info["ui_nativo"]) or bool(info["ui_offscreen"])
                 or bool(info["scipy"]) or bool(info["junit"].get("total")))
    if not ejecutado:
        return "SIN DATOS: no se ejecutó la verificación"
    if any(h["severidad"] == "Alta" for h in encontrados):
        return "REQUIERE CORRECCIONES"
    if any(h["severidad"] == "Media" for h in encontrados):
        return "LISTO PARA REVISIÓN (con observaciones)"
    return "SIN HALLAZGOS BLOQUEANTES"


def hallazgos(info: dict) -> list[dict]:
    """Lista priorizada de problemas y carencias de verificación."""
    encontrados: list[dict] = []

    if not info["pasos"]:
        encontrados.append({
            "severidad": "Media", "area": "Ejecución",
            "titulo": "No se encontró pasos.json: no consta qué se ejecutó",
            "detalle": "Faltan estados, códigos de salida y logs de la orquestación.",
            "accion": "Ejecutar EjecutarVerificacion.ps1 en lugar de consolidar una carpeta vacía."})

    def agregar(severidad: str, area: str, titulo: str, detalle: str, accion: str) -> None:
        encontrados.append({"severidad": severidad, "area": area, "titulo": titulo,
                            "detalle": detalle, "accion": accion})

    for paso in info["pasos"]:
        if paso.get("estado") not in ("OK",):
            agregar("Alta", "Ejecución", f"Paso «{paso.get('nombre')}» no terminó bien",
                    f"estado={paso.get('estado')} código={paso.get('codigo')} "
                    f"duración={paso.get('duracion_s')} s · log={paso.get('log')}",
                    "Revisar la salida completa del log indicado.")

    junit = info["junit"]
    if junit["casos_fallidos"]:
        agregar("Alta", "Pruebas automáticas", f"{len(junit['casos_fallidos'])} prueba(s) de pytest fallan",
                "; ".join(f"{c['prueba']}: {acortar(c['mensaje'], 120)}"
                          for c in junit["casos_fallidos"][:5]),
                "Corregir la regresión antes de publicar.")
    elif junit["total"] == 0:
        agregar("Media", "Pruebas automáticas", "No se encontró junit.xml de pytest",
                "Sin resultado de la suite no se puede afirmar que el código esté sano.",
                "Ejecutar el perfil completo de la verificación.")

    cobertura = info["cobertura"]
    if cobertura["global_pct"] is not None and cobertura["global_pct"] < UMBRALES["cobertura_core_pct"]:
        agregar("Media", "Cobertura",
                f"Cobertura del núcleo {cobertura['global_pct']}% < {UMBRALES['cobertura_core_pct']}%",
                "Módulos por debajo del objetivo: " + ", ".join(
                    f"{m['archivo']} ({m['cobertura_pct']}%)" for m in cobertura["modulos"][:5]),
                "Añadir casos de borde en los módulos con menor cobertura.")

    if info["scipy"]:
        filas = info["scipy"].get("comparaciones", [])
        fallan = [f for f in filas if not f.get("pasa")]
        if fallan:
            agregar("Alta", "Cálculo", f"{len(fallan)} comparación(es) contra SciPy discrepan",
                    "; ".join(f"{f['distribucion']}/{f['operacion']} error="
                              + (f"{f['error_absoluto_maximo']:.3g}"
                                 if isinstance(f.get("error_absoluto_maximo"), (int, float)) else "n/d")
                              for f in fallan[:6]),
                    "Revisar el adaptador de la distribución indicada.")
    else:
        agregar("Media", "Cálculo", "No hay reporte de diferencias contra SciPy",
                "El script validar_contra_scipy.py no generó salida.",
                "Ejecutarlo con --salida y revisar los 121 cotejos.")

    for nombre, documento in (("Cálculo numérico", info["calculo"]),
                              ("Interfaz", info["ui_nativo"]),
                              ("Interfaz (offscreen)", info["ui_offscreen"])):
        if not documento:
            continue
        fallos = [r for r in documento.get("resultados", []) if r["estado"] == "FALLA"]
        if fallos:
            agregar("Alta", nombre, f"{len(fallos)} comprobación(es) fallan en {documento.get('herramienta')}",
                    "; ".join(f"{r['id']} → obtenido={acortar(r.get('obtenido'), 60)} "
                              f"esperado={acortar(r.get('esperado'), 60)}" for r in fallos[:8]),
                    "Ver la tabla detallada de esta sección.")
        omitidas = [r for r in documento.get("resultados", []) if r["estado"] == "OMITIDA"]
        if omitidas:
            agregar("Baja", nombre, f"{len(omitidas)} comprobación(es) omitidas",
                    "; ".join(r["id"] for r in omitidas[:10]),
                    "Confirmar que la omisión es esperada en este equipo (sin GUI, sin red, etc.).")

    # Rendimiento
    rendimiento = info["rendimiento"]
    if rendimiento:
        lentas = [m for m in rendimiento.get("metricas", [])
                  if "referencia SciPy" not in m["operacion"]
                  and (m.get("mediana_ms") or 0) > UMBRALES["operacion_core_ms"]]
        if lentas:
            agregar("Media", "Rendimiento",
                    f"{len(lentas)} operación(es) del núcleo superan {UMBRALES['operacion_core_ms'] / 1000:g} s",
                    "; ".join(f"{m['operacion']}: {m['mediana_ms']:.0f} ms" for m in lentas[:5]),
                    "Perfilar con cProfile; revisar tamaños de entrada usados.")
        factores = [m for m in rendimiento.get("metricas", []) if m.get("factor_sobre_referencia")]
        if factores:
            peor = max(factores, key=lambda m: m["factor_sobre_referencia"])
            if peor["factor_sobre_referencia"] > UMBRALES["factor_scipy"]:
                agregar("Media", "Rendimiento",
                        f"Sobrecoste {peor['factor_sobre_referencia']}× frente a SciPy",
                        f"{peor['operacion']}: {peor['mediana_ms']} ms vs {peor.get('referencia_ms')} ms",
                        "Evaluar si la validación de argumentos o la creación del modelo se puede amortizar.")
        memoria = rendimiento.get("memoria", {})
        if memoria.get("pico_mb") and memoria["pico_mb"] > UMBRALES["memoria_mb"]:
            agregar("Media", "Rendimiento", "Pico de memoria del proceso alto",
                    f"{memoria['pico_mb']} MB en benchmark del núcleo",
                    "Revisar tamaños de muestra usados en la simulación.")

    # UI
    for etiqueta, documento in (("Interfaz nativa", info["ui_nativo"]),
                                ("Interfaz offscreen", info["ui_offscreen"])):
        if not documento:
            continue
        # Si Qt no está disponible, ya se informa de la carencia una sola vez.
        sin_qt = any(r.get("id") == "ui.disponible" and r.get("estado") == "OMITIDA"
                     for r in documento.get("resultados", []))
        tiempos, capturas, extras = recopilar_metricas_ui(documento)
        for metrica in tiempos:
            operacion = metrica["operacion"]
            limite = None
            if operacion.startswith("arranque: VentanaPrincipal"):
                limite = UMBRALES["arranque_ventana_ms"]
            elif operacion.startswith("vista ") and "primer resultado" in operacion:
                limite = UMBRALES["vista_primera_ms"]
            elif operacion.startswith("exportar"):
                limite = UMBRALES["exportacion_ms"]
            if limite and (metrica.get("mediana_ms") or 0) > limite:
                agregar("Media", "Rendimiento UI",
                        f"{operacion} supera el umbral ({limite} ms)",
                        f"{metrica['mediana_ms']} ms en {etiqueta}",
                        "Revisar el cálculo asociado y el coste de Matplotlib/WebEngine.")
        for nombre, metrica in extras.get("contrastes", {}).items():
            if (metrica.get("min_ms") or 99) < UMBRALES["contraste_min"]:
                agregar("Alta", "Accesibilidad visual",
                        f"Contraste por debajo de WCAG AA en {nombre}",
                        f"mínimo {metrica.get('min_ms')}:1 · {metrica.get('notas')}",
                        "Ajustar los pares de color del QSS y volver a medir.")
        a11y = extras.get("accesibilidad") or {}
        if a11y and (a11y.get("obtenido") or 0) < UMBRALES["accesibilidad_nombres"]:
            agregar("Media", "Accesibilidad",
                    f"Nombres accesibles {a11y.get('obtenido')} < {UMBRALES['accesibilidad_nombres']}",
                    acortar(a11y.get("notas"), 300),
                    "Añadir setAccessibleName a los controles listados.")
        for captura in capturas:
            distancia = captura.get("distancia_linea_base")
            if distancia is not None and distancia > UMBRALES["distancia_visual"]:
                agregar("Baja", "Visual",
                        f"Cambio visual en {captura['archivo']} (distancia {distancia}/64)",
                        "Puede ser intencional (rediseño) o una regresión de estilo.",
                        "Comparar la captura con la línea base y aprobar o revertir.")
        if not capturas and not sin_qt:
            agregar("Media", etiqueta, "No se generaron capturas",
                    "Sin imágenes no hay evidencia visual.",
                    "Ejecutar con --plataforma native en un escritorio real.")

    if not info["ui_nativo"]:
        agregar("Media", "Interfaz", "No hay prueba visual en escritorio nativo",
                "Solo existe la ejecución offscreen (sin Chromium ni foco real del SO).",
                "Ejecutar el perfil «visual» en Windows/macOS/Linux con escritorio.")
    selftest = info["selftest"]
    if not selftest or not selftest.is_file():
        agregar("Media", "WebEngine", "No se ejecutó la autoprueba --self-test",
                "KaTeX, MathML, figura local y tema oscuro quedan sin verificar en Chromium real.",
                "Ejecutar python -m ampu --self-test --capture-theory <ruta.png>.")
    return encontrados


# --------------------------------------------------------------------------- #
# Reporte
# --------------------------------------------------------------------------- #
def construir_reporte(info: dict, encontrados: list[dict]) -> str:
    entorno = info.get("entorno", {})
    junit, cobertura = info["junit"], info["cobertura"]
    paso_por_nombre = {p.get("nombre"): p for p in info["pasos"]}
    severidades = {s: sum(1 for h in encontrados if h["severidad"] == s) for s in ("Alta", "Media", "Baja")}
    veredicto = veredicto_de(info, encontrados)
    lineas: list[str] = []
    a = lineas.append

    a("# Reporte de verificación · AmPu 3.0")
    a("")
    a(f"- **Generado:** {datetime.now().astimezone().isoformat(timespec='seconds')}")
    a(f"- **Carpeta del paquete:** `{info['carpeta']}`")
    a(f"- **Veredicto automático:** **{veredicto}** "
      f"({severidades['Alta']} hallazgos altos · {severidades['Media']} medios · {severidades['Baja']} bajos)")
    a("")
    a("> Este reporte lo produce la propia batería. No sustituye la revisión con lector de "
      "pantalla (NVDA/JAWS/VoiceOver) ni la prueba en macOS/Windows reales de los ejecutables.")
    a("")

    # --- entorno
    a("## @@. Entorno y versión verificada")
    a("")
    git = entorno.get("git", {})
    huella = entorno.get("huella_fuentes", {})
    a(md_tabla(["Dato", "Valor"], [
        ["SO", f"{entorno.get('so', 'desconocido')}"],
        ["Arquitectura / núcleos", f"{entorno.get('arquitectura', '?')} · {entorno.get('nucleos_logicos', '?')} lógicos"],
        ["Memoria instalada", fmt_numero(entorno.get("memoria_total_mb"), 0, " MB")],
        ["Python", f"{entorno.get('python', '?')} ({entorno.get('python_implementacion', '?')})"],
        ["AmPu", entorno.get("ampu", "?")],
        ["Bibliotecas", ", ".join(f"{k} {v}" for k, v in entorno.get("librerias", {}).items())],
        ["Commit", f"{git.get('commit', 'n/d')[:12]} · rama {git.get('rama', 'n/d')}"],
        ["Estado del árbol", acortar(git.get("estado", "n/d"), 200)],
        ["Huella de fuentes (SHA-256)", (huella.get("sha256_fuentes") or "n/d")[:32] + "…"],
        ["Pantallas / DPI", "; ".join(
            f"{p.get('nombre')} {p.get('tamano_px')} {p.get('dpi_logico')} dpi ×{p.get('escala')}"
            for p in entorno.get("pantalla", {}).get("pantallas", [])) or "no leídas"],
        ["Fuente del sistema", entorno.get("pantalla", {}).get("fuente_sistema", "n/d")],
        ["Plataforma Qt", entorno.get("pantalla", {}).get("plataforma_qt", "n/d")],
    ]))
    a("")

    # --- ejecución
    a("## @@. Ejecución de la batería")
    a("")
    a(md_tabla(["Paso", "Estado", "Código", "Duración", "Log"], [
        [p.get("nombre"), estado(p.get("estado")), p.get("codigo"),
         f"{p.get('duracion_s')} s", f"`{Path(str(p.get('log'))).name}`"]
        for p in info["pasos"]
    ]))
    a("")

    # --- resumen de áreas
    areas = {
        "Cálculo numérico": info["calculo"],
        "Interfaz y accesibilidad": info["ui_nativo"] or info["ui_offscreen"],
        "Rendimiento del núcleo": info["rendimiento"],
    }
    filas = []
    for nombre, documento in areas.items():
        if not documento:
            filas.append([nombre, "no ejecutado", "—", "—", "—"])
            continue
        resumen = documento.get("resumen", {})
        filas.append([nombre, estado(resumen.get("veredicto")),
                      resumen.get("pasan", 0), resumen.get("fallan", 0),
                      resumen.get("omitidas", 0)])
    if info["scipy"]:
        comparaciones = info["scipy"].get("comparaciones", [])
        filas.append(["Contraste independiente con SciPy",
                      "OK" if all(c.get("pasa") for c in comparaciones) else "**FALLA**",
                      sum(1 for c in comparaciones if c.get("pasa")), 
                      sum(1 for c in comparaciones if not c.get("pasa")), 0])
    if junit["total"]:
        filas.append(["Suite pytest", "OK" if not junit["casos_fallidos"] else "**FALLA**",
                      junit["total"] - junit["fallos"] - junit["errores"] - junit["omitidas"],
                      junit["fallos"] + junit["errores"], junit["omitidas"]])
    a("## @@. Resultado por área")
    a("")
    a(md_tabla(["Área", "Veredicto", "Pasan", "Fallan", "Omitidas"], filas))
    a("")

    # --- pruebas automáticas y cobertura
    a("## @@. Pruebas automáticas y cobertura")
    a("")
    if junit["total"]:
        a(f"- Casos ejecutados: **{junit['total']}** en {junit['tiempo_s']:.1f} s "
          f"({junit['fallos']} fallos, {junit['errores']} errores, {junit['omitidas']} omitidas).")
    else:
        a("- No se encontró `junit.xml`.")
    if cobertura["global_pct"] is not None:
        a(f"- Cobertura del núcleo con ramas: **{cobertura['global_pct']}%** "
          f"(objetivo ≥ {UMBRALES['cobertura_core_pct']}%).")
        a("")
        a("Módulos con menor cobertura de líneas:")
        a("")
        a(md_tabla(["Archivo", "Líneas", "Cobertura", "Ramas"], [
            [m["archivo"], m["lineas"], fmt_numero(m["cobertura_pct"], 1, "%"),
             fmt_numero(m["ramas_pct"], 1, "%") if m["ramas_pct"] is not None else "—"]
            for m in [fila for fila in cobertura["modulos"] if fila["lineas"] > 0][:8]
        ]))
    else:
        a("- No se encontró `coverage.xml`.")
    if junit["casos_fallidos"]:
        a("")
        a("**Pruebas fallidas**")
        a("")
        a(md_tabla(["Prueba", "Tipo", "Mensaje"],
                   [[acortar(c["prueba"], 80), c["tipo"], acortar(c["mensaje"], 220)]
                    for c in junit["casos_fallidos"]]))
    if junit["omitidos"]:
        a("")
        a("**Pruebas omitidas** (confirmar que es esperado en este equipo)")
        a("")
        a(md_tabla(["Prueba", "Motivo"], [[acortar(o["prueba"], 90), acortar(o["motivo"], 160)]
                                          for o in junit["omitidos"]]))
    a("")

    # --- cálculo
    calculo = info["calculo"]
    a("## @@. Cálculo: distribuciones, muestreo, inferencia y simulación")
    a("")
    if calculo:
        resumen = calculo["resumen"]
        a(f"**{resumen['pasan']}/{resumen['total']} comprobaciones pasan** "
          f"({resumen['fallan']} fallan, {resumen['omitidas']} omitidas) en {resumen['duracion_s']} s.")
        a("")
        por_categoria: dict[str, dict] = {}
        for resultado in calculo.get("resultados", []):
            categoria = resultado["categoria"]
            registro = por_categoria.setdefault(categoria, {"total": 0, "pasan": 0, "fallan": 0})
            registro["total"] += 1
            if resultado["estado"] == "PASA":
                registro["pasan"] += 1
            elif resultado["estado"] == "FALLA":
                registro["fallan"] += 1
        a(md_tabla(["Categoría", "Comprobaciones", "Pasan", "Fallan"], [
            [categoria, v["total"], v["pasan"], v["fallan"]]
            for categoria, v in sorted(por_categoria.items())
        ]))
        fallos = [r for r in calculo.get("resultados", []) if r["estado"] == "FALLA"]
        if fallos:
            a("### Discrepancias de cálculo")
            a("")
            a(md_tabla(["ID", "Descripción", "Obtenido", "Esperado", "Tolerancia", "Notas"], [
                [f"`{r['id']}`", acortar(r["descripcion"], 90), acortar(r["obtenido"], 60),
                 acortar(r["esperado"], 60), acortar(r["tolerancia"], 60), acortar(r["notas"], 80)]
                for r in fallos
            ]))
        a("### Cobertura funcional verificada")
        a("")
        ids = [r["id"] for r in calculo.get("resultados", [])]
        distribuciones = {i.split(".")[1] for i in ids
                          if i.startswith("dist.") and i.count(".") >= 2}
        a(md_tabla(["Elemento", "Cubiertos", "Detalle"], [
            ["Distribuciones univariantes", len(distribuciones),
             ", ".join(sorted(distribuciones))[:400] + ("…" if len(distribuciones) > 20 else "")],
            ["Modelos multivariados", 3, "multinomial · Dirichlet · normal bivariada"],
            ["Diseños de muestreo", 7, "finito, infinito, sistemático, proporcional, Neyman, óptimo, conglomerados"],
            ["Técnicas de inferencia", 16,
             "z/t una y dos muestras, z de proporciones (1 y 2), χ² bondad e independencia, ANOVA, Pearson, Spearman, regresión simple y múltiple, Mann–Whitney, Wilcoxon, Kruskal–Wallis"],
            ["Exportadores", 4, "XLSX · CSV · PNG · PDF (+ sesión JSON)"],
        ]))
    else:
        a("_No se ejecutó `pruebas_calculo.py`._")
    a("")

    if info["scipy"]:
        comparaciones = info["scipy"].get("comparaciones", [])
        a("## @@. Contraste independiente con SciPy")
        a("")
        a(f"{sum(1 for c in comparaciones if c.get('pasa'))}/{len(comparaciones)} comparaciones "
          f"superadas con tolerancia relativa {info['scipy'].get('tolerancia_relativa')}.")
        a("")
        errores = sorted([c for c in comparaciones if c.get("error_absoluto_maximo") is not None],
                         key=lambda c: c["error_absoluto_maximo"], reverse=True)[:6]
        a(md_tabla(["Distribución", "Operación", "Error absoluto máximo", "Estado"], [
            [c["distribucion"], c["operacion"], f"{c['error_absoluto_maximo']:.3e}", estado("PASA" if c["pasa"] else "FALLA")]
            for c in errores
        ]))
        a("")

    # --- rendimiento
    rendimiento = info["rendimiento"]
    a("## @@. Rendimiento")
    a("")
    if rendimiento:
        metricas = [m for m in rendimiento.get("metricas", []) if "referencia SciPy" not in m["operacion"]]
        a(f"Escala **{rendimiento.get('opciones', {}).get('escala')}**, "
          f"{rendimiento.get('opciones', {}).get('repeticiones')} repeticiones por operación. "
          f"Memoria del proceso: {fmt_numero(rendimiento.get('memoria', {}).get('pico_mb'), 1, ' MB')} de pico.")
        a("")
        a("### Operaciones más costosas del núcleo")
        a("")
        top = sorted(metricas, key=lambda m: m.get("mediana_ms") or 0, reverse=True)[:20]
        a(md_tabla(["Operación", "Categoría", "Mediana ms", "p95 ms", "Ops/s"], [
            [m["operacion"], m["categoria"], fmt_numero(m.get("mediana_ms")), fmt_numero(m.get("p95_ms")),
             fmt_numero(m.get("ops_por_segundo"), 0)]
            for m in top
        ]))
        con_referencia = [m for m in rendimiento.get("metricas", []) if m.get("factor_sobre_referencia")]
        if con_referencia:
            a("### Sobrecoste frente a SciPy directo")
            a("")
            a(md_tabla(["Operación", "AmPu ms", "SciPy ms", "Factor"], [
                [m["operacion"], fmt_numero(m.get("mediana_ms")), fmt_numero(m.get("referencia_ms")),
                 f"{m['factor_sobre_referencia']}×"]
                for m in sorted(con_referencia, key=lambda m: m["factor_sobre_referencia"], reverse=True)
            ]))
    else:
        a("_No se ejecutó `benchmark_calculo.py`._")
    a("")

    # --- UI
    for etiqueta, documento in (("nativa", info["ui_nativo"]), ("offscreen", info["ui_offscreen"])):
        if not documento:
            continue
        tiempos, capturas, extras = recopilar_metricas_ui(documento)
        a(f"## @@. Interfaz ({etiqueta})")
        a("")
        resumen = documento.get("resumen", {})
        opciones = documento.get("opciones", {})
        a(f"{resumen.get('pasan')}/{resumen.get('total')} comprobaciones pasan "
          f"({resumen.get('fallan')} fallan, {resumen.get('omitidas', 0)} omitidas) · "
          f"plataforma Qt `{opciones.get('plataforma_qt', 'n/d')}` · "
          f"tamaño base {opciones.get('tamano', 'n/d')} · temas `{opciones.get('temas', 'n/d')}`.")
        a("")
        if resumen.get("pasan", 0) == 0 and resumen.get("omitidas", 0) == resumen.get("total", 0):
            a("**La interfaz no se pudo verificar en este equipo** (falta PySide6 o las "
              "bibliotecas gráficas nativas). Es una omisión declarada, no una aprobación: "
              "hay que repetir esta parte en un escritorio con pantalla.")
            a("")
        a("### Tiempos de interfaz")
        a("")
        a(md_tabla(["Operación", "Mediana ms", "Máx ms"], [
            [m["operacion"], fmt_numero(m.get("mediana_ms")), fmt_numero(m.get("max_ms"))]
            for m in tiempos
        ]))
        if extras.get("contrastes"):
            a("### Contraste WCAG medido en píxeles renderizados")
            a("")
            a(md_tabla(["Tema", "Mínimo", "Mediana", "Máximo", "Textos < 4.5:1"], [
                [m["operacion"], fmt_numero(m.get("min_ms")), fmt_numero(m.get("mediana_ms")),
                 fmt_numero(m.get("max_ms")), m.get("notas")]
                for m in extras["contrastes"].values()
            ]))
        a11y = extras.get("accesibilidad") or {}
        if a11y:
            a("")
            a(f"- Nombres accesibles en controles visibles: **{a11y.get('obtenido')}** "
              f"(objetivo ≥ {UMBRALES['accesibilidad_nombres']}). {acortar(a11y.get('notas'), 300)}")
        if capturas:
            a("")
            a("### Capturas reales")
            a("")
            a(f"{len(capturas)} imágenes en `capturas/`. Huella `aHash` de 64 bits: sirve para "
              "detectar cambios de estilo entre ejecuciones (no es un hash criptográfico).")
            a("")
            a(md_tabla(["Archivo", "Tema", "Vista", "Zoom", "px", "Bytes", "aHash", "Luminancia", "Δ línea base"], [
                [c["archivo"], c["tema"], c["vista"], c["zoom"],
                 "×".join(map(str, c.get("px", []))), fmt_numero(c.get("bytes"), 0),
                 f"`{c.get('ahash', '')}`", fmt_numero(c.get("luminancia_media"), 3),
                 c.get("distancia_linea_base", "—")]
                for c in capturas
            ]))
        fallos = [r for r in documento.get("resultados", []) if r["estado"] == "FALLA"]
        if fallos:
            a("### Comprobaciones de interfaz que fallan")
            a("")
            a(md_tabla(["ID", "Descripción", "Obtenido", "Esperado", "Notas"], [
                [f"`{r['id']}`", acortar(r["descripcion"], 90), acortar(r["obtenido"], 90),
                 acortar(r["esperado"], 60), acortar(r["notas"], 120)]
                for r in fallos
            ]))
        a("")

    # --- selftest
    a("## @@. Autoprueba estricta de QtWebEngine")
    a("")
    if info["selftest"] and info["selftest"].is_file():
        contenido = info["selftest"].read_text(encoding="utf-8-sig", errors="replace").strip()
        a("```text")
        a(contenido[-2000:] if contenido else "(vacío)")
        a("```")
    else:
        a("_No se ejecutó `--self-test`._")
    a("")

    # --- hallazgos
    a("## @@. Hallazgos priorizados")
    a("")
    if encontrados:
        a(md_tabla(["#", "Severidad", "Área", "Hallazgo", "Evidencia", "Acción sugerida"], [
            [i + 1, h["severidad"], h["area"], h["titulo"], acortar(h["detalle"], 260),
             acortar(h["accion"], 160)]
            for i, h in enumerate(sorted(encontrados,
                                         key=lambda h: {"Alta": 0, "Media": 1, "Baja": 2}[h["severidad"]]))
        ]))
    else:
        a("_Sin hallazgos: todas las comprobaciones ejecutadas pasan._")
    a("")

    # --- pendientes manuales
    a("## @@. Lo que esta batería no puede certificar")
    a("")
    a("- Lectura con **NVDA, JAWS o VoiceOver**: nombres, orden de foco, anuncios de resultados "
      "y MathML se comprueban a mano con la matriz de `docs/AUDITORIA_UI_UX_IX.md`.")
    a("- **macOS y Windows reales**: esta ejecución es de un solo sistema; los menús nativos "
      "(roles App), el escalado por DPI y el tema del SO deben repetirse en cada destino.")
    a("- **Ejecutables PyInstaller**: `scripts/build_exe.py --gui-self-test` debe correr en cada "
      "SO; aquí solo se verifica el árbol de Python.")
    a("- **Rendimiento absoluto**: los números dependen del equipo. Comparar contra la misma "
      "máquina y la misma escala/repeticiones, nunca contra otro reporte de otro hardware.")
    a("- **Precisión estadística de métodos Monte Carlo**: las pruebas comprueban tolerancias "
      "razonables, no una certificación metodológica.")
    a("")

    # --- entrega
    a("## @@. Cómo entregar este paquete")
    a("")
    a("1. Envía `REPORTE.md` (texto) y, si es posible, el ZIP completo: incluye capturas, "
      "exportaciones y logs, que son la evidencia que no cabe en el Markdown.")
    a("2. Indica el perfil usado (`rapido`, `completo`, `visual`, `rendimiento` o `calculo`) y "
      "si la plataforma de interfaz fue `native` u `offscreen`.")
    a("3. Adjunta `datos/resumen.json` si solo se necesita el análisis automático: contiene los "
      "números clave sin las tablas largas.")
    a("")
    a("---")
    a("")
    a(f"_Paquete generado por `verificacion/` · Python {platform.python_version()} · "
      f"{datetime.now().astimezone().isoformat(timespec='seconds')}_")
    numerado, contador = [], 0
    for linea in lineas:
        if linea.startswith("## @@."):
            contador += 1
            numerado.append(linea.replace("## @@.", f"## {contador}."))
        else:
            numerado.append(linea)
    return "\n".join(numerado)


def resumen_maquina(info: dict, encontrados: list[dict]) -> dict:
    junit, cobertura = info["junit"], info["cobertura"]
    ui = info["ui_nativo"] or info["ui_offscreen"] or {}
    rendimiento = info["rendimiento"] or {}
    return {
        "herramienta": "resumen_verificacion_ampu",
        "version_esquema": 1,
        "generado": datetime.now().astimezone().isoformat(timespec="seconds"),
        "carpeta": info["carpeta"],
        "veredicto": veredicto_de(info, encontrados),
        "hallazgos": {s: sum(1 for h in encontrados if h["severidad"] == s)
                      for s in ("Alta", "Media", "Baja")},
        "pasos": [{"nombre": p.get("nombre"), "estado": p.get("estado"),
                   "codigo": p.get("codigo"), "duracion_s": p.get("duracion_s")}
                  for p in info["pasos"]],
        "pytest": {"total": junit["total"], "fallos": junit["fallos"],
                   "errores": junit["errores"], "omitidas": junit["omitidas"],
                   "casos_fallidos": junit["casos_fallidos"]},
        "cobertura_pct": cobertura["global_pct"],
        "scipy": {"comparaciones": len((info["scipy"] or {}).get("comparaciones", [])),
                  "fallan": sum(1 for c in (info["scipy"] or {}).get("comparaciones", [])
                                if not c.get("pasa"))} if info["scipy"] else None,
        "calculo": (info["calculo"] or {}).get("resumen"),
        "interfaz": ui.get("resumen"),
        "rendimiento": {"metricas": len(rendimiento.get("metricas", [])),
                        "memoria_pico_mb": rendimiento.get("memoria", {}).get("pico_mb"),
                        "peores": sorted(
                            [{"operacion": m["operacion"], "mediana_ms": m.get("mediana_ms")}
                             for m in rendimiento.get("metricas", [])
                             if "referencia SciPy" not in m["operacion"]],
                            key=lambda m: m.get("mediana_ms") or 0, reverse=True)[:8]},
        "capturas": len(ui.get("capturas", [])),
        "entorno": {k: v for k, v in (info.get("entorno") or {}).items()
                    if k in ("so", "python", "ampu", "nucleos_logicos", "memoria_total_mb",
                             "librerias", "git", "huella_fuentes")},
        "hallazgos_detalle": encontrados,
        "umbrales": UMBRALES,
    }


def empaquetar(carpeta: Path) -> Path | None:
    destino = carpeta / "reporte.zip"
    try:
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as archivo:
            for ruta in sorted(carpeta.rglob("*")):
                if ruta == destino or not ruta.is_file():
                    continue
                archivo.write(ruta, ruta.relative_to(carpeta).as_posix())
        return destino
    except Exception as exc:
        print(f"Aviso: no se pudo crear el ZIP: {exc}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolida el reporte de verificación de AmPu 3.0")
    parser.add_argument("--carpeta", type=Path, required=True, help="Salida de EjecutarVerificacion.ps1")
    parser.add_argument("--sin-zip", action="store_true")
    args = parser.parse_args()

    if not args.carpeta.is_dir():
        print(f"No existe la carpeta {args.carpeta}", file=sys.stderr)
        return 2
    info = evaluar(args.carpeta)
    encontrados = hallazgos(info)
    (args.carpeta / "REPORTE.md").write_text(construir_reporte(info, encontrados), encoding="utf-8")
    (args.carpeta / "resumen.json").write_text(
        json.dumps(resumen_maquina(info, encontrados), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    if not args.sin_zip:
        zip_ruta = empaquetar(args.carpeta)
        if zip_ruta:
            print(f"Paquete comprimido: {zip_ruta}")
    print(f"Reporte: {args.carpeta / 'REPORTE.md'}")
    print(f"Resumen: {args.carpeta / 'resumen.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
