# AmPu 3.0

**Laboratorio de probabilidad y estadística de escritorio, en español y sin conexión.** AmPu 3.0 usa **Dear PyGui** para toda la interfaz y mantiene un motor científico independiente del toolkit. El árbol Java de AmPu 2.0 permanece intacto.

## Instalar y ejecutar

Se necesita **Python 3.12 o posterior** y un entorno de escritorio. Dear PyGui incluye sus ruedas para Windows, macOS y Linux; en Linux también deben estar disponibles las bibliotecas gráficas habituales de X11/OpenGL. No se requieren Qt, QtWebEngine, Chromium, rutas exclusivas de Windows ni acceso a Internet al ejecutar la aplicación.

Desde esta carpeta (`AmPu 3.0/`):

```bash
python3.12 -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m ampu
```

También se instala el comando `ampu`. `python -m ampu --version` y `python -m ampu --verify-resources` funcionan sin abrir una ventana. El primer `pip install` sí necesita una fuente de paquetes; después, lecciones, figuras, fórmulas y recursos se cargan localmente.

## Primer recorrido

1. En **Distribuciones** elige una familia, cambia sus parámetros, `x` o `q` y pulsa **Calcular y visualizar**. La tabla presenta PMF/PDF, CDF, cola inclusiva, momentos y parámetros; la gráfica alterna masa/densidad y acumulada.
2. En **Muestreo** define población, tamaño y semilla, o activa el cálculo automático del tamaño; compara el diseño y abre las hojas de asignación/selección.
3. En **Descriptiva**, **Probabilidad**, **Inferencia** o **Simulación** pega números separados por comas/espacios y ejecuta la acción principal.
4. Usa **Abrir teoría** para consultar definiciones, ejemplos, código LaTeX, figuras y referencias. Filtra las 57 lecciones y busca dentro de cada documento. `Ctrl+1…7` cambia de módulo, `F1` abre la lección correspondiente y `Ctrl+L` muestra el asistente no modal.
5. **Exportar** produce XLSX (todas las hojas), CSV UTF-8 (hoja visible), PNG (gráfico) o PDF (informe con fórmula, tabla y figura). **Guardar sesión** conserva entradas incluso incompletas, tablas editadas, hoja activa, semillas, asistente y tema en JSON versionado; **Abrir** restaura ese estado.

Cada módulo calcula su ejemplo al abrirlo por primera vez. Los cálculos se ejecutan en un `ThreadPoolExecutor`; solo el hilo principal actualiza Dear PyGui. Si una entrada cambia después del último cálculo, la exportación queda bloqueada hasta recalcular.

## Cobertura funcional

- **26 distribuciones** descubiertas desde `core/distribuciones/registro.py`: 8 discretas y 18 continuas/multivariadas, con API uniforme `pmf`/`pdf`, `cdf`, `ppf`, momentos, `rvs`, `soporte` y `validar`.
- **Muestreo:** aleatorio simple finito/con reemplazo, sistemático, estratificado proporcional/Neyman/óptimo y conglomerados de una o dos etapas; semilla reproducible.
- **Descriptiva y probabilidad:** frecuencias, tendencia central, dispersión, percentiles, combinatoria exacta, condicional, probabilidad total, Bayes, esperanza, varianza y MGF.
- **Inferencia:** 16 técnicas de contraste, correlación y regresión, con intervalos y conclusiones responsables.
- **Simulación:** π, integración Monte Carlo, muestras, ajuste por máxima verosimilitud y QQ-plot con datos reales.
- **Teoría:** 57 lecciones Markdown+LaTeX y 31 figuras locales, filtro y búsqueda. Dear PyGui presenta el texto seleccionable y las imágenes como texturas; no incrusta un navegador.
- **Asistente:** aritmética mediante AST restringido y explicación paso a paso. La pestaña LaTeX usa MathText para una vista previa local y **no calcula** la fórmula.

La **UI no implementa las fórmulas estadísticas**: prepara entradas, delega en `core/` y presenta sus salidas. NumPy/SciPy/pandas realizan los métodos; Dear PyGui cubre widgets y texturas; Matplotlib `Agg` genera las figuras compartidas con PNG/PDF; openpyxl y ReportLab cubren exportaciones.

