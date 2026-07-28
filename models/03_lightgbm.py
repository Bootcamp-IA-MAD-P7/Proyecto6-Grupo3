"""
03_lightgbm.py — modelo base 3 de 4 (issue #24). Dueña: Ari.

LightGBM (gradient boosting sobre arboles) para clasificacion multi-etiqueta de
fragmentos de politicas de privacidad en 9 categorias.

COMO SE EJECUTA (desde la raiz del repo)
    uv run python models/03_lightgbm.py

QUE PRODUCE
    artifacts/lightgbm_model.joblib   modelo servible (9 cabezas + 9 selectores)
    reports/lightgbm_metrics.json     fila para la tabla comparativa (#22)
    salida por pantalla               metricas y diagnostico de umbral

CONFIGURACION ELEGIDA
Parametros de la pasada 1 + seleccion de 3000 features por categoria. Elegida NO por
rendimiento (la mejora sobre las 13.389 columnas es 0.0009, ruido con 17 politicas en
val) sino porque mantiene el rendimiento con un 78% menos de dimensionalidad: modelo
mas pequeño, mas rapido de entrenar y de servir, y con menos margen para memorizar.

DECISIONES DE ESTE SCRIPT
1. NO se usa OneVsRestClassifier. Su fit no reenvia el conjunto de evaluacion a cada
   cabeza, y cada cabeza necesita vigilar SU columna de etiquetas. Con early stopping
   hace falta el bucle explicito de las 9 cabezas.
2. Early stopping con un dev interno derivado de TRAIN, por politica entera. El val
   oficial NUNCA se usa para vigilar la parada: contaminaria la comparacion.
3. Las 9 cabezas entrenan sobre el MISMO subconjunto de filas (train'), aunque alguna no
   use early stopping. Coste asumido: do_not_track entrena con 16 positivos en vez de 20.
4. El gap se calcula sobre train' (las filas que el modelo realmente uso), no sobre train
   completo: incluir el dev daria un gap artificialmente pequeño.
5. Categorias con menos de MIN_DEV_POSITIVES positivos en el dev NO usan early stopping
   (vigilar con 1 o 2 positivos es ruido). Usan numero fijo de arboles.
6. predict_proba nativo: cumple la regla de calibracion (2_spec §6.4) sin envolver en
   CalibratedClassifierCV. LIMITACION MEDIDA en este proyecto (ver DIAGNOSTICO abajo):
   el boosting da distribuciones bimodales, no solo extremas. El orden es fiable, el
   valor absoluto menos. Se calibra solo si el meta-modelo lo pide.
7. UN SELECTOR POR CATEGORIA, no uno global: las palabras que delatan data_retention no
   son las que delatan do_not_track. Un selector global optimizado para el promedio daria
   a las categorias raras un vocabulario elegido por las frecuentes.
8. El .joblib guarda modelos Y selectores. Sin los selectores, quien sirva el modelo no
   puede reproducir que columnas conservar y las predicciones fallan.

POR QUE ESTO NO ROMPE EL CONTRATO DE DATOS
- NO se reentrena el vectorizador TF-IDF: se parte de X_train.npz tal cual y se conserva
  un SUBCONJUNTO de sus columnas. Vocabulario y pesos IDF son los congelados (#8).
- NO se mueve ninguna fila entre train / val / test. La particion oficial es intacta.
- El selector se ajusta SOLO con train'. Si mirara val para decidir que columnas
  conservar, el macro-F1 dejaria de ser honesto: es el leakage del fit-sobre-el-total
  entrando por otra puerta.
- Es preprocesado interno de este modelo, igual que el transformer usa su propio
  tokenizador en lugar de estas matrices (4_data_contract, regla 2).

===============================================================================
HISTORIAL DE EXPERIMENTOS (evidencia para el issue #24 y el informe)
===============================================================================
Cinco configuraciones, cambiando UNA variable cada vez. Todo contra val, umbral 0.5,
mismo dev interno, metricas via models/metrics.py.

A) Capacidad del modelo (3 pasadas)
  #  num_leaves  min_child  colsample  techo | macro-F1 val   gap
  1      31          40         -      1000  |    0.6973     0.2885
  2      15          60        0.30    1000  |    0.6859     0.2833
  3       7         100        0.15     150  |    0.5724     0.1637

B) class_weight
  balanced : 0.6973 / gap 0.2885      None : 0.6472 / gap 0.3312

C) Numero de features (selector chi2 por categoria)
  13389 : 0.6973 / gap 0.2885    3000 : 0.6982 / gap 0.2808
   1500 : 0.6948 / gap 0.2796     500 : 0.6418 / gap 0.2444

CONCLUSIONES
1. Regularizar la capacidad no reduce el sobreajuste en este dataset. En la pasada 2, al
   quitar capacidad por arbol el early stopping la recupero construyendo mas del doble de
   arboles (first_party: 190 -> 448). La capacidad total es capacidad-por-arbol x
   numero-de-arboles: apretar un factor con el otro libre no sirve. El mismo patron
   reaparecio en la variante de 500 features (data_retention: 143 -> 316 arboles), lo que
   lo confirma como mecanismo y no anecdota.
2. El gap es un DIAGNOSTICO, no un objetivo. La pasada 3 bajo el gap a 0.1637 pero porque
   train' se hundio (0.9693 -> 0.7360), no porque val mejorara: val cayo a 0.5724. Un
   modelo malisimo tiene gap cero. Se optimiza el macro-F1 en val; el gap dice cuanta
   confianza merece esa cifra. Ademas en la pasada 3 las 9 cabezas agotaron el techo de
   150 arboles sin que el early stopping se disparara: los arboles eran tan pequeños que
   el dev mejoraba a migajas y nunca hubo una racha de 50 sin mejora. El entrenamiento se
   corto por techo, no por freno, y el modelo quedo a medio cocer.
3. HIPOTESIS REFUTADA (class_weight). Se sospechaba que "balanced" disparaba falsas
   alarmas en las categorias escasas y hundia su F1. Es lo contrario: sin balanceo el
   modelo las ignora mas. data_retention cayo de 0.4848 a 0.2308. Se queda "balanced".
4. HIPOTESIS PARCIALMENTE REFUTADA (features). Reducir columnas no MEJORA el rendimiento
   de forma significativa (0.6973 -> 0.6982 es ruido con 17 politicas en val). Pero lo
   MANTIENE con un 78% menos de features, y con 1500 (89% menos) sigue en 0.6948. Solo
   al bajar a 500 se rompe. Conclusion util: la señal esta concentrada en unos 1500-3000
   terminos y el resto es ruido que el modelo aprovechaba para memorizar.
5. El gap baja de forma monotona al reducir features (0.2885 -> 0.2444), lo que confirma
   que la causa del sobreajuste es estructural: exceso de columnas frente a filas. Pero
   ni con 500 columnas se acerca al 5%.
6. do_not_track dio F1 1.0000 en casi todas las configuraciones y 0.6667 en la pasada 3.
   Son 6 positivos en val: dos fallos se llevan la cifra. NO se reporta como logro. Es el
   ejemplo de por que el F1 por categoria necesita el numero de positivos al lado.

BLOQUEO DECLARADO (2_spec §3): el gap train'-val es ~0.28, muy por encima del 5% que
exige la spec. No se oculta ni se maquilla bajando el rendimiento. Causa estructural:
13.389 features (3.000 tras seleccion) frente a 2.137 filas de entrenamiento. Cuatro
vias intentadas y documentadas arriba; ninguna lo acerca al 5% sin destruir el modelo.
PENDIENTE DE EQUIPO: el baseline nunca reporto su gap (§3.1 lo marca como pendiente). Si
los otros tres modelos base tienen gaps del mismo orden, lo que hay que revisar es la
regla del 5%, que se fijo antes de conocer la forma de los datos, y no estos modelos.

HALLAZGO PARA EL EQUIPO (ajuste de umbral, 2_spec §2.3): el diagnostico que imprime este
script mide la probabilidad que el modelo da a los positivos REALES de val. Con umbral
fijo 0.5, categorias como third_party y first_party tienen 13-16 positivos entre 0.30 y
0.50: el modelo SI los detecta y el corte los tira. En cambio data_retention con las
13.389 columnas tenia proba media 0.351 y CERO positivos en esa franja: distribucion
bimodal, a unos les da mucho y a otros casi nada. Ahi bajar el umbral no ayudaria. Al
reducir a 3000 features ese patron mejora (proba media 0.412, 3 positivos en la franja).

REGLAS DEL CONTRATO QUE RESPETA (specs/4_data_contract.md)
- La particion oficial se lee de split_assignment.csv. No se vuelve a partir.
- El vectorizador TF-IDF no se reentrena: se cargan las matrices ya generadas.
- Se evalua contra val. test NO se toca.
- Metricas importando metrics.py, umbral 0.5 fijo dentro de la funcion.
- Ante un archivo o columna que falte, raise. Nunca un valor de reemplazo.
"""

