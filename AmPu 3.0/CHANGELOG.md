# Registro de cambios

## Sin publicar · cierre de pendientes de 3.0

- Sesiones: se restauran las celdas editadas, el orden de filas y la hoja activa en las seis vistas; las otras hojas editadas ya no desaparecen al cambiar de pestaña. El motor recalcula indicadores/gráficos con la semilla guardada, sin confundir anotaciones de tablas con datos de entrada. Se descartan trabajos anteriores a una restauración, también al cargar una vista sin resultados.
- Tabla: orden numérico actualizado tras editar una celda; los valores originales de coma flotante e identificadores enteros mantienen su precisión al exportar, aunque el texto en pantalla esté abreviado.
- XLSX y CSV neutralizan fórmulas pegadas en celdas/cabeceras. Se agregaron pruebas de seguridad y regresión para sesiones, múltiples hojas, precisión y trabajos Qt asíncronos.
- La teoría rechaza solicitudes remotas en QWebEngine y sigue ofreciendo enlaces de referencia en el navegador externo. Si faltan bibliotecas nativas, la navegación muestra un error claro sin dejar la interfaz rota. Se añadió prueba de integración con Chromium real (omitida *solo* cuando faltan bibliotecas nativas) y autoprueba estricta `--self-test` de KaTeX, figura, CSS y tema oscuro.
- Autoprueba `--verify-resources` del ejecutable sin GUI; PyInstaller verifica versión, lecciones, figuras, fuentes, exportaciones, sesión JSON y helper/recursos de WebEngine después de compilar. Corregida la ruta de salida `--onedir` de Windows y añadidos iconos ICO/ICNS nativos. `--gui-self-test` exige verificación WebEngine en el SO de destino.
- En Python 3.12.11: **123 pruebas aprobadas, 1 WebEngine omitida por bibliotecas NSS/X11 ausentes, 92 % cobertura de core con ramas, 121/121 cotejos SciPy**. Builds Linux `--onefile` y `--onedir` verificados a nivel de recursos/exportaciones; sigue pendiente la prueba visual *en cada escritorio/SO real*. Ningún suplente nativo de pruebas forma parte del código ni del binario.

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
