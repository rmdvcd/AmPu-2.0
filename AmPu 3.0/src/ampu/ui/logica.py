"""Operaciones de presentación puras compartidas por las vistas Dear PyGui.

Estas funciones reciben valores, nunca identificadores de widgets. Por tanto se
pueden ejecutar en un trabajador y probar sin crear un contexto gráfico.
"""

from dataclasses import asdict

import numpy as np
import pandas as pd

from ampu.core.distribuciones import obtener
from ampu.core.errores import ParametroInvalidoError
from ampu.core.estadistica import combinatoria as c, probabilidad as p
from ampu.core.estadistica import inferencia as i, regresion as r
from ampu.core.estadistica.descriptiva import frecuencias, resumir
from ampu.core.estadistica.inferencia import correlacion
from ampu.core.simulacion.montecarlo import (
    ajustar_distribucion, curva_ajustada, generar_muestra, integral_cuadrado,
    puntos_pi, qq_plot, simular_pi,
)
from ampu.ui.entradas import grupos, matriz, numeros


def _resumir_datos(texto_x: str, texto_y: str):
    """Analiza entradas fuera del hilo principal; sin operaciones en widgets."""
    x = numeros(texto_x)
    y = numeros(texto_y) if texto_y.strip() else None
    if y is not None and len(x) != len(y):
        raise ParametroInvalidoError("X e Y deben contener igual número de observaciones.")
    r = resumir(x)
    corr = correlacion(x, y).estadistico if y is not None and len(x) >= 3 else None
    tabla = pd.DataFrame([{"Estadístico": clave.replace("_", " ").capitalize(), "Resultado": str(valor) if isinstance(valor, tuple) else valor}
                          for clave, valor in asdict(r).items()])
    originales = pd.DataFrame({"X": x, **({"Y": y} if y is not None else {})})
    return r, corr, {"Frecuencias": frecuencias(x), "Resumen": tabla, "Datos": originales}, x, y


def _resolver_probabilidad(tipo: str, n: int, k: int, a: float, b: float,
                           pri: str, ver: str, t: float):
    """Resuelve consultas discretas sin usar Qt en el hilo de cálculo."""
    if tipo == "combinatoria":
        datos = {"Factorial n!": c.factorial(n), "Permutaciones P(n,k)": c.permutaciones(n, k),
                 "Combinaciones C(n,k)": c.combinaciones(n, k)}
        tabla = pd.DataFrame({"Operación": list(datos), "Resultado exacto": [str(x) for x in datos.values()]})
        return f"C({n},{k}) = {datos['Combinaciones C(n,k)']} elecciones sin orden.", tabla, ["n!", "P(n,k)", "C(n,k)"], [float(v) for v in datos.values()]
    if tipo == "condicional":
        cond = p.condicional(a, b)
        tabla = pd.DataFrame({"Magnitud": ["P(A∩B)", "P(B)", "P(A|B)"], "Valor": [a, b, cond]})
        return f"P(A|B) = {cond:.6g}. La independencia necesita además P(A).", tabla, ["Conjunta", "Condicional"], [a, cond]
    priores, condiciones = numeros(pri), numeros(ver)
    if tipo == "bayes":
        if len(priores) != len(condiciones):
            raise ParametroInvalidoError("Las listas previas y verosimilitudes deben tener la misma longitud.")
        total = p.probabilidad_total(priores.tolist(), condiciones.tolist())
        if total == 0:
            raise ParametroInvalidoError("No se define Bayes para evidencia de probabilidad cero.")
        posteriores = [p.bayes(j, priores.tolist(), condiciones.tolist()) for j in range(len(priores))]
        tabla = pd.DataFrame({"Hipótesis": [f"B{j+1}" for j in range(len(priores))], "Priori": priores,
                              "Verosimilitud": condiciones, "Posterior": posteriores})
        return (f"P(evidencia) = {total:.6g}; posterior de B1 = {posteriores[0]:.6g}.", tabla,
                [f"B{j+1}" for j in range(len(priores))], posteriores)
    if len(priores) != len(condiciones):
        raise ParametroInvalidoError("Soporte y masas deben tener igual longitud.")
    media = p.esperanza(priores, condiciones)
    var = p.varianza(priores, condiciones)
    mgf = p.generadora_momentos(t, priores, condiciones)
    tabla = pd.DataFrame({"x": priores, "P(X=x)": condiciones})
    return (f"E(X)={media:.6g}, Var(X)={var:.6g}, M_X({t:g})={mgf:.6g}.", tabla,
            [str(v) for v in priores], list(condiciones))


