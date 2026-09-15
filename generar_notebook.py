import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(t):
    cells.append(nbf.v4.new_markdown_cell(t))

def code(t):
    cells.append(nbf.v4.new_code_cell(t))

md("""# Relación entre el nivel educativo y los ingresos laborales en México

**ENIGH 2024 (INEGI, serie Nueva Construcción)**

Proyecto de práctica: análisis descriptivo y econométrico de la relación educación-ingresos.  
Autora: Sayde Abigail Canche Quintana""")

md("""## 1. Definición de la investigación

**Pregunta:** ¿Cuál es la relación entre el nivel educativo y los ingresos laborales, considerando características como edad, sexo y horas trabajadas?

**Hipótesis:**
- H1: a mayor nivel educativo, mayor ingreso laboral.
- H2: la brecha de ingresos entre hombres y mujeres persiste aun controlando por educación, edad y horas trabajadas.
- H3: el perfil ingreso-edad es cóncavo (crece y luego decrece).

**Objetivo:** estimar el rendimiento de la educación mediante la ecuación de Mincer con controles de edad, sexo y horas trabajadas, usando los factores de expansión de la encuesta.""")

md("""## 2. Elección de la fuente: ENOE vs ENIGH

| Criterio | ENOE | ENIGH |
|---|---|---|
| Objetivo | Dinámica del mercado laboral | Distribución de ingresos y gastos |
| Periodicidad | Trimestral | Bienal |
| Ingresos | Solo laborales, detalle limitado | Detallados por concepto (sueldos, horas extras, aguinaldo, negocios...) |
| Educación | Nivel e años de escolaridad | Nivel y grado aprobado de cada integrante |
| Uso típico | Empleo | Pobreza, distribución del ingreso, Mincer |

**Elección: ENIGH 2024** por su detalle de ingresos laborales por concepto, la educación de cada integrante del hogar y los factores de expansión. Archivos usados: `poblacion.csv`, `trabajos.csv`, `ingresos.csv` y `concentradohogar.csv`.""")

md("""## 3. Descarga y limpieza de datos""")

code("""import sys
print("Python:", sys.executable)
try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import statsmodels.api as sm
except ModuleNotFoundError as e:
    raise RuntimeError(
        f"Falta el paquete {e.name}. Ejecuta 'pip install -r requirements.txt' "
        "y verifica que el kernel del notebook sea 'Python 3.12 (ENIGH)'."
    ) from e
print("Paquetes OK: numpy", np.__version__, "| pandas", pd.__version__, "| statsmodels", sm.__version__)""")

code("""import os
if os.path.basename(os.getcwd()) == "notebook":
    os.chdir("..")
if not os.path.exists("salida/base_ocupados_limpia.csv"):
    print("Descargando microdatos...")
    !python descarga_datos.py
    print("Limpiando datos...")
    !python limpieza.py
else:
    print("La base limpia ya existe en salida/.")""")

code("""base = pd.read_csv("salida/base_ocupados_limpia.csv", low_memory=False)
base = base.copy()
base["ln_ing_men"] = np.log(base["ing_lab_men"].clip(lower=1))
base["ln_hrs"] = np.log(base["hrs_sem"].clip(lower=1))
base["sexo_etq"] = base["sexo"].map({1: "Hombre", 2: "Mujer"})
print(f"Ocupados 14+ en la muestra: {len(base):,}")
print(f"Población expandida: {base['factor'].sum():,.0f}")
base[["sexo_etq", "edad", "escolaridad", "hrs_sem", "ing_lab_men", "factor"]].head()""")

md("""## 4. Análisis descriptivo (ponderado por factor de expansión)

Perfil de la población ocupada y distribución del ingreso por nivel educativo y sexo.""")

code("""def media_pond(g):
    vals = g["ing_lab_men"] if isinstance(g, pd.DataFrame) else g
    return np.average(vals, weights=base.loc[vals.index, "factor"])

perfil = base.groupby("sexo_etq", observed=True).agg(
    personas=("factor", "sum"),
    ingreso_medio=("ing_lab_men", media_pond),
    horas_medias=("hrs_sem", media_pond),
).round(2)
print("Perfil por sexo (ponderado)")
print(perfil)""")

code("""orden = ["Sin instruccion", "Preescolar", "Primaria", "Secundaria", "Preparatoria",
         "Normal", "Tecnica", "Profesional", "Especialidad", "Maestria", "Doctorado"]
base["nivel_edu"] = pd.Categorical(base["nivel_edu"], categories=orden, ordered=True)
tabla = base.groupby("nivel_edu", observed=True).agg(
    personas=("factor", "sum"),
    ingreso_medio=("ing_lab_men", media_pond),
    horas_medias=("hrs_sem", media_pond),
).round(2)
tabla""")

