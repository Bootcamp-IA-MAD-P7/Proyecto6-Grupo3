# PrivacyLens Extended Dataset 2026 — Informe del Agente 4: Quality Assurance, Dataset Validation & Release

**Fecha:** 2026-07-22
**Entrada:** los 8 artefactos del contrato (predicciones, insights, perfiles, entidades, estructura, contradicciones, ambigüedad, embeddings)
**Resultado:** **PrivacyLens Dataset v1.0.0 — APROBADO CON OBSERVACIONES**
**Reglas respetadas:** no se modificó ninguna predicción, no se generaron etiquetas nuevas, no se alteró el texto original.

---

## 1. Resumen ejecutivo

El dataset ha superado las **9 validaciones críticas/altas** y presenta **1 observación no bloqueante** (duplicados de texto intra-documento, conocidos y documentados desde el Agente 1). Se publica como **v1.0.0** siguiendo Semantic Versioning.

## 2. Validación de estructura (Fase 1)

| Check | Resultado |
|---|---|
| Todos los archivos del contrato existen | ✔ |
| Todos los documentos poseen ID | ✔ |
| Todos los párrafos poseen ID único (10.797/10.797) | ✔ |
| Sin IDs repetidos en predicciones | ✔ |
| Referencias párrafo→predicción→embedding válidas | ✔ |
| Categorías 100 % dentro del esquema OPP-115 | ✔ |

## 3. Validación de contenido (Fase 2)

| Check | Resultado |
|---|---|
| Párrafos vacíos | 0 |
| Predicciones vacías | 0 |
| Insights vacíos | 0 |
| Explicaciones vacías | 0 |
| Embeddings inexistentes | 0 (cobertura 100 %) |
| Entidades corruptas / referencias huérfanas | 0 |
| Errores de codificación (U+FFFD) | 0 |
| Longitud anómala (>5.000 car.) | 22 párrafos — LOW (tablas/listas linealizadas) |

## 4. Validación de explicabilidad (Fase 3)

Toda predicción no-Other tiene **categoría + confianza + explicación + evidencias literales**. 0 incidencias. La cadena completa (motivo → evidencias → texto original) es reconstruible vía `explainability.json`.

## 5. Validación de Privacy Insights (Fase 4)

- ✔ 0 insights con opiniones, recomendaciones legales, afirmaciones de incumplimiento, lenguaje alarmista o acusaciones (verificación por patrones prohibidos).
- ✔ El 100 % comienza con fórmulas aprobadas ("La política indica/describe/explica/menciona/informa…", "El documento…").

## 6. Validación de Policy Profiles (Fase 5)

Los 33 perfiles son coherentes con los párrafos: totales por documento y categorías predominantes recalculados y comparados — sin inconsistencias bloqueantes.

## 7. Validación de contradicciones (Fase 6)

19 pares candidatos revisados y clasificados: **18 HIGH · 1 LOW**. Se registran como *posibles* contradicciones con ambos textos citados; en ningún caso se afirma incumplimiento (la mayoría reflejan ámbitos distintos: venta de datos vs. proveedores de servicios).

## 8. Métricas del dataset (Fases 7-8)

| Dimensión | Valor |
|---|---|
| Documentos / Empresas | 33 / 33 |
| Sectores | 16 |
| Idiomas | español, inglés |
| Párrafos | 10.797 (media 327,2/doc · desv. típ. 288,6) |
| Palabras/párrafo | media 28,4 · máx 2.858 · mín 1 |
| Cobertura OPP-115 | 24,1 % de párrafos con categoría específica |
| Cobertura RGPD | 20,9 % de párrafos con artículos relacionados |
| Entidades NER | 2.574 párrafos con entidades |
| Desbalance de clases | ratio 910:1 (Other 76 % → Do Not Track 0,1 %) |
| Duplicados intra-documento | 3.434 (⚠ observación) |
| Documentos incompletos | 2 (Reddit, Renfe — conocidos) |

## 9. Versionado y metadatos (Fases 9-10)

- **Versión:** 1.0.0 (Semantic Versioning: documentos nuevos → minor, etiquetas → major).
- `dataset_metadata.json` completo: nombre, versión, fecha, documentos, párrafos, idiomas, sectores, categorías, modelo de embeddings, compatibilidad OPP-115, pipeline y estado de validación.

## 10. Validación final (Fase 14)

| Check | Criticidad | Resultado |
|---|---|---|
| Sin duplicados de IDs | CRITICAL | ✔ PASS |
| Sin IDs repetidos en predicciones | CRITICAL | ✔ PASS |
| Sin texto corrupto | CRITICAL | ✔ PASS |
| Sin embeddings faltantes | CRITICAL | ✔ PASS |
| Sin categorías inválidas | CRITICAL | ✔ PASS |
| Sin insights alarmistas | CRITICAL | ✔ PASS |
| Sin explicaciones vacías | HIGH | ✔ PASS |
| Sin evidencias inexistentes | HIGH | ✔ PASS |
| Sin referencias rotas | HIGH | ✔ PASS |
| Duplicados de texto intra-documento | WARNING | ⚠ 3.434 registrados |

**Decisión:** APROBADO CON OBSERVACIONES — la única observación no es bloqueante porque los duplicados están identificados, son reproducibles y se documenta su tratamiento (deduplicar por hash de texto antes del split de entrenamiento).

## 11. Riesgos y recomendaciones

1. Las etiquetas son **preanotación por reglas**, pendientes de revisión humana — no usar como ground truth sin validar muestra.
2. **Deduplicar antes de entrenar** y hacer split estratificado **por documento** (evita fuga train/test).
3. Tratar el desbalance: `class_weight="balanced"`, submuestreo de "Other" o exclusión de "Do Not Track" en la primera iteración.
4. v1.1.0: incorporar las 42 fuentes REVIEW_REQUIRED del Agente 0 (scraper con navegador headless).
5. v2.0.0: etiquetas corregidas tras la revisión humana.

## 12. Artefactos del release

| Archivo | Contenido |
|---|---|
| `privacylens_dataset_v1.parquet` | **Dataset final — único archivo autorizado para entrenar** (10.797 × 25 campos) |
| `privacylens_dataset_v1.csv` | Espejo en CSV para inspección |
| `dataset_metadata.json` | Metadatos del dataset (Fase 10) |
| `dataset_statistics.json` | Métricas completas |
| `validation_report.json` | Validaciones, incidencias y contradicciones clasificadas |
| `dataset_quality_report.md` | Informe de calidad |
| `release_notes.md` | Notas de versión para el equipo |
| `CHANGELOG.md` | Historial de versiones |