OPCIONES = [
    ("z · una media", "z_una", "prueba_z_una"), ("z · dos medias", "z_dos", "prueba_z_dos"),
    ("t · una media", "t_una", "prueba_t_una"), ("t de Welch · dos medias", "t_dos", "prueba_t_dos"),
    ("z · una proporción", "prop_una", "prueba_proporcion_una"), ("z · dos proporciones", "prop_dos", "prueba_proporcion_dos"),
    ("χ² · bondad de ajuste", "chi_bondad", "chi_bondad"), ("χ² · independencia", "chi_independencia", "chi_independencia"),
    ("ANOVA · una vía", "anova", "anova"), ("Correlación · Pearson", "pearson", "correlacion"),
    ("Correlación · Spearman", "spearman", "correlacion"), ("Regresión · simple", "reg_simple", "regresion"),
    ("Regresión · múltiple", "reg_multiple", "regresion"), ("Mann–Whitney U", "mann", "mann_whitney"),
    ("Wilcoxon pareado", "wilcoxon", "wilcoxon"), ("Kruskal–Wallis", "kruskal", "kruskal"),
]


EJEMPLOS = {
    "chi_bondad": ("12, 15, 23", "15, 15, 20", "X = observadas; Y = esperadas (totales iguales)."),
    "chi_independencia": ("18, 12\n10, 20", "", "X = matriz de contingencia (una fila por línea)."),
    "anova": ("2, 3, 4, 5\n9, 10, 11, 12\n5, 6, 7, 8", "", "X = un grupo por línea; cada grupo con dos o más datos."),
    "kruskal": ("1, 2, 3, 4\n4, 5, 6, 7\n2, 3, 4, 5", "", "X = un grupo por línea."),
    "reg_multiple": ("1, 1\n2, 4\n3, 9\n4, 16\n5, 25\n6, 36\n7, 49", "4, 6, 8, 10, 12, 14, 16", "X = matriz filas×predictores; Y = respuesta."),
}


