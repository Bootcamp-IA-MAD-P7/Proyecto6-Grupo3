"""Build the train/val/test split, grouped by policy, with a fixed seed."""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
TRAIN_FRAC, VAL_FRAC = 0.70, 0.15

IN_PATH = Path("data/processed/training_table.csv")
OUT_PATH = Path("data/processed/split_assignment.csv")

df = pd.read_csv(IN_PATH)

policies = np.sort(df["policy"].unique())
rng = np.random.default_rng(SEED)
shuffled = rng.permutation(policies)

n = len(shuffled)
n_train = round(n * TRAIN_FRAC)
n_val = round(n * VAL_FRAC)

assignment = {}
for p in shuffled[:n_train]:
    assignment[p] = "train"
for p in shuffled[n_train:n_train + n_val]:
    assignment[p] = "val"
for p in shuffled[n_train + n_val:]:
    assignment[p] = "test"

out = df[["policy", "segment"]].copy()
out["split"] = out["policy"].map(assignment)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(OUT_PATH, index=False)

print(f"seed = {SEED}")
print("\nfilas por split:")
print(out["split"].value_counts())
print("\npoliticas por split:")
print(out.groupby("split")["policy"].nunique())

# --- Verification ---

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

assert len(out) == len(df), "row count changed"
assert out["split"].notna().all(), "some rows were not assigned"
assert out.groupby("policy")["split"].nunique().eq(1).all(), "LEAKAGE: policy in two splits"

merged = df.merge(out, on=["policy", "segment"], validate="one_to_one")
coverage = merged.groupby("split")[LABEL_COLS].sum()

print("\ncobertura de etiquetas por split:")
print(coverage.T)

empty = [(s, c) for s in coverage.index for c in LABEL_COLS if coverage.loc[s, c] == 0]
if empty:
    print("\nFALLO — etiquetas vacias:", empty)
else:
    print("\nOK — las 9 etiquetas estan presentes en los 3 splits")