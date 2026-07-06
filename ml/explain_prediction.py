"""Generate SHAP-based explanations for startup outcome predictions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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


def create_shap_explanation(payload: Dict[str, Any], bundle: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create SHAP-based insight for a single prediction payload."""
    if bundle is None:
        bundle = load_model_bundle()

    try:
        import shap
    except ImportError as exc:
        logger.warning("shap is not installed; returning a fallback explanation figure. %s", exc)
        return create_fallback_explanation(payload, bundle)

    from ml.predict import build_feature_frame

    X = build_feature_frame(payload, feature_columns=bundle["feature_columns"])
    pipeline = bundle["model"]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = REPORTS_DIR / "shap_summary_plot.png"
    waterfall_path = REPORTS_DIR / "shap_waterfall_plot.png"

    try:
        model = pipeline.named_steps["model"] if hasattr(pipeline, "named_steps") and "model" in pipeline.named_steps else pipeline
        explainer = shap.Explainer(model, X)
        shap_values = explainer(X)

        try:
            shap.summary_plot(shap_values, X, show=False)
            plt.savefig(summary_path, dpi=300, bbox_inches="tight")
            plt.close()
        except Exception as exc:
            logger.warning("Could not generate SHAP summary plot: %s", exc)
            summary_path = None

        try:
            shap.plots.waterfall(shap_values[0], show=False)
            plt.savefig(waterfall_path, dpi=300, bbox_inches="tight")
            plt.close()
        except Exception as exc:
            logger.warning("Could not generate SHAP waterfall plot: %s", exc)
            waterfall_path = None

        if hasattr(shap_values, "values"):
            values = shap_values.values
        else:
            values = getattr(shap_values, "values", None)

        if values is None:
            return create_fallback_explanation(payload, bundle)

        if isinstance(values, list):
            values = values[0]

        if isinstance(values, np.ndarray):
            values = values.reshape(-1)

        feature_names = list(X.columns)
        feature_contributions = list(zip(feature_names, values))
        sorted_contributions = sorted(feature_contributions, key=lambda item: abs(item[1]), reverse=True)

        top_positive = [
            {"feature": name, "value": round(float(score), 3)}
            for name, score in sorted_contributions[:3]
            if score > 0
        ]
        top_negative = [
            {"feature": name, "value": round(float(score), 3)}
            for name, score in sorted_contributions[:3]
            if score < 0
        ]

        explanation_text = (
            "The prediction is driven by the strongest positive and negative feature contributions. "
            "Positive values support the predicted outcome, while negative values push against it."
        )

        return {
            "summary_plot_path": str(summary_path) if summary_path else None,
            "waterfall_plot_path": str(waterfall_path) if waterfall_path else None,
            "top_positive_features": top_positive,
            "top_negative_features": top_negative,
            "explanation_text": explanation_text,
        }
    except Exception as exc:
        logger.warning("SHAP explanation generation failed; using fallback figure. %s", exc)
        return create_fallback_explanation(payload, bundle)


def create_fallback_explanation(payload: Dict[str, Any], bundle: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a small matplotlib feature-importance figure when SHAP is unavailable or incompatible."""
    if bundle is None:
        bundle = load_model_bundle()

    from ml.predict import build_feature_frame

    X = build_feature_frame(payload, feature_columns=bundle["feature_columns"])
    pipeline = bundle["model"]
    model = pipeline.named_steps["model"] if hasattr(pipeline, "named_steps") and "model" in pipeline.named_steps else pipeline

    feature_names = list(X.columns)
    if hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_, dtype=float)
    else:
        values = np.zeros(len(feature_names), dtype=float)

    if len(values) != len(feature_names):
        count = min(len(feature_names), len(values))
        feature_names = feature_names[:count]
        values = values[:count]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    fallback_path = REPORTS_DIR / "fallback_feature_importance.png"

    plt.figure(figsize=(8, 4))
    plt.barh(feature_names, values)
    plt.title("Feature importance proxy")
    plt.xlabel("Relative importance")
    plt.tight_layout()
    plt.savefig(fallback_path, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "summary_plot_path": str(fallback_path),
        "waterfall_plot_path": None,
        "top_positive_features": [],
        "top_negative_features": [],
        "explanation_text": "The SHAP explanation could not be generated, so a feature-importance fallback view was produced instead.",
    }


def main() -> None:
    """Run a demo explanation generation with a sample payload."""
    sample_payload = {
        "industry": "Fintech",
        "country": "United States",
        "funding": 5000000,
        "revenue": 1200000,
        "burn_rate": 250000,
        "employees": 25,
        "market_size_billion": 10.5,
        "funding_rounds": 3,
        "capital_efficiency": 0.24,
        "runway_months": 18,
        "revenue_per_employee": 48000,
        "burn_multiple": 1.8,
    }
    logger.info(create_shap_explanation(sample_payload))


if __name__ == "__main__":
    main()
