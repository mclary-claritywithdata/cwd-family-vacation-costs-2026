import plotly.express as px
import streamlit as st
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

budget_file = BASE_DIR / "vacation_budget_simulator.xlsx"
gas_file = BASE_DIR / "gas_summary.xlsx"