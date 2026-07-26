# SPEC 2 — Spec (fuente única de verdad)

**Proyecto:** Clasificador de políticas de privacidad — Proyecto 6, Grupo 3
**Versión:** 0.4 (25 de julio de 2026: modelos base con nombre, frontend React, seguridad como diseño)

> Este documento manda sobre el resto. Si el código, un notebook, una rama o una
> decisión lo contradicen, se corrige el trabajo **o** se actualiza este documento
> de forma explícita. Nunca conviven dos versiones de la verdad.
>
> Es un documento **vivo**: cuando el EDA o el entrenamiento revelen algo nuevo, se
> actualiza aquí.

---

## 1. Dataset

### 1.1 Fuente principal — OPP-115

- **Fuente:** OPP-115 (*Online Privacy Policies, 115*), del Usable Privacy Policy
  Project — Wilson et al., 2016 (CMU / Fordham / Universidad de Pittsburgh).
- **Contenido:** 115 políticas de privacidad reales **en inglés**, partidas en ~3.800
  fragmentos, con un archivo aparte de ~23.000 anotaciones hechas a mano.
- **Por qué este dataset:** las anotaciones manuales son lo que convierte el texto en
  algo aprendible. Sin ellas no hay target. Son **etiquetas de oro**.
- **Uso:** investigación y docencia, citando a Wilson et al. (2016).
- **Ubicación en el repo:** `data/dataset/`.

### 1.2 Mapeo al RGPD

- **Fuente:** Poplavska, E., Norton, T. B., Wilson, S. & Sadeh, N. (2020),
  *From Prescription to Description: Mapping the GDPR to a Privacy Policy Corpus
  Annotation Scheme*, JURIX 2020, pp. 243-246. DOI: 10.3233/FAIA200874.
- **Descarga:** `JURIX_2020_OPP-115_GDPR_v1.0.zip` (83 KB) desde
  <https://usableprivacy.org/data>.
