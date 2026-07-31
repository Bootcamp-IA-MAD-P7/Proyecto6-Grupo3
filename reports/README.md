# Informes y figuras

Resultados derivados de EDA y entrenamiento.

## Archivos actuales

| Ruta | Origen |
|---|---|
| `figures/target_distribution.png` | `eda/01_target_distribution.py` |
| `figures/multilabel_distribution.png` | `eda/02_target_multilabel.py` |
| `figures/cooccurrence_heatmap.png` | `eda/02_target_multilabel.py` |
| `figures/50_longitud_texto.png` | `eda/03_text_length_vocab.py` |
| `figures/51_particion_politicas.png` | `eda/04_text_split_rare_classes.py` |
| `lightgbm_metrics.json` | `models/03_lightgbm.py` |
| `multiclass_comparison.csv` | `models/12_multiclass_compare.py` |
| `test_evaluation.json` | `models/14_evaluate_test_and_extension.py`, modelo de producción sobre el split test de OPP-115 |
| `dataset_extension_evaluation.json` | `models/14_evaluate_test_and_extension.py`, modelo de producción sobre `dataset_extension`, con la salvedad de que las etiquetas de comparación son preanotación automática, no humana |

Son resultados reproducibles, no entradas de la aplicación. Ejecutar de nuevo los scripts correspondientes puede sobrescribirlos. `models/14_evaluate_test_and_extension.py` en particular no está pensado para correrse por rutina.
