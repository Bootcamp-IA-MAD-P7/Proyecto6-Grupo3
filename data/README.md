# Datos de PrivacyLens

## Estructura

| Carpeta | Rol |
|---|---|
| `dataset/` | Corpus original OPP-115 y anotaciones |
| `processed/` | Tablas derivadas por los scripts |
| `dataset_extension/` | Políticas actuales para evaluación externa, exploración y demo |

## Separación de usos

- El entrenamiento documentado utiliza OPP-115.
- `dataset_extension/` no se combina con `training_table.csv`.
- Los conjuntos `evaluation_es.csv` y `evaluation_en.csv` son externos al split de entrenamiento.
- Las etiquetas automáticas de la extensión no deben tratarse como gold standard sin revisión humana.

Los archivos derivados pueden regenerarse. Consulte `scripts/README.md` y `specs/4_data_contract.md`.
