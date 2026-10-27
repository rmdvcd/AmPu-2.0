"""Autoprueba del paquete y de la lección web, sin depender de pytest.

``--verify-resources`` comprueba un ejecutable incluso sin escritorio gráfico.
``--self-test`` exige QtWebEngine funcional y un entorno de escritorio completo.
"""

import math
import sys
import tempfile
from pathlib import Path


def verificar_recursos() -> dict:
    """Comprueba contenido distribuido, rutas relativas y los cuatro exportadores."""
    from matplotlib.figure import Figure
    from openpyxl import load_workbook
    import pandas as pd

    from ampu.docs.teoria import DOCUMENTOS, PLANTILLA, listar_teoria, renderizar
    from ampu.io import ServicioExportacion as io

    raiz = DOCUMENTOS.parent.parent
    estilos = raiz / "ui" / "estilos"
    icono = raiz / "ui" / "recursos" / "icono.svg"
    render = PLANTILLA.parent
    recursos = [PLANTILLA, icono, estilos / "claro.qss", estilos / "oscuro.qss",
                render / "katex.min.js", render / "katex.min.css", render / "auto-render.min.js",
                render / "fonts" / "KaTeX_Main-Regular.woff2",
                render / "fonts" / "stix-two-math-latin-400-normal.woff2",
                DOCUMENTOS / "binomial.md", DOCUMENTOS.parent / "imagenes" / "binomial.png"]
    ausentes = [str(ruta) for ruta in recursos if not ruta.is_file() or ruta.stat().st_size == 0]
    if ausentes:
        raise RuntimeError("Faltan recursos empaquetados: " + ", ".join(ausentes))
    lecciones = listar_teoria()
    imagenes = list((DOCUMENTOS.parent / "imagenes").glob("*.png"))
    if len(lecciones) != 57 or len(imagenes) != 31:
        raise RuntimeError(f"Catálogo incompleto: {len(lecciones)} lecciones, {len(imagenes)} imágenes")
    for tema in ("claro", "oscuro"):
        html = renderizar("binomial", tema)
        if f'data-tema="{tema}"' not in html or "formula-bloque" not in html:
            raise RuntimeError(f"La plantilla de teoría {tema} no se pudo renderizar")

    with tempfile.TemporaryDirectory(prefix="ampu-autoprueba-") as temporal:
        carpeta = Path(temporal)
        tabla = pd.DataFrame({"probabilidad": [0.12345678912345678], "etiqueta": ["AmPu"]})
        figura = Figure(figsize=(2, 2))
        figura.subplots().plot([0, 1], [0, 1])
        archivos = [io.excel({"Prueba": tabla}, carpeta / "prueba.xlsx"),
                    io.csv(tabla, carpeta / "prueba.csv"),
                    io.png(figura, carpeta / "prueba.png"),
                    io.pdf(carpeta / "prueba.pdf", "Autoprueba", "Funciona sin red", {"Prueba": tabla}, figura)]
        io.guardar({"semilla": 42}, carpeta / "sesion.json")
        if io.cargar(carpeta / "sesion.json")["semilla"] != 42:
            raise RuntimeError("No se pudo leer la sesión empaquetada")
        if any(not ruta.is_file() or not ruta.stat().st_size for ruta in archivos):
            raise RuntimeError("Algún exportador no generó un archivo")
        excel = load_workbook(archivos[0], read_only=True)
        try:
            # XLSX/Excel conserva aproximadamente 15 dígitos decimales.
            if not math.isclose(excel.active["A2"].value, tabla.iloc[0, 0], rel_tol=0, abs_tol=5e-16):
                raise RuntimeError("Se perdió precisión al exportar Excel")
        finally:
            excel.close()

    reporte = {"recursos": "correctos", "lecciones": len(lecciones), "imagenes": len(imagenes),
               "formatos": ["xlsx", "csv", "png", "pdf", "json"], "congelado": bool(getattr(sys, "frozen", False))}
    if getattr(sys, "frozen", False):
        # En macOS el helper puede residir fuera de _MEIPASS, en la misma .app.
        paquete = (Path(sys.executable).resolve().parents[2] if sys.platform == "darwin"
                   else Path(sys._MEIPASS))
        helper = next((p for p in paquete.rglob("QtWebEngineProcess*") if p.is_file()), None)
        recursos_web = next(paquete.rglob("qtwebengine_resources.pak"), None)
        if helper is None or recursos_web is None:
            raise RuntimeError("El paquete no incluye QtWebEngineProcess y sus recursos Chromium")
        reporte["webengine_empaquetado"] = "helper y Chromium presentes (no implica verificación visual)"
    return reporte


