# %% [markdown]
# ## Modelo base — DeBERTa-v3-small (issue #25)
#
# Transformer preentrenado para clasificacion multi-etiqueta. NO usa TF-IDF:
# lee texto crudo de training_table.csv y tokeniza con su propio tokenizer.
# Respeta exactamente split_assignment.csv (mismas politicas que los clasicos).

# %% 1. Imports
from pathlib import Path
import pandas as pd

# %% 2. Rutas (funcionan sin importar desde que carpeta se ejecute)
def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while not (current / "pyproject.toml").exists():
        if current.parent == current:
            raise FileNotFoundError("No se encontro pyproject.toml en ningun ancestro")
        current = current.parent
    return current

REPO_ROOT = find_repo_root(Path.cwd())

TRAINING_TABLE = REPO_ROOT / "data/processed/training_table.csv"
SPLIT_ASSIGNMENT = REPO_ROOT / "data/processed/split_assignment.csv"

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

# %% 3. Load data (patron exacto de 4_data_contract.md)
df = pd.read_csv(TRAINING_TABLE)

split = pd.read_csv(SPLIT_ASSIGNMENT)

data = df.merge(split, on=["policy", "segment"], validate="one_to_one")

train = data[data["split"] == "train"]
val = data[data["split"] == "val"]
test = data[data["split"] == "test"]

print(f"train: {len(train)} filas, {train['policy'].nunique()} politicas")
print(f"val:   {len(val)} filas, {val['policy'].nunique()} politicas")
print(f"test:  {len(test)} filas, {test['policy'].nunique()} politicas")

# %% 4. Load tokenizer
from transformers import AutoTokenizer

MODEL_NAME = "microsoft/deberta-v3-small"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print(tokenizer)
