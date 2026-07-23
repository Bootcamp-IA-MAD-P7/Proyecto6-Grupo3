# Scripts
 
## Qué hay
 
| Script | Qué hace | Escribe en |
|---|---|---|
| `01_inspect_opp115.py` | Imprime la estructura real del dataset descargado. Solo lee, no escribe nada | — |
| `02_build_target.py` | Cruza fragmentos con anotaciones y construye la tabla de entrenamiento | `data/processed/` |
 | `03_prepare_evaluation_set.py` | Deduplica la extensión y la convierte al esquema de la tabla de entrenamiento, separada por idioma | `data/processed/` |
| `34_untrack_external.sh` | Saca del rastreo git los datasets externos (ejecutado 23/7 tras contención del #34) | — |
| `alinear_tablero_v2.sh` / `sub_issues_5.sh` | Utilitarios de un solo uso para el tablero de GitHub (ya ejecutados) | — |
Al añadir un script nuevo, se añade su fila aquí.