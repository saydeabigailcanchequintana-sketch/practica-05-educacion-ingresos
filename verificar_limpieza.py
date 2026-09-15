import pandas as pd
import numpy as np

base = pd.read_csv("salida/base_ocupados_limpia.csv", low_memory=False)
print("Forma:", base.shape)
print("\nColumnas clave:", [c for c in ["folioviv","foliohog","numren","sexo","mujer","edad","edad2",
      "nivelaprob","gradoaprob","escolaridad","nivel_edu","ing_lab_tri","ing_lab_men",
      "hrs_sem","salario_hora","n_trabajos","ocupado","factor"] if c in base.columns])
print("\nTipos:", base[["edad","escolaridad","ing_lab_tri","hrs_sem"]].dtypes.to_dict())
print("\nNulos por columna clave:")
print(base[["edad","nivelaprob","escolaridad","ing_lab_tri","hrs_sem","factor"]].isna().sum())
print("\nResumen:")
print(base[["edad","escolaridad","ing_lab_tri","ing_lab_men","hrs_sem","salario_hora","factor"]].describe().round(2))
print("\nTabla nivel educativo:")
print(base.groupby("nivel_edu").agg(n=("folioviv","count"),
      ing_medio=("ing_lab_tri","mean"), hrs=("hrs_sem","mean"),
      edad=("edad","mean"), escol=("escolaridad","mean")).round(2))
print("\nPor sexo:")
print(base.groupby(["sexo"]).agg(n=("folioviv","count"), ing_medio=("ing_lab_tri","mean"), hrs=("hrs_sem","mean")).round(2))
