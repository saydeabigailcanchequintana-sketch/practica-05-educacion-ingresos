# Glosario de variables (ENIGH 2024, Nueva Construcción)

Resumen compacto de las variables usadas en este proyecto. Documentación completa: *Descriptor de archivos (FD)* de la ENIGH 2024, disponible en la página de microdatos del INEGI.

## Archivos de microdatos usados

| Archivo | Contenido | Llave |
|---|---|---|
| `poblacion.csv` | Características sociodemográficas de cada persona | `folioviv` + `foliohog` + `numren` |
| `trabajos.csv` | Trabajos de las personas de 12+ años | `folioviv` + `foliohog` + `numren` + `id_trabajo` |
| `ingresos.csv` | Ingresos por persona y clave de concepto | `folioviv` + `foliohog` + `numren` + `clave` |
| `concentradohogar.csv` | Variables resumen del hogar | `folioviv` + `foliohog` |

## Variables crudas clave

### poblacion.csv
| Variable | Descripción | Valores |
|---|---|---|
| `folioviv`, `foliohog`, `numren` | Identificadores de vivienda, hogar y persona | — |
| `sexo` | Sexo | 1 = hombre, 2 = mujer |
| `edad` | Edad en años cumplidos | 0–106 |
| `nivelaprob` | Nivel de instrucción aprobado | 0 = sin instrucción, 1 = preescolar, 2 = primaria, 3 = secundaria, 4 = preparatoria, 5 = normal, 6 = técnica, 7 = profesional, 8 = especialidad, 9 = maestría, 10 = doctorado |
| `gradoaprob` | Grado aprobado dentro del nivel | 0–6 |
| `num_trabaj` | Número de trabajos | 1 = uno, 2 = dos o más (personas de 12+) |
| `factor` | Factor de expansión poblacional | — |

### trabajos.csv
| Variable | Descripción |
|---|---|
| `id_trabajo` | Identificador del trabajo de la persona |
| `htrab` | Horas trabajadas a la semana en ese trabajo (0–168) |
| `sinco` | Ocupación (catálogo SINCO) |
| `scian` | Rama de actividad (catálogo SCIAN) |
| `tiene_suel` | 1 = recibe sueldo, 2 = no recibe |
| `no_ing` | Razón por la que no recibe ingresos (solo cuando `tiene_suel = 2`) |

### ingresos.csv
| Variable | Descripción |
|---|---|
| `clave` | Clave del concepto de ingreso (P001–P108, ver catálogo abajo) |
| `mes_1` … `mes_6` | Meses del trimestre de referencia |
| `ing_1` … `ing_6` | Ingreso mensual de cada mes; `ing_6` = mes pasado a la entrevista |
| `ing_tri` | Ingreso trimestral (suma de los 6 meses) |

#### Claves de ingreso laboral usadas en el proyecto
| Grupo | Claves |
|---|---|
| Trabajo principal subordinado | P001 sueldos, P002 destajo, P003 comisiones, P004 horas extras, P005 incentivos, P006 bono, P007 primas, P008 reparto de utilidades, P009 aguinaldo |
| Trabajo principal independiente | P011, P012, P013 |
| Trabajo secundario subordinado | P014, P015, P016 |
| Trabajo secundario independiente | P018, P019, P020 |
| Otros trabajos | P021 (mes pasado), P022 (5 meses anteriores) |
| Menores de 12 años | P067 |
| Negocio propio | P068–P081 |

*Otras claves (no laborales, excluidas del proyecto):* P023–P031 rentas, P032–P048 transferencias, P049 otros ingresos, P050–P066 percepciones financieras y de capital, P101–P108 programas sociales.

### concentradohogar.csv
| Variable | Descripción |
|---|---|
| `ing_cor` | Ingreso corriente total del hogar (trimestral) |
| `ingtrab` | Ingreso del hogar por trabajo |
| `educa_jefe` | Escolaridad del jefe del hogar (1–11) |
| `sexo_jefe`, `edad_jefe` | Sexo y edad del jefe del hogar |
| `tot_integ` | Número de integrantes del hogar |
| `ocupados` | Personas ocupadas del hogar |

## Variables construidas (`limpieza.py`)

| Variable | Construcción |
|---|---|
| `ing_lab_tri` | Ingreso laboral trimestral = suma de `ing_tri` de las claves laborales por persona |
| `ing_lab_men` | Ingreso laboral del mes pasado = suma de `ing_6` de las claves laborales por persona |
| `escolaridad` | Años de escolaridad: 0 sin instrucción/preescolar; primaria = grado; secundaria = 6 + grado; preparatoria = 9 + grado; profesional = 12 + grado; especialidad/maestría = 17 + grado; doctorado = 19 + grado |
| `hrs_sem` | Horas semanales totales = suma de `htrab` de todos los trabajos de la persona |
| `salario_hora` | Salario por hora ≈ `ing_lab_men` / (`hrs_sem` × 4.33) |
| `n_trabajos` | Número de trabajos distintos de la persona |
| `mujer` | 1 si mujer, 0 si hombre |
| `edad2` | Edad al cuadrado (perfil cóncavo de Mincer) |
| `ocupado` | 1 si la persona tiene 14+ años y `num_trabaj` ∈ {1, 2} |

## Convenciones

- **Ponderación:** toda estadística poblacional debe usar `factor` como peso (promedios ponderados; en regresiones se usa WLS con `weights = factor`).
- **Población objetivo:** ocupados de 14 años o más (`salida/base_ocupados_limpia.csv`).
- **Ingresos en pesos corrientes** del trimestre de entrevista de la ENIGH 2024.
- Los blancos (`" "`) en los CSV originales equivalen a "no aplica"; `limpieza.py` los convierte a nulos.
