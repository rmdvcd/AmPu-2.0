# Batería de verificación de AmPu 3.0 (PowerShell)

Este directorio contiene los comandos y los scripts necesarios para ejecutar **todas las
pruebas visuales, de rendimiento y de cálculo** de AmPu 3.0 en un equipo Windows, y para
generar un **reporte consolidado** (`REPORTE.md` + `resumen.json` + `reporte.zip`) que se
puede compartir para su análisis y corrección.

No es un sustituto de la revisión manual con lector de pantalla ni de compilar en macOS,
pero deja evidencia medible de todo lo automatizable.

---

## 1. Requisitos

| Requisito | Detalle |
|---|---|
| Sistema | Windows 10/11 (también funciona en PowerShell de macOS/Linux) |
| PowerShell | 5.1 (incluido en Windows) o 7+ (`pwsh`). Ambos soportados |
| Python | **3.12 o posterior** en el `PATH`, o se indica con `-Python` |
| Escritorio | Necesario solo para pruebas **visuales nativas** y capturas; `--self-test` funciona sin viewport |
| Red | Solo para el primer `pip install`; la app y las pruebas funcionan sin conexión |

Comprueba el intérprete antes de empezar:

```powershell
py -3.12 --version
python --version
```

---

## 2. Inicio rápido (copia y pega)

Abre **PowerShell**, entra en la carpeta `AmPu 3.0` y lanza el perfil completo. La primera
vez añade `-Instalar` para crear `.venv` e instalar dependencias:

```powershell
cd "C:\ruta\a\AmPu-2.0\AmPu 3.0"
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil completo -Instalar -AbrirReporte
```

En PowerShell 7:

```powershell
pwsh -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil completo -Instalar -AbrirReporte
```

Al terminar:

```
verificacion\salidas\<fecha-hora>\
├── REPORTE.md            ← el documento que hay que entregar
├── resumen.json          ← números clave (para análisis automático)
├── reporte.zip           ← paquete con reporte + datos + logs + capturas
├── pasos.json            ← estado y duración de cada paso
├── datos\                ← JSON de cada herramienta, junit.xml, coverage.xml
├── logs\                 ← salida completa de cada comando
├── capturas\             ← PNG reales por tema, vista y zoom
└── exportaciones\        ← XLSX/CSV/PNG/PDF y sesión generados por la UI
```

---

## 3. Perfiles: qué ejecuta cada uno

| Perfil | Para qué sirve | Duración aprox. | Incluye |
|---|---|---|---|
| `rapido` | Humo tras un cambio pequeño | 5–10 min | entorno, recursos, pytest, SciPy, cálculo abreviado, UI Dear PyGui sin viewport |
| `completo` | **Recomendado antes de entregar** | 20–40 min | todo + cobertura + rendimiento + UI nativa + `--self-test` |
| `visual` | Revisar diseño, temas, contraste y accesibilidad | 5–10 min | capturas en tema claro y oscuro, zoom 150/200 %, contraste WCAG de paletas y teoría local |
| `rendimiento` | Comparar dos equipos o dos versiones | 15–30 min | benchmarks a escala completa (10 repeticiones) + tiempos de UI |
| `calculo` | Auditar el motor numérico | 10–20 min | 26 distribuciones, 7 diseños, 16 pruebas, simulación, exportadores, cobertura |

Ejemplos:

```powershell
# Perfil rápido (sin instalar nada si ya existe .venv)
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil rapido

# Solo visual, con etiqueta para identificar el equipo
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil visual -Etiqueta "pc-aula-04"

# Solo rendimiento, 15 repeticiones y carpeta de salida propia
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil rendimiento -Repeticiones 15 -Salida "D:\reportes\ampu-2026-10-30"

# Forzar el contexto sin viewport (servidor sin pantalla)
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil calculo -Interfaz offscreen

# Incluir la compilación del ejecutable con su autoprueba gráfica
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil completo -Empaquetar
```

Parámetros disponibles:

