# specs — decisions, glossary, OPP-115 to GDPR mapping, exposure-level logic
# specs — decisions, OPP-115 to GDPR mapping, exposure-level logic

## Qué hay

| Archivo | Responde a |
|---|---|
| `1_intent.md` | Por qué existe el proyecto, qué es el mínimo protegido y qué es aspiracional |
| `2_spec.md` | Qué se construye. **El documento que manda:** target, métricas, partición, contrato de salida, limitaciones, alcance |
| `3_plan.md` | Cómo y cuándo: fases, frentes de trabajo, orden de corte si falta tiempo |
| `4_data_contract.md` | El contrato de datos en formato **pegable**. Lo que hay que dar a un asistente de IA antes de escribir código |
| `GLOSSARY.md` | Glosario del equipo. Vive como documento compartido y se congela aquí al cerrar cada sprint (ver `1_intent`) |

## Por dónde empezar

- **Si vas a escribir código:** `4_data_contract.md`. Pega el bloque en tu IA antes de
  pedirle nada. Sin eso, cualquier asistente te va a proponer un `train_test_split` que
  rompe la partición del proyecto.
- **Si vas a decidir algo:** `2_spec.md`. Si tu decisión lo contradice, se cambia la
  spec o se cambia la decisión, nunca conviven las dos versiones.
- **Si quieres saber qué toca hoy:** `3_plan.md` y el tablero.

## Cómo se cambia una spec

- Se abre una rama y un PR. No se edita directamente sobre la rama de integración.
- Se sube la versión del documento (0.2 -> 0.3).
- Se añade una entrada al historial de cambios del propio documento.
- Se revisa como se revisa el código.

## Si una tarea se bloquea por lo que dice una spec

Se para y **se dice** — en la daily o en el issue, no en la cabeza de nadie. El equipo
decide cuál de los tres casos es:

1. La spec está desactualizada -> se cambia la spec.
2. La spec está bien, la tarea no cabe -> se cambia la tarea, no el criterio.
3. Ambas están bien pero el criterio no se cumple -> **se documenta el bloqueo**: qué
   criterio, por qué no se cumple, qué se intentó.

Un bloqueo explicado se defiende; un resultado maquillado no.

Lo que nunca se hace es seguir trabajando contra una spec que se ha decidido ignorar
por cuenta propia.

## Convención de idioma

Estos documentos están **en español** porque su público son personas.

**En inglés va todo lo interno del repo:** nombres de carpetas y archivos, nombres de
variables y funciones, **nombres de columnas de los datasets**, nombres de rama,
mensajes de commit y comentarios de código.

**En español pueden ir** las conversaciones (issues, dailies), los entregables para
humanos (informe, presentaciones) y estas specs.

## Una nota sobre por qué existe esta carpeta

Las tres cosas que más tiempo han costado en este proyecto han sido, en los tres casos,
un acuerdo que existía en la cabeza de alguien y no en un archivo: el nombre de una
columna, cuál era la partición válida, y qué archivos se versionan. Escribirlo aquí es
más rápido que volver a discutirlo.