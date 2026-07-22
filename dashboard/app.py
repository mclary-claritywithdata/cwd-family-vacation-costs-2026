from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="What Does a Family Vacation Cost in 2026?",
    layout="wide",
)


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def find_existing_file(*filenames):
    """
    Return the first matching file found in the data directory.

    This allows the app to support both the correctly spelled
    'simulator' filename and the current 'simulater' filename.
    """

    for filename in filenames:
        file_path = DATA_DIR / filename

        if file_path.exists():
            return file_path

    return DATA_DIR / filenames[0]


budget_file = find_existing_file(
    "vacation_budget_simulator.xlsx",
    "vacation_budget_simulater.xlsx",
)

gas_file = DATA_DIR / "gas_summary.xlsx"
tsa_file = DATA_DIR / "tsa_summary.xlsx"
bls_file = DATA_DIR / "bls_summary.xlsx"


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_required_data():
    budget_df = pd.read_excel(budget_file)
    gas_df = pd.read_excel(gas_file)

    return budget_df, gas_df


@st.cache_data
def load_optional_data(file_path):
    if file_path.exists():
        return pd.read_excel(file_path)

    return pd.DataFrame()


try:
    budget_df, gas_df = load_required_data()
    tsa_df = load_optional_data(tsa_file)
    bls_df = load_optional_data(bls_file)

except FileNotFoundError as error:
    st.error("A required data file could not be found.")
    st.code(str(error))
    st.stop()

except Exception as error:
    st.error("The project data could not be loaded.")
    st.code(str(error))
    st.stop()


# =========================================================
# STANDARDIZE COLUMN NAMES
# =========================================================

