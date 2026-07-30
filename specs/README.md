# Especificaciones de PrivacyLens

Estas especificaciones describen el estado implementado y separan las decisiones vigentes de las líneas futuras.

| Archivo | Contenido |
|---|---|
| `1_intent.md` | Objetivo, límites y principios del producto |
| `2_spec.md` | Funcionalidad y arquitectura actuales |
| `3_plan.md` | Estado por área y trabajo pendiente |
| `4_data_contract.md` | Datos, splits, artefactos y categorías |
| `5_backend_contract.md` | API FastAPI y contrato JSON |

## Fuentes de verdad

1. El código y los archivos presentes en la rama actual.
2. `4_data_contract.md` para pipelines y artefactos.
3. `5_backend_contract.md` para la API.

El experimento multiclase no sustituye automáticamente el contrato multietiqueta del backend. Cualquier cambio de enfoque debe alinear código, artefactos, categorías del frontend y contrato de API.
