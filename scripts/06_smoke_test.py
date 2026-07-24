"""Throwaway baseline: prove the artifacts load and the pipeline has an exit."""
import numpy as np
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score, classification_report

LABEL_COLS = [
    "first_party_collection_use", "third_party_sharing_collection",
    "user_choice_control", "user_access_edit_deletion", "data_retention",
    "data_security", "policy_change", "do_not_track",
    "international_specific_audiences",
]

Xtr = sparse.load_npz("artifacts/X_train.npz")
ytr = np.load("artifacts/y_train.npy")
Xva = sparse.load_npz("artifacts/X_val.npz")
yva = np.load("artifacts/y_val.npy")

clf = OneVsRestClassifier(LogisticRegression(max_iter=1000, class_weight="balanced"))
clf.fit(Xtr, ytr)
pred = clf.predict(Xva)

print("macro-F1:", round(f1_score(yva, pred, average="macro", zero_division=0), 4))
print("micro-F1:", round(f1_score(yva, pred, average="micro", zero_division=0), 4))
print()
print(classification_report(yva, pred, target_names=LABEL_COLS, zero_division=0))