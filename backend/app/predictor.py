"""
Módulo encargado de realizar la inferencia del modelo de Machine Learning.

Este archivo actúa como puente entre la API y el modelo entrenado. Su función
es cargar el vectorizador TF-IDF y el modelo previamente entrenados, transformar
los fragmentos de texto recibidos en características numéricas y obtener las
probabilidades de predicción para cada categoría.

Responsabilidades:
- Cargar el vectorizador almacenado en la carpeta artifacts.
- Cargar el modelo entrenado una única vez al iniciar la aplicación.
- Vectorizar los fragmentos de texto recibidos.
- Ejecutar la inferencia mediante el modelo.
- Devolver las probabilidades que serán utilizadas por analyze.py para
  construir la respuesta de la API.

Este módulo no realiza entrenamiento, ajuste de hiperparámetros ni cálculo de
métricas. Su única responsabilidad es ejecutar predicciones utilizando un
modelo previamente entrenado, permitiendo además sustituir el modelo en el
futuro sin modificar el resto del backend.
"""
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from .categories import CATEGORIES

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "artifacts"
MODEL_PATH = ARTIFACTS / "multiclass_complementnb.joblib"
VECTORIZER_PATH = ARTIFACTS / "tfidf_vectorizer.joblib"

MODEL_VERSION = "1.0.0"


@lru_cache(maxsize=1)
def _load():
    """Carga modelo y vectorizador UNA sola vez (lru_cache), no en cada peticion.

    El vectorizador no es opcional: el modelo solo entiende matrices TF-IDF, no
    texto. Sin el no hay nada sobre lo que predecir.
    """
    for path in (MODEL_PATH, VECTORIZER_PATH):
        if not path.exists():
            raise FileNotFoundError(
                f"Falta {path}. Ejecuta scripts/05_vectorize.py y "
                f"models/12_multiclass_compare.py antes de arrancar la API."
            )

    model = joblib.load(MODEL_PATH)["model"]
    vectorizer = joblib.load(VECTORIZER_PATH)

    # CRITICO: predict_proba devuelve las columnas en el orden de model.classes_,
    # que es ALFABETICO, no el de CATEGORIES. Sin este remapeo cada probabilidad
    # aterrizaria en la categoria equivocada, y en silencio: no habria error, solo
    # resultados incorrectos.
    trained = list(model.classes_)
    missing = [c for c in CATEGORIES if c not in trained]
    if missing:
        raise ValueError(
            f"El modelo no fue entrenado con estas clases: {missing}. "
            f"Entrenadas: {trained}"
        )
    column_order = [trained.index(c) for c in CATEGORIES]
    return model, vectorizer, column_order


def predict_proba(fragment_texts: list[str], full_text: str) -> np.ndarray:
    """Matriz (n_fragmentos, n_clases) con las columnas en el orden de CATEGORIES.

    Misma firma que stub.predict_proba: es la costura del contrato, asi que
    analyze.py solo cambia el modulo que llama.
    """
    if not fragment_texts:
        return np.empty((0, len(CATEGORIES)))
    model, vectorizer, column_order = _load()
    X = vectorizer.transform(fragment_texts)
    return model.predict_proba(X)[:, column_order]