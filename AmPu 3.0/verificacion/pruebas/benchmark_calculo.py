"""Rendimiento del motor de cálculo de AmPu 3.0 (sin interfaz gráfica).

Mide cada operación con ``perf_counter_ns`` (calentamiento + repeticiones) y
reporta mínimo, mediana, p95 y operaciones/segundo. Cuando existe una llamada
SciPy equivalente se mide también para obtener el factor de sobrecoste.

Uso:
    python verificacion/pruebas/benchmark_calculo.py --salida datos/rendimiento.json
    python ... --escala rapida --repeticiones 3
    python ... --escala completa --repeticiones 10

Los tamaños no pretenden ser un récord: pretenden ser comparables entre dos
equipos y entre dos versiones del mismo equipo (misma escala y repeticiones).
"""

from __future__ import annotations

import argparse
import math
import tempfile
from pathlib import Path

import _comun  # noqa: E402

RAIZ = _comun.preparar_import()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from scipy import stats  # noqa: E402

from ampu.core.distribuciones import obtener  # noqa: E402
from ampu.core.estadistica import (  # noqa: E402
    combinatoria as comb, descriptiva as desc, inferencia as inf,
    probabilidad as prob, regresion as reg,
)
from ampu.core.muestreo import aleatorio as m_ale, diseno as m_dis  # noqa: E402
from ampu.core.simulacion import montecarlo as mc  # noqa: E402
from ampu.io import ServicioExportacion as io  # noqa: E402

ESCALAS = {"rapida": 0.1, "normal": 1.0, "completa": 3.0}


def medir(r: _comun.Revisor, nombre: str, categoria: str, funcion, repeticiones: int,
          referencia=None, notas: str = "") -> float:
    """Cronometra una operación y, opcionalmente, su equivalente SciPy."""
    mediana = r.medir(nombre, categoria, funcion, repeticiones=repeticiones, calentamiento=1, notas=notas)
    if referencia is not None:
        mediana_ref = r.medir(f"referencia SciPy · {nombre}", categoria, referencia,
                              repeticiones=repeticiones, calentamiento=1,
                              notas="misma magnitud, sin capa de adaptación AmPu")
        r.metricas[-2]["referencia_ms"] = mediana_ref
        r.metricas[-2]["factor_sobre_referencia"] = round(mediana / mediana_ref, 2) if mediana_ref else None
    return mediana


