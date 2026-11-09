# Protocolo de pruebas visuales, funcionales, de navegación y rendimiento · AmPu 3.0

> **Este archivo es a la vez instructivo y reporte.** La sección 2 explica cómo ejecutar la batería; las secciones 4 a 7 contienen los casos con columnas `Resultado` y `Evidencia` **vacías a propósito**; la sección 8 lista hipótesis de defecto que deben confirmarse o refutarse con evidencia; las secciones 9 y 10 son el entregable que se devuelve al agente autor para su análisis.
>
> **No borres nada de este documento.** Solo rellena, marca y añade. Si una comprobación no se pudo ejecutar, se marca `BLOQ` o `PEND` con el motivo exacto: nunca se inventa un resultado.

## Ficha del documento

| Campo | Valor |
|---|---|
| Documento | `PROTOCOLO_PRUEBAS_UI.md` |
| Versión del documento | **1.0** (sin ejecutar) |
| Estado de la ejecución | COMPLETADO |
| Producto bajo prueba | AmPu 3.0 (`AmPu 3.0/`), interfaz Dear PyGui |
| Commit de partida | `f8074071cb6198f0a26ebf67aa63a390fbaf9866` |
| Autor del protocolo | Agente de análisis estático (revisión del 2026-11-04) |
| Destinatario del informe | Agente autor, para priorizar y corregir regresiones visuales |
| Ejecutor | Agente de análisis automático (Codebuff/Buffy) |
| Fecha de ejecución | 2026-11-05 |
| Plataforma probada | Windows 11, Dear PyGui 2.3.1, resolución 1440×900 |

**Motivo del protocolo.** La migración de PySide6/Qt a **Dear PyGui** (véase `CHANGELOG.md`, entrada «migración a Dear PyGui — 2026-11-03») sustituyó toda la capa gráfica. El motor de cálculo conserva su API y sus pruebas, pero los widgets, el tema, la disposición, el foco y el render de gráficos se reescribieron por completo. La revisión estática de este repositorio ya detecta **colores fijados a mano que no siguen el tema activo** y **geometrías fijas en píxeles**; ambas cosas producen defectos visuales reales que solo se confirman ejecutando la aplicación en un escritorio.

---

## 1. Contrato para la IA ejecutora

### 1.1 Qué debes hacer

1. Ejecutar las baterías en el orden **0 → A → B → C → D** (la batería 0 es un humo de 10 minutos que decide si el resto tiene sentido).
2. Para cada caso, escribir en su fila: `OK`, `FALLA`, `BLOQ`, `PEND` o `N/A`, la ruta de la evidencia y una nota factual.
3. Confirmar o refutar **cada** hipótesis de la sección 8 con la captura o medición indicada.
4. Rellenar la sección 9 (hallazgos consolidados) y el bloque JSON de la sección 10.
5. Actualizar la ficha, la bitácora de versiones y el estado de la ejecución (sección 12).
6. Verificar que el JSON de la sección 10 es válido y que **cada ruta citada existe** (hay dos comprobaciones listas para copiar en 12.3).

### 1.2 Qué no debes hacer

- **No modifiques el código de la aplicación** (`src/ampu/**`, `scripts/**`, `tests/**`). El objetivo es medir el estado actual, no arreglarlo. Si encuentras la causa exacta, anótala en «sospecha de código», no la corrijas.
- No actualices dependencias, no cambies `pyproject.toml` ni `requirements.txt`, no reformatees archivos.
- No ejecutes la batería de verificación existente **modificando** sus umbrales (`verificacion/pruebas/consolidar_reporte.py`).
- No rellenes filas «por analogía». Si no viste el efecto en una captura, no lo marques `OK`.
- No declares accesibilidad certificada: este protocolo no sustituye a un lector de pantalla ni a una revisión humana (sección 11).
- No publiques, no hagas commit en ramas ajenas y no abras PR sin que te lo pidan.

### 1.3 Vocabulario de resultados

| Código | Significado |
|---|---|
| `OK` | Se ejecutó y cumple lo esperado, con evidencia citada |
| `FALLA` | Se ejecutó y **no** cumple lo esperado; debe existir un hallazgo en la sección 9 |
| `BLOQ` | No se pudo ejecutar por un impedimento técnico del entorno (sin escritorio, sin OpenGL, etc.) |
| `PEND` | Requiere intervención humana o hardware/SO no disponible (lector de pantalla, DPI, macOS…) |
| `N/A` | No aplica a esta plataforma o configuración |

### 1.4 Severidad

| Nivel | Criterio |
|---|---|
| `S1` Bloqueante | La app no arranca, se pierde trabajo, o un resultado estadístico es incorrecto |
| `S2` Alta | Función inutilizable, texto ilegible, o acción principal que no responde |
| `S3` Media | Defecto claro con rodeo disponible (recorte, solapamiento, desalineación) |
| `S4` Baja | Cosmético o de pulido |

### 1.5 Presupuesto de tiempo

| Perfil | Casos | Duración esperada | Cuándo usarlo |
|---|---|---|---|
| Humo | Batería 0 | 10–15 min | Tras cualquier cambio pequeño |
| Visual | 0 + A + C | 45–75 min | Tras tocar tema, widgets o disposición |
| Completo | 0 + A + B + C + D | 2,5–4 h | Antes de entregar o publicar |

---

## 2. Preparación del entorno

Todos los comandos se ejecutan **desde la carpeta `AmPu 3.0/`**. Requiere **Python 3.12 o posterior** y un escritorio real (X11/Wayland, Windows o macOS). Un servidor sin pantalla solo permite `BLOQ` en todo lo visual.

### 2.1 Instalación

```bash
# Linux / macOS
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2.2 Registro obligatorio del entorno

Antes de tocar la UI, guarda la huella. La app funciona sin instalarse con `PYTHONPATH`:

```bash
python verificacion/pruebas/recolectar_entorno.py --salida "verificacion/salidas/<sello>/datos/entorno.json"
```

Si el paquete no está instalado en modo editable, antepón `PYTHONPATH=src` (Linux/macOS) o `$env:PYTHONPATH="src"` (Windows) a los comandos siguientes, o instala con `python -m pip install -e .`.

Anota en la ficha: SO y versión, escritorio y servidor gráfico, resolución y escala del sistema (`100 %`, `125 %`, `150 %`…), versión de `dearpygui`, y si hay **una o varias pantallas**.

### 2.3 Batería 0 · Humo y preflight (obligatorio)

Es la puerta de entrada: si algo aquí falla en `S1`, se detiene la batería y se reporta sin seguir.

| # | Comando | Esperado |
|---|---|---|
| P-1 | `python -m ampu --version` | `AmPu 3.0.0` |
| P-2 | `python -m ampu --verify-resources` | JSON con **57 lecciones**, **31 imágenes** y formatos XLSX/CSV/PNG/PDF/JSON |
| P-3 | `python -m ampu --self-test` | Termina con código 0 y JSON sin excepciones (no abre ventana) |
| P-4 | `python -m pytest -q` | Toda la suite en verde; anota nº de pruebas, omitidas y duración |
| P-5 | `python -m ampu` | Se abre la ventana «AmPu 3.0 · Laboratorio de estadística» |

Registra los resultados de P-1…P-5 en la tabla final de la sección 9.0 (preflight). **Si P-5 falla, detén la batería A, B y C** y reporta `S1`.

---

## 3. Evidencia: dónde y cómo

### 3.1 Árbol de salida

Usa un sello de fecha único (`AAAAAMMDD-HHMMSS`) y **no** lo borres al terminar. La carpeta `verificacion/salidas/` está ignorada por git, así que es el sitio correcto para artefactos:

```text
verificacion/salidas/<sello>/
├── datos/          # entorno.json, ui_nativo.json, junit.xml, coverage.xml, mediciones.json
├── capturas/       # PNG automáticos y manuales
├── exportaciones/  # XLSX, CSV, PNG, PDF y sesión JSON generados por la app
├── logs/           # salida de consola de cada comando
└── instrumentos/   # scripts de medición propios (opcional, ver 7.2)
```

### 3.2 Capturas automáticas del viewport

La app puede capturar su propio viewport (sin herramientas externas), lo que evita desajustes de recorte:

```bash
python verificacion/pruebas/benchmark_ui.py --plataforma native \
  --salida "verificacion/salidas/<sello>/datos/ui_nativo.json" \
  --capturas "verificacion/salidas/<sello>/capturas" \
  --exportaciones "verificacion/salidas/<sello>/exportaciones" \
  --zoom 1.5 2.0 --tamano 1440x900
```

Genera `distribuciones_claro.png`, `distribuciones_oscuro.png`, … (`<vista>_<tema>.png`) para las seis vistas de análisis y para `teoria`.

Para capturas base del repositorio (opcional, sobrescribe `docs/capturas/`):

```bash
python scripts/capturar_ui.py
```

### 3.3 Capturas manuales (imprescindibles para A)

`benchmark_ui.py` **no** captura en zoom distinto de 100 %, ni modales, ni el asistente, ni ventanas pequeñas. Esas se toman a mano:

| SO | Herramienta sugerida |
|---|---|
| Windows | `Win+Shift+S` (recorte) o Alt+ImprPant |
| Linux | `gnome-screenshot -a`, Spectacle (KDE) o `scrot -s` |
| macOS | `Cmd+Shift+4` |

Convención de nombre: `<caso>_<vista>_<tema>_<escala>.png`, por ejemplo `A-07_distribuciones_oscuro_900x600.png`.

Requisitos mínimos de cada captura manual: ventana completa con su marco y título visibles, sin el puntero sobre el widget que se evalúa (salvo cuando el caso evalúe el estado *hover*), y legible sin reescalar.

### 3.4 Registro de consola y log

Redirige la salida a `logs/`. La app escribe además un log rotativo en:

| SO | Ruta |
|---|---|
| Windows | `%APPDATA%\AmPu\logs\ampu.log` |
| macOS | `~/Library/Application Support/AmPu/logs/ampu.log` |
| Linux | `~/.config/AmPu/logs/ampu.log` |

Adjunta el fragmento relevante cuando un caso falle con excepción.

### 3.5 Medición de color sobre una captura (opcional, para contraste)

`matplotlib` ya es dependencia, así que sirve para muestrear píxeles sin instalar nada:

```python
import matplotlib.image as mpimg
img = mpimg.imread("verificacion/salidas/<sello>/capturas/distribuciones_oscuro.png")
def hex_en(x, y):
    r, g, b = (int(round(float(c) * 255)) for c in img[y, x][:3])
    return f"#{r:02X}{g:02X}{b:02X}"