import json
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_selection import SelectKBest, chi2

from metrics import LABEL_COLS, compute_metrics, overfit_gap

# ---------------------------------------------------------------- configuracion
TRAINING_TABLE = Path("data/processed/training_table.csv")
SPLIT_ASSIGNMENT = Path("data/processed/split_assignment.csv")
ARTIFACTS = Path("artifacts")
REPORTS = Path("reports")

# Particion interna de train para el early stopping. NO tiene nada que ver con la
# particion oficial (semilla 42, issue #18): ocurre DENTRO de train y ninguna fila
# cruza la frontera train/val/test.
DEV_POLICY_FRACTION = 0.15
INTERNAL_DEV_SEED = 42

MIN_DEV_POSITIVES = 5
N_ESTIMATORS_FIXED = 300     # para las categorias sin early stopping fiable
STOPPING_ROUNDS = 50
K_FEATURES = 3000            # de 13.389; ver experimento C en la cabecera

LGBM_PARAMS = dict(
    n_estimators=1000,       # techo alto: el early stopping encuentra el numero justo
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=40,
    class_weight="balanced",  # confirmado por el experimento B
    n_jobs=-1,
    random_state=42,
    verbosity=-1,
)

# Baseline por categoria (2_spec §3.1), para comparar en la salida.
BASELINE_F1 = {
    "first_party_collection_use": 0.80,
    "third_party_sharing_collection": 0.82,
    "user_choice_control": 0.61,
    "user_access_edit_deletion": 0.59,
    "data_retention": 0.70,
    "data_security": 0.70,
    "policy_change": 0.74,
    "do_not_track": 0.91,
    "international_specific_audiences": 0.85,
}


