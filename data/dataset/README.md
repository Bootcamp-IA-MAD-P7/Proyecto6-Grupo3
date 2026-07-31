# Corpus OPP-115

Esta carpeta contiene los textos y anotaciones originales utilizados para construir el conjunto de entrenamiento.

## Verificación

Desde la raíz.

```bash
uv run python scripts/01_inspect_opp115.py
```

El script valida la presencia de políticas y anotaciones. Sin las anotaciones no puede generarse `training_table.csv`.

## Fuente

OPP-115 puede obtenerse en [Usable Privacy Project](https://usableprivacy.org/data).

Referencia.

> Wilson, S. et al. (2016). *The Creation and Analysis of a Website Privacy Policy Corpus*. ACL 2016.

El mapeo entre categorías OPP-115 y RGPD utilizado como referencia académica procede de esta fuente.

> Poplavska, E., Norton, T. B., Wilson, S. & Sadeh, N. (2020). *From Prescription to Description: Mapping the GDPR to a Privacy Policy Corpus Annotation Scheme*. JURIX 2020. DOI: 10.3233/FAIA200874.

Consulte las condiciones y requisitos de citación de las fuentes originales antes de redistribuir o publicar resultados.
