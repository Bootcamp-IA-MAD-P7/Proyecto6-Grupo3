# %% [markdown]
# # 📊 Sub-issue #50: Longitudes de Texto y Vocabulario
# **Frente de trabajo:** Análisis del texto en OPP-115 para definir max_length y vocabulario.
# **Cumplimiento de Specs:** SPEC 3 §3 (Preprocesado) y SPEC 2 §2.

# %% [importaciones]
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Estilo gráfico homogéneo
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 150

# %% [carga_datos]
# Cargar la tabla procesada CSV generada por scripts/02_build_target.py
DATA_PATH = 'data/processed/training_table.csv'

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    # Ruta de respaldo si el script se ejecuta dentro de la subcarpeta eda/
    df = pd.read_csv('../data/processed/training_table.csv')

print(f"✅ Cargados {len(df)} fragmentos de OPP-115 desde {DATA_PATH}.")

# %% [longitud_texto]
# Medir conteo de palabras y caracteres en la columna de texto
df['word_count'] = df['text'].apply(lambda x: len(str(x).split()))
df['char_count'] = df['text'].apply(lambda x: len(str(x)))

# Estadísticos descriptivos clave
stats_length = df['word_count'].describe(percentiles=[0.5, 0.75, 0.90, 0.95, 0.99])
print("\n--- 📈 ESTADÍSTICAS DE LONGITUD DE PALABRAS ---")
print(stats_length)

# Visualización: Histograma con Percentil 95
plt.figure(figsize=(10, 4))
sns.histplot(df['word_count'], kde=True, bins=40, color='teal')
p95 = df['word_count'].quantile(0.95)
plt.axvline(p95, color='red', linestyle='--', label=f'Percentil 95 ({int(p95)} palabras)')

plt.title('Distribución de Longitud de Palabras por Fragmento (OPP-115)', fontsize=12, fontweight='bold')
plt.xlabel('Cantidad de Palabras')
plt.ylabel('Frecuencia de Fragmentos')
plt.legend()
plt.tight_layout()



# %% [analisis_vocabulario]
# Análisis del vocabulario básico
all_words = " ".join(df['text'].dropna()).lower().split()
vocab_size = len(set(all_words))
word_freq = Counter(all_words)

print(f"\n🗣️ Vocabulario total único: {vocab_size:,} palabras únicas.")
print("\nTop 15 palabras más frecuentes:")
print(pd.DataFrame(word_freq.most_common(15), columns=['Palabra', 'Frecuencia']))

# %% [conclusiones_spec]
print("\n💡 CONCLUSIONES PARA LA SPEC 3 §3:")
print(f"1. El 95% de los fragmentos tiene {int(p95)} palabras o menos.")
print(f"2. Se recomienda fijar el max_length / vectorizado tomando como referencia ~{int(p95)} palabras para evitar truncado innecesario.")