def main() -> int:
    parser = argparse.ArgumentParser(description="Rendimiento del núcleo de AmPu 3.0")
    parser.add_argument("--salida", type=Path, default=Path("datos/rendimiento.json"))
    parser.add_argument("--escala", choices=list(ESCALAS), default="normal")
    parser.add_argument("--repeticiones", type=int, default=5)
    parser.add_argument("--sin-exportadores", action="store_true")
    args = parser.parse_args()

    factor = ESCALAS[args.escala]
    reps = max(1, args.repeticiones)
    r = _comun.Revisor(f"rendimiento-{args.escala}")
    rng = np.random.default_rng(2026)
    n_vector = max(2_000, int(20_000 * factor))
    n_grande = max(5_000, int(100_000 * factor))
    n_millon = max(50_000, int(1_000_000 * factor))
    n_muestra = max(1_000, int(50_000 * factor))

    print("== distribuciones ==")
    normal, binomial, t_student, gamma = (obtener("normal"), obtener("binomial"),
                                          obtener("t_student"), obtener("gamma"))
    pn, pb, pt, pg = normal.validar(), binomial.validar(), t_student.validar(), gamma.validar()
    x_escalar = 0.7
    xs = rng.normal(0, 1, n_vector)
    qs = rng.random(n_vector)
    enteros = rng.integers(0, 12, n_vector)

    medir(r, f"pdf escalar · normal (n={n_vector})", "distribuciones",
          lambda: normal.pdf(x_escalar, **pn), reps,
          referencia=lambda: stats.norm.pdf(x_escalar))
    medir(r, f"pdf vector ({n_vector:,}) · normal", "distribuciones",
          lambda: normal.pdf(xs, **pn), reps,
          referencia=lambda: stats.norm.pdf(xs), notas="adaptador AmPu vs SciPy directo")
    medir(r, "cdf vector · t de Student", "distribuciones",
          lambda: t_student.cdf(xs, **pt), reps,
          referencia=lambda: stats.t.cdf(xs, pt["gl"]))
    medir(r, "ppf vector · gamma", "distribuciones",
          lambda: gamma.ppf(qs, **pg), reps,
          referencia=lambda: stats.gamma.ppf(qs, pg["forma"], scale=pg["escala"]))
    medir(r, f"pmf vector ({n_vector:,}) · binomial", "distribuciones",
          lambda: binomial.pmf(enteros, **pb), reps,
          referencia=lambda: stats.binom(pb["n"], pb["p"]).pmf(enteros))
    medir(r, f"rvs ({n_millon:,}) · normal", "distribuciones",
          lambda: normal.rvs(n_millon, seed=7, **pn), reps,
          referencia=lambda: stats.norm.rvs(size=n_millon, random_state=7))
    medir(r, "recorrido del catálogo (26 modelos)", "distribuciones",
          lambda: [m.media(**m.validar()) for m in
                   __import__("ampu.core.distribuciones", fromlist=["catalogo"]).catalogo()
                   if m.dimensionalidad == "univariante"], reps)

    print("\n== muestreo ==")
    estratos = [(f"E{i}", 10_000, 1.0 + i / 10, 1.0) for i in range(1, 11)]
    medir(r, "diseño aleatorio simple (N=100 000, n=1 000)", "muestreo",
          lambda: m_dis.ejecutar_diseno("finito", N=100_000, n=1_000, seed=5), reps)
    medir(r, "diseño sistemático (N=100 000, n=1 000)", "muestreo",
          lambda: m_dis.ejecutar_diseno("sistematico", N=100_000, n=1_000, seed=5), reps)
    medir(r, "diseño estratificado Neyman (10 estratos)", "muestreo",
          lambda: m_dis.ejecutar_diseno("neyman", N=100_000, n=1_000, seed=5, estratos=estratos), reps)
    medir(r, "diseño por conglomerados (10 grupos)", "muestreo",
          lambda: m_dis.ejecutar_diseno("conglomerados", N=0, n=10, seed=5, estratos=estratos), reps)
    medir(r, "tamaño de muestra de proporción (×1000)", "muestreo",
          lambda: [m_ale.tamano_proporcion(0.5, 0.05, 0.95, N=50_000) for _ in range(1000)], reps)

    print("\n== descriptiva y probabilidad ==")
    datos = rng.normal(50, 12, n_grande)
    enteros_discretos = rng.integers(0, 1_000, n_grande)
    valores = np.arange(1_000)
    masas = np.full(1_000, 1 / 1_000)
    medir(r, f"resumen descriptivo (n={n_grande:,})", "descriptiva",
          lambda: desc.resumir(datos), reps,
          referencia=lambda: (float(np.mean(datos)), float(np.std(datos, ddof=1)), float(np.median(datos))),
          notas="referencia: media, desviación y mediana con NumPy")
    medir(r, f"tabla de frecuencias (n={n_grande:,}, 1 000 valores)", "descriptiva",
          lambda: desc.frecuencias(enteros_discretos), reps)
    medir(r, "percentil 95", "descriptiva", lambda: desc.percentil(datos, 0.95), reps)
    medir(r, "combinaciones C(500, 250) exactas", "probabilidad",
          lambda: comb.combinaciones(500, 250), reps,
          referencia=lambda: math.comb(500, 250))
    medir(r, "factorial 500 exacto", "probabilidad", lambda: comb.factorial(500), reps)
    medir(r, "esperanza y varianza sobre 1 000 masas", "probabilidad",
          lambda: (prob.esperanza(valores, masas), prob.varianza(valores, masas)), reps,
          referencia=lambda: (float(np.sum(valores * masas)),
                              float(np.sum((valores - np.sum(valores * masas)) ** 2 * masas))))
    medir(r, "Bayes con 1 000 hipótesis", "probabilidad",
          lambda: prob.bayes(10, list(masas), list(masas)), reps)

    print("\n== inferencia ==")
    a = rng.normal(10, 2, n_muestra)
    b = rng.normal(10.3, 2.1, n_muestra)
    grupos = [rng.normal(10 + i * .2, 2, n_muestra // 5) for i in range(5)]
    tabla_chi = rng.integers(5, 50, (20, 20))
    X = rng.normal(0, 1, (n_muestra, 5))
    Y = X @ np.array([1.0, -0.5, 0.25, 0.0, 2.0]) + rng.normal(0, 1, n_muestra)
    x_simple = X[:, 0]

    medir(r, f"t de Welch dos muestras (n={n_muestra:,} c/u)", "inferencia",
          lambda: inf.t_dos_muestras(a, b), reps,
          referencia=lambda: stats.ttest_ind(a, b, equal_var=False), notas="estadístico y p-valor")
    medir(r, f"z de dos medias (n={n_muestra:,} c/u)", "inferencia",
          lambda: inf.z_dos_muestras(a, b, 2, 2.1), reps)
    medir(r, "ANOVA de 5 grupos", "inferencia",
          lambda: inf.anova(grupos), reps, referencia=lambda: stats.f_oneway(*grupos))
    medir(r, "chi² de independencia 20×20", "inferencia",
          lambda: inf.chi_independencia(tabla_chi), reps,
          referencia=lambda: stats.chi2_contingency(tabla_chi, correction=False))
    medir(r, "chi² de bondad con 20 celdas", "inferencia",
          lambda: inf.chi_bondad(tabla_chi.sum(axis=0), tabla_chi.sum(axis=0) * 1.0), reps)
    medir(r, f"correlación de Pearson (n={n_muestra:,})", "inferencia",
          lambda: inf.correlacion(x_simple, Y), reps,
          referencia=lambda: stats.pearsonr(x_simple, Y), notas="incluye IC bootstrap-free de SciPy")
    medir(r, f"correlación de Spearman (n={n_muestra:,})", "inferencia",
          lambda: inf.correlacion(x_simple, Y, "spearman"), reps,
          referencia=lambda: stats.spearmanr(x_simple, Y))
    medir(r, f"Mann–Whitney (n={n_muestra:,} c/u)", "inferencia",
          lambda: inf.mann_whitney(a, b), reps,
          referencia=lambda: stats.mannwhitneyu(a, b), notas="dos colas")
    medir(r, "Kruskal–Wallis de 5 grupos", "inferencia",
          lambda: inf.kruskal(grupos), reps, referencia=lambda: stats.kruskal(*grupos))
    medir(r, f"regresión simple (n={n_muestra:,})", "inferencia",
          lambda: reg.lineal_simple(x_simple, Y), reps,
          referencia=lambda: stats.linregress(x_simple, Y))
    medir(r, f"regresión múltiple (n={n_muestra:,}, 5 predictores)", "inferencia",
          lambda: reg.lineal_multiple(X, Y), reps)
    medir(r, "intervalo de confianza de la media", "inferencia",
          lambda: inf.intervalo_media(a), reps)
    medir(r, "intervalo de Wilson para proporción", "inferencia",
          lambda: inf.intervalo_proporcion(437, 1000), reps)

    print("\n== simulación ==")
    medir(r, f"Monte Carlo de π (n={n_millon:,})", "simulacion",
          lambda: mc.simular_pi(n=n_millon, seed=3), reps)
    medir(r, f"integración Monte Carlo de x² (n={n_millon:,})", "simulacion",
          lambda: mc.integral_cuadrado(n=n_millon, seed=3), reps)
    medir(r, f"generar muestra normal (n={n_millon:,})", "simulacion",
          lambda: mc.generar_muestra("normal", {"mu": 0.0, "sigma": 1.0}, n_millon, seed=3), reps,
          referencia=lambda: stats.norm.rvs(size=n_millon, random_state=3))
    datos_ajuste = rng.normal(4, 1.5, max(200, int(2_000 * factor)))
    medir(r, f"ajuste por máxima verosimilitud (n={len(datos_ajuste):,})", "simulacion",
          lambda: mc.ajustar_distribucion(datos_ajuste, "normal", seed=7), reps,
          notas="differential_evolution: coste dominante del módulo")
    datos_qq = rng.normal(0, 1, max(500, int(10_000 * factor)))
    medir(r, f"QQ-plot (n={len(datos_qq):,})", "simulacion",
          lambda: mc.qq_plot(datos_qq, "normal", {"mu": 0.0, "sigma": 1.0}), reps)
    medir(r, "curva ajustada para gráfico", "simulacion",
          lambda: mc.curva_ajustada(mc.ajustar_distribucion(datos_ajuste, "normal", seed=7), datos_ajuste),
          max(1, reps // 2), notas="incluye el ajuste completo")

    if not args.sin_exportadores:
        print("\n== exportadores ==")
        filas = max(500, int(20_000 * factor))
        tabla = pd.DataFrame({
            "valor": rng.normal(0, 1, filas),
            "entero": rng.integers(0, 1000, filas),
            "texto": [f"fila-{i}" for i in range(filas)],
            "probabilidad": rng.random(filas),
            "acumulada": np.cumsum(rng.random(filas)) / filas,
        })
        figura = Figure(figsize=(7, 3.6))
        eje = figura.subplots()
        eje.plot(np.arange(200), rng.normal(0, 1, 200))
        eje.set_title("Serie de verificación")
        with tempfile.TemporaryDirectory(prefix="ampu-rendimiento-") as temporal:
            carpeta = Path(temporal)
            medir(r, f"exportar XLSX ({filas:,} filas × 5 columnas)", "exportacion",
                  lambda: io.excel({"Resultados": tabla}, carpeta / "r.xlsx"), max(1, reps // 2))
            medir(r, f"exportar CSV ({filas:,} filas)", "exportacion",
                  lambda: io.csv(tabla, carpeta / "r.csv"), reps)
            medir(r, "exportar PNG del gráfico", "exportacion",
                  lambda: io.png(figura, carpeta / "r.png"), reps)
            medir(r, "exportar PDF con tabla y figura", "exportacion",
                  lambda: io.pdf(carpeta / "r.pdf", "Verificación", "Resumen",
                                 {"Resultados": tabla.head(300)}, figura, r"\\frac{x}{2}"), max(1, reps // 2))
            estado = {"semilla": 42, "tabla": tabla, "anidado": {"a": list(range(50))}}
            medir(r, f"guardar sesión JSON ({filas:,} filas)", "exportacion",
                  lambda: io.guardar(estado, carpeta / "s.json"), reps)
            sesion = io.guardar(estado, carpeta / "s2.json")
            medir(r, "cargar sesión JSON", "exportacion",
                  lambda: io.cargar(sesion), reps)

    # Umbrales de cordura: no son objetivos de rendimiento absolutos, solo
    # detectan regresiones groseras y bloqueos accidentales.
    cat_ = "rendimiento"
    peores = sorted(r.metricas, key=lambda m: m["mediana_ms"], reverse=True)[:5]
    r.verdadero("rendimiento.sin_operacion_bloqueante", cat_,
                "Ninguna operación del núcleo supera 10 s de mediana",
                all(m["mediana_ms"] < 10_000 for m in r.metricas if "referencia SciPy" not in m["operacion"]),
                obtenido=[{m["operacion"]: m["mediana_ms"]} for m in peores])
    referencias = [m for m in r.metricas if m.get("factor_sobre_referencia")]
    if referencias:
        peor = max(referencias, key=lambda m: m["factor_sobre_referencia"])
        r.verdadero("rendimiento.sobrecoste_adaptador", cat_,
                    "El sobrecoste del adaptador AmPu frente a SciPy es < 20×",
                    peor["factor_sobre_referencia"] < 20,
                    obtenido={peor["operacion"]: peor["factor_sobre_referencia"]},
                    esperado="< 20", tolerancia="razón AmPu/SciPy")
    memoria = _comun.memoria_mb()
    r.verdadero("rendimiento.memoria", cat_, "Memoria del proceso por debajo de 4 GB",
                memoria.get("pico_mb") is None or memoria["pico_mb"] < 4096,
                obtenido=memoria, esperado="< 4096 MB")

    documento = r.documento("benchmark_calculo",
                            {"escala": args.escala, "repeticiones": reps, "factor": factor})
    _comun.guardar_json(args.salida, documento)
    print(f"Rendimiento guardado en {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
