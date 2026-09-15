import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col

SALIDA = "salida"
base = pd.read_csv(f"{SALIDA}/base_ocupados_limpia.csv", low_memory=False)
base = base.copy()

base["ln_ing_men"] = np.log(base["ing_lab_men"].clip(lower=1))
base["ln_hrs"] = np.log(base["hrs_sem"].clip(lower=1))
base["ln_salario_hora"] = np.log(base["salario_hora"].clip(lower=0.01))
base["mujer"] = base["mujer"].astype(int)

niveles = ["Sin instruccion", "Preescolar", "Primaria", "Secundaria", "Preparatoria",
           "Normal", "Tecnica", "Profesional", "Especialidad", "Maestria", "Doctorado"]
dummies = pd.get_dummies(base["nivel_edu"].astype("category"), prefix="nivel", dtype=float)
dummies.columns = [c.replace(" ", "_") for c in dummies.columns]
ref = "nivel_Sin_instruccion"
dummies = dummies.drop(columns=[ref])
base = pd.concat([base, dummies], axis=1)

muestra = base[base["ing_lab_men"] > 0].copy()
muestra_hora = muestra[muestra["hrs_sem"] > 0].copy()

resultados = {}
log = []
def anotar(msg):
    log.append(msg)
    print(msg)

anotar(f"Muestra de regresion: ocupados 14+ con ingreso mensual > 0 (n={len(muestra):,})")
anotar(f"Expandida: {muestra['factor'].sum():,.0f} personas\n")

X1 = sm.add_constant(muestra[["escolaridad", "edad", "edad2", "mujer"]])
y1 = muestra["ln_ing_men"]
m1 = sm.WLS(y1, X1, weights=muestra["factor"]).fit(cov_type="HC1")
resultados["(1) Mincer basico"] = m1
anotar("=== MODELO 1: Mincer basico ===")
anotar(f"R2 = {m1.rsquared:.4f} | n = {int(m1.nobs):,}")
b_esc = m1.params["escolaridad"]
anotar(f"Rendimiento por ano de escolaridad: {b_esc * 100:.2f}%")
anotar(f"Brecha mujer: {(np.exp(m1.params['mujer']) - 1) * 100:.2f}%")
anotar(f"Edad de ingreso maximo: {-m1.params['edad'] / (2 * m1.params['edad2']):.1f} anos\n")

X2 = sm.add_constant(muestra[["escolaridad", "edad", "edad2", "mujer", "ln_hrs"]])
m2 = sm.WLS(y1, X2, weights=muestra["factor"]).fit(cov_type="HC1")
resultados["(2) Mincer + horas"] = m2
anotar("=== MODELO 2: Mincer + log(horas) ===")
anotar(f"R2 = {m2.rsquared:.4f} | n = {int(m2.nobs):,}")
anotar(f"Rendimiento por ano de escolaridad: {m2.params['escolaridad'] * 100:.2f}%")
anotar(f"Brecha mujer: {(np.exp(m2.params['mujer']) - 1) * 100:.2f}%")
anotar(f"Elasticidad horas: {m2.params['ln_hrs']:.3f}\n")

cols_nivel = [c for c in base.columns if c.startswith("nivel_") and c != "nivel_edu"]
X3 = sm.add_constant(muestra[cols_nivel + ["edad", "edad2", "mujer", "ln_hrs"]])
m3 = sm.WLS(y1, X3, weights=muestra["factor"]).fit(cov_type="HC1")
resultados["(3) Niveles educativos"] = m3
anotar("=== MODELO 3: dummies de nivel educativo ===")
anotar(f"R2 = {m3.rsquared:.4f} | n = {int(m3.nobs):,}")
for c in cols_nivel:
    p = m3.params[c]
    anotar(f"  {c.replace('nivel_', '')}: +{(np.exp(p) - 1) * 100:6.2f}% vs sin instruccion")
anotar("")

y2 = muestra_hora["ln_salario_hora"]
X4 = sm.add_constant(muestra_hora[["escolaridad", "edad", "edad2", "mujer"]])
m4 = sm.WLS(y2, X4, weights=muestra_hora["factor"]).fit(cov_type="HC1")
resultados["(4) Salario por hora"] = m4
anotar("=== MODELO 4: log(salario por hora) ===")
anotar(f"R2 = {m4.rsquared:.4f} | n = {int(m4.nobs):,}")
anotar(f"Rendimiento por ano de escolaridad: {m4.params['escolaridad'] * 100:.2f}%")
anotar(f"Brecha mujer: {(np.exp(m4.params['mujer']) - 1) * 100:.2f}%\n")

with open(f"{SALIDA}/resultados_econometria.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log))
    f.write("\n\n")
    for nombre, m in resultados.items():
        f.write(f"{'=' * 70}\n{nombre}\n{'=' * 70}\n")
        f.write(m.summary().as_text())
        f.write("\n\n")

tabla = summary_col(
    list(resultados.values()),
    stars=True,
    model_names=list(resultados.keys()),
    info_dict={"N": lambda x: f"{int(x.nobs):,}", "R2": lambda x: f"{x.rsquared:.3f}"},
    regressor_order=["escolaridad", "edad", "edad2", "mujer", "ln_hrs"],
)
tabla.tables[0].to_csv(f"{SALIDA}/tabla_regresiones.csv")
print(f"\nResultados guardados en {SALIDA}/resultados_econometria.txt")
print(f"Tabla comparativa guardada en {SALIDA}/tabla_regresiones.csv")
