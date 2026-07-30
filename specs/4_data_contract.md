# SPEC 4 — Contrato de datos

## 1. Tabla multietiqueta

`data/processed/training_table.csv` contiene 3.792 filas.

Columnas:

- `policy`: identificador de política.
- `segment`: posición del fragmento.
- `text`: texto en inglés.
- Nueve columnas binarias, en este orden:

```text
first_party_collection_use
third_party_sharing_collection
user_choice_control
user_access_edit_deletion
data_retention
data_security
policy_change
do_not_track
international_specific_audiences
```

La clave natural es `(policy, segment)`. Las filas con nueve ceros son válidas.

## 2. Partición

`data/processed/split_assignment.csv` contiene:

```text
policy, segment, split
```

Valores de `split`: `train`, `val`, `test`.

Distribución congelada:

| Split | Filas | Políticas |
|---|---:|---:|
| train | 2.550 | 80 |
| val | 579 | 17 |
| test | 663 | 18 |

La unión con la tabla se hace por ambas columnas y debe validarse como uno a uno.

## 3. Artefactos TF-IDF actuales

| Archivo | Descripción |
|---|---|
| `tfidf_vectorizer.joblib` | Vectorizador ajustado con train |
| `X_train.npz` | Features de entrenamiento |
| `X_val.npz` | Features de validación |
| `X_test.npz` | Features reservadas de test |
| `y_train.npy` | Nueve targets binarios |
| `y_val.npy` | Nueve targets binarios |
| `y_test.npy` | Targets reservados |
| `linear_svc_model.joblib` | Modelo multietiqueta generado |

## 4. Evaluación externa

`evaluation_es.csv` y `evaluation_en.csv` se generan desde `data/dataset_extension/`. No pertenecen a train, validación ni test de OPP-115.

Las etiquetas de la extensión son automáticas y requieren revisión humana antes de utilizarlas como referencia de calidad.

## 5. Target multiclase

`scripts/10_build_multiclass_target.py` puede crear:

```text
policy, segment, label, split
```

El target usa prioridad explícita para resolver fragmentos multietiqueta y añade `Other`. Este archivo no está presente actualmente en `data/processed/`; debe generarse antes de ejecutar los modelos multiclase.

## 6. Reglas obligatorias

1. No crear una nueva partición.
2. No ajustar TF-IDF con validación o test.
3. No usar test para elegir hiperparámetros o modelo.
4. No incorporar `dataset_extension` al entrenamiento.
5. No inventar columnas o valores ausentes.
6. Comprobar alineación de filas y formas antes de entrenar.
7. No usar una `y` multiclase con un modelo multietiqueta ni viceversa.

## 7. Carga recomendada

```python
import pandas as pd

table = pd.read_csv("data/processed/training_table.csv")
split = pd.read_csv("data/processed/split_assignment.csv")
data = table.merge(split, on=["policy", "segment"], validate="one_to_one")

train = data[data["split"] == "train"]
validation = data[data["split"] == "val"]
```
