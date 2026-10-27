"""Genera reporte JSON de errores del adaptador AmPu respecto a scipy.stats.

Desde AmPu 3.0: python scripts/validar_contra_scipy.py [--salida dist/reporte.json]
"""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import stats

from ampu.core.distribuciones import catalogo, obtener


REFERENCIAS = {
    "bernoulli": stats.bernoulli(.4), "binomial": stats.binom(10, .5),
    "binomial_negativa": stats.nbinom(2, .5), "geometrica": stats.geom(.5),
    "hipergeometrica": stats.hypergeom(30, 12, 8), "poisson": stats.poisson(3),
    "uniforme_discreta": stats.randint(1, 7), "uniforme": stats.uniform(1, 4),
    "normal_estandar": stats.norm(), "normal": stats.norm(),
    "chi_cuadrado": stats.chi2(5), "exponencial": stats.expon(scale=1),
    "t_student": stats.t(5), "f_fisher": stats.f(5, 10),
    "gamma": stats.gamma(2, scale=2), "erlang": stats.erlang(3),
    "beta": stats.beta(2, 5), "lognormal": stats.lognorm(.5, scale=1),
    "weibull": stats.weibull_min(1.5, scale=2), "cauchy": stats.cauchy(),
    "logistica": stats.logistic(), "triangular": stats.triang(.25, scale=4),
    "pareto": stats.pareto(3, scale=1),
}


def diferencias() -> list[dict]:
    """Contrasta PMF/PDF, CDF, PPF y momentos para valores por defecto."""
    filas = []
    for modelo in catalogo():
        d = modelo.clave
        params = modelo.validar()
        if d in REFERENCIAS:
            referencia = REFERENCIAS[d]
            x = np.asarray(referencia.ppf([.1, .3, .5, .7, .9]))
            funcion = "pmf" if modelo.discreta else "pdf"
            pares = [(funcion, (modelo.pmf if modelo.discreta else modelo.pdf)(x, **params), getattr(referencia, funcion)(x)),
                     ("cdf", modelo.cdf(x, **params), referencia.cdf(x)),
                     ("ppf", modelo.ppf([.2, .5, .8], **params), referencia.ppf([.2, .5, .8])),
                     ("media", modelo.media(**params), referencia.mean()),
                     ("varianza", modelo.varianza(**params), referencia.var())]
        elif d == "multinomial":
            x = [2, 2, 4]
            pares = [("pmf", modelo.pmf(x, **params), stats.multinomial.pmf(x, 8, params["p"])),
                     ("media", modelo.media(**params), stats.multinomial.mean(8, params["p"]))]
        elif d == "normal_bivariada":
            ref = stats.multivariate_normal([0,0], [[1,.4],[.4,1]])
            pares = [("pdf", modelo.pdf([0,0], **params), ref.pdf([0,0])),
                     ("cdf", modelo.cdf([0,0], **params), ref.cdf([0,0]))]
        else:
            x = [.2, .3, .5]
            pares = [("pdf", modelo.pdf(x, **params), stats.dirichlet.pdf(x, params["alpha"])),
                     ("media", modelo.media(**params), stats.dirichlet.mean(params["alpha"]))]
        for operacion, obtenido, esperado in pares:
            a, b = np.asarray(obtenido, dtype=float), np.asarray(esperado, dtype=float)
            finitos = np.isfinite(a) & np.isfinite(b)
            # Pareto/Cauchy pueden carecer de momentos; dos NaN/inf iguales están bien.
            error = np.max(np.abs(a[finitos]-b[finitos])) if np.any(finitos) else 0.
            coincide = bool(np.allclose(a, b, rtol=1e-10, atol=1e-12, equal_nan=True))
            filas.append({"distribucion": d, "operacion": operacion, "error_absoluto_maximo": float(error), "pasa": coincide})
    return filas


def main():
    """Escribe reporte legible por máquina y retorna error en desacuerdos."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, default=Path("dist/diferencias_scipy.json"))
    args = parser.parse_args()
    filas = diferencias()
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps({"tolerancia_relativa": 1e-10, "comparaciones": filas}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{sum(f['pasa'] for f in filas)}/{len(filas)} comparaciones superadas · {args.salida}")
    if not all(f["pasa"] for f in filas):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