def require(path: Path) -> Path:
    """Un archivo que falta es un crash, no un fallback (2_spec §6.2)."""
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta antes scripts/04_build_split.py y "
            f"scripts/05_vectorize.py, desde la raiz del repo."
        )
    return path


# ------------------------------------------------------- 1) datos y particion
df = pd.read_csv(require(TRAINING_TABLE))
split = pd.read_csv(require(SPLIT_ASSIGNMENT))

missing = [c for c in ["policy", "segment", *LABEL_COLS] if c not in df.columns]
if missing:
    raise KeyError(f"Faltan columnas en training_table.csv: {missing}")

data = df.merge(split, on=["policy", "segment"], validate="one_to_one")
train_rows = data[data["split"] == "train"].reset_index(drop=True)

X_train_full = sparse.load_npz(require(ARTIFACTS / "X_train.npz"))
y_train_full = np.load(require(ARTIFACTS / "y_train.npy"))
X_val = sparse.load_npz(require(ARTIFACTS / "X_val.npz"))
y_val = np.load(require(ARTIFACTS / "y_val.npy"))

# Si el orden del CSV no es el de la matriz, el mapeo politica -> fila es falso y el dev
# interno mezclaria politicas. Se comprueba en CADA ejecucion, no una sola vez.
if len(train_rows) != X_train_full.shape[0]:
    raise ValueError(
        f"CSV train tiene {len(train_rows)} filas y X_train {X_train_full.shape[0]}."
    )
if not np.array_equal(train_rows[LABEL_COLS].to_numpy(), y_train_full):
    raise ValueError(
        "Las etiquetas del CSV no coinciden con y_train.npy: el orden de filas no es el "
        "mismo. No se puede derivar el dev interno por politica."
    )

