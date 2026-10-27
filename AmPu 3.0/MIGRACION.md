# Migración desde AmPu 2.0

AmPu 3.0 es una **implementación nueva en Python**. Ningún archivo de la versión Java se cambió; `../src/`, `../test/` y `../src/teoriahtml/` se usaron solo como referencias. Las sesiones JSON nuevas no importan automáticamente archivos/objetos Swing o proyectos NetBeans.

## De la interfaz antigua a los módulos nuevos

| AmPu 2.0 | AmPu 3.0 |
|---|---|
| Métodos de `Funciones.java` y tablas de Swing | `ampu.core.distribuciones.obtener(clave)` y panel **Distribuciones**; 26 modelos y parámetros validados por metadatos. |
| Muestreo simple, infinito y estratificado | Panel **Muestreo**: sin/con reemplazo, sistemático, proporcional, Neyman, óptimo y conglomerados de una o dos etapas; semilla explícita. |
| JFreeChart y exportación Excel | Matplotlib QtAgg, tablas editables y servicio común XLSX/CSV/PNG/PDF. |
| Páginas HTML integradas | 57 lecciones Markdown+LaTeX, KaTeX y fuentes locales, 31 figuras, búsqueda, índice, claro/oscuro. |
| Accesos directos a programas de Windows | Calculadora científica integrada, sin rutas de Windows. |

Además se incorporan descriptiva, Bayes, combinatoria, pruebas de hipótesis, intervalos, regresión, Monte Carlo, ajuste y QQ-plots. El formato de sesión es **JSON versionado**: se guarda con `Guardar sesión`, se recupera con `Abrir`, y se rechazan versiones incompatibles.

## Casos de `test/Clases/FuncionesTest.java`: resultados y correcciones

Los tests históricos emplean `Math.rint(x*10000)/10000`: **redondear a cuatro cifras solo para comparar**, nunca durante los cálculos. `tests/test_paridad_java.py` reproduce los ejemplos compatibles; `scripts/validar_contra_scipy.py` contrasta 121 operaciones con tolerancia relativa `1e-10` y absoluta `1e-12`. El último ensayo con Python 3.12.11 y SciPy 1.18.1 pasó **121/121**.

