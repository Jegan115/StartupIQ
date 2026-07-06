"""Generate business recommendations from startup prediction inputs."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_recommendations(payload: Dict[str, Any], predicted_outcome: Optional[str] = None) -> List[Dict[str, str]]:
    """Create rule-based recommendations from startup characteristics and predicted outcome."""
    recommendations: List[Dict[str, str]] = []

    burn_rate = float(payload.get("burn_rate", 0) or 0)
    capital_efficiency = float(payload.get("capital_efficiency", 0) or 0)
    runway_months = float(payload.get("runway_months", 0) or 0)
    burn_multiple = float(payload.get("burn_multiple", 0) or 0)
    funding = float(payload.get("funding", 0) or 0)
    revenue = float(payload.get("revenue", 0) or 0)
    employees = int(payload.get("employees", 0) or 0)
    funding_rounds = int(payload.get("funding_rounds", 0) or 0)

    if burn_rate > 250000:
        recommendations.append(
            {
                "priority": "High",
                "title": "Reduce operating burn",
                "message": "High burn rate suggests tighter expense controls and a review of non-essential spending.",
            }
        )

    if capital_efficiency < 0.1:
        recommendations.append(
            {
                "priority": "High",
                "title": "Improve monetization efficiency",
                "message": "Low capital efficiency indicates the business should improve pricing, conversion, or monetization strategy.",
            }
        )

    if runway_months < 12:
        recommendations.append(
            {
                "priority": "High",
                "title": "Extend runway",
                "message": "Low runway creates near-term liquidity risk; consider raising additional funding or cutting costs.",
            }
        )

    if burn_multiple > 2:
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Rebalance growth spending",
                "message": "A high burn multiple points to inefficient customer acquisition costs and should be optimized.",
            }
        )

    if funding < 1000000 and revenue < 500000:
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Strengthen financing readiness",
                "message": "The company may benefit from a clearer fundraising narrative and milestones that improve investor confidence.",
            }
        )

    if employees > 50 and funding_rounds < 2:
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Simplify organizational structure",
                "message": "A larger team without enough funding rounds may require leaner operating processes and tighter hiring discipline.",
            }
        )

    if predicted_outcome in {"Failure", "Failed"}:
        recommendations.append(
            {
                "priority": "High",
                "title": "Pivot the business model",
                "message": "The model signals elevated downside risk; revisit target segments, pricing, and product-market fit.",
            }
        )
    elif predicted_outcome in {"Acquisition", "IPO"}:
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Prepare for growth milestones",
                "message": "The current profile is favorable for strategic or public-market outcomes; focus on execution discipline and investor readiness.",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "priority": "Low",
                "title": "Maintain current trajectory",
                "message": "The startup profile is balanced; continue monitoring unit economics and cash discipline.",
            }
        )

    return recommendations


def main() -> None:
    """Run a demo recommendation generation using a sample payload."""
    sample_payload = {
        "burn_rate": 400000,
        "capital_efficiency": 0.06,
        "runway_months": 8,
        "burn_multiple": 3.5,
        "funding": 900000,
        "revenue": 300000,
        "employees": 60,
        "funding_rounds": 1,
    }
    logger.info(generate_recommendations(sample_payload, predicted_outcome="Failure"))


if __name__ == "__main__":
    main()
