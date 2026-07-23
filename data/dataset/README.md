# dataset — original OPP-115 dataset files (.csv annotations, policy texts)

## Cómo obtener los datos

OPP-115 — el corpus de entrenamiento, con sus anotaciones. Descarga: https://usableprivacy.org/data

Cita obligatoria si se usa en una publicación:

Wilson, S., Schaub, F., Dara, A., Liu, F., Cherivirala, S., Giovanni Leon, P., Schaarup Andersen, M., Zimmeck, S., Sathyendra, K. M., Russell, N. C., Norton, T. B., Hovy, E., Reidenberg, J. & Sadeh, N. (2016). The Creation and Analysis of a Website Privacy Policy Corpus. ACL 2016.

Mapeo OPP-115 → RGPD — tabla de consulta categoría → artículo. Misma página: JURIX_2020_OPP-115_GDPR_v1.0.zip (83 KB).

Este archivo sí se versiona, por dos razones: pesa 83 KB y es fuente de referencia, no producto derivado.

### Cita obligatoria:

Poplavska, E., Norton, T. B., Wilson, S. & Sadeh, N. (2020). From Prescription to Description: Mapping the GDPR to a Privacy Policy Corpus Annotation Scheme. JURIX 2020, pp. 243-246. DOI: 10.3233/FAIA200874.

Cómo comprobar que la descarga está completa

El dataset no sirve solo con los textos: hace falta el archivo de anotaciones, que es el que dice a qué categorías pertenece cada fragmento. Sin él no hay target y no se puede entrenar nada.

## bash
uv run python scripts/01_inspect_opp115.py

Ese script imprime qué hay dentro y confirma que las anotaciones están presentes.