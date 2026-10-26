import streamlit as st
from pathlib import Path
import pandas as pd
import re

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="HanuAI Insight Engine",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).parent

TASK1_REPORT = (
    BASE_DIR
    / "task1_voice_of_customer"
    / "reports"
    / "insights_DEMO.md"
)

TASK1_IMAGE = (
    BASE_DIR
    / "task1_voice_of_customer"
    / "reports"
    / "aspect_net_sentiment_DEMO.png"
)

TASK2_REPORT = (
    BASE_DIR
    / "task2_field_failure_intelligence"
    / "reports"
    / "auto_insights_SYNTHETIC_DEMO.md"
)

# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------
def read_file(path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def extract_number(text, pattern, default="N/A"):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else default


# ---------------------------------------------------------
# LOAD REPORTS
# ---------------------------------------------------------
task1_text = read_file(TASK1_REPORT)
task2_text = read_file(TASK2_REPORT)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("🤖 HanuAI Insight Engine")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Overview",
        "📊 Voice of Customer",
        "🔧 Field Failure Intelligence"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "AI-powered analytics platform for "
    "Customer Voice and Field Failure Intelligence."
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🤖 HanuAI Insight Engine")
st.caption(
    "AI-powered Customer Voice & Field Failure Intelligence"
)

# =========================================================
# OVERVIEW
# =========================================================
if page == "🏠 Overview":

    st.header("📌 Project Overview")

    st.write(
        """
        HanuAI Insight Engine analyzes customer feedback and field
        failure data to identify important patterns, trends,
        sentiment, components, and potential root causes.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Customer Reviews", "180")
    col2.metric("Failure Records", "1,202")
    col3.metric("Failure Clusters", "9")
    col4.metric("Data Sources", "2")

    st.markdown("---")

    st.subheader("🚀 Key Capabilities")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            ### 📊 Voice of Customer

            - Customer review analysis
            - Sentiment analysis
            - Aspect-level sentiment
            - Customer insights
            - Review trends
            """
        )

    with c2:
        st.markdown(
            """
            ### 🔧 Field Failure Intelligence

            - Failure categorization
            - Component analysis
            - Root-cause candidates
            - Failure trends
            - Downtime analysis
            - Repair-cost analysis
            """
        )

    st.markdown("---")

    st.subheader("📈 Project Status")

    st.success(
        "Task 1 and Task 2 pipelines have been successfully "
        "executed locally."
    )


# =========================================================
# TASK 1
# =========================================================
elif page == "📊 Voice of Customer":

    st.header("📊 Voice of Customer")

    st.write(
        "Customer review and sentiment intelligence generated "
        "from the Task 1 pipeline."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Reviews Analyzed", "180")
    col2.metric("Analysis", "Sentiment")
    col3.metric("Output", "Aspect Insights")

    st.markdown("---")

    if TASK1_IMAGE.exists():
        st.subheader("📈 Aspect-Level Sentiment")
        st.image(
            str(TASK1_IMAGE),
            use_container_width=True
        )
    else:
        st.warning("Task 1 sentiment image was not found.")

    st.markdown("---")

    st.subheader("💡 Customer Insights")

    if task1_text:
        st.markdown(task1_text)
    else:
        st.warning("Task 1 report was not found.")


# =========================================================
# TASK 2
# =========================================================
elif page == "🔧 Field Failure Intelligence":

    st.header("🔧 Field Failure Intelligence")

    st.write(
        "Analysis of field failures, issue categories, "
        "components, trends, downtime and repair costs."
    )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Raw Records", "1,230")
    col2.metric("Cleaned Records", "1,202")
    col3.metric("Clusters", "9")
    col4.metric("Silhouette Score", "0.25")

    st.markdown("---")

    # -----------------------------------------------------
    # TOP ISSUES
    # -----------------------------------------------------
    st.subheader("🔥 Top Issue Categories")

    issue_data = pd.DataFrame(
        {
            "Issue Category": [
                "Electrical / Short & Power",
                "Energy Storage (Battery)",
                "Mechanical Wear / Vibration",
                "Thermal / Overheating",
                "Leakage / Fluid System",
            ],
            "Count": [
                271,
                173,
                173,
                171,
                156,
            ],
        }
    )

    st.bar_chart(
        issue_data.set_index("Issue Category")
    )

    st.dataframe(
        issue_data,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # COMPONENTS
    # -----------------------------------------------------
    st.subheader("🔩 Top Components")

    component_data = pd.DataFrame(
        {
            "Component": [
                "battery pack",
                "control board",
                "motor",
                "sensor",
                "pump",
            ],
            "Count": [
                301,
                149,
                113,
                102,
                99,
            ],
        }
    )

    st.bar_chart(
        component_data.set_index("Component")
    )

    # -----------------------------------------------------
    # ROOT CAUSE
    # -----------------------------------------------------
    st.subheader("🔍 Strongest Root-Cause Candidates")

    root_data = pd.DataFrame(
        {
            "Driver": [
                "product_model",
                "product_model",
                "primary_condition",
                "primary_condition",
                "product_model",
                "primary_condition",
                "region",
                "primary_condition",
            ],
            "Driver Value": [
                "Rx-300",
                "Rx-300",
                "under full load",
                "after 3 months in service",
                "Rx-200",
                "after 3 months in service",
                "North",
                "after vibration on rough roads",
            ],
            "Outcome": [
                "Energy Storage (Battery)",
                "battery pack",
                "pump",
                "Uncategorised",
                "Corrosion / Environmental",
                "motor",
                "Display / UI",
                "bearing",
            ],
            "Lift": [
                1.92,
                1.86,
                1.63,
                1.62,
                1.55,
                1.53,
                1.51,
                1.49,
            ],
        }
    )

    st.dataframe(
        root_data,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # TREND
    # -----------------------------------------------------
    st.subheader("📈 Recent 3-Month Change")

    trend_data = pd.DataFrame(
        {
            "Issue Category": [
                "Leakage / Fluid System",
                "Uncategorised",
                "Electrical / Short & Power",
                "Thermal / Overheating",
                "Mechanical Wear / Vibration",
                "Display / UI",
                "Energy Storage (Battery)",
                "Sensor / Calibration",
                "Corrosion / Environmental",
            ],
            "Change %": [
                33.3,
                16.7,
                8.3,
                3.6,
                -4.0,
                -25.0,
                -30.8,
                -47.8,
                -50.0,
            ],
        }
    )

    st.bar_chart(
        trend_data.set_index("Issue Category")
    )

    st.dataframe(
        trend_data,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # DOWNTIME
    # -----------------------------------------------------
    st.subheader("⏱️ Average Downtime by Issue")

    downtime_data = pd.DataFrame(
        {
            "Issue Category": [
                "Energy Storage (Battery)",
                "Uncategorised",
                "Thermal / Overheating",
                "Electrical / Short & Power",
                "Sensor / Calibration",
                "Corrosion / Environmental",
                "Leakage / Fluid System",
                "Mechanical Wear / Vibration",
                "Display / UI",
            ],
            "Downtime Hours": [
                6.8,
                6.5,
                6.4,
                6.4,
                6.3,
                6.2,
                6.1,
                6.1,
                6.0,
            ],
        }
    )

    st.bar_chart(
        downtime_data.set_index("Issue Category")
    )

    # -----------------------------------------------------
    # REPAIR COST
    # -----------------------------------------------------
    st.subheader("💰 Average Repair Cost")

    repair_data = pd.DataFrame(
        {
            "Issue Category": [
                "Display / UI",
                "Sensor / Calibration",
                "Energy Storage (Battery)",
                "Electrical / Short & Power",
                "Corrosion / Environmental",
                "Mechanical Wear / Vibration",
                "Leakage / Fluid System",
                "Thermal / Overheating",
                "Uncategorised",
            ],
            "Average Repair Cost": [
                205,
                204,
                196.4,
                192.6,
                190,
                182.4,
                181,
                180.8,
                173.7,
            ],
        }
    )

    st.bar_chart(
        repair_data.set_index("Issue Category")
    )

    # -----------------------------------------------------
    # FULL REPORT
    # -----------------------------------------------------
    st.markdown("---")

    with st.expander("📄 View Complete Task 2 Report"):

        if task2_text:
            st.markdown(task2_text)
        else:
            st.warning("Task 2 report was not found.")