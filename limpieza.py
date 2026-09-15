import pandas as pd
import numpy as np

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)

SALIDA = "salida"
LOG = []

def log(msg):
    LOG.append(msg)
    print(msg)

import os
os.makedirs(SALIDA, exist_ok=True)

CLAVES_LABOR = [
    "P001", "P002", "P003", "P004", "P005", "P006", "P007", "P008", "P009",
    "P011", "P012", "P013",
    "P014", "P015", "P016",
    "P018", "P019", "P020",
    "P021", "P022",
    "P067",
    "P068", "P069", "P070", "P071", "P072", "P073", "P074",
    "P075", "P076", "P077", "P078", "P079", "P080", "P081",
]

log("=== 1. CARGA DE ARCHIVOS CRUDOS ===")
pob = pd.read_csv("data/poblacion.csv", low_memory=False, dtype={"foliohog": str})
tra = pd.read_csv("data/trabajos.csv", low_memory=False, dtype={"foliohog": str})
ing = pd.read_csv("data/ingresos.csv", low_memory=False, dtype={"foliohog": str})
log(f"poblacion: {pob.shape}")
log(f"trabajos:  {tra.shape}")
log(f"ingresos:  {ing.shape}")

log("\n=== 2. EXPLORACIÓN INICIAL ===")
log(f"Sexo: {pob['sexo'].value_counts().sort_index().to_dict()} (1=hombre, 2=mujer)")
edad_bins = pd.cut(pob["edad"], [0, 13, 17, 24, 34, 44, 54, 64, 130], right=False)
log("Grupos de edad (todas las personas):")
for rango, n in edad_bins.value_counts().sort_index().items():
    log(f"  {rango}: {n}")
log(f"Condicion laboral (num_trabaj): {pob['num_trabaj'].value_counts(dropna=False).to_dict()}")
log("Claves de ingreso mas frecuentes (ingresos.csv):")
for clave, n in ing["clave"].value_counts().head(5).items():
    log(f"  {clave}: {n} registros")
log(f"Resumen horas trabajadas (trabajos.htrab):")
log(f"  media={tra['htrab'].mean():.1f} mediana={tra['htrab'].median():.0f} max={tra['htrab'].max()}")

log("\n=== 3. CONSISTENCIA DE LLAVES ENTRE TABLAS ===")
llave_p = set(pob[["folioviv", "foliohog", "numren"]].drop_duplicates().apply(tuple, axis=1))
llave_t = set(tra[["folioviv", "foliohog", "numren"]].drop_duplicates().apply(tuple, axis=1))
llave_i = set(ing[["folioviv", "foliohog", "numren"]].drop_duplicates().apply(tuple, axis=1))
log(f"trabajos sin persona en poblacion: {len(llave_t - llave_p)}")
log(f"ingresos sin persona en poblacion: {len(llave_i - llave_p)}")

