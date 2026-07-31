# Backend de PrivacyLens

API FastAPI que implementa el contrato de análisis definido en `specs/5_backend_contract.md`, respaldada por un modelo ComplementNB multiclase entrenado sobre OPP-115.

## Componentes

| Archivo | Responsabilidad |
|---|---|
| `app/main.py` | Aplicación, CORS y registro de rutas |
| `app/routes/health.py` | Comprobación de salud |
| `app/routes/analyze.py` | Validación de la petición |
| `app/analyze.py` | Orquestación del análisis |
| `app/chunker.py` | Fragmentación por párrafos y offsets |
| `app/predictor.py` | Carga el modelo y el vectorizador, ejecuta la inferencia |
| `app/fetcher.py` | Descarga y limpia el texto de una URL, con guardas contra SSRF |
| `app/translation.py` | Detección heurística de idioma y traducción español a inglés vía Google Cloud Translation |
| `app/exposure.py` | Cálculo del nivel de exposición por pesos de categoría |
| `app/gdpr.py` | Referencia RGPD, pendiente, devuelve un valor fijo |
| `app/schemas.py` | Modelos Pydantic del contrato |
| `app/stub.py` | Generador de probabilidades simuladas, sin uso, ningún módulo lo importa |

## Configuración

Copie `backend/.env.example` a `backend/.env`.

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173
GOOGLE_TRANSLATE_API_KEY=
```

`CORS_ALLOWED_ORIGINS` admite varios orígenes separados por comas, nunca `*`. `GOOGLE_TRANSLATE_API_KEY` es opcional, sin ella el texto en español se clasifica sin traducir, en vez de fallar.

## Instalación y ejecución

Desde la raíz.

```bash
uv sync
uv run uvicorn backend.app.main:app --reload --port 8000
```

## Endpoints

### Salud

```bash
curl http://localhost:8000/api/health
```

### Análisis de texto

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"We collect account data.\\n\\nWe share data with providers.\"}"
```

### Análisis por URL

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://example.com/privacy\"}"
```

El texto vacío o superior a 100.000 caracteres produce HTTP 400. Una URL que resuelve a una dirección privada o reservada produce HTTP 400, antes de intentar la descarga. Si el texto extraído de la página queda por debajo de 500 caracteres útiles, típico de páginas que cargan contenido con JavaScript, la respuesta es 422.

## Funcionamiento real

1. Detecta `es` o `en` mediante una heurística.
2. Si el idioma es español y hay `GOOGLE_TRANSLATE_API_KEY` configurada, traduce cada fragmento a inglés antes de clasificarlo, en caché por texto dentro del mismo proceso. Sin la clave, o si la llamada falla, sigue en español sin interrumpir el análisis.
3. Divide el original por párrafos y conserva offsets reales sobre el texto sin traducir.
4. Vectoriza cada fragmento con el TF-IDF entrenado y calcula las probabilidades de las diez clases con el modelo ComplementNB cargado desde `artifacts/`.
5. Cada fragmento gana la clase de mayor probabilidad, sin umbral de decisión.
6. Calcula la exposición del documento con la fórmula de pesos de `app/exposure.py`, no es un valor fijo.
7. Construye el contrato JSON con `stub: false` y versión `1.0.0`.

`gdpr_reference` sigue siendo `"TODO"` para cualquier categoría, esa parte no está implementada.

## Carga del modelo

`app/predictor.py` carga `artifacts/tfidf_vectorizer.joblib` y `artifacts/multiclass_complementnb.joblib` en la primera petición de análisis, no al arrancar el proceso. Si esos archivos faltan, esa primera petición devuelve un 500 genérico, el mensaje descriptivo que el propio módulo genera no llega a quien hizo la petición, el manejador de errores no distingue ese caso de cualquier otro fallo inesperado.

No existe Dockerfile ni configuración Docker Compose, el despliegue en Render corre directamente sobre el entorno de `uv`.
