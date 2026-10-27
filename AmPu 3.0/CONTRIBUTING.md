# Contribuir a AmPu 3.0

## Regla de aislamiento

El proyecto `AmPu 2.0` (los archivos Java, Swing, HTML, pruebas y recursos fuera de esta carpeta) es **referencia de solo lectura**. Agrega o cambia archivos **únicamente bajo `AmPu 3.0/`**. Si hay un resultado histórico incorrecto, conserva una prueba del resultado matemático correcto y documenta la diferencia en [MIGRACION.md](MIGRACION.md); no modifiques la expectativa para «hacerla pasar».

## Entorno

```bash
cd 'AmPu 3.0'
python3.12 -m venv .venv
. .venv/bin/activate            # PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m pytest
python -m pytest --cov=ampu.core --cov-branch --cov-report=term-missing
python scripts/validar_contra_scipy.py
```

La UI necesita bibliotecas Qt del sistema. En Linux headless, `QT_QPA_PLATFORM=offscreen` ejecuta las pruebas Qt si las bibliotecas nativas están presentes; si faltan, las pruebas correspondientes se omiten con una razón explícita. `test_webengine.py` prueba Chromium auténtico y **nunca** usa mocks; un skip indica validación visual *pendiente*, no éxito. `python -m ampu --self-test` falla en lugar de omitir. **No** integres los suplentes nativos del sandbox en este repositorio ni empaquetes una construcción hecha con ellos para usuarios. La cobertura de `core/` debe mantenerse **≥85 % con ramas**; la simulación aleatoria siempre se prueba con semilla.

## Organización y estilo

- `src/ampu/core/` no importa `PySide6` ni calcula en el hilo GUI. Todos los métodos públicos reciben datos explícitos, devuelven números/arrays/tablas y validan entradas mediante `core/validacion.py` y `core/errores.py`.
- Para una distribución nueva, define metadatos (`Parametro`, rangos, valor inicial), anótala en `core/distribuciones/registro.py` y respeta la interfaz uniforme de `core/distribuciones/base.py`: `pmf`/`pdf`, `cdf`, `ppf`, `media`, `varianza`, `desviacion`, `rvs(size,seed)`, `soporte`, `validar`. Incluye soporte, casos límite, cotejo SciPy y documentación de la convención.
- La UI construye sus formularios mediante el registro, recoge entradas y presenta salidas precomputadas por el motor. Si una gráfica necesita una media/proporción, haz que el núcleo la devuelva en vez de calcularla dentro de `ui/`.
- Agrega pruebas para valores límite, errores de dominio, determinismo, exportaciones y cambios de semántica. Usa `pytest.approx` con tolerancia justificada para resultados flotantes; no dependas de orden de hilos ni de un display X11 real.
- El formato de sesiones es versionado: si cambia la estructura, crea una migración/versión explícita; no ejecutes expresiones provenientes de JSON/Markdown. Los errores imprevistos se registran en el log rotativo y la UI presenta mensajes seguros en español.
- La teoría está en `src/ampu/docs/teoria/` con LaTeX entre `$…$` o `$$…$$`, ejemplo resuelto, fuentes identificables y figura. `scripts/generar_teoria.py` reproduce el conjunto actual; **revísalo antes de regenerar**, ya que sobreescribe lecciones. KaTeX y STIX se distribuyen localmente con sus licencias.

## Pantallas y paquetes

Con un escritorio completo, ejecuta `python -m ampu`, visita las siete pantallas y abre una lección para verificar fórmulas, enlaces e imágenes. `python scripts/capturar_ui.py` actualiza las cuatro capturas PNG *de widgets reales* tras terminar los cálculos; evita maquetas o cifras falsas. Para la captura genuina de teoría ejecuta `python -m ampu --self-test --capture-theory docs/capturas/05_teoria_oscuro.png`: solo se escribe después de verificar con JavaScript KaTeX, figura, CSS y paleta.

`python scripts/build_exe.py --onedir` prepara una carpeta y `python scripts/build_exe.py` el formato predeterminado. El script comprueba versión, recursos, `QtWebEngineProcess` y exportadores **dentro del artefacto**. Antes de publicar usa `python scripts/build_exe.py --gui-self-test` **en cada SO de destino** (Windows, macOS, Linux) y revisa visualmente la teoría. Un build Linux no genera un `.exe` Windows, y un `--verify-resources` satisfactorio **no** sustituye la autoprueba visual. `build/`, `dist/` y `.venv/` están ignorados.

Antes de enviar un cambio: ejecuta `python -m compileall -q src/ampu scripts`, todas las pruebas, la validación SciPy y revisa que `git diff` no incluya cambios fuera de `AmPu 3.0/`.
