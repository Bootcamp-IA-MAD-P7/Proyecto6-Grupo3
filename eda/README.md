# eda — exploratory data analysis notebooks
# 📊 Análisis Exploratorio de Datos (EDA)

Esta carpeta contiene los scripts ejecutables de análisis exploratorio encargados de validar las hipótesis de los datos, comprobar los requisitos de preprocesado y fundamentar las decisiones de diseño registradas en las **SPECs** del proyecto.

---

## 🛠️ Scripts y Responsabilidades

### 📄 `01_target_distribution.py` (Issue #48)
* **Objetivo:** Cuantificar cuántas veces aparece cada una de las 9 categorías en la tabla de entrenamiento generada a partir de OPP-115, y visualizar el desbalance entre la más frecuente y la menos frecuente.
* **Qué hace:**
  * Cuenta las apariciones de cada una de las 9 etiquetas objetivo.
  * Genera un gráfico de barras horizontales con la distribución.
  * Cuantifica el ratio de desbalance entre la categoría más frecuente y la menos frecuente.
* **Artefactos generados:** 
  * 📊 `reports/figures/target_distribution.png`
* **Conclusiones:** Las 9 categorías están fuertemente desbalanceadas (ratio 47.5:1 entre `first_party_collection_use` y `do_not_track`). Esto justifica la elección de la métrica **macro-F1** en las SPECs para evitar que el modelo ignore las clases minoritarias.

---

### 📄 `02_target_multilabel.py` (Issue #49)
* **Objetivo:** Demostrar con datos que este es un problema multi-etiqueta (no multiclase), mostrando cuántas categorías tiene cada fragmento a la vez y qué combinaciones aparecen juntas más seguido.
* **Qué hace:**
  * Calcula el número de etiquetas por fragmento y detecta cuántos fragmentos no tienen etiqueta (texto clasificado como "Other").
  * Genera un gráfico de distribución del número de etiquetas por fragmento.
  * Construye una matriz de co-ocurrencia y un mapa de calor (*heatmap*).
* **Artefactos generados:** 
  * 📊 `reports/figures/multilabel_distribution.png`
  * 📊 `reports/figures/cooccurrence_heatmap.png`
* **Conclusiones:** Se confirma que el problema es multi-etiqueta (media de 1.23 etiquetas por fragmento). Aunque la gran mayoría de fragmentos tiene entre 0 y 2 etiquetas, también hay casos excepcionales que acumulan hasta 8 categorías de forma simultánea. Esto demuestra que forzar una sola categoría por fragmento descartaría información real. La combinación más frecuente es `first_party_collection_use` + `third_party_sharing_collection`.

---

### 📄 `03_text_length_vocab.py` (Sub-issue #50)
* **Objetivo:** Analizar la distribución de la longitud de los textos de OPP-115 y la densidad del vocabulario.
* **Cumplimiento de Specs:** SPEC 3 §3 (Parámetros a congelar) y SPEC 2 §2.
* **Qué hace:**
  * Calcula las métricas de palabras y caracteres por fragmento.
  * Identifica el **percentil 95** de la distribución de longitud de palabras para definir la longitud máxima (`max_length`) recomendada en el preprocesado/vectorizado de los modelos base.
  * Muestra el tamaño total de palabras únicas y el Top 15 de palabras más frecuentes en el corpus.
* **Artefactos generados:** 
  * 📊 `reports/figures/50_longitud_texto.png`

---

### 📄 `04_text_split_rare_classes.py` (Sub-issue #51)
* **Objetivo:** Validar la estrategia de partición agrupada por política y evaluar el impacto sobre categorías de baja frecuencia.
* **Cumplimiento de Specs:** SPEC 2 §1.3 (Extensión dataset), §4.1 (Reparto por política) y SPEC 3 §3.
* **Qué hace:**
  * Analiza el desbalance de las 9 categorías multi-etiqueta objetivo en OPP-115.
  * Simula el reparto 80/20 agrupado por empresa (`policy_id` / `policy_name`) con `GroupShuffleSplit(seed=42)` y valida mediante assertion que no exista *data leakage* entre Train y Test.
  * Garantiza que clases minoritarias como `do_not_track` contengan ejemplos suficientes en el conjunto de prueba congelado.
  * Evalúa la escasez de `Do Not Track` en la extensión del dataset de 33 políticas actuales, demostrando que es una práctica obsoleta en la actualidad (~9 ejemplos en +10.000 párrafos).
* **Artefactos generados:** 
  * 📊 `reports/figures/51_particion_politicas.png`

---

## 🚀 Cómo ejecutar los scripts

Dado que los archivos están escritos en formato **Percent Script** (`# %%`), pueden ejecutarse celda a celda en VS Code usando el botón **"Ejecutar celda"** o de forma completa desde la raíz del proyecto usando `uv`:

```bash
# Ejecutar análisis de longitud y vocabulario
uv run python eda/03_text_length_vocab.py

# Ejecutar validación de partición por política y clases raras
uv run python eda/04_text_split_rare_classes.py