## Tablas, sesiones y recuperación

- Las tablas son editables y paginadas (40 filas por página), con copiar/pegar TSV y hasta 20 operaciones de deshacer/rehacer por hoja. La paginación evita crear cientos de miles de widgets en simulaciones grandes.
- Las celdas editadas son **anotaciones exportables**: no alteran estadísticas ni gráficas, que se recalculan desde entradas y semilla.
- Al guardar se conservan todas las hojas, incluso las no visibles. Al abrir, el motor reproduce el cálculo y restaura únicamente anotaciones cuyo esquema coincide.
- Un trabajo iniciado antes de restaurar o limpiar una vista no puede sobrescribir la sesión nueva.
- XLSX y CSV neutralizan texto con prefijos de fórmula para impedir ejecución al abrir la hoja de cálculo.

## Apariencia y teclado

Temas **claro y oscuro** definidos en `ui/temas.py`, con pruebas WCAG AA para texto, fondo y botones. El texto se ajusta entre 90 % y 200 % desde **Ver**. `Ctrl++`, `Ctrl+-` y `Ctrl+0` están disponibles en el menú; los atajos principales son `Ctrl+S`, `Ctrl+O`, `Ctrl+E`, `Ctrl+L`, `F1` y `F2`.

La autoprueba sin viewport verifica construcción y lógica de widgets, no certifica foco nativo, lector de pantalla, DPI ni apariencia en cada SO. Esas comprobaciones deben hacerse en escritorios reales de Windows, macOS y Linux.

## Pruebas y autodiagnóstico

```bash
python -m pytest
python -m pytest --cov=ampu.core --cov-branch --cov-report=term-missing
python scripts/validar_contra_scipy.py
python -m ampu --verify-resources
python -m ampu --self-test
```

Las pruebas de interfaz crean un **contexto Dear PyGui real sin viewport**, por lo que no necesitan pantalla ni simulan los widgets. `--self-test` recorre los seis análisis, teoría, asistente y temas; `--verify-resources` comprueba lecciones, imágenes, exportadores y sesión. Ninguna de estas opciones sustituye la revisión visual nativa.

Para capturas genuinas del viewport en un escritorio:

```bash
python scripts/capturar_ui.py
```

Las capturas anteriores de la implementación Qt deben regenerarse con este script antes de publicar una revisión visual.

## Ejecutable

```bash
python -m pip install -e .[dev]
python scripts/build_exe.py --onedir --gui-self-test
# o archivo único:
python scripts/build_exe.py --gui-self-test
```

Cada sistema **debe compilar en el propio sistema**: PyInstaller no crea un `.exe` de Windows desde Linux. El comando incorpora Dear PyGui, lecciones, figuras, recursos documentales e iconos; excluye explícitamente PySide/PyQt. Después ejecuta el artefacto con `--version`, `--verify-resources` y, si se solicita, `--self-test`.

## Estructura

```text
src/ampu/
├── core/                 # Estadística sin dependencias gráficas
├── docs/                 # Lecciones, imágenes y recursos documentales
├── io/                   # XLSX, CSV, PNG, PDF y JSON
├── ui/
│   ├── main_window.py    # Ventana Dear PyGui y orquestación
│   ├── entradas.py       # Parsing sin toolkit
│   ├── logica.py         # Operaciones puras para trabajadores
│   ├── preferencias.py   # Preferencias JSON locales
│   ├── temas.py          # Paleta compartida
│   ├── vistas/           # Siete módulos Dear PyGui
│   └── widgets/          # Formularios, tablas, gráficos y trabajos
└── app.py                # CLI y arranque
scripts/
├── build_exe.py
└── capturar_ui.py
tests/                    # Motor + integración Dear PyGui sin viewport
verificacion/             # Batería reproducible y reportes
```

Las convenciones matemáticas y diferencias respecto de Java se describen en [MIGRACION.md](MIGRACION.md) y [PLAN.md](PLAN.md).