| Parámetro | Valores | Por omisión | Uso |
|---|---|---|---|
| `-Perfil` | `rapido`, `completo`, `visual`, `rendimiento`, `calculo` | `completo` | Qué batería se ejecuta |
| `-Python` | ruta o nombre | `.venv\Scripts\python.exe`, luego `py`/`python` | Intérprete a usar |
| `-Instalar` | — | desactivado | Crea `.venv` y ejecuta `pip install -r requirements.txt` |
| `-Interfaz` | `native`, `offscreen`, `ambas` | `ambas` | `native` es la prueba visual real |
| `-Empaquetar` | — | desactivado | Añade `scripts\build_exe.py --gui-self-test` |
| `-Repeticiones` | entero | `5` | Repeticiones por operación en benchmarks |
| `-TimeoutGui` | segundos | `45` | Espera máxima por cálculo de una vista |
| `-Salida` | ruta | `verificacion\salidas\<fecha>` | Carpeta de resultados |
| `-Etiqueta` | texto | — | Sufijo para identificar el equipo |
| `-SinConsolidar` / `-SinZip` | — | desactivado | No consolidar / no comprimir |
| `-AbrirReporte` | — | desactivado | Abre `REPORTE.md` al terminar |

---

## 4. Comandos individuales (si quieres ejecutar solo una parte)

Todos se lanzan **desde la carpeta `AmPu 3.0`** y funcionan con el Python del `.venv`
(`.venv\Scripts\python.exe`) o con el comando `ampu` instalado.

### 4.1 Pruebas automáticas y cobertura

```powershell
python -m pytest -p no:cacheprovider
python -m pytest -p no:cacheprovider --junitxml="verificacion\salidas\datos\junit.xml"
python -m pytest -p no:cacheprovider --cov=ampu.core --cov-branch --cov-report=term-missing --cov-report=xml:"verificacion\salidas\datos\coverage.xml"
```

### 4.2 Cálculo: cotejo con SciPy y pruebas numéricas

```powershell
python scripts\validar_contra_scipy.py --salida "verificacion\salidas\datos\scipy.json"
python verificacion\pruebas\pruebas_calculo.py --salida "verificacion\salidas\datos\calculo.json"
python verificacion\pruebas\pruebas_calculo.py --rapido --solo inferencia
python verificacion\pruebas\pruebas_calculo.py --sin-exportadores
```

Qué comprueba `pruebas_calculo.py` (todo con tolerancia explícita en el JSON):

- **26 distribuciones**: normalización (Σ PMF = 1 / ∫ PDF = 1), CDF monótona y acotada,
  `CDF(PPF(q)) ≈ q`, PPF monótona, soporte coherente, media/varianza contra integración
  numérica, `desviacion = √varianza`, cola inclusiva, simulación reproducible con semilla y
  media simulada dentro de 6 errores estándar, rechazo de parámetros inválidos.
- **Multivariadas**: masa de todas las composiciones de la multinomial, PDF/media de
  Dirichlet y PDF/CDF de la normal bivariada contra SciPy.
- **Muestreo**: 7 diseños, tamaños, unicidad, reproducibilidad por semilla, cuotas
  proporcional/Neyman/óptimo, conglomerados en 1 y 2 etapas, tamaño automático contra la
  fórmula clásica con corrección por población finita.
- **Descriptiva**: media, mediana, varianza muestral, cuartiles, extremos, CV, modas
  múltiples, percentiles y tabla de frecuencias contra NumPy.
- **Probabilidad**: combinatoria exacta (`math.comb`/`math.perm`), condicional, total,
  Bayes, independencia, esperanza/varianza y MGF con su derivada numérica.
- **Inferencia (16 técnicas)**: p-valores contra SciPy, intervalos t y Wilson deducidos a
  mano, regresión simple/múltiple contra `linregress` y mínimos cuadrados, conclusión
  cautelosa ("no se rechaza" ≠ "se acepta"), y cobertura empírica de los IC por Monte Carlo.
- **Simulación**: π e integral de x² dentro del IC, muestra reproducible, ajuste por máxima
  verosimilitud recuperando μ y σ, QQ-plot y curva ajustada.
- **Exportadores**: XLSX con ~15 dígitos y sin fórmulas ejecutables, CSV UTF-8-BOM y
  neutralización de `=`, PNG válido, PDF con cabecera y `%%EOF`, sesión JSON versionada.

### 4.3 Rendimiento del motor

