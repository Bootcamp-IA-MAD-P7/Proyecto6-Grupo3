"""Tune TF-IDF and linear classifiers using only the frozen train/val split.

This experiment intentionally does not read X_test, y_test, or dataset_extension.
It preserves the policy-level split from ``split_assignment.csv`` and fits every
candidate vectorizer exclusively on train text.

The definitive Joblib is written only when a configuration satisfies the
project overfitting rule: macro-F1(train) - macro-F1(val) <= 0.05.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

import joblib
import numpy as np
from scipy import sparse
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC

if __package__:
    from .metrics import LABEL_COLS
else:
    from metrics import LABEL_COLS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_TABLE = PROJECT_ROOT / "data" / "processed" / "training_table.csv"
SPLIT_ASSIGNMENT = PROJECT_ROOT / "data" / "processed" / "split_assignment.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "artifacts" / "linear_svc_model.joblib"

RANDOM_STATE = 42
CALIBRATION_FOLDS = 5
DEFAULT_THRESHOLD = 0.5
MAX_ALLOWED_GAP = 0.05
MODEL_VERSION = "2.0"

# Strong regularisation is intentionally explored below the previous 0.01 floor.
C_VALUES = (0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
CLASS_WEIGHTS = (None, "balanced")
MODEL_NAMES = ("linear_svc", "logistic_regression")
SCREENING_C = 0.01

BASE_VECTORIZER_CONFIG = {
    "min_df": 3,
    "max_df": 0.90,
    "ngram_range": (1, 2),
    "max_features": None,
    "sublinear_tf": True,
}


@dataclass(frozen=True)
class TextSplit:
    """Raw text and nine binary targets for one official split."""

    texts: list[str]
    y: np.ndarray


@dataclass(frozen=True)
class TrainValData:
    """Only the two splits authorised for model development."""

    train: TextSplit
    val: TextSplit


@dataclass
class Candidate:
    """One fitted candidate and its comparable measurements."""

    stage: str
    model_name: str
    C: float
    class_weight: str | None
    vectorizer_config: dict[str, Any]
    n_features: int
    train_macro_f1: float
    val_macro_f1: float
    train_micro_f1: float
    val_micro_f1: float
    gap: float
    elapsed_seconds: float
    model: OneVsRestClassifier
    vectorizer: TfidfVectorizer

    @property
    def valid(self) -> bool:
        return abs(self.gap) <= MAX_ALLOWED_GAP


def _require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path


def _load_allowed_keys(path: Path) -> dict[tuple[str, int], str]:
    """Load only train/val assignments; test keys are deliberately discarded."""
    allowed: dict[tuple[str, int], str] = {}
    with _require_file(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"policy", "segment", "split"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain columns {sorted(required)}.")
        for row in reader:
            split_name = row["split"]
            if split_name not in {"train", "val"}:
                continue
            key = (row["policy"], int(row["segment"]))
            if key in allowed:
                raise ValueError(f"Duplicate split key: {key}")
            allowed[key] = split_name
    if not allowed:
        raise ValueError("No train/validation assignments were found.")
    return allowed


def load_train_val(
    training_table: Path = TRAINING_TABLE,
    split_assignment: Path = SPLIT_ASSIGNMENT,
) -> TrainValData:
    """Stream the canonical table and retain only official train/val rows."""
    allowed = _load_allowed_keys(split_assignment)
    texts: dict[str, list[str]] = {"train": [], "val": []}
    labels: dict[str, list[list[int]]] = {"train": [], "val": []}
    seen: set[tuple[str, int]] = set()

    with _require_file(training_table).open(
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        required = {"policy", "segment", "text", *LABEL_COLS}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"{training_table} must contain columns {sorted(required)}."
            )
        for row in reader:
            key = (row["policy"], int(row["segment"]))
            split_name = allowed.get(key)
            if split_name is None:
                continue
            if key in seen:
                raise ValueError(f"Duplicate training-table key: {key}")
            seen.add(key)
            texts[split_name].append(row["text"])
            labels[split_name].append([int(row[label]) for label in LABEL_COLS])

    missing = set(allowed) - seen
    if missing:
        sample = sorted(missing)[:3]
        raise ValueError(f"{len(missing)} split keys have no data rows; sample={sample}")

    def make_split(name: str) -> TextSplit:
        y = np.asarray(labels[name], dtype=np.int8)
        if not texts[name] or y.shape != (len(texts[name]), len(LABEL_COLS)):
            raise ValueError(f"Invalid {name} text/target shape.")
        if not np.isin(y, (0, 1)).all():
            raise ValueError(f"{name} labels must contain only 0/1.")
        return TextSplit(texts=texts[name], y=y)

    return TrainValData(train=make_split("train"), val=make_split("val"))


def vectorizer_configurations() -> list[dict[str, Any]]:
    """Return a deterministic one-factor-at-a-time TF-IDF screening design."""
    configs: list[dict[str, Any]] = []

    def add(**changes: Any) -> None:
        config = {**BASE_VECTORIZER_CONFIG, **changes}
        if config not in configs:
            configs.append(config)

    for value in (2, 3, 5, 10):
        add(min_df=value)
    for value in (0.90, 0.95, 1.0):
        add(max_df=value)
    for value in ((1, 1), (1, 2)):
        add(ngram_range=value)
    for value in (3000, 5000, 8000, None):
        add(max_features=value)
    for value in (True, False):
        add(sublinear_tf=value)
    return configs


def build_vectorizer(config: dict[str, Any]) -> TfidfVectorizer:
    """Build an unfitted vectorizer with the project's fixed preprocessing."""
    return TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        min_df=config["min_df"],
        max_df=config["max_df"],
        ngram_range=config["ngram_range"],
        max_features=config["max_features"],
        sublinear_tf=config["sublinear_tf"],
    )


