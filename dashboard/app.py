from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="What Does a Family Vacation Cost in 2026?",
    layout="wide",
)


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# This matches the current filename in GitHub.
budget_file = DATA_DIR / "vacation_budget_simulater.xlsx"
gas_file = DATA_DIR / "gas_summary.xlsx"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():
    budget_df = pd.read_excel(budget_file)
    gas_df = pd.read_excel(gas_file)

    return budget_df, gas_df


try:
    budget_df, gas_df = load_data()

except FileNotFoundError as error:
    st.error("A required data file could not be found.")
    st.code(str(error))
    st.stop()

except Exception as error:
    st.error("The data files could not be loaded.")
    st.code(str(error))
    st.stop()


# ---------------------------------------------------------
# PREPARE DATA
# ---------------------------------------------------------

budget_numeric_columns = [
    "avg_duration",
    "avg_accommodation_cost",
    "avg_transportation_cost",
    "avg_total_known_trip_cost",
    "trips",
    "family_size",
    "vacation_days",
    "estimated_food_cost",
    "estimated_activity_cost",
    "estimated_total_vacation_cost",
]

for column in budget_numeric_columns:
    if column in budget_df.columns:
        budget_df[column] = pd.to_numeric(
            budget_df[column],
            errors="coerce",
        )

if "year" in gas_df.columns:
    gas_df["year"] = pd.to_numeric(
        gas_df["year"],
        errors="coerce",
    )

if "avg_gas_price" in gas_df.columns:
    gas_df["avg_gas_price"] = pd.to_numeric(
        gas_df["avg_gas_price"],
        errors="coerce",
    )

budget_df = budget_df.dropna(
    subset=[
        "destination",
        "estimated_total_vacation_cost",
    ]
)


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------

st.title("What Does a Family Vacation Cost in 2026?")

st.markdown(
    """
    **An interactive Clarity With Data project exploring the cost of
    lodging, transportation, food, activities, and fuel.**

    Use the calculator to explore how destination, family size, trip
    length, and daily spending choices affect the estimated cost of
    a family vacation.
    """
)


# ---------------------------------------------------------
# NAVIGATION TABS
# ---------------------------------------------------------

overview_tab, calculator_tab, trends_tab, methodology_tab = st.tabs(
    [
        "Project Overview",
        "Vacation Calculator",
        "Travel Trends",
        "Data & Methodology",
    ]
)


# =========================================================
# TAB 1: PROJECT OVERVIEW
# =========================================================

with overview_tab:
    st.header("The Cost of Family Travel")

    average_vacation_cost = (
        budget_df["estimated_total_vacation_cost"].mean()
    )

    average_lodging_cost = (
        budget_df["avg_accommodation_cost"].mean()
    )

    average_transportation_cost = (
        budget_df["avg_transportation_cost"].mean()
    )

    average_gas_price = (
        gas_df["avg_gas_price"].mean()
        if "avg_gas_price" in gas_df.columns
        else 0
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    metric_1.metric(
        "Average Vacation Cost",
        f"${average_vacation_cost:,.0f}",
    )

    metric_2.metric(
        "Average Lodging Cost",
        f"${average_lodging_cost:,.0f}",
    )

    metric_3.metric(
        "Average Transportation",
        f"${average_transportation_cost:,.0f}",
    )

    metric_4.metric(
        "Average Gas Price",
        f"${average_gas_price:,.2f}",
    )

    st.divider()

    destination_comparison = (
        budget_df.groupby(
            "destination",
            as_index=False,
        )
        .agg(
            estimated_vacation_cost=(
                "estimated_total_vacation_cost",
                "mean",
            )
        )
        .sort_values(
            "estimated_vacation_cost",
            ascending=True,
        )
    )

    destination_chart = px.bar(
        destination_comparison,
        x="estimated_vacation_cost",
        y="destination",
        orientation="h",
        title="Estimated Vacation Cost by Destination",
        labels={
            "estimated_vacation_cost": "Estimated Vacation Cost",
            "destination": "Destination",
        },
        text="estimated_vacation_cost",
    )

    destination_chart.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
    )

    destination_chart.update_layout(
        height=550,
        xaxis_tickprefix="$",
        showlegend=False,
    )

    st.plotly_chart(
        destination_chart,
        use_container_width=True,
    )

    st.caption(
        "The destination estimates include lodging, transportation, "
        "food, and activity costs."
    )


# =========================================================
# TAB 2: VACATION CALCULATOR
# =========================================================

