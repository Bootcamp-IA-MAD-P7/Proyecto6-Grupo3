# Backend de PrivacyLens

API FastAPI que conserva el contrato de análisis definido en `specs/5_backend_contract.md`. En esta rama utiliza un generador determinista de probabilidades, no un modelo entrenado.

## Componentes

| Archivo | Responsabilidad |
|---|---|
| `app/main.py` | Aplicación, CORS y registro de rutas |
| `app/routes/health.py` | Comprobación de salud |
| `app/routes/analyze.py` | Validación de la petición |
| `app/analyze.py` | Orquestación del análisis |
| `app/chunker.py` | Fragmentación por párrafos y offsets |
| `app/stub.py` | Probabilidades simuladas con semilla derivada del texto |
| `app/translation.py` | Detección heurística y traducción no-op |
| `app/exposure.py` | Exposición fija de demostración |
| `app/gdpr.py` | Referencia RGPD pendiente |
| `app/schemas.py` | Modelos Pydantic del contrato |

## Configuración

Copie `backend/.env.example` a `backend/.env`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Se admiten varios orígenes separados por comas. No use `*`.

## Instalación y ejecución

Desde la raíz:

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

El texto vacío o superior a 100.000 caracteres produce HTTP 400. Enviar solo `url` produce HTTP 501 porque la descarga de políticas no está implementada.

## Funcionamiento real

1. Detecta `es` o `en` mediante una heurística.
2. La capa de traducción devuelve el texto sin modificar.
3. Divide el original por párrafos y conserva offsets reales.
4. Genera nueve probabilidades reproducibles por fragmento.
5. Aplica un umbral fijo de `0.5`.
6. Construye el contrato JSON con `stub: true` y versión `0.1.0`.

La exposición siempre es `medium` con score `0.5`; `gdpr_reference` siempre es `"TODO"`.

## Integración pendiente

Los modelos de `models/` no están conectados a esta API. Integrar uno requiere sustituir la fuente de probabilidades manteniendo los esquemas, revisar la correspondencia de clases y decidir cómo producir probabilidades. El experimento multiclase de diez clases tampoco está conectado al backend multietiqueta actual.

No existe Dockerfile ni configuración Docker Compose.