def _validate_calibration_support(y_train: np.ndarray) -> None:
    for index, label in enumerate(LABEL_COLS):
        positives = int(y_train[:, index].sum())
        negatives = int(y_train.shape[0] - positives)
        if min(positives, negatives) < CALIBRATION_FOLDS:
            raise ValueError(
                f"{label} cannot support {CALIBRATION_FOLDS}-fold calibration: "
                f"{positives} positives, {negatives} negatives."
            )


def build_model(
    model_name: str,
    *,
    C: float,
    class_weight: str | None,
) -> OneVsRestClassifier:
    """Build one calibrated SVC or comparable logistic baseline."""
    if C <= 0:
        raise ValueError("C must be greater than zero.")
    if model_name == "linear_svc":
        calibration_cv = StratifiedKFold(
            n_splits=CALIBRATION_FOLDS,
            shuffle=True,
            random_state=RANDOM_STATE,
        )
        estimator = CalibratedClassifierCV(
            estimator=LinearSVC(
                C=C,
                class_weight=class_weight,
                random_state=RANDOM_STATE,
            ),
            method="sigmoid",
            cv=calibration_cv,
        )
    elif model_name == "logistic_regression":
        estimator = LogisticRegression(
            C=C,
            class_weight=class_weight,
            max_iter=2000,
            random_state=RANDOM_STATE,
            solver="liblinear",
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")
    return OneVsRestClassifier(estimator)


def _scores(y_true: np.ndarray, predictions: np.ndarray) -> tuple[float, float]:
    return (
        float(f1_score(y_true, predictions, average="macro", zero_division=0)),
        float(f1_score(y_true, predictions, average="micro", zero_division=0)),
    )


def fit_candidate(
    data: TrainValData,
    *,
    stage: str,
    model_name: str,
    C: float,
    class_weight: str | None,
    vectorizer_config: dict[str, Any],
) -> Candidate:
    """Fit and measure one complete TF-IDF/model configuration."""
    started = perf_counter()
    vectorizer = build_vectorizer(vectorizer_config)
    X_train = vectorizer.fit_transform(data.train.texts)
    X_val = vectorizer.transform(data.val.texts)

    if model_name == "linear_svc":
        _validate_calibration_support(data.train.y)
    model = build_model(model_name, C=C, class_weight=class_weight)
    model.fit(X_train, data.train.y)

    train_predictions = model.predict(X_train).astype(np.int8)
    val_predictions = model.predict(X_val).astype(np.int8)
    train_macro, train_micro = _scores(data.train.y, train_predictions)
    val_macro, val_micro = _scores(data.val.y, val_predictions)

    return Candidate(
        stage=stage,
        model_name=model_name,
        C=C,
        class_weight=class_weight,
        vectorizer_config=dict(vectorizer_config),
        n_features=X_train.shape[1],
        train_macro_f1=train_macro,
        val_macro_f1=val_macro,
        train_micro_f1=train_micro,
        val_micro_f1=val_micro,
        gap=train_macro - val_macro,
        elapsed_seconds=perf_counter() - started,
        model=model,
        vectorizer=vectorizer,
    )


def _candidate_key(candidate: Candidate) -> tuple[float, float]:
    """Validation decides; lower absolute gap breaks exact metric ties."""
    return candidate.val_macro_f1, -abs(candidate.gap)


def run_search(data: TrainValData) -> list[Candidate]:
    """Run TF-IDF screening, then a C sweep for each model/weight family."""
    results: list[Candidate] = []
    screening_configs = vectorizer_configurations()

    # Stage 1 covers every requested TF-IDF value with a fixed, regularised C.
    for config in screening_configs:
        for model_name in MODEL_NAMES:
            for class_weight in CLASS_WEIGHTS:
                results.append(
                    fit_candidate(
                        data,
                        stage="tfidf_screen",
                        model_name=model_name,
                        C=SCREENING_C,
                        class_weight=class_weight,
                        vectorizer_config=config,
                    )
                )

    # Select the most promising vectorizer separately for each model/weight
    # family, preferring valid candidates when at least one exists.
    for model_name in MODEL_NAMES:
        for class_weight in CLASS_WEIGHTS:
            family = [
                result
                for result in results
                if result.model_name == model_name
                and result.class_weight == class_weight
                and result.stage == "tfidf_screen"
            ]
            valid_family = [result for result in family if result.valid]
            pool = valid_family or family
            best_vectorizer = max(pool, key=_candidate_key).vectorizer_config
            for C in C_VALUES:
                # C=SCREENING_C with this exact vectorizer already exists.
                duplicate = any(
                    result.stage == "tfidf_screen"
                    and result.model_name == model_name
                    and result.class_weight == class_weight
                    and result.C == C
                    and result.vectorizer_config == best_vectorizer
                    for result in results
                )
                if duplicate:
                    continue
                results.append(
                    fit_candidate(
                        data,
                        stage="c_sweep",
                        model_name=model_name,
                        C=C,
                        class_weight=class_weight,
                        vectorizer_config=best_vectorizer,
                    )
                )
    return results


def select_best_valid(results: Iterable[Candidate]) -> Candidate | None:
    """Return the highest-validation candidate satisfying the official gap."""
    valid = [result for result in results if result.valid]
    return max(valid, key=_candidate_key) if valid else None


def _format_ngram(value: tuple[int, int]) -> str:
    return f"{value[0]}-{value[1]}"


def print_comparison_table(results: list[Candidate]) -> None:
    """Print all configurations and required measurements."""
    header = (
        f"{'#':>3} {'stage':<12} {'model':<19} {'weight':<8} {'C':>7} "
        f"{'min':>3} {'max':>4} {'ngram':>5} {'features cap':>12} {'sub':>4} "
        f"{'nfeat':>6} {'tr macro':>8} {'va macro':>8} "
        f"{'tr micro':>8} {'va micro':>8} {'gap':>7} {'sec':>7} {'valid':>5}"
    )
    print("\n" + header)
    print("-" * len(header))
    for index, result in enumerate(results, start=1):
        config = result.vectorizer_config
        cap = "None" if config["max_features"] is None else config["max_features"]
        weight = "None" if result.class_weight is None else "balanced"
        print(
            f"{index:>3} {result.stage:<12} {result.model_name:<19} "
            f"{weight:<8} {result.C:>7.4f} {config['min_df']:>3} "
            f"{config['max_df']:>4.2f} {_format_ngram(config['ngram_range']):>5} "
            f"{str(cap):>12} {str(config['sublinear_tf']):>4} "
            f"{result.n_features:>6} {result.train_macro_f1:>8.4f} "
            f"{result.val_macro_f1:>8.4f} {result.train_micro_f1:>8.4f} "
            f"{result.val_micro_f1:>8.4f} {result.gap:>7.4f} "
            f"{result.elapsed_seconds:>7.2f} {str(result.valid):>5}"
        )


def save_definitive(candidate: Candidate, output_path: Path) -> Path:
    """Atomically replace the definitive model, but only for a valid candidate."""
    if not candidate.valid:
        raise ValueError(
            f"Refusing to save model with gap {candidate.gap:.4f} > "
            f"{MAX_ALLOWED_GAP:.2f}."
        )
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    payload = {
        "model": candidate.model,
        "vectorizer": candidate.vectorizer,
        "model_name": candidate.model_name,
        "model_version": MODEL_VERSION,
        "label_cols": list(LABEL_COLS),
        "thresholds": np.full(len(LABEL_COLS), DEFAULT_THRESHOLD),
        "C": candidate.C,
        "class_weight": candidate.class_weight,
        "vectorizer_config": candidate.vectorizer_config,
        "n_features": candidate.n_features,
        "train_macro_f1": candidate.train_macro_f1,
        "validation_macro_f1": candidate.val_macro_f1,
        "train_micro_f1": candidate.train_micro_f1,
        "validation_micro_f1": candidate.val_micro_f1,
        "gap": candidate.gap,
        "random_state": RANDOM_STATE,
        "calibration_method": (
            "sigmoid" if candidate.model_name == "linear_svc" else None
        ),
    }
    joblib.dump(payload, temporary_path)
    temporary_path.replace(output_path)
    return output_path


def load_model(model_path: Path = DEFAULT_MODEL_PATH) -> dict[str, Any]:
    """Load a definitive model bundle produced by this experiment."""
    payload = joblib.load(_require_file(Path(model_path).resolve()))
    required = {"model", "vectorizer", "label_cols", "thresholds"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise TypeError("Invalid model bundle.")
    if payload["label_cols"] != list(LABEL_COLS):
        raise ValueError("The saved label order is incompatible with this project.")
    return payload


def predict_texts(
    texts: list[str],
    *,
    model_path: Path = DEFAULT_MODEL_PATH,
) -> dict[str, np.ndarray]:
    """Predict probabilities and binary labels for new non-empty fragments."""
    if not texts or any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("texts must be a non-empty list of non-empty strings.")
    payload = load_model(model_path)
    X = payload["vectorizer"].transform(texts)
    probabilities = np.asarray(payload["model"].predict_proba(X), dtype=float)
    thresholds = np.asarray(payload["thresholds"], dtype=float)
    predictions = (probabilities >= thresholds).astype(np.int8)
    return {"probabilities": probabilities, "predictions": predictions}


def print_best_report(candidate: Candidate, data: TrainValData) -> None:
    """Print the winning validation report without retaining test data."""
    X_val = candidate.vectorizer.transform(data.val.texts)
    predictions = candidate.model.predict(X_val)
    y_val = data.val.y
    print("\nBEST VALID CONFIGURATION")
    print(f"model: {candidate.model_name}")
    print(f"C: {candidate.C}")
    print(f"class_weight: {candidate.class_weight}")
    print(f"vectorizer: {candidate.vectorizer_config}")
    print(f"features: {candidate.n_features}")
    print(f"train macro-F1: {candidate.train_macro_f1:.4f}")
    print(f"validation macro-F1: {candidate.val_macro_f1:.4f}")
    print(f"train micro-F1: {candidate.train_micro_f1:.4f}")
    print(f"validation micro-F1: {candidate.val_micro_f1:.4f}")
    print(f"gap: {candidate.gap:.4f}")
    print("\nValidation report by label:")
    print(
        classification_report(
            y_val,
            predictions,
            target_names=LABEL_COLS,
            zero_division=0,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tune TF-IDF + LinearSVC/LogReg using train and validation only."
    )
    parser.add_argument("--training-table", type=Path, default=TRAINING_TABLE)
    parser.add_argument("--split-assignment", type=Path, default=SPLIT_ASSIGNMENT)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_train_val(args.training_table, args.split_assignment)
    results = run_search(data)
    print_comparison_table(results)
    best = select_best_valid(results)
    if best is None:
        print(
            "\nNO VALID CONFIGURATION: no model met gap <= 0.05. "
            "The existing definitive Joblib was not modified."
        )
        return
    print_best_report(best, data)
    saved = save_definitive(best, args.model_output)
    print(f"\ndefinitive model saved to: {saved}")


if __name__ == "__main__":
    main()
