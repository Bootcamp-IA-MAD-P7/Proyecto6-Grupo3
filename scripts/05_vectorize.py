"""Fit the shared TF-IDF vectorizer on train only, transform all three splits."""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

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

ART = Path("artifacts")
ART.mkdir(exist_ok=True)

df = pd.read_csv("data/processed/training_table.csv")
split = pd.read_csv("data/processed/split_assignment.csv")
data = df.merge(split, on=["policy", "segment"], validate="one_to_one")

train = data[data["split"] == "train"]

vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.9,
    sublinear_tf=True,
)

vectorizer.fit(train["text"])
joblib.dump(vectorizer, ART / "tfidf_vectorizer.joblib")

for name in ["train", "val", "test"]:
    part = data[data["split"] == name]
    X = vectorizer.transform(part["text"])
    y = part[LABEL_COLS].to_numpy(dtype=np.int8)
    sparse.save_npz(ART / f"X_{name}.npz", X)
    np.save(ART / f"y_{name}.npy", y)
    print(f"{name}: X={X.shape}  y={y.shape}  density={X.nnz/(X.shape[0]*X.shape[1]):.5f}")

print(f"vocabulary size: {len(vectorizer.vocabulary_)}")