code("""sns.set_theme(style="whitegrid")
ing = base.groupby("nivel_edu", observed=True).apply(media_pond, include_groups=False)
fig, ax = plt.subplots(figsize=(10, 5))
colores = ["#7f8c8d" if n in ["Sin instruccion", "Preescolar"] else "#2e86de" for n in ing.index]
ax.bar(ing.index, ing.values, color=colores)
ax.set_title("Ingreso laboral mensual medio por nivel educativo (ponderado)")
ax.set_ylabel("Ingreso mensual ($)")
ax.tick_params(axis="x", rotation=45)
for i, v in enumerate(ing.values):
    ax.text(i, v + 300, f"${v:,.0f}", ha="center", fontsize=8)
plt.tight_layout()
plt.show()""")

code("""fig, ax = plt.subplots(figsize=(9, 5.5))
muestra = base[base["ing_lab_men"] > 0]
ax.scatter(muestra["escolaridad"], muestra["ln_ing_men"], s=4, alpha=0.08, color="#4C72B0")
p, i = np.polyfit(muestra["escolaridad"], muestra["ln_ing_men"], 1)
x = np.linspace(muestra["escolaridad"].min(), muestra["escolaridad"].max(), 100)
ax.plot(x, p * x + i, color="#C44E52", lw=2.5, label=f"pendiente {p * 100:.1f}% por año")
ax.set_title("Log(ingreso mensual) vs escolaridad")
ax.set_xlabel("Años de escolaridad")
ax.set_ylabel("log(ingreso laboral mensual)")
ax.legend()
plt.tight_layout()
plt.show()""")

code("""piv = base.pivot_table(index="nivel_edu", columns="sexo_etq", values="ing_lab_men",
                        aggfunc=media_pond, observed=True)
piv.plot(kind="bar", color=["#4C72B0", "#C44E52"], figsize=(11, 5))
plt.title("Ingreso laboral mensual medio por nivel educativo y sexo (ponderado)")
plt.ylabel("Ingreso mensual ($)")
plt.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.show()""")

md("""## 5. Econometría: ecuación de Mincer

$$\\ln(ingreso_i) = \\beta_0 + \\beta_1 escolaridad_i + \\beta_2 edad_i + \\beta_3 edad_i^2 + \\beta_4 mujer_i + \\beta_5 \\ln(horas_i) + u_i$$

Estimación por **mínimos cuadrados ponderados (WLS)** con el factor de expansión como peso y errores robustos (HC1). La muestra incluye ocupados de 14 años o más con ingreso laboral mensual positivo.""")

code("""muestra = base[base["ing_lab_men"] > 0].copy()
X = sm.add_constant(muestra[["escolaridad", "edad", "edad2", "mujer", "ln_hrs"]])
m2 = sm.WLS(muestra["ln_ing_men"], X, weights=muestra["factor"]).fit(cov_type="HC1")
print(m2.summary().tables[1])""")

code("""rend = m2.params["escolaridad"] * 100
brecha = (np.exp(m2.params["mujer"]) - 1) * 100
edad_max = -m2.params["edad"] / (2 * m2.params["edad2"])
print(f"Rendimiento de la educación: {rend:.2f}% por año de escolaridad")
print(f"Brecha de género: {brecha:.2f}%")
print(f"Edad de ingreso máximo estimado: {edad_max:.1f} años")
print(f"Elasticidad ingreso-horas: {m2.params['ln_hrs']:.3f}")""")

code("""X3 = sm.add_constant(muestra[["escolaridad", "edad", "edad2", "mujer"]])
m1 = sm.WLS(muestra["ln_ing_men"], X3, weights=muestra["factor"]).fit(cov_type="HC1")
print(f"Sin controlar horas, la brecha de género es {(np.exp(m1.params['mujer']) - 1) * 100:.2f}% "
      f"y el rendimiento educativo {m1.params['escolaridad'] * 100:.2f}%.")""")

md("""## 6. Conclusiones

1. **H1 se confirma:** existe una relación positiva y marcada entre educación e ingresos. Cada año adicional de escolaridad se asocia con un incremento cercano al 9% del ingreso laboral mensual; un profesional gana ~300% más que alguien sin instrucción.
2. **H2 se confirma:** aun controlando por educación, edad y horas, las mujeres ganan ~25% menos que los hombres (la brecha baja a ~18% al comparar salario por hora).
3. **H3 se confirma:** el perfil ingreso-edad es cóncavo, con un máximo estimado alrededor de los 44 años.
4. Las horas trabajadas son un canal importante: su elasticidad es ~0.67 y explica parte de la brecha de género (las mujeres trabajan menos horas en promedio).

*Resultados descriptivos y econométricos completos en `informe.md` y `salida/`.*""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3.12 (ENIGH)", "language": "python", "name": "enigh"},
    "language_info": {"name": "python", "version": "3.12"},
}

os.makedirs("notebook", exist_ok=True)
with open("notebook/analisis.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook creado: notebook/analisis.ipynb")
