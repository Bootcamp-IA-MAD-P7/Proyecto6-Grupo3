# ## Modelo base — DeBERTa-v3-small (issue #25)
#
# Transformer preentrenado para clasificacion multi-etiqueta. NO usa TF-IDF:
# lee texto crudo de training_table.csv y tokeniza con su propio tokenizer.
# Respeta exactamente split_assignment.csv (mismas politicas que los clasicos).

# 1. Imports
from pathlib import Path
import pandas as pd
import torch

# 2. Rutas (funcionan sin importar desde que carpeta se ejecute)
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

# 3. Load data (patron exacto de 4_data_contract.md)
df = pd.read_csv(TRAINING_TABLE)

split = pd.read_csv(SPLIT_ASSIGNMENT)

data = df.merge(split, on=["policy", "segment"], validate="one_to_one")

train = data[data["split"] == "train"]
val = data[data["split"] == "val"]
test = data[data["split"] == "test"]

print(f"train: {len(train)} filas, {train['policy'].nunique()} politicas")
print(f"val:   {len(val)} filas, {val['policy'].nunique()} politicas")
print(f"test:  {len(test)} filas, {test['policy'].nunique()} politicas")

# 4. Load tokenizer
from transformers import AutoTokenizer

MODEL_NAME = "microsoft/deberta-v3-small"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print(tokenizer)

# 5. Probar el tokenizer con un fragmento real
sample_text = train["text"].iloc[0]
print(sample_text)

encoded = tokenizer(sample_text)
print("\nIDs de los tokens:")
print(encoded["input_ids"])

print("\nTokens (version legible):")
print(tokenizer.convert_ids_to_tokens(encoded["input_ids"]))

# 6. Definir el modelo con cabeza multi-etiqueta
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABEL_COLS),
    problem_type="multi_label_classification",
    dtype=torch.float32,
)
print(model.config.problem_type)
print(model.config.num_labels)

# 7. Preparar etiquetas (deben ser float para BCEWithLogitsLoss)
y_train = train[LABEL_COLS].values.astype("float32")
y_val = val[LABEL_COLS].values.astype("float32")

print ("y_train shape:", y_train.shape, y_train.dtype)

# 8. Tokenizar train y val 
train_encodings = tokenizer(
    train["text"].tolist(),
    truncation=True,
    padding=True,
    max_length=256,
    return_tensors="pt"
)
val_encodings = tokenizer(
    val["text"].tolist(),
    truncation=True,
    padding=True,
    max_length=256,
    return_tensors="pt"
)

print(train_encodings["input_ids"].shape)
print(val_encodings["input_ids"].shape)   

# 9. Empaquetar los datos en un Dataset de PyTorch
class PolicyDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item  

train_dataset = PolicyDataset(train_encodings, y_train)
val_dataset = PolicyDataset(val_encodings, y_val)

print(len(train_dataset), len(val_dataset))

# 10. Configurar la semilla para reproducibilidad
SEED = 42
torch.manual_seed(SEED)

# 11. Configurar el entrenamiento 
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="models/deberta_output",
    num_train_epochs=3,
    learning_rate=3e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    seed=SEED,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# 12. Entrenar
trainer.train()

# 13. Calcular metricas sobre val
import sys
sys.path.insert(0, "models")
from metrics import compute_metrics

predictions_val = trainer.predict(val_dataset)
logits_val = predictions_val.predictions
proba_val = torch.sigmoid(torch.tensor(logits_val)).numpy()

m_val = compute_metrics(y_val, proba_val, LABEL_COLS)
print("macro-F1 val:", m_val["macro_f1"])
print("F1 por categoria:")
for cat, f1 in m_val["f1_per_category"].items():
    print(f"  {cat}: {f1:.4f}")
    
# 14. Análisis de Overfitting (Train vs Val)
predictions_train = trainer.predict(train_dataset)
logits_train = predictions_train.predictions
proba_train = torch.sigmoid(torch.tensor(logits_train)).numpy()

m_train = compute_metrics(y_train, proba_train, LABEL_COLS)

calculated_gap = m_train["macro_f1"] - m_val["macro_f1"]

print("\n--- ANÁLISIS DE OVERFITTING ---")
print(f"macro-F1 train: {m_train['macro_f1']:.4f}")
print(f"macro-F1 val:   {m_val['macro_f1']:.4f}")
print(f"Overfit Gap:    {calculated_gap:.4f} (Debe ser < 0.05)")

# ==============================================================================
# RESULTADOS FINALES DE EJECUCIÓN (REGISTRO HISTÓRICO):
# ------------------------------------------------------------------------------
# --- RESULTADOS VALIDACIÓN ---
# macro-F1 val: 0.5785
# F1 por categoria:
#   first_party_collection_use: 0.8552
#   third_party_sharing_collection: 0.8312
#   user_choice_control: 0.6554
#   user_access_edit_deletion: 0.6471
#   data_retention: 0.0000
#   data_security: 0.6522
#   policy_change: 0.7541
#   do_not_track: 0.0000
#   international_specific_audiences: 0.8113
#
# --- ANÁLISIS DE OVERFITTING ---
# macro-F1 train: 0.6541
# macro-F1 val:   0.5785
# Overfit Gap:    0.0756 (Debe ser < 0.05)
# ==============================================================================