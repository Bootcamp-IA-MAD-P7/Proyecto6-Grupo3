# SPEC 5 — Contrato del backend

## Estado

Implementado en `backend/` con FastAPI. La estructura de respuesta es real; las probabilidades, traducción, exposición y referencias RGPD no lo son todavía.

## Configuración

- Python 3.12 o superior.
- Ejecución con `uv`.
- Puerto local: `8000`.
- Variable obligatoria: `CORS_ALLOWED_ORIGINS`.
- Límite fijo: 100.000 caracteres.

## Endpoints

### `GET /api/health`

Respuesta:

```json
{"status": "ok"}
```

### `POST /api/analyze`

Entrada implementada:

```json
{"text": "Policy text"}
```

También existe el campo opcional `url`, pero una petición sin texto y con URL devuelve HTTP 501.

## Respuesta

```json
{
  "model_version": "0.1.0",
  "stub": true,
  "document": {
    "source_language": "en",
    "translated": false,
    "translation_available": true,
    "exposure": {
      "level": "medium",
      "score": 0.5,
      "disclaimer": "Estimacion basada en los temas detectados, no en una lectura clausula por clausula."
    },
    "categories": [
      {
        "id": "first_party_collection_use",
        "present": true,
        "confidence": 0.75,
        "fragment_count": 2,
        "gdpr_reference": "TODO"
      }
    ],
    "fragment_count": 2
  },
  "fragments": [
    {
      "id": 0,
      "text": "Original paragraph",
      "start": 0,
      "end": 18,
      "labels": [
        {
          "id": "first_party_collection_use",
          "score": 0.75
        }
      ]
    }
  ]
}
```

La lista `categories` contiene entradas para las nueve categorías, aunque el ejemplo muestre una.

## Reglas implementadas

- `text`, `start` y `end` siempre se refieren al original.
- Fragmentación por saltos de párrafo.
- Misma entrada, mismas probabilidades simuladas.
- Etiqueta presente con score mayor o igual a `0.5`.
- `stub` es `true`.
- Traducción no-op y detección heurística `es`/`en`.
- Exposición fija `medium`/`0.5`.
- Referencia RGPD `"TODO"`.

## Errores

| Caso | HTTP |
|---|---:|
| Sin texto ni URL | 400 |
| Texto vacío | 400 |
| Más de 100.000 caracteres | 400 |
| Solo URL | 501 |
| Error inesperado | 500 con JSON legible |

## Seguridad

- CORS no permite comodín.
- La configuración se lee de `backend/.env`.
- No hay persistencia de textos.
- No hay fetch remoto ni superficie SSRF implementada.

## Integración con modelos

La API importa `app.stub`, no los artefactos de `artifacts/`. El contrato espera scores por categoría, pero no fija todavía un modelo de producción. Antes de sustituir el stub hay que:

1. Elegir multietiqueta o multiclase.
2. Alinear el número y orden de clases.
3. Producir scores compatibles.
4. Mantener offsets y texto original.
5. Cambiar `model_version` y `stub`.
6. Añadir pruebas del contrato.
