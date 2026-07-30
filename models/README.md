# Modelos de PrivacyLens

Scripts de experimentación sobre OPP-115. Conviven dos enfoques distintos y no deben confundirse.

## Enfoque multietiqueta

Cada fragmento puede tener varias de las nueve etiquetas oficiales.

| Archivo | Modelo | Entrada principal |
|---|---|---|
| `linear_svc.py` | One-vs-rest LinearSVC, búsqueda de hiperparámetros y predicción de texto | Artefactos TF-IDF |
| `02_complement_nb.py` | ComplementNB por etiqueta | Artefactos TF-IDF |
| `03_lightgbm.py` | LightGBM por etiqueta | Tabla, split y artefactos |
| `04_deberta.py` | DeBERTa-v3-small | Texto crudo y split |
| `metrics.py` | Métricas compartidas | Etiquetas y predicciones |

La métrica principal documentada es macro-F1, acompañada de micro-F1, resultados por etiqueta y gap train-validación. El conjunto test está reservado para la evaluación final.

## Enfoque multiclase experimental

`scripts/10_build_multiclass_target.py` deriva una sola clase de las nueve etiquetas mediante prioridad y añade `Other`.

| Archivo | Función |
|---|---|
| `11_multiclass_baseline.py` | Baseline LogisticRegression |
| `12_multiclass_compare.py` | Compara LogisticRegression, LinearSVC y ComplementNB |

La comparación usa únicamente train y validación. Guarda `reports/multiclass_comparison.csv` y un modelo `artifacts/multiclass_<modelo>.joblib` cuando se ejecuta.

Resultados actualmente versionados:

| Modelo | Accuracy val | Macro-F1 val | Gap macro-F1 |
|---|---:|---:|---:|
| LogisticRegression | 0.7202 | 0.7121 | 0.1899 |
| LinearSVC | 0.7237 | 0.7054 | 0.2796 |
| ComplementNB | 0.7461 | 0.7118 | 0.1778 |

El selector considera empate técnico una diferencia de macro-F1 inferior a `0.01` y desempata por menor gap; con estos resultados elige ComplementNB. El artefacto multiclase no está presente en esta rama ni conectado al backend.

## Ejecución

Desde la raíz:

```bash
uv run python models/linear_svc.py
uv run python models/02_complement_nb.py
uv run python models/03_lightgbm.py
uv run python models/04_deberta.py

uv run python scripts/10_build_multiclass_target.py
uv run python models/11_multiclass_baseline.py
uv run python models/12_multiclass_compare.py
```

Revise el encabezado de cada script antes de ejecutarlo: entrenar modelos puede sobrescribir reportes o artefactos generados. No mezcle targets multietiqueta y multiclase.
