"""
14_evaluate_test_and_extension.py -- evaluacion final del modelo en produccion.

QUE HACE
Corre el modelo que sirve la API (artifacts/multiclass_complementnb.joblib +
artifacts/tfidf_vectorizer.joblib) contra dos conjuntos que nunca tocaron el
entrenamiento ni la seleccion de modelo.

1. El split test de OPP-115 (multiclass_target.csv, split == "test", 663 filas).
   Es la primera vez que este conjunto se usa para algo. 12_multiclass_compare.py
   solo usa train y val, y elige el modelo con esos dos. Esta es la evaluacion
   final que ese script deja pendiente por diseno.

2. evaluation_es.csv y evaluation_en.csv, derivados de dataset_extension. NO es
   una evaluacion equivalente a la anterior, y el resultado se documenta como tal.
   - Las etiquetas son preanotacion automatica por reglas, label_source vale
     silver_rules_not_validated en los dos CSV, no anotacion humana. Medir contra
     ellas mide el acuerdo entre dos clasificadores automaticos distintos, uno
     entrenado y uno por reglas, no accuracy contra ground truth.
   - El vocabulario es de politicas de 2025-2026, frente al de OPP-115, de 2016.
     El proposito de esta parte es ver como reacciona el modelo a vocabulario y
     practicas que no existian cuando se recogio el corpus de entrenamiento.
   - Las 9 columnas binarias de estos CSV se reducen a una sola clase con la
     MISMA regla de prioridad de scripts/10_build_multiclass_target.py, para
     poder comparar contra una prediccion multiclase. Si esa regla cambia alli,
     debe cambiar aqui tambien.

COMO SE EJECUTA (desde la raiz del repo)
    uv run python models/14_evaluate_test_and_extension.py

ESCRIBE
    reports/test_evaluation.json
    reports/dataset_extension_evaluation.json
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.translation import translate_fragments  # noqa: E402

TRAINING_TABLE = Path("data/processed/training_table.csv")
MULTICLASS_TARGET = Path("data/processed/multiclass_target.csv")
EVAL_ES = Path("data/processed/evaluation_es.csv")
EVAL_EN = Path("data/processed/evaluation_en.csv")
MODEL_PATH = Path("artifacts/multiclass_complementnb.joblib")
VECTORIZER_PATH = Path("artifacts/tfidf_vectorizer.joblib")

OUT_TEST = Path("reports/test_evaluation.json")
OUT_EXTENSION = Path("reports/dataset_extension_evaluation.json")

# Misma regla que scripts/10_build_multiclass_target.py. No reordenar sin
# actualizar ese script tambien, tienen que coincidir.
PRIORITY = [
    "third_party_sharing_collection",
    "data_retention",
    "do_not_track",
    "user_access_edit_deletion",
    "user_choice_control",
    "data_security",
    "international_specific_audiences",
    "policy_change",
    "first_party_collection_use",
]
OTHER = "Other"


def assign_class(row) -> str:
    for name in PRIORITY:
        if row[name] == 1:
            return name
    return OTHER


def evaluate(model, vectorizer, texts, y_true, label):
    X = vectorizer.transform(texts)
    y_pred = model.predict(X)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    per_class = {
        k: v for k, v in report.items()
        if k not in ("accuracy", "macro avg", "weighted avg")
    }
    return {
        "label": label,
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "per_class": per_class,
    }


def require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"No existe {path}.")
    return path


def main():
    model_bundle = joblib.load(require(MODEL_PATH))
    model = model_bundle["model"]
    vectorizer = joblib.load(require(VECTORIZER_PATH))

    # 1) OPP-115, split test, nunca visto por el modelo hasta ahora.
    training_table = pd.read_csv(require(TRAINING_TABLE))
    multiclass_target = pd.read_csv(require(MULTICLASS_TARGET))
    data = multiclass_target.merge(
        training_table[["policy", "segment", "text"]],
        on=["policy", "segment"],
        validate="one_to_one",
    )
    test = data[data["split"] == "test"]

    test_result = evaluate(model, vectorizer, test["text"], test["label"], "opp115_test")

    print("=== OPP-115, split test, nunca visto por el modelo ===")
    print(f"filas: {test_result['n']}")
    print(f"accuracy: {test_result['accuracy']:.4f}")
    print(f"macro-F1: {test_result['macro_f1']:.4f}")

    OUT_TEST.parent.mkdir(parents=True, exist_ok=True)
    OUT_TEST.write_text(json.dumps(test_result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Escrito: {OUT_TEST}")

    # 2) dataset_extension, vocabulario moderno, etiquetas silver, no comparable
    #    en rigor con el test de arriba. La salvedad queda en el propio JSON.
    ext = pd.concat(
        [pd.read_csv(require(EVAL_ES)), pd.read_csv(require(EVAL_EN))],
        ignore_index=True,
    )
    ext["label"] = ext.apply(assign_class, axis=1)

    ext_result = evaluate(model, vectorizer, ext["text"], ext["label"], "dataset_extension")
    ext_result["caveat"] = (
        "Las etiquetas de este conjunto son preanotacion automatica por reglas "
        "(label_source=silver_rules_not_validated en evaluation_es.csv y "
        "evaluation_en.csv), no anotacion humana. Este numero mide el acuerdo "
        "entre el modelo entrenado y un clasificador de reglas distinto, no "
        "accuracy contra ground truth. No es comparable en rigor con "
        "opp115_test. Uso previsto, ver como reacciona el modelo, entrenado "
        "sobre OPP-115 de 2016, a vocabulario y practicas de politicas de "
        "2025-2026, la mayoria en espanol."
    )

    by_language = {}
    for lang, group in ext.groupby("language"):
        by_language[lang] = evaluate(
            model, vectorizer, group["text"], group["label"], f"dataset_extension_{lang}"
        )
    ext_result["by_language"] = by_language

    # 2b) El espanol sin traducir es ruido por diseno (translation.py lo documenta,
    #     el vocabulario TF-IDF esta en ingles). Traducimos con la misma capa que
    #     usa la API real, para saber que numero produce el sistema en produccion,
    #     no solo el modelo aislado sobre texto sin traducir.
    es_group = ext[ext["language"] == "es"]
    translation_result = translate_fragments(es_group["text"].tolist(), "es")
    es_translated_result = evaluate(
        model, vectorizer, translation_result.texts, es_group["label"], "dataset_extension_es_translated"
    )
    es_translated_result["translation_available"] = translation_result.available
    es_translated_result["translation_note"] = translation_result.note
    ext_result["es_translated"] = es_translated_result

    print("\n=== dataset_extension, vocabulario moderno, etiquetas silver ===")
    print(f"filas: {ext_result['n']}")
    print(f"accuracy: {ext_result['accuracy']:.4f}")
    print(f"macro-F1: {ext_result['macro_f1']:.4f}")
    for lang, res in by_language.items():
        print(f"  {lang}: n={res['n']} accuracy={res['accuracy']:.4f} macro_f1={res['macro_f1']:.4f}")
    print(
        f"  es_translated (translation_available={translation_result.available}): "
        f"n={es_translated_result['n']} accuracy={es_translated_result['accuracy']:.4f} "
        f"macro_f1={es_translated_result['macro_f1']:.4f}"
    )

    OUT_EXTENSION.write_text(json.dumps(ext_result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Escrito: {OUT_EXTENSION}")


if __name__ == "__main__":
    main()
