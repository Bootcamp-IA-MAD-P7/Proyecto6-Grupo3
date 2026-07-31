# SPEC 3. Estado y plan

Este documento registra el estado observable, no promete funcionalidades no implementadas.

## Completado

- Preparación multietiqueta de OPP-115.
- Split agrupado y vectorización TF-IDF.
- EDA y figuras principales.
- Implementaciones LinearSVC, ComplementNB, LightGBM y DeBERTa, en modo multietiqueta.
- Derivación y comparación multiclase, con ComplementNB elegido como modelo de producción.
- API FastAPI con modelo real cargado desde `artifacts/`, análisis por texto y por URL, exposición calculada, y contrato estable.
- Extensión de Chrome (MV3) que analiza la pestaña activa y llama a la API real desplegada en Render.
- Descarga de URL en el backend con guardas SSRF, extracción de texto y detección de contenido cargado por JavaScript.
- Traducción de español a inglés antes de clasificar, vía la API de Google Cloud Translation, verificada funcionando de extremo a extremo en un backend local.
- Evaluación final del modelo de producción sobre el split test de OPP-115, 663 filas nunca usadas hasta ahora, accuracy 0,6968, macro-F1 0,6753.
- Primera comparación automática del modelo de producción contra `dataset_extension`, documentada con su salvedad de etiquetas no humanas, en `models/README.md`.
- Frontend multipágina responsive, con la página de análisis conectada a la API real.
- Contenido de Riesgos, RGPD, Aprende, PrivacyLens Lab y Categorías.
- Diálogos accesibles en Riesgos y Categorías.

## Parcial

| Área | Situación |
|---|---|
| Traducción | Funciona en un backend local con la clave puesta, verificado con una petición real. En el backend desplegado en Render la clave todavía no está configurada, así que ahí el español se sigue clasificando sin traducir |
| Frontend, portada | Análisis recientes y estadísticas siguen siendo datos fijos, por decisión de diseño |
| Taxonomía visual | El catálogo educativo de `/categorias` usa identificadores propios, sin traducción formal a las categorías reales del backend |
| Referencias RGPD | El campo existe en cada categoría de la respuesta, devuelve siempre `"TODO"` |
| PrivacyLens Lab | Tarjetas de acceso con métricas reales, sin submódulos navegables |
| Frontend en producción | Desplegado en Render como sitio estático, depende de que `VITE_API_BASE_URL` esté puesta en el entorno de build de ese servicio |
| Evaluación externa | Comparación automática hecha contra el modelo de producción, macro-F1 0,2266 en español traducido, 0,3473 en inglés. Sigue sin validación humana de las etiquetas de `dataset_extension`, así que no sustituye una evaluación real de calidad |

## Pendiente

1. Aplicar el mapeo de Poplavska et al. (2020) en `gdpr.py`, hoy es un placeholder fijo.
2. Alinear los identificadores de `frontend/src/config/categories.js` con las diez categorías reales del backend.
3. Añadir pruebas automatizadas sobre el contrato de la API.
4. Decidir si el histórico de análisis pasa a ser persistente, y con qué almacenamiento, o si se mantiene como decisión permanente de no guardar textos analizados.
5. Publicar la extensión en la Chrome Web Store, o mantenerla como paquete de instalación manual.

## Criterios antes de declarar la integración completa

- Un clon limpio puede instalar y arrancar ambos procesos.
- El artefacto requerido por el backend existe y se carga sin error.
- Una petición real llega desde el frontend y desde la extensión, y muestra la respuesta sin adaptación manual.
- No se utiliza el conjunto de test para elegir modelo.
- El conjunto de test, una vez usado para la evaluación final, no se vuelve a usar para ajustar el modelo.
- La documentación indica con precisión qué es cálculo real y qué sigue siendo contenido educativo o dato de ejemplo.

Todos estos criterios se cumplen a fecha de esta revisión, salvo la traducción real en el backend desplegado, que cumple el criterio de código, verificado también en local, pero no el de configuración en Render, porque la clave de API todavía no está puesta en ese servicio.
