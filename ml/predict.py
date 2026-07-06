"""Reusable prediction helpers for the startup outcome model."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "saved_models" / "startup_predictor.pkl"

FEATURE_ALIASES = {
    "sector": ["sector", "industry"],
    "revenue_usd": ["revenue_usd", "revenue"],
    "burn_rate_usd": ["burn_rate_usd", "burn_rate"],
    "team_size": ["team_size", "employees"],
    "capital_efficiency_ratio": ["capital_efficiency_ratio", "capital_efficiency"],
    "burn_ratio": ["burn_ratio", "burn_multiple"],
    "market_size_billion": ["market_size_billion", "market_size"],
    "funding_rounds": ["funding_rounds"],
    "founder_experience_years": ["founder_experience_years"],
    "product_traction_users": ["product_traction_users"],
    "investor_type": ["investor_type"],
    "founder_background": ["founder_background"],
    "revenue_per_employee": ["revenue_per_employee"],
    "user_traction_per_employee": ["user_traction_per_employee"],
}

CATEGORICAL_FEATURES = {"sector", "investor_type", "founder_background"}


def load_model_bundle(path: Path = MODEL_PATH) -> Dict[str, Any]:
    """Load the persisted model bundle from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Model bundle not found at {path}")
    return joblib.load(path)


def build_feature_frame(payload: Dict[str, Any], feature_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Convert a prediction payload into a feature dataframe for the trained model."""
    if feature_columns is None:
        bundle = load_model_bundle()
        feature_columns = bundle["feature_columns"]

    normalized_payload: Dict[str, Any] = {}
    for feature_name in feature_columns:
        candidate = payload.get(feature_name)
        if candidate is None or candidate == "":
            for alias in FEATURE_ALIASES.get(feature_name, [feature_name]):
                if alias in payload and payload[alias] not in (None, ""):
                    candidate = payload[alias]
                    break
        if candidate is None or candidate == "":
            candidate = "" if feature_name in CATEGORICAL_FEATURES else 0
        normalized_payload[feature_name] = candidate

    return pd.DataFrame([normalized_payload])[feature_columns]


def predict_outcome(payload: Dict[str, Any], bundle: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Predict startup outcome and return probabilities and confidence metrics."""
    if bundle is None:
        bundle = load_model_bundle()

    feature_columns = bundle["feature_columns"]
    X_new = build_feature_frame(payload, feature_columns=feature_columns)
    pipeline = bundle["model"]
    prediction_encoded = pipeline.predict(X_new)[0]
    probabilities = pipeline.predict_proba(X_new)[0]

    label_encoder = bundle["label_encoder"]

    # Decode prediction back to text
    prediction = label_encoder.inverse_transform([prediction_encoded])[0]

    classes = label_encoder.classes_

    probability_map = {
        class_name: float(prob)
        for class_name, prob in zip(classes, probabilities)
    }

    top_class = max(probability_map, key=probability_map.get)
    top_probability = probability_map[top_class]

    confidence_score = float(round(top_probability * 100, 2))
    risk_level = "Low"
    if confidence_score < 70:
        risk_level = "High"
    elif confidence_score < 85:
        risk_level = "Medium"
    return {
        "predicted_outcome": prediction,
        "probability_by_class": probability_map,
        "top_probability": top_probability,
        "confidence_score": confidence_score,
        "risk_level": risk_level,
        "model_name": bundle.get("model_name", "unknown"),
    }


def predict_from_inputs(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience wrapper for single-record predictions."""
    return predict_outcome(payload)


def main() -> None:
    """Run a demo prediction using a sample payload."""
    sample_payload = {
        "sector": "Fintech",
        "founder_experience_years": 8,
        "team_size": 25,
        "market_size_billion": 10.5,
        "product_traction_users": 250000,
        "investor_type": "tier2_vc",
        "founder_background": "academic",
        "revenue_usd": 1200000,
        "burn_rate_usd": 250000,
        "burn_ratio": 1.8,
        "revenue_per_employee": 48000,
        "user_traction_per_employee": 10000,
        "capital_efficiency_ratio": 0.24,
        "funding_rounds": 3,
    }
    logger.info(predict_outcome(sample_payload))


if __name__ == "__main__":
    main()
