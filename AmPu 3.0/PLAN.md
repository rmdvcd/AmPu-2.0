# Plan y mapa de migración · AmPu 2.0 → 3.0

El árbol original (`src/`, `test/`, `Libraries/`, etc.) es **solo de lectura**. Todo el código nuevo está en esta carpeta. `src/Clases/Funciones.java`, `src/Utiles/GestionEncabezadoTabla.java`, las 15 páginas `src/teoriahtml/` y `test/Clases/FuncionesTest.java` son las referencias examinadas.

| Referencia AmPu 2.0 | Implementación AmPu 3.0 | Comprobación |
|---|---|---|
| `binomialVp`, `binomialNVp`, `geometricaVp`, `hipergeometricaVp`, `poissonVp` | Registro de distribuciones discretas (SciPy), PMF/CDF/PPF/cola inclusiva | `tests/test_distribuciones_discretas.py`, `test_paridad_java.py` |
| `multinomialVp(N,x,p)` | `scipy.stats.multinomial` con vector de conteos y probabilidades; evita confundir el divisor por producto factorial con un único escalar | `tests/test_distribuciones_multivariadas.py` |
| `UniformeF`, `NormalF`, `ExponencialF`, `JiF`, `TstudentF`, `FdeFisherF` | Continuas SciPy con parámetros explícitos, cuantiles y momentos | `tests/test_distribuciones_continuas.py` |
| `MASFinito`, `MASInfinito`, `MEstratificado` | Tamaños con corrección finita, selección con semilla y asignación entera | `tests/test_muestreo.py` |
| `GestionEncabezadoTabla` y modelos Swing | Tabla consultando el registro; columnas de parámetros, PMF/PDF, CDF, cola inclusiva, media, varianza y DE | `tests/test_distribuciones_*.py`, pruebas de UI |
| `Graficos.java` / JFreeChart | Matplotlib QtAgg con curva PMF/PDF/CDF y región/evento resaltado, barra de herramientas | pruebas de UI y capturas |
| `ExportarE.java` / POI | Servicio unificado XLSX/CSV/PNG/PDF (guardado único, formato y filas completas) | `tests/test_io.py` |
| 12 HTML de distribuciones + 3 de muestreo | 57 Markdown con fórmulas LaTeX, ejemplos y referencias, 31 figuras nuevas y KaTeX/STIX locales | `tests/test_teoria.py` |
| `Interfaz.java` | Navegación PySide6, controles dinámicos por metadatos y vistas para distribuciones, muestreo, descriptiva, inferencia, simulación | `tests/test_ui.py` |
| Calculadora de Windows y OSK | Calculadora científica segura integrada; entrada y atajos Qt | pruebas de UI |

## Plan de implementación

1. Motor independiente de Qt: registro/validación, SciPy, muestreo, probabilidad, descriptiva, inferencia, regresión y simulación.
2. Pruebas de SciPy y casos de `FuncionesTest` interpretados con semántica matemática correcta. Se anotan explícitamente las expectativas históricas incompatibles (la distribución t, la cola F, la desviación uniforme y el escalar multinomial).
3. Teoría nueva en Markdown/LaTeX con figuras reproducibles; motor KaTeX y fuentes empaquetados localmente (sin CDN).
4. UI orientada a metadatos, cálculos en QThread, gráficos interactivos, validación y exportaciones comunes.
5. Documentación, capturas reproducibles y script PyInstaller. Cada plataforma debe ejecutar PyInstaller en *su propio SO*: no existe compilación cruzada de Windows desde Linux.

## Semántica estable de la API

- Binomial negativa: `x` = fracasos antes de `r` éxitos. Geométrica: `x` = número de intentos hasta el primer éxito. Exponencial: `tasa` (SciPy usa `scale=1/tasa`).
- Las colas discretas inclusivas se calculan como `1 − CDF(x−1)`; la CDF incluye `x`. PPF de distribuciones discretas en `q=0` sigue la convención de SciPy (puede devolver soporte mínimo menos uno).
- Para modelos multivariados: `pmf/pdf` acepta un vector (o matriz de observaciones), los momentos son vectores marginales. `cdf` multinomial y Dirichlet y `ppf` de los tres modelos multidimensionales se definen **por componente marginal** (no existe un cuantil conjunto canónico); la `cdf` de la normal bivariada sí es conjunta. La UI explica esta distinción.
- El muestreo estratificado redondea con método de mayores restos, preserva el tamaño total y respeta la capacidad de cada estrato.
