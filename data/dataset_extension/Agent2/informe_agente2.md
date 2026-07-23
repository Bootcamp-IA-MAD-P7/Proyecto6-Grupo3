# PrivacyLens Extended Dataset 2026 — Informe del Agente 2: Segmentación y construcción del dataset

**Fecha:** 2026-07-22
**Entrada:** `dataset/clean_documents/` (33 documentos) + `dataset/metadata/` + `processing_log.json`
**Reglas respetadas:** texto original intacto — sin traducir, resumir ni modificar significado. Las incidencias se registran, nunca se corrigen automáticamente.

---

## 1. Resultados principales

| Métrica | Valor |
|---|---|
| Documentos segmentados | **33 / 33 (100 %)** |
| Párrafos totales | **10.797** |
| IDs únicos (`DOC_XXXXX_PXXXX`) | ✔ 10.797 / 10.797 |
| Pérdida de texto | 0 (verificación de preservación ≥ 99,5 % por documento) |
| Palabras por párrafo | media 28,4 · mediana ~20 |
| Idioma por párrafo | es: mayoría (21 docs) · en: 12 docs · mismatches registrados: 97 (0,9 %) |
| Entidades NER | 3.356 en 3.000+ párrafos |
| Embeddings | 10.797 vectores × 256 dims en Parquet |

## 2. Artefactos generados (contrato de salida)

| Archivo | Contenido |
|---|---|
| `paragraphs_raw.csv` | 10.797 filas × 27 columnas, esquema exacto del contrato |
| `paragraph_statistics.json` | Estadísticas globales, por documento, features, QC |
| `paragraph_index.json` | Índice párrafo → documento, posición, líneas, `contains_percentages`, SHA-1 del texto |
| `document_structure.json` | Árbol de secciones (H1–H4) de los 33 documentos |
| `paragraph_entities.json` | Entidades por párrafo (9 tipos) |
| `paragraph_embeddings.parquet` | `paragraph_id`, `embedding_model`, `embedding_dimension`, `embedding_vector` |

## 3. NER (basado en reglas jurídicas)

| Tipo | Instancias |
|---|---|
| ORGANIZATION | 1.937 |
| COUNTRY | 581 |
| URL | 213 |
| ARTICLE | 190 |
| EMAIL | 178 |
| LAW | 145 (RGPD, GDPR, CCPA, LOPDGDD, ePrivacy…) |
| DATE | 84 |
| REGULATION | 28 (Reglamento UE 2016/679, 2018/1725, Directivas…) |
| PERSON | 0 (no implementado: la detección por reglas de nombres de persona es demasiado ruidosa; ver §5) |

## 4. Control de calidad (registrado, no modificado)

| Incidencia | Nº | Interpretación |
|---|---|---|
| Duplicados exactos dentro del documento | 3.442 | Conocidos del Agente 1: acordeones móvil/escritorio en Vodafone (1.076), Generali (1.005), CaixaBank (634), Santander (550) y versión anterior incluida en eBay (418) |
| Párrafos casi vacíos (<2 palabras) | 1.177 | Celdas de tablas linealizadas ("Purpose", "Contract", "Feedback"…): contenido legítimo, no ruido |
| Idioma inesperado | 97 (0,9 %) | Principalmente párrafos en inglés dentro de políticas en español (cláusulas estándar, nombres de programas) |
| Longitud extrema / codificación | 0 | ✔ |

## 5. Limitaciones declaradas y mejoras futuras

1. **Embeddings**: el runtime no dispone de modelos neuronales; se generaron vectores **TF-IDF hasheados (256 dims, L2-normalizados)**. Válidos para clustering, búsqueda semántica básica y detección de duplicados (uso previsto). Recomendación: regenerar con `sentence-transformers` (p. ej. `paraphrase-multilingual-MiniLM-L12-v2`) antes de funciones RAG.
2. **NER**: basado en reglas/regex y listas cerradas (leyes, reglamentos, autoridades, países). PERSON no implementado por ruido. Recomendación: spaCy (`es_core_news_lg` / `en_core_web_lg`) o un modelo legal-NER en fases posteriores.
3. **Detección de encabezados**: heurística sobre texto plano (numeración, mayúsculas, Title Case). Funciona bien con secciones numeradas; en documentos sin numeración (p. ej. Amazon) algunos títulos principales quedan como nivel 2. Suficiente para el Agente 3, mejorable con el HTML original.
4. **Duplicados intra-documento**: se registran pero se conservan (regla del contrato). El Agente 3 debería decidir si los ignora al preanotar.

## 6. Criterios de aceptación

- [x] 100 % de documentos segmentados
- [x] IDs únicos
- [x] Sin pérdida de texto
- [x] Metadatos completos (27 columnas del esquema)
- [x] Embeddings generados
- [x] Árbol documental generado
- [x] NER generado
- [x] Dataset listo para el Agente 3