- **Se versiona en el repo** por ser fuente citable y de tamaño mínimo.
- **Ubicación real (descargado, issue #32):**
  `data/dataset_extension/Agent4/external_datasets/JURIX_2020_OPP115_GDPR/jurix_2020_opp-115_gdpr_dataset/`
  con `categories_articles_matrix.csv`, `categories_principles_matrix.csv`,
  `connections_overview.csv` y `readme.pdf`. Es la tabla de consulta del §8.
- **Alcance del mapeo publicado:** 88 conexiones entre artículos del RGPD y
  categorías de OPP-115, con asociaciones en 49 de los 99 artículos y una mediana
  de dos conexiones por artículo. La correspondencia concreta de cada categoría
  está en los CSV, no en el texto del paper.

### 1.3 Extensión del dataset — conjunto de evaluación

Conjunto de políticas actuales (julio 2026) recogidas de webs reales. Incluye una
**preanotación automática** generada con reglas de palabras clave bilingües, usando la
taxonomía de OPP-115.

**Estado tras el procesado (script `03_prepare_evaluation_set.py`, issue #33 cerrado):**

| | Antes de deduplicar | Después |
|---|---|---|
| Párrafos totales | 10.797 | **7.363** |
| Español | 8.680 | **5.385** (`evaluation_es.csv`) |
| Inglés | 2.117 | **1.978** (`evaluation_en.csv`) |

Se eliminaron **3.434 duplicados exactos**. Los dos archivos siguen el mismo esquema
que la tabla de entrenamiento, más dos columnas: `language` y `label_source`.

**Corrección de metadatos (§11 anterior, ya resuelta):** el campo
`authorized_training_file` pasó a llamarse `evaluation_file` y se añadió
`labels_status`. La contradicción entre los metadatos y el rol declarado de este
conjunto quedó eliminada antes de entrenar.

**Rol acordado: material de evaluación y de demo, no de entrenamiento.** Aporta lo que
OPP-115 no tiene (políticas actuales, reales y en español), y es la fuente natural del
conjunto de prueba en español del §4.3.

Características a tener en cuenta antes de usarla:

| Característica | Implicación |
|---|---|
| Preanotación por reglas, sin revisión humana (confianza media 58,8%; 79% marcado para revisión) | Son **etiquetas de plata**: no se entrena ni se mide contra ellas sin validar |
| Una categoría principal por párrafo (2,8% con alternativa) | No es multi-etiqueta como nuestro esquema |
| 76% de los párrafos caen en `Other` | Coherente con dejar `Other` fuera (§2.2) |
| `Do Not Track` casi ausente | La preanotación previa a deduplicar registró 9 casos. **Medido tras deduplicar (24 jul):** el término aparece en 4 de 1.978 párrafos en inglés (0,20%) y en 0 de 5.385 en español. Ver limitaciones §13.1 |
| 3.434 párrafos duplicados exactos dentro del mismo documento | Deduplicados ya por el script 03. Ojo: al ser texto formulaico, la deduplicación puede haber reducido la frecuencia observada de categorías como `do_not_track` (§13.1) |
| Granularidad más fina que OPP-115 (mediana ~20 palabras) | Si alguna vez se mezclan, hay que reagrupar párrafos |
| Campo de artículos RGPD generado por las mismas reglas léxicas | No es trazable jurídicamente; se usa el mapeo de §1.2 en su lugar |
| Los artefactos de los agentes de recogida no son regenerables (proceden de webs vivas, que cambian) | Se conservan versionados. El paso 1 de la secuencia del §12 está cumplido: los scripts 01-03 ya existen |

### 1.4 Fuentes evaluadas y descartadas

**MAPP Corpus** (Mobile App Privacy Policies, set of 155) — Arora et al., 2022,
*A Tale of Two Regulatory Regimes: Creation and Analysis of a Bilingual Privacy Policy
Corpus*, Usable Privacy Policy Project. 64 políticas en inglés y 91 en alemán, con
anotación manual de prácticas de datos.

**Descartado.** Motivos, en orden de peso:

1. **Son políticas de aplicaciones móviles, no de sitios web.** Nuestro producto lee
   políticas de webs: es otro dominio. Este es el motivo principal.
2. No incluye español.
3. Su esquema de anotación es comparable al de OPP-115 pero no idéntico (menos
   prácticas anotadas por política; OPP-115 tiene unas 200), lo que exigiría un trabajo
   de homologación que no cabe en el plazo.
4. Sin tiempo dentro del alcance de dos semanas.

Se registra como opción **evaluada y descartada con motivos**, no se borra la mención:
en la defensa del proyecto la pregunta "¿por qué solo un corpus?" tiene respuesta.

Los archivos de MAPP se retiran del rastreo de git (redescargables desde CMU y sin
ningún script del proyecto que los use), junto con los artefactos de sistema de macOS
(`__MACOSX/`, `.DS_Store`). Ver §12.

## 2. Definición del target

### 2.1 Tipo de clasificación — **multi-etiqueta** (multi-label)

Cada fragmento puede llevar **varias categorías a la vez**. Un mismo párrafo puede
decir "recogemos tu correo **y** lo compartimos con socios publicitarios": son dos
prácticas distintas en una frase.

**Por qué:** es como está anotado OPP-115 (~23.000 anotaciones sobre ~3.800
fragmentos, unas seis por fragmento). Forzar una sola etiqueta por fragmento
(multiclase) obligaría a descartar información real del texto.

**Implicación técnica:** el modelo devuelve **una probabilidad por cada categoría**
(nueve decisiones binarias en paralelo), y un **umbral** decide cuáles se marcan.

### 2.2 Categorías modeladas — **nueve** (de las 10 del dataset)

| # | Categoría (id interno) | En cristiano |
|---|---|---|
| 1 | `first_party_collection_use` | Qué recoge el propio sitio y para qué |
| 2 | `third_party_sharing_collection` | Qué se comparte con o recogen terceros |
| 3 | `user_choice_control` | Qué opciones de control tiene el usuario |
| 4 | `user_access_edit_deletion` | Si puedes acceder, editar o borrar tus datos |
| 5 | `data_retention` | Cuánto tiempo guardan tus datos |
| 6 | `data_security` | Qué medidas protegen tu información |
| 7 | `policy_change` | Cómo avisan si la política cambia |
| 8 | `do_not_track` | Si respetan la señal "no me rastrees" |
| 9 | `international_specific_audiences` | Prácticas para grupos concretos |

**Decisión documentada:** la décima categoría de OPP-115, `Other`, **queda fuera del
target**. Motivos: (a) es un cajón de sastre heterogéneo (texto introductorio,
contacto, lo no cubierto) y por tanto ruidoso; (b) no aporta nada al nivel de
exposición; (c) con macro-F1, una categoría ruidosa arrastra la métrica sin aportar
valor al producto. Dato de apoyo: en la extensión del §1.3, `Other` concentra el 76%
de los párrafos.

**Importante:** "dejar fuera" significa quitar la etiqueta del target, **no borrar
fragmentos**. Los fragmentos anotados solo como `Other` se conservan con todas las
etiquetas a cero. Es el comportamiento correcto del producto: ante un párrafo de
contacto, el modelo no enciende ninguna luz.

**Dato verificado:** son **520 fragmentos de 3.792 (13,7%)** los que quedan con las
nueve etiquetas a cero. Entran al entrenamiento como ejemplos negativos: es lo que
enseña al modelo a callar ante relleno legal, que es la mitad de una política real.
Consecuencia para la lectura de métricas: con estas filas dentro, un modelo que
prediga poco pero calle cuando toca puede obtener un `micro-F1` engañosamente decente.
Por eso la métrica que manda es `macro-F1` (§3).

### 2.2.1 Consolidación de las anotaciones

OPP-115 trae tres versiones de consolidación de las anotaciones de los juristas.
**Decisión: se usa el umbral 0.75**, el punto medio de las tres. Es el criterio con el
que se construyó `training_table.csv` (script `02_build_target.py`).

Efecto documentado: al no exigir unanimidad, entran fragmentos con acuerdo parcial
entre anotadores. Eso explica los pocos casos límite que aparecen al comparar
etiquetas con reglas léxicas (§13.1).

### 2.3 Umbral de decisión

- [ ] **TODO:** fijar el umbral a partir del cual una categoría se considera presente
  (por defecto 0.5, o ajustado por categoría).

Es una decisión de producto, no un detalle técnico: un umbral bajo marca más cosas y
se equivoca por exceso; uno alto solo marca lo evidente y deja pasar prácticas reales.

**Cuándo se decide:** no antes de que exista un modelo que emita probabilidades. Se
ajusta **contra el conjunto de validación**, nunca contra test — probar valores contra
test invalidaría la cifra final del informe. Esta es la razón por la que la partición
tiene tres grupos y no dos (§4.4). Con el desbalance 47:1 documentado, un umbral fijo
de 0.5 probablemente deje `do_not_track` sin detectar nunca.

## 3. Métrica y control de sobreajuste

- **Métrica principal: macro-F1.** Promedia las nueve categorías **por igual**, de
  modo que una categoría rara pero importante (p. ej. `do_not_track`) pesa lo mismo
  que una frecuente (`first_party_collection_use`). Es la métrica que manda al
  comparar modelos y elegir el meta-modelo.
- **Por qué esta y no micro-F1:** micro-F1 da más peso a las categorías con muchos
  ejemplos y produce una nota más alta y optimista. Para una herramienta de privacidad,
  pasar por alto una práctica poco frecuente pero grave es el fallo que no queremos.
- **Métricas reportadas** (en el informe, no deciden): micro-F1, F1 por categoría,
  precision y recall por categoría, matriz de confusión por categoría, y **macro-F1
  desglosada por idioma** (§4.3).
- **Regla de sobreajuste:** la diferencia de macro-F1 entre entrenamiento y
  validación debe ser **menor al 5%**. Si no, se documenta como bloqueo.

### 3.1 Baseline de referencia (el suelo contra el que se compara)

`scripts/06_smoke_test.py` — `OneVsRestClassifier(LogisticRegression(class_weight="balanced"))`
sobre la vectorización común, evaluado en validación:

| Métrica | Valor |
|---|---|
| **macro-F1** | **0,7466** |
| micro-F1 | 0,7599 |

F1 por categoría: `third_party_sharing_collection` 0,82 · `first_party_collection_use`
0,80 · `international_specific_audiences` 0,85 · `policy_change` 0,74 ·
`data_retention` 0,70 · `data_security` 0,70 · `user_choice_control` 0,61 ·
`user_access_edit_deletion` 0,59 · `do_not_track` 0,91.

**No es uno de los cuatro modelos base.** Es referencia, y entra como tal en la tabla
comparativa. TF-IDF con regresión logística es un baseline notoriamente fuerte en
clasificación de texto: **un modelo base que quede en 0,72 no ha fracasado, y superar
0,75 es un resultado real.**

- [ ] **PENDIENTE:** este baseline no reporta el `gap` train/validación que exige la
  regla de sobreajuste. Los cuatro modelos base sí deben reportarlo.
- [ ] **PENDIENTE (investigación, issue #2):** no existe todavía una cifra de
  referencia de la literatura sobre OPP-115. Sin ella, el equipo no puede interpretar
  si 0,75 es bueno, normal o pobre. Es la única investigación realmente pendiente.

## 4. Reparto de los datos

### 4.1 Por política, no por fragmento

Las 115 políticas se reparten **enteras** entre train / validación / test. Ninguna
política puede aparecer en dos grupos a la vez.

**Por qué:** si se repartieran los fragmentos al azar, trozos de una misma política
caerían en train y en test, y el modelo acertaría en parte por reconocer el estilo y
el vocabulario de esa empresa, no por saber leer políticas. Las métricas saldrían
infladas y el modelo rendiría peor ante webs nuevas, que es el uso real.

**Contrapartida asumida:** con solo 115 unidades, el reparto de categorías queda
menos equilibrado entre grupos y hay algo más de azar. Se mitiga fijando la
**semilla aleatoria** y documentando la distribución resultante por grupo.

### 4.2 Deduplicación previa

Antes de partir hay que **eliminar duplicados exactos**. Un mismo párrafo repetido a
los dos lados de la partición produce el mismo efecto que el reparto por fragmento:
el modelo aprueba porque ya vio la respuesta. En la extensión del §1.3 se han
detectado 3.434 duplicados exactos intra-documento.

### 4.3 Conjunto de prueba en español

Como el español entra en el suelo protegido (§5), hace falta poder **demostrar** que
funciona, no solo afirmarlo: un conjunto de **100-200 fragmentos en español con
etiquetas validadas a mano**, tomados de la extensión del §1.3.

Se usa **solo para evaluar**, nunca para entrenar, y produce una macro-F1 separada
por idioma.

- [ ] **TODO (decisión de equipo):** validar una muestra ya preanotada (más rápido,
  con riesgo de dejarse llevar por la sugerencia) o etiquetar en limpio sin ver la
  preanotación (más lento, y de paso mide qué tal lo hacen las reglas).

**Alcance realista de la sesión de verificación (issue #29).** La muestra se concentra
en las **4-5 categorías con volumen real** en español. `do_not_track` tiene **1 sola
fila etiquetada** en el conjunto en español: es imposible cubrirla, y así se declara en
el informe en lugar de dar una cifra sin base. Ver §13.3.

### 4.4 Partición ejecutada — congelada el 24 de julio (issue #18)

`scripts/04_build_split.py` produce `data/processed/split_assignment.csv`.
**Es la única partición del proyecto.** Ningún script vuelve a repartir los datos.

| Parámetro | Valor |
|---|---|
| Unidad de partición | `policy` (115 políticas) |
| Clave de fila | `policy` + `segment` (clave natural, única, sin duplicados) |
| Proporciones objetivo | 70 / 15 / 15 **sobre políticas** |
| Semilla | **42** (funcionó a la primera; no hubo que cambiarla) |
| Salida | `split_assignment.csv`, columnas `policy`, `segment`, `split` |
| Valores de `split` | `train` / `val` / `test` (minúsculas, exactos) |

**Reparto obtenido:**

| | train | val | test |
|---|---|---|---|
| políticas | 80 | 17 | 18 |
| filas | 2.550 | 579 | 663 |

Suma 115 políticas y 3.792 filas. Las proporciones **por fila** son 67/15/18 y no
coinciden con las de política, porque las políticas tienen distinto número de
fragmentos. Es correcto: ajustarlo exigiría mover fragmentos entre grupos, es decir
reintroducir el leakage que la partición existe para evitar.

**Verificaciones que cierran el issue:**

1. Ninguna política aparece en dos grupos. La estructura del código lo hace imposible:
   la asignación es un diccionario indexado por política, así que dos fragmentos del
   mismo documento no pueden recibir valores distintos ni con un fallo de programación.
2. Ninguna fila queda sin asignar y el total no cambia (asserts en el script).
3. Las nueve etiquetas están presentes en los tres grupos:

```
                                  test  train  val
first_party_collection_use         255   1034  232
third_party_sharing_collection     182    804  200
user_choice_control                103    426  103
user_access_edit_deletion           36    156   39
data_retention                      26    108   22
data_security                       63    253   59
policy_change                       38    117   37
do_not_track                         6     20    6
international_specific_audiences    65    227   61
```

4. **Reproducibilidad:** dos ejecuciones seguidas producen un archivo idéntico
   (`diff` vacío).

**Nota metodológica sobre estratificación.** No existe en scikit-learn un splitter que
combine agrupación por grupo, estratificación y multi-etiqueta a la vez. El
procedimiento adoptado es: reparto aleatorio con semilla fija **y verificación
posterior de cobertura**. Si una categoría rara hubiera quedado fuera de algún grupo,
la respuesta correcta es cambiar de semilla **y dejar registro de las probadas** — no
mover filas a mano. Con la 42 no fue necesario.

### 4.5 Vectorización común — congelada el 24 de julio (issue #8)

`scripts/05_vectorize.py`. **Ningún modelo reentrena el vectorizador.**

- **TF-IDF** con: `lowercase=True`, `strip_accents="unicode"`, `ngram_range=(1,2)`,
  `min_df=3`, `max_df=0.9`, `sublinear_tf=True`.
- **Regla no negociable: `fit` una sola vez y solo sobre las filas de `train`;**
  `transform` sobre los tres grupos. Un `fit` sobre el total metería vocabulario de
  test en el modelo: es el mismo leakage del §4.1 entrando por otra puerta.
- **Artefactos** en `artifacts/` (generados, **no versionados**):
  `tfidf_vectorizer.joblib`, `X_{train,val,test}.npz`, `y_{train,val,test}.npy`.

| split | X | y | densidad |
|---|---|---|---|
| train | (2550, 13389) | (2550, 9) | 0,00684 |
| val | (579, 13389) | (579, 9) | 0,00664 |
| test | (663, 13389) | (663, 9) | 0,00595 |

Vocabulario: **13.389 términos**. Las tres matrices comparten número de columnas, lo
que confirma un único `fit`. La densidad decrece de train a test por efecto
*out-of-vocabulary*: las políticas de test usan vocabulario que las de train no tienen,
señal coherente con una partición sin fuga.

**Los parámetros son provisionales** y se ajustan con los datos del EDA (§4.6) cuando
haga falta. Están declarados como constantes al principio del script.

### 4.6 Resultados del EDA (issues #48-#51, carpeta `eda/`)

**Distribución y desbalance (#48, `eda/01_target_distribution.py`).**
Ratio de desbalance **47,5:1** entre `first_party_collection_use` (1.521) y
`do_not_track` (32). Cuatro categorías por debajo de 250 apariciones: `do_not_track`
(32), `data_retention` (156), `policy_change` (192), `user_access_edit_deletion` (231).
Este dato es la justificación empírica de macro-F1 como métrica principal (§3): con una
métrica que pese por instancia, el modelo podría ignorar las categorías raras y aun así
sacar nota alta.

**Comportamiento multi-etiqueta (#49, `eda/02_target_multilabel.py`).**
Media de **1,23 etiquetas por fragmento**. **El 25% de los fragmentos tiene 2 o más
categorías**: este es el dato que justifica el enfoque multi-etiqueta del §2.1 —
forzar una sola categoría descartaría información real en uno de cada cuatro
fragmentos. Casos extremos con hasta 8 categorías simultáneas. Co-ocurrencia más
frecuente: `first_party_collection_use` + `third_party_sharing_collection`, en **503
fragmentos**, que corresponde al patrón habitual de un párrafo que declara recogida y
además cesión a terceros.

**Longitudes y vocabulario (#50, `eda/03_text_length_vocab.py`).**
Media **70 palabras**, mediana 59, percentil 95 en **163**, máximo 372, mínimo 1.
Vocabulario crudo: **12.062 palabras únicas** (coherente con los 13.389 términos del
TF-IDF, que suma bigramas y filtra por `min_df`/`max_df`). Las 15 palabras más
frecuentes son de función gramatical (`to`, `the`, `and`, `you`, `of`), lo que justifica
empíricamente el filtro `max_df`.

Consecuencias: **para TF-IDF no hay nada que cambiar, no trunca.** La referencia
`max_length` ≈ 163-256 tokens aplica solo a modelos con límite de secuencia, si alguno
de los cuatro base lo tuviera.

## 5. Idiomas: inglés y español

**Ruta acordada: traducir en la inferencia.** El modelo se entrena y vive **en
inglés**. Si llega una política en español, se traduce y luego se clasifica.

**Por qué esta ruta:**

- Las etiquetas de oro solo existen en inglés, así que entrenar en español no está
  disponible.
- No toca el modelo: la elección de los ≥4 modelos base (§6) queda intacta y
  representaciones como TF-IDF siguen siendo válidas.
- Solo necesitamos detectar **de qué tema** habla un fragmento, no extraer una
  obligación legal con precisión jurídica; para eso la traducción automática basta.

**Rutas descartadas:** (A) modelo multilingüe con transferencia entre idiomas — obliga
a embeddings neuronales más pesados y lentos; (B) traducir el corpus de entrenamiento
— hereda errores de traducción y duplica el preprocesado.

**Reglas de implementación:**

1. **La traducción es interna y desechable.** Al usuario se le devuelve **su texto
   original**. Si la extensión de Chrome resalta un párrafo, resalta el español que la
   persona está viendo, no una traducción que no aparece en la página.
2. **Degradación elegante (requisito del suelo).** Si el servicio de traducción no
   responde o no hay clave configurada, la aplicación **avisa y sigue funcionando en
   inglés**. Nunca se cae. Esto es lo que permite que otra persona pueda ejecutar el
   proyecto desde el README sin registrarse en ningún servicio.
3. **Caché de traducciones**, indexada por hash del texto, para no consumir cuota
   traduciendo lo mismo repetidamente durante el desarrollo y la demo.
4. **Credenciales:** la clave va en `.env` (ignorado por git), con un `.env.example`
   versionado que documenta los nombres de las variables sin valores.
5. Solo se traduce cuando se detecta español; el inglés no pasa por el traductor.

**Candidatos identificados (24 jul, pendiente de decisión):**

| Opción | A favor | En contra |
|---|---|---|
| **eTranslation** (Comisión Europea) | Gratuito, diseñado para texto legal y administrativo de la UE. Su fidelidad terminológica en este dominio exacto está documentada en literatura reciente | El acceso está pensado para administraciones y proyectos concretos: **hay que comprobar si un equipo de bootcamp puede darse de alta y cuánto tarda** |
| **Modelo de traducción local** (p. ej. familia `opus-mt` vía `transformers`) | Sin clave, sin cuota, sin coste por consulta, y **no envía el texto a ningún tercero** | Más pesado de instalar; calidad a verificar |
| **API comercial** | La más simple de montar | Coste, cuota, y envía el documento a un tercero |

**Argumento de diseño a favor de la opción local.** Una extensión de privacidad que
envía a un servidor ajeno la política que el usuario está leyendo es una contradicción
con su propio propósito. "Nada sale de tu navegador" es un argumento defendible en la
presentación, y encaja con la degradación elegante ya exigida.

**Referencia de literatura (preprint, sin revisión por pares — verificar antes de
citar):** *Enabling Multilingual Privacy Policy Audits: Large-Scale Analysis of Spanish
Mobile Apps*, arXiv 2607.18424 (julio 2026). Tradujeron OPP-115 y MAPP a las 24 lenguas
oficiales de la UE con eTranslation y validaron la traducción con métricas automáticas y
revisión de un experto legal. Su clasificador basado en LLM mantiene macro-F1 estable
entre 0,91 y 0,94 entre idiomas.

**Cuidado con ese número: no es comparable con el nuestro.** Su tarea es más estrecha
(identificar categorías de recogida de datos personales, no las nueve de OPP-115), usan
GPT-4o sin entrenamiento específico, y evalúan sobre texto traducido. Los propios
autores reconocen que no pueden separar del todo la calidad de la traducción del
rendimiento de clasificación.

Este trabajo es además evidencia de que la **ruta descartada (B)** —traducir el corpus
de entrenamiento— es viable con recursos suficientes. Material para el apartado de
trabajo futuro, no para esta entrega.

- [ ] **TODO:** elegir proveedor y comprobar cuotas, límites y **elegibilidad de
  acceso** de la capa gratuita.

## 6. Enfoque de modelado

- **≥4 modelos base diversos** (distintas familias y representaciones del texto) +
  un **meta-modelo por stacking** que aprende a combinarlos.
- **Por qué cuatro y diversos:** cuatro modelos que se equivocan en lo mismo no
  aportan más que uno. Lo que hace útil al ensamble es que fallen en cosas distintas.
  La diversidad importa más que la cantidad.
- El meta-modelo es trabajo del Sprint 2.

### 6.1 Criterio de terminado común de los cuatro modelos base

**El mismo texto se aplica a los issues #9, #23, #24 y #25.** Cuatro personas
trabajando por separado contra el mismo criterio producen cuatro resultados
comparables; sin criterio común producen cuatro cosas distintas.

> Un **script** en `models/` que carga los artefactos de `artifacts/`, entrena, evalúa
> contra `val`, y escribe su resultado con el formato de la tabla comparativa (#22).
> **No toca `test`.** Corre de arriba abajo sin errores.

Por qué script y no notebook: un notebook depende del orden en que se ejecutaron las
celdas y del estado de la memoria; otra persona lo abre y no obtiene lo mismo.

### 6.2 Reglas de la etapa de entrenamiento

1. **Nadie vuelve a partir los datos.** Se lee `split_assignment.csv` (§4.4).
2. **Nadie reentrena el vectorizador.** Se carga `tfidf_vectorizer.joblib` (§4.5).
3. **Nadie toca `test`.** Se trabaja contra `val`. **`test` se abre una sola vez, al
   final, con el equipo presente** — no es una tarea individual.

Estas reglas no son formalismo. El 24 de julio se detectó que `eda/04` calculaba una
partición propia con un `policy_id` fabricado (`np.arange(len(df))`), lo que producía
3.792 grupos de una fila en lugar de 115 políticas. El resultado era un reparto
aleatorio por fila —**con** group leakage— y una verificación que no podía fallar por
construcción. **El fallo no se detecta mirando las métricas**, solo mirando cómo se
partieron los datos.

Regla de código que sale de ahí: **un fallback que inventa datos es peor que un crash.**
Ante una columna que no se encuentra, `raise`, no `print` de advertencia.

### 6.3 Los cuatro modelos base (propuesta, pendiente de confirmar en la daily)

Elegidos por **diversidad de familia**: cada uno mira el texto de una forma distinta, así
que sus errores no coinciden y el meta-modelo tiene algo que combinar.

| # | Modelo | Familia | Representación | Respaldo |
|---|---|---|---|---|
| 1 | **LinearSVC** | Lineal, margen máximo | TF-IDF congelado | Ganó en Wilson 2016 y en Liu 2018 (sobre este corpus) |
| 2 | **ComplementNB** | Probabilístico | TF-IDF (o CountVectorizer) | Variante diseñada para clases desbalanceadas |
| 3 | **LightGBM** | Árboles / ensemble | TF-IDF | Captura combinaciones no lineales de palabras |
| 4 | **DeBERTa-v3-small** | Transformer | Embeddings propios | Único que lee orden y contexto; entiende negación y sinónimos |

La **regresión logística del baseline (§3.1) NO es uno de los cuatro**: se queda como
suelo de la tabla comparativa. Los cuatro huecos son modelos nuevos.

**Contexto de la literatura (issue #2):** el rango publicado de macro-F1 sobre OPP-115
con BERT es 65-76% (Mousavi Nejad et al. 2020). Nuestro baseline está en 74,66%. SVM es
el clásico más fuerte en este corpus; CNN es mala apuesta (perdió contra TF-IDF+SVM en
Liu et al.). Los transformers ganan, pero por poco (BERT +5% sobre el estado del arte
previo, XLNet +1-3% sobre BERT). **Aviso: los números entre papers no son comparables**
—varían el patrón de oro, la partición, el número de categorías y el nivel de análisis—
así que en el informe se cita el rango como referencia, no como meta exacta.

### 6.4 Regla de calibración: todo modelo base emite probabilidad por categoría

El semáforo (§7), el umbral multi-etiqueta (§2.3) y el contrato de salida (§9) necesitan
una **probabilidad** por categoría, no una etiqueta cruda. Por tanto:

> **Todo modelo base debe devolver una probabilidad por categoría. Si su algoritmo no la
> da de forma nativa, se calibra.**

- `LinearSVC` **no** da probabilidad (devuelve distancia al margen). Se envuelve en
  `CalibratedClassifierCV(method="sigmoid")`, que la deriva por validación cruzada
  **dentro de train** (no toca val ni test). Es una línea.
- `ComplementNB` y `LightGBM` la dan de forma nativa (`predict_proba`).
- El transformer da logits que se pasan por sigmoide; requiere
  `problem_type="multi_label_classification"`, que **no** es la configuración por defecto.

### 6.5 Requisitos de entorno (instalar HOY, no el lunes)

- Transformer: `uv add torch transformers` — son varios GB, con mala conexión es media
  mañana perdida si se deja para el lunes.
- Árboles: `uv add lightgbm`.
- SVM, NB y calibración: ya cubiertos por scikit-learn.

- [ ] **TODO:** confirmar los cuatro en la daily. El único hueco realmente en discusión
  es el #1 (LinearSVC frente a la LogisticRegression que ya es el baseline); los otros
  tres vienen de la propuesta del equipo.
- [ ] **TODO:** la investigación de literatura sobre OPP-115 (issue #2) sigue
  pendiente. **Si los cuatro se eligen sin ella, el informe no puede afirmar que la
  elección se basó en la literatura.** Se declara que fue por criterio propio.

## 7. Capa de exposición (el semáforo)

> **Esta capa NO sale del dataset.** OPP-115 dice qué prácticas describe una
> política (descriptivo), no si son buenas o malas. El semáforo es una capa propia
> del equipo, con reglas transparentes y justificables.

### 7.1 Principio: exposición ≠ cumplimiento

Una web puede cumplir el RGPD al 100% y aun así exponerte mucho: declara que
comparte tus datos con decenas de socios, que los retiene indefinidamente, y tú
"consientes". Un semáforo de *cumplimiento* pintaría eso verde.

**Nuestro semáforo mide exposición real de la privacidad**, no conformidad legal.
La pregunta que pesa cada categoría es *"¿por cuántas manos pasan mis datos, cuánto
tiempo se quedan, y me dejan control?"*, no *"¿es legal?"*.

### 7.2 Mecanismo: puntuación ponderada por impacto

Cada categoría detectada suma o resta puntos de exposición; el total cae en
bajo / medio / alto según unos umbrales.

| Dirección | Categorías | Razón |
|---|---|---|
| **Suben** | `third_party_sharing_collection` (fuerte), `first_party_collection_use`, `data_retention` | Los datos se esparcen o permanecen |
| **Bajan** | `data_security`, `user_choice_control`, `user_access_edit_deletion`, `do_not_track` | Protegen o devuelven control al usuario |
| **Contexto** (poco peso) | `policy_change`, `international_specific_audiences` | Informan, pero no cambian la exposición por sí solas |

**Ruta descartada:** reglas por simple presencia ("si aparece X → amarillo"). Más
simple, pero no gradúa: una web con una práctica dudosa pesaría igual que otra con
cinco.

> **⚠️ Contradicción abierta dentro de esta spec.** La tabla de arriba coloca
> `do_not_track` entre las categorías que **bajan** la exposición, pero el §13.2
> demuestra que la categoría es ciega a la polaridad: se activa igual cuando la web
> respeta la señal que cuando declara ignorarla. Con el peso actual, **el semáforo
> premiaría a una web por declarar que no respeta DNT.** Hay que resolverlo al fijar
> los pesos: sacar `do_not_track` del cálculo y mostrarla solo como información, o
> hacer que su dirección dependa del contenido del fragmento y no solo de la etiqueta.
> El mismo problema afecta en menor grado a `data_retention` (§13.2).

- [ ] **TODO:** fijar los pesos numéricos exactos y los umbrales de corte, y resolver
  la contradicción de `do_not_track` señalada arriba.

### 7.3 Limitación asumida (y declarada al usuario)

El modelo detecta **qué temas** trata una política, **no si los trata bien o mal**.
`data_retention` etiqueta igual un "borramos a los 30 días" que un "guardamos para
siempre"; que aparezca `do_not_track` puede significar que lo respetan o que no.
El detalle fino vive en los subatributos de OPP-115, que quedan fuera de alcance (§11).

Consecuencias que asumimos de forma explícita:

1. El semáforo es una **estimación por presencia de temas**, no una lectura cláusula
   por cláusula. La interfaz debe **decírselo al usuario** con claridad.
2. Las categorías que **suben** la exposición se pesan con **más confianza** que las
   que la bajan: que el tema aparezca no garantiza que la práctica sea buena.
3. Para compensar la caja negra, la salida incluye **qué fragmento activó qué
   categoría**, para que el usuario pueda juzgar por sí mismo (§9).

## 8. Capa RGPD (educativa, separada del semáforo)

El RGPD **no puntúa** el semáforo. Se muestra al lado, como contexto:
*"esta práctica se relaciona con el artículo X del RGPD — este es tu derecho"*.

**Por qué separada:** si el artículo sumara puntos, volveríamos a medir cumplimiento,
que es justo lo que decidimos no hacer (§7.1).

**Fuente:** el mapeo de Poplavska et al. (2020) del §1.2, publicado y auditable.
No se usa el campo de artículos RGPD de la extensión (§1.3), porque sale de un motor
de reglas léxicas y no de una tabla citable: no se podría defender ante una pregunta
de "¿de dónde sale que este párrafo es el artículo 28?".

- [ ] **TODO:** aplicar el mapeo descargado y fijar el artículo (o artículos) que se
  muestra para cada una de las nueve categorías, con texto explicativo para no
  juristas.

## 9. Contrato de salida del modelo

Este contrato lo consumen **tres** piezas: la API, la web PrivacyLens (React) y la
extensión de Chrome. Se define **completo desde el principio** para no tener que
rehacerlo cuando llegue la extensión.

**Este contrato es la pieza que permite construir en paralelo.** El backend se puede
montar HOY, sin modelo, devolviendo esta misma estructura con datos de un *stub* (una
función que inventa probabilidades). El día que exista el modelo, se reemplaza esa
función por `predict_proba`; la web nunca nota el cambio porque la forma de la respuesta
no varía. Lo que el stub decida ahora **es** el contrato: congelarlo es escribirlo.

Nivel de detalle acordado: **documento + fragmento**.

```json
{
  "model_version": "0.1.0",
  "document": {
    "source_language": "es",
    "translated": true,
    "exposure": {
      "level": "high",
      "score": 0.72,
      "disclaimer": "Estimación basada en los temas detectados, no en una lectura cláusula por cláusula."
    },
    "categories": [
      {
        "id": "third_party_sharing_collection",
        "present": true,
        "confidence": 0.91,
        "fragment_count": 7,
        "gdpr_reference": "TODO"
      }
    ],
    "fragment_count": 84
  },
  "fragments": [
    {
      "id": 12,
      "text": "Podemos compartir tu información con nuestros socios publicitarios.",
      "start": 4210,
      "end": 4276,
      "labels": [
        { "id": "third_party_sharing_collection", "score": 0.88 }
      ]
    }
  ]
}
```

Notas del contrato:

- Los **nombres de campo van en inglés**, según la convención de idioma del repo.
- `text`, `start` y `end` se refieren **siempre al documento original**, no a su
  traducción (§5, regla 1). Las posiciones son lo que permite a la extensión resaltar
  el párrafo en la página.
- `translated` indica si el fragmento pasó por el traductor, para poder desglosar
  métricas y avisar al usuario.
- El bloque `fragments` permite a la web y a la extensión resaltar el párrafo concreto.
  La web no está obligada a pintarlo en el MVP: el campo existe desde el principio, la
  interfaz lo muestra cuando dé tiempo.
- **Aviso de seguridad (§11.1):** el campo `text` es contenido no confiable (viene de una
  web externa). Si la web React lo resalta con `dangerouslySetInnerHTML` sin sanear, es
  XSS. Se sanea antes de renderizar.
- `confidence` a nivel de documento y `score` a nivel de fragmento salen de las
  probabilidades del modelo multi-etiqueta.

## 10. Qué muestra cada pieza

| Pieza | Muestra | Nivel |
|---|---|---|
| **Web PrivacyLens** (React + Vite) | Categorías detectadas + aviso de estimación + aviso si la traducción no está disponible | **Esencial** |
| **API** (backend) | El contrato completo del §9. La web la consume | **Esencial** (subió desde Avanzado) |
| **Informe técnico** | Métricas, macro-F1 global y por idioma, análisis de errores, límites | Esencial |
| **Semáforo** | Nivel de exposición bajo/medio/alto | Medio |
| **Búsqueda de política en footer** (scraping) | Acepta la URL de una web y localiza su política | Avanzado |
| **Extensión de Chrome** | Semáforo en la web visitada + resaltado por fragmento | Aspiracional |

El repo ya tiene `frontend/` (Vite + React + react-router-dom, producto **PrivacyLens**)
y `backend/` (aún solo un README). El stack de la API está por confirmar; si es FastAPI
vive en el mismo entorno `uv` que el modelo y cargar el artefacto es trivial.

## 11. Fuera de alcance

Queda **explícitamente fuera** de este proyecto:

- Leer los **subatributos** de OPP-115 (el detalle fino de cada práctica).
- Emitir juicios de **cumplimiento legal** o asesoramiento jurídico.
- **Idiomas distintos del inglés y el español.**
- **Entrenar con etiquetas generadas automáticamente** sin validación humana.
- Capa MLOps (Champion/Challenger, A/B testing, data drift, auto-reemplazo).
- Despliegue en la nube, Docker, CI/CD.
- **Hardening de seguridad de nivel producción.** Lo que SÍ entra está en §11.1; lo que
  queda fuera (rate limiting avanzado, WAF, pentesting, auth de usuarios) va al apartado
  de trabajo futuro del informe.

## 11.1 Seguridad como diseño (requisito del suelo, no mejora)

Decisión del 25 de julio: la seguridad se piensa **cuando se monta el backend**, no
después. Asegurar una API ya construida es la vía por la que se cuelan los fallos. Un
informe de revisión sobre el repo (25 jul) confirmó que **hoy no hay secretos
commiteados**; el resto son riesgos a prevenir al construir, no problemas presentes.

**Mínimos obligatorios del backend (parte del suelo protegido):**

| # | Requisito | Por qué | Estado |
|---|---|---|---|
| 1 | **Cero secretos en el repo.** Claves en `.env` (ignorado), `.env.example` versionado | Repo público | ✅ limpio hoy, mantener |
| 2 | **Límite de tamaño** del texto que entra a la API | Sin él, alguien manda 2 GB y tumba el backend | ❌ fijar en el issue de API |
| 3 | **CORS restringido** al origen de la web (Vite, `localhost:5173` en local), nunca `allow_origins=["*"]` | Un `*` deja que cualquier web llame a la API | ❌ al montar |
| 4 | **Saneo del texto renderizado** en la web (no `dangerouslySetInnerHTML` sin limpiar) | El `text` de los fragmentos viene de una web externa: XSS (§9) | ❌ al implementar el resaltado |

**Riesgos anticipados, a trabajo futuro del informe (no del suelo):**

- **SSRF** en la búsqueda de política por footer: seguir una URL dada por el usuario
  puede apuntar a una red interna. Cuando se implemente el scraper (Nivel Avanzado),
  validar el destino y limitar tamaño y tiempo de descarga.
- **Carga de `.joblib`:** `joblib.load` sobre un archivo malicioso ejecuta código. Hoy
  el riesgo es bajo (los artefactos los genera el propio equipo), pero si algún día se
  carga un modelo de origen externo, es una puerta abierta.

Para un proyecto de bootcamp, cubrir los cuatro mínimos cubre el grueso del riesgo real.
Lo demás se **nombra** en el informe como superficie identificada y priorizada, que ya
demuestra criterio.

## 12. Datos generados en el repositorio

**Norma:** se versiona **el script que genera** los datos, no su salida. Los datos
pequeños y citables (p. ej. el mapeo del RGPD, 83 KB) sí se versionan: son fuente,
no producto.

**Por qué:** git no sabe comparar archivos binarios, así que guarda cada versión
entera para siempre; y un pull request de 100.000 líneas no se revisa de verdad.

**Secuencia acordada** (el orden importa: hoy no existen scripts que regeneren los
artefactos, así que quitarlos ahora significaría perderlos):

1. Convertir los procesos existentes en scripts reproducibles.
2. Acordar la norma por escrito en `specs/`.
3. Solo entonces dejar de rastrear los archivos generados.

No se reescribe el historial del repositorio a mitad de sprint: obligaría a todo el
mundo a volver a clonar y rompería los pull requests abiertos.

### 12.1 Criterio operativo: regenerabilidad

**Si un script lo reconstruye idéntico, no se versiona. Si viene de una fuente que
cambia o desaparece, sí.**

| Archivo / carpeta | ¿Regenerable? | ¿Se versiona? |
|---|---|---|
| `training_table.csv` | Sí, script 02 | No |
| `split_assignment.csv` | Sí, script 04 | No |
| `artifacts/` (vectorizador y matrices) | Sí, script 05 | No — `artifacts/` va en `.gitignore` |
| `evaluation_{es,en}.csv` | Sí, script 03 | No |
| Mapeo RGPD de Poplavska (§1.2) | Sí, redescargable, y es **fuente citable** | **Sí** |
| Artefactos de los agentes de recogida | **No** — proceden de webs vivas que cambian | **Sí** |
| `MAPP_Corpus` (§1.4) | Sí, redescargable de CMU, y **descartado** | **No** |
| `__MACOSX/`, `.DS_Store` | Basura del sistema, sin datos | **No** |

**El paso 1 de la secuencia de arriba ya está cumplido:** los scripts 01-05 existen y
regeneran todo lo regenerable. Queda ejecutar el paso 3 sobre MAPP y la basura de macOS
(`scripts/34_untrack_external.sh`, issue #34).

**Aviso técnico importante.** Añadir una ruta al `.gitignore` **no deja de rastrear lo
que ya estaba rastreado**: hace falta `git rm -r --cached`. El intento anterior quedó
"preparado sin ejecutar", y el resultado fue que el 24 de julio esos archivos bloquearon
un merge entre ramas. **Le pasará a cualquiera que tenga una rama creada antes de que se
ejecute.** Salida: mover la carpeta fuera del repo y volver a mergear.

**Nota de licencia, a mirar antes de la entrega.** El repositorio es público y las
anotaciones de estos corpus se ceden solo para investigación y docencia, con licencia
comercial aparte para algunos archivos. En un proyecto sobre cumplimiento normativo
conviene no dejar la pregunta sin revisar. Retirar MAPP la resuelve de forma trivial.

## 13. Limitaciones conocidas

Se declaran aquí porque van al informe y a la defensa. Un límite explicado se
defiende; uno descubierto por el tribunal, no.

### 13.1 `do_not_track`: estándar discontinuado, mención obligatoria por ley

**Verificado:** el W3C cerró el grupo de trabajo de Tracking Protection el **17 de
enero de 2019**, por falta de despliegue y sin indicios de soporte previsto en el
ecosistema. Apple retiró DNT de Safari calificándolo de estándar expirado.

**Pero la mención persiste en las políticas por obligación legal:** la **CalOPPA**,
enmendada por la **AB 370** (vigente desde el 1 de enero de 2014), exige a los
operadores de webs y apps declarar **cómo responden** a la señal. La ley no obliga a
respetarla, solo a informar. Fuente primaria a citar en el informe:
**Cal. Bus. & Prof. Code § 22575(b)(5)** y la guía de la Fiscalía General de California.

**Frecuencias medidas en nuestros datos** (presencia del término en el texto):

| Corpus | Con el término | Total | % |
|---|---|---|---|
| OPP-115 (2016) | 35 | 3.792 | 0,92% |
| Nuestra muestra en inglés (2026) | 4 | 1.978 | 0,20% |
| Nuestra muestra en español (2026) | 0 | 5.385 | 0,00% |

**Lo que NO se afirma.** No se afirma que DNT sea obsoleto en la web actual. Dos
razones: (a) ninguna de nuestras dos muestras es representativa del universo de
políticas — OPP-115 es una selección de 2016 y nuestra extensión es una muestra de
conveniencia; (b) la baja frecuencia en español se explica igual de bien por
**jurisdicción** que por el paso del tiempo: las políticas en español no van dirigidas
a residentes de California y por tanto no tienen obligación CalOPPA. Es una variable
confusora.

Además, la **deduplicación exacta** aplicada a nuestro corpus pudo reducir la
frecuencia observada, precisamente porque estos fragmentos son texto formulaico que se
copia literalmente entre sitios.

**Redacción admisible para el informe:** *"El estándar DNT fue discontinuado por el W3C
en enero de 2019. Su mención en políticas persiste por obligación legal (CalOPPA, AB
370). En nuestra muestra en español la categoría no aparece, lo que atribuimos a que
estas políticas no están sujetas a CalOPPA. No afirmamos nada sobre la prevalencia
general de DNT en la web actual."*

**Trabajo futuro:** el sucesor del DNT es el **Global Privacy Control (GPC)**, con
reconocimiento legal en algunas jurisdicciones. Un modelo entrenado sobre un corpus de
2016 no puede detectarlo.

### 13.2 Las categorías son ciegas a la polaridad

`data_retention` etiqueta igual "borramos a los 30 días" que "guardamos para siempre".
Y estos dos párrafos reciben la **misma** etiqueta `do_not_track`:

- *"Honramos las señales Do Not Track de tu navegador."* → lo mejor que puede decir una web
- *"No respondemos a las señales Do Not Track."* → lo peor

**Consecuencia directa para el semáforo (§7.2): ningún peso fijo para `do_not_track` es
correcto.** Si se le da dirección "baja la exposición", se premia a las webs que
declaran abiertamente que la ignoran. Si se le da "sube", se penaliza a las que la
respetan. Es el caso más limpio del principio *exposición ≠ cumplimiento* (§7.1), y
está pendiente de resolver en el §7.2.

### 13.3 Cobertura desigual del español

`do_not_track` tiene **1 sola fila etiquetada** en el conjunto de evaluación en español.
No se puede verificar manualmente ni medir su rendimiento en español. La sesión de
verificación (§4.3) se concentra en las categorías con volumen real y esto se declara.

### 13.4 Categorías semánticamente difusas

En el baseline (§3.1), las dos peores no son las escasas sino `user_choice_control`
(F1 0,61, con 103 ejemplos en validación) y `user_access_edit_deletion` (0,59, con 39).
`data_retention`, con solo 22, saca 0,70. **La escasez no es la única causa del bajo
rendimiento**; hay indicios de solape semántico entre esas dos categorías.

Precisión metodológica: la matriz de **co-ocurrencia** del #49 **no** confirma esta
hipótesis, y no es el test adecuado. Co-ocurrir (aparecer en el mismo fragmento) y
confundirse (compartir vocabulario sin aparecer juntas) son cosas distintas; la segunda
es la que hunde el F1 y solo se ve analizando los errores del modelo. Queda para el
análisis de errores del informe.

### 13.5 Calidad de la segmentación heredada del corpus

Existen fragmentos de **1 sola palabra** (mínimo de la distribución del #50) y
fragmentos con **8 de las 9 categorías** simultáneas (#49). Los dos extremos sugieren
que el criterio de segmentación de OPP-115 no es uniforme. No bloquea el modelado y no
se corrige, pero se declara.

## 14. Criterios de cierre por nivel

**Esencial (suelo protegido):** dataset documentado · EDA con visualizaciones ·
preprocesado reproducible · clasificador multi-etiqueta de las nueve categorías
funcionando · macro-F1 con gap train/validación <5% · español vía traducción con
degradación elegante · conjunto de prueba en español validado a mano · demo en
web PrivacyLens + API · informe técnico · README ejecutable sin necesidad de claves.

**Medio:** capa de exposición implementada y justificada · ≥4 modelos base +
meta-modelo por stacking.

**Avanzado:** mapeo RGPD integrado en la salida · API sirviendo el contrato del §9.

**Aspiracional:** extensión de Chrome · presentaciones pulidas.

---

## 15. Pendientes (TODO)

### Cerrados el 24 de julio

- [x] Pipeline de **preprocesado y vectorización** (§4.5, issue #8).
- [x] **Partición** train/val/test por política con semilla fija (§4.4, issue #18).
- [x] **Deduplicación** del conjunto de evaluación (§1.3, issue #33).
- [x] **Umbral de consolidación** de anotaciones: 0.75 (§2.2.1).
- [x] **Mapeo RGPD descargado** y localizado en el repo (§1.2, issue #32).
- [x] **EDA** de las nueve categorías, multi-etiqueta, longitudes y clases raras
      (§4.6, issues #48-#51).
- [x] **`do_not_track` se mantiene** dentro de las nueve categorías, sin regla especial:
      el baseline le saca F1 0,91 con 20 ejemplos de entrenamiento (§3.1). Quedan
      descartadas las propuestas de excluirla del target o del macro-F1.

### Bloquean el entrenamiento (decisión de equipo, urgente)

- [ ] Confirmar los **cuatro modelos base** propuestos en §6.3 y el **dueño de cada uno**
      (issues #2, #1). El único hueco en discusión es el #1 (LinearSVC vs LogReg).
- [ ] Instalar hoy `torch transformers` y `lightgbm` (§6.5): con mala conexión, dejarlo
      para el lunes cuesta media mañana.
- [ ] **Formato de la tabla comparativa** (issue #22): modelo, dueño, macro-F1,
      micro-F1, **F1 por cada una de las nueve categorías**, gap train/val, tiempo.
      La columna de F1 por categoría no es opcional: es la que hizo visibles los
      hallazgos de los §13.2 y §13.4.
- [ ] Adoptar el **criterio de terminado común** del §6.1 en los cuatro issues.

### Necesitan un modelo entrenado antes

- [ ] **Umbral** de decisión multi-etiqueta, ajustado contra `val` (§2.3).
- [ ] **Pesos y umbrales** del semáforo, y resolver la contradicción de `do_not_track`
      (§7.2, §13.2).
- [ ] **Validación de la premisa inglés→español**: traducir el conjunto de evaluación
      en español una sola vez por lotes, pasarlo por el modelo y comparar el macro-F1
      con el obtenido en inglés. **Es un go/no-go de arquitectura**: si la traducción
      degrada mucho, cambia el producto. Se hace con el primer modelo disponible, no al
      final.

### Sin bloqueos, pendientes de hacer

- [ ] **Investigación de literatura sobre OPP-115** (issue #2): qué modelos se han
      probado y **qué macro-F1 se considera bueno en este corpus**. Sin la segunda
      cifra, el equipo no puede interpretar sus propios resultados.
- [ ] **Mapeo RGPD** categoría → artículo + texto para no juristas (§8, issue #7).
      Los CSV ya están en el repo (§1.2).
- [ ] **Proveedor de traducción**, cuotas y elegibilidad de acceso (§5).
- [ ] **Cómo etiquetar** el conjunto de prueba en español (§4.3).
- [ ] Ejecutar el destracking del §12.1 (issue #34).
- [x] ~~Que `eda/04` lea `split_assignment.csv`~~ — hecho el 25 de julio (PR #58): ahora
      lee la partición oficial, audita el leakage contra ella y lanza `raise` si falta
      el archivo o una columna. El `eda/README.md` quedó desactualizado describiendo el
      comportamiento viejo: corregirlo.
- [ ] Ratificar el **idioma** de las specs.
- [ ] **Contrato de salida** (§9): congelar montando el backend con *stub*. Es lo que
      desbloquea al frente de producto (issue #19) y se puede hacer sin modelo.
- [ ] **Mínimos de seguridad del backend** (§11.1): fijar límite de tamaño y CORS en el
      issue de la API antes de aceptar texto externo.
- [ ] Cerrar el issue **#20** (Streamlit): sin objeto tras el cambio a React.
- [ ] Corregir `eda/README.md`, `scripts/README.md` (solo documenta 01-02 de seis
      scripts) y `models/README.md` (plantilla vacía).

## 16. Historial de cambios

### Cambios respecto a la versión 0.3 (25 de julio de 2026)

- **§6.3-6.5 nuevos:** los cuatro modelos base con nombre (LinearSVC, ComplementNB,
  LightGBM, DeBERTa-v3-small), la regla de que todo modelo emite probabilidad calibrada,
  y los requisitos de entorno a instalar hoy. Incluye el contexto de literatura del #2.
- **Streamlit eliminado** de §9 y §10, sustituido por la web React (PrivacyLens) y la
  API. La API sube a Esencial.
- **§9:** el contrato se congela montando el backend con un *stub*, sin esperar al
  modelo. Añadido el aviso de XSS sobre el campo `text`.
- **§11.1 nuevo: seguridad como diseño**, con cuatro mínimos obligatorios del backend
  como parte del suelo, y SSRF/joblib anotados como trabajo futuro.
- **§15:** marcado `eda/04` como resuelto (PR #58); añadidos los pendientes de
  seguridad, entorno y limpieza de READMEs.

### Cambios respecto a la versión 0.2 (24 de julio de 2026)

**Correcciones de datos ya escritos:**

- §1.3: los números eran previos a deduplicar. Actualizados a 7.363 párrafos
  (5.385 es / 1.978 en). El dato "`Do Not Track` con 9 ejemplos" era de la preanotación
  antes de deduplicar y **se usó por error como si fuera una medición**; ahora está
  medido y contextualizado.
- §1.3: registrada la corrección de metadatos (`evaluation_file`, `labels_status`).
- §7.2: marcada una **contradicción interna** entre el peso asignado a `do_not_track` y
  el §13.2.

**Añadido:**

- §1.2: ubicación real del mapeo RGPD en el repo y alcance del mapeo publicado.
- §1.4: **MAPP evaluado y descartado**, con motivos. El principal es de dominio (apps
  frente a webs), no de idioma.
- §2.2: las 520 filas sin etiqueta (13,7%) y su efecto sobre la lectura de métricas.
- §2.2.1: **umbral de consolidación 0.75**.
- §3.1: **baseline de referencia, macro-F1 0,7466**, con F1 por categoría.
- §4.4: **la partición ejecutada y verificada** (semilla 42, 70/15/15, 80/17/18).
- §4.5: **la vectorización común congelada** y sus artefactos.
- §4.6: los resultados del EDA de los cuatro sub-issues.
- §6.1: **criterio de terminado común** de los cuatro modelos base.
- §6.2: las tres reglas de la etapa de entrenamiento, con el caso real que las motiva.
- §5: candidatos de proveedor de traducción, con el argumento de privacidad a favor de
  la opción local.
- §12.1: **criterio de regenerabilidad** con la tabla de qué se versiona y qué no, y el
  aviso de que `.gitignore` no destrackea lo ya rastreado.
- **§13 nuevo: limitaciones conocidas** (DNT y CalOPPA, ceguera a la polaridad,
  cobertura del español, categorías difusas, calidad de la segmentación).

### Cambios respecto a la versión 0.1

- Añadido §1.3: la extensión del dataset, su rol acordado (evaluación y demo) y sus
  características a tener en cuenta.
- Añadido §1.2 con la fuente concreta del mapeo RGPD, ya localizada.
- Nuevo §5: idiomas. El español entra vía traducción en la inferencia, con reglas de
  implementación (traducción interna, degradación elegante, caché, credenciales).
- Nuevo §4.2 (deduplicación) y §4.3 (conjunto de prueba en español).
- Nuevo §12: norma de datos generados en el repositorio, con la secuencia a seguir.
- §9: el contrato ahora devuelve **posiciones del texto original** y campos de idioma.
  TODO de "texto vs. posición" cerrado.
- §11: el español sale de "fuera de alcance"; entra la prohibición de entrenar con
  etiquetas sin validar.
- Añadidas las rutas descartadas y su motivo en §2.1, §5, §7.2 y §8.
