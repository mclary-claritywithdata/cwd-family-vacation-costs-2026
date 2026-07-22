import plotly.express as px
import streamlit as st
from pathlib import Path
import pandas as pd


st.set_page_config(
    page_title="What Does a Family Vacation Cost in 2026?",
    layout="wide"
)
 

#FILE PATHS

BASE_DIR = Path.cwd()

budget_file = BASE_DIR / "vacation_budget_simulator.xlsx"
gas_file = BASE_DIR / "gas_summary.xlsx"

#LOAD DATA

budget_df = pd.read_excel(budget_file)
gas_df = pd.read_excel(gas_file)


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

import plotly.express as px
import streamlit as st
from pathlib import Path
import pandas as pd

 

st.set_page_config(
    page_title="What Does a Family Vacation Cost in 2026?",
    layout="wide"
)

#FILE PATHS

BASE_DIR = Path.cwd()

budget_file = BASE_DIR / "vacation_budget_simulator.xlsx"
gas_file = BASE_DIR / "gas_summary.xlsx"


#LOAD DATA

budget_df = pd.read_excel(budget_file)

gas_df = pd.read_excel(gas_file)

 

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