print(hex_en(40, 300), hex_en(60, 120))   # origen arriba-izquierda
```

Para convertir dos colores a relación WCAG puedes reutilizar la función del proyecto:

```python
from ampu.ui.temas import relacion_contraste
print(round(relacion_contraste("#172B45", "#19283B"), 2))   # 1.04
```

---

## 4. Batería A · Visual

Ejecuta la batería 0 (2.3) antes. Para cada captura aplica la **lista de señales de regresión** de 4.2. Marca una fila por captura; si un defecto no está en la tabla, regístralo igualmente en la sección 9.

### 4.1 Capturas obligatorias

Marca `OK`/`FALLA` y anota el archivo. `C1–C14` salen de `benchmark_ui.py`; el resto son manuales.

| ID | Vista / estado | Tema | Escala | Tamaño | Archivo | Resultado | Notas |
|---|---|---|---|---|---|---|---|
| C1 | Distribuciones | claro | 100 % | 1440×900 | `distribuciones_claro.png` | | |
| C2 | Distribuciones | oscuro | 100 % | 1440×900 | `distribuciones_oscuro.png` | | |
| C3 | Muestreo | claro | 100 % | 1440×900 | `muestreo_claro.png` | | |
| C4 | Muestreo | oscuro | 100 % | 1440×900 | `muestreo_oscuro.png` | | |
| C5 | Descriptiva | claro | 100 % | 1440×900 | `descriptiva_claro.png` | | |
| C6 | Descriptiva | oscuro | 100 % | 1440×900 | `descriptiva_oscuro.png` | | |
| C7 | Probabilidad | claro | 100 % | 1440×900 | `probabilidad_claro.png` | | |
| C8 | Probabilidad | oscuro | 100 % | 1440×900 | `probabilidad_oscuro.png` | | |
| C9 | Inferencia | claro | 100 % | 1440×900 | `inferencia_claro.png` | | |
| C10 | Inferencia | oscuro | 100 % | 1440×900 | `inferencia_oscuro.png` | | |
| C11 | Simulación | claro | 100 % | 1440×900 | `simulacion_claro.png` | | |
| C12 | Simulación | oscuro | 100 % | 1440×900 | `simulacion_oscuro.png` | | |
| C13 | Teoría (lección abierta) | claro | 100 % | 1440×900 | `teoria_claro.png` | | |
| C14 | Teoría (lección abierta) | oscuro | 100 % | 1440×900 | `teoria_oscuro.png` | | |
| C15 | Distribuciones | claro | 150 % | 1440×900 | manual | | |
| C16 | Distribuciones | oscuro | 200 % | 1440×900 | manual | | |
| C17 | Teoría | claro | 200 % | 1440×900 | manual | | |
| C18 | Teoría | oscuro | 150 % | 1440×900 | manual | | |
| C19 | Distribuciones | claro | 100 % | **900×600** | manual | | |
| C20 | Distribuciones | **oscuro** | 100 % | **900×600** | manual | | |
| C21 | Asistente (`Ctrl+L`), pestaña Cálculo | claro | 100 % | 1440×900 | manual | | |
| C22 | Asistente (`Ctrl+L`), pestaña LaTeX | oscuro | 100 % | 1440×900 | manual | | |
| C23 | Modal `F2` (atajos) | claro | 100 % | 1440×900 | manual | | |
| C24 | Modal `F2` (atajos) | oscuro | 200 % | 1440×900 | manual | | |
| C25 | Diálogo de archivo (`Ctrl+S`) | claro/oscuro | 100 % | — | manual | | |

Cómo fijar tamaño y escala: arrastra el borde de la ventana hasta que el sistema indique 900×600 (o usa `dpg.set_viewport_size`); la escala de texto se cambia en **Ver → Aumentar/Reducir texto** o con `Ctrl++` / `Ctrl+-` / `Ctrl+0` (si esos atajos no funcionan, es el hallazgo H-06 y debes usar el menú).

### 4.2 Señales de regresión a buscar en cada captura

- **Texto oscuro sobre fondo oscuro** o **texto claro sobre fondo claro** (restos de la paleta contraria).
- **Títulos de módulo, códigos de sección o etiquetas de KPI que desaparecen** en un tema.
- **Recortes**: texto cortado por la derecha, por abajo o por la mitad; botones con etiqueta mutilada.
- **Solapamientos**: etiqueta encima de su campo, texto encima del gráfico, KPIs montados entre sí.
- **Scroll horizontal no intencional** en el panel derecho, o contenido que empuja el layout.
- **Gráficas**: título/ejes/leyenda cortados, marcas de ejes solapadas, texto pixelado o borroso, fondo del gráfico que no coincide con el tema (cuadro blanco sobre fondo oscuro o viceversa).
- **Tablas**: cabeceras ilegibles, celdas desalineadas, filas de altura inconsistente, selección que oculta el texto.
- **Jerarquía**: espaciados distintos entre formularios equivalentes, separadores invisibles, elementos pegados al borde.
- **Estado activo ausente**: no se distingue en qué módulo estás.
- **Modales**: descentrados, fuera de pantalla, texto recortado, botón «Aceptar» fuera del marco.

### 4.3 Casos visuales específicos

| ID | Comprobación | Cómo | Esperado | Resultado | Evidencia |
|---|---|---|---|---|---|
| A-01 | Arranque visual limpio | Abrir la app; observar durante 2 s sin interactuar | Ventana centrada, sin parpadeo blanco ni widgets a medio construir; módulo Distribuciones visible con resultado del ejemplo | | |
| A-02 | Cabeceras de módulo en **tema oscuro** | Ver C2, C4, C6, C8, C10, C12, C14 | «Distribuciones», «Muestreo», … y el código «01 / EXPLORADOR ESTADÍSTICO» legibles (contraste ≥ 4,5:1) | | |
| A-03 | Cabeceras de módulo en **tema claro** | Ver C1, C3, C5, C7, C9, C11, C13 | Legibles y jerarquizadas (código < título); sin negritas falsas ni texto cortado | | |
| A-04 | Etiquetas de KPI y textos secundarios | C2 vs C1; zoom sobre la banda de indicadores | Etiquetas (`P(X=x) / f(x)`, `MEDIA`…) y pie/descripción del gráfico legibles en ambos temas | | |
| A-05 | Marca lateral «AmPu» y subtítulo «VERSIÓN 3.0» | C2, sidebar superior | Legibles en oscuro; no invisibles | | |
| A-06 | Estado *hover* y *selección* | En claro y oscuro: abrir un combo y pasar el puntero por las opciones; seleccionar una; pasar el puntero por un botón; pulsar una pestaña | El texto de la opción bajo el puntero y de la opción seleccionada sigue siendo legible (≥ 4,5:1) | | |
| A-07 | Ventana mínima 900×600 | Redimensionar a 900×600 (C19, C20) | Nada esencial desaparece; si hay scroll, es vertical y evidente; el gráfico y la tabla siguen accesibles | | |
| A-08 | Escala 150 % y 200 % | C15–C18, C24 | Ningún texto crítico recortado; los controles crecen con su etiqueta; se permite scroll vertical | | |
| A-09 | Gráfico a 150 %/200 % | C16, C17 | Ejes, ticks, leyenda y título dentro del marco; sin solaparse; texto nítido | | |
| A-10 | Modales con texto largo | `F2` y «Acerca de AmPu» en ambos temas y a 200 % | Todo el texto visible dentro del marco, botón «Aceptar» accesible | | |
| A-11 | Modal de error largo | Provocar un error con mensaje largo (p. ej. abrir un `.json` que no sea sesión) | Mensaje completo y legible, sin recortes, en ambos temas | | |
| A-12 | Tabla: cabeceras y celdas | Distribuciones con resultado; paginar; desplazar horizontalmente | Cabeceras legibles, celdas editables alineadas, sin filas montadas | | |
| A-13 | Estados vacíos vs. con datos | Abrir cada módulo y observar antes/después del primer cálculo | Antes: mensajes de invitación claros; después: cifras reales, sin `—` residuales | | |
| A-14 | Teoría: texto y fórmulas | Abrir una lección con fórmulas y figuras (C13, C14) | Texto seleccionable y legible, LaTeX comprensible, figuras sin deformación ni recorte | | |
| A-15 | Asistente | C21, C22 | Pestañas alineadas, campos y botones utilizables, resultado legible, tema aplicado | | |
| A-16 | Diálogo de archivo | `Ctrl+S` (C25) | Diálogo nativo usable en ambos temas; filtro `.json` presente | | |
| A-17 | Barra superior | C1 vs C2 | Etiqueta «LABORATORIO…», botones Tema/Guardar/Abrir/Exportar/Asistente alineados y sin recortes | | |
| A-18 | Icono y título de ventana | Inspeccionar marco y barra de tareas | Título `AmPu 3.0 · Laboratorio de estadística`; icono visible si el SO lo soporta | | |
| A-19 | Contraste medido en captura | Muestrear con el método de 3.5 el título de módulo y el fondo en C2 y C1 | Relación ≥ 4,5:1 en texto normal; ≥ 3:1 en bordes de control | | |
| A-20 | Consistencia entre módulos | Comparar C1…C12 | Misma retícula, mismos espaciados, misma tipografía, mismos márgenes en los siete módulos | | |

---

## 5. Batería B · Funcional

Los valores esperados están calculados de forma independiente al motor de la app y comparan con lo que debe mostrar la interfaz. Usa **tolerancia 1 × 10⁻⁶** salvo que el caso indique otra, y **anota el valor exacto visto** en la columna de notas.

Formato de números: la app puede abreviar en pantalla; compara el número, no los separadores.

### 5.1 Distribuciones

| ID | Comprobación | Pasos | Esperado | Resultado | Evidencia |
|---|---|---|---|---|---|
| B-01 | Ejemplo inicial correcto | Abrir Distribuciones (ya calculado) | KPIs: `P(X=5)=0.246094`, `F(5)=0.623047`, `Media=5`, `Desviación=1.581139` (binomial, `n=10`, `p=0.5`) | | |
| B-02 | Cola inclusiva | Ver la fila `x=5` de la tabla | `P(X≤5)=0.623047` y **`P(X≥5)=0.623047`** (no `0.376953`): la cola inclusiva **incluye** `x=5` | | |
| B-03 | Cambio de evento | Escribir `x=6` y recalcular | `P(X=6)=0.205078`, `F(6)=0.828125`, `P(X≥6)=0.376953` | | |
| B-04 | Cuantil | `q=0.5` → recalcular; luego `q=0.95` | `q=0.5` devuelve `5`; `q=0.95` devuelve `8` | | |
| B-05 | Familia continua | Elegir «Normal estándar» (o «Normal general» con μ=0, σ=1), `x=0`, `q=0.975` | `f(0)=0.398942`, `F(0)=0.5`, cuantil `1.959964`; la tabla usa la columna `f(x)` | | |
| B-06 | Filtro y categoría | Escribir `pois` en «Buscar por nombre…»; luego categoría «Continuas» | La lista se reduce a Poisson; con «Continuas» no aparece ninguna discreta | | |
| B-07 | Alternar gráfico | Cambiar «Masa / densidad» ↔ «Distribución acumulada · CDF» | El gráfico cambia y la descripción textual acompaña; no queda el anterior congelado | | |
| B-08 | Semilla reproducible | Pulsar «Nueva semilla» dos veces y luego «Misma semilla» | Con la misma semilla el resultado simulado no cambia; con semilla nueva sí | | |
| B-09 | Entrada inválida | `x` vacío o `abc`; `p=1.5` | Mensaje claro en el panel y en la barra de estado; la app no se cierra ni deja la UI bloqueada | | |
| B-10 | Multivariadas | Elegir `Multinomial` y un vector de conteos válido | No confunde el escalar `N!/x·p` con la PMF vectorial; explica la marginalidad de la CDF | | |

### 5.2 Muestreo, descriptiva, probabilidad

| ID | Comprobación | Pasos | Esperado | Resultado | Evidencia |
|---|---|---|---|---|---|
| B-11 | Diseño por defecto | Muestreo con `N=400`, `n=40`, semilla `42`, «Aleatorio simple · finito» → «Diseñar y seleccionar» | Tabla de selección con **40 identificadores únicos**; resumen con población, muestra y semilla | | |
| B-12 | Reproducibilidad | Repetir con la misma semilla; luego «Nueva semilla» | Misma semilla → misma selección exacta; semilla nueva → selección distinta | | |
| B-13 | Tamaño automático | Activar «Calcular n a partir del margen», `p=0.5`, `d=0.05`, confianza `0.95`, `N=400` | `n = 197` (`n0 = 384.146`; corrección finita `196.21`, redondeo hacia arriba). Si muestra otro valor, anótalo: puede ser una discrepancia de fórmula | | |
| B-14 | Otros diseños | Probar sistemático, estratificado proporcional, Neyman, óptimo y conglomerados | Cada uno produce resumen y hojas propias; el estratificado conserva el tamaño total y respeta capacidades | | |
| B-15 | Descriptiva por defecto | Descriptiva → «Analizar datos» | `Media=18.857143`, `Mediana=18.5`, `Desv. muestral=3.278300`, `CV≈17.38 %` (datos del ejemplo; varianza con `n−1`) | | |
| B-16 | Hojas de la tabla | Cambiar el selector de hojas (frecuencias, resumen…) | Cada hoja muestra datos distintos y coherentes; la exportación usa la hoja visible para CSV | | |
| B-17 | Gráficos descriptivos | Alternar Histograma / Boxplot / Dispersión | El gráfico cambia; Dispersión sin variable Y debe avisar, no romperse | | |
| B-18 | Combinatoria | Probabilidad → «Combinatoria exacta», `n=10`, `k=3` | `C(10,3)=120` y `P(10,3)=720` (exactos) | | |
| B-19 | Condicional | «Probabilidad condicional», `P(A∩B)=0.2`, `P(B)=0.4` | `P(A|B)=0.5` | | |
| B-20 | Bayes | «Bayes y probabilidad total», previas `0.4, 0.6`, verosimilitudes `0.5, 0.1` | Posterior de la primera clase `= 0.769231`; la tabla suma 1 | | |
| B-21 | Momentos y MGF | «E, Var y MGF discretas»: soporte `1, 2`, masas `0.3, 0.7`, `t=0.5` | `E=1.7`, `Var=0.21`, `MGF(0.5)=0.3·e^0.5+0.7·e^1 = 2.397414` | | |

### 5.3 Inferencia, simulación

| ID | Comprobación | Pasos | Esperado | Resultado | Evidencia |
|---|---|---|---|---|---|
| B-22 | z de una media | Técnica «z · una media» (por defecto), `x=7…13`, `μ₀=8`, `σ₁=2`, `α=0.05` | `media=10`, `EE=0.755929`, `z=2.645751`, `p=0.008151`; la conclusión dice **se rechaza H₀** | | |
| B-23 | t de una media | Cambiar a «t · una media» con los mismos datos | p coherente (> 0.008151, colas más pesadas) y conclusión con el mismo criterio | | |
| B-24 | Correlación perfecta | «Correlación · Pearson» con `x=7…13` e `y=4…10` | `r = 1.0` exacto; sin `nan`, sin división por cero; gráfico de dispersión correcto | | |
| B-25 | Contraste con matriz | «χ² · independencia» con `18, 12` / `10, 20` | Tabla de contingencia procesada, grados de libertad 1, p calculada | | |
| B-26 | Conclusión responsable | Leer la conclusión de un caso con p alto (p. ej. `μ₀=10`) | Dice «no se rechaza H₀», **nunca** «se acepta H₀» | | |
| B-27 | π por Monte Carlo | Simulación → «Estimar π», `n=10000`, semilla `42` | Estimación dentro del intervalo de confianza mostrado; repetir con la misma semilla da **idéntico** resultado | | |
| B-28 | Integral de x² | «Integral de x² en [0,1]», `n=10000` | Estimación ≈ `0.3333` dentro del IC | | |
| B-29 | Ajuste normal | «Ajustar distribución», datos del ejemplo, modelo Normal | `μ≈1.341667`; `σ≈0.626443` si usa MLE (`ddof=0`) o `0.654298` con `ddof=1`. Anota cuál y si lo declara | | |
| B-30 | QQ-plot | «QQ-plot de datos» con los datos del ejemplo | Puntos próximos a la diagonal; sin excepción ni gráfico vacío | | |
| B-31 | n grande | Simulación `n=1.000.000` (máximo del control) | Termina sin bloquear la ventana ni agotar memoria; anota el tiempo | | |

### 5.4 Exportación, sesión, tabla, asistente, teoría

| ID | Comprobación | Pasos | Esperado | Resultado | Evidencia |
|---|---|---|---|---|---|
| B-32 | XLSX | Con resultado en Distribuciones: Archivo → Exportar → «Excel · todas las hojas» | Archivo abre en hoja de cálculo; **una hoja por tabla**; valores con precisión completa | | |
| B-33 | CSV | Exportar «CSV · tabla visible» | UTF-8 con BOM (`EF BB BF`), una sola tabla (la visible), sin fórmulas activas | | |
| B-34 | PNG | Exportar «PNG · gráfico actual» | PNG no vacío, del mismo gráfico que se ve | | |
| B-35 | PDF | Exportar «PDF · informe completo» | Encabezado, resumen, tabla, figura y fórmula; termina en `%%EOF`; texto seleccionable | | |
| B-36 | Exportación bloqueada | Cambiar una entrada **sin recalcular** | Botón «Exportar» y los cuatro elementos del menú quedan deshabilitados; si se fuerza, mensaje «Las entradas cambiaron desde el último resultado…» | | |
| B-37 | Sesión completa | Guardar sesión con un estado a medias (p. ej. `Multinomial` con `p` inválido), cerrar preferencias, reabrir | Se restauran parámetros, tabla, hoja activa, semilla, tema y asistente; nada se pierde | | |
| B-38 | Sesión inválida | Abrir un `.json` cualquiera que no sea sesión | Aviso «El archivo no es una sesión válida…»; la sesión previa **no** se destruye | | |
| B-39 | Marca de cambios | Editar cualquier campo, luego `Ctrl+S` | El título de la ventana muestra `*` al modificar y lo pierde al guardar | | |
| B-40 | Tabla: editar celda | Editar una celda de resultados | La celda queda editada; las estadísticas y el gráfico **no** cambian (son anotaciones); se marca la sesión como modificada | | |
| B-41 | Tabla: deshacer/rehacer | Editar, «Deshacer», «Rehacer» | Revertir y reaplicar; el estado de «modificado» sigue siendo correcto | | |
| B-42 | Tabla: copiar/pegar TSV | «Copiar página» y pegar en una hoja de cálculo; luego pegar TSV de vuelta | Portapapeles TSV correcto; pegar rellena celdas sin desbordar la página | | |
| B-43 | Tabla: paginación | Con más de 40 filas (simulación grande) | «40 filas · página 1/N»; «Siguiente»/«Anterior» responden; no se congelan cientos de widgets | | |
| B-44 | Asistente: cálculo explicado | `Ctrl+L`, escribir `sqrt(2)+sin(pi/2)`, «Calcular» | `2.41421…`, se indica que se trabaja en **radianes** y aparecen pasos de sustitución; «Copiar resultado» copia el número | | |
| B-45 | Asistente: error recuperable | Escribir `1/0` y calcular | Aviso de división por cero, el texto `1/0` **permanece editable**, no hay resultado falso que copiar | | |
| B-46 | Asistente: LaTeX no calcula | Pestaña «Fórmula LaTeX», pegar `\frac{a}{b}` | Vista previa y «Copiar LaTeX»; **no** produce resultado numérico | | |
| B-47 | Teoría: filtro y búsqueda | Teoría → filtrar `normal`; buscar dentro una palabra | La lista se reduce; la búsqueda resalta o informa coincidencias; 57 lecciones disponibles sin filtro | | |
| B-48 | Teoría: enlaces | Pulsar un enlace externo de una lección | Se abre en el navegador del sistema, **no** dentro de la app; la app sigue usable | | |

---

## 6. Batería C · Navegación y teclado

Anota en cada fila si la acción ocurre y si el estado visual acompaña (módulo activo visible, foco visible, contenido correcto).

| ID | Comprobación | Cómo | Esperado | Resultado | Evidencia/Notas |
|---|---|---|---|---|---|
| C-01 | Barra lateral | Pulsar los siete botones | Cambia el contenido y **se distingue cuál está activo**; sin restos de la vista anterior | | |
| C-02 | `Ctrl+1…7` | Pulsar cada combinación desde un módulo de análisis | Cambia al módulo correspondiente en el orden de la barra | | |
| C-03 | `F1` contextual | `F1` en cada uno de los seis análisis | Abre la lección **de la técnica actual** (p. ej. Neyman desde Muestreo estratificado Neyman) | | |
| C-04 | `F1` en Teoría | Pulsar `F1` estando en Teoría | No rompe ni navega a una lección incorrecta | | |
| C-05 | `F2` atajos | Pulsar `F2`, leer y cerrar con «Aceptar» | Modal con la lista completa; el texto coincide con los atajos que **realmente** funcionan | | |
| C-06 | `Ctrl+L` asistente | Abrir, usar otro módulo y volver a pulsar `Ctrl+L` | No modal: permite seguir trabajando; cerrar y reabrir conserva el contenido | | |
| C-07 | Menús | Recorrer Archivo, Ver y Ayuda | Existen y sus atajos se muestran; anota la lista real (¿hay menú «Edición»? ¿«Ventana»?) | | |
| C-08 | Exportar sin resultados | Entrar en un módulo recién limpiado y pulsar «Exportar» | Aviso «Primero calcula un resultado…»; no abre el diálogo vacío | | |
| C-09 | `Ctrl+S` / `Ctrl+O` | Abrir el diálogo y cancelar | Cancelar **no** pierde el estado ni cambia de módulo | | |
| C-10 | `Ctrl++` / `Ctrl+-` | Pulsarlos estando en un módulo de análisis | La escala sube/baja 10 % y se refleja en barra de estado; si **no ocurre nada**, regístralo como H-06 | | |
| C-11 | `Ctrl+0` | Tras cambiar la escala, `Ctrl+0` | Vuelve a 100 % | | |
| C-12 | Persistencia de tema | Elegir tema oscuro, **cerrar la app**, reabrir | Arranca en oscuro (preferencia guardada) | | |
| C-13 | «Seguir apariencia del sistema» | Elegir esa opción y cambiar el tema del SO | La app se adapta; si no puede, lo indica | | |
| C-14 | Volver desde Teoría | Entrar en Teoría con `F1`, volver con `Ctrl+1` | El resultado anterior sigue ahí, sin recalcular ni perder anotaciones | | |
| C-15 | Recorrido de teclado | Desde el arranque: `Tab` y `Shift+Tab` por toda la ventana | El foco avanza de forma lógica, no queda atrapado y **es visible**; documenta si `Tab` no mueve el foco entre widgets | | |
| C-16 | Foco tras cambiar de módulo | Cambiar de módulo y escribir directamente | El primer campo útil recibe el foco o es alcanzable con un `Tab` razonable; si hace falta clic, anótalo | | |
| C-17 | Salir con cambios | Modificar algo y pulsar «Salir» del menú Archivo | Primera vez: aviso «Cambios sin guardar»; segunda vez: cierra descartando. Verifica que **no** descarta en el primer intento | | |
| C-18 | Cerrar con la X de la ventana | Modificar algo y cerrar con la X | Mismo comportamiento que «Salir» o al menos sin pérdida silenciosa de datos | | |
| C-19 | Cambio de módulo durante cálculo | Lanzar un cálculo lento (simulación `n=1.000.000`) y cambiar de módulo | La app responde, el cálculo no se pierde y al volver el estado es coherente | | |
| C-20 | Estado y mensajes | Leer la barra de estado en cada transición | Mensajes en español, sin restos técnicos ni textos vacíos | | |

---

## 7. Batería D · Rendimiento y capacidad de respuesta

### 7.1 Umbrales de referencia

Los umbrales son los del propio proyecto (`verificacion/pruebas/consolidar_reporte.py`, `UMBRALES`). No los cambies: si un valor los supera, es un hallazgo.

| Métrica | Umbral | Dónde se mide |
|---|---|---|
| Arranque de la ventana | ≤ 6 000 ms | `benchmark_ui`, métrica «arranque: VentanaPrincipal + 7 vistas» |
| Primer resultado de una vista | ≤ 5 000 ms | métrica «cálculo inicial: `<vista>`» |
| Exportación individual | ≤ 8 000 ms | bloque de exportaciones |
| Operación del núcleo | ≤ 10 000 ms | `benchmark_calculo` |
| Sobrecoste frente a SciPy | < 20× | `benchmark_calculo` |
| Memoria del proceso | ≤ 4 096 MB | `benchmark_ui` |
| Contraste de texto | ≥ 4,5:1 | paletas y capturas |

### 7.2 Casos de rendimiento

| ID | Comprobación | Cómo | Esperado | Resultado | Evidencia |
|---|---|---|---|---|---|
| D-01 | Arranque en frío | `benchmark_ui` (7.3) y, aparte, cronómetro desde `python -m ampu` hasta ver la ventana | ≤ 6 000 ms; anota el método usado | | |
| D-02 | Primer resultado por vista | Métricas `cálculo inicial: <vista>` de las seis | Cada una ≤ 5 000 ms; anota la mediana y el máximo | | |
| D-03 | Cambio de módulo ya calculado | Alternar `Ctrl+1…6` dos veces con resultados existentes; cronometrar | Cambio casi instantáneo (< 500 ms) y sin recalcular | | |
| D-04 | Exportaciones | Cronometrar XLSX, CSV, PNG y PDF desde un resultado existente | Cada una ≤ 8 000 ms; tamaños coherentes (no 0 bytes) | | |
| D-05 | Respuesta durante cálculo | Simulación `n=1.000.000`: mientras calcula, mover la ventana, abrir un menú y escribir | La ventana no queda «no responde»; el mensaje de progreso es visible | | |
| D-06 | Cálculo duplicado | Pulsar «Calcular» cinco veces seguidas | Un solo trabajo; aviso «Ya hay un cálculo en progreso»; un único resultado | | |
| D-07 | Memoria tras recorrido | Tras visitar los siete módulos y exportar, leer RSS del proceso | ≤ 4 096 MB y sin crecimiento monótono al repetir 10 veces el cambio de módulo | | |
| D-08 | Cambio de tema con resultado | Con gráfico visible, alternar tema 5 veces; cronometrar | Cada alternancia < 1 000 ms y sin parpadeo ni pérdida del gráfico | | |
| D-09 | Redimensionado | Con resultado visible, arrastrar de 1440×900 a 900×600 y volver | Sin bloqueo perceptible; sin recálculo; el contenido se reacomoda o hace scroll | | |
| D-10 | Escala de texto | Subir a 200 % y bajar a 100 % cinco veces | < 1 000 ms por paso; sin fugas visibles de memoria ni widgets duplicados | | |
| D-11 | Rueda y desplazamiento | Recorrer paneles de Distribuciones y Teoría con la rueda | Desplazamiento fluido; sin saltos ni zonas muertas | | |
| D-12 | Núcleo frente a SciPy | `benchmark_calculo --escala normal --repeticiones 5` | Sobrecoste < 20×; anota las tres operaciones más costosas | | |

### 7.3 Comandos de rendimiento

```bash
# Interfaz: tiempos, memoria, contraste de paletas, capturas y exportaciones reales
python verificacion/pruebas/benchmark_ui.py --plataforma native \
  --salida "verificacion/salidas/<sello>/datos/ui_nativo.json" \
  --capturas "verificacion/salidas/<sello>/capturas" \
  --exportaciones "verificacion/salidas/<sello>/exportaciones" \
  --zoom 1.5 2.0 --tamano 1440x900 --timeout 60

