# Informe final: Relación entre el nivel educativo y los ingresos laborales en México (ENIGH 2024)

**Autora:** Sayde Abigail Canche Quintana  
**Datos:** Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) 2024, INEGI, serie Nueva Construcción  
**Herramientas:** Python (pandas, matplotlib, seaborn, statsmodels)

---

## Resumen

Se estima la relación entre el nivel educativo y los ingresos laborales de la población ocupada de 14 años o más en México en 2024, controlando por edad, sexo y horas trabajadas. Los resultados muestran una relación positiva y económicamente significativa: cada año adicional de escolaridad se asocia con un incremento aproximado de 9% en el ingreso laboral mensual. Se confirma además una brecha de género persistente (≈25% a favor de los hombres, una vez controladas la educación, la edad y las horas) y un perfil cóncavo del ingreso respecto a la edad, con un máximo cercano a los 44 años.

---

## 1. Pregunta de investigación

¿Cuál es la relación entre el nivel educativo y los ingresos laborales, considerando características como edad, sexo y horas trabajadas?

**Hipótesis**

- H1: a mayor nivel educativo, mayor ingreso laboral.
- H2: la brecha de ingresos entre hombres y mujeres persiste aun controlando por educación, edad y horas.
- H3: el perfil ingreso-edad es cóncavo.

## 2. Datos

Se compararon la ENOE (trimestral, orientada a la dinámica del mercado laboral) y la ENIGH (bienal, orientada a la distribución del ingreso y el gasto). Se eligió la **ENIGH 2024** porque:

1. Capta los ingresos laborales con claves desagregadas por concepto (sueldos, horas extras, comisiones, aguinaldo, negocios propios, etc.), lo que permite construir el ingreso laboral individual.
2. Registra el nivel y grado educativo aprobado de cada integrante del hogar (`nivelaprob`, `gradoaprob`), base para construir la escolaridad en años.
3. Incluye horas trabajadas por trabajo, edad, sexo y factor de expansión para inferencia nacional.

**Archivos utilizados:** `poblacion.csv` (308,598 personas), `trabajos.csv` (164,325 trabajos), `ingresos.csv` (391,563 registros de ingreso) y `concentradohogar.csv` (91,414 hogares).

**Limpieza:** normalización de tipos y espacios, detección de duplicados (0 encontrados), validación de rangos (0 valores fuera de rango) y construcción de variables:

- `ing_lab_men` / `ing_lab_tri`: ingreso laboral mensual y trimestral (suma de las claves P001–P081 de `ingresos.csv`).
- `escolaridad`: años de escolaridad construidos con `nivelaprob` y `gradoaprob`.
- `hrs_sem`: horas semanales (suma de `htrab` por persona).
- `mujer`, `edad2`, `salario_hora`.

**Población de análisis:** 149,276 ocupados de 14 años o más (63.7 millones expandidos con el factor).

## 3. Análisis descriptivo

Ingreso laboral mensual medio: **$10,124** (ponderado). La mediana es $7,530 y el percentil 90, $18,400, lo que refleja la marcada asimetría de la distribución del ingreso.

**Por sexo**

| Sexo | Personas (miles) | Ingreso medio | Horas semanales | Escolaridad (años) |
|---|---|---|---|---|
| Hombre | 36,437 | $11,688 | 48.8 | 10.3 |
| Mujer | 27,238 | $8,033 | 39.6 | 10.8 |

**Por nivel educativo**

| Nivel educativo | Ingreso medio | Horas semanales |
|---|---|---|
| Sin instrucción | $3,928 | 39.9 |
| Primaria | $6,013 | 43.6 |
| Secundaria | $7,866 | 46.2 |
| Preparatoria | $9,118 | 46.2 |
| Técnica | $10,395 | 43.6 |
| Normal | $12,854 | 36.5 |
| Profesional | $16,061 | 43.9 |
| Maestría | $26,241 | 42.5 |
| Doctorado | $29,841 | 42.5 |

Existe un gradiente educativo claro: un profesionista gana 4.1 veces lo que una persona sin instrucción, y una persona con doctorado 7.6 veces. La brecha de género aparece en todos los niveles educativos (de −20% a −56% para las mujeres), con excepción del nivel Normal.