def clean_columns(dataframe):
    dataframe = dataframe.copy()

    dataframe.columns = (
        dataframe.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    return dataframe


budget_df = clean_columns(budget_df)
gas_df = clean_columns(gas_df)
tsa_df = clean_columns(tsa_df)
bls_df = clean_columns(bls_df)


# =========================================================
# PREPARE BUDGET DATA
# =========================================================

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


required_budget_columns = [
    "destination",
    "avg_duration",
    "avg_accommodation_cost",
    "avg_transportation_cost",
    "estimated_food_cost",
    "estimated_activity_cost",
    "estimated_total_vacation_cost",
]

missing_budget_columns = [
    column
    for column in required_budget_columns
    if column not in budget_df.columns
]

if missing_budget_columns:
    st.error(
        "The vacation budget file is missing these required columns:"
    )

    st.code(", ".join(missing_budget_columns))
    st.stop()


budget_df = budget_df.dropna(
    subset=[
        "destination",
        "estimated_total_vacation_cost",
    ]
)


# =========================================================
# PREPARE GAS DATA
# =========================================================

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


gas_region_names = {
    "emm_epm0u_pte_nus_dpg": "United States",
    "emm_epm0u_pte_r10_dpg": "East Coast",
    "emm_epm0u_pte_r1x_dpg": "New England",
    "emm_epm0u_pte_r1y_dpg": "Central Atlantic",
    "emm_epm0u_pte_r1z_dpg": "Lower Atlantic",
    "emm_epm0u_pte_r20_dpg": "Midwest",
    "emm_epm0u_pte_r30_dpg": "Gulf Coast",
    "emm_epm0u_pte_r40_dpg": "Rocky Mountain",
    "emm_epm0u_pte_r50_dpg": "West Coast",
    "emm_epm0u_pte_sco_dpg": "Colorado",
    "emm_epm0u_pte_sfl_dpg": "Florida",
    "emm_epm0u_pte_smn_dpg": "Minnesota",
    "emm_epm0u_pte_sny_dpg": "New York",
    "emm_epm0u_pte_soh_dpg": "Ohio",
    "emm_epm0u_pte_stx_dpg": "Texas",
    "emm_epm0u_pte_swa_dpg": "Washington",
    "emm_epm0u_pte_y48se_dpg": "Seattle",
    "emm_epm0u_pte_ycle_dpg": "Cleveland",
    "emm_epm0u_pte_yden_dpg": "Denver",
    "emm_epm0u_pte_ymia_dpg": "Miami",
}


regional_gas_names = {
    "United States",
    "East Coast",
    "New England",
    "Central Atlantic",
    "Lower Atlantic",
    "Midwest",
    "Gulf Coast",
    "Rocky Mountain",
    "West Coast",
}


if "source_key" in gas_df.columns:
    gas_df["region_name"] = (
        gas_df["source_key"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace(gas_region_names)
    )

    gas_df["location_type"] = gas_df["region_name"].apply(
        lambda value: (
            "Region"
            if value in regional_gas_names
            else "State or City"
        )
    )


# =========================================================
# PAGE HEADER
# =========================================================

st.title("What Does a Family Vacation Cost in 2026?")

st.markdown(
    """
    **An interactive Clarity With Data project exploring lodging,
    transportation, food, activities, fuel prices, inflation, and
    travel demand.**

    Use the calculator to explore how destination, family size,
    trip length, and daily spending choices affect the estimated
    cost of a family vacation.
    """
)


# =========================================================
# NAVIGATION
# =========================================================

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

    # -----------------------------------------------------
    # COST DRIVERS
    # -----------------------------------------------------

    st.subheader("What’s Driving Vacation Costs?")

    st.write(
        """
        This view shows how each major spending category contributes
        to the average vacation estimate produced by this model.
        """
    )

    cost_driver_data = pd.DataFrame(
        {
            "Cost Category": [
                "Lodging",
                "Transportation",
                "Food",
                "Activities",
            ],
            "Average Cost": [
                budget_df[
                    "avg_accommodation_cost"
                ].mean(),
                budget_df[
                    "avg_transportation_cost"
                ].mean(),
                budget_df[
                    "estimated_food_cost"
                ].mean(),
                budget_df[
                    "estimated_activity_cost"
                ].mean(),
            ],
        }
    )

    total_driver_cost = cost_driver_data[
        "Average Cost"
    ].sum()

    if total_driver_cost > 0:
        cost_driver_data["Share of Estimated Cost"] = (
            cost_driver_data["Average Cost"]
            / total_driver_cost
        )
    else:
        cost_driver_data["Share of Estimated Cost"] = 0

    cost_driver_data = cost_driver_data.sort_values(
        "Average Cost",
        ascending=True,
    )

    largest_driver = cost_driver_data.loc[
        cost_driver_data["Average Cost"].idxmax()
    ]

    driver_chart = px.bar(
        cost_driver_data,
        x="Average Cost",
        y="Cost Category",
        orientation="h",
        title="Average Contribution by Cost Category",
        labels={
            "Average Cost": "Average Cost",
            "Cost Category": "Cost Category",
        },
        text="Average Cost",
    )

    driver_chart.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
    )

    driver_chart.update_layout(
        xaxis_tickprefix="$",
        showlegend=False,
        height=420,
    )

    st.plotly_chart(
        driver_chart,
        use_container_width=True,
    )

    st.info(
        f"""
        **{largest_driver['Cost Category']} is the largest average
        cost driver in this model**, accounting for approximately
        {largest_driver['Share of Estimated Cost']:.0%} of the four
        major vacation spending categories.
        """
    )

    st.caption(
        "These percentages represent contribution within this "
        "project’s vacation-cost model. They do not establish "
        "universal or causal drivers of travel prices."
    )

    st.divider()

    # -----------------------------------------------------
    # DESTINATION COMPARISON
    # -----------------------------------------------------

    st.subheader("How Do Destinations Compare?")

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
            "estimated_vacation_cost": (
                "Estimated Vacation Cost"
            ),
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
        "Destination estimates include lodging, transportation, "
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
        The calculator uses destination-level lodging and
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
        source_duration = (
            selected_row["vacation_days"]
            if "vacation_days" in selected_row.index
            else 5
        )

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
        title=(
            "Estimated Cost Breakdown: "
            f"{selected_destination}"
        ),
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
    st.header("Travel Trends")

    gas_tab, demand_tab, inflation_tab = st.tabs(
        [
            "Gas Prices",
            "Traveler Demand",
            "Travel-Related Inflation",
        ]
    )

    # -----------------------------------------------------
    # GAS PRICE TRENDS
    # -----------------------------------------------------

    with gas_tab:
        st.subheader("Average Gas Prices Over Time")

        required_gas_columns = {
            "year",
            "source_key",
            "region_name",
            "avg_gas_price",
            "location_type",
        }

        if required_gas_columns.issubset(gas_df.columns):
            regional_tab, state_city_tab = st.tabs(
                [
                    "U.S. Regional View",
                    "State & City View",
                ]
            )

            # ---------------------------------------------
            # REGIONAL VIEW
            # ---------------------------------------------

            with regional_tab:
                regional_data = gas_df[
                    gas_df["location_type"] == "Region"
                ].dropna(
                    subset=[
                        "year",
                        "region_name",
                        "avg_gas_price",
                    ]
                )

                available_regions = sorted(
                    regional_data["region_name"]
                    .astype(str)
                    .unique()
                    .tolist()
                )

                preferred_regional_defaults = [
                    "United States",
                    "East Coast",
                    "Midwest",
                    "Gulf Coast",
                    "West Coast",
                ]

                regional_defaults = [
                    region
                    for region in preferred_regional_defaults
                    if region in available_regions
                ]

                selected_regions = st.multiselect(
                    "Select national or regional series",
                    options=available_regions,
                    default=regional_defaults,
                    key="regional_gas_selection",
                )

                if selected_regions:
                    regional_chart_data = regional_data[
                        regional_data["region_name"].isin(
                            selected_regions
                        )
                    ]

                    regional_chart = px.line(
                        regional_chart_data,
                        x="year",
                        y="avg_gas_price",
                        color="region_name",
                        markers=True,
                        title=(
                            "National and Regional Gas "
                            "Price Trends"
                        ),
                        labels={
                            "year": "Year",
                            "avg_gas_price": (
                                "Average Gas Price"
                            ),
                            "region_name": "Region",
                        },
                    )

                    regional_chart.update_layout(
                        yaxis_tickprefix="$",
                        legend_title_text="Region",
                    )

                    st.plotly_chart(
                        regional_chart,
                        use_container_width=True,
                    )

                else:
                    st.info(
                        "Select at least one region to "
                        "display the chart."
                    )

            # ---------------------------------------------
            # STATE AND CITY VIEW
            # ---------------------------------------------

            with state_city_tab:
                local_data = gas_df[
                    gas_df["location_type"] == "State or City"
                ].dropna(
                    subset=[
                        "year",
                        "region_name",
                        "avg_gas_price",
                    ]
                )

                available_locations = sorted(
                    local_data["region_name"]
                    .astype(str)
                    .unique()
                    .tolist()
                )

                preferred_location_defaults = [
                    "Florida",
                    "Texas",
                    "New York",
                    "Colorado",
                    "Washington",
                ]

                location_defaults = [
                    location
                    for location in preferred_location_defaults
                    if location in available_locations
                ]

                selected_locations = st.multiselect(
                    "Select states or cities",
                    options=available_locations,
                    default=location_defaults,
                    key="local_gas_selection",
                )

                if selected_locations:
                    local_chart_data = local_data[
                        local_data["region_name"].isin(
                            selected_locations
                        )
                    ]

                    local_chart = px.line(
                        local_chart_data,
                        x="year",
                        y="avg_gas_price",
                        color="region_name",
                        markers=True,
                        title=(
                            "State and City Gas Price Trends"
                        ),
                        labels={
                            "year": "Year",
                            "avg_gas_price": (
                                "Average Gas Price"
                            ),
                            "region_name": "Location",
                        },
                    )

                    local_chart.update_layout(
                        yaxis_tickprefix="$",
                        legend_title_text="Location",
                    )

                    st.plotly_chart(
                        local_chart,
                        use_container_width=True,
                    )

                else:
                    st.info(
                        "Select at least one state or city "
                        "to display the chart."
                    )

        else:
            st.warning(
                "The gas-price chart could not be displayed "
                "because the expected columns were not found."
            )

    # -----------------------------------------------------
    # TSA TRAVELER DEMAND
    # -----------------------------------------------------

    with demand_tab:
        st.subheader("TSA Traveler Volume")

        required_tsa_columns = {
            "year",
            "total_travelers",
        }

        if (
            not tsa_df.empty
            and required_tsa_columns.issubset(tsa_df.columns)
        ):
            tsa_df["year"] = pd.to_numeric(
                tsa_df["year"],
                errors="coerce",
            )

            tsa_df["total_travelers"] = pd.to_numeric(
                tsa_df["total_travelers"],
                errors="coerce",
            )

            tsa_chart_data = tsa_df.dropna(
                subset=[
                    "year",
                    "total_travelers",
                ]
            )

            tsa_chart = px.line(
                tsa_chart_data,
                x="year",
                y="total_travelers",
                markers=True,
                title="TSA Traveler Volume Over Time",
                labels={
                    "year": "Year",
                    "total_travelers": "Total Travelers",
                },
            )

            st.plotly_chart(
                tsa_chart,
                use_container_width=True,
            )

        else:
            st.info(
                "The TSA summary file is unavailable or does "
                "not contain the expected columns."
            )

    # -----------------------------------------------------
    # BLS CPI TRENDS
    # -----------------------------------------------------

    with inflation_tab:
        st.subheader("Travel-Related Consumer Prices")

        required_bls_columns = {
            "year",
            "series",
            "avg_cpi",
        }

        if (
            not bls_df.empty
            and required_bls_columns.issubset(bls_df.columns)
        ):
            bls_df["year"] = pd.to_numeric(
                bls_df["year"],
                errors="coerce",
            )

            bls_df["avg_cpi"] = pd.to_numeric(
                bls_df["avg_cpi"],
                errors="coerce",
            )

            bls_chart_data = bls_df.dropna(
                subset=[
                    "year",
                    "series",
                    "avg_cpi",
                ]
            )

            available_series = sorted(
                bls_chart_data["series"]
                .astype(str)
                .unique()
                .tolist()
            )

            selected_series = st.multiselect(
                "Select cost categories",
                options=available_series,
                default=available_series,
            )

            if selected_series:
                filtered_bls_data = bls_chart_data[
                    bls_chart_data["series"].isin(
                        selected_series
                    )
                ]

                bls_chart = px.line(
                    filtered_bls_data,
                    x="year",
                    y="avg_cpi",
                    color="series",
                    markers=True,
                    title=(
                        "Travel-Related Consumer Price Trends"
                    ),
                    labels={
                        "year": "Year",
                        "avg_cpi": "Average CPI",
                        "series": "Cost Category",
                    },
                )

                st.plotly_chart(
                    bls_chart,
                    use_container_width=True,
                )

            else:
                st.info(
                    "Select at least one cost category "
                    "to display the chart."
                )

        else:
            st.info(
                "The BLS summary file is unavailable or does "
                "not contain the expected columns."
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

    with st.expander("Preview gas price data"):
        gas_preview_columns = [
            column
            for column in [
                "year",
                "source_key",
                "region_name",
                "avg_gas_price",
            ]
            if column in gas_df.columns
        ]

        st.dataframe(
            gas_df[gas_preview_columns].head(20),
            use_container_width=True,
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Clarity With Data | Where Insight Meets Intention"
)
