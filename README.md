# PrivacyLens

PrivacyLens es un proyecto educativo que ayuda a comprender políticas de privacidad. Combina una interfaz React, una API FastAPI y experimentos de clasificación de texto basados en OPP-115.

> Los resultados son orientativos y no constituyen asesoramiento jurídico.
> ## WEB
> https://privacylens-project.onrender.com/
> https://privacylensproject.onrender.com/docs
> 

## Estado actual

| Área | Estado real |
|---|---|
| Frontend | Aplicación multipágina funcional con datos de demostración |
| Backend | API funcional con clasificador simulado y determinista |
| Modelo multietiqueta | Pipeline y varios modelos de experimentación disponibles |
| Experimento multiclase | Target de 10 clases y comparativa de tres modelos disponibles |
| Integración frontend-backend | Preparada mediante `/api`, pero desactivada con `USE_MOCK = true` |
| Análisis por URL | No implementado en el backend; responde HTTP 501 |
| Traducción, exposición y referencias RGPD | Interfaces presentes; lógica real pendiente |
| Extensión Chrome | Página pública informativa; no hay extensión empaquetable en esta rama |

## Funcionalidades del frontend

- Analizador y vista preliminar de resultados.
- Contenido educativo sobre riesgos, derechos RGPD y hábitos de privacidad.
- Diálogos accesibles en las tarjetas de riesgos y categorías.
- PrivacyLens Lab como presentación visual del proceso de IA.
- Página informativa de la futura extensión de Chrome.
- Navegación y footer compartidos y responsive.

## Arquitectura

```text
Navegador
   |
   v
React + Vite (frontend/, puerto 5173)
   |
   | /api mediante proxy de Vite
   v
FastAPI (backend/, puerto 8000)
   |
   +-- fragmentación por párrafos
   +-- detección heurística de idioma
   +-- probabilidades simuladas y deterministas
   +-- contrato JSON estable

Datos OPP-115 -> scripts/ -> data/processed/ y artifacts/ -> models/
```

El frontend usa actualmente los mocks de `frontend/src/services/mockData.js`. La API no participa en la experiencia visible mientras `USE_MOCK` permanezca activado.

## Estructura

| Ruta | Contenido |
|---|---|
| `frontend/` | Aplicación React, estilos, recursos locales y capa de servicios |
| `backend/` | API FastAPI y contrato de respuesta |
| `scripts/` | Preparación, partición, vectorización y validaciones de datos |
| `models/` | Entrenamiento y comparación de modelos |
| `data/` | OPP-115, datos procesados y dataset de evaluación externa |
| `artifacts/` | Matrices, vectorizador y modelos generados |
| `eda/` | Análisis exploratorio reproducible |
| `reports/` | Métricas y figuras generadas |
| `specs/` | Decisiones y contratos vigentes |

No existe una carpeta `docs/` ni configuración Docker en el repositorio actual.

## Requisitos

- Python 3.12 o superior.
- [`uv`](https://docs.astral.sh/uv/) para el entorno Python.
- Node.js y npm para el frontend.

## Instalación

Desde la raíz:

```bash
uv sync
cd frontend
npm install
```

Copie la configuración local del backend:

```bash
cp backend/.env.example backend/.env
```

En PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
```

## Ejecución

Terminal 1, desde la raíz:

```bash
uv run uvicorn backend.app.main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Abra `http://localhost:5173`.

## API disponible

| Método | Ruta | Estado |
|---|---|---|
| `GET` | `/api/health` | Implementado |
| `POST` | `/api/analyze` con `{"text": "..."}` | Implementado con stub |
| `POST` | `/api/analyze` con `{"url": "..."}` | No implementado; HTTP 501 |

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

Los scripts de entrenamiento y generación escriben archivos. Consulte sus README antes de ejecutarlos. El conjunto `data/dataset_extension/` está reservado para evaluación externa y demostración, no para entrenar los modelos documentados.

## Documentación

- [Frontend](frontend/README.md)
- [Backend](backend/README.md)
- [Modelos](models/README.md)
- [Scripts](scripts/README.md)
- [Datos](data/README.md)
- [Especificaciones](specs/README.md)
