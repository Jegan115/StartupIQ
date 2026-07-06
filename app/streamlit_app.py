import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover - fallback when plotly is unavailable
    go = None

from ml.predict import predict_outcome
from ml.recommendations import generate_recommendations
from ml.explain_prediction import create_shap_explanation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="StartupIQ Founder Decision Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
:root {
    --bg: #07111f;
    --panel: rgba(10, 20, 35, 0.95);
    --panel-2: rgba(16, 30, 50, 0.95);
    --text: #f4f7fb;
    --muted: #9fb0c9;
    --accent: #5eead4;
    --accent-2: #8b5cf6;
    --danger: #fb7185;
    --warning: #fbbf24;
    --success: #34d399;
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #07111f 0%, #0f172a 100%);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(7, 17, 31, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

.stTextInput > div > div > input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,0.04);
    color: var(--text);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
}

div[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.stButton > button {
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    color: white;
    border: none;
    border-radius: 999px;
    padding: 0.6rem 1.1rem;
    font-weight: 700;
}

.stButton > button:hover {
    filter: brightness(1.05);
    box-shadow: 0 10px 25px rgba(94,234,212,0.3);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: white;
    letter-spacing: -0.02em;
}

.kpi-card {
    background: linear-gradient(135deg, rgba(14, 24, 40, 0.95) 0%, rgba(28, 44, 70, 0.95) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.25);
}

.glass-panel {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 18px;
    backdrop-filter: blur(18px);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Field definitions: (key, widget_type, default_value)
# Keeping this in one place keeps widget keys, defaults, and payload fields in sync.
FIELDS = [
    ("industry", "text_input", "Fintech"),
    ("country", "text_input", "United States"),
    ("funding", "number_input", 5000000.0),
    ("revenue", "number_input", 1200000.0),
    ("burn_rate", "number_input", 250000.0),
    ("employees", "number_input", 25),
    ("market_size_billion", "number_input", 10.5),
    ("funding_rounds", "number_input", 3),
    ("capital_efficiency", "number_input", 0.24),
    ("runway_months", "number_input", 18.0),
    ("revenue_per_employee", "number_input", 48000.0),
    ("burn_multiple", "number_input", 1.8),
]

FIELD_LABELS = {
    "industry": "Industry",
    "country": "Country",
    "funding": "Funding",
    "revenue": "Revenue",
    "burn_rate": "Burn Rate",
    "employees": "Employees",
    "market_size_billion": "Market Size",
    "funding_rounds": "Funding Rounds",
    "capital_efficiency": "Capital Efficiency",
    "runway_months": "Runway Months",
    "revenue_per_employee": "Revenue / Employee",
    "burn_multiple": "Burn Multiple",
}

FIELD_STEP = {
    "funding": 100000.0,
    "revenue": 100000.0,
    "burn_rate": 10000.0,
    "employees": 1,
    "market_size_billion": 0.1,
    "funding_rounds": 1,
    "capital_efficiency": 0.01,
    "runway_months": 1.0,
    "revenue_per_employee": 1000.0,
    "burn_multiple": 0.1,
}

FIELD_MIN = {
    "funding": 0.0,
    "revenue": 0.0,
    "burn_rate": 0.0,
    "employees": 1,
    "market_size_billion": 0.0,
    "funding_rounds": 0,
    "capital_efficiency": 0.0,
    "runway_months": 0.0,
    "revenue_per_employee": 0.0,
    "burn_multiple": 0.0,
}


@st.cache_data(show_spinner=False)
def get_sample_payloads() -> List[Dict[str, Any]]:
    return [
        {
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
        },
        {
            "industry": "Health",
            "country": "Canada",
            "funding": 1800000,
            "revenue": 400000,
            "burn_rate": 380000,
            "employees": 34,
            "market_size_billion": 6.2,
            "funding_rounds": 2,
            "capital_efficiency": 0.08,
            "runway_months": 9,
            "revenue_per_employee": 12000,
            "burn_multiple": 2.8,
        },
    ]


def render_header() -> None:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("## 🚀 StartupIQ Founder Decision Simulator")
        st.markdown("Premium decision intelligence for founders, investors, and operators.")
    with col_b:
        st.markdown(
            "<div class='kpi-card'>"
            "<div style='font-size: 1.2rem; font-weight: 700;'>Executive Mode</div>"
            "<div style='color: #9fb0c9; margin-top: 6px;'>AI-led outcome forecasting with strategic guidance</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def render_sidebar() -> Dict[str, Any]:
    logo_path = BASE_DIR / "images" / "startupiq_logo.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        st.sidebar.markdown("### 🧠 StartupIQ")

    st.sidebar.markdown("### Founder Inputs")

    # Seed session_state with defaults exactly once, so widgets always have
    # a value to bind to via their `key=`.
    for field_name, _, default in FIELDS:
        st.session_state.setdefault(field_name, default)

    # Apply any pending "Load Sample" values now, BEFORE the widgets below
    # are instantiated. Writing to a widget's session_state key is only
    # allowed before that widget exists in the current run.
    if st.session_state.get("_pending_sample"):
        sample = get_sample_payloads()[0]
        for field_name, _, _ in FIELDS:
            st.session_state[field_name] = sample[field_name]
        st.session_state["_pending_sample"] = False

    payload: Dict[str, Any] = {}
    for field_name, widget_type, _ in FIELDS:
        label = FIELD_LABELS[field_name]
        if widget_type == "text_input":
            payload[field_name] = st.sidebar.text_input(label, key=field_name)
        else:
            payload[field_name] = st.sidebar.number_input(
                label,
                min_value=FIELD_MIN[field_name],
                step=FIELD_STEP[field_name],
                key=field_name,
            )

    st.sidebar.markdown("---")

    if st.sidebar.button("Predict", use_container_width=True, type="primary"):
        st.session_state["predict_clicked"] = True

    if st.sidebar.button("Load Sample", use_container_width=True):
        st.session_state["_pending_sample"] = True
        st.session_state["predict_clicked"] = True
        st.rerun()

    return payload


def build_confidence_gauge(confidence: float) -> Any:
    if go is None:
        return None

    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=confidence,
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "white"},
                "bar": {"color": "#5eead4"},
                "steps": [
                    {"range": [0, 50], "color": "rgba(251, 113, 133, 0.25)"},
                    {"range": [50, 80], "color": "rgba(251, 191, 36, 0.25)"},
                    {"range": [80, 100], "color": "rgba(52, 211, 153, 0.25)"},
                ],
            },
        )
    )
    figure.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def render_results(payload: Dict[str, Any]) -> None:
    current_payload_key = tuple(sorted((str(key), payload.get(key)) for key in payload))
    if st.session_state.get("last_payload_key") != current_payload_key:
        with st.spinner("Running premium decision analysis..."):
            prediction = predict_outcome(payload)
            explanation = create_shap_explanation(payload)
            recommendations = generate_recommendations(payload, prediction["predicted_outcome"])

        st.session_state["last_payload_key"] = current_payload_key
        st.session_state["last_prediction"] = prediction
        st.session_state["last_explanation"] = explanation
        st.session_state["last_recommendations"] = recommendations
        st.session_state["history"] = st.session_state.get("history", [])
        st.session_state["history"].append(
            {
                "payload": payload,
                "prediction": prediction,
                "recommendations": recommendations,
            }
        )
        st.session_state["history"] = st.session_state["history"][-8:]
    else:
        prediction = st.session_state.get("last_prediction", {})
        explanation = st.session_state.get("last_explanation", {})
        recommendations = st.session_state.get("last_recommendations", [])

    outcome = prediction.get("predicted_outcome", "Pending")
    confidence = float(prediction.get("confidence_score", 0.0))
    risk = prediction.get("risk_level", "Unknown")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='kpi-card'><div style='font-size:0.95rem;color:#9fb0c9;'>Predicted Outcome</div><div style='font-size:1.5rem;font-weight:700;margin-top:6px;'>{outcome}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div style='font-size:0.95rem;color:#9fb0c9;'>Confidence</div><div style='font-size:1.5rem;font-weight:700;margin-top:6px;'>{confidence:.2f}%</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><div style='font-size:0.95rem;color:#9fb0c9;'>Risk Level</div><div style='font-size:1.5rem;font-weight:700;margin-top:6px;'>{risk}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='kpi-card'><div style='font-size:0.95rem;color:#9fb0c9;'>Recommendations</div><div style='font-size:1.5rem;font-weight:700;margin-top:6px;'>{len(recommendations)}</div></div>", unsafe_allow_html=True)

    st.markdown("### Prediction")
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("#### 🔎 Confidence Gauge")
    gauge_fig = build_confidence_gauge(confidence)
    if gauge_fig is not None:
        st.plotly_chart(gauge_fig, use_container_width=True)
    else:
        st.progress(min(confidence / 100.0, 1.0))
        st.caption(f"Model confidence: {confidence:.2f}%")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("#### 📊 Probability Chart")
    probability_df = pd.DataFrame(
        [
            {"Class": class_name, "Probability": probability}
            for class_name, probability in prediction.get("probability_by_class", {}).items()
        ]
    )
    if not probability_df.empty:
        st.bar_chart(probability_df.set_index("Class")["Probability"])
    st.markdown("</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 0.8])
    with col_left:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("#### 🎯 SHAP Explanation")
        if explanation.get("summary_plot_path") and Path(explanation["summary_plot_path"]).exists():
            st.image(explanation["summary_plot_path"], use_container_width=True)
        else:
            st.markdown(explanation.get("explanation_text", "No explanation available."))
        if explanation.get("top_positive_features"):
            st.markdown("**Top positive drivers**")
            for item in explanation["top_positive_features"]:
                st.markdown(f"- {item['feature']}: {item['value']}")
        if explanation.get("top_negative_features"):
            st.markdown("**Top negative drivers**")
            for item in explanation["top_negative_features"]:
                st.markdown(f"- {item['feature']}: {item['value']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("#### 🧭 Founder Recommendations")
        for recommendation in recommendations:
            st.markdown(f"- **{recommendation['priority']}** {recommendation['title']} — {recommendation['message']}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Prediction History")
    if st.session_state.get("history"):
        history_df = pd.DataFrame(
            [
                {
                    "Outcome": entry["prediction"]["predicted_outcome"],
                    "Confidence": entry["prediction"]["confidence_score"],
                    "Risk": entry["prediction"]["risk_level"],
                    "Industry": entry["payload"].get("industry", ""),
                }
                for entry in st.session_state["history"]
            ]
        )
        st.dataframe(history_df, use_container_width=True)

    st.download_button(
        label="⬇️ Download Prediction CSV",
        data=pd.DataFrame([payload]).to_csv(index=False),
        file_name="prediction_snapshot.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    if "predict_clicked" not in st.session_state:
        st.session_state["predict_clicked"] = False
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "last_payload_key" not in st.session_state:
        st.session_state["last_payload_key"] = None

    render_header()
    payload = render_sidebar()

    if st.session_state.get("predict_clicked"):
        render_results(payload)
    else:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("### ✨ Ready for premium analysis")
        st.markdown("Enter startup characteristics in the sidebar or load a sample profile to receive an executive-grade forecast.")
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
