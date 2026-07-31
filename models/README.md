# Modelos de PrivacyLens

Scripts de experimentación sobre OPP-115. Conviven dos enfoques distintos y no deben confundirse.

## Enfoque multietiqueta

Cada fragmento puede tener varias de las nueve etiquetas oficiales. Este enfoque queda documentado y comparado aquí, pero no es el que sirve la API en producción.

| Archivo | Modelo | Entrada principal |
|---|---|---|
| `linear_svc.py` | One-vs-rest LinearSVC, búsqueda de hiperparámetros y predicción de texto | Artefactos TF-IDF |
| `02_complement_nb.py` | ComplementNB por etiqueta | Artefactos TF-IDF |
| `03_lightgbm.py` | LightGBM por etiqueta | Tabla, split y artefactos |
| `04_deberta.py` | DeBERTa-v3-small | Texto crudo y split |
| `metrics.py` | Métricas compartidas | Etiquetas y predicciones |

La métrica principal documentada es macro-F1, acompañada de micro-F1, resultados por etiqueta y gap train-validación. El conjunto test está reservado para la evaluación final. `04_deberta.py` usa `transformers` y `torch`, dependencias del extra opcional `training` de `pyproject.toml`, no instaladas por defecto.

## Enfoque multiclase, en producción

`scripts/10_build_multiclass_target.py` deriva una sola clase de las nueve etiquetas mediante prioridad y añade `Other`, sobre `data/processed/multiclass_target.csv`.

| Archivo | Función |
|---|---|
| `11_multiclass_baseline.py` | Baseline LogisticRegression |
| `12_multiclass_compare.py` | Compara LogisticRegression, LinearSVC y ComplementNB, guarda el artefacto ganador |

La comparación usa únicamente train y validación. Guarda `reports/multiclass_comparison.csv` y un modelo `artifacts/multiclass_<modelo>.joblib` cada vez que se ejecuta.

Resultados versionados.

| Modelo | Accuracy val | Macro-F1 val | Gap macro-F1 |
|---|---:|---:|---:|
| LogisticRegression | 0.7202 | 0.7121 | 0.1899 |
| LinearSVC | 0.7237 | 0.7054 | 0.2796 |
| ComplementNB | 0.7461 | 0.7118 | 0.1778 |

El selector considera empate técnico una diferencia de macro-F1 inferior a `0.01`, y desempata por menor gap. Con estos resultados elige ComplementNB. Ese artefacto, `artifacts/multiclass_complementnb.joblib`, es el que carga `backend/app/predictor.py` en producción, junto con `artifacts/tfidf_vectorizer.joblib`.

## Evaluación final

`models/14_evaluate_test_and_extension.py` corre el modelo de producción, el mismo artefacto que carga el backend, contra dos conjuntos que ninguno de los scripts anteriores toca. Escribe `reports/test_evaluation.json` y `reports/dataset_extension_evaluation.json`.

**OPP-115, split test, 663 filas.** Primera vez que este conjunto se usa para algo, `12_multiclass_compare.py` solo compara con train y validación. Accuracy 0,6968, macro-F1 0,6753. Algo por debajo de los valores en validación de la tabla de arriba, 0,7461 y 0,7118, una caída moderada y esperable, no hay señal de que el modelo se haya sobreajustado a validación al elegirlo.

**dataset_extension, 7.363 filas, español e inglés.** Esta comparación no es equivalente a la anterior, y no debe leerse como accuracy contra ground truth. Las etiquetas de `evaluation_es.csv` y `evaluation_en.csv` son preanotación automática por reglas, `label_source=silver_rules_not_validated`, así que el número mide el acuerdo entre el modelo entrenado y un clasificador de reglas distinto, no una medición sobre anotación humana. El interés de correrlo es ver cómo reacciona el modelo, entrenado sobre políticas de 2016, a vocabulario y prácticas de políticas de 2025-2026.

| Subconjunto | Filas | Accuracy | Macro-F1 |
|---|---:|---:|---:|
| Inglés | 1.978 | 0,3352 | 0,3473 |
| Español, sin traducir | 5.385 | 0,2806 | 0,0922 |
| Español, traducido con Google Cloud Translation | 5.385 | 0,2448 | 0,2266 |

El español sin traducir cae justo en el rango de ruido que describe el docstring de `backend/app/translation.py`, el vectorizador TF-IDF está en inglés y casi no reconoce vocabulario español. Traducir antes de clasificar más que duplica el macro-F1, de 0,0922 a 0,2266, aunque sigue lejos del inglés o del test de OPP-115, lo que queda después de traducir es la diferencia real de vocabulario y prácticas entre 2016 y 2025-2026, no un problema de idioma.

No vuelva a ejecutar la parte de traducción de este script sin necesidad.

## Ejecución

Desde la raíz.

```bash
uv run python models/linear_svc.py
uv run python models/02_complement_nb.py
uv run python models/03_lightgbm.py
uv run python models/04_deberta.py

uv run python scripts/10_build_multiclass_target.py
uv run python models/11_multiclass_baseline.py
uv run python models/12_multiclass_compare.py
uv run python models/14_evaluate_test_and_extension.py
```

`14_evaluate_test_and_extension.py` traduce todo el subconjunto en español de `dataset_extension` antes de evaluarlo, si `GOOGLE_TRANSLATE_API_KEY` está configurada. No es un script para correr por rutina.

Para `04_deberta.py`, instale antes las dependencias de entrenamiento.

```bash
uv sync --extra training
```

Revise el encabezado de cada script antes de ejecutarlo, entrenar modelos puede sobrescribir reportes o artefactos generados, incluido el que carga el backend en producción. No mezcle targets multietiqueta y multiclase.
