
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Load data
data = pd.read_excel("Mini-Schedule Template R2.xlsx", sheet_name="Data")
actuals = pd.read_excel("Mini-Schedule Template R2.xlsx", sheet_name="Actuals")

# Preprocessing
actuals_summary = actuals.groupby("Activity ID")["Actual QTY"].sum().reset_index()
data = data.merge(actuals_summary, on="Activity ID", how="left")
data["Actual QTY"] = data["Actual QTY"].fillna(0)
data["Planned Start"] = pd.to_datetime(data["Planned Start"])
data["Planned Finish"] = pd.to_datetime(data["Planned Finish"])

# Sidebar filters
st.sidebar.title("Filters")
buildings = st.sidebar.multiselect("Select Building", data["Building Name"].unique(), default=data["Building Name"].unique())
zones = st.sidebar.multiselect("Select Zone", data["Zone"].unique(), default=data["Zone"].unique())
divisions = st.sidebar.multiselect("Select Division", data["Div of work"].unique(), default=data["Div of work"].unique())

# Filter data
filtered_data = data[(data["Building Name"].isin(buildings)) &
                     (data["Zone"].isin(zones)) &
                     (data["Div of work"].isin(divisions))]

# Gantt Chart
st.header("Gantt Chart")
gantt_fig = px.timeline(
    filtered_data,
    x_start="Planned Start",
    x_end="Planned Finish",
    y="Activity Name",
    color="Div of work",
    hover_data=["Project Name", "Building Name", "Zone", "QTY", "Actual QTY"]
)
gantt_fig.update_yaxes(autorange="reversed")
st.plotly_chart(gantt_fig, use_container_width=True)

# S-Curve
st.header("S-Curve")
filtered_data = filtered_data.sort_values("Planned Start")
filtered_data["Cumulative Planned"] = filtered_data["QTY"].cumsum()
filtered_data["Cumulative Actual"] = filtered_data["Actual QTY"].cumsum()

s_curve = go.Figure()
s_curve.add_trace(go.Scatter(x=filtered_data["Planned Start"], y=filtered_data["Cumulative Planned"], mode='lines+markers', name='Planned'))
s_curve.add_trace(go.Scatter(x=filtered_data["Planned Start"], y=filtered_data["Cumulative Actual"], mode='lines+markers', name='Actual'))

s_curve.update_layout(title="S-Curve: Planned vs Actual", xaxis_title="Date", yaxis_title="Cumulative Quantity")
st.plotly_chart(s_curve, use_container_width=True)
