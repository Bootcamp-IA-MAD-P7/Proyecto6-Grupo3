# SPEC 5. Contrato del backend

## Estado

Implementado en `backend/` con FastAPI. La estructura de respuesta, las probabilidades del modelo y la exposición calculada son reales. La traducción es real pero depende de una clave de API configurada por entorno. La referencia RGPD por categoría sigue siendo un valor fijo.

## Configuración

- Python 3.12 o superior.
- Ejecución con `uv`.
- Puerto local, `8000`.
- Variable obligatoria, `CORS_ALLOWED_ORIGINS`.
- Variable opcional, `GOOGLE_TRANSLATE_API_KEY`, sin ella el texto en español se clasifica sin traducir, sin error.
- Límite fijo, 100.000 caracteres, no configurable por entorno.

## Endpoints

### `GET /api/health`

Respuesta.

```json
{"status": "ok"}
```

### `POST /api/analyze`

Entrada, con texto directo.

```json
{"text": "Policy text"}
```

Entrada, con URL. El backend descarga la página, la limpia y extrae su texto.

```json
{"url": "https://example.com/privacy"}
```

Si llegan ambos campos, se usa `text` y se ignora `url`. Si `text` llega vacío o ausente y hay `url`, se intenta la descarga.

## Respuesta

Ejemplo real, generado contra el backend desplegado.

```json
{
  "model_version": "1.0.0",
  "stub": false,
  "document": {
    "source_language": "en",
    "translated": false,
    "translation_available": true,
    "exposure": {
      "level": "medium",
      "score": 1.0,
      "disclaimer": "Estimacion basada en los temas detectados, no en una lectura clausula por clausula."
    },
    "categories": [
      {
        "id": "third_party_sharing_collection",
        "present": true,
        "confidence": 0.7147,
        "fragment_count": 1,
        "gdpr_reference": "TODO"
      }
    ],
    "fragment_count": 2
  },
  "fragments": [
    {
      "id": 0,
      "text": "We share your personal data with third-party advertising partners.",
      "start": 0,
      "end": 66,
      "labels": [
        {
          "id": "third_party_sharing_collection",
          "score": 0.7147
        }
      ]
    }
  ]
}
```

La lista `categories` siempre trae las diez categorías de `backend/app/categories.py`, presentes o no, aunque el ejemplo muestre una sola por brevedad.

## Reglas implementadas

- `text`, `start` y `end` siempre se refieren al texto original, incluso en los fragmentos que se tradujeron internamente para clasificarlos.
- Fragmentación por saltos de párrafo dobles.
- Cada fragmento gana una sola etiqueta, la de mayor probabilidad entre las diez clases, no hay umbral de decisión.
- `stub` es siempre `false`.
- `model_version` es `"1.0.0"`.
- La exposición se calcula con una fórmula de pesos por categoría, documentada en `backend/app/exposure.py`, no es un valor fijo.
- La traducción es real cuando hay clave de API configurada, se degrada a texto sin traducir cuando no la hay o cuando la llamada falla, en ningún caso interrumpe el análisis.
- Referencia RGPD, `"TODO"` para cualquier categoría, sin excepción.

## Errores

| Caso | HTTP |
|---|---:|
| Sin texto ni URL | 400 |
| Texto vacío | 400 |
| Más de 100.000 caracteres | 400 |
| URL con esquema distinto de http o https | 400 |
| URL que resuelve a una dirección privada, loopback o reservada | 400 |
| La página tarda más de 10 segundos en responder | 504 |
| La página no se puede descargar, o supera 5 MB | 502 |
| La página bloquea la petición con 403 | 502, con mensaje que sugiere usar la extensión |
| Menos de 500 caracteres útiles tras extraer el texto de la página | 422 |
| Error inesperado | 500, con JSON legible, sin detalle interno |

## Seguridad

- CORS no permite comodín en ningún entorno.
- La configuración se lee de `backend/.env`, o de las variables de entorno del servicio en Render.
- No hay persistencia de textos ni de resultados.
- La descarga de una URL resuelve el hostname antes de la petición y revalida cada salto de redirección, hasta un máximo de 3 saltos, sin ejecutar JavaScript en ningún punto.

## Integración con modelos

`backend/app/predictor.py` carga `artifacts/multiclass_complementnb.joblib` y `artifacts/tfidf_vectorizer.joblib` la primera vez que se le pide una predicción, no al arrancar la aplicación. Si esos archivos no existen, la primera petición de análisis falla con un 500 genérico, aunque `predictor.py` sí genera internamente un mensaje descriptivo, ese mensaje no llega a quien hizo la petición porque el manejador de errores no distingue ese caso de cualquier otro fallo inesperado.

`backend/app/stub.py` sigue en el árbol del repositorio, genera probabilidades pseudoaleatorias deterministas por hash del texto. Ningún módulo lo importa.
