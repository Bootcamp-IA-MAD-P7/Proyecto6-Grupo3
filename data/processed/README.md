# Datos procesados

Archivos derivados de los pipelines:

| Archivo | Contenido |
|---|---|
| `training_table.csv` | 3.792 fragmentos OPP-115, texto y nueve etiquetas binarias |
| `split_assignment.csv` | Asignación `train`, `val` o `test` por `(policy, segment)` |
| `evaluation_es.csv` | Evaluación externa en español |
| `evaluation_en.csv` | Evaluación externa en inglés |
| `multiclass_target.csv` | Target experimental de diez clases, si se genera |

`multiclass_target.csv` no está presente actualmente en esta rama. Se crea con:

```bash
uv run python scripts/10_build_multiclass_target.py
```

No mezcle las evaluaciones externas con train, validación o test.
