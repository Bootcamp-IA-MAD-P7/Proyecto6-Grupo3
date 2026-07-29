"""
11_multiclass_baseline.py — paso 2 del enfoque multiclase. Baseline de referencia.

QUE HACE
Entrena una REGRESION LOGISTICA MULTINOMIAL sobre las 10 clases del target multiclase, y
reporta accuracy, macro-F1, F1 por clase y la matriz de confusion 10x10.

POR QUE ESTE MODELO
- Es la version multiclase del baseline que ya existia (scripts/06_smoke_test.py usaba la
  misma LogisticRegression envuelta en OneVsRest para las 9 binarias). Al pasarle una y de
  una sola columna, sklearn usa softmax y se convierte en multiclase de verdad. La
  continuidad importa: es el mismo algoritmo, otro planteamiento del problema.
- Entrena en segundos, asi que se puede iterar sin esperas.
- Es INTERPRETABLE: al final imprime las palabras con mas peso para cada clase, que es
  material directo para la presentacion tecnica.

QUE REUTILIZA SIN TOCAR
- artifacts/X_{train,val}.npz : las matrices TF-IDF congeladas (issue #8). Las features son
  las mismas que en el enfoque multi-etiqueta; lo unico que cambia es la y.
- La particion oficial (semilla 42, por politica, issue #18). Ninguna fila cambia de grupo.
- data/processed/multiclass_target.csv, generado por scripts/10_build_multiclass_target.py.

POR QUE NO SE USA models/metrics.py
metrics.py esta escrito para MULTI-ETIQUETA: recibe una matriz de probabilidades de 9
columnas y la binariza con umbral 0.5. En multiclase no hay umbral (gana la clase con
mayor probabilidad, argmax) y la y es una sola columna de texto. Son metricas distintas,
asi que aqui se calculan con sklearn directamente. NO es saltarse la norma del equipo: es
que la norma se escribio para otro planteamiento del problema. Si el enfoque multiclase se
adopta, hay que escribir el metrics.py equivalente y que todos los modelos lo importen.

METRICAS Y COMO LEERLAS
- accuracy: % de fragmentos clasificados bien. En multiclase SI tiene sentido (en
  multi-etiqueta no servia). SUELO: 31.3%, que es el % de la clase mayoritaria; un modelo
  que prediga siempre third_party lo alcanza sin aprender nada.
- macro-F1: promedio simple del F1 de las 10 clases. Cada clase pesa igual, tenga 1186
  ejemplos o 30. Es la que dice si el modelo atiende tambien a las pequeñas.
- accuracy y macro-F1 dicen cosas DISTINTAS: con desbalance 39.5:1, un modelo puede tener
  accuracy alta y macro-F1 baja si acierta las grandes e ignora las pequeñas.
- gap: accuracy y macro-F1 de train menos las de val. Diagnostico de sobreajuste, NO
  objetivo a optimizar (bajarlo sacrificando rendimiento produce un modelo peor).

COMO SE EJECUTA (desde la raiz del repo)
    uv run python models/11_multiclass_baseline.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

TARGET = Path("data/processed/multiclass_target.csv")
ARTIFACTS = Path("artifacts")

# Mismo orden que el script 10. Fija el orden de filas y columnas de la matriz de
# confusion, para que se pueda leer siempre igual.
CLASSES = [
    "third_party_sharing_collection",
    "data_retention",
    "do_not_track",
    "user_access_edit_deletion",
    "user_choice_control",
    "data_security",
    "international_specific_audiences",
    "policy_change",
    "first_party_collection_use",
    "Other",
]
# Etiquetas cortas para que la matriz 10x10 quepa en pantalla.
SHORT = {
    "third_party_sharing_collection": "3rd_party",
    "data_retention": "retention",
    "do_not_track": "dnt",
    "user_access_edit_deletion": "access",
    "user_choice_control": "choice",
    "data_security": "security",
    "international_specific_audiences": "intl",
    "policy_change": "change",
    "first_party_collection_use": "1st_party",
    "Other": "Other",
}


def require(path: Path) -> Path:
    """Un archivo que falta es un crash, no un fallback (2_spec §6.2)."""
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta antes "
            f"scripts/10_build_multiclass_target.py y scripts/05_vectorize.py."
        )
    return path


# ------------------------------------------------- 1) target y matrices
tgt = pd.read_csv(require(TARGET))
X_train = sparse.load_npz(require(ARTIFACTS / "X_train.npz"))
X_val = sparse.load_npz(require(ARTIFACTS / "X_val.npz"))

y_train = tgt.loc[tgt["split"] == "train", "label"].to_numpy()
y_val = tgt.loc[tgt["split"] == "val", "label"].to_numpy()

# La alineacion es POSICIONAL: el script 10 conserva el orden de training_table.csv, que es
# el orden con el que 05_vectorize.py construyo las matrices. Si no cuadra, raise.
if len(y_train) != X_train.shape[0]:
    raise ValueError(
        f"train: {len(y_train)} etiquetas y {X_train.shape[0]} filas en la matriz. "
        "El target y los artefactos no estan alineados."
    )
if len(y_val) != X_val.shape[0]:
    raise ValueError(
        f"val: {len(y_val)} etiquetas y {X_val.shape[0]} filas en la matriz."
    )

print("=== datos ===")
print(f"train : {X_train.shape[0]} filas x {X_train.shape[1]} features")
print(f"val   : {X_val.shape[0]} filas")
print(f"clases: {len(set(y_train))}")

# Suelo de accuracy: predecir siempre la clase mayoritaria de train.
mayoritaria = pd.Series(y_train).value_counts().idxmax()
suelo = float((y_val == mayoritaria).mean())
print(f"\nSUELO de accuracy en val: {suelo:.4f}")
print(f"  (predecir siempre '{mayoritaria}' sin aprender nada)")

# ------------------------------------------------- 2) entrenar
# class_weight="balanced" por el desbalance 39.5:1: sin el, las clases pequeñas
# (do_not_track con 19 ejemplos en train) se ignoran. Confirmado empiricamente en el
# enfoque multi-etiqueta, donde quitarlo hundio data_retention de 0.48 a 0.23.
clf = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42,
)
print("\nentrenando regresion logistica multinomial...")
clf.fit(X_train, y_train)

pred_val = clf.predict(X_val)
pred_train = clf.predict(X_train)

# ------------------------------------------------- 3) metricas
acc_val = accuracy_score(y_val, pred_val)
acc_train = accuracy_score(y_train, pred_train)
macro_val = f1_score(y_val, pred_val, average="macro", zero_division=0)
macro_train = f1_score(y_train, pred_train, average="macro", zero_division=0)

print("\n=== resultados en val ===")
print(f"accuracy      : {acc_val:.4f}   (suelo {suelo:.4f})")
print(f"macro-F1      : {macro_val:.4f}")
print(f"micro-F1      : {f1_score(y_val, pred_val, average='micro', zero_division=0):.4f}")
print("  nota: en multiclase de etiqueta unica, micro-F1 == accuracy por construccion.")

print("\n=== sobreajuste (diagnostico, no objetivo) ===")
print(f"accuracy train {acc_train:.4f} - val {acc_val:.4f} = gap {acc_train-acc_val:.4f}")
print(f"macro-F1 train {macro_train:.4f} - val {macro_val:.4f} = gap {macro_train-macro_val:.4f}")

print("\n=== F1 por clase en val ===")
print(classification_report(y_val, pred_val, labels=CLASSES, zero_division=0))

# ------------------------------------------------- 4) matriz de confusion 10x10
# Lo que el enfoque multi-etiqueta NO permitia ver: que clase se confunde con cual.
cm = confusion_matrix(y_val, pred_val, labels=CLASSES)
cols = [SHORT[c] for c in CLASSES]

print("=== matriz de confusion en val ===")
print("filas = clase REAL · columnas = lo que PREDIJO el modelo")
print("la diagonal son los aciertos; fuera de la diagonal, las confusiones\n")
print(f"{'real \\ pred':>12s} " + " ".join(f"{c:>9s}" for c in cols))
for i, c in enumerate(CLASSES):
    print(f"{SHORT[c]:>12s} " + " ".join(f"{v:9d}" for v in cm[i]))

print("\n=== confusiones mas frecuentes (fuera de la diagonal) ===")
pares = []
for i, real in enumerate(CLASSES):
    for j, pred in enumerate(CLASSES):
        if i != j and cm[i][j] > 0:
            total_real = cm[i].sum()
            pares.append((cm[i][j], real, pred, 100 * cm[i][j] / total_real if total_real else 0))
pares.sort(reverse=True)
for n, real, pred, pct in pares[:10]:
    print(f"  {n:3d} fragmentos de {real} predichos como {pred}  ({pct:.0f}% de su clase)")

# --------------------------- 5) interpretabilidad: palabras con mas peso por clase
# Material para la presentacion tecnica: se puede MOSTRAR en que se fija el modelo.
try:
    import joblib

    vec = joblib.load(require(ARTIFACTS / "tfidf_vectorizer.joblib"))
    vocab = np.array(vec.get_feature_names_out())
    print("\n=== en que se fija el modelo (10 terminos de mayor peso por clase) ===")
    for idx, clase in enumerate(clf.classes_):
        top = np.argsort(clf.coef_[idx])[-10:][::-1]
        print(f"  {clase:34s}: {', '.join(vocab[top])}")
except FileNotFoundError:
    print("\n(sin tfidf_vectorizer.joblib no se pueden mostrar los terminos por clase)")
