"""Evaluate the trained startup outcome classifier and save diagnostic artifacts."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    auc,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize

from ml.train_model import TARGET_COLUMN, resolve_dataset_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "saved_models" / "startup_predictor.pkl"
REPORTS_DIR = BASE_DIR / "reports" / "model_evaluation"


def load_model_bundle(path: Path = MODEL_PATH) -> Dict[str, Any]:
    """Load the persisted model bundle from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Model bundle not found at {path}")
    return joblib.load(path)


def load_evaluation_frame(bundle: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Load and split the dataset into train/test frames using the same strategy as training."""
    dataset_path = resolve_dataset_path()
    df = pd.read_csv(dataset_path)

    feature_columns = bundle["feature_columns"]
    available_features = [column for column in feature_columns if column in df.columns]
    if not available_features:
        raise ValueError("No compatible features were found in the dataset for evaluation.")

    X = df[available_features]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test


def get_feature_importance(pipeline: Any) -> List[Tuple[str, float]]:
    """Extract feature importance values for the trained pipeline."""
    model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]
    feature_names = preprocessor.get_feature_names_out()

    if hasattr(model, "feature_importances_"):
        importance_values = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        coef = np.asarray(model.coef_, dtype=float)
        if coef.ndim == 1:
            importance_values = np.abs(coef)
        else:
            importance_values = np.mean(np.abs(coef), axis=0)
    else:
        logger.warning("The selected model does not expose feature importance scores.")
        return []

    if len(importance_values) != len(feature_names):
        if len(importance_values) > len(feature_names):
            importance_values = importance_values[: len(feature_names)]
        else:
            importance_values = np.pad(importance_values, (0, len(feature_names) - len(importance_values)), constant_values=0.0)

    ranked_features = sorted(zip(feature_names, importance_values), key=lambda item: item[1], reverse=True)
    return ranked_features


def save_classification_report(report: Dict[str, Any], labels: List[str]) -> None:
    """Persist the classification report as a CSV file."""
    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(REPORTS_DIR / "classification_report.csv")

    report_path = REPORTS_DIR / "classification_report.txt"
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write(pd.DataFrame(report).transpose().to_string())


def save_confusion_matrix(y_true: pd.Series, y_pred: pd.Series, labels: List[str]) -> None:
    """Save the confusion matrix and its visualization."""
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_df.to_csv(REPORTS_DIR / "confusion_matrix.csv")

    fig, ax = plt.subplots(figsize=(8, 6))
    ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels).plot(ax=ax, cmap="Blues")
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "confusion_matrix.png", dpi=300)
    plt.close(fig)


def save_feature_importance(importance: List[Tuple[str, float]]) -> None:
    """Save a feature importance chart and table."""
    if not importance:
        logger.info("No feature importance values were available for plotting.")
        return

    importance_df = pd.DataFrame(importance, columns=["feature", "importance"])
    importance_df.head(15).to_csv(REPORTS_DIR / "feature_importance.csv", index=False)

    top_features = importance_df.head(15).copy()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_features["feature"].astype(str).tolist(), top_features["importance"].tolist())
    ax.invert_yaxis()
    ax.set_title("Top Feature Importances")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "feature_importance.png", dpi=300)
    plt.close(fig)


def save_roc_curve(pipeline: Any, X_test: pd.DataFrame, y_test: pd.Series, labels: List[str]) -> None:
    """Save a one-vs-rest ROC curve plot when probability predictions are available."""
    if not hasattr(pipeline, "predict_proba"):
        logger.info("The selected model does not expose predict_proba; skipping ROC curve generation.")
        return

    probabilities = pipeline.predict_proba(X_test)
    if probabilities.shape[1] != len(labels):
        logger.info("Probability output shape does not match the expected class list; skipping ROC curve generation.")
        return

    y_bin = label_binarize(y_test, classes=labels)
    fig, ax = plt.subplots(figsize=(8, 6))

    for index, class_name in enumerate(labels):
        fpr, tpr, _ = roc_curve(y_bin[:, index], probabilities[:, index])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, label=f"{class_name} (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Baseline")
    ax.set_title("ROC Curve (One-vs-Rest)")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "roc_curve.png", dpi=300)
    plt.close(fig)


def evaluate_model(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the saved model and write all requested artifacts to disk."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    X_train, X_test, y_train, y_test = load_evaluation_frame(bundle)
    pipeline = bundle["model"]

    predictions = pipeline.predict(X_test)
    labels = bundle.get("target_classes", sorted(pd.Series(y_test).unique().tolist()))

    report = classification_report(y_test, predictions, labels=labels, output_dict=True, zero_division=0)
    save_classification_report(report, labels)
    save_confusion_matrix(y_test, predictions, labels)
    save_feature_importance(get_feature_importance(pipeline))
    save_roc_curve(pipeline, X_test, y_test, labels)

    metrics = {
        "model_name": bundle.get("model_name", "unknown"),
        "accuracy": float((predictions == y_test).mean()),
        "precision": float(precision_score(y_test, predictions, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, predictions, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_test, predictions, average="weighted", zero_division=0)),
        "classification_report": report,
    }

    metrics_path = REPORTS_DIR / "evaluation_summary.csv"
    pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
    logger.info("Saved evaluation artifacts to %s", REPORTS_DIR)
    return metrics


def main() -> None:
    """Load the persisted model bundle and generate evaluation artifacts."""
    bundle = load_model_bundle()
    evaluate_model(bundle)


if __name__ == "__main__":
    main()
