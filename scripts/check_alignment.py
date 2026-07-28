"""
check_alignment.py — paso 0, antes de entrenar nada.

QUE HACE
Comprueba que los CSV del proyecto y las matrices de artifacts/ hablan de las mismas
filas en el mismo orden. No entrena, no guarda, no modifica nada. Solo imprime.

POR QUE HACE FALTA
Para el early stopping necesito un dev interno sacado de train que respete politicas
enteras. Las matrices X_train.npz son solo numeros: no dicen a que politica pertenece
cada fila. Eso solo lo sabe el CSV. Asi que hay que cruzarlos por posicion, y eso es
una SUPOSICION. Si es falsa, el dev interno mezclaria politicas de train y no se veria
en las metricas: el script correria, los numeros saldrian, y estarian mal. Es el mismo
patron del fallo de eda/04 del 24 de julio.

COMO LO COMPRUEBA DE FORMA QUE PUEDA FALLAR
Si el orden de filas coincide, las 9 columnas de etiqueta del CSV filtrado por
split == "train" tienen que ser IDENTICAS a y_train.npy. Si difieren en una sola fila,
lanza excepcion y para.

COMO SE EJECUTA
    uv run python models/lightgbm/check_alignment.py
(desde la raiz del repo)
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

TRAINING_TABLE = Path("data/processed/training_table.csv")
SPLIT_ASSIGNMENT = Path("data/processed/split_assignment.csv")
ARTIFACTS = Path("artifacts")

# Orden oficial de 4_data_contract.md. NO reordenar.
LABEL_COLS = [
    "first_party_collection_use",
    "third_party_sharing_collection",
    "user_choice_control",
    "user_access_edit_deletion",
    "data_retention",
    "data_security",
    "policy_change",
    "do_not_track",
    "international_specific_audiences",
]


def require(path: Path) -> Path:
    """Un archivo que falta es un crash, no un fallback (2_spec 6.2)."""
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta antes scripts/04_build_split.py y "
            f"scripts/05_vectorize.py, y hazlo desde la raiz del repo."
        )
    return path


# --- 1) CSV: tabla de entrenamiento + particion oficial ---
df = pd.read_csv(require(TRAINING_TABLE))
split = pd.read_csv(require(SPLIT_ASSIGNMENT))

missing = [c for c in ["policy", "segment", *LABEL_COLS] if c not in df.columns]
if missing:
    raise KeyError(f"Faltan columnas en training_table.csv: {missing}")

# validate="one_to_one": pandas grita si hay claves duplicadas o que no cruzan,
# en lugar de multiplicar filas en silencio.
data = df.merge(split, on=["policy", "segment"], validate="one_to_one")
train = data[data["split"] == "train"]

# --- 2) artefactos congelados (cargar, nunca reentrenar) ---
X_train = sparse.load_npz(require(ARTIFACTS / "X_train.npz"))
y_train = np.load(require(ARTIFACTS / "y_train.npy"))

print("--- formas ---")
print(f"CSV train   : {len(train)} filas, {train['policy'].nunique()} politicas")
print(f"X_train.npz : {X_train.shape}")
print(f"y_train.npy : {y_train.shape}")

# --- 3) comprobaciones que PUEDEN fallar ---
if len(train) != X_train.shape[0]:
    raise ValueError(
        f"El CSV filtrado por train tiene {len(train)} filas pero X_train tiene "
        f"{X_train.shape[0]}. No se puede mapear politica -> fila."
    )

if y_train.shape[1] != len(LABEL_COLS):
    raise ValueError(
        f"y_train tiene {y_train.shape[1]} columnas, esperaba {len(LABEL_COLS)}."
    )

y_from_csv = train[LABEL_COLS].to_numpy()
if not np.array_equal(y_from_csv, y_train):
    n_diff = int((y_from_csv != y_train).any(axis=1).sum())
    raise ValueError(
        f"Las etiquetas del CSV NO coinciden con y_train.npy en {n_diff} filas. "
        "El orden de filas del CSV no es el de los artefactos, asi que no sirve para "
        "mapear politicas a filas. Preguntar en el issue #8 con que orden se generaron."
    )

print("\nOK: el orden de filas del CSV coincide con los artefactos.")
print("    Puedo usar train['policy'] para agrupar filas de X_train por politica.")

# --- 4) datos que necesito para el dev interno y para el informe ---
print(f"\nPoliticas en train: {train['policy'].nunique()}")
print("Positivos por categoria en train (ojo con las raras):")
for name, count in zip(LABEL_COLS, y_train.sum(axis=0)):
    print(f"  {name:36s} {int(count):5d}")