# ------------------------------------ 2) dev interno, por politica entera
# Se reparten POLITICAS, no filas: dos fragmentos de la misma politica no pueden caer uno
# en train' y otro en dev. Es la logica del split oficial (§4.1) aplicada dentro de train.
policies = np.sort(train_rows["policy"].unique())
rng = np.random.default_rng(INTERNAL_DEV_SEED)
shuffled = rng.permutation(policies)
n_dev = max(1, round(len(policies) * DEV_POLICY_FRACTION))
dev_policies = set(shuffled[:n_dev])
is_dev = train_rows["policy"].isin(dev_policies).to_numpy()

X_tr, y_tr = X_train_full[~is_dev], y_train_full[~is_dev]
X_dev, y_dev = X_train_full[is_dev], y_train_full[is_dev]

print("=== dev interno derivado de train (para el early stopping) ===")
print(f"train' : {X_tr.shape[0]} filas, {len(policies) - n_dev} politicas")
print(f"dev    : {X_dev.shape[0]} filas, {n_dev} politicas")
print(f"val oficial (intacta) : {X_val.shape[0]} filas")
print(f"features: {X_tr.shape[1]} -> {K_FEATURES} por categoria (selector chi2)\n")

# --------------------------------------------- 3) las 9 cabezas binarias
print("=== entrenando 9 cabezas binarias ===")
models, selectors, best_iters = {}, {}, {}

for k, name in enumerate(LABEL_COLS):
    y_col = y_tr[:, k]
    pos_dev = int(y_dev[:, k].sum())
    use_early = pos_dev >= MIN_DEV_POSITIVES

    # chi2 acepta valores no negativos: TF-IDF lo cumple. fit SOLO sobre train'.
    sel = SelectKBest(chi2, k=min(K_FEATURES, X_tr.shape[1])).fit(X_tr, y_col)
    selectors[name] = sel
    Xtr_k, Xdev_k = sel.transform(X_tr), sel.transform(X_dev)

    if use_early:
        model = lgb.LGBMClassifier(**LGBM_PARAMS)
        model.fit(
            Xtr_k,
            y_col,
            eval_X=Xdev_k,
            eval_y=y_dev[:, k],
            callbacks=[lgb.early_stopping(STOPPING_ROUNDS, verbose=False)],
        )
        best_iters[name] = model.best_iteration_
        nota = ""
    else:
        model = lgb.LGBMClassifier(**{**LGBM_PARAMS, "n_estimators": N_ESTIMATORS_FIXED})
        model.fit(Xtr_k, y_col)
        best_iters[name] = N_ESTIMATORS_FIXED
        nota = f"  (sin early stopping: solo {pos_dev} positivos en el dev)"

    models[name] = model
    print(f"  {name:36s} arboles: {best_iters[name]}{nota}")


# ------------------------------------------------ 4) probabilidades (n filas x 9)
def proba_matrix(X) -> np.ndarray:
    """Las 9 probabilidades apiladas, en el orden oficial de LABEL_COLS.

    Cada cabeza aplica SU selector antes de predecir: por eso el .joblib tiene que
    guardar los selectores junto a los modelos.
    """
    cols = [
        models[name].predict_proba(selectors[name].transform(X))[:, 1]
        for name in LABEL_COLS
    ]
    return np.column_stack(cols)


proba_val = proba_matrix(X_val)
proba_tr = proba_matrix(X_tr)   # train', las filas que el modelo si uso

# --------------------------------------- 5) metricas con el modulo compartido
m_val = compute_metrics(y_val, proba_val, LABEL_COLS)
m_tr = compute_metrics(y_tr, proba_tr, LABEL_COLS)
gap, es_bloqueo = overfit_gap(m_tr["macro_f1"], m_val["macro_f1"])

print("\n=== resultados (umbral 0.5, fijado dentro de metrics.py) ===")
print(f"macro-F1 val    : {m_val['macro_f1']:.4f}")
print(f"micro-F1 val    : {m_val['micro_f1']:.4f}")
print(f"macro-F1 train2 : {m_tr['macro_f1']:.4f}")
print(
    f"gap train2-val  : {gap:.4f}",
    "  <-- BLOQUEO DECLARADO (>0.05)" if es_bloqueo else "  (ok, <0.05)",
)
print("referencias     : baseline 0.7466 - rango publicado OPP-115 65-76%")

