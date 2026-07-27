# PrivacyLens Frontend

Frontend web de **PrivacyLens** — Legal AI que traduce políticas de privacidad a lenguaje claro.

## Stack técnico

- React 18
- React Router DOM (navegación entre páginas)
- Vite (servidor de desarrollo y build)

## Estructura del proyecto

```
src/
├── components/   # Componentes reutilizables (tarjetas, cajas de UI, etc.)
├── pages/        # Vistas / páginas de la app
├── services/     # Capa de acceso a datos (API y mocks)
├── config/       # Configuración de la app
├── styles/       # Estilos globales
├── App.jsx       # Componente raíz (rutas)
└── main.jsx      # Punto de entrada
```

## Páginas

| Página | Ruta | Estado | Descripción |
|---|---|---|---|
| `HomePage` | `/` | ✅ Funcional | Landing principal. Caja para pegar una URL, tarjeta de análisis de ejemplo, métricas del corpus/modelo y lista de análisis recientes. |
| `AnalysisPage` | `/analisis` | 🚧 Esqueleto (Fase 2) | Página de resultado ("radiografía" de la política): resumen, categorías detectadas, evidencias y artículos del RGPD relacionados. |
| `ModelPage` | `/modelo` | 🚧 Esqueleto (Fase 3) | Explica el modelo de IA: métricas del corpus y, más adelante, rendimiento por categoría. |
| `PlaceholderPage` | rutas futuras | 🚧 Genérica | Página "en construcción" para rutas que todavía no tienen vista propia (ej. categorías, extensión). |

## Conexión con el backend

Toda la comunicación con el backend pasa por `src/services/analysisService.js`. Los componentes **nunca** hacen `fetch` directamente, siempre llaman a este servicio.

Actualmente funciona en modo **mock** (`USE_MOCK = true` en `analysisService.js`), usando datos de ejemplo definidos en `src/services/mockData.js`.

Contrato de API previsto para cuando el backend esté disponible:

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/analyze` | Recibe `{ url }` y devuelve el resultado del análisis de la política. |
| `GET` | `/api/analyses/recent` | Devuelve los últimos análisis realizados. |
| `GET` | `/api/stats` | Devuelve las métricas globales del corpus y del modelo. |

Para conectar con el backend real:
1. Cambiar `USE_MOCK` a `false` en `analysisService.js`.
2. Verificar el proxy `/api` en `vite.config.js`.
3. Ajustar los nombres de campos si la API real difiere del mock.

## Instalación

```bash
npm install
```

## Ejecución en desarrollo

```bash
npm run dev
```

## Build de producción

```bash
npm run build
```

## Previsualizar build

```bash
npm run preview
```

## Roadmap

- **Fase 1** ✅ — Home funcional con datos mock.
- **Fase 2** 🚧 — Completar `AnalysisPage`: cobertura por categoría, evidencias, artículos RGPD, visor del documento original.
- **Fase 3** 🚧 — Completar `ModelPage`: gráficas de F1 por categoría y matriz de confusión, alimentadas por la API real.