"""
metrics.py — calculadora de metricas compartida para los cuatro modelos base.

Por que existe: si cada persona calcula el macro-F1 por su cuenta, las cuatro filas
de la tabla comparativa (#22) dejan de ser comparables. Esta funcion calcula TODO lo
que pide 2_spec §3 de la misma forma para las cuatro. Se importa, no se copia.

Uso (al final del script de tu modelo, sobre val):

    from metrics import compute_metrics, overfit_gap, LABEL_COLS

    proba_val = model.predict_proba(X_val)          # PROBABILIDADES, no 0/1
    m_val = compute_metrics(y_val, proba_val, LABEL_COLS)
    print("macro-F1 val:", m_val["macro_f1"])
    print("F1 por categoria:", m_val["f1_per_category"])

Gap de sobreajuste (2_spec §3, exige < 0.05):

    m_train = compute_metrics(y_train, model.predict_proba(X_train), LABEL_COLS)
    gap, es_bloqueo = overfit_gap(m_train["macro_f1"], m_val["macro_f1"])
    if es_bloqueo:
        print("BLOQUEO: gap", round(gap, 4), "> 0.05 — documentar en el issue")

macro-F1 por idioma (2_spec §4.3): NO se saca aqui sobre val. val es OPP-115, solo
ingles. El desglose es/en se hace mas tarde llamando a esta misma funcion sobre los
subconjuntos de evaluation_{es,en}.csv. Misma funcion, otros datos.

Reglas fijadas por la spec:
- Umbral 0.5 fijo (2_spec §2.3, valor por defecto). El ajuste por categoria es tarea
  POSTERIOR del equipo, una sola vez, contra val. NO se toca aqui ni en los issues.
- Se evalua contra val. NUNCA contra test (2_spec §6.2).
"""

from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    multilabel_confusion_matrix,
)

# Orden oficial de las 9 categorias (4_data_contract.md). NO reordenar: las columnas
# de y_true / y_proba tienen que salir en este mismo orden.
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


def compute_metrics(y_true, y_proba, label_names=LABEL_COLS, threshold=0.5):
    """
    y_true : matriz 0/1   (n_filas x 9) — etiquetas reales
    y_proba: matriz float (n_filas x 9) — probabilidad de la clase positiva por categoria
    threshold: umbral para binarizar. 0.5 fijo para la tabla comparativa; no cambiarlo aqui.

    Devuelve un dict con todo lo que 2_spec §3 manda reportar.
    """
    # Paso que convierte probabilidad -> 0/1. AQUI vive el umbral.
    y_pred = (y_proba >= threshold).astype(int)

    # Por categoria: un valor por cada una de las 9. zero_division=0 evita el warning
    # cuando una categoria rara (do_not_track) no recibe ninguna prediccion positiva.
    f1_cat = f1_score(y_true, y_pred, average=None, zero_division=0)
    prec_cat = precision_score(y_true, y_pred, average=None, zero_division=0)
    rec_cat = recall_score(y_true, y_pred, average=None, zero_division=0)

    # Una matriz 2x2 [[TN, FP], [FN, TP]] por categoria.
    confusion = multilabel_confusion_matrix(y_true, y_pred)

    return {
        # las dos que van a la tabla comparativa
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        # desgloses para el informe
        "f1_per_category": {n: float(v) for n, v in zip(label_names, f1_cat)},
        "precision_per_category": {n: float(v) for n, v in zip(label_names, prec_cat)},
        "recall_per_category": {n: float(v) for n, v in zip(label_names, rec_cat)},
        "confusion_per_category": {
            n: cm.tolist() for n, cm in zip(label_names, confusion)
        },
        "threshold": threshold,
    }


def overfit_gap(macro_f1_train, macro_f1_val):
    """
    Gap de sobreajuste (2_spec §3): train - val.
    La spec exige < 0.05; si se supera, se documenta como BLOQUEO en el issue, no se oculta.
    Devuelve (gap, es_bloqueo).
    """
    gap = macro_f1_train - macro_f1_val
    return gap, gap > 0.05
