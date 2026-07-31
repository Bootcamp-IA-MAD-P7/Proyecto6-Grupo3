# Datos procesados

Archivos derivados de los pipelines.

| Archivo | Contenido |
|---|---|
| `training_table.csv` | 3.792 fragmentos OPP-115, texto y nueve etiquetas binarias |
| `split_assignment.csv` | Asignación `train`, `val` o `test` por `(policy, segment)` |
| `evaluation_es.csv` | Evaluación externa en español |
| `evaluation_en.csv` | Evaluación externa en inglés |
| `multiclass_target.csv` | Target de diez clases, el que consumen los modelos multiclase, incluido el que sirve la API en producción |

`multiclass_target.csv` ya está generado en esta rama. Se regenera con este comando, si hace falta.

```bash
uv run python scripts/10_build_multiclass_target.py
```

No mezcle las evaluaciones externas con train, validación o test.
