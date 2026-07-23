# Agent 02 — Segmentation and Dataset Builder

## Objetivo

Transformar los documentos limpios generados por el Agente 1 en un dataset estructurado a nivel de párrafo, manteniendo la trazabilidad completa y enriqueciendo cada registro con metadatos estructurales.

## Contrato de entrada

```
clean_documents/
metadata/
processing_log.json
```

## Contrato de salida

```
paragraphs_raw.csv
paragraph_statistics.json
paragraph_index.json
document_structure.json
paragraph_entities.json
paragraph_embeddings.parquet
```

## Flujo

```
Documentos limpios
      │
      ▼
Lectura
      ▼
Detección de estructura (H1-H4)
      ▼
Segmentación en párrafos
      ▼
Enriquecimiento de metadatos
      ▼
NER
      ▼
Detección de idioma por párrafo
      ▼
Embeddings
      ▼
Validación
      ▼
paragraphs_raw.csv
```

## Fase 1. Lectura

- Mantener el texto original.
- No traducir.
- No resumir.
- No modificar significado.

## Fase 2. Estructura documental

Detectar:

- H1
- H2
- H3
- H4

Guardar:

- section
- subsection
- heading_level

## Fase 3. Segmentación

Cada fila representa un único párrafo.

No dividir frases.

No unir párrafos.

## Fase 4. Identificadores

Formato recomendado:

```
DOC_00001_P0001
```

## Fase 5. Metadatos estructurales

Calcular:

- characters
- words
- sentences
- lines
- paragraph_number
- total_paragraphs
- paragraph_position
- relative_position

## Fase 6. Características documentales

Booleanos:

- contains_url
- contains_email
- contains_phone
- contains_dates
- contains_percentages
- contains_articles
- contains_lists
- contains_tables
- contains_legal_reference

## Fase 7. NER (Mejora)

Detectar entidades:

- ORGANIZATION
- LAW
- REGULATION
- ARTICLE
- PERSON
- COUNTRY
- DATE
- URL
- EMAIL

Guardar un archivo:

```
paragraph_entities.json
```

Ejemplo:

```json
{
  "paragraph_id":"DOC_00001_P0004",
  "entities":[
    {"type":"LAW","text":"RGPD"},
    {"type":"ARTICLE","text":"17"}
  ]
}
```

## Fase 8. Árbol documental (Mejora)

Generar:

```
document_structure.json
```

Ejemplo:

```json
{
  "document_id":"DOC_00001",
  "sections":[
    {
      "title":"Information We Collect",
      "level":1,
      "children":[]
    }
  ]
}
```

## Fase 9. Idioma por párrafo (Mejora)

Campos nuevos:

- paragraph_language
- language_matches_document

## Fase 10. Embeddings (Mejora)

Generar:

```
paragraph_embeddings.parquet
```

Campos:

- paragraph_id
- embedding_model
- embedding_dimension
- embedding_vector

Uso previsto:

- búsqueda semántica
- clustering
- detección de duplicados
- futuras funciones RAG

## Esquema de paragraphs_raw.csv

- dataset_version
- document_id
- paragraph_id
- company
- sector
- language
- paragraph_language
- section
- subsection
- heading_level
- paragraph_number
- paragraph_position
- relative_position
- total_paragraphs
- text
- characters
- words
- sentences
- contains_url
- contains_email
- contains_phone
- contains_dates
- contains_articles
- contains_lists
- contains_tables
- contains_legal_reference
- processing_status

## Control de calidad

Detectar:

- párrafos vacíos
- duplicados
- codificación incorrecta
- idioma inesperado
- longitud extrema

Registrar incidencias, nunca modificar automáticamente el contenido.

## Criterios de aceptación

- 100 % de documentos segmentados.
- IDs únicos.
- Sin pérdida de texto.
- Metadatos completos.
- Embeddings generados.
- Árbol documental generado.
- NER generado.
- Dataset listo para el Agente 3.
