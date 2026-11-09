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

La UI usa Dear PyGui y Matplotlib `Agg`. Las pruebas de integración crean un contexto Dear PyGui real sin viewport, por lo que no necesitan pantalla ni reemplazan los widgets por mocks. `python -m ampu --self-test` recorre los módulos y falla en lugar de omitir errores. La validación de foco, DPI y apariencia requiere un escritorio nativo. La cobertura de `core/` debe mantenerse **≥85 % con ramas**; la simulación aleatoria siempre se prueba con semilla.

## Organización y estilo

- `src/ampu/core/` no importa `dearpygui` ni calcula en el hilo GUI. Todos los métodos públicos reciben datos explícitos, devuelven números/arrays/tablas y validan entradas mediante `core/validacion.py` y `core/errores.py`.
- Para una distribución nueva, define metadatos (`Parametro`, rangos, valor inicial), anótala en `core/distribuciones/registro.py` y respeta la interfaz uniforme de `core/distribuciones/base.py`: `pmf`/`pdf`, `cdf`, `ppf`, `media`, `varianza`, `desviacion`, `rvs(size,seed)`, `soporte`, `validar`. Incluye soporte, casos límite, cotejo SciPy y documentación de la convención.
- La UI construye sus formularios mediante el registro, recoge entradas y presenta salidas precomputadas por el motor. Si una gráfica necesita una media/proporción, haz que el núcleo la devuelva en vez de calcularla dentro de `ui/`.
- Agrega pruebas para valores límite, errores de dominio, determinismo, exportaciones y cambios de semántica. Usa `pytest.approx` con tolerancia justificada para resultados flotantes; no dependas de orden de hilos ni de un display X11 real.
- El formato de sesiones es versionado: si cambia la estructura, crea una migración/versión explícita; no ejecutes expresiones provenientes de JSON/Markdown. Los errores imprevistos se registran en el log rotativo y la UI presenta mensajes seguros en español.
- La teoría está en `src/ampu/docs/teoria/` con LaTeX entre `$…$` o `$$…$$`, ejemplo resuelto, fuentes identificables y figura. `scripts/generar_teoria.py` reproduce el conjunto actual; **revísalo antes de regenerar**, ya que sobreescribe lecciones. Dear PyGui muestra el contenido y el LaTeX original; HTML/KaTeX/STIX se conservan solo para las APIs documentales existentes.

## Pantallas y paquetes

Con un escritorio completo, ejecuta `python -m ampu`, visita las siete pantallas y abre una lección para verificar texto, código LaTeX e imágenes. `python scripts/capturar_ui.py` actualiza las cuatro capturas PNG *del viewport real* tras terminar los cálculos; evita maquetas o cifras falsas. No confundas la captura de una textura individual con una captura de la ventana completa.

`python scripts/build_exe.py --onedir` prepara una carpeta y `python scripts/build_exe.py` el formato predeterminado. El script comprueba versión, recursos, Dear PyGui y exportadores **dentro del artefacto**. Antes de publicar usa `python scripts/build_exe.py --gui-self-test` **en cada SO de destino** (Windows, macOS, Linux) y revisa visualmente la interfaz y la teoría. Un build Linux no genera un `.exe` Windows, y un `--verify-resources` satisfactorio **no** sustituye la autoprueba visual. `build/`, `dist/` y `.venv/` están ignorados.

Antes de enviar un cambio: ejecuta `python -m compileall -q src/ampu scripts`, todas las pruebas, la validación SciPy y revisa que `git diff` no incluya cambios fuera de `AmPu 3.0/`.