log("\n=== 4. NORMALIZACIÓN DE TIPOS Y ESPACIOS ===")
for df, nombre in [(pob, "poblacion"), (tra, "trabajos"), (ing, "ingresos")]:
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].str.strip().replace({"": np.nan})
            if c not in ["folioviv", "foliohog", "numren", "id_trabajo", "clave",
                         "upm", "est_dis", "entidad", "sinco", "scian", "parentesco"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
log("Espacios eliminados y columnas convertidas a numérico.")

log("\n=== 5. DETECCIÓN DE DUPLICADOS ===")
log(f"poblacion duplicados (folioviv,foliohog,numren): {pob.duplicated(subset=['folioviv','foliohog','numren']).sum()}")
log(f"trabajos duplicados (folioviv,foliohog,numren,id_trabajo): {tra.duplicated(subset=['folioviv','foliohog','numren','id_trabajo']).sum()}")
log(f"ingresos filas duplicadas completas: {ing.duplicated().sum()}")
for df, nombre, sub in [(pob, "poblacion", ['folioviv','foliohog','numren']),
                        (tra, "trabajos", ['folioviv','foliohog','numren','id_trabajo'])]:
    n = df.duplicated(subset=sub).sum()
    if n > 0:
        df.drop_duplicates(subset=sub, inplace=True)
        log(f"  -> {n} duplicados eliminados de {nombre}")

log("\n=== 6. VALIDACIÓN DE RANGOS ===")
checks = [
    ("poblacion", pob, "edad", 0, 130),
    ("poblacion", pob, "sexo", 1, 2),
    ("poblacion", pob, "nivelaprob", 0, 10),
    ("poblacion", pob, "gradoaprob", 0, 6),
    ("trabajos", tra, "htrab", 0, 168),
    ("ingresos", ing, "ing_tri", 0, 1e9),
]
for tabla, df, col, lo, hi in checks:
    n_fuera = ((df[col] < lo) | (df[col] > hi)).sum()
    n_nulos = df[col].isna().sum()
    log(f"{tabla}.{col}: rango esperado [{lo},{hi}] | fuera de rango: {n_fuera} | nulos: {n_nulos}")

log("\n=== 7. VARIABLES DERIVADAS ===")

LABOR = ing[ing["clave"].isin(CLAVES_LABOR)].copy()
LABOR["ing_6"] = pd.to_numeric(LABOR["ing_6"], errors="coerce").fillna(0)
ing_lab = LABOR.groupby(["folioviv", "foliohog", "numren"]).agg(
    ing_lab_tri=("ing_tri", "sum"),
    ing_lab_men=("ing_6", "sum"),
).reset_index()
log(f"Personas con ingreso laboral: {len(ing_lab)}")

hrs = tra.groupby(["folioviv", "foliohog", "numren"]).agg(
    hrs_sem=("htrab", "sum"),
    n_trabajos=("id_trabajo", "nunique"),
    horas_cap=("htrab", "max"),
).reset_index()

pob_limpia = pob.merge(ing_lab, on=["folioviv", "foliohog", "numren"], how="left")
pob_limpia["ing_lab_tri"] = pob_limpia["ing_lab_tri"].fillna(0)
pob_limpia["ing_lab_men"] = pob_limpia["ing_lab_men"].fillna(0)
pob_limpia = pob_limpia.copy()

def escolaridad(row):
    nivel = row["nivelaprob"]
    grado = row["gradoaprob"]
    if pd.isna(nivel):
        return np.nan
    grado = 0 if pd.isna(grado) else grado
    if nivel in (0, 1):
        return 0
    if nivel == 2:
        return grado
    if nivel == 3:
        return 6 + grado
    if nivel == 4:
        return 9 + grado
    if nivel == 5:
        return 9 + grado
    if nivel == 6:
        return 9 + grado
    if nivel == 7:
        return 12 + grado
    if nivel == 8:
        return 17 + grado
    if nivel == 9:
        return 17 + grado
    if nivel == 10:
        return 19 + grado
    return np.nan

ETIQUETA_NIVEL = {0: "Sin instruccion", 1: "Preescolar", 2: "Primaria", 3: "Secundaria",
                  4: "Preparatoria", 5: "Normal", 6: "Tecnica", 7: "Profesional",
                  8: "Especialidad", 9: "Maestria", 10: "Doctorado"}

pob_limpia["escolaridad"] = pob_limpia.apply(escolaridad, axis=1)
pob_limpia["nivel_edu"] = pob_limpia["nivelaprob"].map(ETIQUETA_NIVEL)
pob_limpia["mujer"] = np.where(pob_limpia["sexo"] == 2, 1, 0)
pob_limpia["edad2"] = pob_limpia["edad"] ** 2

pob_limpia["ocupado"] = ((pob_limpia["edad"] >= 14) &
                         (pob_limpia["num_trabaj"].isin(["1", "2"]))).astype(int)

base = pob_limpia.merge(hrs, on=["folioviv", "foliohog", "numren"], how="left")
base["hrs_sem"] = base["hrs_sem"].fillna(0)
base["salario_hora"] = np.where(base["hrs_sem"] > 0,
                                base["ing_lab_men"] / (base["hrs_sem"] * 4.33),
                                np.nan)

log(f"Base completa (todas las personas): {base.shape}")

log("\n=== 8. FILTRO DE POBLACIÓN OBJETIVO (ocupados 14+) ===")
ocupados = base[base["ocupado"] == 1].copy()
log(f"Ocupados 14+: {len(ocupados)}")
log(f"  con ing_lab_tri > 0: {(ocupados['ing_lab_tri'] > 0).sum()}")
log(f"  con ing_lab_tri == 0: {(ocupados['ing_lab_tri'] == 0).sum()}")
log(f"  con hrs_sem > 0: {(ocupados['hrs_sem'] > 0).sum()}")

n_horas_raras = ((ocupados["hrs_sem"] > 126) | (ocupados["hrs_sem"] <= 0)).sum()
log(f"  horas sospechosas (0 o >126): {n_horas_raras}")

log("\n=== 9. VALORES ATÍPICOS DE INGRESO (percentiles) ===")
for p in [0.01, 0.05, 0.5, 0.95, 0.99]:
    log(f"  percentil {p}: ing_lab_tri = {ocupados['ing_lab_tri'].quantile(p):,.2f}")

log("\n=== 10. GUARDADO ===")
ocupados.to_csv(f"{SALIDA}/base_ocupados_limpia.csv", index=False)
pob_limpia.to_csv(f"{SALIDA}/poblacion_limpia.csv", index=False)
log(f"Guardado: {SALIDA}/base_ocupados_limpia.csv ({len(ocupados)} filas, {ocupados.shape[1]} columnas)")
log(f"Guardado: {SALIDA}/poblacion_limpia.csv ({len(pob_limpia)} filas)")

with open(f"{SALIDA}/limpieza_reporte.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\nReporte: {SALIDA}/limpieza_reporte.txt")
