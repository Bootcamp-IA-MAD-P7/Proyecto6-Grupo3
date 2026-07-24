# SPEC 4 — Contrato de datos

**Proyecto:** Clasificador de políticas de privacidad — Proyecto 6, Grupo 3
**Versión:** 1.0 (24 de julio de 2026)

> Este documento existe para **una** cosa: que cualquiera del equipo pueda pegar el
> bloque de abajo en su asistente de IA y obtenga código que encaje con el resto del
> proyecto, sin tener que explicar nada.
>
> El detalle y el *por qué* de cada decisión están en `2_spec` §4.4, §4.5 y §6.2. Aquí
> solo está el *qué*, en formato copiable.
>
> **Si algo de aquí cambia, se cambia en `2_spec` primero y luego se refleja aquí.**
> Este archivo es un resumen operativo, no una fuente de verdad paralela.

---

## Por qué hace falta

El 24 de julio dos personas escribieron código contra la misma tabla asumiendo nombres
de columna distintos, y una tercera pieza calculó su propia partición de los datos. En
los tres casos el motivo fue el mismo: **el contrato existía en la cabeza de alguien,
no en un archivo.**

Y hay un motivo específico de trabajar con asistentes de IA: ante una tarea de
clasificación, cualquier IA escribe `train_test_split(df, test_size=0.2)` por defecto,
porque es lo que aparece en todos los tutoriales. Eso destruiría la partición agrupada
del proyecto sin que nadie lo note, porque **el error no se ve en las métricas** — se
ve mejores métricas, que es peor.

---

## Bloque para pegar en tu IA

```
CONTEXTO DEL PROYECTO
Clasificación multi-etiqueta de fragmentos de políticas de privacidad en 9
categorías. Corpus OPP-115 (115 políticas en inglés, 3792 fragmentos, anotadas
por juristas). Entorno: uv + Python 3.12. Ejecutar siempre con `uv run python ...`
desde la raíz del repo.

ENTRADA 1 — data/processed/training_table.csv
3792 filas, 12 columnas:
  policy    id de la política, formato "1017_sci-news.com". 115 valores únicos.
  segment   posición del fragmento dentro de su política.
  text      el texto del fragmento (inglés).
  + 9 columnas de etiqueta con valores 0/1, en este orden:
      first_party_collection_use
      third_party_sharing_collection
      user_choice_control
      user_access_edit_deletion
      data_retention
      data_security
      policy_change
      do_not_track
      international_specific_audiences

  La clave única de cada fila es la pareja (policy, segment). NO hay columna
  policy_id ni policy_name ni fragment_id. No la inventes: si tu código necesita
  la política, es `policy`.

  520 filas (13.7%) tienen las 9 etiquetas a cero. Son correctas y entran al
  entrenamiento: son texto que no trata de ninguna de las 9 categorías.

ENTRADA 2 — data/processed/split_assignment.csv
3792 filas, 3 columnas: policy, segment, split
  split toma exactamente estos valores en minúsculas: train / val / test
  Se une a training_table por la pareja (policy, segment).
  Reparto: train 2550 filas (80 políticas), val 579 (17), test 663 (18).

ENTRADA 3 — artifacts/  (generado por scripts/05_vectorize.py, no versionado)
  tfidf_vectorizer.joblib     vectorizador TF-IDF ya entrenado
  X_train.npz / X_val.npz / X_test.npz    matrices dispersas scipy, 13389 columnas
  y_train.npy / y_val.npy / y_test.npy    matrices 0/1 de N filas x 9 columnas

REGLAS NO NEGOCIABLES
1. NO vuelvas a partir los datos. No uses train_test_split, GroupShuffleSplit,
   KFold ni ninguna variante. La partición ya existe: se lee de
   split_assignment.csv. Si tu propuesta incluye partir los datos, está mal.
2. NO reentrenes el vectorizador. Se carga con joblib desde
   artifacts/tfidf_vectorizer.joblib. Si necesitas hacer fit de algo, hazlo
   SOLO sobre las filas de train.
3. NO uses el conjunto test. Se evalúa contra val. test se abre una sola vez
   al final del proyecto.
4. Ante un archivo o columna que no encuentres, lanza una excepción (raise).
   NO generes un valor de reemplazo ni sigas con un aviso: un fallback que
   inventa datos produce resultados falsos que parecen correctos.
5. Todo lo que va al repo se escribe en inglés: nombres de archivo, variables,
   funciones, columnas, ramas y mensajes de commit. Los comentarios explicativos
   y la documentación pueden ir en español.

MÉTRICA
La métrica que manda es macro-F1 (promedia las 9 categorías por igual). Se
reporta siempre junto al F1 por categoría. El desbalance es 47:1 entre la
categoría más frecuente (first_party_collection_use, 1521 filas) y la menos
frecuente (do_not_track, 32).

Baseline de referencia ya existente: macro-F1 0.7466 en validación, con
OneVsRest + LogisticRegression(class_weight="balanced") sobre estos artefactos.
```

