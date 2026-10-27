# AmPu 3.0

**Laboratorio de probabilidad y estadística de escritorio, en español y sin conexión.** Una reimplementación multiplataforma de AmPu 2.0 con un motor científico separado de Qt, controles claros, resultados reproducibles y teoría consultable durante el análisis. El árbol Java original sigue intacto.

![Explorador de distribuciones en tema claro](docs/capturas/01_distribuciones_claro.png)

| Diseño muestral | Inferencia | Tema oscuro |
|---|---|---|
| [![Muestreo](docs/capturas/02_muestreo_claro.png)](docs/capturas/02_muestreo_claro.png) | [![Inferencia](docs/capturas/03_inferencia_claro.png)](docs/capturas/03_inferencia_claro.png) | [![Distribuciones, tema oscuro](docs/capturas/04_distribuciones_oscuro.png)](docs/capturas/04_distribuciones_oscuro.png) |

## Instalar y ejecutar

Se necesita **Python 3.12 o posterior**, un sistema con entorno gráfico y las bibliotecas nativas habituales de Qt/QtWebEngine. En Linux instale las bibliotecas gráficas de su distribución, entre ellas OpenGL/EGL, `libxkbcommon`, D-Bus, NSS y las dependencias X11 de QtWebEngine. El entorno de evaluación minimalista no trae todas estas bibliotecas de serie; **no se requieren rutas exclusivas de Windows ni acceso a Internet al ejecutar la aplicación**. En macOS/Windows basta con una instalación normal de Python y el entorno de escritorio del sistema.

Desde esta carpeta (`AmPu 3.0/`):

```bash
python3.12 -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m ampu
```

También se instala el comando `ampu`. `python -m ampu --version` funciona incluso sin servidor gráfico. El primer `pip install` sí necesita una fuente de paquetes; después, los recursos de lectura, fórmulas y fuentes se cargan **localmente**. Para facilitar la instalación manual: `python -m pip install -e .[dev]` instala los mismos extras de desarrollo.

### Primer recorrido

1. En **Distribuciones** elige una familia, cambia `n`, `p`, `x` o `q` y pulsa **Calcular y visualizar**. La tabla presenta la PMF/PDF, CDF, cola inclusiva, momentos y parámetros; la gráfica alterna masa/densidad y acumulada.
2. En **Muestreo** define población, tamaño y semilla, o activa el cálculo automático del tamaño; compara el diseño visualmente y abre las hojas de asignación/selección.
3. En **Descriptiva**, **Probabilidad**, **Inferencia** o **Simulación** pega números separados por coma/espacio, pulsa la acción principal y explora resultados y gráfico.
4. Usa **Abrir teoría** para ver fórmulas, ejemplos resueltos, figuras y fuentes; filtra lecciones en **Teoría**. Los atajos `Ctrl+1…7` cambian de módulo, `F1` abre la lección correspondiente y `Ctrl+L` abre la calculadora científica.
5. **Exportar** produce XLSX (todas las hojas), CSV UTF-8 (hoja visible), PNG (gráfico) o PDF (informe con fórmula, tabla y figura). **Guardar sesión** conserva entradas, tablas, semilla y tema como JSON versionado; **Abrir** restaura la sesión local.

## Cobertura funcional

- **26 distribuciones** descubiertas desde `core/distribuciones/registro.py` — **8 discretas** (Bernoulli, binomial, binomial negativa, multinomial, geométrica, hipergeométrica, Poisson, uniforme discreta) y **18 continuas** (uniforme, normal estándar/general/bivariada, chi-cuadrado, exponencial, t, F, gamma, Erlang, beta, lognormal, Weibull, Cauchy, logística, triangular, Pareto, Dirichlet). API uniforme `pmf`/`pdf`, `cdf`, `ppf`, `media`, `varianza`, `desviacion`, `rvs`, `soporte` y `validar`. Las CDF y PPF multivariadas siguen la convención explícita de [PLAN.md](PLAN.md).
- **Muestreo:** aleatorio simple finito y con reemplazo, sistemático, estratificado proporcional/Neyman/óptimo y conglomerados de una o dos etapas; tamaño automático de proporciones con corrección finita, tamaños para medias/diferencias y semilla reproducible.
- **Descriptiva y probabilidad:** frecuencias, tendencia central, dispersión, percentiles, combinatoria exacta, probabilidades condicional y total, Bayes, esperanza, varianza y MGF.
- **Inferencia:** 16 técnicas entre z/t de una/dos muestras, z de proporciones, chi-cuadrado, ANOVA, Pearson/Spearman, regresión simple/múltiple, Mann–Whitney, Wilcoxon y Kruskal–Wallis; intervalos de confianza y conclusiones que distinguen «no se rechaza» de «se acepta». La prueba KS posterior a un ajuste se marca **exploratoria**, sin corrección por estimación.
- **Simulación:** π, integración Monte Carlo, muestras, ajuste por máxima verosimilitud de cinco familias y QQ-plot con datos reales; intervalos y errores estándar donde corresponde.
- **Teoría:** 57 lecciones Markdown+LaTeX, 31 figuras, KaTeX 0.16.22 y STIX Two Math locales con tema claro/oscuro, índice y búsqueda en `QWebEngineView`. La calculadora integrada evalúa expresiones de forma restringida sin invocar procesos externos.

