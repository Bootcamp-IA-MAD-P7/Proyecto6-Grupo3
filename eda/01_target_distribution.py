# %%
# ## EDA - Distribución y desbalance de las 9 categorías
#
# Objetivo: cuantificar cuántas veces aparece cada una de las 9 categorías
# en la tabla de entrenamiento generada a partir de OPP-115, y visualizar
# el desbalance entre la más frecuente y la menos frecuente.

# %% 1. Imports
import os
import pandas as pd
import matplotlib.pyplot as plt

#%% 2. Load data
df = pd.read_csv("data/processed/training_table.csv")
df.shape

# %%
df.columns.tolist()
# %% 3. Contar apariciones de cada categoría
LABEL_COLUMNS = [
    'first_party_collection_use',
    'third_party_sharing_collection',
    'user_choice_control',
    'user_access_edit_deletion',
    'data_retention',
    'data_security',
    'policy_change',
    'do_not_track',
    'international_specific_audiences'
]

counts = df[LABEL_COLUMNS].sum().sort_values(ascending=False)
counts
# %% 4. Gráfico de barras - distribución de las 9 categorías
plt.figure(figsize=(10, 6))
counts.sort_values().plot(kind='barh')
plt.xlabel("Numero de fragmentos con esta etiqueta")
plt.title("Distribucion de las 9 categorias (OPP-115)")
plt.tight_layout()

os.makedirs('reports/figures', exist_ok=True)
plt.savefig('reports/figures/target_distribution.png', bbox_inches='tight')

plt.show()

# %% 5. Cuantificar el desbalance 
ratio = counts.max() / counts.min()
print(f"Categoria mas frecuente : {counts.idxmax()} ({counts.max()})")
print(f"Categoria menos frecuente: {counts.idxmin()} ({counts.min()})")
print(f"Ratio de desbalance      : {ratio:.1f}:1")

# %% [markdown]
# ### Conclusiones
#
# Las 9 categorías están fuertemente desbalanceadas: `first_party_collection_use`
# aparece en 1521 fragmentos, mientras que `do_not_track` aparece en solo 32
# (ratio 47.5:1). Cuatro categorías (`do_not_track`, `data_retention`,
# `policy_change`, `user_access_edit_deletion`) tienen menos de 250 apariciones,
# muy por debajo de las dos más frecuentes.
#
# Esto confirma por qué el equipo eligió macro-F1 como métrica principal
# (2_spec.md): con una métrica que pese por instancia (micro-F1 o accuracy),
# el modelo podría ignorar casi por completo categorías raras como
# `do_not_track` y aún así sacar una nota alta, porque pesan poco en el total.
# Macro-F1 obliga a que el modelo también funcione bien en las categorías con
# pocos ejemplos, no solo en las frecuentes.