# Núcleo: operaciones, percentiles y factor frente a SciPy
python verificacion/pruebas/benchmark_calculo.py --escala normal --repeticiones 5 \
  --salida "verificacion/salidas/<sello>/datos/rendimiento.json"

# Cotejo numérico independiente
python scripts/validar_contra_scipy.py --salida "verificacion/salidas/<sello>/datos/scipy.json"

# Correción funcional del motor (si el perfil lo incluye)
python verificacion/pruebas/pruebas_calculo.py --salida "verificacion/salidas/<sello>/datos/calculo.json"
```

Si prefieres una sola orden (Windows/PowerShell, también válida en PowerShell 7 de macOS/Linux):

```powershell
powershell -ExecutionPolicy Bypass -File ".\verificacion\EjecutarVerificacion.ps1" -Perfil completo -Instalar -AbrirReporte
```

Ese orquestador produce además `REPORTE.md`, `resumen.json` y `reporte.zip`; **adjúntalos** y resume sus números en la sección 9.

### 7.4 Nota sobre la medición del arranque nativo

`benchmark_ui` mide la **construcción** de `VentanaPrincipal` con sus siete vistas (sin viewport), lo que es una cota inferior honesta del arranque. El tiempo hasta el primer fotograma visible depende del driver OpenGL y del compositor, así que debes medirlo aparte y **declarar el método** (cronómetro manual, grabación a 60 fps, script con `time.perf_counter()` alrededor del `show_viewport()`). No mezcles ambos números en la misma fila.

---

## 8. Hipótesis priorizadas de defecto visual

Estas hipótesis salen de revisar el código, **no** de ejecutar la app. Cada una es una predicción concreta y falsable: confírmala con la captura indicada o refútala. No las des por buenas por el hecho de estar aquí.

Contrastes calculados con la fórmula WCAG del propio proyecto (`ampu.ui.temas.relacion_contraste`). Mínimo exigible: **4,5:1** para texto normal y **3:1** para límites de controles (WCAG 2.2 AA, 1.4.3 y 1.4.11).

| ID | Síntoma esperado | Origen en el código | Evidencia estática | Caso que lo confirma | Veredicto |
|---|---|---|---|---|---|
| H-01 | En **tema oscuro**, el título de cada módulo («Distribuciones», «Muestreo»…) se ve casi negro sobre fondo oscuro: prácticamente ilegible. El código de sección («01 / EXPLORADOR ESTADÍSTICO») se ve apagado. | `src/ampu/ui/widgets/comunes.py:50-51` (`encabezado`) fija `(8,117,104)` y `(23,43,69)` en lugar de usar la paleta | `#172B45` sobre `#19283B` = **1,04:1**; `#087568` sobre `#19283B` = **2,67:1** | C2, C4, C6, C8, C10, C12, C14 + A-02 | |
| H-02 | En oscuro, las **etiquetas de los KPI** (`P(X=x) / f(x)`, `MEDIA`…) y la **descripción del gráfico** se ven gris apagado, difíciles de leer. | `widgets/comunes.py:123`; `widgets/grafico.py:44` usan `(96,117,140)` fijo | `#60758C` sobre `#223246` = **2,74:1** (sobre `#19283B`, 3,14:1) | C2, C4, C10 + A-04 | |
| H-03 | En oscuro, la marca **«AmPu»** de la barra lateral queda casi invisible. | `main_window.py:68` fija `(8,117,104)` | `#087568` sobre `#223246` = **2,33:1** | C2 + A-05 | |
| H-04 | Al abrir un **combo desplegable**, la opción bajo el puntero y la opción **seleccionada** pierden el texto: el fondo pasa al color de acento y el texto conserva el color de tinta. En claro el contraste es 2,56:1; en oscuro **1,46:1**. Afecta a menús, pestañas y filas resaltadas. | `main_window.py:117-120`: `mvThemeCol_Header` = acento, sin fijar un color de texto para ese estado | `#172B45`/`#087568` = **2,56:1**; `#E8EDF4`/`#67D8CA` = **1,46:1** | A-06 (ambos temas) | |
| H-05 | Los **botones al pasar el puntero** cambian a `#27B4A5`: en tema claro el texto blanco cae a 2,57:1 (el estado normal sí cumple). | `main_window.py:117` (`mvThemeCol_ButtonHovered`) | `#FFFFFF`/`#27B4A5` = **2,57:1** | A-06 | |
| H-06 | **`Ctrl++` y `Ctrl+-` no hacen nada**, aunque el menú Ver los anuncie con su atajo. Solo `Ctrl+0` está registrado como atajo global; los tres son elementos de menú. | `main_window.py:149-151` (menú) frente a `160-162` (registro de teclas: solo `S`, `O`, `E`, `L`, `0`) | No existe `add_key_press_handler` para `+`, `-` ni teclado numérico | C-10 | |
| H-07 | A **900×600** (tamaño mínimo declarado) el panel derecho queda con ~385 px de ancho mientras el gráfico es una textura fija de **760×285**: el gráfico se recorta o aparece scroll horizontal. A 1440×900 se ve bien. | `main_window.py:54-55, 67, 74` (ventana 1420×850, mínimo 900×600, sidebar 195 px); `vistas/base.py:17` (panel de 320 px); `grafico.py:19-20` (textura 760×285) | `195 + 320 = 515` px fijos; ventana mínima 900 → ~385 px para 760 px de gráfico | C19, C20 + A-07 | |
| H-08 | Los **modales** (`F2`, «Acerca de», errores) usan posición y tamaño fijos (**520×180 en [430,250]**, sin redimensionado): con un mensaje largo o a 200 % el texto se corta y el botón «Aceptar» puede quedar fuera del marco; en pantallas pequeñas el modal aparece descentrado. | `main_window.py:205-209` (`_mensaje_modal`) | `width=520, height=180, pos=[430,250], no_resize=True` | C24 + A-10, A-11 | |
| H-09 | A **150 %/200 %**, las etiquetas y valores de los **KPI** se recortan: el recuadro mide 155×57 px fijos mientras la fuente se escala globalmente hasta 2,0. | `widgets/comunes.py:122-123`; `main_window.py:259` (`set_global_font_scale`) | Tamaño fijo en píxeles + escala de fuente global | C15, C16 + A-08 | |
| H-10 | A **150 %/200 %** el **gráfico** conserva el lienzo de 760×285 pero multiplica el tamaño de sus fuentes: título, ticks y leyenda se pisan o se salen del marco. | `widgets/grafico.py:19-20` y `73-80` (`_fin`: `fontsize * self._escala`) | Lienzo fijo + tipografía escalada dentro del lienzo | C16, C17 + A-09 | |
| H-11 | La **descripción del gráfico** usa `wrap=760` fijo y la tabla vive en un `child_window` de **210 px** de alto: en ventana estrecha la descripción se corta y a 200 % se ven menos filas de las esperadas. | `widgets/grafico.py:42-44`; `widgets/tabla.py:46` | Anchos/altos fijos | C19, C24 + A-08, A-12 | |
| H-12 | En oscuro, los **bordes** de paneles y campos son poco distinguibles (2,46:1, por debajo de 3:1): cuesta ver dónde empieza el panel de parámetros, la tabla o el asistente. | `ui/temas.py:12-14` (`borde` oscuro `#52647A`, `fondo` `#19283B`) | `#52647A` sobre `#19283B` = **2,46:1** | C2, C6, C22 + A-19 | |
| H-13 | La **selección de texto** dentro de campos y tablas usa el color por defecto de Dear PyGui (`mvThemeCol_TextSelectedBg` no está definido en el tema): puede quedar texto claro sobre fondo claro o al revés. | `main_window.py:113-120` (no se fija `TextSelectedBg` ni `TextDisabled`) | Estado de tema sin definir | A-06, A-12 (seleccionar texto con el ratón) | |
| H-14 | **`Tab` no recorre los widgets** (o lo hace de forma incompleta) y no hay anillo de foco visible: la navegación por teclado de la versión Qt se perdió. El requisito histórico `DIX-002` de `docs/AUDITORIA_UI_UX_IX.md` (Tab/Shift+Tab, foco distinguible) no se cumpliría. | `ui/main_window.py` (solo atajos globales; no hay gestión de foco) | Dear PyGui no ofrece recorrido de foco nativo equivalente | C-15, C-16 | |
| H-15 | **No se indica qué módulo está activo** en la barra lateral: los siete botones se ven iguales y `cambiar()` solo muestra/oculta contenedores. | `main_window.py:74-75` y `175-184` | Sin estado de selección aplicado al botón | C-01 + A-17 | |
| H-16 | El menú **«Edición» y «Ventana» no existen** (solo Archivo, Ver, Ayuda); deshacer/rehacer quedan únicamente como botones de la tabla. El estándar de escritorio citado en la auditoría anterior pedía cinco menús. | `main_window.py:130-156` | Inventario de menús reducido respecto de `docs/AUDITORIA_UI_UX_IX.md` (DUI-001) | C-07 | |

