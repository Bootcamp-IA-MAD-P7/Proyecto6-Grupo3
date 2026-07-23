# PrivacyLens Dataset v1.0.0 — Informe de Calidad

**Fecha:** 2026-07-22 · **Estado:** ✅ APROBADO CON OBSERVACIONES

---

## 1. Calidad general

| Validación crítica | Resultado |
|---|---|
| Sin duplicados de IDs | ✔ PASS |
| Sin texto corrupto | ✔ PASS |
| Sin embeddings faltantes | ✔ PASS (10.797/10.797) |
| Sin categorías inválidas | ✔ PASS (100 % esquema OPP-115) |
| Sin insights alarmistas | ✔ PASS |
| Sin explicaciones vacías | ✔ PASS |
| Sin evidencias inexistentes | ✔ PASS |
| Sin referencias rotas | ✔ PASS |
| Duplicados de texto intra-documento | ⚠ WARNING (3.434, conocidos y documentados) |

## 2. Cobertura

| Métrica | Valor |
|---|---|
| Documentos / Empresas | 33 / 33 |
| Sectores | 16 |
| Idiomas | Español, Inglés |
| Párrafos totales | 10.797 (media 327,2 por documento) |
| Cobertura OPP-115 (párrafos con categoría específica) | 24,1 % |
| Cobertura RGPD (párrafos con artículos relacionados) | 20,9 % |
| Entidades NER | 2.574 párrafos con entidades |

## 3. Distribución de categorías

| Categoría | Párrafos | % |
|---|---|---|
| Other | 8.191 | 75,9 |
| Third Party Sharing/Collection | 1.038 | 9,6 |
| User Choice/Control | 544 | 5,0 |
| First Party Collection/Use | 411 | 3,8 |
| Data Retention | 196 | 1,8 |
| User Access, Edit & Deletion | 173 | 1,6 |
| Data Security | 110 | 1,0 |
| International & Specific Audiences | 85 | 0,8 |
| Policy Change | 40 | 0,4 |
| Do Not Track | 9 | 0,1 |

**Desbalance:** ratio max/min = 910:1 (Do Not Track apenas tiene 9 ejemplos). Recomendación: `class_weight="balanced"`, sobremuestreo, o excluir Do Not Track del entrenamiento inicial.

## 4. Incidencias registradas

- 2 documentos incompletos conocidos: **Reddit** (falta la sección de compartición, anti-bot) y **Renfe** (2 políticas de servicio inaccesibles).
- 19 contradicciones potenciales clasificadas: 18 HIGH, 1 LOW (son candidatas; normalmente reflejan ámbitos distintos, no incoherencias).
- Párrafos >5.000 caracteres: tablas/listas linealizadas (LOW).

## 5. Riesgos

1. **Preanotación por reglas:** las etiquetas son baseline automático, pendientes de revisión humana; no usar como ground truth sin validar una muestra.
2. **Duplicados intra-documento (3.434):** deduplicar por `text` antes del entrenamiento para evitar fuga train/test.
3. **"Other" dominante (76 %):** incluye fragmentos sin contenido jurídico; considerar binario "relevante/no relevante" como primera fase del clasificador.
4. **Embeddings TF-IDF:** sustituir por embeddings neuronales antes de funciones semánticas avanzadas.

## 6. Recomendaciones

- Deduplicar por hash de texto al construir los splits (estratificar por documento para evitar fuga).
- Revisión humana priorizada: párrafos `status=REVIEW` con `confidence<60` y "Other" largos.
- Ampliar el dataset con las 42 fuentes REVIEW_REQUIRED del Agente 0 (navegador headless) para v1.1.0.
