import plotly.express as px
import streamlit as st
from pathlib import Path
import pandas as pd


#PAGE CONFIGURATIONS
st.set_page_config(
    page_title="What Does a Family Vacation Cost in 2026?",
    layout="wide"
)
 

#FILE PATHS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

budget_file = DATA_DIR / "vacation_budget_simulator.xlsx"
gas_file = DATA_DIR / "gas_summary.xlsx"

#LOAD DATA

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


#PAGE CONTENT

st.title("What Does a Family Vacation Cost in 2026?")

st.write(

    """
    An interactive Clarity with Data project exploring the cost of
    lodging, transporation, food, activities, and fuel.
    """
)

#VACATION BUDGET DATA

st.success("The Streamlit app and data files loaded successfully")

st.subheader("Vacation Budget Data")

st.set_page_config(
    page_title="What Does a Family Vacation Cost in 2026?",
    layout="wide"
)



#PAGE CONTENT

st.title("What Does a Family Vacation Cost in 2026?")

st.write(
    """
    An interactive Clarity with Data project exploring the cost of
    lodging, transporation, food, activities, and fuel.
    """
)

st.success("The Streamlit app and data files loaded successfully")
st.subheader("Vacation Budget Data")

