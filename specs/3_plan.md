# SPEC 3 — Estado y plan

Este documento registra el estado observable; no promete funcionalidades no implementadas.

## Completado

- Preparación multietiqueta de OPP-115.
- Split agrupado y vectorización TF-IDF.
- EDA y figuras principales.
- Implementaciones LinearSVC, ComplementNB, LightGBM y DeBERTa.
- Derivación y comparación multiclase.
- API FastAPI con health, validación, fragmentación y contrato.
- Frontend multipágina responsive.
- Contenido de Riesgos, RGPD, Aprende, PrivacyLens Lab y Categorías.
- Diálogos accesibles en Riesgos y Categorías.

## Parcial

| Área | Situación |
|---|---|
| Analizador web | Flujo visual basado en mocks |
| Página de resultados | Vista preliminar |
| Backend | Contrato real con probabilidades simuladas |
| PrivacyLens Lab | Tarjetas de acceso sin contenido navegable |
| Extensión | Página promocional, sin paquete Chrome |
| Evaluación externa | Datos preparados, pendientes de validación humana suficiente |

## Pendiente para integración

1. Elegir formalmente enfoque y modelo de producción.
2. Generar y versionar o distribuir el artefacto servible correspondiente.
3. Conectar el backend al modelo y validar el orden de clases.
4. Adaptar el frontend al contrato real de texto o implementar descarga segura de URL.
5. Sustituir mocks sin depender de endpoints inexistentes.
6. Alinear las taxonomías visual y técnica.
7. Añadir pruebas automatizadas.
8. Implementar, si se decide, traducción, exposición y referencias RGPD.

## Criterios antes de declarar integración completa

- Un clon limpio puede instalar y arrancar ambos procesos.
- El artefacto requerido por el backend existe.
- Una petición real llega desde el frontend y muestra la respuesta sin adaptación manual.
- No se utiliza test para elegir modelo.
- La documentación indica con precisión qué es cálculo real y qué es contenido educativo.
