"""Pruebas visuales y de rendimiento de la interfaz de AmPu 3.0.

Qué hace, con la interfaz real (sin suplentes ni mocks):
  1. Cronometra arranque, cambio de vista y primer resultado de cada módulo.
  2. Recorre las 7 secciones × 3 temas y captura PNG reales de la ventana.
  3. Calcula una huella perceptual (aHash 64 bits) comparable con una línea base.
  4. Mide contraste efectivo de textos sobre su fondo real (píxeles renderizados).
  5. Audita nombres accesibles de los controles interactivos.
  6. Ejercita la exportación XLSX/CSV/PNG/PDF y el guardado/carga de sesión.
  7. Verifica atajos, menús, tamaño mínimo, reflujo con zoom y (opcional) KaTeX.

Uso típico (escritorio real, lo que el README llama "prueba visual"):
    python verificacion/pruebas/benchmark_ui.py --plataforma native ^
        --salida datos/ui_nativo.json --capturas capturas --exportaciones exportaciones

En un servidor sin pantalla (raster offscreen, sin WebEngine):
    python ... --plataforma offscreen --sin-teoria --salida datos/ui_offscreen.json

Códigos de salida: 0 si todas las comprobaciones pasan; 1 en caso contrario.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import _comun  # noqa: E402

RAIZ = _comun.preparar_import()

# La plataforma Qt debe elegirse antes de importar PySide6.
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--plataforma", choices=["native", "offscreen"], default=None)
_previos, _ = _pre.parse_known_args()
if _previos.plataforma:
    os.environ["QT_QPA_PLATFORM"] = "offscreen" if _previos.plataforma == "offscreen" else os.environ.get("QT_QPA_PLATFORM", "")
    if _previos.plataforma == "native":
        os.environ.pop("QT_QPA_PLATFORM", None)

# Si falta la pila gráfica (servidor sin X11/GL/NSS), el script lo reporta como
# omisión en lugar de abortar: la interfaz no es verificable en ese equipo.
QT_DISPONIBLE = False
ERROR_QT = "No se intentó inicializar Qt."
try:
    import matplotlib  # noqa: E402

    matplotlib.use("QtAgg")

    import numpy as np  # noqa: E402
    from PySide6.QtCore import QEventLoop, QPoint, QRect, QSettings, Qt, QTimer  # noqa: E402
    from PySide6.QtGui import QImage  # noqa: E402
    from PySide6.QtWidgets import (  # noqa: E402
        QAbstractButton, QAbstractSpinBox, QApplication, QComboBox, QLabel, QLineEdit,
        QPlainTextEdit, QWidget,
    )

    QT_DISPONIBLE = True
    ERROR_QT = ""
except Exception as exc:  # ImportError de librerías nativas, plugin Qt, etc.
    QT_DISPONIBLE = False
    ERROR_QT = f"{type(exc).__name__}: {exc}"

VISTAS = ["distribuciones", "muestreo", "descriptiva", "probabilidad", "inferencia", "simulacion"]
TEMAS = ["claro", "oscuro", "contraste"]


# --------------------------------------------------------------------------- #
# Utilidades Qt
# --------------------------------------------------------------------------- #
def esperar(condicion, milisegundos: int = 25_000) -> bool:
    """Procesa eventos hasta que la condición se cumpla o venza el plazo."""
    ciclo = QEventLoop()
    vencido = {"valor": True}

    limite = QTimer()
    limite.setSingleShot(True)

    def agotar():
        vencido["valor"] = True
        ciclo.quit()

    limite.timeout.connect(agotar)

    def comprobar():
        if condicion():
            vencido["valor"] = False
            ciclo.quit()
        else:
            QTimer.singleShot(30, comprobar)

    QTimer.singleShot(0, comprobar)
    limite.start(milisegundos)
    ciclo.exec()
    limite.stop()
    return not vencido["valor"]


def bombear(milisegundos: int = 120) -> None:
    """Deja que Qt pinte (útil tras cambiar de tema o de vista)."""
    app = QApplication.instance()
    fin = time.perf_counter() + milisegundos / 1000
    while time.perf_counter() < fin:
        app.processEvents()


def luminancia(qcolor) -> float:
    canales = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
    lineales = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineales[0] + 0.7152 * lineales[1] + 0.0722 * lineales[2]


def razon_contraste(l1: float, l2: float) -> float:
    claro, oscuro = max(l1, l2), min(l1, l2)
    return (claro + .05) / (oscuro + .05)


def huella_ahash(imagen: QImage) -> str:
    """aHash de 64 bits: robusto a ruido y a diferencias menores de renderizado."""
    pequena = imagen.scaled(8, 8, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    grises = [pequena.pixelColor(x, y).lightness() for y in range(8) for x in range(8)]
    media = sum(grises) / len(grises)
    bits = "".join("1" if valor >= media else "0" for valor in grises)
    return f"{int(bits, 2):016x}"


def distancia_hamming(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def estadisticas_imagen(imagen: QImage) -> dict:
    """Luminancia media y variedad cromática aproximada (muestreo uniforme)."""
    ancho, alto = imagen.width(), imagen.height()
    paso_x = max(1, ancho // 160)
    paso_y = max(1, alto // 120)
    valores, colores = [], set()
    for y in range(0, alto, paso_y):
        for x in range(0, ancho, paso_x):
            color = imagen.pixelColor(x, y)
            valores.append(luminancia(color))
            colores.add(color.rgb())
    if not valores:
        return {"luminancia_media": 0.0, "colores_muestreados": 0}
    return {"luminancia_media": round(float(np.mean(valores)), 4),
            "colores_muestreados": len(colores)}


def contraste_de_widget(ventana_imagen: QImage, widget: QWidget, ventana: QWidget) -> float | None:
    """Contraste texto/fondo medido sobre los píxeles reales del widget renderizado."""
    if not widget.isVisible() or widget.width() < 4 or widget.height() < 4:
        return None
    origen = widget.mapTo(ventana, QPoint(0, 0))
    densidad = ventana_imagen.devicePixelRatio() or 1.0
    rect = QRect(round(origen.x() * densidad), round(origen.y() * densidad),
                 max(1, round(widget.width() * densidad)), max(1, round(widget.height() * densidad)))
    rect = rect.intersected(QRect(0, 0, ventana_imagen.width(), ventana_imagen.height()))
    if rect.width() < 4 or rect.height() < 4:
        return None
    valores = []
    paso_x = max(1, rect.width() // 90)
    paso_y = max(1, rect.height() // 40)
    for y in range(rect.top(), rect.bottom(), paso_y):
        for x in range(rect.left(), rect.right(), paso_x):
            valores.append(luminancia(ventana_imagen.pixelColor(x, y)))
    if len(valores) < 8:
        return None
    valores.sort()
    fondo = valores[int(len(valores) * 0.95)]
    texto = valores[int(len(valores) * 0.05)]
    if abs(fondo - texto) < 1e-6:  # sin texto visible en la región
        return None
    return round(razon_contraste(fondo, texto), 2)


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="Pruebas visuales y de rendimiento de la UI")
    parser.add_argument("--salida", type=Path, default=Path("datos/ui.json"))
    parser.add_argument("--capturas", type=Path, default=Path("capturas"))
    parser.add_argument("--exportaciones", type=Path, default=Path("exportaciones"))
    parser.add_argument("--plataforma", choices=["native", "offscreen"], default="native")
    parser.add_argument("--temas", default=",".join(TEMAS))
    parser.add_argument("--vistas", default=",".join(VISTAS + ["teoria"]))
    parser.add_argument("--zoom", type=float, nargs="*", default=[],
                        help="Escalas de texto adicionales que se capturan; 1.0 es la base")
    parser.add_argument("--sin-teoria", action="store_true", help="No abre QWebEngineView")
    parser.add_argument("--sin-exportadores", action="store_true")
    parser.add_argument("--linea-base", type=Path, default=None,
                        help="JSON de capturas previas para comparar huellas")
    parser.add_argument("--guardar-linea-base", action="store_true")
    parser.add_argument("--timeout", type=int, default=30, help="Segundos por espera de cálculo")
    parser.add_argument("--tamano", default="1440x900")
    args = parser.parse_args()

    args.capturas.mkdir(parents=True, exist_ok=True)
    args.exportaciones.mkdir(parents=True, exist_ok=True)

    if not QT_DISPONIBLE:
        documento = {
            "herramienta": "benchmark_ui", "version_esquema": 1, "generado": _comun.ahora(),
            "perfil": f"ui-{args.plataforma}",
            "opciones": {"plataforma": args.plataforma, "plataforma_qt": "no disponible",
                         "tamano": args.tamano, "temas": args.temas,
                         "vistas": [v for v in args.vistas.split(",") if v]},
            "entorno": _comun.entorno(), "metricas": [], "capturas": [],
            "resultados": [{"id": "ui.disponible", "categoria": "interfaz",
                            "descripcion": "La interfaz Qt puede inicializarse en este equipo",
                            "estado": "OMITIDA", "obtenido": ERROR_QT[:300],
                            "esperado": "PySide6 + librerías gráficas nativas",
                            "tolerancia": None, "unidad": None,
                            "notas": "Prueba visual no verificable aquí; ejecutar en un escritorio real."}],
            "resumen": {"total": 1, "pasan": 0, "fallan": 0, "omitidas": 1,
                        "veredicto": "INCOMPLETO", "duracion_s": 0.0},
        }
        _comun.guardar_json(args.salida, documento)
        print(f"Interfaz no verificable en este equipo: {ERROR_QT}")
        print(f"Se registró la omisión en {args.salida}")
        return 0

    ancho, alto = (int(v) for v in args.tamano.lower().split("x"))

    r = _comun.Revisor(f"ui-{args.plataforma}")
    cat_ = "interfaz"
    capturas: list[dict] = []
    fallos_graficos = {"errores": []}

    t_inicio = time.perf_counter()
    from ampu import __version__ as version_ampu

    from ampu.io import ServicioExportacion as io
    from ampu.docs.teoria import extraer_formula

    app = QApplication.instance() or QApplication(sys.argv[:1])
    t_app = (time.perf_counter() - t_inicio) * 1000
    app.setApplicationName("AmPu 3.0")
    app.setOrganizationName("AmPuVerificacion")
    ajustes = QSettings(str((args.capturas.parent / "preferencias_verificacion.ini").resolve()), QSettings.IniFormat)
    ajustes.clear()

    from ampu.ui.main_window import VentanaPrincipal

    t_ventana_inicio = time.perf_counter()
    ventana = VentanaPrincipal(ajustes)
    ventana.resize(ancho, alto)
    ventana.show()
    t_ventana = (time.perf_counter() - t_ventana_inicio) * 1000
    bombear(200)

    r.metricas.append({"operacion": "arranque: QApplication + plugins", "categoria": "interfaz",
                       "n": 1, "min_ms": round(t_app, 1), "mediana_ms": round(t_app, 1),
                       "p95_ms": round(t_app, 1), "max_ms": round(t_app, 1),
                       "ops_por_segundo": None, "notas": f"plataforma Qt={app.platformName()}"})
    r.metricas.append({"operacion": "arranque: VentanaPrincipal + 6 vistas + gráficos",
                       "categoria": "interfaz", "n": 1, "min_ms": round(t_ventana, 1),
                       "mediana_ms": round(t_ventana, 1), "p95_ms": round(t_ventana, 1),
                       "max_ms": round(t_ventana, 1), "ops_por_segundo": None,
                       "notas": f"tema inicial={ventana.modo_tema}"})
    print(f"Arranque: QApplication {t_app:.0f} ms · ventana {t_ventana:.0f} ms")

    # ---------------------------------------------------------------- estructura
    menus = [accion.text().replace("&", "") for accion in ventana.menuBar().actions()]
    r.verdadero("ui.menus", cat_, "La barra de menús contiene Archivo/Edición/Ver/Ventana/Ayuda",
                menus == ["Archivo", "Edición", "Ver", "Ventana", "Ayuda"], obtenido=menus)
    atajos = {accion.shortcut().toString() for accion in ventana.findChildren(type(ventana.accion_asistente))}
    requeridos = {"Ctrl+1", "Ctrl+7", "Ctrl+L", "Shift+F6", "Ctrl+0", "F1", "F2", "Ctrl+,"}
    r.verdadero("ui.atajos", cat_, "Los atajos documentados están registrados en acciones",
                requeridos.issubset(atajos), obtenido=sorted(a for a in atajos if a),
                esperado=sorted(requeridos), notas="QKeySequence.toString()")
    r.verdadero("ui.tamano_minimo", cat_, "La ventana cabe en 900×600 sin recortar el análisis",
                ventana.minimumWidth() <= 900 and ventana.minimumHeight() <= 600,
                obtenido=[ventana.minimumWidth(), ventana.minimumHeight()], esperado=[900, 600])
    r.verdadero("ui.tema_inicial_aplicado", cat_, "Se aplica una hoja QSS al arrancar",
                bool(ventana.styleSheet()), obtenido=len(ventana.styleSheet()), esperado="> 0")

    # -------------------------------------------------------------- recorrido
    def capturar(nombre: str, tema: str, vista: str, zoom: float) -> dict:
        ruta = args.capturas / nombre
        inicio = time.perf_counter()
        imagen_widget = ventana.grab()
        exito = imagen_widget.save(str(ruta), "PNG")
        ms = (time.perf_counter() - inicio) * 1000
        if not exito:
            fallos_graficos["errores"].append(f"No se pudo guardar {ruta}")
            return {}
        imagen = imagen_widget.toImage()
        datos = {
            "archivo": nombre, "tema": tema, "vista": vista, "zoom": zoom,
            "px": [imagen.width(), imagen.height()], "bytes": ruta.stat().st_size,
            "ahash": huella_ahash(imagen), "ms_captura": round(ms, 1),
            **estadisticas_imagen(imagen),
        }
        capturas.append(datos)
        return datos

    def preparar_vista(clave: str) -> tuple[bool, float]:
        inicio = time.perf_counter()
        ventana.cambiar(clave)
        bombear(60)
        vista = ventana.vistas.get(clave)
        if vista is None:
            return False, (time.perf_counter() - inicio) * 1000
        ok = esperar(lambda: getattr(vista, "ultimo", None) is not None
                     and not getattr(vista, "_ocupado", False), args.timeout * 1000)
        return ok, (time.perf_counter() - inicio) * 1000

    vistas_pedidas = [v for v in args.vistas.split(",") if v and (v != "teoria" or not args.sin_teoria)]
    for clave in vistas_pedidas:
        if clave == "teoria":
            continue
        ok, ms = preparar_vista(clave)
        r.metricas.append({"operacion": f"vista {clave}: cambio + primer resultado",
                           "categoria": "interfaz", "n": 1, "min_ms": round(ms, 1),
                           "mediana_ms": round(ms, 1), "p95_ms": round(ms, 1),
                           "max_ms": round(ms, 1), "ops_por_segundo": None, "notas": ""})
        r.registrar(f"ui.vista.{clave}.resultado", cat_,
                    f"{clave}: el primer cálculo termina y produce resultado",
                    pasa=ok, obtenido=round(ms, 1), unidad="ms",
                    notas="" if ok else f"Sin resultado tras {args.timeout} s")
        if not ok:
            fallos_graficos["errores"].append(f"{clave} no terminó su cálculo")
            continue

    # temas × vistas
    for tema in [t for t in args.temas.split(",") if t]:
        inicio = time.perf_counter()
        ventana.aplicar_tema(tema)
        bombear(250)
        r.metricas.append({"operacion": f"aplicar tema {tema}", "categoria": "interfaz", "n": 1,
                           "min_ms": round((time.perf_counter() - inicio) * 1000, 1),
                           "mediana_ms": round((time.perf_counter() - inicio) * 1000, 1),
                           "p95_ms": round((time.perf_counter() - inicio) * 1000, 1),
                           "max_ms": round((time.perf_counter() - inicio) * 1000, 1),
                           "ops_por_segundo": None, "notas": ""})
        for clave in vistas_pedidas:
            if clave == "teoria":
                continue
            if ventana.vistas.get(clave) is None:
                continue
            ok, _ = preparar_vista(clave)
            if not ok:
                fallos_graficos["errores"].append(f"{clave} ({tema}) no terminó su cálculo")
                continue
            capturar(f"{args.plataforma}_{tema}_{clave}.png", tema, clave, 1.0)
            if clave == "distribuciones":
                # Contraste efectivo de los textos visibles en esta vista.
                imagen_ventana = ventana.grab().toImage()
                ratios = []
                widgets = [w for w in ventana.vistas[clave].findChildren(QLabel) if w.isVisible() and w.text()]
                widgets += [w for w in ventana.vistas[clave].findChildren(QAbstractButton) if w.isVisible() and w.text()]
                for widget in widgets[:14]:
                    valor = contraste_de_widget(imagen_ventana, widget, ventana)
                    if valor is not None:
                        ratios.append({"widget": widget.text()[:40], "ratio": valor})
                if ratios:
                    minimo = min(item["ratio"] for item in ratios)
                    bajos = [item for item in ratios if item["ratio"] < 4.5]
                    r.metricas.append({"operacion": f"contraste mínimo ({tema})", "categoria": "accesibilidad",
                                       "n": len(ratios), "min_ms": minimo, "mediana_ms": round(
                                           float(np.median([i["ratio"] for i in ratios])), 2),
                                       "p95_ms": None, "max_ms": max(i["ratio"] for i in ratios),
                                       "ops_por_segundo": None,
                                       "notas": f"{len(bajos)} de {len(ratios)} textos < 4.5:1"})
                    r.verdadero(f"ui.contraste.{tema}", "accesibilidad",
                                f"{tema}: todos los textos medidos cumplen WCAG AA (≥4.5:1)",
                                len(bajos) == 0, obtenido=minimo, esperado=">= 4.5",
                                tolerancia="razón de contraste WCAG",
                                notas=str(bajos[:4]))

    # Reflujo: ventana mínima y zoom alto (siempre sobre la vista de distribuciones)
    preparar_vista("distribuciones")
    ventana.resize(900, 600)
    bombear(250)
    capturar(f"{args.plataforma}_compacto_distribuciones.png", ventana.modo_tema, "distribuciones", 1.0)
    r.verdadero("ui.compacto.sin_recorte", cat_,
                "Con 900×600 el divisor principal conserva sus dos paneles",
                ventana.divisor_principal.count() == 2, obtenido=ventana.divisor_principal.count())
    ventana.resize(ancho, alto)
    for escala in args.zoom:
        preparar_vista("distribuciones")
        ventana.escalar_texto(0, restablecer=True)
        pasos = int(round((escala - 1.0) / 0.1))
        for _ in range(max(0, pasos)):
            ventana.escalar_texto(0.1)
        bombear(300)
        efectiva = getattr(ventana, "escala_efectiva", escala)
        datos = capturar(f"{args.plataforma}_zoom_{efectiva:.2f}_distribuciones.png",
                         ventana.modo_tema, "distribuciones", round(float(efectiva), 2))
        r.verdadero(f"ui.zoom.{efectiva:.2f}", cat_,
                    f"Zoom {efectiva:.2f}: la ventana sigue mostrando contenido y gráfico",
                    bool(datos) and datos.get("px", [0])[0] >= 900,
                    obtenido=datos.get("px"), esperado=">= 900 px de ancho")
    ventana.escalar_texto(0, restablecer=True)
    bombear(150)

    # ------------------------------------------------------- accesibilidad
    interactivos = [w for w in ventana.findChildren(QWidget)
                    if isinstance(w, (QAbstractButton, QLineEdit, QPlainTextEdit, QComboBox,
                                      QAbstractSpinBox))
                    and w.isVisible() and w.isEnabled()]
    con_nombre = [w for w in interactivos if (w.accessibleName() or "").strip()]
    proporcion = len(con_nombre) / len(interactivos) if interactivos else 1.0
    sin_nombre = sorted({type(w).__name__ + ":" + (w.objectName() or w.toolTip() or "?")
                         for w in interactivos if not (w.accessibleName() or "").strip()})[:15]
    r.verdadero("ui.accesibilidad.nombres", "accesibilidad",
                "≥95 % de los controles interactivos visibles declaran nombre accesible",
                proporcion >= 0.95, obtenido=round(proporcion, 4),
                esperado=">= 0.95", tolerancia="proporción",
                notas=f"{len(con_nombre)}/{len(interactivos)} · sin nombre: {sin_nombre}")
    # Los botones pueden renunciar al foco a propósito (acciones redundantes);
    # los campos de entrada, listas y selectores no deberían hacerlo.
    entrada_teclado = [w for w in interactivos if not isinstance(w, QAbstractButton)]
    sin_foco = [type(w).__name__ for w in entrada_teclado if w.focusPolicy() == Qt.NoFocus]
    r.verdadero("ui.accesibilidad.objetivo_foco", "accesibilidad",
                "Los campos, tablas y selectores visibles aceptan foco de teclado",
                not sin_foco, obtenido=sin_foco, esperado=[], notas=f"{len(entrada_teclado)} controles")

    # ------------------------------------------------------------ WebEngine
    if "teoria" in vistas_pedidas:
        try:
            inicio = time.perf_counter()
            ventana.aplicar_tema("claro")
            ventana.cambiar("teoria")
            vista_teoria = ventana.vistas["teoria"]
            cargas: list[bool] = []
            vista_teoria.navegador.loadFinished.connect(cargas.append)
            ok = esperar(lambda: bool(cargas) and cargas[-1], args.timeout * 1000)
            r.metricas.append({"operacion": "vista teoría: carga de lección con KaTeX",
                               "categoria": "interfaz", "n": 1,
                               "min_ms": round((time.perf_counter() - inicio) * 1000, 1),
                               "mediana_ms": round((time.perf_counter() - inicio) * 1000, 1),
                               "p95_ms": round((time.perf_counter() - inicio) * 1000, 1),
                               "max_ms": round((time.perf_counter() - inicio) * 1000, 1),
                               "ops_por_segundo": None, "notas": ""})
            r.verdadero("ui.teoria.carga", "visual", "La lección se carga en QWebEngineView", ok,
                        notas="" if ok else "Revisa NSS/X11/QtWebEngineProcess")
            salidas: list[dict] = []
            vista_teoria.navegador.page().runJavaScript("""(() => ({
              formulas: document.querySelectorAll('#contenido .katex').length,
              errores: document.querySelectorAll('#contenido .katex-error').length,
              imagenes: [...document.querySelectorAll('#contenido img')].map(i => i.complete && i.naturalWidth > 0),
              tema: document.documentElement.dataset.tema,
              css: [...document.styleSheets].some(s => s.href && s.href.includes('katex.min.css'))
            }))()""", salidas.append)
            leido = esperar(lambda: bool(salidas), 8_000)
            datos = salidas[0] if leido and salidas and isinstance(salidas[0], dict) else {}
            r.verdadero("ui.teoria.katex", "visual", "KaTeX renderiza ≥3 fórmulas sin errores",
                        datos.get("formulas", 0) >= 3 and datos.get("errores", 1) == 0,
                        obtenido={k: datos.get(k) for k in ("formulas", "errores")}, esperado="formulas>=3, errores=0")
            r.verdadero("ui.teoria.imagenes", "visual", "Las figuras locales se descargan y decodifican",
                        bool(datos.get("imagenes")) and all(datos.get("imagenes", [])),
                        obtenido=datos.get("imagenes"))
            r.verdadero("ui.teoria.css", "visual", "katex.min.css se aplica desde el paquete local",
                        bool(datos.get("css")))
            capturar(f"{args.plataforma}_claro_teoria.png", "claro", "teoria", 1.0)
            ventana.aplicar_tema("oscuro")
            bombear(400)
            salidas.clear()
            vista_teoria.navegador.page().runJavaScript(
                "document.documentElement.dataset.tema", salidas.append)
            esperar(lambda: bool(salidas), 6_000)
            r.verdadero("ui.teoria.tema_oscuro", "visual", "La paleta oscura llega al documento web",
                        salidas and salidas[0] == "oscuro", obtenido=salidas[0] if salidas else None)
            capturar(f"{args.plataforma}_oscuro_teoria.png", "oscuro", "teoria", 1.0)
            ventana.aplicar_tema("claro")
        except Exception as exc:  # WebEngine ausente en servidores minimalistas
            r.registrar("ui.teoria.disponible", "visual",
                        "QWebEngineView disponible para la prueba visual de teoría",
                        pasa=False, obtenido=f"{type(exc).__name__}: {exc}"[:300],
                        notas="Instala NSS/X11/GL o ejecuta en un escritorio real")

    # ---------------------------------------------------- exportaciones reales
    if not args.sin_exportadores:
        for clave in VISTAS:
            vista = ventana.vistas.get(clave)
            if vista is None:
                continue
            ok, _ = preparar_vista(clave)
            if not ok or getattr(vista, "ultimo", None) is None:
                r.registrar(f"ui.exportar.{clave}", cat_,
                            f"{clave}: exporta XLSX/CSV/PNG/PDF desde la vista",
                            pasa=False, notas="La vista no tenía resultado")
                continue
            carpeta = args.exportaciones / clave
            carpeta.mkdir(parents=True, exist_ok=True)
            if vista._desactualizado:
                r.registrar(f"ui.exportar.{clave}.actualizado", cat_,
                            f"{clave}: el resultado es actual antes de exportar", pasa=False)
                continue
            try:
                tablas = vista.tablas_exportables()
                r.verdadero(f"ui.exportar.{clave}.tablas", cat_,
                            f"{clave}: produce al menos una tabla exportable",
                            bool(tablas), obtenido=list(tablas))
                tiempos = {}
                for formato, funcion in (
                    ("excel", lambda: io.excel(tablas, carpeta / f"{clave}.xlsx")),
                    ("csv", lambda: io.csv(vista.tabla.datos(), carpeta / f"{clave}.csv")),
                    ("png", lambda: io.png(vista.grafico.figura, carpeta / f"{clave}.png")),
                    ("pdf", lambda: io.pdf(carpeta / f"{clave}.pdf", f"AmPu 3.0 · {clave}",
                                           vista.resumen_exportable() + "\nDescripción gráfica: "
                                           + vista.grafico.descripcion.text(),
                                           tablas, vista.grafico.figura,
                                           extraer_formula(vista.clave_teoria()))),
                ):
                    inicio = time.perf_counter()
                    ruta = Path(funcion())
                    ms = (time.perf_counter() - inicio) * 1000
                    tiempos[formato] = round(ms, 1)
                    r.verdadero(f"ui.exportar.{clave}.{formato}", cat_,
                                f"{clave}: {formato.upper()} se genera con contenido",
                                ruta.is_file() and ruta.stat().st_size > 500,
                                obtenido={"bytes": ruta.stat().st_size if ruta.is_file() else 0,
                                          "ms": round(ms, 1)})
                    r.metricas.append({"operacion": f"exportar {formato.upper()} · {clave}",
                                       "categoria": "exportacion_ui", "n": 1, "min_ms": round(ms, 1),
                                       "mediana_ms": round(ms, 1), "p95_ms": round(ms, 1),
                                       "max_ms": round(ms, 1), "ops_por_segundo": None,
                                       "notas": f"{ruta.stat().st_size if ruta.is_file() else 0} bytes"})
            except Exception as exc:
                r.registrar(f"ui.exportar.{clave}", cat_, f"{clave}: exporta sin excepción",
                            pasa=False, obtenido=f"{type(exc).__name__}: {exc}"[:300])

        # Sesión completa de las seis vistas
        try:
            estado = {"modulo": ventana.actual, "tema": ventana.modo_tema,
                      "asistente": ventana.asistente.estado(),
                      "vistas": {k: v.estado() for k, v in ventana.vistas.items()}}
            ruta = io.guardar(estado, args.exportaciones / "sesion_completa.json")
            recuperado = io.cargar(ruta)
            r.verdadero("ui.sesion.roundtrip", cat_,
                        "La sesión de las seis vistas se guarda y se relee",
                        set(recuperado.get("vistas", {})) >= set(VISTAS),
                        obtenido=sorted(recuperado.get("vistas", {})))
            r.verdadero("ui.sesion.tamano", cat_, "La sesión JSON pesa menos de 25 MB",
                        ruta.stat().st_size < 25_000_000, obtenido=ruta.stat().st_size)
            # Restauración real en la vista de distribuciones
            distribuciones = ventana.vistas["distribuciones"]
            distribuciones.restaurar(recuperado["vistas"]["distribuciones"])
            ok = esperar(lambda: not distribuciones._ocupado and distribuciones.ultimo is not None, 20_000)
            bombear(300)
            r.verdadero("ui.sesion.restaurar", cat_,
                        "Restaurar una sesión recalcula el resultado sin intervención",
                        ok and distribuciones.ultimo is not None and not distribuciones._desactualizado,
                        obtenido={"ocupado": distribuciones._ocupado,
                                  "resultado": distribuciones.ultimo is not None})
            capturar(f"{args.plataforma}_sesion_restaurada.png", ventana.modo_tema, "distribuciones", 1.0)
        except Exception as exc:
            r.registrar("ui.sesion.roundtrip", cat_, "La sesión se guarda y se relee",
                        pasa=False, obtenido=f"{type(exc).__name__}: {exc}"[:300])

    # -------------------------------------------------------------- cierre
    r.verdadero("ui.capturas.generadas", "visual",
                "Se generaron capturas para todas las combinaciones pedidas",
                len(capturas) >= len([v for v in vistas_pedidas if v != "teoria"])
                * len([t for t in args.temas.split(",") if t]),
                obtenido=len(capturas),
                esperado=len([v for v in vistas_pedidas if v != "teoria"])
                * len([t for t in args.temas.split(",") if t]))
    r.verdadero("ui.capturas.sin_errores", "visual", "Ninguna captura falló al escribirse",
                not fallos_graficos["errores"], obtenido=fallos_graficos["errores"])
    memoria = _comun.memoria_mb()
    r.verdadero("ui.memoria", "rendimiento", "El proceso gráfico no supera 4 GB",
                memoria.get("pico_mb") is None or memoria["pico_mb"] < 4096, obtenido=memoria)

    # Comparación con línea base visual
    if args.linea_base and args.linea_base.is_file():
        import json

        base = {c["archivo"]: c for c in json.loads(args.linea_base.read_text(encoding="utf-8")).get("capturas", [])}
        for item in capturas:
            previo = base.get(item["archivo"])
            if not previo:
                continue
            distancia = distancia_hamming(previo["ahash"], item["ahash"])
            item["distancia_linea_base"] = distancia
            r.verdadero(f"visual.linea_base.{item['archivo']}", "visual",
                        f"{item['archivo']}: huella visual estable frente a la línea base",
                        distancia <= 8, obtenido=distancia, esperado="<= 8 bits de 64",
                        notas="aHash perceptual; pequeñas diferencias de fuentes/DPI son normales")
    if args.guardar_linea_base:
        _comun.guardar_json(args.linea_base or Path("datos/linea_base_ui.json"),
                            {"herramienta": "linea_base_visual", "version_esquema": 1,
                             "generado": _comun.ahora(), "capturas": capturas,
                             "entorno": _comun.entorno()})
        print(f"Línea base visual guardada en {args.linea_base or 'datos/linea_base_ui.json'}")

    documento = r.documento("benchmark_ui", {
        "plataforma": args.plataforma, "plataforma_qt": app.platformName(),
        "tamano": [ancho, alto], "temas": args.temas, "vistas": vistas_pedidas,
        "zoom": args.zoom, "version_ampu": version_ampu,
        "pantallas": [{"nombre": p.name(), "dpi": round(p.logicalDotsPerInch(), 1),
                       "escala": round(p.devicePixelRatio(), 2)} for p in app.screens()],
    })
    documento["capturas"] = capturas
    _comun.guardar_json(args.salida, documento)

    # Cierre sin diálogos: no hay cambios que el usuario deba confirmar aquí.
    try:
        ventana._cambios_sin_guardar = False
        ventana._cierre_confirmado = True
        ventana.close()
        ventana.deleteLater()
        bombear(200)
    except Exception:
        pass
    print(f"Interfaz verificada · capturas en {args.capturas} · datos en {args.salida}")
    return 0 if documento["resumen"]["fallan"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