La **UI no implementa las fórmulas**: prepara entradas, envía trabajos a hilos Qt y presenta la salida calculada por `core/`. NumPy/SciPy/pandas ejecutan los métodos; Matplotlib QtAgg, PySide6, openpyxl y ReportLab cubren presentación y exportaciones.

## Desarrollo y verificación

```bash
python -m pytest
python -m pytest --cov=ampu.core --cov-branch --cov-report=term-missing
python scripts/validar_contra_scipy.py
```

Verificado en Python **3.12.11**, NumPy **2.5.4**, SciPy **1.18.1**, pandas **3.1.0**, PySide6 **6.12.0**: **114 tests pasan**, **92 % de cobertura del núcleo con ramas** (objetivo ≥85 %) y **121/121** comparaciones contra SciPy. Las pruebas Qt se ejecutaron con la plataforma offscreen y suplentes gráficos **solo de pruebas** porque esta imagen Linux carece de algunas bibliotecas nativas; los suplentes **no forman parte del proyecto ni del paquete**. La vista `QWebEngineView` requiere verificar su ejecución visual en un sistema con NSS/X11/QtWebEngine completos. Si el entorno carece de `libGL.so.1`/`libEGL.so.1`, la prueba Qt se omite limpiamente; el núcleo y el HTML se siguen probando.

Los ejemplos originales Java se comparan en [`tests/test_paridad_java.py`](tests/test_paridad_java.py). Los resultados que eran erróneos **no se copian**: consulta [MIGRACION.md](MIGRACION.md) para fórmulas, casos y diferencias. La ubicación de archivos y alcance se explican en [PLAN.md](PLAN.md). Las contribuciones y convenciones están en [CONTRIBUTING.md](CONTRIBUTING.md).

## Empaquetar

```bash
python scripts/build_exe.py              # un archivo en Linux/Windows, .app en macOS
python scripts/build_exe.py --onedir     # carpeta portable en Linux/Windows
```

Cada sistema **debe compilar en el propio sistema**: PyInstaller no crea un `.exe` de Windows desde Linux. El script incorpora las lecciones, imágenes, KaTeX, fuentes, QSS, icono y `QtWebEngineProcess` mediante hooks; usa rutas relativas a `__file__`. La carpeta `dist/` se ignora. Una compilación Linux `--onedir` se completó con Python 3.12 y se comprobó `dist/AmPu3/AmPu3 --version`; este sandbox no contiene todas las dependencias gráficas del sistema, por lo que **el paquete Linux de este sandbox no es una distribución portable verificada visualmente**. Ejecuta el empaquetado y la prueba de la lección web en un equipo con las bibliotecas nativas completas antes de publicar.

## Estructura

```text
AmPu 3.0/
├── src/ampu/
│   ├── core/              # validación, modelos, muestreo, estadística, simulación
│   ├── io/                # Excel/CSV/PNG/PDF y sesiones JSON
│   ├── docs/              # 57 lecciones, 31 imágenes y motor KaTeX offline
│   ├── ui/                # siete vistas, componentes, temas e icono
│   ├── app.py             # QApplication, logging rotativo y entrada
│   └── __main__.py        # python -m ampu
├── tests/                 # SciPy, bordes, exportaciones, teoría y Qt opcional
├── scripts/               # editor de teoría, validador, capturas y PyInstaller
├── docs/capturas/         # PNG genuinos de QWidget con resultados terminados
├── PLAN.md
├── MIGRACION.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

**Licencias:** el código Python nuevo está bajo MIT ([LICENSE](LICENSE)); KaTeX incluye su MIT en [`LICENSE.katex`](src/ampu/docs/render/LICENSE.katex) y STIX Two Math su OFL en [`LICENSE.stix`](src/ampu/docs/render/LICENSE.stix). El proyecto Java original conserva su situación de derechos previa; no se ha incorporado ni modificado su código.
