# PrivacyLens Extended Dataset 2026 — Informe del Agente 1: Extracción, limpieza y normalización documental

**Fecha de procesado:** 2026-07-22
**Entrada:** `sources_catalog.csv` + `company_metadata/` (solo políticas con estado VALIDATED del Agente 0)
**Alcance:** 33 políticas oficiales. No se ha clasificado, etiquetado, traducido, resumido ni reescrito ningún contenido.

---

## 1. Estadísticas generales

| Métrica | Valor |
|---|---|
| Documentos procesados | **33 / 33** |
| Procesados sin incidencias (OK) | 31 |
| Procesados parciales (PARTIAL) | 2 (Reddit, Renfe) |
| Descartados / errores | 0 |
| Longitud media (limpio) | ~9.488 palabras |
| Longitud máxima | 39.280 palabras (Generali — 4 notas por tipo de interesado) |
| Longitud mínima | 2.071 palabras (DuckDuckGo — política minimalista por diseño) |
| Idiomas | Español: 21 · Inglés: 12 |
| Volumen total limpio | ~2,1 MB de texto jurídico |
| Hashes SHA-256 generados | 33 (en `dataset/metadata/*_metadata.json`) |

## 2. Calidad

| Métrica | Valor / Detalle |
|---|---|
| Contenido eliminado (media) | ~4 % del texto extraído |
| Texto útil (media) | ~96 % |
| Documentos incompletos | 1 (Reddit — falta la sección "How We Share Your Information") |
| Documentos repetidos | 0 entre documentos; duplicados internos detectados en Generali y Vodafone (acordeones móvil/escritorio) |
| Anomalías totales | 33 → CRITICAL: 0 · HIGH: 1 · MEDIUM: 9 · LOW: 23 |

**Nota metodológica sobre el % eliminado:** en la mayoría de los sitios la extracción de contenido principal ya descartaba la navegación antes de guardar el raw, por lo que el porcentaje de limpieza incremental es bajo. En sitios con HTML completo descargado (Trello, Spotify, Iberia, MAPFRE, Cabify) el recorte real fue mayor.

## 3. Incidencias relevantes

| Gravedad | Empresa | Incidencia |
|---|---|---|
| HIGH | Reddit | Sección "How We Share Your Information" no recuperable (reto anti-bot JS); 13 secciones presentes |
| MEDIUM | eBay | La página oficial incluye el aviso vigente + la versión anterior completa (conservadas ambas) |
| MEDIUM | Zalando | Documento >15.000 palabras (extensión legítima, capítulo por países) |
| MEDIUM | Santander | Restos de pie de página al final del clean → **recortados en post-procesado** |
| MEDIUM | Generali | Duplicados internos por acordeones móvil/escritorio no totalmente deduplicados |
| MEDIUM | Vodafone | Duplicados internos por acordeones; la pestaña de cookies fue separada y excluida |
| MEDIUM | Renfe | 2 políticas de servicio enlazadas no accesibles (Canal Ético, rodaje) |

**Casos especiales resueltos:**
- **ING**: PDF oficial de 34 páginas convertido a texto (10.101 palabras, extracción correcta).
- **Vodafone**: separada la política de privacidad de la de cookies (página compartida); se descartó un PDF desactualizado (22/05/2025) en favor del texto web vigente (01/01/2026).
- **Coursera**: la primera extracción devolvió la versión en chino por geolocalización; se forzó la versión original en inglés.
- **Renfe**: unificadas la política general + 5 políticas de servicio accesibles en el orden enlazado.
- **Fechas detectadas durante la extracción** (más recientes que las del catálogo): ClickUp (02/06/2026), Booking (mayo 2026), Zalando (05/2026), Wallapop (24/02/2026).

## 4. Recomendaciones

1. **Revisión humana prioritaria: Reddit.** Recuperar la sección "How We Share Your Information" con navegador real (o Kimi WebBridge) antes de segmentar.
2. **Deduplicación fina**: Generali y Vodafone conservan duplicados internos de acordeones; el Agente 2 (segmentación) debería aplicar deduplicación a nivel de párrafo.
3. **eBay**: decidir si la versión anterior del aviso se mantiene en el dataset o se segrega (podría contaminar la preanotación por duplicidad conceptual).
4. **Futuras ejecuciones**: usar navegador headless (Playwright) para los sitios con anti-bot (~20 fuentes REVIEW_REQUIRED del Agente 0) y fijar cabecera `Accept-Language` explícita para evitar geolocalización de idioma.
5. **Control de versiones**: los 33 hashes SHA-256 permiten detectar cambios; se recomienda re-ejecutar el Agente 1 trimestralmente y comparar hashes.

## 5. Contrato de salida (para el Agente 2)

| Artefacto | Ruta | Contenido |
|---|---|---|
| Documentos limpios | `dataset/clean_documents/` | 33 ficheros `<slug>_clean.txt` (UTF-8, estructura conservada) |
| Metadatos | `dataset/metadata/` | 33 ficheros `<slug>_metadata.json` (document_id, hash, longitudes, estado…) |
| Log de procesado | `processing_log.json` | Registro completo por documento con anomalías |
| Informe de errores | `errors_report.json` | 33 anomalías clasificadas por gravedad |
| Documentos raw | `dataset/raw_documents/` | 33 raw (`ing_raw.pdf` conservado además como fuente original) |
