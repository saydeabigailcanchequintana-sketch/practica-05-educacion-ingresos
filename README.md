# Relación entre el nivel educativo y los ingresos laborales en México (ENIGH 2024)

Proyecto de análisis de datos sobre la relación entre educación e ingresos laborales en México, usando la Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) 2024 del INEGI.

---

## Fase 1. Definición de la investigación

**Pregunta de investigación**

¿Cuál es la relación entre el nivel educativo y los ingresos laborales, considerando características como edad, sexo y horas trabajadas?

**Objetivo general**

Estimar la relación entre el nivel educativo de las personas ocupadas y sus ingresos laborales en México en 2024, controlando por edad, sexo y horas trabajadas.

**Objetivos específicos**

1. Describir el perfil sociodemográfico y laboral de la población ocupada (nivel educativo, edad, sexo y horas trabajadas).
2. Medir las brechas de ingreso laboral entre niveles educativos y entre hombres y mujeres.
3. Estimar econométricamente el rendimiento de la educación (ecuación de Mincer) y su interpretación.

**Hipótesis**

- H1: a mayor nivel educativo, mayor ingreso laboral (relación positiva).
- H2: la brecha de ingresos entre hombres y mujeres persiste aun controlando por educación, edad y horas trabajadas.
- H3: el perfil ingreso-edad es cóncavo (los ingresos crecen con la edad, pero a tasa decreciente).

**Justificación**

La educación es uno de los determinantes más estudiados del ingreso laboral. Medir su rendimiento permite dimensionar las brechas sociales y aportar evidencia para políticas educativas y laborales. La ENIGH permite hacerlo con datos de cobertura nacional y representatividad estadística.

---

## Fase 2. Investigación de fuentes: ENOE vs ENIGH

Se compararon las dos principales encuestas de hogares del INEGI que contienen información de ingresos y empleo:

| Criterio | ENOE (Encuesta Nacional de Ocupación y Empleo) | ENIGH (Encuesta Nacional de Ingresos y Gastos de los Hogares) |
|---|---|---|
| Objetivo principal | Medir la dinámica del mercado laboral (ocupación, desocupación, subocupación) | Medir la distribución de ingresos y gastos de los hogares |
| Periodicidad | Trimestral | Bienal (serie Nueva Construcción) |
| Ingresos | Solo ingresos laborales de las personas ocupadas, con detalle limitado | Ingresos monetarios y no monetarios, con claves detalladas por concepto (sueldos, horas extras, aguinaldo, negocios, transferencias, etc.) |
| Educación | Nivel de instrucción y años de escolaridad | Nivel y grado aprobado de cada integrante del hogar, alfabetismo y asistencia escolar |
| Horas trabajadas | Sí (habituales y efectivas) | Sí (horas trabajadas a la semana por trabajo) |
| Hogar | Características laborales de los miembros | Ingresos y gastos completos del hogar, factores de expansión |
| Uso típico | Análisis laboral y de empleo | Análisis de distribución del ingreso, pobreza y ecuaciones de ingreso (Mincer) |

**Conclusión de la comparación.** La pregunta de investigación exige: (a) ingresos laborales individuales detallados, (b) nivel y grado educativo de cada persona, (c) horas trabajadas, (d) edad y sexo, y (e) factores de expansión para inferencia nacional. La ENIGH cumple todos los requisitos en una sola base; la ENOE, si bien es más frecuente, registra los ingresos laborales con menor desagregación y no capta la estructura completa de ingresos por concepto.

Fuentes oficiales:

- INEGI, ENIGH 2024: https://www.inegi.org.mx/programas/enigh/nc/2024/
- INEGI, ENOE: https://www.inegi.org.mx/programas/enoe/15ymas/

---

## Fase 3. Elección de la base de datos

**Base elegida: ENIGH 2024, serie Nueva Construcción (NC).**

Razones:

1. Permite construir el ingreso laboral individual sumando las claves de ingreso por trabajo (P001–P081).
2. Contiene nivel educativo (`nivelaprob`) y grado aprobado (`gradoaprob`) de cada integrante, con los que se construye la escolaridad en años.
3. Incluye horas trabajadas (`htrab`) por trabajo, edad, sexo y factor de expansión.
4. La serie Nueva Construcción es comparable con las ediciones 2016–2022 y es la base oficial para estudios de ingreso en México.

**Archivos utilizados** (microdatos CSV):

| Archivo | Contenido |
|---|---|
| `poblacion.csv` | Características sociodemográficas de cada persona (edad, sexo, educación) |
| `trabajos.csv` | Condición de actividad y horas trabajadas por trabajo |
| `ingresos.csv` | Ingresos por persona y clave de concepto |
| `concentradohogar.csv` | Ingresos y características principales del hogar |

Muestra: 91,414 hogares y 308,598 personas; 149,276 personas ocupadas de 14 años o más.

---

## Estructura del repositorio

```
.
├── README.md                  ← este documento
├── informe.md                 ← informe final del proyecto
├── requirements.txt           ← dependencias de Python
├── descarga_datos.py          ← descarga y verifica los microdatos de INEGI
├── limpieza.py                ← limpieza y construcción de la base de análisis
├── analisis_descriptivo.py    ← tablas y gráficas descriptivas
├── econometria.py             ← regresión de Mincer (statsmodels)
├── verificar_limpieza.py      ← verificación de la base limpia
├── notebook/
│   └── analisis.ipynb         ← notebook con la narrativa completa
├── graficas/                  ← gráficas generadas
├── data/                      ← datos crudos (NO se sube al repositorio)
└── salida/                    ← bases limpias y reportes (NO se sube al repositorio)
```

## Reproducción

```bash
pip install -r requirements.txt
python descarga_datos.py
python limpieza.py
python analisis_descriptivo.py
python econometria.py
```