```powershell
python verificacion\pruebas\benchmark_calculo.py --salida "verificacion\salidas\datos\rendimiento.json" --escala normal --repeticiones 5
python verificacion\pruebas\benchmark_calculo.py --escala rapida --repeticiones 3
python verificacion\pruebas\benchmark_calculo.py --escala completa --repeticiones 10
```

Mide con `perf_counter_ns` (1 calentamiento + N repeticiones) el mínimo, mediana, p95, máximo
y operaciones/segundo de: PDF/CDF/PPF/PMF vectorizados, `rvs` de un millón, los 7 diseños de
muestreo, descriptiva y frecuencias, combinatoria exacta, las 16 técnicas de inferencia,
Monte Carlo, ajuste por máxima verosimilitud, QQ-plot y los cuatro exportadores. Cuando
existe una llamada SciPy equivalente se mide también para dar el **factor de sobrecoste del
adaptador**.

> Los milisegundos solo son comparables en el **mismo equipo, misma escala y mismas
> repeticiones**. El reporte lo indica en cada tabla.

### 4.4 Interfaz: pruebas visuales, contraste y accesibilidad

```powershell
# Prueba visual real (requiere escritorio). Capturas y exportaciones reales.
python verificacion\pruebas\benchmark_ui.py --plataforma native --salida "verificacion\salidas\datos\ui_nativo.json" --capturas "verificacion\salidas\capturas" --exportaciones "verificacion\salidas\exportaciones\nativo" --zoom 1.5 2.0

# Servidor sin pantalla: contexto Dear PyGui real, pero sin viewport ni píxeles.
$env:MPLBACKEND="Agg"
python verificacion\pruebas\benchmark_ui.py --plataforma offscreen --salida "verificacion\salidas\datos\ui_offscreen.json"
```

Qué mide u observa:

1. **Arranque** de `VentanaPrincipal` con sus siete vistas y texturas.
2. **Primer cálculo** de los seis módulos y existencia de resultados/tablas reales.
3. **Capturas reales del viewport** para cada vista solicitada en claro y oscuro (solo `native`).
4. **Huella perceptual** `aHash` de 64 bits por captura y comparación opcional con una línea base.
5. **Contraste WCAG de las paletas** de texto/fondo. No se presenta como una medición de píxeles.
6. **Escala de texto** adicional; los recortes y el foco se revisan visualmente en el SO.
7. **Teoría local** con contenido seleccionable, código LaTeX y figuras como texturas.
8. **Exportaciones** XLSX/CSV/PNG/PDF y **sesión completa** guardada, releída y recalculada.
9. **Memoria** del proceso y duración de cada operación.

El modo `offscreen` registra las capturas como omitidas: construir widgets no equivale a
renderizarlos. Tampoco certifica lector de pantalla, orden de foco, DPI ni portabilidad.

Línea base visual (para comparar tras un rediseño):

```powershell
python verificacion\pruebas\benchmark_ui.py --plataforma native --salida "verificacion\salidas\datos\ui_nativo.json" --guardar-linea-base
python verificacion\pruebas\benchmark_ui.py --plataforma native --linea-base "verificacion\salidas\datos\linea_base_ui.json"
```

### 4.5 Autoprueba estricta de escritorio

```powershell
python -m ampu --verify-resources
python -m ampu --self-test
```

`--self-test` no abre viewport ni omite módulos: falla si los seis análisis, la teoría local,
el asistente o los temas Dear PyGui no funcionan. La captura visual se realiza por separado
con `scripts/capturar_ui.py` en un escritorio.

### 4.6 Consolidar un reporte a mano

```powershell
python verificacion\pruebas\consolidar_reporte.py --carpeta "verificacion\salidas\20261030-101500"
```

---

## 5. Qué contiene el reporte

`REPORTE.md` incluye, en este orden:

1. Veredicto automático (requiere correcciones / sin hallazgos bloqueantes).
2. Entorno y **huella SHA-256 de las fuentes** y commit, para saber exactamente qué se probó.
3. Tabla de pasos con estado, código de salida, duración y log.
4. Resultado por área y detalle de pytest + cobertura por módulo.
5. Cálculo: comprobaciones por categoría y **tabla de discrepancias con tolerancias**.
6. Cotejo con SciPy y los mayores errores absolutos.
7. Rendimiento: operaciones más costosas y sobrecoste frente a SciPy.
8. Interfaz: tiempos, contraste por tema, accesibilidad, capturas y huellas.
9. Autoprueba Dear PyGui.
10. **Hallazgos priorizados** (severidad, evidencia, acción sugerida).
11. Lo que esta batería **no** puede certificar.
12. Instrucciones de entrega.

