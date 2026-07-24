# %% [markdown]
# ## EDA — Multi-etiqueta: combinaciones de categorías (issue #49)
#
# Objetivo: demostrar con datos que este es un problema multi-etiqueta (no
# multiclase), mostrando cuántas categorías tiene cada fragmento a la vez, y
# qué combinaciones de categorías aparecen juntas más seguido.

#%% 1. Imports
import os
import pandas as pd
import matplotlib.pyplot as plt

#%% 2. Load data
df = pd.read_csv("data/processed/training_table.csv")
df.shape


# %% 3. Número de etiquetas por fragmentos
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

df["n_labels"] = df[LABEL_COLUMNS].sum(axis=1)
df["n_labels"].describe()

# %% 4. Fragmentos sin niguna etiqueta
sin_etiqueta = (df["n_labels"] == 0).sum()
pct_sin_etiqueta = sin_etiqueta / len(df) * 100
print(f"Fragmentos sin ninguna etiqueta: {sin_etiqueta} ({pct_sin_etiqueta:.1f}%)")

# %% 5. Gráfico - distribución del número de etiquetas por fragmento
plt.figure(figsize=(8, 5))
df["n_labels"].value_counts().sort_index().plot(kind="bar")
plt.xlabel("Numero de etiquetas por fragmento")
plt.ylabel("Numero de fragmentos")
plt.title("Cuantas categorias tiene cada fragmento a la vez")
plt.xticks(rotation=0)
plt.tight_layout()

os.makedirs('reports/figures', exist_ok=True)
plt.savefig('reports/figures/multilabel_distribution.png', bbox_inches='tight')

plt.show()


# %% 6. Matriz de co-ocurrencia entre categorías
co_matrix = df[LABEL_COLUMNS].T.dot(df[LABEL_COLUMNS])
co_matrix

# %% 7. Heatmap de co-ocurrencia
import seaborn as sns

plt.figure(figsize=(9, 7))
sns.heatmap(co_matrix, annot=True, fmt="d", cmap="Blues")
plt.title("Co-ocurrencia entre categorias (cuantos fragmentos comparten ambas)")
plt.tight_layout()

os.makedirs('reports/figures', exist_ok=True)
plt.savefig('reports/figures/cooccurrence_heatmap.png', bbox_inches='tight')

plt.show()

# %% [markdown]
# ### Conclusiones
#
# La media es de 1.23 etiquetas por fragmento, con un 13.7% de fragmentos
# (520 de 3792) sin ninguna categoría activa — corresponden a texto
# clasificado como "Other" (contacto, introducciones), que se excluye del
# target por decisión de la spec.
#
# La distribución muestra que la mayoría de fragmentos tiene 0, 1 o 2
# etiquetas, aunque también existen casos excepcionales que acumulan hasta
# 8 categorías de forma simultánea. Esto confirma que el problema es
# multi-etiqueta y no multiclase: forzar una sola categoría por fragmento
# descartaría información real en el 25% de fragmentos que tienen 2 o más
# categorías simultáneas.
#
# La combinación más frecuente entre categorías distintas es
# `first_party_collection_use` + `third_party_sharing_collection`
# (503 fragmentos comparten ambas) — coincide con el patrón más común en
# políticas de privacidad: un mismo párrafo que declara que recogen un dato
# y además lo comparten con terceros.

