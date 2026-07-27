# models/02_complement_nb.py
import sys
from pathlib import Path
import joblib
import numpy as np
from scipy import sparse
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import ComplementNB

# Asegurar la ruta a la raíz del proyecto para importaciones relativas
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from models.metrics import LABEL_COLS, compute_metrics, overfit_gap

# Rutas de artefactos requeridos según la SPEC 4
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
X_TRAIN_PATH = ARTIFACTS_DIR / "X_train.npz"
Y_TRAIN_PATH = ARTIFACTS_DIR / "y_train.npy"
X_VAL_PATH = ARTIFACTS_DIR / "X_val.npz"
Y_VAL_PATH = ARTIFACTS_DIR / "y_val.npy"


def load_artifacts():
    """
    Carga los artefactos vectorizados generados por scripts/05_vectorize.py
    cumpliendo estrictamente con el contrato de la SPEC 4.
    """
    paths_to_check = [X_TRAIN_PATH, Y_TRAIN_PATH, X_VAL_PATH, Y_VAL_PATH]
    for path in paths_to_check:
        if not path.exists():
            raise FileNotFoundError(
                f"Falta el artefacto requerido: '{path}'. "
                "Ejecuta 'uv run python scripts/05_vectorize.py' primero."
            )

    X_train = sparse.load_npz(X_TRAIN_PATH)
    y_train = np.load(Y_TRAIN_PATH)
    X_val = sparse.load_npz(X_VAL_PATH)
    y_val = np.load(Y_VAL_PATH)

    return X_train, y_train, X_val, y_val


def extract_probabilities(ovr_model, X) -> np.ndarray:
    """
    Extrae las probabilidades de la clase positiva (1) para las 9 categorías.
    Devuelve un array 2D de numpy con dimensión (N_muestras, 9).
    """
    proba_list = ovr_model.predict_proba(X)
    
    if isinstance(proba_list, list):
        pos_cols = [p[:, 1] for p in proba_list]
        return np.column_stack(pos_cols)
    elif isinstance(proba_list, np.ndarray):
        if proba_list.ndim == 3:    # Estructura: (N, 9, 2)
            return proba_list[:, :, 1]
        elif proba_list.ndim == 2:  # Estructura: (N, 9)
            return proba_list

    raise ValueError(f"Formato inesperado devuelto por predict_proba: {type(proba_list)}")


def train_and_select_best_complement_nb(alphas=(0.1, 0.5, 1.0)):
    """
    Evalúa una pequeña cuadrícula de alpha y selecciona el modelo con el Macro-F1 de validación más alto.
    """
    X_train, y_train, X_val, y_val = load_artifacts()

    best_alpha = None
    best_macro_f1 = -1.0
    best_ovr_model = None
    best_m_train = None
    best_m_val = None

    print(f"[1/4] Evaluating alpha grid: {alphas}...")

    for alpha in alphas:
        
        base_estimator = ComplementNB(alpha=alpha)
        ovr_model = OneVsRestClassifier(base_estimator)
        ovr_model.fit(X_train, y_train)

        y_proba_train = extract_probabilities(ovr_model, X_train)
        y_proba_val = extract_probabilities(ovr_model, X_val)

        m_train = compute_metrics(y_train, y_proba_train, LABEL_COLS)
        m_val = compute_metrics(y_val, y_proba_val, LABEL_COLS)

        current_val_macro = m_val["macro_f1"]

        print(f"  • alpha={alpha:<4} --> Val Macro-F1: {current_val_macro:.4f}")

        # Selección simple basada únicamente en el desempeño de Macro-F1 en validación
        if current_val_macro > best_macro_f1:
            best_macro_f1 = current_val_macro
            best_alpha = alpha
            best_ovr_model = ovr_model
            best_m_train = m_train
            best_m_val = m_val

    print(f"\n[2/4] Selected hyperparameter: alpha={best_alpha}")

    # Evaluación post-selección del overfit gap
    gap, blocked = overfit_gap(best_m_train["macro_f1"], best_m_val["macro_f1"])

    print("\n" + "=" * 60)
    print(f"MODEL RESULTS: ComplementNB (alpha={best_alpha})")
    print("=" * 60)
    print(f"Train Macro-F1 : {best_m_train['macro_f1']:.4f} | Micro-F1: {best_m_train['micro_f1']:.4f}")
    print(f"Val   Macro-F1 : {best_m_val['macro_f1']:.4f} | Micro-F1: {best_m_val['micro_f1']:.4f}")
    print(f"Overfit Gap    : {gap:.4f} (Train - Val)")

    if blocked:
        print("\nWARNING: Overfit gap exceeds SPEC.")
    else:
        print("\n✓ ÉXITO: Brecha de sobreajuste <= 0.05 (Cumple criterios esenciales de SPEC 1 y 2).")

    print("\n--- Validation F1 per category ---")
    for category, score in best_m_val["f1_per_category"].items():
        print(f"  • {category:<35}: {score:.4f}")

    return best_ovr_model, best_m_val


if __name__ == "__main__":
    trained_model, final_metrics = train_and_select_best_complement_nb()

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    save_path = ARTIFACTS_DIR / "complement_nb_model.joblib"

    print(f"\n[3/4] Guardando el artefacto del modelo en: {save_path}...")
    joblib.dump(trained_model, save_path)
    print("[4/4] ¡Entrenamiento y exportación del modelo completados con éxito!")