
"""Throwaway baseline: prove the artifacts load and the pipeline has an exit.
 
Referencia de la tabla comparativa (2_spec §3.1). NO es uno de los cuatro modelos base.
 
Añadido el 28 de julio: el gap train-val, que 2_spec §3.1 marcaba como PENDIENTE
("este baseline no reporta el gap train/validacion que exige la regla de sobreajuste").
Sin esa cifra no se puede interpretar si los gaps de los cuatro modelos base son
anomalias suyas o una propiedad de los datos.
 
Nota de comparabilidad: aqui el macro-F1 se calcula con f1_score directamente y no
importando models/metrics.py, porque este script vive en scripts/ y el import exigiria
parchear sys.path. Es la MISMA operacion: compute_metrics binariza las probabilidades en
0.5 y llama a f1_score(average="macro", zero_division=0), y clf.predict sobre
OneVsRest+LogisticRegression ya aplica ese mismo corte en 0.5. Las cifras son
directamente comparables con las de los modelos base.
"""
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
pred_tr = clf.predict(Xtr)   # train COMPLETO: este baseline no usa dev interno
 
macro_va = f1_score(yva, pred, average="macro", zero_division=0)
macro_tr = f1_score(ytr, pred_tr, average="macro", zero_division=0)
gap = macro_tr - macro_va
 
print("macro-F1:", round(macro_va, 4))
print("micro-F1:", round(f1_score(yva, pred, average="micro", zero_division=0), 4))
print()
print("macro-F1 train:", round(macro_tr, 4))
print("gap train-val :", round(gap, 4),
      "  <-- SUPERA EL 5% que exige 2_spec §3" if gap > 0.05 else "  (ok, <0.05)")
print()
print(classification_report(yva, pred, target_names=LABEL_COLS, zero_division=0))