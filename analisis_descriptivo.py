import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

SALIDA = "salida"
GRAF = "graficas"
os.makedirs(GRAF, exist_ok=True)

sns.set_theme(style="whitegrid")
COLOR_H = "#4C72B0"
COLOR_M = "#C44E52"

base = pd.read_csv(f"{SALIDA}/base_ocupados_limpia.csv", low_memory=False)
base = base.copy()
base["ln_ing_men"] = np.log(base["ing_lab_men"].clip(lower=1))
base["ln_hrs"] = np.log(base["hrs_sem"].clip(lower=1))
base["sexo_etq"] = base["sexo"].map({1: "Hombre", 2: "Mujer"})

ORDEN_NIVEL = ["Sin instruccion", "Preescolar", "Primaria", "Secundaria", "Preparatoria",
               "Normal", "Tecnica", "Profesional", "Especialidad", "Maestria", "Doctorado"]
base["nivel_edu"] = pd.Categorical(base["nivel_edu"], categories=ORDEN_NIVEL, ordered=True)

def media_pond(g):
    return np.average(g["ing_lab_men"], weights=g["factor"])

def media_pond_col(g, col):
    return np.average(g[col], weights=g["factor"])

print("=== 1. PERFIL DE LA POBLACIÓN OCUPADA (ponderado por factor) ===")
print(f"Total ocupados (muestra): {len(base):,}")
print(f"Total ocupados (expandido): {base['factor'].sum():,.0f}")
print(f"Ingreso laboral mensual medio: ${media_pond(base):,.2f}")
print(f"Horas semanales medias: {media_pond_col(base, 'hrs_sem'):.1f}")
print(f"Escolaridad media (años): {media_pond_col(base, 'escolaridad'):.1f}")

perfil_sexo = base.groupby("sexo_etq", observed=True).agg(
    personas=("factor", "sum"),
    ingreso_medio=("ing_lab_men", lambda g: np.average(g, weights=base.loc[g.index, "factor"])),
    horas_medias=("hrs_sem", lambda g: np.average(g, weights=base.loc[g.index, "factor"])),
    escolaridad_media=("escolaridad", lambda g: np.average(g, weights=base.loc[g.index, "factor"])),
).round(2)
print("\nPor sexo:")
print(perfil_sexo)

print("\n=== 2. INGRESO Y HORAS POR NIVEL EDUCATIVO (ponderado) ===")
tabla_nivel = base.groupby("nivel_edu", observed=True).agg(
    personas=("factor", "sum"),
    ingreso_medio=("ing_lab_men", lambda g: np.average(g, weights=base.loc[g.index, "factor"])),
    horas_medias=("hrs_sem", lambda g: np.average(g, weights=base.loc[g.index, "factor"])),
    escolaridad_media=("escolaridad", lambda g: np.average(g, weights=base.loc[g.index, "factor"])),
).round(2)
print(tabla_nivel)

print("\n=== 3. INGRESO POR SEXO Y NIVEL EDUCATIVO (ponderado) ===")
tabla_sexo_nivel = base.pivot_table(
    index="nivel_edu", columns="sexo_etq", values="ing_lab_men",
    aggfunc=lambda g: np.average(g, weights=base.loc[g.index, "factor"]),
    observed=True,
).round(2)
tabla_sexo_nivel["brecha_mujer_hombre"] = (tabla_sexo_nivel["Mujer"] / tabla_sexo_nivel["Hombre"] - 1).round(4) * 100
print(tabla_sexo_nivel)

print("\n=== 4. PERCENTILES DEL INGRESO MENSUAL ===")
for p in [10, 25, 50, 75, 90, 95, 99]:
    print(f"  p{p}: ${np.percentile(base['ing_lab_men'], p):,.2f}")

tablas = pd.concat(
    [perfil_sexo.assign(tabla="perfil_sexo").reset_index(),
     tabla_nivel.assign(tabla="nivel_educativo").reset_index(),
     tabla_sexo_nivel.assign(tabla="sexo_x_nivel").reset_index()],
    ignore_index=True, sort=False,
)
tablas.to_csv(f"{SALIDA}/tablas_descriptivas.csv", index=False)
print(f"\nTablas guardadas en {SALIDA}/tablas_descriptivas.csv")

print("\n=== 5. GRÁFICAS ===")
plt.figure(figsize=(10, 5.5))
ing_medio = base.groupby("nivel_edu", observed=True).apply(media_pond, include_groups=False)
colores = ["#7f8c8d" if n in ["Sin instruccion", "Preescolar"] else "#2e86de" for n in ing_medio.index]
plt.bar(ing_medio.index, ing_medio.values, color=colores)
plt.title("Ingreso laboral mensual medio por nivel educativo (ocupados 14+, ENIGH 2024)")
plt.ylabel("Ingreso mensual ($)")
plt.xlabel("Nivel educativo")
plt.xticks(rotation=45, ha="right")
for i, v in enumerate(ing_medio.values):
    plt.text(i, v + 400, f"${v:,.0f}", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig(f"{GRAF}/ingreso_por_nivel_educativo.png", dpi=150)
plt.close()
print(f"  {GRAF}/ingreso_por_nivel_educativo.png")

plt.figure(figsize=(9, 6))
muestra = base[base["ing_lab_men"] > 0]
plt.scatter(muestra["escolaridad"], muestra["ln_ing_men"], s=4, alpha=0.08, color="#4C72B0")
pendiente, intercepto = np.polyfit(muestra["escolaridad"], muestra["ln_ing_men"], 1)
x = np.linspace(muestra["escolaridad"].min(), muestra["escolaridad"].max(), 100)
plt.plot(x, pendiente * x + intercepto, color="#C44E52", lw=2.5,
         label=f"pendiente ≈ {pendiente * 100:.1f}% por año de escolaridad")
plt.title("Log(ingreso mensual) vs escolaridad (ocupados con ingreso > 0)")
plt.xlabel("Años de escolaridad")
plt.ylabel("log(ingreso laboral mensual)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{GRAF}/dispersion_logingreso_escolaridad.png", dpi=150)
plt.close()
print(f"  {GRAF}/dispersion_logingreso_escolaridad.png")

plt.figure(figsize=(11, 5.5))
ing_sexo = base.groupby(["nivel_edu", "sexo_etq"], observed=True).apply(media_pond, include_groups=False).unstack()
ing_sexo.plot(kind="bar", color=[COLOR_H, COLOR_M], width=0.85)
plt.title("Ingreso laboral mensual medio por nivel educativo y sexo")
plt.ylabel("Ingreso mensual ($)")
plt.xlabel("Nivel educativo")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Sexo")
plt.tight_layout()
plt.savefig(f"{GRAF}/brecha_sexo_educacion.png", dpi=150)
plt.close()
print(f"  {GRAF}/brecha_sexo_educacion.png")

plt.figure(figsize=(9, 5))
for sexo, color, etq in [(1, COLOR_H, "Hombre"), (2, COLOR_M, "Mujer")]:
    sns.kdeplot(base.loc[base["sexo"] == sexo, "ln_ing_men"], color=color, label=etq, fill=True, alpha=0.35)
plt.title("Distribución del log(ingreso mensual) por sexo")
plt.xlabel("log(ingreso laboral mensual)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{GRAF}/densidad_logingreso_sexo.png", dpi=150)
plt.close()
print(f"  {GRAF}/densidad_logingreso_sexo.png")

print("\nAnálisis descriptivo completo.")
