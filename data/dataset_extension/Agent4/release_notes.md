# PrivacyLens Dataset — Release Notes

**Para:** equipo PrivacyLens (Grupo 3) · **Fecha:** 2026-07-22

> **Actualización v1.1.0 (mismo día):** el campo `rgpd_articles` usa ahora el mapeo académico oficial de Poplavska et al. 2020 (JURIX) y se añade `rgpd_principles_poplavska` (principios del Art. 5). Archivo autorizado para entrenamiento: **`privacylens_dataset_v1_1.parquet`** (sustituye a `privacylens_dataset_v1.parquet`).

## Qué incluye esta versión (v1.0.0)

## Qué incluye esta versión

Primera versión del dataset PrivacyLens Extended 2026, complementario de OPP-115:

- **33 políticas de privacidad oficiales post-RGPD** (20 con actualización 2025-2026), de 16 sectores, en español e inglés.
- **10.797 párrafos** con 25 campos: identificadores, metadatos estructurales, categoría OPP-115 (principal + alternativa), confianza, ambigüedad, insight, explicación, evidencias literales, artículos RGPD y keywords.
- **Embeddings** TF-IDF (256 dims) en `paragraph_embeddings.parquet`.
- **NER jurídico** por reglas en `paragraph_entities.json`.
- **Trazabilidad completa:** hash SHA-256 por documento fuente; cada predicción reconstruible vía `explainability.json`.

## Archivo autorizado para entrenamiento

`privacylens_dataset_v1.parquet` (espejo en CSV para inspección). Es el único archivo autorizado para entrenar el modelo Ensemble.

## Incidencias conocidas

- Reddit: falta una sección (anti-bot). Renfe: 2 políticas de servicio no accesibles.
- 3.434 duplicados exactos intra-documento (acordeones móvil/escritorio): **deduplicar antes de entrenar**.
- 19 contradicciones potenciales registradas como candidatas (18 HIGH / 1 LOW), sin afirmación de incumplimiento.

## Limitaciones

- Etiquetas generadas por clasificador de reglas (baseline OPP-115): pendientes de revisión humana.
- Desbalance extremo de clases (Other 76 %; Do Not Track 9 ejemplos).
- Embeddings no neuronales; NER sin modelo spaCy.

## Próximos pasos

1. Revisión humana con cola priorizada (REVIEW + "Other" largos).
2. v1.1.0: añadir las fuentes REVIEW_REQUIRED del Agente 0 (scraper con navegador).
3. v2.0.0: etiquetas corregidas tras revisión humana (Semantic Versioning: cambio de etiquetas = major).

## Recomendaciones para el entrenamiento

- Split estratificado **por documento** (no por párrafo) para evitar fuga de datos.
- Deduplicar por `text` antes del split.
- `class_weight="balanced"` o submuestreo de "Other"; valorar excluir "Do Not Track" en la primera iteración.
- Baseline recomendado: TF-IDF + Regresión Logística / LinearSVC antes del Ensemble (RandomForest + GradientBoosting + XGBoost).