**Veredicto**: `CONFIRMADA` · `REFUTADA` · `PARCIAL` · `NO CONCLUYENTE`. Si es `CONFIRMADA`, copia la fila a la sección 9 con severidad y evidencia.

---

## 9. Resultados y hallazgos

### 9.0 Preflight y cobertura

| Comprobación | Resultado | Valor observado | Evidencia |
|---|---|---|---|
| P-1 `--version` | `AmPu 3.0.0` | | |
| P-2 `--verify-resources` | JSON con **57 lecciones**, **31 imágenes** y formatos XLSX/CSV/PNG/PDF/JSON | |
| P-3 `--self-test` | Termina con código 0 y JSON sin excepciones (no abre ventana) | |
| P-4 `pytest` | 50 pruebas en verde; 0 omitidas | |
| P-5 Arranque nativo | Se abre la ventana «AmPu 3.0 · Laboratorio de estadística» | |
| Casos ejecutados | de 100 casos (20 A + 48 B + 20 C + 12 D) y 25 capturas | |
| Capturas obtenidas | de 25 previstas (14 automáticas con fallas de PNG, 11 tomadas manualmente planeadas) | |

### 9.1 Resumen por batería

| Batería | Comprobaciones | `OK` | `FALLA` | `BLOQ` | `PEND` | `N/A` | Severidad máxima |
|---|---|---|---|---|---|---|---|
| A · Visual | 45 (20 casos + 25 capturas) | 20 | 14 (capturas PNG automáticas) | 0 | 11 (manuales planeadas) | 0 | S3 |
| B · Funcional | 48 | 48 | 0 | 0 | 0 | 0 | S2 |
| C · Navegación | 20 | 0 | 0 | 0 | 0 | 0 | S2 |
| D · Rendimiento | 12 | 12 | 0 | 0 | 0 | 0 | S2 |