def _evaluar(tipo: str, x_txt: str, y_txt: str, alfa: float, mu0: float, s1: float,
             s2: float, p0: float, x1: int, n1: int, x2: int, n2: int) -> dict:
    """Despacha todas las pruebas a ``core.estadistica`` en un hilo de fondo."""
    grafico = None
    if tipo in ("prop_una", "prop_dos"):
        prueba = i.proporcion_una(x1, n1, p0, alfa) if tipo == "prop_una" else i.proporcion_dos(x1, n1, x2, n2, alfa)
        grafico = ("barras", ["Grupo A", "Grupo B"] if tipo == "prop_dos" else ["Éxitos", "Fracasos"],
                   list(prueba.detalles["proporciones_observadas"]) if tipo == "prop_dos" else
                   [prueba.detalles["proporcion_observada"], prueba.detalles["proporcion_fallos"]])
    elif tipo == "chi_independencia":
        muestra = matriz(x_txt)
        prueba = i.chi_independencia(muestra, alfa)
        grafico = ("barras", [f"Fila {j+1}" for j in range(muestra.shape[0])],
                   prueba.detalles["totales_fila"])
    elif tipo in ("anova", "kruskal"):
        muestras = grupos(x_txt)
        prueba = i.anova(muestras, alfa) if tipo == "anova" else i.kruskal(muestras, alfa)
        grafico = ("barras", [f"Grupo {j+1}" for j in range(len(muestras))],
                   prueba.detalles["medias"] if tipo == "anova" else prueba.detalles["medias_descriptivas"])
    elif tipo == "reg_multiple":
        X, y = matriz(x_txt), numeros(y_txt)
        modelo = r.lineal_multiple(X, y, confianza=1-alfa)
        tabla = pd.DataFrame({"Coeficiente": modelo.nombres, "Estimación": modelo.coeficientes,
                              "p-valor": modelo.p_valores, "IC inferior": modelo.intervalos[:, 0], "IC superior": modelo.intervalos[:, 1]})
        return {"tabla": tabla, "resumen": modelo.conclusion, "estadistico": modelo.r_cuadrado,
                "p": float(modelo.p_valores[1:].min()), "intervalo": None,
                "grafico": ("dispersion", y, modelo.predecir(X), None, "Observado vs predicho"), "regresion": True}
    elif tipo == "chi_bondad":
        a, b = numeros(x_txt), numeros(y_txt)
        prueba = i.chi_bondad(a, b, alfa)
        grafico = ("barras", [f"Clase {j+1}" for j in range(len(a))], list(a))
    else:
        x = numeros(x_txt)
        y = numeros(y_txt) if tipo in ("z_dos", "t_dos", "pearson", "spearman", "reg_simple", "mann", "wilcoxon") else None
        if tipo == "z_una":
            prueba = i.z_una_muestra(x, mu0, s1, alfa)
        elif tipo == "z_dos":
            prueba = i.z_dos_muestras(x, y, s1, s2, alfa)
        elif tipo == "t_una":
            prueba = i.t_una_muestra(x, mu0, alfa)
        elif tipo == "t_dos":
            prueba = i.t_dos_muestras(x, y, alfa)
        elif tipo in ("pearson", "spearman"):
            prueba = i.correlacion(x, y, tipo, alfa)
        elif tipo == "reg_simple":
            modelo = r.lineal_simple(x, y, confianza=1-alfa)
            tabla = pd.DataFrame({"Coeficiente": modelo.nombres, "Estimación": modelo.coeficientes,
                                  "p-valor": modelo.p_valores, "IC inferior": modelo.intervalos[:, 0], "IC superior": modelo.intervalos[:, 1]})
            return {"tabla": tabla, "resumen": modelo.conclusion, "estadistico": modelo.r_cuadrado,
                    "p": float(modelo.p_valores[1]), "intervalo": tuple(modelo.intervalos[1]),
                    "grafico": ("dispersion", x, y, modelo.predecir(x[:, None]), "Regresión lineal simple"), "regresion": True}
        elif tipo == "mann":
            prueba = i.mann_whitney(x, y, alfa)
        elif tipo == "wilcoxon":
            prueba = i.wilcoxon(x, y, alfa)
        else:
            raise ValueError("Prueba no registrada.")
        grafico = ("dispersion", x, y, None, "Datos pareados") if tipo in ("pearson", "spearman") else ("histograma", x)
    resumen = prueba.conclusion
    if prueba.detalles.get("advertencia"):
        resumen += " " + prueba.detalles["advertencia"]
    contenido = [("Método", prueba.metodo), ("Estadístico", prueba.estadistico),
                 ("p-valor", prueba.p_valor), ("α", prueba.alfa), ("Grados de libertad", prueba.gl),
                 ("IC inferior", prueba.intervalo[0] if prueba.intervalo else None),
                 ("IC superior", prueba.intervalo[1] if prueba.intervalo else None),
                 ("Conclusión", resumen)]
    return {"tabla": pd.DataFrame(contenido, columns=["Resultado", "Valor"]),
            "resumen": resumen, "estadistico": prueba.estadistico,
            "p": prueba.p_valor, "intervalo": prueba.intervalo,
            "grafico": grafico, "regresion": False}


