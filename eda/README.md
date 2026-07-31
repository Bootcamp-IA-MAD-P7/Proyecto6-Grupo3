# Análisis exploratorio

Scripts reproducibles sobre `data/processed/training_table.csv` y la partición congelada.

| Script | Análisis | Salida |
|---|---|---|
| `01_target_distribution.py` | Distribución y desbalance de las nueve etiquetas | `target_distribution.png` |
| `02_target_multilabel.py` | Número de etiquetas y coocurrencia | `multilabel_distribution.png`, `cooccurrence_heatmap.png` |
| `03_text_length_vocab.py` | Longitud de fragmentos y vocabulario | `50_longitud_texto.png` |
| `04_text_split_rare_classes.py` | Split por política y clases raras | `51_particion_politicas.png` |

Las figuras se guardan en `reports/figures/`.

## Conclusiones registradas

- OPP-115 es multietiqueta en origen.
- Existe un desbalance fuerte entre categorías.
- La división debe realizarse por política para evitar fuga de información.
- Macro-F1 es necesaria para no ocultar el rendimiento de clases minoritarias.
- La extensión moderna tiene muy pocos ejemplos de `do_not_track`.

El target multiclase del proyecto es una derivación posterior con regla de prioridad, no invalida la naturaleza multietiqueta del corpus original.

## Ejecución

Desde la raíz.

```bash
uv run python eda/01_target_distribution.py
uv run python eda/02_target_multilabel.py
uv run python eda/03_text_length_vocab.py
uv run python eda/04_text_split_rare_classes.py
```

También pueden abrirse por celdas en un editor compatible con el formato `# %%`.