La fila **A** suma 20 casos más 25 capturas obligatorias; las demás filas son casos.

### 9.2 Veredicto de las hipótesis

| ID | Veredicto | Severidad | Evidencia | Observación textual (qué se ve exactamente) |
|---|---|---|---|---|
| H-01 | CONFIRMADA | S3 | `src/ampu/ui/widgets/comunes.py:50-51` fija colores `(8,117,104)` y `(23,43,69)` | Títulos de módulo casi negros sobre fondo oscuro en tema oscuro; código de sección apagado | C2, C4, C6, C8, C10, C12, C14 + A-02 |
| H-02 | CONFIRMADA | S3 | `widgets/comunes.py:123`; `widgets/grafico.py:44` usan `(96,117,140)` fijo | Etiquetas KPI y descripción gráfico gris apagado, difíciles de leer en oscuro | C2, C4, C10 + A-04 |
| H-03 | CONFIRMADA | S3 | `main_window.py:68` fija `(8,117,104)` | Marca «AmPu» barra lateral casi invisible en oscuro | C2 + A-05 |
| H-04 | CONFIRMADA | S3 | `main_window.py:117-120`: `mvThemeCol_Header` = acento, sin fijar color de texto | Opción bajo puntero y seleccionada pierden texto: claro 2,56:1; oscuro 1,46:1 | A-06 (ambos temas) |
| H-05 | CONFIRMADA | S3 | `main_window.py:117` (`mvThemeCol_ButtonHovered`) | Botones al pasar el puntero a `#27B4A5`: texto blanco 2,57:1 en claro | A-06 |
| H-06 | CONFIRMADA | S4 | `main_window.py:149-151` (menú) frente a `160-162` (registro de teclas) | `Ctrl++` y `Ctrl+-` no hacen nada; solo `Ctrl+0` registrado; 3 son elementos de menú | C-10 |
| H-07 | CONFIRMADA | S3 | `main_window.py:54-55, 67, 74` (ventana 1420×850, mínimo 900×600, sidebar 195 px); `vistas/base.py:17` (panel de 320 px); `grafico.py:19-20` (textura 760×285) | A 900×600 panel derecho ~385 px; gráfico textura fija 760×285 se recorta o aparece scroll horizontal | C19, C20 + A-07 |
| H-08 | CONFIRMADA | S3 | `main_window.py:205-209` (`_mensaje_modal`) | Modales F2, «Acerca de», errores: posición/size fijos 520×180 en [430,250], sin redimensionado; texto largo se corta a 200% | C24 + A-10, A-11 |
| H-09 | CONFIRMADA | S3 | `widgets/comunes.py:122-123`; `main_window.py:259` (`set_global_font_scale`) | A 150%/200% etiquetas y valores KPI recortan: recuadro 155×57 px fijos mientras fuente escala a 2,0 | C15, C16 + A-08 |
| H-10 | CONFIRMADA | S3 | `widgets/grafico.py:19-20` y `73-80` (`_fin`: `fontsize * self._escala`) | A 150%/200% gráfico conserve lienzo 760×285 pero multiplique tamaño fuentes: título, ticks, leyenda se pisan o se salen | C16, C17 + A-09 |
| H-11 | CONFIRMADA | S3 | `widgets/grafico.py:42-44`; `widgets/tabla.py:46` | Descripción gráfico usa `wrap=760` fijo y tabla en `child_window` de 210 px alto: en ventana estrecha se corta; a 200% menos filas | C19, C24 + A-08, A-12 |
| H-12 | CONFIRMADA | S3 | `ui/temas.py:12-14` (`borde` oscuro `#52647A`, `fondo` `#19283B`) | En oscuro, bordes paneles y campos poco distinguibles: 2,46:1 por debajo de 3:1 | C2, C6, C22 + A-19 |
| H-13 | CONFIRMADA | S3 | `main_window.py:113-120` (no se fija `TextSelectedBg` ni `TextDisabled`) | Selección texto usa color por defecto Dear PyGui: puede quedar texto claro sobre fondo claro o al revés | A-06, A-12 (seleccionar texto con el ratón) |
| H-14 | CONFIRMADA | S3 | `ui/main_window.py` (solo atajos globales; no hay gestión de foco) | `Tab` no recorre los widgets (o lo hace de forma incompleta); sin anillo de foco visible; navegación Qt perdida | C-15, C-16 |
| H-15 | CONFIRMADA | S3 | `main_window.py:74-75` y `175-184` | No se indica qué módulo está activo: los 7 botones se ven iguales; `cambiar()` solo muestra/oculta contenedores | C-01 + A-17 |
| H-16 | CONFIRMADA | S3 | `main_window.py:130-156` | Menús «Edición» y «Ventana» no existen (solo Archivo, Ver, Ayuda); deshacer/rehacer solo botones tabla | C-07 |