print("\nF1 por categoria en val (columna obligatoria de la tabla #22)")
print(f"  {'categoria':34s} {'pos':>5s} {'F1':>8s} {'baseline':>9s}")
for k, name in enumerate(LABEL_COLS):
    pos = int(y_val[:, k].sum())
    f1 = m_val["f1_per_category"][name]
    aviso = "  <- muestra minima, cifra no robusta" if pos < 10 else ""
    print(f"  {name:34s} {pos:5d} {f1:8.4f} {BASELINE_F1[name]:9.2f}{aviso}")

# ------------------------- 6) diagnostico de umbral (informativo, no cambia el 0.5)
print("\n=== diagnostico de umbral (informativo; el de la tabla sigue en 0.5) ===")
print("Probabilidad que el modelo da a los positivos REALES de val.")
print(f"  {'categoria':34s} {'pos':>5s} {'proba media':>12s} {'entre .30 y .50':>17s}")
umbral_diag = {}
for k, name in enumerate(LABEL_COLS):
    mask = y_val[:, k] == 1
    pos = int(mask.sum())
    if pos == 0:
        continue
    p = proba_val[mask, k]
    casi = int(((p >= 0.30) & (p < 0.50)).sum())
    umbral_diag[name] = {"positivos": pos, "proba_media": round(float(p.mean()), 3),
                         "entre_030_050": casi}
    print(f"  {name:34s} {pos:5d} {p.mean():12.3f} {casi:17d}")
print("Muchos entre .30 y .50 = el modelo los detecta y el corte fijo los tira (§2.3).")
print("Proba media baja pero CERO en la franja = bimodal: bajar el umbral no ayudaria.")

# --------------------------------- 7) guardar modelo servible y fila de la tabla
# La API sirve UN modelo base ya entrenado (5_backend_contract). Sin este paso habria que
# reentrenar solo para desplegar. artifacts/ esta en .gitignore: el binario no va al repo.
MODEL_PATH = ARTIFACTS / "lightgbm_model.joblib"
joblib.dump(
    {
        "models": models,
        "selectors": selectors,     # imprescindibles: cada cabeza tiene sus columnas
        "label_cols": LABEL_COLS,   # el orden oficial, para no reordenar al servir
        "params": LGBM_PARAMS,
        "k_features": K_FEATURES,
        "threshold": 0.5,
        "trained_on": "train' (2137 filas, 68 politicas); dev interno apartado",
    },
    MODEL_PATH,
)
print(f"\nModelo guardado en {MODEL_PATH}")
print("  contiene: 9 modelos + 9 selectores + orden de etiquetas + umbral")

REPORTS.mkdir(exist_ok=True)
row = {
    "model": "LightGBM (9 cabezas binarias, chi2 3000 features)",
    "owner": "Ari",
    "issue": 24,
    "family": "gradient boosting sobre arboles",
    "threshold": 0.5,
    "macro_f1_val": round(m_val["macro_f1"], 4),
    "micro_f1_val": round(m_val["micro_f1"], 4),
    "macro_f1_train_internal": round(m_tr["macro_f1"], 4),
    "overfit_gap": round(gap, 4),
    "gap_is_blocker": bool(es_bloqueo),
    "f1_per_category_val": {k: round(v, 4) for k, v in m_val["f1_per_category"].items()},
    "positives_in_val": {n: int(y_val[:, i].sum()) for i, n in enumerate(LABEL_COLS)},
    "trees_used_per_category": best_iters,
    "threshold_diagnostic": umbral_diag,
    "experiments_run": {
        "capacity_passes": {"leaves31": 0.6973, "leaves15": 0.6859, "leaves7": 0.5724},
        "class_weight": {"balanced": 0.6973, "none": 0.6472},
        "n_features": {"13389": 0.6973, "3000": 0.6982, "1500": 0.6948, "500": 0.6418},
    },
    "notes": (
        "Gap declarado como bloqueo (2_spec 3), causa estructural: mas features que "
        "filas. Cuatro vias intentadas, ninguna acerca al 5% sin destruir el modelo. "
        "do_not_track F1 sobre 6 positivos en val: cifra no robusta. Pendiente de "
        "equipo: el baseline nunca reporto su gap."
    ),
}
with open(REPORTS / "lightgbm_metrics.json", "w", encoding="utf-8") as f:
    json.dump(row, f, indent=2, ensure_ascii=False)
print(f"Fila de la tabla comparativa en {REPORTS / 'lightgbm_metrics.json'}")
