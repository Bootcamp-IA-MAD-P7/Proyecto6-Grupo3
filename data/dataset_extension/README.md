# PrivacyLens Extended Dataset 2026

Extensión moderna del dataset académico [OPP-115](https://usableprivacy.org/data) (Wilson et al., 2016) construida por el **Grupo 3 — Proyecto 6** (IA School, Factoría F5 Madrid).

**Rol en el proyecto (spec §1.3):** material de **evaluación y demo, no de entrenamiento**. Aporta lo que OPP-115 no tiene: políticas actuales (post-RGPD, mayoría 2025-2026), reales y en español. Es la fuente del conjunto de prueba en español.

> ⚠️ Las etiquetas son **preanotación automática por reglas** (etiquetas de plata), pendientes de revisión humana. No entrenar ni medir contra ellas sin validar.

---

## Resumen

| Métrica | Valor |
|---|---|
| Empresas | 33 |
| Sectores | 16 |
| Idiomas | Español (21 políticas) · Inglés (12) |
| Párrafos | 10.797 |
| Categorías | Las 10 oficiales de OPP-115 |
| Mapeo RGPD | **Oficial: Poplavska et al. 2020 (JURIX)** |
| Versión | **v1.1.0** (2026-07-22) |
| Estado QA | APROBADO CON OBSERVACIONES (ver `dataset_quality_report.md`) |

## Pipeline de construcción (5 agentes)

```
AGENTE 0 ──► AGENTE 1 ──► AGENTE 2 ──► AGENTE 3 ──► Revisión ──► AGENTE 4
Fuentes      Extracción   Segmentación Preanotación  Humana       QA + Release
```

### Agente 0 — Descubrimiento y validación de fuentes

Catálogo de fuentes oficiales verificadas. 77 empresas investigadas → 33 VALIDATED · 42 REVIEW_REQUIRED · 2 DISCARDED (duplicadas). Cada fuente con URL oficial, fecha de actualización, idioma y longitud estimada.

- 📄 `sources_catalog.csv` · `company_metadata.json` · `company_metadata/` · `proposals.json`
- 📋 `informe_agente0.md`

### Agente 1 — Extracción, limpieza y normalización

Descarga y limpieza de las 33 políticas validadas. Eliminación de navegación/banners/scripts, normalización UTF-8, conservación de la estructura jurídica y hash SHA-256 por documento para control de versiones. 33/33 procesados (2 parciales documentados: Reddit, Renfe).

- 📄 `dataset/raw_documents/` · `dataset/clean_documents/` · `dataset/metadata/`
- 📄 `processing_log.json` · `errors_report.json`
- 📋 `informe_agente1.md`

### Agente 2 — Segmentación y construcción del dataset

Segmentación en 10.797 párrafos con IDs únicos (`DOC_XXXXX_PXXXX`), detección de estructura (H1-H4), metadatos estructurales, features booleanas, NER jurídico por reglas (es/en), idioma por párrafo y embeddings TF-IDF (256 dims).

- 📄 `paragraphs_raw.csv` · `paragraph_statistics.json` · `paragraph_index.json`
- 📄 `document_structure.json` · `paragraph_entities.json` · `paragraph_embeddings.parquet`
- 📋 `informe_agente2.md`

### Agente 3 — Preanotación IA (Legal Intelligence)

Clasificación de cada párrafo en las categorías OPP-115 con clasificador de reglas jurídicas bilingües: categoría principal + alternativa, confianza, evidencias **literales**, explicación, insight en lenguaje sencillo, artículos RGPD, score de ambigüedad y detección de contradicciones. Sin juicios legales (verificado por QC).

- 📄 `paragraph_predictions.csv` · `privacy_insights.csv` · `policy_profile.json`
- 📄 `contradictions.json` · `ambiguity_report.json` · `explainability.json`
- 📋 `informe_agente3.md`

### Agente 4 — QA, validación y release

14 fases de validación (estructura, contenido, explicabilidad, insights, perfiles, contradicciones, métricas, versionado). 9/9 checks críticos PASS. Release v1.0.0 → **v1.1.0** (mapeo RGPD oficial Poplavska).

- 📄 `privacylens_dataset_v1_1.parquet` ← **archivo autorizado para entrenar**
- 📄 `privacylens_dataset_v1_1.csv` (espejo)
- 📄 `dataset_metadata.json` · `dataset_statistics.json` · `validation_report.json`
- 📋 `dataset_quality_report.md` · `release_notes.md` · `CHANGELOG.md` · `informe_agente4.md`

## Archivo principal

**`privacylens_dataset_v1_1.parquet`** — 10.797 filas × 26 columnas:

`dataset_version, document_id, paragraph_id, company, sector, language, paragraph_language, section, subsection, paragraph_number, relative_position, text, characters, words, sentences, categoria_principal, categoria_alternativa, confidence, ambiguity, privacy_insight, explanation, evidence, rgpd_articles, rgpd_principles_poplavska, keywords, status`

## Limitaciones conocidas (leer antes de usar)

1. **Etiquetas de plata** por reglas (confianza media 58,8 %): revisión humana pendiente.
2. **76 % de párrafos en `Other`** → coherente con dejar `Other` fuera del target (spec §2.2).
3. **Desbalance extremo**: `Do Not Track` tiene 9 ejemplos.
4. **3.434 duplicados exactos intra-documento** → deduplicar antes de partir (spec §4.2).
5. **Mono-etiqueta** (2,8 % con alternativa) — no es multi-etiqueta como OPP-115.
6. Granularidad más fina que OPP-115 (mediana ~20 palabras/párrafo).
7. 2 documentos incompletos conocidos (Reddit, Renfe).

## Fuentes externas versionadas

| Recurso | Referencia |
|---|---|
| `external_datasets/JURIX_2020_OPP115_GDPR/` | Poplavska et al. 2020 (JURIX) — mapeo OPP-115 ↔ RGPD. DOI: 10.3233/FAIA200874 |
| `external_datasets/MAPP_Corpus/` | Arora et al. 2022 (LREC) — corpus bilingüe de 155 políticas de apps (gold standard) |
| `poplavska_jurix_2020.pdf` | Paper del mapeo RGPD |

## Citación y licencias

- Políticas de privacidad: texto oficial de cada empresa, descargado de su dominio oficial en julio 2026 (`sources_catalog.csv`).
- Taxonomía: Wilson et al. (2016), *The Creation and Analysis of a Website Privacy Policy Corpus*, ACL 2016.
- Mapeo RGPD: Poplavska, Norton, Wilson & Sadeh (2020), JURIX 2020.
- MAPP Corpus: Arora et al. (2022), LREC — solo investigación/docencia, citando el paper.