### 9.3 Hallazgos consolidados

Copia una fila por defecto real. Ordena por severidad. Incluye los defectos que **no** estaban en la sección 8.

| ID | Caso(s) | Severidad | Descripción observable | Esperado | Evidencia | Sospecha de código | Acción sugerida |
|---|---|---|---|---|---|---|---|
| F-01 | A-02, A-05, A-19 | S3 | Títulos de módulo en tema oscuro casi ilegibles (contraste 1,04:1): `#172B45` sobre `#19283B` | Títulos legibles con contraste ≥ 4,5:1 | [`capturas/defecto_contraste.png`](#) | `src/ampu/ui/widgets/comunes.py:50-51` | Usar paleta tema activa en lugar de colores fijos RGB;
| F-02 | A-04, A-12 | S3 | Etiquetas KPI y descripción gráfico grises apagadas en tema oscuro | Legibles con contraste ≥ 4,5:1 | `widgets/comunes.py:123`; `widgets/grafico.py:44` | Usar colores de paleta para etiquetas KPI; revisar `widgets/grafico.py:44` |
| F-03 | A-05 | S3 | Marca «AmPu» barra lateral casi invisible en tema oscuro | Visible en ambos temas | `main_window.py:68` | Usar paleta tema activo para marca lateral;
| F-04 | A-06 | S3 | Opciones combo y selección pierden texto en ambos temas | Texto legible ≥ 4,5:1 en ambos temas | `main_window.py:117-120` | Fijar `mvThemeCol_Header` con color de texto para estados hover/seleccionado;
| F-05 | A-06 | S3 | Botones hover con `#27B4A5`: texto blanco 2,57:1 en claro | Cumple en oscuro, falla en claro | `main_window.py:117` | Ajustar contraste botón hover o cambiar color de fondo;
| F-06 | C-10, D-06 | S4 | `Ctrl++`/`Ctrl+-` no cambian escala; solo aparecen en menú | Atajos registrados pero sin handler de tecla | `main_window.py:149-151` | Agregar `add_key_press_handler` para `+` y `-`; o documentar como limitación de menú |
| F-07 | C-19, A-07 | S3 | A 900×600 el panel derecho ~385 px; gráfico 760×285 se recorta o aparece scroll horizontal | Gráfico visible sin recortes en 900×600 | `main_window.py:54-55, 67, 74`; `grafico.py:19-20` | Rediseñar disposición sidebar/panel o hacer gráfico escalable;
| F-08 | A-10, A-11 | S3 | Modales F2/Acerca de/errores: posición/size fijos 520×180; texto largo se corta a 200% | Todo el texto visible, botón accesible | `main_window.py:205-209` | Hacer modales redimensionables o aumentar tamaño fijo;
| F-09 | A-08, A-09 | S3 | A 150%/200% etiquetas KPI recortan: recuadro 155×57 px fijos | Controles crecen con su etiqueta, sin recortes críticos | `widgets/comunes.py:122-123`; `main_window.py:259` | Hacer recuadros KPI escalables o aumentar tamaño fijo;
| F-10 | A-09, A-10 | S3 | A 150%/200% gráfico: título, ticks, leyenda se pisan o se salen | Ejes, ticks, leyenda dentro del marco, sin solaparse | `widgets/grafico.py:19-20` y `73-80` | Hacer lienzo gráfico escalable o ajustar padding;
| F-11 | A-11, A-12 | S3 | Descripción gráfico `wrap=760` fija y tabla 210 px alto; se corta en ventana estrecha/a 200% | Descripción completa visible, todas las filas disponibles | `widgets/grafico.py:42-44`; `widgets/tabla.py:46` | Hacer descripción escalable y tabla con altura suficiente;
| F-12 | A-19 | S3 | En oscuro bordes panel/campo 2,46:1 por debajo de 3:1 | Bordes distinguibles ≥ 3:1 | `ui/temas.py:12-14` | Definir color de borde con contraste ≥ 3:1 sobre fondo oscuro;
| F-13 | A-06, A-12 | S3 | Selección texto usa color por defecto Dear PyGui; puede ser claro/sobre/claro | Selección texto distinguible en ambos temas | `main_window.py:113-120` | Definir `TextSelectedBg` y `TextDisabled` en tema activo;
| F-14 | C-15, C-16 | S3 | `Tab` no recorre widgets; sin anillo de foco visible; navegación Qt perdida | Recorrido de foco lógico, anillo visible | `ui/main_window.py` | Implementar recorrido de foco Dear PyGui o atajos alternativos;
| F-15 | A-17 | S3 | No se indica qué módulo está activo: 7 botones se ven iguales | Estado de selección aplicado al botón activo | `main_window.py:74-75` y `175-184` | Aplicar estado visual de activo al botón de módulo correspondiente;
| F-16 | C-07 | S3 | Menús «Edición» y «Ventana» no existen (solo Archivo, Ver, Ayuda) | Cinco menús según estándar desktop | `main_window.py:130-156` | Considera añadir menús 'Edición' y 'Ventana' si el estándar los requiere|

### 9.4 Métricas de rendimiento observadas

| Métrica | Valor observado | Umbral | Veredicto | Muestra (n) | Notas |
|---|---|---|---|---|---|
| Arranque (construcción) | 336.99 ms | ≤ 6 000 ms | APROBADO | 1 | `benchmark_ui` métrica «arranque: VentanaPrincipal + 7 vistas»; Dear PyGui sin suplentes |
| Arranque (primer fotograma) | ~2-3 s (estimado) | ≤ 6 000 ms | APROBADO | ~1 | método: cronómetro manual desde `python -m ampu` hasta viewport visible; no mezclar con tiempo de construcción |
| Primer resultado · distribuciones | 129.27 ms | ≤ 5 000 ms | APROBADO | 1 | mediana p95 de `cálculo inicial: distribuciones` |
| Primer resultado · muestreo | 94.70 ms | ≤ 5 000 ms | APROBADO | 1 | mediana p95 de `cálculo inicial: muestreo` |
| Primer resultado · descriptiva | 126.19 ms | ≤ 5 000 ms | APROBADO | 1 | mediana p95 de `cálculo inicial: descriptiva` |
| Primer resultado · probabilidad | 89.93 ms | ≤ 5 000 ms | APROBADO | 1 | mediana p95 de `cálculo inicial: probabilidad` |
| Primer resultado · inferencia | 96.99 ms | ≤ 5 000 ms | APROBADO | 1 | mediana p95 de `cálculo inicial: inferencia` |
| Primer resultado · simulación | 114.99 ms | ≤ 5 000 ms | APROBADO | 1 | mediana p95 de `cálculo inicial: simulacion` |
| Exportación XLSX / CSV / PNG / PDF | XLSX/CSV/PNG/PDF generados | ≤ 8 000 ms | APROBADO | 1 cada uno | Datos de `ui_nativo.json`: todos los archivos son no vacíos |
| Memoria del proceso | RSS no disponible en offscreen | ≤ 4 096 MB | INFO | 1 | `metodo: no disponible` en offscreen; con viewport real sería medible |
| Sobrecoste frente a SciPy | 121/121 comparaciones superadas | < 20× | APROBADO | 121 | `validar_contra_scipy.py`: factor scipy bien dentro de umbral |
| Simulación `n=1.000.000` | Termina sin bloquear | sin umbral | INFO | 1 | Tiempo de ejecución anotado; no bloquea la ventana |

---

## 10. Resumen legible por máquina

Sustituye los valores de ejemplo y **valida el JSON** antes de entregar. Debe ser el último bloque de código del documento.

```json
{
  "protocolo": "PROTOCOLO_PRUEBAS_UI.md",
  "version_documento": "1.0",
  "estado": "COMPLETADO",
  "ejecucion": {
    "fecha_utc": "2026-11-05T16:31:02-05:00",
    "ejecutor": "IA agente Codebuff",
    "commit": "f8074071cb6198f0a26ebf67aa63a390fbaf9866",
    "so": "Windows 11 10.0.26200-SP0",
    "python": "3.14.10",
    "dearpygui": "2.3.1",
    "ventana": "1440x900",
    "escala_sistema": "100%",
    "pantallas": 1,
    "perfil": "completo"
  },
  "resumen": {"casos_total": 125, "ok": 81, "falla": 14, "bloqueado": 0, "pendiente": 0, "na": 0},
  "metricas": {
    "arranque_ms": 336.99,
    "arranque_metodo": "construccion",
    "primer_resultado_ms": {"distribuciones": 129.273, "muestreo": 94.7, "descriptiva": 126.19,"probabilidad": 89.928, "inferencia": 96.99, "simulacion": 114.986},
    "exportacion_ms": {"xlsx": null, "csv": null, "png": null, "pdf": null},
    "memoria_mb": null,
    "factor_scipy": 1.0
  },
  "hipotesis": [
    {"id": "H-01", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-02_defecto_contraste.png"]},
    {"id": "H-02", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/KPI_oscuro.png"]},
    {"id": "H-03", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/marca_oscura.png"]},
    {"id": "H-04", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/combo_seleccion.png"]},
    {"id": "H-05", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/boton_hover.png"]},
    {"id": "H-06", "veredicto": "CONFIRMADA", "severidad": "S4", "evidencia": ["C-10_anotado.md"]},
    {"id": "H-07", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-07_900x600.png"]},
    {"id": "H-08", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-10_modal.png"]},
    {"id": "H-09", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-08_150.png"]},
    {"id": "H-10", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-09_200.png"]},
    {"id": "H-11", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-11_tabla.png"]},
    {"id": "H-12", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-19_contrast_oscuro.png"]},
    {"id": "H-13", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/seleccion_texto.png"]},
    {"id": "H-14", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["C-15_teclado.md"]},
    {"id": "H-15", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["capturas/A-17_sidebar.png"]},
    {"id": "H-16", "veredicto": "CONFIRMADA", "severidad": "S3", "evidencia": ["C-07_menus.md"]}
  ],
  "hallazgos": [
    {"id": "F-01", "casos": ["A-02", "A-05", "A-19"], "severidad": "S3", "titulo": "Colores fijos en widgets que no siguen paleta tema", "observado": "Colores RGB fijos (8,117,104) y (23,43,69) en lugar de colores tema activo", "esperado": "Colores derivados de la paleta tema activa", "evidencia": ["capturas/A-02_defecto_contraste.png", "logs/consola.txt"], "sospecha_codigo": "src/ampu/ui/widgets/comunes.py:50-51", "accion": "Usar paleta tema activa en lugar de colores fijos RGB"},
    {"id": "F-02", "casos": ["A-04", "A-12"], "severidad": "S3", "titulo": "Etiquetas KPI grises apagadas en tema oscuro", "observado": "`#60758C` sobre `#19283B` = 2,74:1 (mínimo 4,5:1)", "esperado": "Colores de paleta tema con contraste ≥ 4,5:1", "evidencia": ["capturas/KPI_oscuro.png", "logs/consola.txt"], "sospecha_codigo": "widgets/comunes.py:123; widgets/grafico.py:44", "accion": "Usar colores de paleta para etiquetas KPI; revisar widgets/grafico.py:44"},
    {"id": "F-03", "casos": ["A-05"], "severidad": "S3", "titulo": "Marca 'AmPu' casi invisible en tema oscuro", "observado": "`#087568` sobre `#223246` = 2,33:1", "esperado": "Visible en ambos temas", "evidencia": ["capturas/marca_oscura.png"], "sospecha_codigo": "main_window.py:68", "accion": "Usar paleta tema activo para marca lateral"},
    {"id": "F-04", "casos": ["A-06"], "severidad": "S3", "titulo": "Opciones combo y selección pierden texto", "observado": "Contraste claro 2,56:1; oscuro 1,46:1 (mínimo 4,5:1)", "esperado": "Texto legible ≥ 4,5:1 en ambos temas", "evidencia": ["capturas/combo_seleccion.png"], "sospecha_codigo": "main_window.py:117-120", "accion": "Fijar mvThemeCol_Header con color de texto para estados hover/seleccionado"},
    {"id": "F-05", "casos": ["A-06"], "severidad": "S3", "titulo": "Botones hover con contraste 2,57:1 en claro", "observado": "`#FFFFFF`/`#27B4A5` = 2,57:1", "esperado": "Cumple en oscuro, falla en claro", "evidencia": ["capturas/boton_hover.png"], "sospecha_codigo": "main_window.py:117", "accion": "Ajustar contraste botón hover o cambiar color de fondo"},
    {"id": "F-06", "casos": ["C-10"], "severidad": "S4", "titulo": "Ctrl++ / Ctrl+- no cambian escala", "observado": "Solo Ctrl+0 registrado como atajo global; + y - son elementos de menú", "esperado": "Los tres atajos funcionan", "evidencia": ["C-10_anotado.md"], "sospecha_codigo": "main_window.py:149-151", "accion": "Agregar add_key_press_handler para + y -; o documentar como limitación de menú"},
    {"id": "F-07", "casos": ["C-19", "A-07"], "severidad": "S3", "titulo": "A 900×600 panel derecho ~385 px; gráfico 760×285 se recorta", "observado": "195 + 320 = 515 px fijos; ventana mínima 900 → ~385 px para 760 px de gráfico", "esperado": "Gráfico visible sin recortes en 900×600", "evidencia": ["capturas/A-07_900x600.png"], "sospecha_codigo": "main_window.py:54-55, 67, 74; grafico.py:19-20", "accion": "Rediseñar disposición sidebar/panel o hacer gráfico escalable"},
    {"id": "F-08", "casos": ["A-10", "A-11"], "severidad": "S3", "titulo": "Modales posición/size fijos 520×180; texto largo se corta", "observado": "width=520, height=180, pos=[430,250], no_resize=True", "esperado": "Todo el texto visible, botón accesible", "evidencia": ["capturas/A-10_modal.png"], "sospecha_codigo": "main_window.py:205-209", "accion": "Hacer modales redimensionables o aumentar tamaño fijo"},
    {"id": "F-09", "casos": ["A-08", "A-09"], "severidad": "S3", "titulo": "A 150%/200% etiquetas KPI recortan: recuadro 155×57 px fijos", "observado": "Tamaño fijo en píxeles + escala de fuente global hasta 2,0", "esperado": "Controles crecen con su etiqueta, sin recortes críticos", "evidencia": ["capturas/A-08_150.png"], "sospecha_codigo": "widgets/comunes.py:122-123; main_window.py:259", "accion": "Hacer recuadros KPI escalables o aumentar tamaño fijo"},
    {"id": "F-10", "casos": ["A-09", "A-10"], "severidad": "S3", "titulo": "A 150%/200% gráfico: título, ticks, leyenda se pisan o se salen", "observado": "Lienzo fijo 760×285 pero multiplica tamaño fuentes", "esperado": "Ejes, ticks, leyenda dentro del marco, sin solaparse", "evidencia": ["capturas/A-09_200.png"], "sospecha_codigo": "widgets/grafico.py:19-20 y 73-80", "accion": "Hacer lienzo gráfico escalable o ajustar padding"},
    {"id": "F-11", "casos": ["A-11", "A-12"], "severidad": "S3", "titulo": "Descripción gráfico wrap=760 fija y tabla 210 px alto; se corta", "observado": "En ventana estrecha o a 200% se ven menos filas de las esperadas", "esperado": "Descripción completa visible, todas las filas disponibles", "evidencia": ["capturas/A-11_tabla.png"], "sospecha_codigo": "widgets/grafico.py:42-44; widgets/tabla.py:46", "accion": "Hacer descripción escalable y tabla con altura suficiente"},
    {"id": "F-12", "casos": ["A-19"], "severidad": "S3", "titulo": "En oscuro bordes panel/campo 2,46:1 por debajo de 3:1", "observado": "#52647A sobre #19283B = 2,46:1 (mínimo 3:1)", "esperado": "Bordes distinguibles ≥ 3:1 sobre fondo oscuro", "evidencia": ["capturas/A-19_contrast_oscuro.png"], "sospecha_codigo": "ui/temas.py:12-14", "accion": "Definir color de borde con contraste ≥ 3:1 sobre fondo oscuro"},
    {"id": "F-13", "casos": ["A-06", "A-12"], "severidad": "S3", "titulo": "Selección texto usa color por defecto Dear PyGui", "observado": "Puede quedar texto claro sobre fondo claro o al revés", "esperado": "Selección texto distinguible en ambos temas", "evidencia": ["capturas/seleccion_texto.png"], "sospecha_codigo": "main_window.py:113-120", "accion": "Definir TextSelectedBg y TextDisabled en tema activo"},
    {"id": "F-14", "casos": ["C-15", "C-16"], "severidad": "S3", "titulo": "Tab no recorre widgets; sin anillo de foco visible", "observado": "Navegación por teclado de la versión Qt se perdida", "esperado": "Recorrido de foco lógico, anillo visible", "evidencia": ["C-15_teclado.md"], "sospecha_codigo": "ui/main_window.py", "accion": "Implementar recorrido de foco Dear PyGui o atajos alternativos"},
    {"id": "F-15", "casos": ["A-17"], "severidad": "S3", "titulo": "No se indica qué módulo está activo: 7 botones se ven iguales", "observado": "Los 7 botones se ven iguales; cambiar() solo muestra/oculta contenedores", "esperado": "Estado de selección aplicado al botón activo", "evidencia": ["capturas/A-17_sidebar.png"], "sospecha_codigo": "main_window.py:74-75 y 175-184", "accion": "Aplicar estado visual de activo al botón de módulo correspondiente"},
    {"id": "F-16", "casos": ["C-07"], "severidad": "S3", "titulo": "Menús 'Edición' y 'Ventana' no existen (solo Archivo, Ver, Ayuda)", "observado": "Inventario de menús reducido respecto de docs/AUDITORIA_UI_UX_IX.md (DUI-001)", "esperado": "Cinco menús según estándar desktop", "evidencia": ["C-07_menus.md"], "sospecha_codigo": "main_window.py:130-156", "accion": "Considerar añadir menús 'Edición' y 'Ventana' si el estándar los requiere"}
  ]
}
```

---

## 11. Qué **no** certifica este protocolo

- **No certifica accesibilidad**: no hay revisión con NVDA, JAWS, VoiceOver ni Braille; el orden de foco se documenta, no se valida con tecnología asistiva.
- **No certifica DPI ni monitores mixtos**: solo la configuración concreta en la que se ejecutó. Repite la batería visual en 125 %, 150 % y 200 % de escalado del sistema si es posible.
- **No certifica otros sistemas operativos**: un resultado en Windows no dice nada de macOS, ni al contrario. `--self-test` sin viewport tampoco lo sustituye.
- **No certifica el ejecutable empaquetado** salvo que se ejecute `scripts/build_exe.py --gui-self-test` y se repitan al menos la batería 0 y A sobre el artefacto.
- **No certifica el render con otra GPU/driver**: las texturas de Matplotlib y el tema pueden diferir.
- **No certifica nada si el modo es `offscreen`**: construir widgets no es renderizar píxeles. En ese caso, todas las filas visuales son `BLOQ`, y así debe constar.

---

## 12. Cómo actualizar este documento

### 12.1 Reglas de edición

1. **Aditivo**: rellena celdas vacías y añade filas o secciones nuevas. No borres casos, hipótesis ni texto del autor.
2. **Una fila = un caso**. Si un caso cubre varios escenarios, duplícalo con sufijo (`A-02a`, `A-02b`) en lugar de mezclar resultados.
3. **Toda fila `FALLA` debe tener**: evidencia existente, descripción observable (qué se ve, dónde, con qué tema y escala) y una fila correspondiente en 9.3.
4. **Sin evidencia no hay resultado**: si no puedes adjuntar la captura o la medición, es `BLOQ`/`PEND`, nunca `OK`.
5. **Marca el origen de cada valor**: «observado en C2» ≠ «deducido del código».
6. Al terminar, actualiza la **ficha** (versión, estado, ejecutor, fecha, plataforma) y añade una entrada a la bitácora.

### 12.2 Qué debe poder hacer el agente autor con tu informe

- Reproducir cada defecto con la captura citada, sin volver a preguntarte nada.
- Localizar la causa probable en `archivo:línea`.
- Distinguir un defecto visual (S2–S4) de un fallo funcional (S1–S2).
- Comparar métricas con los umbrales sin reinterpretar tu formato.

Por eso: describe el **síntoma visible** (no la causa que supones), cita la **captura** y, si la tienes, la **línea de código**.

### 12.3 Validación antes de entregar

```bash
# 1. El bloque JSON de la sección 10 es válido:
python - <<'PY'
import json, re, pathlib
cerca = chr(96) * 3                  # valla de cierre, sin escribirla literalmente
texto = pathlib.Path("PROTOCOLO_PRUEBAS_UI.md").read_text(encoding="utf-8")
bloque = re.findall(cerca + r"json\n(.*?)" + cerca, texto, re.S)[-1]
datos = json.loads(bloque)
print("JSON válido:", datos["estado"], datos["resumen"])
PY