def _simular(tipo: str, clave: str, params: dict, n: int, seed: int, texto: str) -> dict:
    """Opera en un hilo secundario, devuelve datos y especificación del gráfico."""
    if tipo == "pi":
        estimacion = simular_pi(n, seed)
        puntos, mascara = puntos_pi(min(n, 1000), seed)
        tabla = pd.DataFrame({"Indicador": ["Estimación π", "Error estándar", "IC inferior", "IC superior", "Simulaciones", "Semilla"],
                              "Valor": [estimacion.valor, estimacion.error_estandar, *estimacion.intervalo, n, seed]})
        return {"tabla": tabla, "resumen": f"π ≈ {estimacion.valor:.6g}; IC de simulación 95 %: {estimacion.intervalo[0]:.5g} a {estimacion.intervalo[1]:.5g}. No se infiere incertidumbre de un modelo externo.",
                "grafico": ("pi", puntos, mascara), "valor": estimacion.valor, "error": estimacion.error_estandar}
    if tipo == "integral":
        est, referencia = integral_cuadrado(n, seed)
        tabla = pd.DataFrame({"Indicador": ["Integral estimada", "Error estándar", "IC inferior", "IC superior", "Simulaciones", "Semilla"],
                              "Valor": [est.valor, est.error_estandar, *est.intervalo, n, seed]})
        return {"tabla": tabla, "resumen": f"Integral ∫₀¹ x² dx ≈ {est.valor:.6g}; error de simulación {est.error_estandar:.4g}.",
                "grafico": ("barras", ["Integral estimada", "Referencia exacta"], [est.valor, referencia]),
                "valor": est.valor, "error": est.error_estandar}
    if tipo == "muestra":
        datos = generar_muestra(clave, params, n, seed)
        if datos.ndim != 1:
            raise ParametroInvalidoError("Selecciona un modelo univariante para esta vista.")
        estadisticos = resumir(datos)
        tabla = pd.DataFrame({"Índice": np.arange(1, n+1), "Observación": datos, "Semilla": [seed]*n})
        return {"tabla": tabla, "resumen": f"{n} observaciones de {obtener(clave).nombre} con semilla {seed}. Media empírica {estadisticos.media:.5g}.",
                "grafico": ("histograma", datos), "valor": estadisticos.media, "error": estadisticos.desviacion}
    x = numeros(texto, minimo=5 if tipo == "ajuste" else 2)
    if tipo == "ajuste":
        fit = ajustar_distribucion(x, clave, seed)
        xs, ys = curva_ajustada(fit, x)
        tabla = pd.DataFrame({"Parámetro": [*fit.parametros, "AIC", "Estadístico KS", "p KS exploratoria"],
                              "Estimación": [*fit.parametros.values(), fit.aic, fit.ks, fit.p_ks]})
        resumen = f"Ajuste {clave}: AIC={fit.aic:.5g}, KS={fit.ks:.5g}. La p de KS ({fit.p_ks:.4g}) NO está corregida por estimar parámetros; es exploratoria."
        return {"tabla": tabla, "resumen": resumen, "grafico": ("ajuste", x, xs, ys), "valor": fit.aic, "error": fit.ks}
    if tipo == "qq":
        teorico, observado = qq_plot(x, clave, params)
        descriptivos = resumir(observado)
        return {"tabla": pd.DataFrame({"Cuantil teórico": teorico, "Dato ordenado": observado}),
                "resumen": f"QQ-plot de {len(x)} datos frente a {obtener(clave).nombre}; una recta aproximada sugiere concordancia visual, no un contraste formal.",
                "grafico": ("qq", teorico, observado), "valor": descriptivos.mediana, "error": descriptivos.desviacion}
    raise ParametroInvalidoError("Simulación no registrada.")

