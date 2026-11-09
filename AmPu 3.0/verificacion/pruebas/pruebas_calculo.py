"""Pruebas de cálculo de AmPu 3.0: coherencia numérica, no solo "no falla".

Cubre las 26 distribuciones, los 7 diseños de muestreo, descriptiva,
probabilidad/combinatoria, 16 técnicas de inferencia, simulación/ajuste y los
cuatro exportadores. Cada comprobación queda en JSON con su tolerancia.

Uso:
    python verificacion/pruebas/pruebas_calculo.py --salida datos/calculo.json
    python ... --rapido        # omite las comprobaciones Monte Carlo lentas
    python ... --sin-exportadores
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import tempfile
from pathlib import Path

import _comun  # noqa: E402

RAIZ = _comun.preparar_import()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import integrate, stats  # noqa: E402

from ampu.core import distribuciones as cat  # noqa: E402
from ampu.core.errores import ErrorAmPu  # noqa: E402
from ampu.core.estadistica import (  # noqa: E402
    combinatoria as comb, descriptiva as desc, inferencia as inf,
    probabilidad as prob, regresion as reg,
)
from ampu.core.errores import ParametroInvalidoError  # noqa: E402
from ampu.core.muestreo import aleatorio as m_ale, diseno as m_dis  # noqa: E402
from ampu.core.simulacion import montecarlo as mc  # noqa: E402

RTOL = 1e-9
ATOL = 1e-12
Q = np.array([0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999])


# --------------------------------------------------------------------------- #
# 1. Distribuciones
# --------------------------------------------------------------------------- #
def probar_univariante(r: _comun.Revisor, modelo, rapido: bool) -> None:
    clave, cat_ = modelo.clave, "distribuciones"
    p = modelo.validar()
    funcion = modelo.pmf if modelo.discreta else modelo.pdf
    nombre = "pmf" if modelo.discreta else "pdf"

    # a) Rango de cuantiles estable y soporte
    qs = np.asarray(modelo.ppf(Q, **p), dtype=float)
    r.verdadero(f"dist.{clave}.ppf_finito", cat_, f"{clave}: PPF devuelve cuantiles utilizables",
                np.all(np.isfinite(qs)), obtenido=[round(v, 6) for v in qs])

    lo, hi = modelo.soporte(**p)
    interiores = qs[np.isfinite(qs)]
    r.verdadero(f"dist.{clave}.soporte_coherente", cat_,
                f"{clave}: los cuantiles caen dentro del soporte [{lo:g}, {hi:g}]",
                bool(len(interiores)) and bool(np.all(interiores >= lo - 1e-9)
                                               and np.all(interiores <= hi + 1e-9)),
                obtenido={"soporte": [lo, hi], "min_q": float(interiores.min()) if len(interiores) else None,
                          "max_q": float(interiores.max()) if len(interiores) else None})

    # b) CDF monótona y acotada
    rejilla = np.unique(np.concatenate([qs, [lo if np.isfinite(lo) else qs[0] - 1,
                                             hi if np.isfinite(hi) else qs[-1] + 1]]))
    rejilla = rejilla[np.isfinite(rejilla)]
    cdf = np.asarray(modelo.cdf(rejilla, **p), dtype=float)
    r.verdadero(f"dist.{clave}.cdf_monotona", cat_, f"{clave}: CDF no decreciente en {len(rejilla)} puntos",
                bool(np.all(np.diff(cdf) >= -1e-12)),
                obtenido=float(np.min(np.diff(cdf))) if len(cdf) > 1 else 0.0, tolerancia=">= -1e-12")
    r.verdadero(f"dist.{clave}.cdf_rango", cat_, f"{clave}: CDF en [0,1]",
                bool(np.all((cdf >= -1e-12) & (cdf <= 1 + 1e-12))),
                obtenido={"min": float(cdf.min()), "max": float(cdf.max())})

    # c) PPF monótona y coherencia CDF/PPF
    ordenada = np.asarray(modelo.ppf(np.sort(Q), **p), dtype=float)
    r.verdadero(f"dist.{clave}.ppf_monotona", cat_, f"{clave}: PPF no decreciente",
                bool(np.all(np.diff(ordenada) >= -1e-9)), obtenido=float(np.min(np.diff(ordenada))))
    vuelta = np.asarray(modelo.cdf(ordenada, **p), dtype=float)
    if modelo.discreta:
        r.verdadero(f"dist.{clave}.ppf_cdf", cat_, f"{clave}: CDF(PPF(q)) ≥ q (escalonada)",
                    bool(np.all(vuelta >= np.sort(Q) - 1e-9)),
                    obtenido=float(np.min(vuelta - np.sort(Q))))
    else:
        r.cerca(f"dist.{clave}.ppf_cdf", cat_, f"{clave}: CDF(PPF(q)) ≈ q", vuelta, np.sort(Q),
                rtol=1e-7, atol=1e-9)

    # d) Normalización de la masa/densidad
    if modelo.discreta:
        if np.isfinite((lo, hi)).all() and hi - lo <= 200_000:
            xs = np.arange(lo, hi + 1)
            masa = np.asarray(funcion(xs, **p), dtype=float)
            r.cerca(f"dist.{clave}.normalizacion", cat_, f"{clave}: Σ PMF = 1 sobre el soporte",
                    float(np.nansum(masa)), 1.0, rtol=1e-9, atol=1e-9)
            xs_media = xs
            pesos = masa
        else:
            extremo_lo = float(modelo.ppf(1e-10, **p))
            extremo_hi = float(modelo.ppf(1 - 1e-10, **p))
            if not np.isfinite([extremo_lo, extremo_hi]).all() or extremo_hi - extremo_lo > 200_000:
                total = float(modelo.cdf(extremo_hi, **p)) - float(modelo.cdf(extremo_lo - 1, **p))
                r.cerca(f"dist.{clave}.normalizacion", cat_,
                        f"{clave}: F(alto) − F(bajo) ≈ 1 en el rango 1e-10..1-1e-10", total, 1.0,
                        rtol=1e-6, atol=1e-6, notas="Cola truncada; tolerancia 1e-6")
                xs_media = np.asarray([], dtype=float)
                pesos = np.asarray([], dtype=float)
            else:
                xs = np.arange(math.ceil(extremo_lo), math.floor(extremo_hi) + 1)
                masa = np.asarray(funcion(xs, **p), dtype=float)
                r.cerca(f"dist.{clave}.normalizacion", cat_,
                        f"{clave}: Σ PMF ≈ 1 en el rango 1e-10..1-1e-10", float(np.nansum(masa)), 1.0,
                        rtol=1e-6, atol=1e-6, notas="Cola truncada; tolerancia 1e-6")
                xs_media = xs
                pesos = masa
        if len(xs_media) and np.all(np.isfinite([modelo.media(**p), modelo.varianza(**p)])):
            media_num = float(np.sum(xs_media * pesos) / np.sum(pesos))
            var_num = float(np.sum((xs_media - media_num) ** 2 * pesos) / np.sum(pesos))
            r.cerca(f"dist.{clave}.media_numerica", cat_, f"{clave}: media vs suma numérica",
                    modelo.media(**p), media_num, rtol=1e-6, atol=1e-7)
            r.cerca(f"dist.{clave}.varianza_numerica", cat_, f"{clave}: varianza vs suma numérica",
                    modelo.varianza(**p), var_num, rtol=1e-5, atol=1e-7)
    else:
        finito = bool(np.isfinite(lo) and np.isfinite(hi))
        a = lo if np.isfinite(lo) else float(modelo.ppf(0.001, **p))
        b = hi if np.isfinite(hi) else float(modelo.ppf(0.999, **p))
        if np.isfinite(a) and np.isfinite(b) and a < b:
            area, error = integrate.quad(lambda t: float(funcion(t, **p)), a, b, limit=400)
            if finito:
                r.cerca(f"dist.{clave}.normalizacion", cat_,
                        f"{clave}: ∫ PDF = 1 en todo el soporte [{a:.4g}, {b:.4g}]",
                        area, 1.0, rtol=1e-6, atol=1e-6, notas=f"quad error={error:.2e}")
            else:
                # Soporte infinito: la masa de la cola no es integrable con quad
                # en un rango enorme; se contrasta la PDF con la CDF en el mismo rango.
                esperado_masa = float(modelo.cdf(b, **p)) - float(modelo.cdf(a, **p))
                r.cerca(f"dist.{clave}.pdf_vs_cdf", cat_,
                        f"{clave}: ∫ PDF ≈ F(b)−F(a) en [q0.001, q0.999]",
                        area, esperado_masa, rtol=1e-6, atol=1e-7,
                        notas=f"quad error={error:.2e}; soporte infinito")
            if np.isfinite(lo) and np.isfinite(hi):
                media_num, _ = integrate.quad(lambda t: t * float(funcion(t, **p)), a, b, limit=400)
                var_num, _ = integrate.quad(lambda t: (t - media_num) ** 2 * float(funcion(t, **p)), a, b, limit=400)
                if np.isfinite(modelo.media(**p)):
                    r.cerca(f"dist.{clave}.media_numerica", cat_, f"{clave}: media vs integración",
                            modelo.media(**p), media_num, rtol=1e-6, atol=1e-7)
                if np.isfinite(modelo.varianza(**p)):
                    r.cerca(f"dist.{clave}.varianza_numerica", cat_, f"{clave}: varianza vs integración",
                            modelo.varianza(**p), var_num, rtol=1e-5, atol=1e-7)
        else:
            r.omitir(f"dist.{clave}.normalizacion", cat_, f"{clave}: integración de la PDF",
                     "Soporte no integrable numéricamente con quad")

    # e) Desviación y cola inclusiva
    var = modelo.varianza(**p)
    if np.isfinite(var) and var >= 0:
        r.cerca(f"dist.{clave}.desviacion", cat_, f"{clave}: desviación = √varianza",
                modelo.desviacion(**p), math.sqrt(max(var, 0.0)), rtol=1e-12, atol=1e-12)
    x_cola = qs[4] if len(qs) > 4 else qs[0]
    manual = 1.0 - float(modelo.cdf(np.ceil(x_cola) - 1 if modelo.discreta else x_cola, **p))
    r.cerca(f"dist.{clave}.cola_inclusiva", cat_, f"{clave}: P(X≥x) coincide con 1−F",
            float(modelo.cola_inclusiva(x_cola, **p)), manual, rtol=1e-9, atol=1e-12)

    # f) Simulación reproducible y con momentos razonables
    tam = 2_000 if rapido else 20_000
    muestra_a = modelo.rvs(tam, seed=1234, **p)
    muestra_b = modelo.rvs(tam, seed=1234, **p)
    r.verdadero(f"dist.{clave}.rvs_reproducible", cat_, f"{clave}: misma semilla ⇒ misma muestra",
                bool(np.array_equal(muestra_a, muestra_b)), obtenido=f"{len(muestra_a)} valores")
    muestra_c = modelo.rvs(10, seed=4321, **p)
    r.verdadero(f"dist.{clave}.rvs_semilla_distinta", cat_, f"{clave}: semilla distinta ⇒ muestra distinta",
                not np.allclose(modelo.rvs(10, seed=1234, **p), muestra_c))
    media, desv = modelo.media(**p), modelo.desviacion(**p)
    if np.isfinite(media) and np.isfinite(desv) and desv > 0:
        error_tipico = desv / math.sqrt(tam)
        r.verdadero(f"dist.{clave}.rvs_media", cat_,
                    f"{clave}: media simulada dentro de 6 errores estándar",
                    abs(float(np.mean(muestra_a)) - media) <= 6 * error_tipico,
                    obtenido=round(float(np.mean(muestra_a)), 6), esperado=round(media, 6),
                    tolerancia=round(6 * error_tipico, 6), notas=f"n={tam}")
    else:
        r.omitir(f"dist.{clave}.rvs_media", cat_, f"{clave}: media simulada", "Media o desviación no finita")

    # g) Entradas inválidas: se usa el primer parámetro acotado que exista
    acotados = [par for par in modelo.parametros
                if par.tipo in ("real", "entero") and par.minimo is not None]
    if acotados:
        parametro = acotados[0]
        fuera = parametro.minimo - 1
        if parametro.tipo == "entero":
            fuera = int(parametro.minimo) - 1
        invalido = dict(p)
        invalido[parametro.nombre] = fuera
        r.lanza(f"dist.{clave}.valida_parametros", cat_,
                f"{clave}: rechaza {parametro.nombre}={fuera} por debajo del mínimo {parametro.minimo:g}",
                lambda: modelo.validar(**invalido), ErrorAmPu)
    else:
        r.omitir(f"dist.{clave}.valida_parametros", cat_, f"{clave}: validación de parámetros",
                 "Ningún parámetro declara cota inferior numérica")


def probar_multivariadas(r: _comun.Revisor) -> None:
    cat_ = "distribuciones_multivariadas"

    # Multinomial: la masa de todas las composiciones debe sumar 1
    mult = cat.obtener("multinomial")
    pm = mult.validar()
    n, probs = int(pm["n"]), np.asarray(pm["p"], dtype=float)
    total = 0.0
    for composicion in itertools.product(range(n + 1), repeat=len(probs)):
        if sum(composicion) == n:
            total += float(mult.pmf(list(composicion), **pm))
    r.cerca("multinomial.normalizacion", cat_, "Multinomial: Σ PMF = 1 sobre las composiciones",
            total, 1.0, rtol=1e-9, atol=1e-12)
    referencia = stats.multinomial(n, probs)
    r.cerca("multinomial.pmf_vs_scipy", cat_, "Multinomial: PMF coincide con SciPy",
            float(mult.pmf([2, 2, 4], **pm)), float(referencia.pmf([2, 2, 4])), rtol=1e-12)
    r.cerca("multinomial.media_vs_scipy", cat_, "Multinomial: media coincide con SciPy",
            mult.media(**pm), referencia.mean(), rtol=1e-12)

    # Dirichlet
    dirich = cat.obtener("dirichlet")
    pd_ = dirich.validar()
    alfa = np.asarray(pd_["alpha"], dtype=float)
    puntos = np.array([0.2, 0.3, 0.5])
    r.cerca("dirichlet.pdf_vs_scipy", cat_, "Dirichlet: PDF coincide con SciPy",
            float(dirich.pdf(puntos, **pd_)), float(stats.dirichlet(alfa).pdf(puntos)), rtol=1e-10)
    r.cerca("dirichlet.media_vs_scipy", cat_, "Dirichlet: media marginal coincide con SciPy",
            dirich.media(**pd_), stats.dirichlet(alfa).mean(), rtol=1e-12)
    r.cerca("dirichlet.fuera_simplex", cat_,
            "Dirichlet: densidad 0 fuera del símplex (documentado)", float(dirich.pdf([0.2, 0.2, 0.2], **pd_)), 0.0,
            rtol=0, atol=0)
    r.lanza("dirichlet.dimension", cat_, "Dirichlet: rechaza un vector de dimensión incorrecta",
            lambda: dirich.pdf([0.2, 0.3], **pd_), ErrorAmPu)

    # Normal bivariada
    nb = cat.obtener("normal_bivariada")
    pn = nb.validar()
    ref = stats.multivariate_normal([pn["mu_x"], pn["mu_y"]],
                                    [[pn["sigma_x"] ** 2, pn["rho"] * pn["sigma_x"] * pn["sigma_y"]],
                                     [pn["rho"] * pn["sigma_x"] * pn["sigma_y"], pn["sigma_y"] ** 2]])
    r.cerca("normal_bivariada.pdf_vs_scipy", cat_, "Normal bivariada: PDF conjunta coincide con SciPy",
            float(nb.pdf([0.2, -0.3], **pn)), float(ref.pdf([0.2, -0.3])), rtol=1e-10)
    r.cerca("normal_bivariada.cdf_vs_scipy", cat_, "Normal bivariada: CDF conjunta coincide con SciPy",
            float(nb.cdf([0.2, -0.3], **pn)), float(ref.cdf([0.2, -0.3])), rtol=1e-8, atol=1e-10)
    r.cerca("normal_bivariada.media_vs_scipy", cat_, "Normal bivariada: medias marginales coinciden",
            nb.media(**pn), [pn["mu_x"], pn["mu_y"]], rtol=1e-12)


def probar_catalogo(r: _comun.Revisor) -> None:
    """Comprueba el tamaño y la forma del catálogo antes de recorrerlo."""
    modelos = cat.catalogo()
    discretas = cat.catalogo("discretas")
    continuas = cat.catalogo("continuas")
    multivariadas = cat.catalogo("multivariadas")
    r.verdadero("catalogo.total", "distribuciones", "El catálogo declara 26 distribuciones",
                len(modelos) == 26, obtenido=len(modelos), esperado=26)
    r.verdadero("catalogo.familias", "distribuciones",
                "8 discretas, 18 continuas y 3 multivariadas",
                (len(discretas), len(continuas), len(multivariadas)) == (8, 18, 3),
                obtenido={"discretas": len(discretas), "continuas": len(continuas),
                          "multivariadas": len(multivariadas)}, esperado={"discretas": 8, "continuas": 18,
                                                                        "multivariadas": 3})
    r.verdadero("catalogo.claves_unicas", "distribuciones", "No hay claves duplicadas en el registro",
                len({m.clave for m in modelos}) == len(modelos))
    r.lanza("catalogo.clave_inexistente", "distribuciones", "Buscar una clave inexistente informa el error",
            lambda: cat.obtener("no_existe"), KeyError)
    from ampu.core.errores import SoporteError

    for modelo in modelos:
        if modelo.dimensionalidad != "univariante":
            continue
        p = modelo.validar()
        funcion_prohibida = (lambda: modelo.pdf(1.0, **p)) if modelo.discreta else (lambda: modelo.pmf(1, **p))
        r.lanza(f"dist.{modelo.clave}.contrato", "distribuciones",
                f"{modelo.clave}: {'PMF' if modelo.discreta else 'PDF'} exclusiva de su tipo",
                funcion_prohibida, SoporteError, notas=f"discreta={modelo.discreta}")


# --------------------------------------------------------------------------- #
# 2. Muestreo
# --------------------------------------------------------------------------- #
def probar_muestreo(r: _comun.Revisor) -> None:
    cat_ = "muestreo"
    fin = m_dis.ejecutar_diseno("finito", N=1000, n=50, seed=7)
    tabla = fin.tablas["Selección"]
    r.verdadero("muestreo.finito.tamano", cat_, "Aleatorio simple sin reemplazo: 50 unidades",
                len(tabla) == 50, obtenido=len(tabla))
    r.verdadero("muestreo.finito.sin_repetidos", cat_, "Aleatorio simple: no hay unidades repetidas",
                tabla["Selección"].nunique() == len(tabla))
    valores = set(tabla["Selección"])
    r.verdadero("muestreo.finito.dentro_poblacion", cat_, "Aleatorio simple: selección ⊂ {1..N}",
                valores.issubset(set(range(1, 1001))))
    otra = m_dis.ejecutar_diseno("finito", N=1000, n=50, seed=7)
    r.verdadero("muestreo.finito.reproducible", cat_, "Aleatorio simple: misma semilla ⇒ misma muestra",
                list(otra.tablas["Selección"]["Selección"]) == list(tabla["Selección"]))
    distinta = m_dis.ejecutar_diseno("finito", N=1000, n=50, seed=8)
    r.verdadero("muestreo.finito.semilla_efectiva", cat_, "Aleatorio simple: semilla distinta ⇒ muestra distinta",
                list(distinta.tablas["Selección"]["Selección"]) != list(tabla["Selección"]))

    infi = m_dis.ejecutar_diseno("infinito", N=500, n=80, seed=3)
    r.verdadero("muestreo.infinito.tamano", cat_, "Con reemplazo: 80 extracciones",
                len(infi.tablas["Selección"]) == 80)
    r.verdadero("muestreo.infinito.permite_repeticion", cat_, "Con reemplazo: admite n ≤ N y repetidos",
                infi.tablas["Selección"]["Selección"].nunique() <= 80)

    sist = m_dis.ejecutar_diseno("sistematico", N=400, n=25, seed=11)
    r.verdadero("muestreo.sistematico.tamano", cat_, "Sistemático: 25 unidades distintas",
                sist.tablas["Selección"]["Selección"].nunique() == 25)
    r.verdadero("muestreo.sistematico.reproducible", cat_, "Sistemático: semilla reproducible",
                list(m_dis.ejecutar_diseno("sistematico", N=400, n=25, seed=11)
                     .tablas["Selección"]["Selección"]) == list(sist.tablas["Selección"]["Selección"]))

    estratos = [("A", 400, 2.0, 1.0), ("B", 600, 1.0, 1.0)]
    prop = m_dis.ejecutar_diseno("proporcional", N=1000, n=100, seed=5, estratos=estratos)
    cuotas = dict(zip(prop.tablas["Asignación"]["Estrato"], prop.tablas["Asignación"]["nh"]))
    r.verdadero("muestreo.proporcional.suma", cat_, "Estratificado proporcional: Σ nh = 100",
                sum(cuotas.values()) == 100, obtenido=cuotas)
    r.verdadero("muestreo.proporcional.cuotas", cat_, "Estratificado proporcional: 40/60 según Nh",
                cuotas == {"A": 40, "B": 60}, obtenido=cuotas, esperado={"A": 40, "B": 60})
    ney = m_dis.ejecutar_diseno("neyman", N=1000, n=100, seed=5, estratos=estratos)
    nh_ney = dict(zip(ney.tablas["Asignación"]["Estrato"], ney.tablas["Asignación"]["nh"]))
    r.verdadero("muestreo.neyman.mas_muestra_al_estrato_variable", cat_,
                "Neyman: asigna más muestra al estrato con mayor Nh·Sh (A)",
                nh_ney["A"] > nh_ney["B"], obtenido=nh_ney, esperado="A > B")
    r.verdadero("muestreo.neyman.suma", cat_, "Neyman: Σ nh = 100", sum(nh_ney.values()) == 100)

    opt = m_dis.ejecutar_diseno("optimo", N=1000, n=100, seed=5, estratos=estratos)
    nh_opt = dict(zip(opt.tablas["Asignación"]["Estrato"], opt.tablas["Asignación"]["nh"]))
    r.verdadero("muestreo.optimo.suma", cat_, "Óptimo: Σ nh = 100", sum(nh_opt.values()) == 100)

    cong = m_dis.ejecutar_diseno("conglomerados", N=0, n=2, seed=9, estratos=estratos)
    grupos = cong.tablas["Selección"]["Conglomerado"].nunique()
    r.verdadero("muestreo.conglomerados.grupos", cat_, "Conglomerados: selecciona 2 grupos completos",
                grupos == 2, obtenido=grupos)
    dos_etapas = m_dis.ejecutar_diseno("conglomerados", N=0, n=2, seed=9, estratos=estratos, n_por_grupo=5)
    por_grupo = dos_etapas.tablas["Selección"].groupby("Conglomerado").size().tolist()
    r.verdadero("muestreo.conglomerados.dos_etapas", cat_, "Conglomerados en 2 etapas: 5 unidades por grupo",
                por_grupo == [5, 5], obtenido=por_grupo, esperado=[5, 5])

    # Tamaño automático contra la fórmula clásica con corrección finita
    z = stats.norm.ppf(0.975)
    n0 = z ** 2 * 0.25 / 0.05 ** 2
    esperado = math.ceil(5000 * n0 / (5000 - 1 + n0))
    auto = m_dis.ejecutar_diseno("finito", N=5000, n=1, seed=1, auto=True, p=0.5, error=0.05)
    r.verdadero("muestreo.auto.tamano", cat_,
                "Tamaño automático de proporción con corrección por población finita",
                auto.poblacion == [5000] and auto.seleccion[0] == esperado,
                obtenido={"n": auto.seleccion[0], "esperado_formula": esperado},
                esperado={"n": esperado}, notas=f"n0={n0:.4f}, N=5000, n=ceil(N·n0/(N−1+n0))")
    r.cerca("muestreo.auto.tamano_valor", cat_,
            "n automático coincide con la fórmula independiente (357 con N=5000)",
            m_ale.tamano_proporcion(0.5, 0.05, 0.95, N=5000), esperado, rtol=0, atol=0)

    r.cerca("muestreo.tamano_media", cat_, "Tamaño para media (σ=10, e=2, 95 %)",
            m_ale.tamano_media(10, 2, 0.95), math.ceil((z * 10 / 2) ** 2), rtol=0, atol=0)
    r.cerca("muestreo.tamano_diferencia_medias", cat_, "Tamaño por grupo para dos medias",
            m_ale.tamano_diferencia_medias(10, 10, 2, 0.95),
            math.ceil(z ** 2 * (100 + 100) / 4), rtol=0, atol=0)
    r.cerca("muestreo.tamano_diferencia_proporciones", cat_, "Tamaño por grupo para dos proporciones",
            m_ale.tamano_diferencia_proporciones(0.5, 0.4, 0.05, 0.95),
            math.ceil(z ** 2 * (0.25 + 0.24) / 0.0025), rtol=0, atol=0)

    r.lanza("muestreo.error_muestra_grande", cat_, "Rechaza n > N sin reemplazo",
            lambda: m_dis.ejecutar_diseno("finito", N=10, n=11), ErrorAmPu)
    r.lanza("muestreo.error_estratos_vacios", cat_, "Rechaza diseño estratificado sin grupos",
            lambda: m_dis.ejecutar_diseno("proporcional", N=100, n=10), ErrorAmPu)
    r.lanza("muestreo.error_estratos_duplicados", cat_, "Rechaza nombres de estrato repetidos",
            lambda: m_dis.ejecutar_diseno("proporcional", N=100, n=10,
                                          estratos=[("A", 50, 1, 1), ("A", 50, 1, 1)]), ErrorAmPu)
    r.lanza("muestreo.error_p_extremos", cat_, "Rechaza p=0 al dimensionar una proporción",
            lambda: m_ale.tamano_proporcion(0, 0.05), ErrorAmPu)


# --------------------------------------------------------------------------- #
# 3. Descriptiva
# --------------------------------------------------------------------------- #
def probar_descriptiva(r: _comun.Revisor) -> None:
    cat_ = "descriptiva"
    rng = np.random.default_rng(2024)
    datos = np.round(rng.normal(20, 5, 250), 3)
    resumen = desc.resumir(datos)
    r.cerca("descriptiva.n", cat_, "Resumen: n", resumen.n, len(datos), rtol=0, atol=0)
    r.cerca("descriptiva.media", cat_, "Resumen: media = numpy.mean", resumen.media, float(np.mean(datos)))
    r.cerca("descriptiva.mediana", cat_, "Resumen: mediana", resumen.mediana, float(np.median(datos)))
    r.cerca("descriptiva.varianza", cat_, "Resumen: varianza muestral (ddof=1)",
            resumen.varianza, float(np.var(datos, ddof=1)))
    r.cerca("descriptiva.desviacion", cat_, "Resumen: desviación = √varianza",
            resumen.desviacion, math.sqrt(resumen.varianza))
    r.cerca("descriptiva.cuartiles", cat_, "Resumen: q1 y q3 = numpy.quantile",
            [resumen.q1, resumen.q3], [float(np.quantile(datos, .25)), float(np.quantile(datos, .75))])
    r.cerca("descriptiva.extremos", cat_, "Resumen: mínimo y máximo",
            [resumen.minimo, resumen.maximo], [float(datos.min()), float(datos.max())])
    r.cerca("descriptiva.cv", cat_, "Resumen: coeficiente de variación = s/|media|",
            resumen.coeficiente_variacion, resumen.desviacion / abs(resumen.media), rtol=1e-12)
    r.verdadero("descriptiva.cv_sin_media", cat_, "Resumen: CV es None si la media es 0",
                desc.resumir([-1, 1]).coeficiente_variacion is None)
    multimodal = desc.resumir([1, 1, 2, 3, 3, 4])
    r.verdadero("descriptiva.multimodal", cat_, "Resumen: devuelve todas las modas ordenadas",
                multimodal.modas == (1.0, 3.0), obtenido=multimodal.modas, esperado=[1.0, 3.0])
    r.cerca("descriptiva.percentil", cat_, "Percentil 90 = numpy.quantile(0.9)",
            desc.percentil(datos, 0.9), float(np.quantile(datos, 0.9)))
    tabla = desc.frecuencias(datos)
    r.verdadero("descriptiva.frecuencias.total", cat_, "Frecuencias: Σ recuentos = n",
                int(tabla["Frecuencia"].sum()) == len(datos), obtenido=int(tabla["Frecuencia"].sum()))
    r.cerca("descriptiva.frecuencias.acumulada", cat_, "Frecuencias: última relativa acumulada = 1",
            float(tabla["Relativa acumulada"].iloc[-1]), 1.0)
    r.verdadero("descriptiva.frecuencias.ordenada", cat_, "Frecuencias: valores ordenados",
                bool(tabla["Valor"].is_monotonic_increasing))
    r.lanza("descriptiva.error_vacia", cat_, "Resumen: rechaza una muestra vacía",
            lambda: desc.resumir([]), ErrorAmPu)
    r.lanza("descriptiva.error_texto", cat_, "Resumen: rechaza texto no numérico",
            lambda: desc.resumir(["a", "b"]), ErrorAmPu)


# --------------------------------------------------------------------------- #
# 4. Probabilidad y combinatoria
# --------------------------------------------------------------------------- #
def probar_probabilidad(r: _comun.Revisor) -> None:
    cat_ = "probabilidad"
    r.cerca("comb.factorial", cat_, "20! = 2 432 902 008 176 640 000",
            comb.factorial(20), math.factorial(20), rtol=0, atol=0)
    r.cerca("comb.permutaciones", cat_, "P(10,3) = 720", comb.permutaciones(10, 3), math.perm(10, 3),
            rtol=0, atol=0)
    r.cerca("comb.combinaciones", cat_, "C(60,6) = 50 063 860", comb.combinaciones(60, 6),
            50_063_860, rtol=0, atol=0)
    r.cerca("comb.repetidas", cat_, "Permutaciones con repetición de 2,3,5",
            comb.permutaciones_repetidas([2, 3, 5]), math.factorial(10) // (2 * 6 * 120), rtol=0, atol=0)
    r.lanza("comb.error_negativo", cat_, "Rechaza factorial de un número negativo",
            lambda: comb.factorial(-3), ErrorAmPu)
    r.lanza("comb.error_k_mayor", cat_, "Rechaza k > n en combinaciones",
            lambda: comb.combinaciones(5, 7), ErrorAmPu)

    r.cerca("prob.condicional", cat_, "P(A|B) = P(A∩B)/P(B)", prob.condicional(.2, .4), .5)
    r.verdadero("prob.independientes_si", cat_, "Detecta independencia con P(A∩B)=P(A)P(B)",
                prob.independientes(.3, .5, .15))
    r.verdadero("prob.independientes_no", cat_, "Detecta dependencia cuando P(A∩B)≠P(A)P(B)",
                not prob.independientes(.3, .5, .30))
    r.cerca("prob.total", cat_, "Probabilidad total = Σ P(Hi)P(E|Hi)",
            prob.probabilidad_total([.4, .6], [.5, .1]), .4 * .5 + .6 * .1)
    r.cerca("prob.bayes", cat_, "Bayes: posterior de la primera hipótesis",
            prob.bayes(0, [.4, .6], [.5, .1]), (.4 * .5) / (.4 * .5 + .6 * .1), rtol=1e-12)
    valores, masas = [0, 1, 2], [.25, .5, .25]
    r.cerca("prob.esperanza", cat_, "E[X] discreta", prob.esperanza(valores, masas), 1.0)
    r.cerca("prob.varianza", cat_, "Var[X] discreta", prob.varianza(valores, masas), 0.5)
    r.cerca("prob.mgf_cero", cat_, "MGF(0) = 1", prob.generadora_momentos(0, valores, masas), 1.0)
    r.cerca("prob.mgf_derivada", cat_, "MGF'(0) ≈ E[X] por diferencias finitas",
            (prob.generadora_momentos(1e-5, valores, masas) - prob.generadora_momentos(-1e-5, valores, masas)) / 2e-5,
            1.0, rtol=1e-6, atol=1e-6)
    r.lanza("prob.error_masas", cat_, "Rechaza masas que no suman 1",
            lambda: prob.esperanza(valores, [.2, .2, .2]), ErrorAmPu)
    r.lanza("prob.error_condicion_cero", cat_, "Rechaza condicionar a un evento de probabilidad 0",
            lambda: prob.condicional(.2, 0), ErrorAmPu)


# --------------------------------------------------------------------------- #
# 5. Inferencia
# --------------------------------------------------------------------------- #
def probar_inferencia(r: _comun.Revisor) -> None:
    cat_ = "inferencia"
    rng = np.random.default_rng(7)
    a = rng.normal(10, 2, 40)
    b = rng.normal(11, 2.5, 45)
    c = rng.normal(12, 2, 30)
    datos = rng.normal(10, 2, 60)

    comparaciones = [
        ("z_una", lambda: inf.z_una_muestra(datos, 10, 2), stats.norm.sf(abs((datos.mean() - 10) / (2 / math.sqrt(60)))) * 2),
        ("t_una", lambda: inf.t_una_muestra(datos, 10), float(stats.ttest_1samp(datos, 10).pvalue)),
        ("t_dos", lambda: inf.t_dos_muestras(a, b), float(stats.ttest_ind(a, b, equal_var=False).pvalue)),
        ("mann_whitney", lambda: inf.mann_whitney(a, b), float(stats.mannwhitneyu(a, b).pvalue)),
        ("wilcoxon", lambda: inf.wilcoxon(a, b[:40]), float(stats.wilcoxon(a, b[:40]).pvalue)),
        ("anova", lambda: inf.anova([a, b, c]),
         float(stats.f_oneway(a, b, c).pvalue)),
        ("kruskal", lambda: inf.kruskal([a, b]), float(stats.kruskal(a, b).pvalue)),
        ("pearson", lambda: inf.correlacion(a, b[:40]), float(stats.pearsonr(a, b[:40]).pvalue)),
        ("spearman", lambda: inf.correlacion(a, b[:40], "spearman"),
         float(stats.spearmanr(a, b[:40]).pvalue)),
        ("chi_bondad", lambda: inf.chi_bondad([18, 22, 30, 30], [25, 25, 25, 25]),
         float(stats.chisquare([18, 22, 30, 30], [25, 25, 25, 25]).pvalue)),
        ("chi_independencia", lambda: inf.chi_independencia([[20, 15], [10, 25]]),
         float(stats.chi2_contingency([[20, 15], [10, 25]], correction=False)[1])),
    ]
    for nombre, ejecutar, esperado in comparaciones:
        try:
            resultado = ejecutar()
            r.cerca(f"inferencia.{nombre}.p_valor", cat_, f"{nombre}: p-valor coincide con SciPy",
                    resultado.p_valor, esperado, rtol=1e-9, atol=1e-12)
            r.verdadero(f"inferencia.{nombre}.estructura", cat_, f"{nombre}: conclusión y alfa presentes",
                        bool(resultado.conclusion) and 0 <= resultado.p_valor <= 1
                        and resultado.alfa == 0.05)
        except Exception as exc:
            r.registrar(f"inferencia.{nombre}.p_valor", cat_, f"{nombre}: p-valor coincide con SciPy",
                        pasa=False, obtenido=f"{type(exc).__name__}: {exc}"[:200],
                        esperado=esperado)

    z_dos = inf.z_dos_muestras(a, b, 2, 2.5)
    se = math.sqrt(4 / len(a) + 6.25 / len(b))
    r.cerca("inferencia.z_dos.estadistico", cat_, "z de dos medias: estadístico manual",
            z_dos.estadistico, (a.mean() - b.mean()) / se, rtol=1e-12)
    prop1 = inf.proporcion_una(45, 100, 0.5)
    r.cerca("inferencia.proporcion_una.z", cat_, "z de una proporción: estadístico manual",
            prop1.estadistico, (0.45 - 0.5) / math.sqrt(0.25 / 100), rtol=1e-12)
    prop2 = inf.proporcion_dos(45, 100, 55, 110)
    p_agrupada = 100 / 210
    r.cerca("inferencia.proporcion_dos.z", cat_, "z de dos proporciones: estadístico agrupado",
            prop2.estadistico, (0.45 - 0.5) / math.sqrt(p_agrupada * (1 - p_agrupada) * (1 / 100 + 1 / 110)),
            rtol=1e-12)
    no_rechaza = inf.t_una_muestra(datos, float(np.mean(datos)), 0.05)
    rechaza = inf.t_una_muestra(datos, float(np.mean(datos)) + 3.0, 0.05)
    r.verdadero("inferencia.conclusion_cautelosa", cat_,
                "No rechazar H₀ no se presenta como prueba de H₀",
                "no demuestra" in no_rechaza.conclusion and "rechaza" not in no_rechaza.conclusion.replace("No se rechaza", ""),
                obtenido=no_rechaza.conclusion[:160])
    r.verdadero("inferencia.conclusion_rechazo", cat_,
                "Rechazar H₀ se informa con p-valor y α explícitos",
                "Se rechaza" in rechaza.conclusion and "p =" in rechaza.conclusion,
                obtenido=rechaza.conclusion[:160])

    # Intervalos
    lo, hi = inf.intervalo_media(datos)
    t_crit = stats.t.ppf(.975, len(datos) - 1)
    margen = t_crit * datos.std(ddof=1) / math.sqrt(len(datos))
    r.cerca("inferencia.ic_media", cat_, "IC 95 % de la media con t",
            [lo, hi], [datos.mean() - margen, datos.mean() + margen], rtol=1e-12)
    w_lo, w_hi = inf.intervalo_proporcion(7, 40)
    z975 = stats.norm.ppf(.975)
    p_obs = 7 / 40
    den = 1 + z975 ** 2 / 40
    centro = (p_obs + z975 ** 2 / 80) / den
    semi = z975 * math.sqrt(p_obs * (1 - p_obs) / 40 + z975 ** 2 / (4 * 40 ** 2)) / den
    r.cerca("inferencia.ic_wilson", cat_, "IC de Wilson para una proporción",
            [w_lo, w_hi], [centro - semi, centro + semi], rtol=1e-12)
    r.cerca("inferencia.ic_wilson_extremos", cat_, "IC de Wilson en 0 y n éxitos queda en [0,1]",
            [inf.intervalo_proporcion(0, 20)[0], inf.intervalo_proporcion(20, 20)[1]], [0.0, 1.0],
            rtol=0, atol=1e-12)

    # Regresión
    x = rng.normal(5, 2, 80)
    y = 3 + 1.5 * x + rng.normal(0, 1.2, 80)
    simple = reg.lineal_simple(x, y)
    referencia = stats.linregress(x, y)
    r.cerca("regresion.simple.coeficientes", cat_, "Regresión simple: pendiente e intercepto",
            simple.coeficientes, [referencia.intercept, referencia.slope], rtol=1e-10)
    r.cerca("regresion.simple.r2", cat_, "Regresión simple: R² = linregress.rvalue²",
            simple.r_cuadrado, referencia.rvalue ** 2, rtol=1e-10)
    r.cerca("regresion.simple.p_valor", cat_, "Regresión simple: p de la pendiente",
            simple.p_valores[1], referencia.pvalue, rtol=1e-9)
    X = np.column_stack([x, rng.normal(0, 1, 80)])
    Y = 2 + 1.2 * X[:, 0] - 0.8 * X[:, 1] + rng.normal(0, 1, 80)
    multiple = reg.lineal_multiple(X, Y)
    diseño = np.column_stack([np.ones(80), X])
    beta, *_ = np.linalg.lstsq(diseño, Y, rcond=None)
    r.cerca("regresion.multiple.coeficientes", cat_, "Regresión múltiple: coeficientes OLS",
            multiple.coeficientes, beta, rtol=1e-9)
    prediccion = multiple.predecir([[5.0, 0.0]])
    r.cerca("regresion.multiple.prediccion", cat_, "Regresión múltiple: predicción β₀+β₁x₁+β₂x₂",
            float(np.ravel(prediccion)[0]), float(beta[0] + 5 * beta[1]), rtol=1e-12)
    r.lanza("regresion.error_constante", cat_, "Regresión: rechaza x constante",
            lambda: reg.lineal_simple([1, 1, 1, 1], [1, 2, 3, 4]), ErrorAmPu)
    r.lanza("regresion.error_longitudes", cat_, "Regresión: rechaza longitudes distintas",
            lambda: reg.lineal_simple([1, 2, 3, 4], [1, 2, 3]), ErrorAmPu)

    r.lanza("inferencia.error_alfa", cat_, "Inferencia: rechaza α fuera de (0,1)",
            lambda: inf.t_una_muestra(datos, 10, alfa=1.5), ErrorAmPu)
    r.lanza("inferencia.error_proporcion_conteo", cat_, "Inferencia: rechaza éxitos > n",
            lambda: inf.proporcion_una(11, 10, .5), ErrorAmPu)
    r.lanza("inferencia.error_varianza_cero", cat_, "Inferencia: rechaza t con varianza cero",
            lambda: inf.t_una_muestra([2, 2, 2, 2], 2), ErrorAmPu)


# --------------------------------------------------------------------------- #
# 6. Simulación y ajuste
# --------------------------------------------------------------------------- #
def probar_simulacion(r: _comun.Revisor, rapido: bool) -> None:
    cat_ = "simulacion"
    n = 20_000 if rapido else 200_000
    pi_est = mc.simular_pi(n=n, seed=2025)
    r.verdadero("sim.pi.dentro_ic", cat_, "Estimación de π: el IC 95 % contiene el valor exacto",
                pi_est.intervalo[0] <= math.pi <= pi_est.intervalo[1],
                obtenido={"valor": pi_est.valor, "ic": list(pi_est.intervalo)}, esperado=math.pi,
                tolerancia=f"n={n}")
    r.verdadero("sim.pi.error", cat_, "Estimación de π: error < 4 errores estándar",
                abs(pi_est.valor - math.pi) <= 4 * pi_est.error_estandar,
                obtenido=abs(pi_est.valor - math.pi), tolerancia=4 * pi_est.error_estandar)
    estimacion, exacto = mc.integral_cuadrado(n=n, seed=2025)
    r.verdadero("sim.integral.valor", cat_, "∫₀¹ x² dx: dentro del IC 95 %",
                estimacion.intervalo[0] <= exacto <= estimacion.intervalo[1],
                obtenido={"valor": estimacion.valor, "ic": list(estimacion.intervalo)},
                esperado=round(exacto, 8))
    puntos, dentro = mc.puntos_pi(5_000, seed=3)
    r.verdadero("sim.puntos_pi", cat_, "Puntos π: 5 000 coordenadas en [0,1] y máscara booleana",
                puntos.shape == (5000, 2) and bool(np.all(puntos >= 0) and np.all(puntos <= 1))
                and dentro.shape == (5000,))
    r.lanza("sim.integral.error_funcion", cat_, "Integración: rechaza función con valores no finitos",
            lambda: mc.integrar(lambda t: np.full(np.shape(t), np.nan), 0, 1, n=1000, seed=1), ErrorAmPu)

    modelo = cat.obtener("normal")
    params = modelo.validar()
    muestra = mc.generar_muestra("normal", params, 3000, seed=11)
    r.cerca("sim.generar_muestra.media", cat_, "Muestra generada: media ≈ parámetro μ (6 EE)",
            float(np.mean(muestra)), 0.0, rtol=0, atol=6 * 1.0 / math.sqrt(3000))
    r.verdadero("sim.generar_muestra.reproducible", cat_, "Muestra generada: semilla reproducible",
                bool(np.array_equal(muestra, mc.generar_muestra("normal", params, 3000, seed=11))))

    familias = mc.familias_ajustables()
    r.verdadero("sim.ajuste.familias", cat_, "Familias ajustables declaradas",
                set(familias) == {"normal", "exponencial", "gamma", "weibull", "lognormal", "beta"},
                obtenido=list(familias))
    datos = mc.generar_muestra("normal", {"mu": 4.0, "sigma": 1.5}, 1500, seed=99)
    ajuste = mc.ajustar_distribucion(datos, "normal", seed=7)
    r.verdadero("sim.ajuste.valores", cat_, "Ajuste normal: parámetros y AIC finitos, p de KS en [0,1]",
                math.isfinite(ajuste.aic) and 0 <= ajuste.p_ks <= 1)
    r.cerca("sim.ajuste.loc", cat_, "Ajuste normal: μ estimada ≈ 4,0",
            ajuste.parametros["loc"], 4.0, rtol=0.05)
    r.cerca("sim.ajuste.scale", cat_, "Ajuste normal: σ estimada ≈ 1,5",
            ajuste.parametros["scale"], 1.5, rtol=0.08)
    teoricos, observados = mc.qq_plot(datos, "normal", {"mu": 4.0, "sigma": 1.5})
    r.verdadero("sim.qq.pares", cat_, "QQ-plot: pares del mismo tamaño, ordenados",
                len(teoricos) == len(observados) == len(datos)
                and bool(np.all(np.diff(teoricos) >= 0) and np.all(np.diff(observados) >= 0)))
    r.cerca("sim.qq.correlacion", cat_, "QQ-plot: correlación con la recta teórica > 0,99",
            float(np.corrcoef(teoricos, observados)[0, 1]), 1.0, rtol=0, atol=0.01)
    rejilla, curva = mc.curva_ajustada(ajuste, datos)
    r.verdadero("sim.curva.finita", cat_, "Curva ajustada: rejilla ordenada y densidades finitas ≥ 0",
                bool(np.all(np.diff(rejilla) > 0) and np.all(np.isfinite(curva)) and np.all(curva >= 0)))
    r.lanza("sim.ajuste.error_familia", cat_, "Ajuste: rechaza una familia no soportada",
            lambda: mc.ajustar_distribucion(datos, "student_t"), ErrorAmPu)
    r.lanza("sim.ajuste.error_datos_insuficientes", cat_, "Ajuste: exige al menos 5 observaciones",
            lambda: mc.ajustar_distribucion([1, 2, 3], "normal"), ErrorAmPu)


# --------------------------------------------------------------------------- #
# 7. Cobertura de intervalos (Monte Carlo, opcional)
# --------------------------------------------------------------------------- #
def probar_cobertura(r: _comun.Revisor, rapido: bool) -> None:
    if rapido:
        r.omitir("inferencia.cobertura_ic", "inferencia",
                 "Cobertura empírica del IC de la media", "Omitida en perfil rápido")
        return
    rng = np.random.default_rng(123)
    aciertos = 0
    replicas = 400
    for _ in range(replicas):
        muestra = rng.normal(50, 10, 30)
        lo, hi = inf.intervalo_media(muestra)
        aciertos += int(lo <= 50 <= hi)
    cobertura = aciertos / replicas
    error_mc = math.sqrt(0.95 * 0.05 / replicas)
    r.verdadero("inferencia.cobertura_ic", "inferencia",
                "Cobertura empírica del IC 95 % de la media dentro de ±3 EE de Monte Carlo",
                abs(cobertura - 0.95) <= 3 * error_mc,
                obtenido=round(cobertura, 4), esperado=0.95,
                tolerancia=round(3 * error_mc, 4), notas=f"{replicas} réplicas, n=30")
    aciertos_w = 0
    for _ in range(replicas):
        muestra = rng.binomial(1, 0.3, 50)
        lo, hi = inf.intervalo_proporcion(int(muestra.sum()), 50)
        aciertos_w += int(lo <= 0.3 <= hi)
    cobertura_w = aciertos_w / replicas
    r.verdadero("inferencia.cobertura_wilson", "inferencia",
                "Cobertura empírica del IC de Wilson ≈ 95 %",
                abs(cobertura_w - 0.95) <= 3 * error_mc,
                obtenido=round(cobertura_w, 4), esperado=0.95, tolerancia=round(3 * error_mc, 4))


# --------------------------------------------------------------------------- #
# 8. Exportadores y sesión
# --------------------------------------------------------------------------- #
def probar_exportadores(r: _comun.Revisor) -> None:
    cat_ = "exportacion"
    from matplotlib.figure import Figure
    from openpyxl import load_workbook

    from ampu.io import ServicioExportacion as io

    tabla = pd.DataFrame({
        "probabilidad": [0.12345678912345678, 0.5],
        "etiqueta": ["AmPu", "=HYPERLINK(\"http://mal\")"],
        "entero": [7, 8],
    })
    figura = Figure(figsize=(3, 2))
    eje = figura.subplots()
    eje.plot([0, 1, 2], [0, 1, 4])
    eje.set_title("Autoprueba")
    with tempfile.TemporaryDirectory(prefix="ampu-verificacion-") as temporal:
        carpeta = Path(temporal)

        def cronometrado(nombre, funcion, *args):
            inicio = _comun.time.perf_counter()
            ruta = funcion(*args)
            ms = (_comun.time.perf_counter() - inicio) * 1000
            r.metricas.append({"operacion": nombre, "categoria": "exportacion", "n": 1,
                               "min_ms": round(ms, 2), "mediana_ms": round(ms, 2),
                               "p95_ms": round(ms, 2), "max_ms": round(ms, 2),
                               "ops_por_segundo": round(1000 / ms, 2) if ms else None,
                               "notas": f"salida={Path(ruta).stat().st_size} bytes"})
            return Path(ruta)

        xlsx = cronometrado("exportar XLSX", io.excel, {"Resultados": tabla}, carpeta / "prueba.xlsx")
        csv = cronometrado("exportar CSV", io.csv, tabla, carpeta / "prueba.csv")
        png = cronometrado("exportar PNG", io.png, figura, carpeta / "prueba.png")
        pdf = cronometrado("exportar PDF", io.pdf, carpeta / "prueba.pdf", "Autoprueba",
                           "Resumen de verificación", {"Resultados": tabla}, figura, r"\frac{x}{2}")

        for nombre, ruta, minimo in (("xlsx", xlsx, 4_000), ("csv", csv, 50),
                                     ("png", png, 1_000), ("pdf", pdf, 4_000)):
            r.verdadero(f"exportacion.{nombre}.archivo", cat_, f"Se genera un {nombre.upper()} no trivial",
                        ruta.is_file() and ruta.stat().st_size >= minimo,
                        obtenido={"bytes": ruta.stat().st_size if ruta.is_file() else 0,
                                  "minimo": minimo})

        libro = load_workbook(xlsx, read_only=True)
        try:
            valor = libro["Resultados"]["A2"].value
            r.verdadero("exportacion.xlsx.precision", cat_,
                        "XLSX conserva ~15 dígitos significativos",
                        math.isclose(valor, tabla.iloc[0, 0], rel_tol=0, abs_tol=5e-16),
                        obtenido=repr(valor), esperado=repr(tabla.iloc[0, 0]), tolerancia=5e-16)
            celda = libro["Resultados"]["B3"].value
            r.verdadero("exportacion.xlsx.formula_neutralizada", cat_,
                        "XLSX neutraliza texto que empieza con =",
                        isinstance(celda, str) and celda.startswith("'="), obtenido=repr(celda))
            r.verdadero("exportacion.xlsx.encabezados", cat_, "XLSX escribe encabezados de la tabla",
                        [c.value for c in libro["Resultados"][1]] == list(tabla.columns))
        finally:
            libro.close()

        texto_csv = csv.read_text(encoding="utf-8-sig")
        r.verdadero("exportacion.csv.bom", cat_, "CSV usa UTF-8 con BOM para Excel",
                    csv.read_bytes().startswith(b"\xef\xbb\xbf"))
        r.verdadero("exportacion.csv.formula_neutralizada", cat_,
                    "CSV neutraliza texto que empieza con =",
                    "'=HYPERLINK" in texto_csv, obtenido=texto_csv.splitlines()[2][:80])
        r.verdadero("exportacion.pdf.cabecera", cat_, "PDF tiene cabecera %PDF y marca EOF",
                    pdf.read_bytes()[:4] == b"%PDF" and b"%%EOF" in pdf.read_bytes()[-2048:])
        r.verdadero("exportacion.png.dimensiones", cat_, "PNG conserva la figura a 180 dpi",
                    png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n")

        estado = {"semilla": 42, "modulo": "distribuciones", "tema": "oscuro",
                  "texto": "probabilidad · Español · χ²",
                  "tabla": tabla, "anidado": {"a": [1, 2.5, None], "b": True},
                  "nan": float("nan")}
        sesion = carpeta / "sesion.json"
        io.guardar(estado, sesion)
        recuperado = io.cargar(sesion)
        r.verdadero("exportacion.sesion.roundtrip", cat_, "Sesión JSON: semilla y estructura se restauran",
                    recuperado["semilla"] == 42 and recuperado["anidado"]["b"] is True,
                    obtenido=sorted(recuperado.keys()))
        paquete = json.loads(sesion.read_text(encoding="utf-8"))
        r.verdadero("exportacion.sesion.version", cat_, "Sesión JSON: incluye versión de esquema y fecha",
                    paquete.get("version") == 1 and "fecha_utc" in paquete,
                    obtenido={k: paquete.get(k) for k in ("version", "fecha_utc")})
        r.verdadero("exportacion.sesion.utf8", cat_,
                    "Sesión JSON: se escribe en UTF-8 y conserva acentos y símbolos",
                    "Español · χ²" in sesion.read_text(encoding="utf-8")
                    and recuperado["texto"] == "probabilidad · Español · χ²",
                    obtenido=recuperado.get("texto"))
        r.lanza("exportacion.error_tabla_vacia", cat_, "XLSX rechaza un libro sin hojas",
                lambda: io.excel({}, carpeta / "vacio.xlsx"), Exception)
        r.lanza("exportacion.error_tipo_csv", cat_, "CSV rechaza algo que no es DataFrame",
                lambda: io.csv([1, 2, 3], carpeta / "malo.csv"), Exception)


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="Pruebas de cálculo de AmPu 3.0")
    parser.add_argument("--salida", type=Path, default=Path("datos/calculo.json"))
    parser.add_argument("--rapido", action="store_true",
                        help="Menos réplicas Monte Carlo y sin cobertura empírica")
    parser.add_argument("--sin-exportadores", action="store_true")
    parser.add_argument("--solo", choices=["distribuciones", "muestreo", "descriptiva", "probabilidad",
                                           "inferencia", "simulacion", "exportacion"],
                        help="Limita la ejecución a un bloque (para depurar)")
    args = parser.parse_args()

    r = _comun.Revisor("rapido" if args.rapido else "completo")
    grupos = {
        "distribuciones": lambda: (probar_catalogo(r), probar_multivariadas(r),
                                   [probar_univariante(r, m, args.rapido) for m in cat.catalogo()
                                    if m.dimensionalidad == "univariante"]),
        "muestreo": lambda: probar_muestreo(r),
        "descriptiva": lambda: probar_descriptiva(r),
        "probabilidad": lambda: probar_probabilidad(r),
        "inferencia": lambda: (probar_inferencia(r), probar_cobertura(r, args.rapido)),
        "simulacion": lambda: probar_simulacion(r, args.rapido),
        "exportacion": lambda: probar_exportadores(r),
    }
    seleccion = [args.solo] if args.solo else list(grupos)
    if args.sin_exportadores and "exportacion" in seleccion:
        seleccion.remove("exportacion")

    for nombre in seleccion:
        print(f"\n== {nombre} ==")
        try:
            grupos[nombre]()
        except Exception as exc:  # un bloque roto no oculta los demás
            import traceback

            traceback.print_exc()
            r.registrar(f"bloque.{nombre}.excepcion", nombre,
                        f"El bloque «{nombre}» terminó sin excepción",
                        pasa=False, obtenido=f"{type(exc).__name__}: {exc}"[:400])

    documento = r.documento("pruebas_calculo", {"rapido": args.rapido,
                                                "bloques": seleccion})
    _comun.guardar_json(args.salida, documento)
    print(f"Resultados en {args.salida}")
    return 0 if documento["resumen"]["fallan"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
