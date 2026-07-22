# PrivacyLens — Informe del Agente 0: Descubrimiento y validación de fuentes

**Fecha:** 2026-07-22
**Objetivo:** catálogo de fuentes oficiales de políticas de privacidad (post-RGPD) para el pipeline del dataset PrivacyLens (complemento moderno de OPP-115).
**Nota:** en esta fase NO se ha descargado ninguna política. Solo se han verificado URLs, accesibilidad, fechas y estimaciones de longitud.

---

## 1. Resumen ejecutivo

| Métrica | Valor |
|---|---|
| Empresas investigadas | **77** |
| VALIDATED | **33** |
| REVIEW_REQUIRED | **42** |
| DISCARDED | **2** |
| Sectores cubiertos | 19 |
| Idiomas del catálogo | Español (50), Inglés (24), Multiidioma (3) |

El catálogo queda listo para el Agente 1 con **75 fuentes únicas** (33 validadas directamente + 42 pendientes de revisión humana ligera, la mayoría por protección anti-bot o fecha no visible, no por problemas de fondo).

## 2. Empresas descartadas y motivos

| Empresa | Motivo |
|---|---|
| Instagram | **Duplicada**: no tiene política independiente; usa la Política de Privacidad de Meta (ya catalogada en Facebook). Además, bloqueo anti-bot (HTTP 400). |
| Prime Video | **Duplicada**: se rige por el Aviso de Privacidad de Amazon (ya catalogado); la propia página lo declara expresamente. |

## 3. Distribución por sectores

| Sector | Nº |
|---|---|
| Retail | 7 |
| Inteligencia Artificial | 6 |
| Redes Sociales | 6 |
| Viajes | 6 |
| Productividad | 5 |
| Ecommerce | 5 |
| Buscadores | 4 |
| Cloud | 4 |
| Streaming | 4 |
| Bancos | 4 |
| Seguros | 4 |
| Educación | 4 |
| Administración | 4 |
| Telecomunicaciones | 3 |
| Transporte | 3 |
| Salud | 3 |
| Inmobiliario | 2 |
| Delivery | 2 |
| Marketplace segunda mano | 1 |

## 4. Distribución por países

| Grupo | Nº | Detalle |
|---|---|---|
| EE. UU. | 33 | Big tech, SaaS, plataformas educativas |
| España | 27 | Banca, seguros, telecom, salud, administración, retail, inmobiliario |
| Otros | 16 | Francia (2), Alemania (3), Reino Unido, Países Bajos (3), Suecia (2), Estonia, Italia, Canadá, China, Singapur, Australia |
| Unión Europea (institucional) | 1 | Comisión Europea |

## 5. Idiomas

- **Español: 50** políticas (versión oficial en español localizada o nativa)
- **Inglés: 24** (sin versión en español oficial o URL canónica en inglés)
- **Multiidioma: 3** (OpenAI, Facebook/Meta, Instagram — la URL sirve versión según locale)

## 6. Validadas con fecha 2025-2026 (núcleo prioritario del dataset)

Anthropic (2026-07), Mistral AI (2026-04), Google Cloud (2026-04), DuckDuckGo (2026-06), Spotify (2026-06), IKEA (2026-06), Just Eat (2026-06), Glovo (2026-03), Expedia (2026-01), Vodafone España (2026-01), Amazon (2025-12), Coursera (2025-12), Generali (2025-11), Wallapop (2025-11), Mercadona (2025-08), ClickUp (2025-07), Reddit (2025-05), Dropbox (2025-05), TikTok (2025-06), eBay (2025-04).

## 7. Hallazgos relevantes para el Agente 1

1. **Anti-bot / JavaScript**: ~20 fuentes devuelven 403/406/400 o renderizan el contenido con JavaScript (Meta, Perplexity, Ecosia, Notion, Asana, Udemy, Carrefour, El Corte Inglés, Idealista, Fotocasa, Zara, AXA, Allianz, Uber, Bolt, Skyscanner, Airbnb, Etsy en español). Requieren extracción con navegador real (Playwright/Selenium) o verificación manual.
2. **Políticas corporativas compartidas**: Bing y Microsoft Azure comparten la Declaración de Privacidad de Microsoft (misma URL) — decidir si se extrae una sola vez. GitHub Copilot → política de GitHub; Trello → Atlassian; Disney+ → The Walt Disney Company; Orange → MasOrange.
3. **PDFs oficiales**: ING (34 páginas) y BBVA/CaixaBank (PDF enlazado) — el Agente 1 necesita extractor de PDF.
4. **Políticas fragmentadas**: Movistar/Telefónica distribuye su política en el Centro de Transparencia; Renfe, Cabify, Glovo y Decathlon tienen políticas por tipo de servicio/interesado. Conviene fijar criterio (política de clientes/pasajeros como referencia).
5. **Posiblemente desactualizadas** (post-RGPD pero antiguas): AliExpress (2021-07), Adeslas (2022-03), Hugging Face (2023-03), Slack (2023-07), Inditex/Zara (PDF de 2018 en la web actual), Movistar (2020). Candidatas a sustitución o a quedar como REVIEW_REQUIRED permanente.

## 8. Recomendaciones

1. **Prioridad de extracción**: empezar por las 33 VALIDATED (extracción directa con requests/BeautifulSoup) y reservar un scraper con navegador headless para las ~20 con anti-bot.
2. **Fijar locales**: para OpenAI, Meta y TikTok decidir explícitamente la versión (EEA vs ROW, es-ES vs en) antes de descargar, dado que el dataset se orienta al RGPD.
3. **Deduplicación**: extraer la Declaración de Microsoft una sola vez y referenciarla desde Bing y Azure.
4. **Ampliación del dataset**: se proponen 17 empresas adicionales en `proposals.json` que aportarían diversidad jurídica (China/PIPL: DeepSeek, Baidu), geográfica (Mercado Libre, OVHcloud), de modelo de negocio (Proton, Khan Academy, Revolut, Supercell) y de categorías especiales de datos (Doctoralia — salud, art. 9 RGPD).
5. **Control de versiones**: registrar `download_date` en la siguiente fase y archivar el HTML/PDF crudo de cada política para reproducibilidad.

## 9. Archivos generados

| Archivo | Contenido |
|---|---|
| `sources_catalog.csv` | Catálogo completo (77 registros, 11 campos) |
| `company_metadata.json` | Metadatos combinados de todas las empresas |
| `company_metadata/*.json` | Un JSON por empresa (77 archivos) |
| `proposals.json` | 17 empresas propuestas para ampliar el dataset |
| `informe_agente0.md` | Este informe |