---

## Cómo cargar los datos (patrón correcto)

```python
import pandas as pd

TRAINING_TABLE = "data/processed/training_table.csv"
SPLIT_ASSIGNMENT = "data/processed/split_assignment.csv"

LABEL_COLS = [
    "first_party_collection_use",
    "third_party_sharing_collection",
    "user_choice_control",
    "user_access_edit_deletion",
    "data_retention",
    "data_security",
    "policy_change",
    "do_not_track",
    "international_specific_audiences",
]

df = pd.read_csv(TRAINING_TABLE)
split = pd.read_csv(SPLIT_ASSIGNMENT)

# validate="one_to_one" hace que pandas grite si hay claves duplicadas
# o que no cruzan, en lugar de multiplicar filas en silencio.
data = df.merge(split, on=["policy", "segment"], validate="one_to_one")

train = data[data["split"] == "train"]
val = data[data["split"] == "val"]
```

## Cómo cargar los artefactos (patrón correcto)

```python
import joblib
import numpy as np
from scipy import sparse

vectorizer = joblib.load("artifacts/tfidf_vectorizer.joblib")   # cargar, no entrenar

X_train = sparse.load_npz("artifacts/X_train.npz")
y_train = np.load("artifacts/y_train.npy")
X_val = sparse.load_npz("artifacts/X_val.npz")
y_val = np.load("artifacts/y_val.npy")
```

## Antipatrones — si tu código hace esto, está mal

```python
# ❌ Vuelve a partir los datos. Rompe la comparabilidad entre los cuatro modelos.
X_tr, X_te = train_test_split(X, test_size=0.2, random_state=42)

# ❌ Reentrena el vectorizador. Produce un vocabulario distinto al de los demás.
vec = TfidfVectorizer().fit(df["text"])

# ❌ fit sobre el total. Mete vocabulario de test en el modelo (leakage).
vec.fit(data["text"])

# ❌ Evalúa contra test. Invalida la cifra final del informe.
score = f1_score(y_test, model.predict(X_test), average="macro")

# ❌ Fallback que inventa datos. Este exacto produjo 3792 "políticas"
#    en lugar de 115, y una verificación de leakage que no podía fallar.
if "policy_id" not in df.columns:
    df["policy_id"] = np.arange(len(df))
```

---

## Orden de los scripts

| Script | Produce | Issue |
|---|---|---|
| `scripts/01_inspect_opp115.py` | inspección del corpus | #5 |
| `scripts/02_build_target.py` | `training_table.csv` | #31 |
| `scripts/03_prepare_evaluation_set.py` | `evaluation_{es,en}.csv` | #33 |
| `scripts/04_build_split.py` | `split_assignment.csv` | #18 |
| `scripts/05_vectorize.py` | `artifacts/` | #8 |
| `scripts/06_smoke_test.py` | baseline de referencia | — |
| `models/*` | un modelo base por persona | #9, #23, #24, #25 |

## Flujo de trabajo diario

```bash
git pull            # traer el trabajo del equipo
uv sync             # sincronizar el entorno con uv.lock
uv add <paquete>    # añadir una dependencia (commitea pyproject.toml Y uv.lock)
uv run python ...   # ejecutar cualquier cosa
```

Nunca `pip install` ni `python` a secas: eso te saca del entorno del proyecto y tu
código deja de funcionar en los portátiles del resto.
