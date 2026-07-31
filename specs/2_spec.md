# SPEC 2. Especificación funcional y técnica

## 1. Producto

PrivacyLens tiene tres capas.

1. Una experiencia educativa React.
2. Una API FastAPI con un contrato de análisis, respaldada por un modelo entrenado.
3. Pipelines de datos y modelos experimentales, fuera del runtime de la API.

Las capas 1 y 2 están conectadas de extremo a extremo a través de `POST /api/analyze`, tanto desde la página de análisis del frontend como desde la extensión de Chrome. La portada del frontend, aparte, sigue mostrando análisis recientes y estadísticas de ejemplo, esos dos bloques no llaman a la API por decisión de diseño, no porque falte conectarlos.

## 2. Frontend

### Rutas

| Ruta | Función |
|---|---|
| `/` | Inicio, entrada de URL, análisis recientes y estadísticas de ejemplo |
| `/analisis` | Resultado real, llama a `POST /api/analyze` |
| `/riesgos` | Educación sobre seis riesgos |
| `/rgpd` | Derechos RGPD y pasos para ejercerlos |
| `/aprende` | Recursos y hábitos |
| `/modelo` | PrivacyLens Lab, métricas de los modelos comparados |
| `/categorias` | Catálogo educativo interactivo |
| `/extension` | Presentación visual de la extensión, sin lógica real |

El estado activo del navbar se resuelve con React Router. Navbar y footer son globales.

### Datos

`analysisService.js` es el único punto del frontend que hace `fetch`. `analyzeUrl()` llama a `POST /api/analyze` de verdad, con la URL del backend fijada en tiempo de compilación por la variable `VITE_API_BASE_URL`, o por el proxy de `vite.config.js` en desarrollo local si esa variable no está puesta. `getRecentAnalyses()` y `getGlobalStats()` devuelven siempre el contenido fijo de `mockData.js`, esos dos endpoints no existen en el backend y no está previsto que existan, según su propio comentario en el código.

## 3. Backend

- FastAPI y Pydantic.
- Puerto local `8000`.
- `GET /api/health`.
- `POST /api/analyze`, acepta `text`, `url`, o ambos.
- Con `text`, se analiza ese texto directamente, hasta 100.000 caracteres.
- Con `url` y sin `text`, el backend descarga la página y extrae su texto, con guardas contra SSRF y sin ejecutar JavaScript.
- CORS mediante `CORS_ALLOWED_ORIGINS`, sin comodín en ningún entorno.

El análisis divide el texto por párrafos, detecta el idioma con una heurística, traduce los fragmentos en español a inglés si hay una clave de Google Cloud Translation configurada, y clasifica cada fragmento con un modelo ComplementNB entrenado sobre OPP-115. No hay umbral de decisión, la categoría con mayor probabilidad gana el fragmento.

## 4. Taxonomías

### Backend, en producción

Diez categorías, en este orden fijo, es el orden de las columnas de probabilidad del modelo.

1. `first_party_collection_use`
2. `third_party_sharing_collection`
3. `user_choice_control`
4. `user_access_edit_deletion`
5. `data_retention`
6. `data_security`
7. `policy_change`
8. `do_not_track`
9. `international_specific_audiences`
10. `Other`

Las primeras nueve son las categorías oficiales de OPP-115. `Other` es la décima clase del target multiclase, para fragmentos que no describen ninguna práctica de datos, como introducciones o datos de contacto.

### Enfoque de entrenamiento

El corpus OPP-115 es multietiqueta en origen, un mismo fragmento puede pertenecer a varias de las nueve categorías. El modelo que sirve la API en producción es multiclase, entrenado sobre un target derivado que resuelve cada fragmento a una sola categoría por prioridad, más `Other`. `models/README.md` documenta ambos enfoques y sus resultados por separado.

### Catálogo visual del frontend

`frontend/src/config/categories.js` define diez identificadores propios, con fines educativos, para la página `/categorias`. Solo tres coinciden textualmente con las categorías reales del backend, `data_retention`, `data_security` y `policy_change`. No existe una capa de traducción formal entre ese catálogo visual y las categorías reales, el propio archivo lo marca con un comentario `TODO(backend)`.

## 5. Datos y partición

- Entrenamiento, OPP-115.
- Clave natural, `(policy, segment)`.
- Split congelado por política, train, validación y test.
- TF-IDF se ajusta solo con train.
- `dataset_extension` se reserva para evaluación externa y demo, no se mezcla con el entrenamiento.
- Test no se utiliza para selección de modelos.

## 6. Métricas

Para el enfoque multietiqueta se reportan macro-F1, micro-F1, F1 por etiqueta y gap train-validación. Para multiclase se reportan accuracy, macro-F1, F1 por clase y esos mismos gaps. `models/README.md` trae la tabla de resultados versionados de los tres modelos multiclase comparados.

## 7. Contrato de salida

La respuesta contiene `model_version`, `stub` (siempre `false` en producción), y un objeto `document` con idioma detectado, si se tradujo, si la traducción estaba disponible, exposición calculada, categorías y número de fragmentos, además de una lista `fragments` con el texto original, sus offsets de carácter y la etiqueta ganadora de cada uno. El esquema completo, con un ejemplo real, está en `5_backend_contract.md`.

## 8. Seguridad y privacidad

- CORS restringido por configuración, nunca comodín.
- Máximo 100.000 caracteres de texto de entrada.
- Errores JSON controlados, con mensaje legible.
- Offsets siempre referidos al texto original, incluso cuando se traduce un fragmento internamente para clasificarlo.
- No se persisten políticas ni resultados en ninguna base de datos.
- La descarga de una URL resuelve el hostname antes de la petición y rechaza direcciones privadas, loopback, link-local o reservadas, mitigación directa de SSRF. No sigue redirecciones sin revalidar cada salto, y no ejecuta JavaScript.

## 9. Fuera del alcance actual

- Dictamen jurídico.
- Mapeo automático de cada categoría a su artículo del RGPD, el campo existe en el contrato pero devuelve un valor fijo.
- Historial persistente de análisis.
- Extensión de Chrome publicada en la Chrome Web Store, hoy se instala como paquete sin empaquetar.
- Traducción de español a inglés cuando no hay clave de Google Cloud Translation configurada en el entorno.