| Caso Java y expectativa aproximada | Resultado correcto / convención nueva | Causa o interpretación |
|---|---|---|
| `binomialVp(5,10,.5)=.2461`; `VpMenor` y `VpMayor` = `.623` | `.246094`, `P(X≤5)=.623047`, `P(X≥5)=.623047` | Coinciden por simetría. La cola superior discreta incluye el punto: `sf(x−1)`. |
| `binomialNVp(3,2,.5)=.125`; media 2, varianza 4 | `.125`, 2, 4 | `x` son **fracasos antes de** `r` éxitos, no número total de ensayos. |
| `geometricaVp(5,.5)=.0312`; media 2, varianza 2 | `.03125`, 2, 2 | `x` cuenta ensayos **desde 1**. |
| Hipergeométrica `(x=2,N=6,n=3,K=2)` masa `.2`, CDF `1`, cola `.2`, media 1, varianza `.4` | Iguales | `K` es el número de éxitos poblacionales, `n` los extraídos. |
| Poisson `P(X=5;λ=1)=.0031`, CDF `.9994`, cola inclusiva `.0037` | `.003066`, `.999406`, `.003660` | Coinciden al redondear. |
| `multinomialVp(5,120,.03125)=.0312` | Requiere **vectores** `x=(x₁,…,xₖ)`, `p=(p₁,…,pₖ)` y `Σxᵢ=n`. Ej.: `n=5, x=(2,1,2), p=(.5,.25,.25)` → `.1171875`. | Java implementa `(N!/x)*p` con un único escalar `x` y `p`; no describe una multinomial. No hay traducción 1:1 de ese caso. |
| `UniformeDes(1,5)=1.7321` | `√((5−1)²/12)=1.1547005` | Java usa erróneamente `(a+b)²/12` en vez de `(b−a)²/12`. Densidad `1/4` y media 3 sí coinciden. |
| `NormalVp(2)=.9772`, `NormalBiseccion(.5)=0` | `.9772499`, 0 | Coinciden; se reemplaza la integración/bisección artesanal por SciPy. |
| `1−ExponencialVp(4,1)=.0183` | `sf(4; tasa=1)=.0183156` | Java está probando la **supervivencia** de la CDF, no la densidad. `scale` de SciPy es `1/tasa`. |
| `1−ExponencialVx(.5,1)=.3069` | `ppf(.5)=ln(2)=.693147`, de donde `1−ppf(.5)=.306853` | El valor Java es una resta del cuantil a uno, **no una probabilidad**; en 3.0 se muestra el cuantil sin esa resta. |
| `JiVp(1,1)=.3173` | `χ².sf(1;1)=.3173105` | Java integra la **cola superior** de la chi-cuadrado. |
| `JiBiseccion(.5,1)=.4553` | `χ².ppf(.5;1)=.4549364` | Error de cuadratura/inversión discretizada en Java. |
| `TstudentVp(1,1)=.9836`; `TstudentBiseccion(.5,1)=.4812` | `t.cdf(1;1)=.75`, `t.ppf(.5;1)=0` | Java trunca nodos a enteros y suma constantes en la integración; la mediana de una t simétrica es exactamente 0. |
| `FdeFisherVp(1,1,5)=.4971`; `FdeFisherVp1(1,5,5)=.5755` | Supervivencia: `F.sf(1;1,5)=.3632175`; `F.sf(1;5,5)=.5` | Cuadraturas Java truncan nodos e incorporan constantes/rangos arbitrarios; se conserva la semántica de **cola**, no los números defectuosos. |
| `FdeFisherVpp(1)=.5`, `FdeFisherVx(.5)=1` | Para `F(1,1)`, `sf(1)=.5` y `ppf(.5)=1` | Coinciden para este caso especial, pero la API nueva exige siempre ambos grados de libertad. |
| `FdeFisherBiseccion(.5,1,5)=.9407` | `F.ppf(.5;1,5)=.5280738` | La inversión Java hereda el error de la cola; no se replica. |
| `MASFinito(N=10, α=.5, p=.3, d=.1)` espera **10**; `MASInfinito(α=.5,p=.3,d=.2)` espera **2** | Confianza `1−α=.5`: `n_finito=ceil(5.15…)=6`; `n_infinito=ceil(2.388…)=3` | El tamaño es un **mínimo**, se redondea hacia arriba. El test finito también es incoherente con la fórmula original, cuyo valor sin redondear ronda 5.15 y `Math.round` daría 5, no 10. |
| `MEstratificado(n=2,N=5,Nh=5)=2` | 2 | Coincide para un solo estrato; con varios se aplica **mayores restos** para preservar el total y las capacidades. |

Las pequeñas diferencias de última cifra que quedan provienen de redondeos o algoritmos numéricos, no de un cambio de definición. Las expectativas matemáticamente incorrectas **no** se incorporan a la API nueva.

## Ejemplo para código nuevo

```python
from ampu.core.distribuciones import obtener
from ampu.core.muestreo.diseno import ejecutar_diseno

modelo = obtener("binomial")
parametros = modelo.validar(n=10, p=0.5)
print(modelo.pmf(5, **parametros))                 # 0.24609375
print(modelo.cola_inclusiva(5, **parametros))      # P(X ≥ 5)

seleccion = ejecutar_diseno("finito", N=400, n=40, seed=42)
print(seleccion.tablas["Selección"].head())
```

El motor **no requiere Qt** para usar estas funciones; la UI descubre los modelos automáticamente desde `registro.py`. Más decisiones de alcance y restricciones se describen en [PLAN.md](PLAN.md).
