# Registro de cambios

## 3.0.0 · 2026-10-26

### Nueva implementación

- Reescrita como aplicación de escritorio de **Python 3.12+**, PySide6 y Matplotlib QtAgg; código y datos nuevos aislados en `AmPu 3.0/`, sin modificar AmPu 2.0.
- Núcleo desacoplado de la GUI con API `Distribucion`, validación y errores de dominio centralizados; **26 modelos** (8 discretos, 18 continuos, incluidos los multivariados) registrados por metadatos y contrastados con SciPy.
- Siete pantallas: distribuciones, muestreo, descriptiva, probabilidad, inferencia, simulación/ajuste y biblioteca teórica. Cálculos costosos en hilos Qt, paletas claro/oscuro, calculadora científica interna y atajos de teclado.
- Muestreo simple/con reemplazo, sistemático, estratificado proporcional/Neyman/óptimo y conglomerados de una/dos etapas; cálculo de tamaños y tablas de selección con semillas locales reproducibles.
- Análisis descriptivo; combinatoria, Bayes y momentos; intervalos, 16 técnicas de contraste/regresión; simulación π/integrales/muestras, ajuste de cinco familias y QQ-plots.
- Exportador uniforme a **XLSX, CSV UTF-8, PNG y PDF**, más sesiones JSON versionadas y logging rotativo en datos de usuario.
- **57 lecciones** Markdown/LaTeX, **31 figuras**, KaTeX y STIX Two Math offline, índice/búsqueda/zoom en QWebEngineView; licencias de recursos incluidas.
- Script PyInstaller con hooks para recursos/QtWebEngine y capturas genuinas de la UI; documentación `README`, `PLAN`, `CONTRIBUTING` y `MIGRACION`.

### Convenciones que cambian respecto de Java

- Corrección de expectativas históricas erróneas: desviación de uniforme, cuantiles y colas de t/F/χ², tamaños muestrales y argumento multinomial. Véanse los cálculos y las pruebas en [MIGRACION.md](MIGRACION.md).
- Probabilidad superior discreta **incluye** el evento `x`; distribución exponencial parametrizada por **tasa** (`scale=1/tasa` en SciPy). La binomial negativa cuenta fracasos antes de `r` éxitos; la geométrica cuenta ensayos desde 1.
- Momentos y cuantiles multivariados etiquetados como **marginales** donde no existe cuantil conjunto canónico. La CDF de la normal bivariada es conjunta.
- Los archivos Java/Swing de la versión 2.0 no son sesiones JSON 3.0; se reintroducen parámetros manualmente.

### Verificación y limitaciones del entorno

- Python 3.12.11: **114 pruebas verdes**, **92 % de cobertura del núcleo con ramas**; **121/121** comparaciones independientes de SciPy. La interfaz Qt se probó en modo raster offscreen con bibliotecas suplentes externas al paquete.
- PyInstaller `--onedir` completado, `--version` del ejecutable y recursos/WebEngineProcess presentes. El sandbox Linux no trae el conjunto completo de bibliotecas nativas NSS/X11/OpenGL que exige QWebEngineView; **la lección dentro del motor web y el artefacto Linux como distribución real necesitan prueba visual en un escritorio completo**. El script no presupone compilación cruzada.