with calculator_tab:
    st.header("Build Your Family Vacation Budget")

    st.write(
        """
        Select a destination and adjust the trip details below.
        The calculator uses the destination-level lodging and
        transportation averages from the processed project data.
        """
    )

    destinations = sorted(
        budget_df["destination"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    control_1, control_2, control_3 = st.columns(3)

    selected_destination = control_1.selectbox(
        "Destination",
        destinations,
    )

    family_size = control_2.slider(
        "Family size",
        min_value=1,
        max_value=10,
        value=4,
        step=1,
    )

    vacation_days = control_3.slider(
        "Vacation length in days",
        min_value=2,
        max_value=14,
        value=5,
        step=1,
    )

    control_4, control_5 = st.columns(2)

    daily_food_cost = control_4.slider(
        "Daily food budget per person",
        min_value=20,
        max_value=150,
        value=55,
        step=5,
        format="$%d",
    )

    daily_activity_cost = control_5.slider(
        "Daily activity budget per person",
        min_value=0,
        max_value=150,
        value=45,
        step=5,
        format="$%d",
    )

    selected_row = budget_df[
        budget_df["destination"].astype(str)
        == selected_destination
    ].iloc[0]

    source_duration = selected_row["avg_duration"]

    if pd.isna(source_duration) or source_duration <= 0:
        source_duration = selected_row["vacation_days"]

    if pd.isna(source_duration) or source_duration <= 0:
        source_duration = 5

    base_lodging_cost = selected_row[
        "avg_accommodation_cost"
    ]

    transportation_cost = selected_row[
        "avg_transportation_cost"
    ]

    lodging_cost = (
        base_lodging_cost
        * vacation_days
        / source_duration
    )

    food_cost = (
        family_size
        * vacation_days
        * daily_food_cost
    )

    activity_cost = (
        family_size
        * vacation_days
        * daily_activity_cost
    )

    estimated_total = (
        lodging_cost
        + transportation_cost
        + food_cost
        + activity_cost
    )

    planning_buffer = estimated_total * 0.10
    comfortable_budget = estimated_total + planning_buffer

    st.divider()

    st.subheader(
        f"Estimated Budget for {selected_destination}"
    )

    result_1, result_2, result_3, result_4 = st.columns(4)

    result_1.metric(
        "Estimated Total",
        f"${estimated_total:,.0f}",
    )

    result_2.metric(
        "Lodging",
        f"${lodging_cost:,.0f}",
    )

    result_3.metric(
        "Transportation",
        f"${transportation_cost:,.0f}",
    )

    result_4.metric(
        "Food & Activities",
        f"${food_cost + activity_cost:,.0f}",
    )

    st.subheader("The Clarity Budget")

    clarity_1, clarity_2, clarity_3 = st.columns(3)

    clarity_1.metric(
        "Base Estimate",
        f"${estimated_total:,.0f}",
    )

    clarity_2.metric(
        "10% Planning Buffer",
        f"${planning_buffer:,.0f}",
    )

    clarity_3.metric(
        "Comfortable Budget",
        f"${comfortable_budget:,.0f}",
    )

    st.info(
        "The planning buffer helps account for parking, taxes, "
        "tips, baggage fees, price changes, and unexpected costs."
    )

    cost_breakdown = pd.DataFrame(
        {
            "Category": [
                "Lodging",
                "Transportation",
                "Food",
                "Activities",
            ],
            "Estimated Cost": [
                lodging_cost,
                transportation_cost,
                food_cost,
                activity_cost,
            ],
        }
    )

    breakdown_chart = px.bar(
        cost_breakdown,
        x="Category",
        y="Estimated Cost",
        title=f"Estimated Cost Breakdown: {selected_destination}",
        text="Estimated Cost",
    )

    breakdown_chart.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
    )

    breakdown_chart.update_layout(
        yaxis_tickprefix="$",
        showlegend=False,
    )

    st.plotly_chart(
        breakdown_chart,
        use_container_width=True,
    )


# =========================================================
# TAB 3: TRAVEL TRENDS
# =========================================================

with trends_tab:
    st.header("Gas Price Trends")

    required_gas_columns = {
        "year",
        "source_key",
        "avg_gas_price",
    }

    if required_gas_columns.issubset(gas_df.columns):
        gas_chart_data = gas_df.dropna(
            subset=[
                "year",
                "source_key",
                "avg_gas_price",
            ]
        )

        available_regions = sorted(
            gas_chart_data["source_key"]
            .astype(str)
            .unique()
            .tolist()
        )

        default_regions = available_regions[:5]

        selected_regions = st.multiselect(
            "Select gas price regions",
            available_regions,
            default=default_regions,
        )

        if selected_regions:
            gas_chart_data = gas_chart_data[
                gas_chart_data["source_key"]
                .astype(str)
                .isin(selected_regions)
            ]

            gas_chart = px.line(
                gas_chart_data,
                x="year",
                y="avg_gas_price",
                color="source_key",
                markers=True,
                title="Average Gas Prices Over Time",
                labels={
                    "year": "Year",
                    "avg_gas_price": "Average Gas Price",
                    "source_key": "Region",
                },
            )

            gas_chart.update_layout(
                yaxis_tickprefix="$",
            )

            st.plotly_chart(
                gas_chart,
                use_container_width=True,
            )

        else:
            st.info(
                "Select at least one region to display "
                "the gas price chart."
            )

    else:
        st.warning(
            "The gas trend chart could not be displayed because "
            "the expected gas summary columns were not found."
        )

    with st.expander("Preview gas summary data"):
        st.dataframe(
            gas_df.head(20),
            use_container_width=True,
        )


# =========================================================
# TAB 4: DATA AND METHODOLOGY
# =========================================================

with methodology_tab:
    st.header("Project Question")

    st.write(
        """
        What does a family vacation cost in 2026, and which
        expenses contribute most to the final budget?
        """
    )

    st.subheader("Data Sources")

    st.markdown(
        """
        - Airbnb lodging data
        - Supplemental destination and travel-cost data
        - U.S. Energy Information Administration gasoline prices
        - Transportation Security Administration traveler throughput
        - Bureau of Labor Statistics consumer-price data
        """
    )

    st.subheader("Methodology")

    st.markdown(
        """
        1. Loaded and standardized multiple public and supplemental datasets.
        2. Cleaned column names and converted cost fields to numeric values.
        3. Created destination-level lodging and transportation summaries.
        4. Estimated food and activity spending by family size and trip length.
        5. Combined the major spending categories into a vacation estimate.
        6. Added a 10% planning buffer for variable and unexpected expenses.
        """
    )

    st.subheader("Important Note")

    st.warning(
        """
        This tool provides an educational planning estimate and is
        not a live travel quote. Actual expenses will vary based on
        departure city, travel dates, season, taxes, fees, lodging
        preferences, and individual spending decisions.
        """
    )

    with st.expander("Preview vacation budget data"):
        st.dataframe(
            budget_df.head(20),
            use_container_width=True,
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Clarity With Data | Where Insight Meets Intention"
)
