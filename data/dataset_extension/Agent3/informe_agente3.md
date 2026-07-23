# PrivacyLens Extended Dataset 2026 — Informe del Agente 3: Legal Intelligence & Privacy Insights

**Fecha:** 2026-07-22
**Entrada:** `paragraphs_raw.csv` (10.797 párrafos) + entidades + estructura + embeddings
**Principios respetados:** neutralidad, trazabilidad, explicabilidad, sin juicios legales, sin información inventada. Todas las evidencias son literales del texto.

---

## 1. Método (declarado con transparencia)

Preanotación **determinista basada en reglas jurídicas bilingües** (es/en): listas ponderadas de indicadores por cada una de las 10 categorías oficiales OPP-115, igual que los baselines del paper original. Los 3.442 duplicados exactos se clasificaron una vez y se propagó la etiqueta. La siguiente fase del pipeline (**Revisión Humana**) corregirá los errores de esta preanotación.

**Nota taxonómica:** OPP-115 no tiene categoría "Cookies"; los párrafos sobre cookies se clasifican en First/Third Party Collection según su contenido, y el concepto "cookies" queda en el campo `keywords`.

## 2. Resultados

| Métrica | Valor |
|---|---|
| Párrafos analizados | 10.797 |
| Párrafos con categoría específica | 2.606 (24,1 %) |
| Other (sin indicadores claros) | 8.191 (75,9 %) |
| Confianza media | 58,8 % |
| Párrafos marcados REVIEW | 8.539 (incluye "Other" largos y confianza <60) |
| Contradicciones potenciales detectadas | 19 pares en varios documentos |

### Distribución por categoría OPP-115

| Categoría | Párrafos |
|---|---|
| Third Party Sharing/Collection | 1.038 |
| User Choice/Control | 544 |
| First Party Collection/Use | 411 |
| Data Retention | 196 |
| User Access, Edit & Deletion | 173 |
| Data Security | 110 |
| International & Specific Audiences | 85 |
| Policy Change | 40 |
| Do Not Track | 9 |

El predominio de Third Party Sharing es coherente con la literatura (es la práctica más descrita en políticas modernas post-RGPD).

## 3. Control de calidad (todo superado)

- ✔ 0 categorías fuera del listado oficial OPP-115
- ✔ 0 clasificaciones sin evidencias literales (fuera de "Other")
- ✔ 0 insights con lenguaje alarmista o juicios legales (verificado por regex)
- ✔ Toda clasificación es reconstruible vía `explainability.json` (motivo → evidencias → texto original)

## 4. Hallazgos

- **Ambigüedad de lenguaje:** el informe `ambiguity_report.json` cuantifica por documento el uso de condicionales (may/might/could, "podría", "en determinados casos"…); los párrafos con mayor score están señalados para revisión.
- **Contradicciones potenciales:** 19 pares del tipo «no compartimos datos» vs. «podemos compartir con socios» registrados en `contradictions.json` con ambos textos citados. Son **candidatas** — normalmente reflejan ámbitos distintos (venta vs. proveedores), no incoherencias reales.
- **Perfiles de política:** `policy_profile.json` resume las 33 políticas con categorías predominantes y aspectos destacados (sin puntuaciones de riesgo, según el brief).

## 5. Limitaciones y mejoras para la revisión humana

1. **Sesgo hacia "Other" (76 %):** el umbral exige ≥2 puntos de evidencia; párrafos con un solo indicador débil quedan sin clasificar. La revisión humana debería centrarse en los "Other" largos (>800 caracteres), ya marcados como REVIEW.
2. **Falsos positivos de baja confianza:** coincidencias de una sola palabra clave (p. ej. "third parties" en un párrafo de portabilidad) — filtrables por `confidence < 60`.
3. **Cobertura léxica:** giros jurídicos sin palabra clave directa ("podrá efectuar el tratamiento de datos…") pueden escapar; mejorable ampliando las listas tras la primera ronda de revisión.
4. **Mejora futura:** una pasada LLM sobre los 8.539 párrafos REVIEW (o sobre una muestra estratificada) elevaría la calidad de la preanotación antes de la revisión humana.

## 6. Artefactos generados

| Archivo | Contenido |
|---|---|
| `paragraph_predictions.csv` | 10.797 × 11 campos (categoría, alternativa, confianza, ambigüedad, insight, explicación, evidencias, RGPD, keywords, status) |
| `privacy_insights.csv` | Insights en lenguaje sencillo por párrafo |
| `policy_profile.json` | Perfil de las 33 políticas |
| `contradictions.json` | 19 contradicciones potenciales con textos citados |
| `ambiguity_report.json` | Scores de lenguaje condicional por documento y top párrafos |
| `explainability.json` | Cadena completa motivo → evidencias → texto original por párrafo |
