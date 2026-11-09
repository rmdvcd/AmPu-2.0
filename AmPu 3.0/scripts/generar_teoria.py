"""Regenera lecciones Markdown y diagramas PNG, siempre dentro de AmPu 3.0.

Ejecutar desde la carpeta AmPu 3.0: python scripts/generar_teoria.py
Las fórmulas son material editorial propio; no se copia el HTML heredado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from ampu.core.distribuciones import DISTRIBUCIONES as REGISTRO  # noqa: E402
from ampu.core.distribuciones.tabla import analizar  # noqa: E402

TEORIA = RAIZ / "src" / "ampu" / "docs" / "teoria"
IMAGENES = RAIZ / "src" / "ampu" / "docs" / "imagenes"

# Definición, PMF/PDF, CDF, E(X), Var(X), propiedades/casos especiales, evento.
DISTRIBUCIONES = {
 "bernoulli": (
  "Un único ensayo binario: $X=1$ si hay éxito y $X=0$ si hay fracaso.",
  r"P(X=x)=\begin{cases}p^x(1-p)^{1-x},&x\in\{0,1\}\\0,&\mathrm{en\ otro\ caso}\end{cases}",
  r"F(x)=\begin{cases}0,&x<0\\1-p,&0\le x<1\\1,&x\ge1\end{cases}",
  r"\operatorname{E}[X]=p", r"\operatorname{Var}(X)=p(1-p)",
  "Los límites $p=0$ y $p=1$ son casos degenerados. Es la binomial con $n=1$.", 1),
 "binomial": (
  "Cuenta éxitos en $n$ ensayos de Bernoulli independientes con probabilidad común $p$.",
  r"P(X=x)=\begin{cases}\binom{n}{x}p^x(1-p)^{n-x},&x\in\{0,\ldots,n\}\\0,&\mathrm{en\ otro\ caso}\end{cases}",
  r"F(x)=\sum_{k=0}^{\lfloor x\rfloor}\binom{n}{k}p^k(1-p)^{n-k}",
  r"\operatorname{E}[X]=np", r"\operatorname{Var}(X)=np(1-p)",
  "$p=0$ o $p=1$ dan resultados deterministas. Para $n$ grande y $np,n(1-p)$ suficientes se usa la aproximación normal.", 5),
 "binomial_negativa": (
  "Cuenta el número de **fracasos** antes de alcanzar el éxito número $r$.",
  r"P(X=x)=\binom{r+x-1}{x}p^r(1-p)^x,\quad x=0,1,\ldots",
  r"F(x)=\sum_{k=0}^{\lfloor x\rfloor}\binom{r+k-1}{k}p^r(1-p)^k",
  r"\operatorname{E}[X]=\frac{r(1-p)}{p}", r"\operatorname{Var}(X)=\frac{r(1-p)}{p^2}",
  "Con $r=1$ se convierte en geométrica de fracasos (que difiere en 1 de la geométrica de intentos). $p=1$ produce siempre 0 fracasos.", 3),
 "multinomial": (
  "Generaliza la binomial a $k$ categorías, con vector de conteos $\\boldsymbol X$ y $\\sum_i X_i=n$.",
  r"P(\boldsymbol X=\boldsymbol x)=\begin{cases}\dfrac{n!}{\prod_{i=1}^{k}x_i!}\prod_{i=1}^{k}p_i^{x_i},&\sum_i x_i=n\\0,&\mathrm{en\ otro\ caso}\end{cases}",
  r"F_i(t)=P(X_i\le t)=\sum_{j=0}^{\lfloor t\rfloor}\binom nj p_i^j(1-p_i)^{n-j}",
  r"\operatorname{E}[X_i]=np_i", r"\operatorname{Var}(X_i)=np_i(1-p_i)",
  "La CDF y PPF que muestra AmPu son **marginales** por categoría, no conjuntas. $\\operatorname{Cov}(X_i,X_j)=-np_ip_j$ para $i\\ne j$. Se exige $\\sum p_i=1$.", [2, 2, 4]),
 "geometrica": (
  "Cuenta los **intentos hasta** el primer éxito independiente con probabilidad $p$.",
  r"P(X=x)=p(1-p)^{x-1},\quad x=1,2,\ldots",
  r"F(x)=\begin{cases}0,&x<1\\1-(1-p)^{\lfloor x\rfloor},&x\ge1\end{cases}",
  r"\operatorname{E}[X]=\frac1p", r"\operatorname{Var}(X)=\frac{1-p}{p^2}",
  "Es la única distribución discreta sin memoria: $P(X>s+t\\mid X>s)=P(X>t)$. Para $p=1$, $X=1$.", 5),
 "hipergeometrica": (
  "Cuenta éxitos en $n$ extracciones **sin reemplazo** de una población de $N$ con $K$ éxitos.",
  r"P(X=x)=\frac{\binom Kx\binom{N-K}{n-x}}{\binom Nn}",
  r"F(x)=\sum_{j=\max(0,n-N+K)}^{\lfloor x\rfloor}\frac{\binom Kj\binom{N-K}{n-j}}{\binom Nn}",
  r"\operatorname{E}[X]=n\frac KN", r"\operatorname{Var}(X)=n\frac KN\left(1-\frac KN\right)\frac{N-n}{N-1}",
  "Soporte: $\\max(0,n-N+K)\\le x\\le\\min(n,K)$. La corrección $\\frac{N-n}{N-1}$ cuantifica la falta de reemplazo; con $N=1$ la varianza es 0.", 3),
 "poisson": (
  "Número de sucesos en un intervalo, con tasa media $\\lambda$ y ocurrencias independientes.",
  r"P(X=x)=e^{-\lambda}\frac{\lambda^x}{x!},\quad x=0,1,\ldots",
  r"F(x)=e^{-\lambda}\sum_{k=0}^{\lfloor x\rfloor}\frac{\lambda^k}{k!}",
  r"\operatorname{E}[X]=\lambda", r"\operatorname{Var}(X)=\lambda",
  "Si $\\lambda=0$, toda la masa está en 0. Aproxima una binomial cuando $n$ es grande, $p$ pequeño y $np=\\lambda$.", 5),
 "uniforme_discreta": (
  "Cada entero entre $a$ y $b$, ambos incluidos, tiene idéntica probabilidad.",
  r"P(X=x)=\begin{cases}\dfrac{1}{b-a+1},&x\in\{a,\ldots,b\}\\0,&\mathrm{en\ otro\ caso}\end{cases}",
  r"F(x)=\begin{cases}0,&x<a\\\dfrac{\lfloor x\rfloor-a+1}{b-a+1},&a\le x<b\\1,&x\ge b\end{cases}",
  r"\operatorname{E}[X]=\frac{a+b}{2}", r"\operatorname{Var}(X)=\frac{(b-a+1)^2-1}{12}",
  "Cuando $a=b$ es una masa puntual. Para $a=1$ y $b=6$ representa un dado ideal.", 3),
 "uniforme": (
  "Una variable continua con densidad constante en el intervalo $[a,b]$.",
  r"f(x)=\begin{cases}\dfrac1{b-a},&a\le x\le b\\0,&\mathrm{en\ otro\ caso}\end{cases}",
  r"F(x)=\begin{cases}0,&x<a\\\dfrac{x-a}{b-a},&a\le x\le b\\1,&x>b\end{cases}",
  r"\operatorname{E}[X]=\frac{a+b}{2}", r"\operatorname{Var}(X)=\frac{(b-a)^2}{12}",
  "La probabilidad de un punto aislado es cero; se calcula el área entre extremos. Sustituye el error original $a+b$ por $b-a$ en la desviación.", 3),
 "normal_estandar": (
  "Distribución normal de media 0 y varianza 1, conocida como campana de Gauss.",
  r"\varphi(z)=\frac{1}{\sqrt{2\pi}}e^{-z^2/2},\quad z\in\mathbb R",
  r"\Phi(z)=\int_{-\infty}^{z}\varphi(t)\,\mathrm{d}t",
  r"\operatorname{E}[Z]=0", r"\operatorname{Var}(Z)=1",
  "Es simétrica: $\\Phi(-z)=1-\\Phi(z)$. Si $X\\sim N(\\mu,\\sigma^2)$, entonces $(X-\\mu)/\\sigma\\sim N(0,1)$.", 2),
 "normal": (
  "Familia de densidades simétricas de media $\\mu$ y desviación $\\sigma$.",
  r"f(x)=\frac{1}{\sigma\sqrt{2\pi}}\exp\left[-\frac{(x-\mu)^2}{2\sigma^2}\right]",
  r"F(x)=\Phi\left(\frac{x-\mu}{\sigma}\right)",
  r"\operatorname{E}[X]=\mu", r"\operatorname{Var}(X)=\sigma^2",
  "La normal estándar es el caso $\\mu=0,\\sigma=1$. Las probabilidades en intervalos se restan entre dos CDF.", 1),
 "chi_cuadrado": (
  "Suma de cuadrados de $\\nu$ normales estándar independientes.",
  r"f(x)=\frac{x^{\nu/2-1}e^{-x/2}}{2^{\nu/2}\Gamma(\nu/2)},\quad x>0",
  r"F(x)=\frac{\gamma(\nu/2,x/2)}{\Gamma(\nu/2)}",
  r"\operatorname{E}[X]=\nu", r"\operatorname{Var}(X)=2\nu",
  "Es una gamma con forma $\\nu/2$ y escala 2. Para $\\nu=1$, la densidad diverge en cero pero la integral es finita.", 2),
 "exponencial": (
  "Tiempo de espera positivo hasta un suceso de proceso de Poisson con tasa $\\lambda$.",
  r"f(x)=\begin{cases}\lambda e^{-\lambda x},&x\ge0\\0,&x<0\end{cases}",
  r"F(x)=\begin{cases}1-e^{-\lambda x},&x\ge0\\0,&x<0\end{cases}",
  r"\operatorname{E}[X]=\frac1\lambda", r"\operatorname{Var}(X)=\frac1{\lambda^2}",
  "Sin memoria: $P(X>s+t\\mid X>s)=P(X>t)$. Su cola estable es $S(x)=e^{-\\lambda x}$ para $x\\ge0$.", 4),
 "t_student": (
  "Cociente de una normal estándar y la raíz de una chi-cuadrado independiente dividida por $\\nu$.",
  r"f(x)=\frac{\Gamma((\nu+1)/2)}{\sqrt{\nu\pi}\,\Gamma(\nu/2)}\left(1+\frac{x^2}{\nu}\right)^{-(\nu+1)/2}",
  r"F(x)=\int_{-\infty}^{x}f(t)\,\mathrm{d}t",
  r"\operatorname{E}[X]=0\ (\nu>1)", r"\operatorname{Var}(X)=\frac\nu{\nu-2}\ (\nu>2)",
  "Para $\\nu=1$ es Cauchy, sin media ni varianza; para $1<\\nu\\le2$ no hay varianza. Al crecer $\\nu$ tiende a la normal.", 1),
 "f_fisher": (
  "Cociente de dos chi-cuadrados independientes normalizados por sus grados de libertad $d_1,d_2$.",
  r"f(x)=\frac{(d_1/d_2)^{d_1/2}x^{d_1/2-1}}{B(d_1/2,d_2/2)(1+d_1x/d_2)^{(d_1+d_2)/2}},\quad x>0",
  r"F(x)=I_{d_1x/(d_1x+d_2)}(d_1/2,d_2/2)",
  r"\operatorname{E}[X]=\frac{d_2}{d_2-2}\ (d_2>2)",
  r"\operatorname{Var}(X)=\frac{2d_2^2(d_1+d_2-2)}{d_1(d_2-2)^2(d_2-4)}\ (d_2>4)",
  "La cola derecha es habitual en ANOVA. En SciPy los grados de libertad son parámetros, no constantes hardcodeadas.", 1),
 "gamma": (
  "Tiempo de espera general positivo de forma $k$ y escala $\\theta$.",
  r"f(x)=\frac{x^{k-1}e^{-x/\theta}}{\Gamma(k)\theta^k},\quad x>0",
  r"F(x)=\frac{\gamma(k,x/\theta)}{\Gamma(k)}",
  r"\operatorname{E}[X]=k\theta", r"\operatorname{Var}(X)=k\theta^2",
  "Para $k=1$ es exponencial con tasa $1/\\theta$; para $k=\\nu/2,\\theta=2$ es chi-cuadrado.", 3),
 "erlang": (
  "Suma de $k$ esperas exponenciales independientes con la misma tasa $\\lambda$; $k$ entero.",
  r"f(x)=\frac{\lambda^k x^{k-1}e^{-\lambda x}}{(k-1)!},\quad x\ge0",
  r"F(x)=1-e^{-\lambda x}\sum_{j=0}^{k-1}\frac{(\lambda x)^j}{j!}",
  r"\operatorname{E}[X]=\frac{k}{\lambda}", r"\operatorname{Var}(X)=\frac{k}{\lambda^2}",
  "Es gamma con forma entera $k$; $k=1$ produce una exponencial.", 3),
 "beta": (
  "Familia flexible de probabilidades/proporciones en el intervalo unitario.",
  r"f(x)=\frac{x^{\alpha-1}(1-x)^{\beta-1}}{B(\alpha,\beta)},\quad 0<x<1",
  r"F(x)=I_x(\alpha,\beta)",
  r"\operatorname{E}[X]=\frac{\alpha}{\alpha+\beta}",
  r"\operatorname{Var}(X)=\frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)}",
  "$\\alpha=\\beta=1$ recupera la uniforme $(0,1)$. Conjugada de Bernoulli/binomial en inferencia bayesiana.", .3),
 "lognormal": (
  "Variable positiva cuyo logaritmo natural es normal con media $\\mu$ y desviación $\\sigma$.",
  r"f(x)=\frac{1}{x\sigma\sqrt{2\pi}}\exp\left[-\frac{(\ln x-\mu)^2}{2\sigma^2}\right],\quad x>0",
  r"F(x)=\Phi\left(\frac{\ln x-\mu}{\sigma}\right),\quad x>0",
  r"\operatorname{E}[X]=e^{\mu+\sigma^2/2}",
  r"\operatorname{Var}(X)=(e^{\sigma^2}-1)e^{2\mu+\sigma^2}",
  "La mediana es $e^\\mu$, no coincide con la media. Para $x\\le0$ la CDF es cero.", 1),
 "weibull": (
  "Modelo de duración no negativa con forma $k$ y escala $\\lambda$.",
  r"f(x)=\frac{k}{\lambda}\left(\frac{x}{\lambda}\right)^{k-1}e^{-(x/\lambda)^k},\quad x\ge0",
  r"F(x)=1-e^{-(x/\lambda)^k},\quad x\ge0",
  r"\operatorname{E}[X]=\lambda\Gamma(1+1/k)",
  r"\operatorname{Var}(X)=\lambda^2\left[\Gamma(1+2/k)-\Gamma(1+1/k)^2\right]",
  "$k=1$ equivale a exponencial. Riesgo decreciente para $k<1$ y creciente para $k>1$.", 2),
 "cauchy": (
  "Distribución de colas muy pesadas, centrada en $x_0$ y de escala $\\gamma$.",
  r"f(x)=\frac{1}{\pi\gamma[1+((x-x_0)/\gamma)^2]}",
  r"F(x)=\frac12+\frac1\pi\arctan\left(\frac{x-x_0}{\gamma}\right)",
  r"\operatorname{E}[X]=\text{indefinida}", r"\operatorname{Var}(X)=\text{indefinida}",
  "Ni la media ni la desviación están definidas; SciPy devuelve NaN. Su mediana es $x_0$. Es t de Student con un grado de libertad.", 1),
 "logistica": (
  "Distribución simétrica con ubicación $\\mu$ y escala $s$, de colas más pesadas que la normal.",
  r"f(x)=\frac{e^{-(x-\mu)/s}}{s[1+e^{-(x-\mu)/s}]^2}",
  r"F(x)=\frac{1}{1+e^{-(x-\mu)/s}}",
  r"\operatorname{E}[X]=\mu", r"\operatorname{Var}(X)=\frac{\pi^2s^2}{3}",
  "El logit de una probabilidad uniforme tiene distribución logística estándar. CDF y función logística coinciden.", 1),
 "triangular": (
  "Distribución acotada definida por mínimo $a$, máximo $b$ y moda $c$ con $a\\le c\\le b$.",
  r"f(x)=\begin{cases}\frac{2(x-a)}{(b-a)(c-a)},&a\le x<c\\\frac{2(b-x)}{(b-a)(b-c)},&c\le x\le b\\0,&\mathrm{en\ otro\ caso}\end{cases}",
  r"F(x)=\begin{cases}0,&x<a\\\frac{(x-a)^2}{(b-a)(c-a)},&a\le x<c\\1-\frac{(b-x)^2}{(b-a)(b-c)},&c\le x\le b\\1,&x>b\end{cases}",
  r"\operatorname{E}[X]=\frac{a+b+c}{3}",
  r"\operatorname{Var}(X)=\frac{a^2+b^2+c^2-ab-ac-bc}{18}",
  "Si $c=a$ o $c=b$, se interpreta la expresión por su límite; la moda está en un extremo.", 1),
 "pareto": (
  "Modelo de cola de potencia para valores superiores a un mínimo $x_m$.",
  r"f(x)=\frac{\alpha x_m^\alpha}{x^{\alpha+1}},\quad x\ge x_m",
  r"F(x)=\begin{cases}0,&x<x_m\\1-(x_m/x)^\alpha,&x\ge x_m\end{cases}",
  r"\operatorname{E}[X]=\frac{\alpha x_m}{\alpha-1}\ (\alpha>1)",
  r"\operatorname{Var}(X)=\frac{\alpha x_m^2}{(\alpha-1)^2(\alpha-2)}\ (\alpha>2)",
  "La media diverge si $\\alpha\\le1$ y la varianza si $\\alpha\\le2$. Multiplicar $x_m$ solo cambia la escala.", 2),
 "normal_bivariada": (
  "Par $(X,Y)$ normal con medias, desviaciones y correlación $\\rho$; $|\\rho|<1$.",
  r"f(x,y)=\frac{\exp\!\left[-\frac{z_x^2-2\rho z_xz_y+z_y^2}{2(1-\rho^2)}\right]}{2\pi\sigma_x\sigma_y\sqrt{1-\rho^2}},\quad z_i=\frac{x_i-\mu_i}{\sigma_i}",
  r"F(x,y)=\int_{-\infty}^{x}\int_{-\infty}^{y}f(u,v)\,\mathrm{d}v\,\mathrm{d}u",
  r"\operatorname{E}[\boldsymbol X]=(\mu_x,\mu_y)",
  r"\operatorname{Var}(X)=\sigma_x^2,\quad\operatorname{Var}(Y)=\sigma_y^2",
  "La CDF es **conjunta**; los cuantiles PPF son marginales. $\\operatorname{Cov}(X,Y)=\\rho\\sigma_x\\sigma_y$.", [0, 0]),
 "dirichlet": (
  "Distribución de un vector de proporciones positivas que suman exactamente uno.",
  r"f(\boldsymbol x)=\frac{\Gamma(\alpha_0)}{\prod_i\Gamma(\alpha_i)}\prod_i x_i^{\alpha_i-1},\quad\alpha_0=\sum_i\alpha_i,\ \sum_i x_i=1",
  r"F_i(t)=I_t(\alpha_i,\alpha_0-\alpha_i)",
  r"\operatorname{E}[X_i]=\frac{\alpha_i}{\alpha_0}",
  r"\operatorname{Var}(X_i)=\frac{\alpha_i(\alpha_0-\alpha_i)}{\alpha_0^2(\alpha_0+1)}",
  "Sus marginales son beta; la CDF/PPF de AmPu son **marginales**, no conjuntas. Para dos componentes equivale a una beta.", [.2, .3, .5]),
}

# Técnica: título, definición, parámetros, estadístico/densidad, CDF bajo H0,
# momentos/escala, propiedades/casos especiales, ejemplo paso a paso, figura.
TECNICAS = {
 "muestreo_finito": (
  "Aleatorio simple · población finita", "Cada subconjunto de $n$ unidades distintas entre $N$ tiene igual probabilidad; se selecciona sin reemplazo.",
  [("N", "Entero positivo; tamaño de población"), ("n", "Entero entre 1 y N; tamaño de muestra"), ("p, d", "Proporción esperada y margen absoluto positivo")],
  r"n=\left\lceil\frac{Nn_0}{N-1+n_0}\right\rceil,\quad n_0=\frac{z_{1-\alpha/2}^2p(1-p)}{d^2}",
  r"P(I_i\le t)=\begin{cases}0,&t<0\\1-n/N,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_i]=\pi_i=\frac nN,\quad\operatorname{Var}(I_i)=\pi_i(1-\pi_i),\quad\sigma_i=\sqrt{\pi_i(1-\pi_i)}",
  "El tamaño de diseño no supera $N$ y se redondea **hacia arriba**. La corrección finita supone unidades igualmente probables.",
  "1. Para $N=1000$, $p=0,5$, confianza 95 % y $d=0,05$, calcule $z=1,960$.\n2. Obtenga $n_0=1,960^2(0,5)(0,5)/0,05^2=384,16$.\n3. Corrija: $n=\\lceil1000(384,16)/(999+384,16)\\rceil=278$. Seleccione 278 identificadores distintos con semilla.", "muestreo"),
 "muestreo_infinito": (
  "Aleatorio simple · población grande", "Dimensiona un diseño de proporciones sin corrección finita; si se muestrea con reemplazo, cada sorteo es independiente.",
  [("p", "Proporción supuesta (0,1)"), ("d", "Error absoluto tolerado >0"), ("1−α", "Confianza estrictamente entre 0 y 1")],
  r"n_0=\left\lceil\frac{z_{1-\alpha/2}^{2}p(1-p)}{d^2}\right\rceil",
  r"P(I_i\le t)=\begin{cases}0,&t<0\\1-p_i,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_i]=p_i,\quad\operatorname{Var}(I_i)=p_i(1-p_i),\quad\sigma_i=\sqrt{p_i(1-p_i)}",
  "Si $p$ es desconocida, usar $p=0,5$ es conservador. Independencia real requiere reemplazo o población suficientemente grande.",
  "1. Fije confianza 95 %, $p=0,5$ y error $d=0,05$.\n2. Calcule $n_0=1,960^2(0,25)/0,0025=384,16$.\n3. Redondee hacia arriba: 385 observaciones. Con reemplazo, una misma unidad puede repetirse.", "muestreo"),
 "muestreo_estratificado": (
  "Muestreo estratificado proporcional", "Divide la población en estratos disjuntos; toma una muestra aleatoria sin reemplazo en cada uno.",
  [("N_h", "Tamaño entero de cada estrato"), ("N", "Suma de N_h"), ("n", "Tamaño de muestra total")],
  r"n_h\approx n\frac{N_h}{N},\qquad\sum_h n_h=n",
  r"P(I_{hi}\le t)=\begin{cases}0,&t<0\\1-n_h/N_h,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_{hi}]=n_h/N_h,\quad\operatorname{Var}(I_{hi})=(n_h/N_h)(1-n_h/N_h)",
  "Se usan mayores restos para obtener enteros de suma exactamente $n$. Cada $n_h$ está acotado por $N_h$; se reproducen sorteos con una sola semilla.",
  "1. Dos estratos tienen $N_1=100$, $N_2=200$ y $n=30$.\n2. Los tamaños proporcionales son $n_1=30(100/300)=10$, $n_2=20$.\n3. Sortea 10 unidades del primero y 20 del segundo, sin reemplazo.", "muestreo"),
 "muestreo_sistematico": (
  "Muestreo sistemático", "Tras un inicio aleatorio sobre una lista ordenada, elige elementos a intervalos aproximadamente constantes.",
  [("N", "Tamaño de la lista"), ("n", "Unidades deseadas (1 ≤ n ≤ N)"), ("r", "Inicio uniforme en [0, N/n)")],
  r"k=N/n,\qquad j_i=\lfloor r+ik\rfloor,\quad i=0,\ldots,n-1",
  r"P(I_i\le t)=\begin{cases}0,&t<0\\1-n/N,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_i]=n/N,\quad\operatorname{Var}(I_i)=(n/N)(1-n/N)",
  "Una periodicidad de la lista correlacionada con $k$ puede sesgar la muestra; se debe aleatorizar la lista si procede.",
  "1. Si $N=40$ y $n=10$, el paso es $k=4$.\n2. Con inicio $r=2$, los índices (desde cero) son 2, 6, 10, …, 38.\n3. Extraiga esas 10 unidades, en orden y sin duplicados.", "muestreo"),
 "muestreo_conglomerados": (
  "Muestreo por conglomerados", "Sortea grupos completos en una etapa, o sorteos adicionales dentro de grupos elegidos en dos etapas.",
  [("G", "Cantidad de conglomerados"), ("g", "Conglomerados elegidos, g ≤ G"), ("m", "Unidades por grupo en segunda etapa, opcional")],
  r"P(C_j\ \mathrm{seleccionado})=\frac{g}{G}",
  r"P(I_j\le t)=\begin{cases}0,&t<0\\1-g/G,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_j]=g/G,\quad\operatorname{Var}(I_j)=(g/G)(1-g/G)",
  "Elegir grupos suele ser barato, pero su homogeneidad interna aumenta el error respecto a MAS. En dos etapas: $\\pi_{ij}=(g/G)(m_j/N_j)$.",
  "1. Enumere $G=5$ escuelas y sortee $g=2$ sin reemplazo.\n2. La probabilidad de inclusión de cada escuela es $2/5=0,4$.\n3. Incluya a todos los alumnos seleccionados, o sortee $m$ en cada escuela.", "muestreo"),
 "muestreo_neyman": (
  "Asignación de Neyman", "Distribuye tamaño estratificado según el tamaño y la variabilidad de cada estrato, a costes iguales.",
  [("N_h", "Unidades en el estrato"), ("S_h", "Desviación esperada (≥0)"), ("n", "Tamaño total")],
  r"n_h\approx n\frac{N_hS_h}{\sum_j N_jS_j}",
  r"P(I_{hi}\le t)=\begin{cases}0,&t<0\\1-n_h/N_h,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_{hi}]=n_h/N_h,\quad\operatorname{Var}(I_{hi})=(n_h/N_h)(1-n_h/N_h)",
  "Se redondea preservando la suma y la capacidad. Si todas las $S_h=0$, no hay asignación informativa por dispersión.",
  "1. Tome $(N_1,S_1)=(100,8)$, $(N_2,S_2)=(200,4)$, $n=40$.\n2. Los pesos de Neyman son 800 y 800.\n3. Asigne $n_1=n_2=20$, en vez de los tamaños proporcionales 13 y 27.", "muestreo"),
 "muestreo_optimo": (
  "Asignación óptima con costes", "Extiende Neyman penalizando estratos cuyo coste por observación es mayor.",
  [("N_h", "Tamaño de estrato"), ("S_h", "Desviación esperada"), ("c_h", "Coste positivo por unidad")],
  r"n_h\approx n\frac{N_hS_h/\sqrt{c_h}}{\sum_j N_jS_j/\sqrt{c_j}}",
  r"P(I_{hi}\le t)=\begin{cases}0,&t<0\\1-n_h/N_h,&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_{hi}]=n_h/N_h,\quad\operatorname{Var}(I_{hi})=(n_h/N_h)(1-n_h/N_h)",
  "La fórmula es una asignación con n fijado. La optimización bajo presupuesto fijo es distinta; registrar costes si existen.",
  "1. Use $(N_1,S_1,c_1)=(100,8,1)$ y $(N_2,S_2,c_2)=(200,4,4)$.\n2. Los pesos son 800 y 400.\n3. Para $n=60$, los tamaños son 40 y 20; seleccione sin reemplazo en cada estrato.", "muestreo"),
 "tamano_media": (
  "Tamaño muestral para estimar medias", "Con desviación poblacional estimada $\\sigma$, determina observaciones necesarias para un margen $d$.",
  [("σ", "Desviación esperada >0"), ("d", "Margen absoluto >0"), ("N", "Población finita, opcional")],
  r"n_0=\left\lceil\left(\frac{z_{1-\alpha/2}\sigma}{d}\right)^2\right\rceil,\quad n_F=\left\lceil\frac{Nn_0}{N-1+n_0}\right\rceil",
  r"P(\bar X\le t)\approx\Phi\left(\frac{t-\mu}{\sigma/\sqrt{n}}\right)",
  r"\operatorname{E}[\bar X]=\mu,\quad\operatorname{Var}(\bar X)=\sigma^2/n,\quad\sigma_{\bar X}=\sigma/\sqrt n",
  "Es una aproximación normal; para poblaciones finitas se aplica factor de corrección y tamaño ≤N.",
  "1. Suponga $\\sigma=12$, $d=2$ y confianza 95 %.\n2. Calcule $n_0=\\lceil(1,960·12/2)^2\\rceil=139$.\n3. Si $N=500$, aplique corrección finita antes de extraer unidades.", "muestreo"),
 "tamano_proporcion": (
  "Tamaño muestral para proporciones", "Planifica precisión de proporciones; el caso conservador si $p$ no se conoce es $p=0,5$.",
  [("p", "Proporción de diseño en (0,1)"), ("d", "Error absoluto"), ("N", "Tamaño finito opcional")],
  r"n_0=\left\lceil\frac{z_{1-\alpha/2}^2p(1-p)}{d^2}\right\rceil",
  r"P(\hat p\le t)\approx\Phi\left(\frac{t-p}{\sqrt{p(1-p)/n}}\right)",
  r"\operatorname{E}[\hat p]=p,\quad\operatorname{Var}(\hat p)=\frac{p(1-p)}n",
  "Para $p=0$ o $1$ esta aproximación de diseño no informa sobre dispersión; se recomienda un estudio piloto.",
  "1. Defina $p=0,5$, confianza 95 % y $d=0,05$.\n2. Sustituya $n_0=1,960²(0,25)/(0,05²)=384,16$.\n3. Requiera al menos 385 elementos; menos si la población finita es pequeña.", "muestreo"),
 "tamano_diferencia": (
  "Tamaños para diferencias de medias y proporciones", "Estima el tamaño **por grupo** de dos muestras independientes de igual tamaño.",
  [("σ₁, σ₂", "Desviaciones poblacionales positivas"), ("p₁, p₂", "Proporciones de diseño en (0,1)"), ("d", "Margen absoluto")],
  r"n_{\bar X_1-\bar X_2}=\left\lceil\frac{z^2(\sigma_1^2+\sigma_2^2)}{d^2}\right\rceil,\quad n_{\hat p_1-\hat p_2}=\left\lceil\frac{z^2[p_1(1-p_1)+p_2(1-p_2)]}{d^2}\right\rceil",
  r"P(D\le t)\approx\Phi\left(\frac{t-\operatorname{E}[D]}{\sqrt{\operatorname{Var}(D)}}\right)",
  r"\operatorname{Var}(\bar X_1-\bar X_2)=\frac{\sigma_1^2+\sigma_2^2}{n},\quad\sigma_D=\sqrt{\operatorname{Var}(D)}",
  "Los tamaños son por brazo y suponen independencia; no incorporan potencia de prueba de hipótesis.",
  "1. Con $\\sigma_1=3$, $\\sigma_2=4$, $d=2$ y confianza 95 %, use $z=1,960$.\n2. Calcule $n=\\lceil1,960²(9+16)/4\\rceil=25$.\n3. Seleccione 25 unidades **en cada grupo**; total 50.", "muestreo"),
 "intervalos_confianza": (
  "Intervalos de confianza y error", "Un intervalo cuantifica variabilidad de un estimador, no la probabilidad posterior del parámetro fijo.",
  [("1−α", "Cobertura nominal en (0,1)"), ("s", "Desviación muestral"), ("n", "Observaciones; n ≥2")],
  r"IC_{1-\alpha}(\mu)=\bar x\pm t_{1-\alpha/2,n-1}\frac{s}{\sqrt n}",
  r"P\!\left(\bar X\le t\mid \mu,\sigma\right)\approx\Phi\left(\frac{t-\mu}{\sigma/\sqrt n}\right)",
  r"\operatorname{E}[\bar X]=\mu,\quad\operatorname{Var}(\bar X)=\sigma^2/n,\quad\sigma_{\bar X}=\sigma/\sqrt n",
  "Para proporciones se usa Wilson, estable incluso con 0 o n éxitos. Error relativo = $|\\hat\\theta-\\theta|/|\\theta|$, indefinido si $\\theta=0$.",
  "1. Muestra de $n=16$, media 20, $s=4$ y confianza 95 %.\n2. Con 15 grados de libertad, $t_{0,975}=2,131$.\n3. IC: $20\\pm2,131(4/4)=[17,87;22,13]$.", "inferencia"),
 "prueba_z_una": (
  "Prueba z · una media", "Contrasta $H_0:\\mu=\\mu_0$ si se conoce la desviación poblacional $\\sigma$.",
  [("μ₀", "Media bajo H₀"), ("σ", "Desviación poblacional >0"), ("α", "Nivel de significación en (0,1)")],
  r"Z=\frac{\bar X-\mu_0}{\sigma/\sqrt n}\overset{H_0}{\sim}N(0,1)",
  r"F_Z(z)=\Phi(z)=\int_{-\infty}^{z}\frac{e^{-u^2/2}}{\sqrt{2\pi}}\,\mathrm{d}u",
  r"\operatorname{E}_{H_0}[Z]=0,\quad\operatorname{Var}_{H_0}(Z)=1,\quad\sigma_Z=1",
  "Ofrece alternativas bilateral y unilaterales; p menor que α permite rechazar H₀, no prueba causalidad.",
  "1. Sea $n=25$, $\\bar x=52$, $\\mu_0=50$ y $\\sigma=5$.\n2. $z=(52-50)/(5/5)=2$.\n3. p bilateral $=2[1-\\Phi(2)]\\approx0,0455$; a 5 %, rechace H₀.", "inferencia"),
 "prueba_z_dos": (
  "Prueba z · dos medias", "Compara dos medias independientes cuando ambas desviaciones poblacionales son conocidas.",
  [("σ₁, σ₂", "Desviaciones poblacionales >0"), ("n₁, n₂", "Tamaños muestrales independientes"), ("α", "Significación")],
  r"Z=\frac{\bar X_1-\bar X_2}{\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}}",
  r"F_Z(z)=\Phi(z)\quad\text{bajo }H_0:\mu_1=\mu_2",
  r"\operatorname{E}_{H_0}[Z]=0,\quad\operatorname{Var}_{H_0}(Z)=1,\quad\sigma_Z=1",
  "El IC de la diferencia usa el mismo error estándar pero no presupone igualdad de medias.",
  "1. $\\bar x_1=12$, $\\bar x_2=10$, $\\sigma_1=\\sigma_2=3$, $n_1=n_2=18$.\n2. $SE=\\sqrt{9/18+9/18}=1$ y $z=2$.\n3. p bilateral $\\approx0,0455$; rechace H₀ al 5 %.", "inferencia"),
 "prueba_t_una": (
  "Prueba t · una media", "Contrasta una media sin conocer la desviación poblacional, con varianza muestral $s^2$.",
  [("μ₀", "Media hipotética"), ("n", "Muestra independiente de tamaño ≥2"), ("s", "Desviación muestral positiva")],
  r"T=\frac{\bar X-\mu_0}{s/\sqrt n}\overset{H_0}{\sim}t_{n-1}",
  r"F_T(t)=\int_{-\infty}^{t}\frac{\Gamma(n/2)}{\sqrt{(n-1)\pi}\,\Gamma((n-1)/2)}\left(1+\frac{u^2}{n-1}\right)^{-n/2}\mathrm{d}u",
  r"\operatorname{E}[T]=0\ (n>2),\quad\operatorname{Var}(T)=\frac{n-1}{n-3}\ (n>3)",
  "Con muestras pequeñas conviene explorar normalidad; varianza cero no permite prueba t.",
  "1. Para $n=10$, $\\bar x=5,8$, $s=1$, $\\mu_0=5$: $t=0,8/(1/\\sqrt{10})=2,530$.\n2. Use 9 grados de libertad y cola bilateral $p\\approx0,032$.\n3. Como $p<0,05$, rechace H₀ sin afirmar causalidad.", "inferencia"),
 "prueba_t_dos": (
  "Prueba t de Welch · dos medias", "Compara medias independientes sin asumir varianzas iguales.",
  [("s₁, s₂", "Desviaciones muestrales"), ("n₁, n₂", "Tamaños de grupo ≥2"), ("α", "Significación")],
  r"T=\frac{\bar X_1-\bar X_2}{\sqrt{s_1^2/n_1+s_2^2/n_2}},\quad\nu=\frac{(s_1^2/n_1+s_2^2/n_2)^2}{(s_1^2/n_1)^2/(n_1-1)+(s_2^2/n_2)^2/(n_2-1)}",
  r"F_T(t)\approx F_{t_\nu}(t)",
  r"\operatorname{E}_{H_0}[T]\approx0,\quad\operatorname{Var}(T)\approx\frac\nu{\nu-2}\ (\nu>2)",
  "Welch es preferible a imponer varianzas iguales sin justificación. El IC se basa en grados de libertad de Satterthwaite.",
  "1. Con $\\bar x_1=10$, $\\bar x_2=8$, $s_1=2$, $s_2=3$ y $n_1=n_2=16$.\n2. $SE=\\sqrt{4/16+9/16}=0,901$, de modo que $t\\approx2,219$.\n3. Evalúe la cola t con $\\nu$ de Welch y compare la p con α.", "inferencia"),
 "prueba_proporcion_una": (
  "Prueba z · una proporción", "Contrasta $H_0:p=p_0$ usando error estándar bajo la hipótesis nula.",
  [("x", "Éxitos observados entre 0 y n"), ("n", "Ensayos positivos"), ("p₀", "Proporción nula en (0,1)")],
  r"Z=\frac{\hat p-p_0}{\sqrt{p_0(1-p_0)/n}},\quad\hat p=x/n",
  r"F_Z(z)\approx\Phi(z)\quad\text{si }np_0,n(1-p_0)\text{ son suficientes}",
  r"\operatorname{E}_{H_0}[Z]\approx0,\quad\operatorname{Var}_{H_0}(Z)\approx1",
  "Para pocos ensayos conviene una prueba binomial exacta; el intervalo descriptivo es de Wilson, incluso con 0 éxitos.",
  "1. Observe 50 éxitos de 100 con $p_0=0,3$.\n2. $z=(0,5-0,3)/\\sqrt{0,3(0,7)/100}\\approx4,364$.\n3. La p bilateral es muy pequeña; rechace H₀ al 5 %.", "inferencia"),
 "prueba_proporcion_dos": (
  "Prueba z · dos proporciones", "Contrasta la igualdad de dos proporciones independientes con tasa agrupada bajo H₀.",
  [("x₁,x₂", "Éxitos de cada grupo"), ("n₁,n₂", "Tamaños positivos"), ("α", "Significación")],
  r"Z=\frac{\hat p_1-\hat p_2}{\sqrt{\hat p(1-\hat p)(1/n_1+1/n_2)}},\quad\hat p=\frac{x_1+x_2}{n_1+n_2}",
  r"F_Z(z)\approx\Phi(z)\quad\text{bajo igualdad de proporciones}",
  r"\operatorname{E}_{H_0}[Z]\approx0,\quad\operatorname{Var}_{H_0}(Z)\approx1",
  "La diferencia IC usa error **no agrupado**. Si todos son éxitos o todos fracasos, la varianza nula impide esta aproximación.",
  "1. Compare 40/100 frente a 20/100: $\\hat p=0,3$.\n2. $SE_0=\\sqrt{0,3(0,7)(0,01+0,01)}=0,0648$.\n3. $z=(0,4-0,2)/0,0648\\approx3,09$; p bilateral $\\approx0,002$.", "inferencia"),
 "chi_bondad": (
  "Chi-cuadrado · bondad de ajuste", "Compara frecuencias observadas con frecuencias esperadas por un modelo categórico.",
  [("Oᵢ", "Frecuencia observada ≥0"), ("Eᵢ", "Frecuencia esperada positiva"), ("m", "Parámetros estimados de estos datos")],
  r"X^2=\sum_{i=1}^{k}\frac{(O_i-E_i)^2}{E_i},\quad\nu=k-1-m",
  r"F_{X^2}(x)=\frac{\gamma(\nu/2,x/2)}{\Gamma(\nu/2)}",
  r"\operatorname{E}[X^2]=\nu,\quad\operatorname{Var}(X^2)=2\nu,\quad\sigma=\sqrt{2\nu}",
  "Pocas frecuencias esperadas (<5) debilitan la aproximación asintótica. El p-valor es cola derecha.",
  "1. Tome observadas (12,15,23) y esperadas (15,15,20).\n2. $X^2=(12-15)^2/15+0+(23-20)^2/20=1,05$.\n3. Con $\\nu=2$, p $\\approx0,592$; no rechace H₀ al 5 %.", "inferencia"),
 "chi_independencia": (
  "Chi-cuadrado · independencia", "Contrasta independencia entre dos variables categóricas en tabla de contingencia.",
  [("Oᵢⱼ", "Frecuencias observadas en la tabla"), ("Eᵢⱼ", "Total fila × total columna / total"), ("r,c", "Número de filas y columnas")],
  r"X^2=\sum_{i=1}^{r}\sum_{j=1}^{c}\frac{(O_{ij}-E_{ij})^2}{E_{ij}},\quad\nu=(r-1)(c-1)",
  r"F_{X^2}(x)=\frac{\gamma(\nu/2,x/2)}{\Gamma(\nu/2)}",
  r"\operatorname{E}[X^2]=\nu,\quad\operatorname{Var}(X^2)=2\nu,\quad\sigma=\sqrt{2\nu}",
  "AmPu evita corrección de Yates automáticamente; cuando esperadas <5, interpretar con cautela o usar prueba exacta.",
  "1. Para la tabla ((18,12),(10,20)), los totales de fila son 30,30 y columna 28,32.\n2. Espere ((14,16),(14,16)) y sume $X^2\\approx4,286$.\n3. Con $\\nu=1$, p $\\approx0,0384$; rechace independencia a α=0,05.", "inferencia"),
 "anova": (
  "ANOVA de una vía", "Prueba igualdad de medias de 2 o más grupos independientes mediante la razón de variaciones.",
  [("k", "Número de grupos ≥2"), ("nᵢ", "Tamaños de grupo"), ("α", "Significación")],
  r"F=\frac{SS_{\mathrm{entre}}/(k-1)}{SS_{\mathrm{dentro}}/(N-k)}",
  r"F_F(x)=I_{(k-1)x/[(k-1)x+N-k]}\left(\frac{k-1}{2},\frac{N-k}{2}\right)",
  r"\operatorname{E}[F]=\frac{N-k}{N-k-2}\ (N-k>2),\quad\sigma_F=\sqrt{\operatorname{Var}(F)}",
  "Requiere independencia y varianzas similares; rechazar H₀ no identifica qué pares difieren.",
  "1. Compare tres grupos con medias 3, 6 y 10.\n2. Calcule sumas de cuadrados entre y dentro, y sus grados de libertad 2 y $N-3$.\n3. Divida medias cuadráticas, consulte cola F y compare p con α.", "inferencia"),
 "correlacion": (
  "Correlación de Pearson y Spearman", "Pearson mide asociación lineal; Spearman mide asociación monótona usando rangos.",
  [("xᵢ,yᵢ", "Observaciones pareadas, n≥3"), ("r", "Coeficiente de Pearson"), ("ρₛ", "Coeficiente de Spearman")],
  r"r=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum_i(x_i-\bar x)^2\sum_i(y_i-\bar y)^2}}",
  r"F_T(t)=F_{t_{n-2}}(t),\quad T=r\sqrt{\frac{n-2}{1-r^2}}\ (H_0:r=0)",
  r"\operatorname{E}[T]=0\ (n>3),\quad\operatorname{Var}(T)=\frac{n-2}{n-4}\ (n>4)",
  "La correlación no implica causalidad. Spearman usa permutación/rangos; su p se obtiene en SciPy según tamaño.",
  "1. Registre $x=(1,2,3)$ e $y=(2,4,6)$.\n2. Pearson $r=1$ y Spearman $\\rho_s=1$ por orden idéntico.\n3. Informe la magnitud y advierta que una muestra pequeña no establece causalidad.", "regresion"),
 "regresion": (
  "Regresión lineal simple y múltiple", "Estima la respuesta a partir de predictores usando mínimos cuadrados ordinarios.",
  [("y", "Variable respuesta numérica"), ("X", "Matriz de predictores de rango completo"), ("β", "Intercepto y coeficientes estimados")],
  r"\hat{\boldsymbol\beta}=(X^\top X)^{-1}X^\top\boldsymbol y,\quad\hat y_i=\hat\beta_0+\sum_j\hat\beta_j x_{ij}",
  r"F_{T_j}(t)=F_{t_{n-k-1}}(t),\quad T_j=\frac{\hat\beta_j}{\operatorname{SE}(\hat\beta_j)}",
  r"\operatorname{E}[\hat\beta_j]=\beta_j,\quad\operatorname{Var}(\hat{\boldsymbol\beta})=\sigma^2(X^\top X)^{-1}",
  "La implementación resuelve por SVD (estable numéricamente), no invierte X para ajustar. $R^2$ y p-valores no prueban causalidad.",
  "1. Para puntos $(1,3),(2,5),(3,7)$, estime pendiente 2 e intercepto 1.\n2. Prediga $\\hat y(4)=1+2(4)=9$.\n3. Compare residuos, $R^2$ e IC t si hay grados de libertad residuales.", "regresion"),
 "mann_whitney": (
  "Prueba de Mann–Whitney U", "Prueba no paramétrica para dos grupos independientes basada en rangos.",
  [("n₁,n₂", "Tamaños de los dos grupos"), ("R₁", "Suma de rangos del primero")],
  r"U_1=R_1-\frac{n_1(n_1+1)}2",
  r"F_U(u)=P(U_1\le u)\quad\text{según la distribución de rangos de SciPy}",
  r"\operatorname{E}[U_1]=\frac{n_1n_2}{2},\quad\operatorname{Var}(U_1)\approx\frac{n_1n_2(n_1+n_2+1)}{12}",
  "La interpretación como comparación de medianas presupone formas distribucionales similares; SciPy controla empates.",
  "1. Ordene conjuntamente muestras (1,2,3) y (4,5,6).\n2. Los rangos del primer grupo suman 6 y $U_1=6-3·4/2=0$.\n3. Compare el p-valor bilateral con α.", "inferencia"),
 "wilcoxon": (
  "Prueba de Wilcoxon pareada", "Contrasta si las diferencias de pares tienden a cero a partir de sus rangos absolutos.",
  [("dᵢ", "Diferencias de pares no idénticos"), ("W", "Suma de rangos con signo")],
  r"W_+=\sum_{i:d_i>0}\operatorname{rango}(|d_i|)",
  r"F_W(w)=P(W\le w)\quad\text{con distribución exacta/asintótica según SciPy}",
  r"\operatorname{E}[W_+]\approx\frac{n(n+1)}4,\quad\operatorname{Var}(W_+)\approx\frac{n(n+1)(2n+1)}{24}",
  "Pares con diferencia cero reciben manejo especial; los tamaños y empates afectan la aproximación.",
  "1. Compare antes (1,2,3,4) y después (2,4,4,7).\n2. Calcule diferencias, ordene magnitudes y sume rangos positivos/negativos.\n3. Use la p bilateral para evaluar si la ubicación cambió.", "inferencia"),
 "kruskal": (
  "Prueba de Kruskal–Wallis", "Alternativa no paramétrica a ANOVA para dos o más grupos independientes.",
  [("k", "Número de grupos ≥2"), ("R_h", "Suma de rangos por grupo"), ("N", "Total de observaciones")],
  r"H=\frac{12}{N(N+1)}\sum_{h=1}^k\frac{R_h^2}{n_h}-3(N+1)",
  r"F_H(h)\approx F_{\chi^2_{k-1}}(h)",
  r"\operatorname{E}[H]\approx k-1,\quad\operatorname{Var}(H)\approx2(k-1)",
  "SciPy ajusta empates; el rechazo global no dice cuáles grupos difieren. Si todos los valores son iguales, no hay contraste.",
  "1. Reúna tres grupos de al menos dos datos y ordene todas las observaciones.\n2. Calcule los rangos medios de empates, sus sumas $R_h$ y el estadístico $H$.\n3. Consulte cola chi-cuadrado con 2 grados de libertad.", "inferencia"),
 "descriptiva": (
  "Estadística descriptiva", "Resume un conjunto de observaciones con medidas robustas y gráficos exploratorios.",
  [("xᵢ", "Datos numéricos finitos"), ("n", "Tamaño n≥2"), ("s", "Desviación muestral")],
  r"\bar x=\frac1n\sum_i x_i,\quad s^2=\frac1{n-1}\sum_i(x_i-\bar x)^2",
  r"F_n(t)=\frac1n\sum_i\boldsymbol1(x_i\le t)",
  r"\operatorname{E}[\bar X]=\mu,\quad\operatorname{Var}(\bar X)=\sigma^2/n,\quad\sigma_{\bar X}=\sigma/\sqrt n",
  "CV=$s/|\\bar x|$ no se define con media cero. Cuartiles usan interpolación lineal; se reportan todas las modas empatadas.",
  "1. Datos (1,2,2,4,5), suma 14 y media 2,8.\n2. Mediana y moda = 2; la varianza muestral se divide por $n-1=4$.\n3. Constrúyase tabla de frecuencias y compare histograma con boxplot.", "analisis"),
 "combinatoria": (
  "Combinatoria exacta", "Cuenta arreglos y elecciones finitas sin errores de coma flotante.",
  [("n", "Elementos disponibles, entero ≥0"), ("k", "Elementos elegidos, 0≤k≤n")],
  r"n!=\prod_{j=1}^n j,\quad P(n,k)=\frac{n!}{(n-k)!},\quad\binom nk=\frac{n!}{k!(n-k)!}",
  r"F_X(t)=\sum_{x\le t}P(X=x)\quad\text{una vez asignadas probabilidades a los arreglos}",
  r"\operatorname{E}[X]=\sum_x xP(X=x),\quad\operatorname{Var}(X)=\sum_x(x-\operatorname{E}[X])^2P(X=x)",
  "Factorial 0! = 1. Con repeticiones de conteos $n_j$, las permutaciones distintas son $n!/\\prod_j n_j!$.",
  "1. Elegir 3 de 10 sin orden da $\\binom{10}{3}$.\n2. Calcule $10·9·8/(3·2·1)=120$.\n3. Si importa el orden, multiplique por $3!=6$ para 720 arreglos.", "analisis"),
 "bayes": (
  "Probabilidad condicional y Bayes", "Actualiza la probabilidad de una hipótesis tras una observación mediante una partición exhaustiva.",
  [("Bᵢ", "Hipótesis disjuntas que suman 1"), ("A", "Evidencia de probabilidad positiva")],
  r"P(B_i\mid A)=\frac{P(A\mid B_i)P(B_i)}{\sum_jP(A\mid B_j)P(B_j)}",
  r"F_{I_A}(t)=\begin{cases}0,&t<0\\1-P(A),&0\le t<1\\1,&t\ge1\end{cases}",
  r"\operatorname{E}[I_A]=P(A),\quad\operatorname{Var}(I_A)=P(A)(1-P(A))",
  "Dos eventos son independientes si $P(A\\cap B)=P(A)P(B)$; condicionar en un evento imposible no está definido.",
  "1. Priori (0,4;0,6), verosimilitudes (0,5;0,1).\n2. Probabilidad total de evidencia $=0,4·0,5+0,6·0,1=0,26$.\n3. Posterior de la primera hipótesis $=0,20/0,26\\approx0,769$.", "analisis"),
 "montecarlo": (
  "Integración y simulación Monte Carlo", "Estima integrales o probabilidades por promedios de valores aleatorios con semilla.",
  [("N", "Número de simulaciones ≥2"), ("a,b", "Extremos finitos con a<b"), ("seed", "Semilla para repetir la corrida")],
  r"\hat I_N=(b-a)\frac1N\sum_{j=1}^N f(U_j),\quad U_j\sim U(a,b)",
  r"P(\hat I_N\le t)\approx\Phi\left(\frac{t-I}{\operatorname{SE}(\hat I_N)}\right)",
  r"\operatorname{E}[\hat I_N]=I,\quad\operatorname{Var}(\hat I_N)=\frac{(b-a)^2\operatorname{Var}(f(U))}{N}",
  "El intervalo normal cubre error de simulación, no sesgos de modelo. En la estimación de π, cuatro veces la fracción de puntos en cuarto de círculo.",
  "1. Genere 10 000 pares uniformes en el cuadrado unitario con semilla 42.\n2. Cuente los que cumplen $u^2+v^2\\le1$ y multiplique la fracción por 4.\n3. Informe estimación de π e intervalo basado en error estándar.", "montecarlo"),
 "ajuste_distribuciones": (
  "Ajuste y comparación de distribuciones", "Busca parámetros que maximizan verosimilitud con límites declarados usando scipy.stats.fit.",
  [("xᵢ", "Muestra numérica finita ≥5"), ("θ", "Parámetros del modelo dentro de límites"), ("AIC", "Criterio de información para comparar modelos")],
  r"\hat\theta=\operatorname*{arg\,max}_{\theta}\sum_{i=1}^n\log f(x_i;\theta),\quad\mathrm{AIC}=2k-2\log L(\hat\theta)",
  r"F_{\hat\theta}(x)=\int_{-\infty}^{x}f(t;\hat\theta)\,\mathrm{d}t",
  r"\operatorname{E}_{\hat\theta}[X]=\int x f(x;\hat\theta)\,\mathrm{d}x,\quad\sigma=\sqrt{\operatorname{Var}_{\hat\theta}(X)}",
  "KS tras estimar parámetros es **exploratoria**: su p sin corrección no debe usarse como prueba formal. Compare AIC solo en los mismos datos.",
  "1. Cargue una muestra positiva y elija exponencial.\n2. Limite localización en cero y ajuste escala por máxima verosimilitud.\n3. Revise histograma vs PDF, AIC y QQ-plot antes de concluir.", "analisis"),
 "qq_plot": (
  "QQ-plot y comparación de datos", "Enfrenta cuantiles empíricos ordenados con cuantiles de un modelo para descubrir colas y asimetrías.",
  [("x_(i)", "i-ésimo dato ordenado"), ("n", "Tamaño de muestra"), ("Q", "Función cuantil teórica")],
  r"q_i=F^{-1}\left(\frac{i-1/2}{n}\right),\quad i=1,\ldots,n",
  r"F_X(x)=P(X\le x),\quad F^{-1}(p)=\inf\{x:F(x)\ge p\}",
  r"\operatorname{E}[X]=\int x\,\mathrm{d}F(x),\quad\sigma_X=\sqrt{\operatorname{Var}(X)}",
  "Puntos aproximadamente lineales sugieren concordancia; desviaciones sistemáticas en extremos señalan colas distintas.",
  "1. Ordene 5 valores reales $x_{(1)},\\ldots,x_{(5)}$.\n2. Calcule probabilidades (0,1;0,3;0,5;0,7;0,9) y sus cuantiles normales.\n3. Trace pares (cuantil teórico, valor empírico) y compare con la recta de referencia.", "analisis"),
}


def _limite(valor, inclusivo=True, inferior=True):
    """Texto editorial para rango de un parámetro."""
    if valor is None:
        return "sin límite"
    return ("≥" if inclusivo else ">") + f" {valor:g}" if inferior else ("≤" if inclusivo else "<") + f" {valor:g}"


def generar_paginas_distribucion():
    """Escribe una página propia por cada modelo del registro."""
    assert set(REGISTRO) == set(DISTRIBUCIONES), "Cada modelo requiere una página editorial."
    for clave, modelo in REGISTRO.items():
        definicion, masa, cdf, media, var, propiedades, x = DISTRIBUCIONES[clave]
        tipo = "masa (PMF)" if modelo.discreta else "densidad (PDF)"
        tabla = "| Parámetro | Significado | Rango | Valor de ejemplo |\n|---|---|---|---|\n"
        if modelo.parametros:
            for param in modelo.parametros:
                limite = f"{_limite(param.minimo, param.incluir_minimo)}; {_limite(param.maximo, param.incluir_maximo, False)}"
                tabla += f"| `{param.nombre}` | {param.descripcion} | {limite} | `{param.default}` |\n"
        else:
            tabla += "| — | Modelo sin parámetros libres | — | — |\n"
        params = modelo.validar()
        valor = (modelo.pmf if modelo.discreta else modelo.pdf)(x, **params)
        acumulada = modelo.cdf(x, **params)
        def formato(a):
            a = np.asarray(a)
            return ", ".join(f"{v:.6g}" for v in a.ravel()) if a.ndim else f"{float(a):.6g}"
        evento = formato(x)
        p_texto = "probabilidad" if modelo.discreta else "densidad (no probabilidad puntual)"
        if modelo.dimensionalidad != "univariante":
            paso3 = ("La CDF mostrada es conjunta para (X,Y)." if clave == "normal_bivariada"
                     else "Las CDF mostradas son marginales por componente, no una CDF conjunta.")
        else:
            paso3 = "Para una cola superior, consulte la función de supervivencia; no sume densidades continuas."
        contenido = f'''# {modelo.nombre}

## Definición formal

{definicion} En AmPu 3.0 se parametriza exactamente como en `scipy.stats`;
los eventos fuera del soporte reciben masa/densidad 0.

## Parámetros y rango

{tabla}

## Función de {tipo}

$$
{masa}
$$

## Función de distribución acumulada (CDF)

$$
{cdf}
$$

En general, la CDF es $F(x)=P(X\\le x)$. Para una variable continua,
$P(a\\le X\\le b)=F(b)-F(a)$; para una discreta los extremos se incluyen
según los saltos de su CDF. {paso3}

## Media, varianza y desviación estándar

$$
{media}
$$

$$
{var}
$$

$$
\\sigma_X=\\sqrt{{\\operatorname{{Var}}(X)}}
$$

En modelos multivariados los momentos anteriores son **por componente**.
Si el momento no existe, la desviación tampoco está definida.

## Propiedades y casos especiales

{propiedades}

![Representación de {modelo.nombre}](../imagenes/{clave}.png)

*Figura 1. Curva teórica o primera marginal ilustrativa para {modelo.nombre}; no sustituye a la densidad conjunta de un modelo multivariante.*

## Ejemplo resuelto, paso a paso

1. Configure {', '.join(f'`{k}={v}`' for k, v in params.items()) or 'la distribución estándar'} y el evento $x={evento}$.
2. Sustituya los parámetros en la fórmula de {tipo}; obtenga {p_texto} **{formato(valor)}**.
3. Evalúe la CDF en ese mismo evento: **{formato(acumulada)}**. {paso3}
4. Interprete unidades y soporte antes de comunicar el resultado; la UI conserva todos los decimales internos.

## Referencias

- Ross, S. M. (2019). *A First Course in Probability* (10.ª ed.). Pearson.
- Casella, G., & Berger, R. L. (2002). *Statistical Inference* (2.ª ed.). Duxbury.
- Virtanen, P., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*, 261–272. https://doi.org/10.1038/s41592-019-0686-2
'''
        (TEORIA / f"{clave}.md").write_text(contenido, encoding="utf-8")


def generar_paginas_tecnicas():
    """Una lección por cada técnica de muestreo e inferencia integrada."""
    for clave, (titulo, definicion, parametros, formula, cdf, momentos, propiedades, ejemplo, figura) in TECNICAS.items():
        filas = "| Parámetro | Significado y rango |\n|---|---|\n" + "".join(f"| `{k}` | {v} |\n" for k, v in parametros)
        texto = f'''# {titulo}

## Definición formal

{definicion}

## Parámetros y rango

{filas}

## Función, estadístico o regla de selección

$$
{formula}
$$

## Función de distribución acumulada (CDF)

{('CDF del indicador de inclusión o aproximación de diseño; no existe una única CDF de toda la técnica.' if clave.startswith('muestreo') else 'CDF de referencia o del estimador bajo las hipótesis indicadas.')}

$$
{cdf}
$$

## Media, varianza y desviación estándar

$$
{momentos}
$$

Si no se explicita $\\sigma=\\sqrt{{\\operatorname{{Var}}}}$, se obtiene como raíz cuadrada de la varianza; cuando no existe, no debe reportarse un valor numérico.

## Propiedades y casos especiales

{propiedades}

![Esquema de {titulo}](../imagenes/{figura}.png)

*Figura 1. Representación orientativa del procedimiento o de su distribución de referencia.*

## Ejemplo resuelto, paso a paso

{ejemplo}

## Referencias

- Cochran, W. G. (1977). *Sampling Techniques* (3.ª ed.). Wiley.
- Casella, G., & Berger, R. L. (2002). *Statistical Inference* (2.ª ed.). Duxbury.
- Virtanen, P., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*, 261–272. https://doi.org/10.1038/s41592-019-0686-2
'''
        (TEORIA / f"{clave}.md").write_text(texto, encoding="utf-8")


def generar_figuras():
    """Diagramas originales con Matplotlib; exporta PNG de tamaño contenido."""
    plt.rcParams.update({"figure.facecolor":"white", "axes.edgecolor":"#d5e2ea", "font.size":10,
                         "axes.titleweight":"bold", "axes.spines.top":False, "axes.spines.right":False})
    for clave, modelo in REGISTRO.items():
        x = DISTRIBUCIONES[clave][-1]
        res = analizar(clave, {}, x, seed=42)
        fig, ax = plt.subplots(figsize=(6.6, 3.2), dpi=110)
        if res.discreta:
            ax.bar(res.x, res.y, width=.78, color="#168f8b", alpha=.9)
        else:
            ax.plot(res.x, res.y, color="#168f8b", lw=2.6)
            ax.fill_between(res.x, res.y, where=res.x <= res.evento, color="#68d6bf", alpha=.48)
        ax.set(xlabel="x" if not res.marginal else "Primera componente", ylabel="PMF" if res.discreta else "Densidad",
               title=modelo.nombre + (" · marginal 1" if res.marginal else ""))
        ax.grid(axis="y", alpha=.18)
        fig.tight_layout()
        fig.savefig(IMAGENES / f"{clave}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)
    nombres = {"muestreo": "Selección aleatoria por estratos",
               "inferencia": "Distribución bajo hipótesis nula",
               "regresion": "Asociación y línea ajustada",
               "analisis": "Datos y densidad de referencia",
               "montecarlo": "Estimación por simulación"}
    rng = np.random.default_rng(42)
    for figura, titulo in nombres.items():
        fig, ax = plt.subplots(figsize=(6.6, 3.2), dpi=110)
        if figura == "muestreo":
            ax.bar(["Estrato A", "Estrato B", "Estrato C"], [10, 18, 12], color=["#168f8b", "#3c77ba", "#f4ae6a"])
            ax.set(ylabel="Unidades seleccionadas", ylim=(0, 22))
        elif figura == "regresion":
            xx = np.linspace(0, 10, 35)
            ax.scatter(xx, 1 + .8*xx + rng.normal(0,1,35), alpha=.6, color="#168f8b")
            ax.plot(xx, 1 + .8*xx, color="#d96163", lw=2)
            ax.set(xlabel="Predictor X", ylabel="Respuesta Y")
        elif figura == "inferencia":
            xx = np.linspace(-4,4,280)
            ax.plot(xx, stats.norm.pdf(xx), color="#168f8b", lw=2.5)
            ax.fill_between(xx, stats.norm.pdf(xx), where=abs(xx)>1.96, color="#d96163", alpha=.55)
            ax.set(xlabel="Estadístico estandarizado", ylabel="Densidad")
        elif figura == "montecarlo":
            puntos = rng.random((500,2))
            dentro = (puntos**2).sum(axis=1) <=1
            ax.scatter(puntos[dentro,0], puntos[dentro,1], s=10, color="#168f8b", alpha=.65)
            ax.scatter(puntos[~dentro,0], puntos[~dentro,1], s=10, color="#d96163", alpha=.65)
            ax.set(xlim=(0,1), ylim=(0,1), xlabel="u", ylabel="v")
        else:
            datos = rng.normal(size=800)
            ax.hist(datos, bins=28, density=True, alpha=.6, color="#168f8b")
            xx = np.linspace(-3,3,250)
            ax.plot(xx, stats.norm.pdf(xx), color="#d96163", lw=2)
            ax.set(xlabel="Valor observado", ylabel="Densidad")
        ax.set_title(titulo)
        ax.grid(axis="y", alpha=.17)
        fig.tight_layout()
        fig.savefig(IMAGENES / f"{figura}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    TEORIA.mkdir(parents=True, exist_ok=True)
    IMAGENES.mkdir(parents=True, exist_ok=True)
    generar_paginas_distribucion()
    generar_paginas_tecnicas()
    generar_figuras()
    print(f"{len(list(TEORIA.glob('*.md')))} lecciones y {len(list(IMAGENES.glob('*.png')))} figuras generadas.")
