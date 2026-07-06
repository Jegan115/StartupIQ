"""Train and persist a multiclass startup outcome prediction model."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.tree import DecisionTreeClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH_CANDIDATES = [
    BASE_DIR / "data" / "processed" / "cleaned_startups.csv",
    BASE_DIR / "data" / "cleaned" / "startup_cleaned.csv",
    BASE_DIR / "data" / "cleaned" / "cleaned_startups.csv",
]

MODEL_DIR = BASE_DIR / "saved_models"
REPORTS_DIR = BASE_DIR / "reports" / "model_evaluation"

MODEL_PATH = MODEL_DIR / "startup_predictor.pkl"
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"

TARGET_COLUMN = "outcome"


def resolve_dataset_path() -> Path:
    for path in DATA_PATH_CANDIDATES:
        if path.exists():
            logger.info("Using dataset at %s", path)
            return path

    raise FileNotFoundError(
        "Could not find cleaned dataset.\nChecked:\n"
        + "\n".join(str(p) for p in DATA_PATH_CANDIDATES)
    )


def get_available_feature_columns(df: pd.DataFrame) -> List[str]:
    feature_columns = [c for c in df.columns if c != TARGET_COLUMN]
    logger.info("Using %d features.", len(feature_columns))
    return feature_columns


def load_dataset(path: Optional[Path] = None) -> pd.DataFrame:
    dataset_path = path or resolve_dataset_path()
    df = pd.read_csv(dataset_path)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found.")

    feature_columns = get_available_feature_columns(df)

    if df[TARGET_COLUMN].isna().any():
        raise ValueError("Target column contains missing values.")

    if df[feature_columns].isna().any().any():
        raise ValueError("Feature columns contain missing values.")

    return df[feature_columns + [TARGET_COLUMN]].copy()


def build_pipeline(model: Any, feature_columns: List[str], X_train: pd.DataFrame) -> Pipeline:

    categorical_features = [
        c for c in feature_columns if pd.api.types.is_object_dtype(X_train[c])
    ]

    numeric_features = [
        c for c in feature_columns if c not in categorical_features
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "num",
                "passthrough",
                numeric_features,
            ),
        ]
    )

    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def build_models() -> Dict[str, Any]:

    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000),

        "Decision Tree": DecisionTreeClassifier(
            random_state=42
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        ),

        "Gradient Boosting": GradientBoostingClassifier(
            random_state=42
        ),
    }

    try:
        from xgboost import XGBClassifier

        models["XGBoost"] = XGBClassifier(
            objective="multi:softprob",
            num_class=None,
            n_estimators=200,
            learning_rate=0.1,
            max_depth=4,
            random_state=42,
            eval_metric="mlogloss",
            n_jobs=-1,
        )

    except ImportError:
        logger.warning("XGBoost not installed. Skipping.")

    return models


def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test,
):

    predictions = pipeline.predict(X_test)

    return {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions,
        ),
    }


def train_and_save_model():

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading dataset...")

    df = load_dataset()

    feature_columns = [
        c for c in df.columns if c != TARGET_COLUMN
    ]

    X = df[feature_columns]

    # -----------------------------
    # Encode target labels
    # -----------------------------
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[TARGET_COLUMN])

    logger.info("Target classes: %s", list(label_encoder.classes_))

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    trained_models = {}
    results = []

    logger.info("Training models...")

    for model_name, model in build_models().items():

        logger.info("Training %s...", model_name)

        pipeline = build_pipeline(
            model,
            feature_columns,
            X_train,
        )

        pipeline.fit(X_train, y_train)

        metrics = evaluate_model(
            pipeline,
            X_test,
            y_test,
        )

        trained_models[model_name] = pipeline

        results.append(
            {
                "Model": model_name,
                "Accuracy": metrics["accuracy"],
                "Precision": metrics["precision"],
                "Recall": metrics["recall"],
                "F1 Score": metrics["f1"],
            }
        )

    comparison_df = (
        pd.DataFrame(results)
        .sort_values("F1 Score", ascending=False)
        .reset_index(drop=True)
    )

    best_model_name = comparison_df.iloc[0]["Model"]

    best_pipeline = trained_models[best_model_name]

    logger.info("\n%s", comparison_df)

    logger.info("Best Model: %s", best_model_name)

    model_bundle = {
        "model": best_pipeline,
        "model_name": best_model_name,
        "feature_columns": feature_columns,
        "target_column": TARGET_COLUMN,
        "target_classes": label_encoder.classes_.tolist(),
        "label_encoder": label_encoder,
        "model_comparison": comparison_df,
    }

    joblib.dump(model_bundle, MODEL_PATH)

    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    comparison_df.to_csv(
        REPORTS_DIR / "model_comparison.csv",
        index=False,
    )

    logger.info("Saved model to %s", MODEL_PATH)
    logger.info("Saved label encoder to %s", LABEL_ENCODER_PATH)
    logger.info("Saved comparison table.")

    return model_bundle


if __name__ == "__main__":
    train_and_save_model()