def _esperar_qt(condicion, milisegundos: int = 20_000) -> bool:
    """Procesa señales WebEngine con plazo explícito en vez de bloquear la UI."""
    from PySide6.QtCore import QEventLoop, QTimer

    ciclo = QEventLoop()
    vencido = False

    def agotar():
        nonlocal vencido
        vencido = True
        ciclo.quit()

    limite = QTimer()
    limite.setSingleShot(True)
    limite.timeout.connect(agotar)
    limite.start(milisegundos)

    def comprobar():
        if condicion():
            ciclo.quit()
        else:
            QTimer.singleShot(40, comprobar)

    QTimer.singleShot(0, comprobar)
    ciclo.exec()
    limite.stop()
    return not vencido


def verificar_webengine(app, captura: str | None = None) -> dict:
    """Verifica en Chromium real HTML, KaTeX, figura local, CSS y tema oscuro.

    No usa capturas sintéticas: ``captura`` es opcional para revisión visual.
    """
    import ampu.ui.vistas.teoria  # import nativo estricto, sin diálogo modal
    from ampu.ui.main_window import VentanaPrincipal

    ventana = VentanaPrincipal()
    ventana.show()
    try:
        distribuciones = ventana.vistas["distribuciones"]
        if not _esperar_qt(lambda: distribuciones.ultimo is not None and not distribuciones._ocupado):
            raise RuntimeError("La ventana no terminó su primer cálculo")
        ventana.cambiar("teoria")
        vista = ventana.vistas["teoria"]
        cargas: list[bool] = []
        vista.navegador.loadFinished.connect(lambda exito: cargas.append(exito))
        if not _esperar_qt(lambda: bool(cargas)) or not cargas[-1]:
            raise RuntimeError("WebEngine no inició; comprueba NSS, QtWebEngineProcess y X11")
        cargas.clear()
        vista.seleccionar("binomial")
        if not _esperar_qt(lambda: bool(cargas)) or not cargas[-1]:
            raise RuntimeError("WebEngine no cargó la lección binomial local")

        javascript = """(() => ({
          titulo: document.querySelector('#contenido h1')?.textContent || '',
          formulas: document.querySelectorAll('#contenido .katex').length,
          errores: document.querySelectorAll('#contenido .katex-error').length,
          imagenes: [...document.querySelectorAll('#contenido img')].map(i => i.complete && i.naturalWidth > 0),
          tema: document.documentElement.dataset.tema,
          css: [...document.styleSheets].some(s => s.href && s.href.includes('katex.min.css')),
          color: getComputedStyle(document.body).backgroundColor
        }))()"""

        def evaluar():
            salidas = []
            vista.navegador.page().runJavaScript(javascript, salidas.append)
            if not _esperar_qt(lambda: bool(salidas), 6_000) or not isinstance(salidas[0], dict):
                raise RuntimeError("WebEngine no devolvió el estado del DOM")
            return salidas[0]

        datos = evaluar()
        if ("binomial" not in datos["titulo"].lower() or datos["formulas"] < 3
                or datos["errores"] or not datos["imagenes"] or not all(datos["imagenes"]) or not datos["css"]):
            raise RuntimeError(f"KaTeX, CSS o imagen local no renderizaron: {datos}")
        cargas.clear()
        ventana.aplicar_tema("oscuro")
        if not _esperar_qt(lambda: bool(cargas)) or not cargas[-1]:
            raise RuntimeError("WebEngine no volvió a cargar el tema oscuro")
        oscuro = evaluar()
        if oscuro["tema"] != "oscuro" or oscuro["formulas"] < 3 or oscuro["color"] == datos["color"]:
            raise RuntimeError(f"La paleta oscura no se aplicó al DOM: {oscuro}")
        if captura:
            ruta = Path(captura)
            ruta.parent.mkdir(parents=True, exist_ok=True)
            app.processEvents()
            if not ventana.grab().save(str(ruta), "PNG"):
                raise RuntimeError(f"No se pudo capturar {ruta}")
        return {"webengine": "correcto", "formulas": oscuro["formulas"], "imagenes": len(oscuro["imagenes"]),
                "tema_oscuro": oscuro["color"]}
    finally:
        ventana.close()
        app.processEvents()