Umbrales usados (editables en `pruebas/consolidar_reporte.py` → `UMBRALES`):

| Métrica | Umbral |
|---|---|
| Cobertura del núcleo con ramas | ≥ 85 % |
| Contraste de texto | ≥ 4.5:1 (WCAG AA) |
| Controles con nombre accesible | ≥ 95 % |
| Arranque de la ventana | ≤ 6 000 ms |
| Primer resultado de una vista | ≤ 5 000 ms |
| Exportación individual | ≤ 8 000 ms |
| Operación del núcleo | ≤ 10 000 ms |
| Sobrecoste frente a SciPy | < 20× |
| Cambio visual vs línea base | ≤ 8 de 64 bits |

---

## 6. Cómo entregar el resultado para su análisis

1. Ejecuta el perfil `completo` (o `visual` + `calculo` + `rendimiento` por separado).
2. Envía **`REPORTE.md`** y **`resumen.json`**. Si puedes, adjunta **`reporte.zip`**: las
   capturas y los logs son la evidencia que no cabe en el texto.
3. Indica el perfil y la interfaz usada, y si el equipo tenía escritorio.

Con eso se pueden priorizar correcciones: el reporte ya separa fallos de cálculo (severidad
alta), regresiones visuales (media/baja), problemas de accesibilidad (alta) y desviaciones de
rendimiento (media).

---

## 7. Problemas frecuentes

| Síntoma | Causa / solución |
|---|---|
| `... no se puede cargar porque la ejecución de scripts está deshabilitada` | Usa `powershell -ExecutionPolicy Bypass -File ...` o `Unblock-File .\verificacion\*.ps1` |
| `No se encontró Python` | Instala Python 3.12+ o pasa `-Python "C:\Python312\python.exe"` |
| `No module named pytest` / `pytest-cov` | `-Instalar` o `pip install -r requirements.txt` (incluye `.[dev]`) |
| `Dear PyGui no puede crear el viewport` | Ejecuta desde una sesión de escritorio con X11/OpenGL; no uses una sesión SSH sin reenvío gráfico |
| `Dear PyGui no inició; comprueba X11/OpenGL y el entorno de escritorio` | Falta el runtime gráfico de Dear PyGui (o MSVC redistributable en Windows). Ejecuta sin `-Empaquetar` y revisa `logs\self_test.log` |
| Las pruebas visuales nativas fallan y las offscreen pasan | Es lo esperado en un servidor: el reporte marcará la verificación visual como pendiente |
| Acentos raros en la consola | Los `.ps1` se guardan en UTF-8 con BOM; en PS 5.1 ejecuta `chcp 65001` antes |
| El ZIP no aparece | `-SinZip` o falta espacio; el resto del paquete sigue disponible |
| Todo tarda mucho | Usa `-Perfil rapido` o reduce `-Repeticiones`; el paso más lento es el ajuste por máxima verosimilitud |

---

## 8. Estructura de esta carpeta

```text
verificacion/
├── EjecutarVerificacion.ps1     # orquestador: perfiles, tiempos límite y logs
├── lib/Comun.ps1                # ejecución de procesos con timeout y entorno controlado
├── pruebas/
│   ├── _comun.py                # contrato de salida JSON, entorno, medidas y memoria
│   ├── recolectar_entorno.py    # SO, versiones, pantallas, DPI, commit y huella de fuentes
│   ├── pruebas_calculo.py       # corrección numérica de todo el motor + exportadores
│   ├── benchmark_calculo.py     # rendimiento del núcleo y sobrecoste frente a SciPy
│   ├── benchmark_ui.py          # capturas, contraste, accesibilidad, exportación y sesión
│   └── consolidar_reporte.py    # REPORTE.md, resumen.json, hallazgos y ZIP
└── salidas/                     # resultados (ignorado por git)
```

Nada de esta carpeta se importa desde la aplicación ni forma parte del ejecutable.
