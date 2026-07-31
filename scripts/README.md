# Scripts del proyecto

Los scripts se ejecutan desde la raíz con `uv run python`. Los pasos de generación escriben en `data/processed/`, `artifacts/` o `reports/`.

## Pipeline principal multietiqueta

| Orden | Script | Lee | Produce |
|---:|---|---|---|
| 1 | `01_inspect_opp115.py` | Corpus OPP-115 | Solo salida por consola |
| 2 | `02_build_target.py` | Anotaciones y textos OPP-115 | `data/processed/training_table.csv` |
| 3 | `03_prepare_evaluation_set.py` | `data/dataset_extension/` | `evaluation_es.csv`, `evaluation_en.csv` |
| 4 | `04_build_split.py` | `training_table.csv` | `split_assignment.csv` |
| 5 | `05_vectorize.py` | Tabla y split | Vectorizador, matrices X y matrices y |
| 6 | `06_smoke_test.py` | X/y de train y validación | Métricas por consola |

Orden reproducible.

```bash
uv run python scripts/01_inspect_opp115.py
uv run python scripts/02_build_target.py
uv run python scripts/03_prepare_evaluation_set.py
uv run python scripts/04_build_split.py
uv run python scripts/05_vectorize.py
uv run python scripts/06_smoke_test.py
```

`03_prepare_evaluation_set.py` no incorpora `dataset_extension` al entrenamiento, genera conjuntos externos separados.

## Pipeline multiclase

Alimenta el modelo que sirve la API en producción, `backend/app/predictor.py` carga el artefacto que resulta de esta rama, no de la multietiqueta.

| Script | Función |
|---|---|
| `10_build_multiclass_target.py` | Deriva una clase única y `Other`, produce `multiclass_target.csv` |
| `check_alignment.py` | Comprueba alineación entre tablas, split y matrices |

Después del target pueden ejecutarse `models/11_multiclass_baseline.py` y `models/12_multiclass_compare.py`, este último es el que genera el artefacto que carga el backend.

## Scripts auxiliares

Los archivos `.sh` son utilidades históricas de coordinación o mantenimiento del repositorio. No forman parte del pipeline de datos ejecutado por la aplicación.

## Reglas

- No vuelva a dividir los datos, use `split_assignment.csv`.
- Ajuste TF-IDF únicamente con train.
- No use test durante selección de modelos.
- La pareja `(policy, segment)` es la clave natural.
- Si falta una entrada, el pipeline debe fallar, no invente valores.
