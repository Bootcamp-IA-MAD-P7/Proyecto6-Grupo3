"""
12_multiclass_compare.py — paso 3 del enfoque multiclase. Comparativa de modelos.

QUE HACE
Entrena TRES modelos multiclase sobre el mismo target, las mismas features y la misma
particion, y los compara en una tabla. Cambia SOLO el algoritmo: todo lo demas es identico,
asi que las diferencias son atribuibles al modelo y no al montaje.

  1. LogisticRegression (multinomial)  el baseline del paso 2, aqui como referencia
  2. LinearSVC                          margen maximo; la literatura dice que es el clasico
                                        mas fuerte en este corpus (gano en Wilson 2016 y en
                                        Liu 2018 sobre OPP-115)
  3. ComplementNB                       probabilistico, diseñado para clases desbalanceadas

POR QUE TRES MODELOS Y NO UN ENSAMBLE
La tutora indico que el ensamble no es necesario y que combinar modelos que discrepan no
era conveniente. Se cubre lo mismo que pedia (varios modelos y un criterio para elegir uno)
entrenandolos por separado y comparandolos: se entrega UN modelo, elegido con evidencia.

QUE REUTILIZA SIN TOCAR
- artifacts/X_{train,val}.npz : matrices TF-IDF congeladas (issue #8).
- La particion oficial (semilla 42, por politica, issue #18).
- data/processed/multiclass_target.csv (scripts/10_build_multiclass_target.py).
- test NO se carga en ningun momento.

NOTA SOBRE LinearSVC
No emite probabilidades (devuelve distancia al margen). Para este enfoque no hace falta:
en multiclase la prediccion es la clase con mayor puntuacion, no hay umbral que calibrar.
Si el semaforo llegara a necesitar una confianza por fragmento, se envuelve en
CalibratedClassifierCV, que es una linea.

METRICAS
- accuracy : % de fragmentos bien clasificados. SUELO 0.3454 en val (predecir siempre la
             clase mayoritaria). En multiclase de etiqueta unica, micro-F1 == accuracy.
- macro-F1 : promedio simple del F1 de las 10 clases; cada clase pesa igual. Es la que dice
             si el modelo atiende tambien a las pequeñas (do_not_track tiene 6 en val).
- gap      : train menos val. DIAGNOSTICO de sobreajuste, no objetivo a optimizar: bajarlo
             sacrificando rendimiento produce un modelo peor (comprobado en el enfoque
             multi-etiqueta, tres pasadas documentadas en models/03_lightgbm.py).

Referencias del enfoque multi-etiqueta, para contexto (macro-F1 en val):
  LogReg 0.7466 · LightGBM 0.6982 · ComplementNB 0.6956 · DeBERTa 0.5785
Rango publicado sobre OPP-115: 65-76% macro-F1 (Mousavi Nejad et al. 2020).

COMO SE EJECUTA (desde la raiz del repo)
    uv run python models/12_multiclass_compare.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC

TARGET = Path("data/processed/multiclass_target.csv")
ARTIFACTS = Path("artifacts")
REPORTS = Path("reports")

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

MODELS = {
    "LogReg": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    "LinearSVC": LinearSVC(class_weight="balanced", random_state=42, max_iter=5000),
    "ComplementNB": ComplementNB(alpha=0.1),   # alpha 0.1 fue el mejor en el enfoque
                                               # multi-etiqueta (issue #23, Nai)
}


def require(path: Path) -> Path:
    """Un archivo que falta es un crash, no un fallback (2_spec §6.2)."""
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta antes scripts/10_build_multiclass_target.py "
            f"y scripts/05_vectorize.py, desde la raiz del repo."
        )
    return path


# ------------------------------------------------- 1) datos
tgt = pd.read_csv(require(TARGET))
X_train = sparse.load_npz(require(ARTIFACTS / "X_train.npz"))
X_val = sparse.load_npz(require(ARTIFACTS / "X_val.npz"))

y_train = tgt.loc[tgt["split"] == "train", "label"].to_numpy()
y_val = tgt.loc[tgt["split"] == "val", "label"].to_numpy()

if len(y_train) != X_train.shape[0] or len(y_val) != X_val.shape[0]:
    raise ValueError(
        "El target y los artefactos no estan alineados: "
        f"train {len(y_train)} vs {X_train.shape[0]}, val {len(y_val)} vs {X_val.shape[0]}."
    )

mayoritaria = pd.Series(y_train).value_counts().idxmax()
suelo = float((y_val == mayoritaria).mean())

print("=== datos ===")
print(f"train {X_train.shape[0]} filas x {X_train.shape[1]} features · val {X_val.shape[0]} filas")
print(f"SUELO de accuracy en val: {suelo:.4f} (predecir siempre '{mayoritaria}')")
print("test NO se carga.\n")

# ------------------------------------------------- 2) entrenar los tres
results = {}
for name, model in MODELS.items():
    print(f"entrenando {name}...")
    model.fit(X_train, y_train)
    pv, pt = model.predict(X_val), model.predict(X_train)
    results[name] = {
        "model": model,
        "pred_val": pv,
        "acc_val": accuracy_score(y_val, pv),
        "acc_train": accuracy_score(y_train, pt),
        "macro_val": f1_score(y_val, pv, average="macro", zero_division=0),
        "macro_train": f1_score(y_train, pt, average="macro", zero_division=0),
        "f1_per_class": dict(
            zip(CLASSES, f1_score(y_val, pv, average=None, labels=CLASSES, zero_division=0))
        ),
    }
    r = results[name]
    print(f"  accuracy val {r['acc_val']:.4f} · macro-F1 val {r['macro_val']:.4f}\n")

# ------------------------------------------------- 3) tabla comparativa
print("=" * 78)
print("COMPARATIVA MULTICLASE (10 clases, val = 579 filas)")
print("=" * 78)
print(f"{'modelo':16s} {'accuracy':>9s} {'macro-F1':>9s} {'acc train':>10s} {'gap acc':>9s} {'gap macro':>10s}")
for name, r in results.items():
    print(
        f"{name:16s} {r['acc_val']:9.4f} {r['macro_val']:9.4f} {r['acc_train']:10.4f} "
        f"{r['acc_train']-r['acc_val']:9.4f} {r['macro_train']-r['macro_val']:10.4f}"
    )
print(f"{'(suelo)':16s} {suelo:9.4f} {'-':>9s}")

print("\n=== F1 por clase en val ===")
head = f"{'clase':34s} {'pos':>5s}"
for name in results:
    head += f" {name:>13s}"
print(head)
soporte = pd.Series(y_val).value_counts()
for c in CLASSES:
    pos = int(soporte.get(c, 0))
    line = f"{c:34s} {pos:5d}"
    for name, r in results.items():
        line += f" {r['f1_per_class'][c]:13.4f}"
    if pos < 10:
        line += "  <- muestra minima"
    print(line)

# ------------------------------------------------- 4) el mejor y su matriz
# Umbral de diferencia minima. Con 579 filas y solo 17 politicas en val, diferencias de
# macro-F1 por debajo de este valor no se distinguen del azar: elegir por ellas es elegir
# por ruido. Caso real de esta comparativa: LogReg 0.7121 frente a ComplementNB 0.7118,
# tres diezmilesimas. Cuando el empate es tecnico, desempata el GAP: menor sobreajuste
# significa mas fiabilidad ante politicas que el modelo no ha visto, que es el uso real.
MIN_DIFF = 0.01


def elegir_modelo(res: dict, min_diff: float = MIN_DIFF):
    """Elige por macro-F1; si hay empate tecnico, desempata por el gap de macro-F1."""
    tope = max(r["macro_val"] for r in res.values())
    empatados = [n for n, r in res.items() if tope - r["macro_val"] < min_diff]
    if len(empatados) == 1:
        return empatados[0], "mejor macro-F1 en val, con diferencia significativa"
    ganador = min(empatados, key=lambda n: res[n]["macro_train"] - res[n]["macro_val"])
    otros = ", ".join(n for n in empatados if n != ganador)
    return ganador, (
        f"empate tecnico con {otros} (diferencia < {min_diff} en macro-F1, "
        f"indistinguible del azar con 17 politicas en val); desempata el menor gap"
    )


best_name, motivo = elegir_modelo(results)
best = results[best_name]
print(f"\nMODELO ELEGIDO: {best_name}")
print(f"  macro-F1 val {best['macro_val']:.4f} · accuracy val {best['acc_val']:.4f} · "
      f"gap macro {best['macro_train'] - best['macro_val']:.4f}")
print(f"  criterio: {motivo}")
cm = confusion_matrix(y_val, best["pred_val"], labels=CLASSES)
cols = [SHORT[c] for c in CLASSES]
print(f"\n=== matriz de confusion de {best_name} en val ===")
print("filas = clase REAL · columnas = lo PREDICHO · la diagonal son los aciertos\n")
print(f"{'real \\ pred':>12s} " + " ".join(f"{c:>9s}" for c in cols))
for i, c in enumerate(CLASSES):
    print(f"{SHORT[c]:>12s} " + " ".join(f"{v:9d}" for v in cm[i]))

print("\n=== confusiones mas frecuentes ===")
pares = []
for i, real in enumerate(CLASSES):
    for j, pred in enumerate(CLASSES):
        if i != j and cm[i][j] > 0:
            tot = cm[i].sum()
            pares.append((int(cm[i][j]), real, pred, 100 * cm[i][j] / tot if tot else 0))
pares.sort(reverse=True)
for n, real, pred, pct in pares[:8]:
    print(f"  {n:3d} de {real} -> {pred}  ({pct:.0f}% de su clase)")

# ------------------------------------------------- 5) guardar
REPORTS.mkdir(exist_ok=True)
rows = []
for name, r in results.items():
    rows.append({
        "approach": "multiclase (10 clases)",
        "model": name,
        "accuracy_val": round(r["acc_val"], 4),
        "macro_f1_val": round(r["macro_val"], 4),
        "accuracy_train": round(r["acc_train"], 4),
        "macro_f1_train": round(r["macro_train"], 4),
        "gap_accuracy": round(r["acc_train"] - r["acc_val"], 4),
        "gap_macro_f1": round(r["macro_train"] - r["macro_val"], 4),
        "accuracy_floor_val": round(suelo, 4),
        **{f"f1_{c}": round(v, 4) for c, v in r["f1_per_class"].items()},
    })
out = REPORTS / "multiclass_comparison.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print(f"\nEscrito: {out}")

import joblib

MODEL_PATH = ARTIFACTS / f"multiclass_{best_name.lower()}.joblib"
joblib.dump(
    {
        "model": best["model"],
        "classes": CLASSES,
        "approach": "multiclass",
        "trained_on": "train (2550 filas, 80 politicas)",
        "note": "usa el vectorizador de artifacts/tfidf_vectorizer.joblib para transformar texto nuevo",
    },
    MODEL_PATH,
)
print(f"Modelo servible guardado en {MODEL_PATH}")
