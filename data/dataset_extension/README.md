# PrivacyLens Extended Dataset 2026

Extensión moderna del dataset académico [OPP-115](https://usableprivacy.org/data) (Wilson et al., 2016), construida por el Grupo 3, Proyecto 6 (IA School, Factoría F5 Madrid).

Su rol en el proyecto, según `specs/1_intent.md`, es material de evaluación y demostración, no de entrenamiento. Aporta lo que OPP-115 no tiene, políticas actuales, la mayoría posteriores al RGPD y de 2025-2026, reales y en español. Es la fuente del conjunto de prueba en español.

Aviso. Las etiquetas son preanotación automática por reglas, etiquetas de plata, pendientes de revisión humana. No entrenar ni medir contra ellas sin validar antes.

## Resumen

| Métrica | Valor |
|---|---|
| Empresas | 33 |
| Sectores | 16 |
| Idiomas | Español, 21 políticas, e inglés, 12 |
| Párrafos | 10.797 |
| Categorías | 9 prácticas OPP-115 más la clase auxiliar `Other` |
| Mapeo RGPD | Oficial, Poplavska et al. 2020 (JURIX) |
| Versión | v1.1.0, del 22 de julio de 2026 |
| Estado QA | Aprobado con observaciones, ver `dataset_quality_report.md` |

## Pipeline de construcción, cinco agentes

```
AGENTE 0 --> AGENTE 1 --> AGENTE 2 --> AGENTE 3 --> Revisión --> AGENTE 4
Fuentes      Extracción   Segmentación Preanotación  Humana       QA y Release
```

### Agente 0, descubrimiento y validación de fuentes

Catálogo de fuentes oficiales verificadas. De 77 empresas investigadas, 33 quedaron `VALIDATED`, 42 `REVIEW_REQUIRED` y 2 `DISCARDED` por duplicadas, cifras confirmadas en `sources_catalog.csv`. Cada fuente trae URL oficial, fecha de actualización, idioma y longitud estimada.

Archivos, `sources_catalog.csv`, `company_metadata.json`, `company_metadata/` (con 77 archivos, uno por empresa investigada, no solo las validadas), `proposals.json`, `informe_agente0.md`.

### Agente 1, extracción, limpieza y normalización

Descarga y limpieza de las 33 políticas validadas, confirmado por los 33 archivos en `dataset/clean_documents/`. Elimina navegación, banners y scripts, normaliza a UTF-8, conserva la estructura jurídica y calcula un hash SHA-256 por documento para control de versiones. Procesó las 33, con 2 casos parciales documentados, Reddit y Renfe.

Archivos, `dataset/raw_documents/`, `dataset/clean_documents/`, `dataset/metadata/`, `processing_log.json`, `errors_report.json`, `informe_agente1.md`.

### Agente 2, segmentación y construcción del dataset

Segmenta en párrafos con identificador único (`DOC_XXXXX_PXXXX`), detecta estructura de encabezados H1 a H4, calcula metadatos estructurales y features booleanas, aplica reconocimiento de entidades jurídicas por reglas en español e inglés, detecta idioma por párrafo y genera incrustaciones TF-IDF de 256 dimensiones. La salida de esta etapa, en `paragraphs_raw.csv`, tiene más filas que el dataset final, la etapa siguiente filtra y deduplica antes de fijar los 10.797 párrafos publicados.

Archivos, `paragraphs_raw.csv`, `paragraph_statistics.json`, `paragraph_index.json`, `document_structure.json`, `paragraph_entities.json`, `paragraph_embeddings.parquet`, `informe_agente2.md`.

### Agente 3, preanotación

Clasifica cada párrafo en las categorías OPP-115 con un clasificador de reglas jurídicas bilingüe, categoría principal más una alternativa, confianza, evidencia literal, explicación, un resumen en lenguaje sencillo, artículos RGPD relacionados, un score de ambigüedad y detección de contradicciones entre párrafos del mismo documento. Sin juicios legales, según su propio control de calidad. La confianza media de esta etapa, medida directamente sobre `paragraph_predictions.csv`, es 58,8 %.

Archivos, `paragraph_predictions.csv`, `privacy_insights.csv`, `policy_profile.json`, `contradictions.json`, `ambiguity_report.json`, `explainability.json`, `informe_agente3.md`.

### Agente 4, control de calidad y release

14 fases de validación, sobre estructura, contenido, explicabilidad, insights, perfiles, contradicciones, métricas y versionado. De los checks críticos y de alta prioridad, 9 de 9 pasaron, con una advertencia no crítica por duplicados de texto intra-documento, según `validation_report.json`. Pasó de la versión v1.0.0 a la v1.1.0 al incorporar el mapeo RGPD oficial de Poplavska et al.

Archivos, `privacylens_dataset_v1_1.parquet`, el archivo principal para evaluación externa y demo, no se usa para entrenar los modelos actuales, con espejo en `privacylens_dataset_v1_1.csv`, más `dataset_metadata.json`, `dataset_statistics.json`, `validation_report.json`, `dataset_quality_report.md`, `release_notes.md`, `CHANGELOG.md`, `informe_agente4.md`.

## Archivo principal

`privacylens_dataset_v1_1.parquet`, 10.797 filas por 26 columnas, verificado con un parser CSV real sobre su espejo en `.csv` (contar líneas de texto sobre ese archivo da un número mayor, porque el campo `text` trae saltos de línea dentro de celdas entre comillas).

Columnas, `dataset_version`, `document_id`, `paragraph_id`, `company`, `sector`, `language`, `paragraph_language`, `section`, `subsection`, `paragraph_number`, `relative_position`, `text`, `characters`, `words`, `sentences`, `categoria_principal`, `categoria_alternativa`, `confidence`, `ambiguity`, `privacy_insight`, `explanation`, `evidence`, `rgpd_articles`, `rgpd_principles_poplavska`, `keywords`, `status`.

## Uso en evaluación

`models/14_evaluate_test_and_extension.py` compara el modelo de producción, entrenado sobre OPP-115 de 2016, contra `evaluation_es.csv` y `evaluation_en.csv`, derivados de este dataset. No es una medición de accuracy contra ground truth, las etiquetas de comparación son las mismas preanotaciones automáticas por reglas de este dataset, así que el resultado mide acuerdo entre dos clasificadores automáticos, no calidad del modelo en sentido estricto. Sirve para ver cómo reacciona el modelo a vocabulario y prácticas de políticas modernas, ausentes en 2016. Resultados y la salvedad completa en `models/README.md` y `reports/dataset_extension_evaluation.json`.

## Limitaciones conocidas, leer antes de usar

1. Etiquetas de plata por reglas, confianza media 58,8 %, revisión humana pendiente.
2. 75,9 % de los párrafos caen en `Other`, según `dataset_quality_report.md`, coherente con dejar `Other` fuera del target de entrenamiento multietiqueta.
3. Desbalance extremo entre categorías, `Do Not Track` tiene 9 ejemplos en todo el dataset.
4. 3.434 duplicados exactos de texto dentro del mismo documento, deduplicar antes de partir en train o test si se usa para entrenar en el futuro.
5. Mono-etiqueta en la práctica, solo 2,8 % de los párrafos trae una categoría alternativa, a diferencia de OPP-115, que sí es multietiqueta.
6. Granularidad más fina que OPP-115, mediana de unas 20 palabras por párrafo.
7. 2 documentos incompletos conocidos, Reddit y Renfe.

## Fuentes externas versionadas

| Recurso | Referencia |
|---|---|
| `external_datasets/JURIX_2020_OPP115_GDPR/` | Poplavska et al. 2020 (JURIX), mapeo OPP-115 y RGPD. DOI 10.3233/FAIA200874 |
| `external_datasets/MAPP_Corpus/` | Arora et al. 2022 (LREC), corpus bilingüe de 155 políticas de apps, gold standard |
| `poplavska_jurix_2020.pdf` | Paper del mapeo RGPD |

## Citación y licencias

- Políticas de privacidad, texto oficial de cada empresa, descargado de su dominio oficial en julio de 2026, ver `sources_catalog.csv`.
- Taxonomía, Wilson et al. (2016), *The Creation and Analysis of a Website Privacy Policy Corpus*, ACL 2016.
- Mapeo RGPD, Poplavska, Norton, Wilson y Sadeh (2020), JURIX 2020.
- MAPP Corpus, Arora et al. (2022), LREC, solo para investigación y docencia, citando el paper original.
