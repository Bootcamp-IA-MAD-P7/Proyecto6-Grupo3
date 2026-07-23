# Changelog — PrivacyLens Dataset

## v1.1.0 — 2026-07-22

Mejora de contenido (sin cambio de documentos ni de etiquetas).

- Campo `rgpd_articles` regenerado con el **mapeo oficial OPP-115 ↔ RGPD de Poplavska et al. 2020 (JURIX)** en sustitución del mapeo heurístico propio (cobertura mucho más rica: hasta 21 artículos por categoría).
- Nuevo campo `rgpd_principles_poplavska`: principios del Art. 5 RGPD asociados a cada categoría.
- Archivo autorizado para entrenamiento: `privacylens_dataset_v1_1.parquet`.
- Referencia añadida: Poplavska, Norton, Wilson & Sadeh, "From Prescription to Description: Mapping the GDPR to a Privacy Policy Corpus Annotation Scheme", JURIX 2020.

## v1.0.0 — 2026-07-22

Primer release.

- 33 empresas.
- 16 sectores.
- 2 idiomas (español, inglés).
- 10.797 párrafos.
- Compatible con OPP-115 (10 categorías oficiales).
- Embeddings incluidos (TF-IDF 256 dims).
- NER incluido (reglas jurídicas es/en).
- Trazabilidad SHA-256 por documento fuente.
- Estado de validación: APROBADO CON OBSERVACIONES (duplicados intra-documento documentados).
