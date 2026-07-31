# PrivacyLens

PrivacyLens es un proyecto educativo que ayuda a comprender políticas de privacidad. Combina una interfaz React, una API FastAPI con un modelo entrenado, una extensión de Chrome y experimentos de clasificación de texto basados en OPP-115.

> Los resultados son orientativos y no constituyen asesoramiento jurídico.
> ## WEB
> https://privacylens-project.onrender.com/
> https://privacylensproject.onrender.com/docs
>

## Estado actual

| Área | Estado real |
|---|---|
| Frontend | Aplicación multipágina funcional, la página de análisis usa la API real |
| Backend | API con un modelo ComplementNB multiclase entrenado, sirve `artifacts/multiclass_complementnb.joblib` |
| Análisis por texto | Implementado |
| Análisis por URL | Implementado, con descarga guardada contra SSRF y extracción de texto |
| Extensión de Chrome | Funcional, analiza la pestaña activa contra el backend real |
| Traducción español a inglés | Implementada vía Google Cloud Translation, requiere una clave de API por variable de entorno, sin ella clasifica sin traducir |
| Exposición estimada | Calculada con una fórmula de pesos por categoría, no es un valor fijo |
| Referencias RGPD por categoría | Pendiente, la API devuelve un valor fijo, `"TODO"` |
| Análisis recientes y estadísticas de portada | Datos fijos de ejemplo, por decisión de diseño |
| Modelo multietiqueta y modelo multiclase | Ambos entrenados y comparados, en producción corre el multiclase |

## Funcionalidades del frontend

- Analizador de políticas por texto pegado o por URL.
- Contenido educativo sobre riesgos, derechos RGPD y hábitos de privacidad.
- Diálogos accesibles en las tarjetas de riesgos y categorías.
- PrivacyLens Lab, con las métricas reales de los modelos comparados.
- Página informativa de la extensión de Chrome.
- Navegación y footer compartidos y responsive.

## Arquitectura

```text
Navegador
   |
   v
React + Vite (frontend/, puerto 5173 en desarrollo)
   |
   | POST /api/analyze, URL absoluta en producción, proxy de Vite en desarrollo
   v
FastAPI (backend/, puerto 8000)
   |
   +-- fragmentación por párrafos
   +-- deteccion heurística de idioma
   +-- traducción español a inglés vía Google Cloud Translation, si hay API key
   +-- clasificación con ComplementNB multiclase entrenado (artifacts/)
   +-- exposición calculada por pesos de categoría
   +-- contrato JSON estable

Extensión de Chrome (extension/)
   |
   v
Misma API, POST /api/analyze, primero por URL, con el texto capturado
del navegador como respaldo si la página no se puede leer por descarga directa

Datos OPP-115 -> scripts/ -> data/processed/ y artifacts/ -> models/
```

La portada del frontend sigue usando los datos fijos de `frontend/src/services/mockData.js` para análisis recientes y estadísticas, esos dos bloques no consultan la API por decisión de diseño, documentada en el propio código. La página de análisis sí consulta la API real.

## Estructura

| Ruta | Contenido |
|---|---|
| `frontend/` | Aplicación React, estilos, recursos locales y capa de servicios |
| `backend/` | API FastAPI, modelo servido y contrato de respuesta |
| `extension/` | Extensión de Chrome (MV3) |
| `scripts/` | Preparación, partición, vectorización y validaciones de datos |
| `models/` | Entrenamiento y comparación de modelos |
| `data/` | OPP-115, datos procesados y dataset de evaluación externa |
| `artifacts/` | Matrices, vectorizador y modelos generados |
| `eda/` | Análisis exploratorio reproducible |
| `reports/` | Métricas y figuras generadas |
| `specs/` | Decisiones y contratos vigentes |

No existe una carpeta `docs/` ni configuración Docker en el repositorio actual. El backend y el frontend se despliegan por separado en Render, como dos servicios distintos.

## Requisitos

- Python 3.12 o superior.
- [`uv`](https://docs.astral.sh/uv/) para el entorno Python.
- Node.js y npm para el frontend.

## Instalación

Desde la raíz.

```bash
uv sync
cd frontend
npm install
```

Copie la configuración local del backend.

```bash
cp backend/.env.example backend/.env
```

En PowerShell.

```powershell
Copy-Item backend/.env.example backend/.env
```

`GOOGLE_TRANSLATE_API_KEY` es opcional en `backend/.env`, sin ella el texto en español se clasifica sin traducir. Para builds de producción del frontend, `VITE_API_BASE_URL` debe apuntar al backend desplegado, en desarrollo local se puede dejar sin definir porque `vite.config.js` reenvía `/api` al backend local.

## Ejecución

Terminal 1, desde la raíz.

```bash
uv run uvicorn backend.app.main:app --reload --port 8000
```

Terminal 2.

```bash
cd frontend
npm run dev
```

Abra `http://localhost:5173`.

Para la extensión, cargue la carpeta `extension/` sin empaquetar desde `chrome://extensions`, con el modo desarrollador activado. Por defecto apunta al backend desplegado en Render, no al backend local.

## API disponible

| Método | Ruta | Estado |
|---|---|---|
| `GET` | `/api/health` | Implementado |
| `POST` | `/api/analyze` con `{"text": "..."}` | Implementado, modelo real |
| `POST` | `/api/analyze` con `{"url": "..."}` | Implementado, descarga y extrae el texto de la página |

## Comandos útiles

```bash
# Build del frontend
cd frontend
npm run build

# Inspección del corpus
uv run python scripts/01_inspect_opp115.py

# Pipeline multietiqueta
uv run python scripts/02_build_target.py
uv run python scripts/03_prepare_evaluation_set.py
uv run python scripts/04_build_split.py
uv run python scripts/05_vectorize.py
uv run python scripts/06_smoke_test.py

# Experimento multiclase
uv run python scripts/10_build_multiclass_target.py
uv run python models/11_multiclass_baseline.py
uv run python models/12_multiclass_compare.py
```

Los scripts de entrenamiento y generación escriben archivos. Consulte sus README antes de ejecutarlos. El conjunto `data/dataset_extension/` está reservado para evaluación externa y demostración, no para entrenar los modelos documentados. Entrenar de nuevo el modelo multiclase, con `models/04_deberta.py` incluido, requiere las dependencias del extra `training`, instalable con `uv sync --extra training`.

## Documentación

- [Frontend](frontend/README.md)
- [Backend](backend/README.md)
- [Modelos](models/README.md)
- [Scripts](scripts/README.md)
- [Datos](data/README.md)
- [Especificaciones](specs/README.md)
- [Revisión técnica completa](AUDITORIA_TECNICA.md)
