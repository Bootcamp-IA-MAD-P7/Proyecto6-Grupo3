# SPEC 2 — Especificación funcional y técnica

## 1. Producto

PrivacyLens tiene tres capas independientes:

1. Una experiencia educativa React.
2. Una API FastAPI con un contrato de análisis.
3. Pipelines de datos y modelos experimentales.

En la rama actual estas capas no forman todavía un sistema de inferencia extremo a extremo: el frontend usa mocks y el backend usa un stub.

## 2. Frontend

### Rutas

| Ruta | Función |
|---|---|
| `/` | Inicio y entrada de URL de demostración |
| `/analisis` | Resultado preliminar |
| `/riesgos` | Educación sobre seis riesgos |
| `/rgpd` | Derechos RGPD y pasos para ejercerlos |
| `/aprende` | Recursos y hábitos |
| `/modelo` | PrivacyLens Lab |
| `/categorias` | Catálogo educativo interactivo |
| `/extension` | Presentación de la futura extensión |

El estado activo del navbar se resuelve con React Router. Navbar y footer son globales.

### Datos

`analysisService.js` mantiene `USE_MOCK = true`. Las estadísticas, análisis recientes y resultado de ejemplo proceden de `mockData.js`.

## 3. Backend

- FastAPI y Pydantic.
- Puerto local `8000`.
- `GET /api/health`.
- `POST /api/analyze`.
- Entrada válida actual: texto no vacío de hasta 100.000 caracteres.
- Entrada solo con URL: HTTP 501.
- CORS mediante `CORS_ALLOWED_ORIGINS`.

El análisis divide por párrafos, detecta idioma de forma heurística y produce probabilidades deterministas simuladas para nueve categorías.

## 4. Taxonomías

### Backend y entrenamiento multietiqueta

Nueve categorías OPP-115:

1. `first_party_collection_use`
2. `third_party_sharing_collection`
3. `user_choice_control`
4. `user_access_edit_deletion`
5. `data_retention`
6. `data_security`
7. `policy_change`
8. `do_not_track`
9. `international_specific_audiences`

### Experimento multiclase

Deriva una clase única mediante prioridad y añade `Other`. Es experimental y no está conectado a la API.

### Catálogo visual del frontend

El frontend muestra diez conceptos educativos con IDs simplificados. No existe todavía una capa de traducción formal entre esos IDs y las categorías del backend.

## 5. Datos y partición

- Entrenamiento: OPP-115.
- Clave: `(policy, segment)`.
- Split congelado por política: train, validación y test.
- TF-IDF se ajusta solo con train.
- `dataset_extension` se reserva para evaluación externa y demo.
- Test no se utiliza para selección de modelos.

## 6. Métricas

Para el enfoque multietiqueta se reportan macro-F1, micro-F1, F1 por etiqueta y gap train-validación. Para multiclase se reportan accuracy, macro-F1, F1 por clase y gaps.

## 7. Contrato de salida

La respuesta contiene:

- `model_version`
- `stub`
- `document`: idioma, traducción, exposición, categorías y número de fragmentos
- `fragments`: texto original, offsets y etiquetas

El esquema completo está en `5_backend_contract.md`.

## 8. Seguridad y privacidad

- CORS restringido por configuración.
- Máximo de 100.000 caracteres.
- Errores JSON controlados.
- Offsets referidos al texto original.
- No se persisten políticas en una base de datos.
- La descarga remota no está implementada, evitando introducir SSRF sin defensas.

## 9. Fuera del alcance actual

- Dictamen jurídico.
- Traducción real.
- Cálculo real de exposición.
- Mapeo automático RGPD.
- Historial persistente.
- Extensión Chrome empaquetada.
- Docker y despliegue automatizado.