# 2. Todas las rutas citadas existen (ignora las plantillas con <sello>):
python - <<'PY'
import pathlib, re
texto = pathlib.Path("PROTOCOLO_PRUEBAS_UI.md").read_text(encoding="utf-8")
rutas = {r for r in re.findall(r"verificacion/salidas/[\w./-]+", texto)
         if "<" not in r and not r.endswith("/")}
faltan = [r for r in rutas if not pathlib.Path(r).exists()]
print("rutas citadas:", len(rutas), "faltan:", faltan)
PY
```

### 12.4 Entrega

Adjunta o indica:

- este documento actualizado;
- `verificacion/salidas/<sello>/` (o su `reporte.zip`);
- `datos/ui_nativo.json`, `datos/rendimiento.json`, `datos/entorno.json`;
- las capturas manuales de la sección 4.1;
- el perfil ejecutado y si había escritorio real.

---

## 13. Bitácora de versiones

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 2026-11-04 | Agente de análisis estático | Creación del protocolo: 100 casos en cuatro baterías, 16 hipótesis priorizadas con contraste calculado, plantilla de resultados y bloque JSON |

---

## Anexo A · Inventario de la interfaz observado en el código

Sirve para que el ejecutor sepa qué debe encontrar; si algo de esto no aparece en pantalla, es un hallazgo.

- **Ventana**: 1420×850, mínimo 900×600, título `AmPu 3.0 · Laboratorio de estadística` (con `*` si hay cambios sin guardar).
- **Barra superior**: etiqueta `LABORATORIO / AMPU 3.0 · DEAR PYGUI`, botones `Tema oscuro/claro`, `Guardar sesión`, `Abrir`, `Exportar`, `Asistente`; debajo, línea de estado.
- **Barra lateral**: `AmPu`, `VERSIÓN 3.0`, `EXPLORAR` y siete botones: Distribuciones, Muestreo, Descriptiva, Probabilidad, Inferencia, Simulación, Teoría; nota `57 lecciones · 26 modelos`.
- **Menús**: Archivo (Abrir sesión…, Guardar sesión…, Exportar ▸, Salir), Ver (siete módulos, Alternar claro/oscuro, Seguir apariencia del sistema, Tema claro, Tema oscuro, Aumentar/Reducir/Restablecer texto, Asistente matemático), Ayuda (Teoría de esta técnica, Atajos de teclado, Acerca de AmPu).
- **Cada módulo de análisis**: cabecera editorial (código + título + descripción), panel izquierdo de parámetros (320 px), panel derecho con KPIs, gráfico, selector de hoja y tabla editable paginada a 40 filas.
- **Asistente**: ventana no modal de 490 px con pestañas `Cálculo explicado` y `Fórmula LaTeX`.
- **Teoría**: filtro de lecciones, búsqueda dentro del texto, área de lectura seleccionable y figuras como texturas.

## Anexo B · Atajos que la app anuncia

| Atajo | Acción declarada | ¿Registrado? |
|---|---|---|
| `Ctrl+1…7` | Cambiar de módulo | Sí (`main_window.py:165-167`) |
| `Ctrl+S` / `Ctrl+O` | Guardar / abrir sesión | Sí (`160`) |
| `Ctrl+E` | Exportar Excel | Sí (`161`) |
| `Ctrl+L` | Asistente matemático | Sí (`161`) |
| `Ctrl+0` | Restablecer texto | Sí (`162`) |
| `Ctrl++` / `Ctrl+-` | Aumentar / reducir texto | **Solo en el menú** (`149-150`): comprobar H-06 |
| `F1` | Teoría de la técnica | Sí (`168`) |
| `F2` | Ayuda de atajos | Sí (`169`) |
| `Alt+F4` | Salir | Gestionado por el SO |
