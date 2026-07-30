# SPEC 1 — Intención del proyecto

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
- Página RGPD, Aprende y PrivacyLens Lab.
- API FastAPI con contrato estable y predicción simulada.
- Pipeline OPP-115, EDA y experimentos multietiqueta y multiclase.
- Dataset moderno separado para evaluación externa y demostración.

## Límites actuales

- La interfaz funciona con mocks y no consume el backend.
- El backend no descarga URLs ni ejecuta modelos entrenados.
- Traducción, exposición y mapeo RGPD son placeholders.
- PrivacyLens Lab presenta módulos visuales, pero no tiene submódulos funcionales.
- No existe una extensión Chrome instalable en esta rama.
- No existe despliegue ni Docker documentable desde el código actual.

## Principios

- Transparencia sobre datos simulados y resultados orientativos.
- Separación estricta entre entrenamiento y evaluación externa.
- Reproducibilidad mediante splits y artefactos compartidos.
- Seguridad básica: límite de texto, CORS configurado y errores legibles.
- Accesibilidad y lenguaje comprensible.
