# SPEC 1. Intención del proyecto

## Propósito

PrivacyLens es una herramienta educativa para facilitar la lectura de políticas de privacidad. Presenta prácticas de tratamiento de datos, derechos RGPD y riesgos habituales mediante lenguaje accesible.

No determina cumplimiento legal, no emite dictámenes y no sustituye asesoramiento jurídico.

## Usuarios

- Personas que quieren entender una política antes de aceptar.
- Estudiantes y docentes interesados en privacidad e IA.
- Equipo del proyecto, que compara enfoques de clasificación sobre OPP-115.

## Alcance implementado

- Aplicación React responsive con páginas educativas.
- Catálogos interactivos de riesgos y categorías.
- Páginas RGPD, Aprende y PrivacyLens Lab.
- API FastAPI con un modelo real entrenado (ComplementNB multiclase, 10 categorías), que analiza texto pegado directamente o el texto de una URL.
- Extensión de Chrome (MV3) que analiza la página activa desde el propio navegador, conectada a esa misma API.
- Pipeline OPP-115, EDA y experimentos multietiqueta y multiclase.
- Dataset moderno propio, separado para evaluación externa y demostración.

## Límites actuales

- Las estadísticas y los análisis recientes de la portada son datos fijos por decisión de diseño, no hay base de datos de análisis persistente ni está prevista.
- El mapeo de cada categoría a su artículo del RGPD no está implementado, la API devuelve un valor fijo para ese campo.
- La traducción de español a inglés antes de clasificar depende de una clave de API de Google Cloud Translation puesta como variable de entorno, sin ella el texto en español se clasifica sin traducir.
- La taxonomía visual del catálogo de categorías del frontend usa identificadores propios que no coinciden con las categorías reales del backend.
- PrivacyLens Lab presenta módulos visuales, pero no tiene submódulos funcionales.
- No hay Dockerfile ni configuración Docker Compose en el repositorio, el backend y el frontend se despliegan por separado en Render.

## Principios

- Transparencia sobre qué resultado es cálculo real y cuál sigue siendo contenido educativo u orientativo.
- Separación estricta entre entrenamiento y evaluación externa.
- Reproducibilidad mediante splits y artefactos compartidos.
- Seguridad básica, límite de longitud de texto, CORS configurado por entorno sin comodín, validación de la URL antes de descargarla, errores legibles.
- Accesibilidad y lenguaje comprensible.