**Gráficas generadas** (`graficas/`): ingreso medio por nivel educativo, dispersión log(ingreso)–escolaridad, ingreso por nivel y sexo, y densidad del log(ingreso) por sexo.

## 4. Modelo econométrico

Se estima la ecuación de Mincer por **mínimos cuadrados ponderados (WLS)** con el factor de expansión como ponderador y errores estándar robustos (HC1):

```
ln(ingreso_i) = β0 + β1·escolaridad_i + β2·edad_i + β3·edad_i² + β4·mujer_i + β5·ln(horas_i) + u_i
```

Muestra: 128,336 ocupados con ingreso laboral positivo (55.8 millones expandidos).

| Variable | (1) Mincer básico | (2) + horas | (4) Salario por hora |
|---|---|---|---|
| Escolaridad | 0.0946*** (0.0009) | 0.0930*** (0.0009) | 0.0922*** (0.0009) |
| Edad | 0.0750*** (0.0016) | 0.0570*** (0.0014) | 0.0482*** (0.0014) |
| Edad² | −0.0009*** (0.0000) | −0.0006*** (0.0000) | −0.0005*** (0.0000) |
| Mujer | −0.4758*** (0.0074) | −0.2918*** (0.0069) | −0.2012*** (0.0069) |
| ln(horas) | | 0.6701*** (0.0090) | |
| Constante | 6.6627*** | 4.4210*** | 1.8517*** |
| R² | 0.2627 | 0.3650 | 0.2167 |
| n | 128,336 | 128,336 | 128,336 |

Errores estándar robustos entre paréntesis. *** p<0.01.

**Modelo con dummies de nivel educativo** (referencia: sin instrucción), controlando edad, edad², mujer y horas:

| Nivel | Prima vs sin instrucción | | Nivel | Prima vs sin instrucción |
|---|---|---|---|---|
| Preescolar | +72% | | Profesional | +305% |
| Primaria | +49% | | Especialidad | +569% |
| Secundaria | +105% | | Maestría | +553% |
| Preparatoria | +152% | | Doctorado | +654% |
| Técnica | +187% | | | |

## 5. Interpretación

1. **Rendimiento de la educación.** Cada año adicional de escolaridad eleva el ingreso laboral mensual ≈ **9.3%** (modelo 2), un valor consistente con la literatura para México (7–10%). El modelo 4, que usa salario por hora, confirma la magnitud (9.2%), indicando que el efecto no es solo por trabajar más horas.
2. **Brecha de género.** Sin controlar horas, las mujeres ganan 37.9% menos; al controlar horas la brecha baja a 25.3%, y en salario por hora a 18.2%. Las horas explican una parte de la brecha (las mujeres trabajan en promedio 9.2 horas menos a la semana), pero subsiste una brecha importante no explicada por educación, edad ni horas.
3. **Perfil de edad.** Los coeficientes de edad y edad² implican un perfil cóncavo con ingreso máximo alrededor de los 44 años, consistente con la teoría del capital humano.
4. **No linealidades.** Las dummies de nivel educativo muestran rendimientos crecientes: los niveles de posgrado (maestría y doctorado) tienen primas mucho mayores que las diferencias entre niveles básicos.

## 6. Conclusiones

Las tres hipótesis se confirman. La educación es un determinante central del ingreso laboral en México en 2024: el rendimiento por año de escolaridad ronda el 9% y los niveles de posgrado triplican o sextuplican el ingreso respecto a la población sin instrucción. La brecha de género persiste aun controlando educación, edad y horas, y el perfil ingreso-edad es cóncavo con máximo cercano a los 44 años. Los resultados son consistentes al usar ingreso mensual, salario por hora y especificaciones con dummies educativas.

## 7. Referencias

- INEGI (2025). *Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) 2024. Nueva serie. Descripción de la base de datos.* https://www.inegi.org.mx/programas/enigh/nc/2024/
- INEGI. *Encuesta Nacional de Ocupación y Empleo (ENOE).* https://www.inegi.org.mx/programas/enoe/15ymas/
- Mincer, J. (1974). *Schooling, Experience, and Earnings*. NBER.

---

*Repositorio reproducible: `pip install -r requirements.txt`, `python descarga_datos.py`, `python limpieza.py`, `python analisis_descriptivo.py`, `python econometria.py`.*
