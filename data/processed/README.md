# data/processed/ — datos derivados; se regeneran con los scripts. No se versionan.


Datos **derivados**: los generan los scripts a partir de `data/dataset/` y
`data/dataset_extension/`. No se versionan — se regeneran con un comando.

## training_table.csv — la lección (entrenamiento)

Una fila por fragmento de OPP-115, con su texto y 9 columnas de etiqueta (0/1).

```bash
uv run python scripts/02_build_target.py
```

Decisiones dentro (detalle en `specs/2_spec.md` §2): consolidación con umbral
**0.75** · `Other` no es columna (fragmentos solo-Other conservados a cero) ·
multi-etiqueta (media 1,23 etiquetas/fila).

Referencia: 115 políticas · 3.792 filas · 9 etiquetas · desbalance 47:1.

## evaluation_es.csv / evaluation_en.csv — el examen (evaluación)

Párrafos de la extensión (políticas reales de 2026) en el **mismo esquema** que
la tabla de entrenamiento, más `language` y `label_source`.

```bash
uv run python scripts/03_prepare_evaluation_set.py
```

  Sus etiquetas son **de plata** (motor de reglas, sin validación humana):
sirven de referencia, **nunca para entrenar ni para medir como verdad**
(`specs/2_spec.md` §11). Referencia: 10.797 → 7.363 filas tras deduplicar
(3.434 exactos) · es: 5.385 · en: 1.978.

Fuentes crudas: `data/dataset/README.md` y `data/dataset_extension/README.md`.