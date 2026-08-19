import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import safe_mean
from utils.styling import (
    apply_page_config, section_title, page_header, render_kpi_cards,
    gradient_bar, chart_title, render_alerts, filter_bar, PRIMARY
)
from utils.auth import require_login

require_login()
apply_page_config("Ambulance")

data = get_data_for_page()
amb = data["ambulance"].copy()

page_header("Ambulance & Transportation", "Response times, travel times, fuel cost and pickup-location patterns.", icon_name="ambulance")

seasons = sorted(amb["Season"].dropna().unique().tolist())
min_d, max_d = amb["Call_Date"].min().date(), amb["Call_Date"].max().date()

bar = filter_bar()
fc1, fc2 = bar.columns([2, 1.3])
with fc1:
    sel_season = st.multiselect("Season", seasons, default=seasons)
with fc2:
    dr = st.date_input("Call date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = amb[
    (amb["Season"].isin(sel_season)) &
    (amb["Call_Date"].dt.date >= start_d) &
    (amb["Call_Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No ambulance records match the selected filters.")
    st.stop()

avg_response = safe_mean(f["Response_Time_Min"])
response_tone = "critical" if avg_response >= 15 else "warning" if avg_response >= 10 else "good"

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Total Trips", "value": f"{len(f):,}", "icon": "ambulance", "hero": True,
     "sub": f"₹{f['Fuel_Cost_INR'].sum():,.0f} total fuel cost"},
    {"label": "Avg Response Time", "value": f"{avg_response} min", "icon": "clock", "tone": response_tone,
     "sub": "Above 15 min target" if response_tone == "critical" else ("Trending high" if response_tone == "warning" else "Within target")},
    {"label": "Avg Travel Time", "value": f"{safe_mean(f['Travel_Time_Min'])} min", "icon": "activity"},
    {"label": "Total Fuel Cost", "value": f"₹{f['Fuel_Cost_INR'].sum():,.0f}", "icon": "money"},
]
render_kpi_cards(kpis, cols_per_row=4)

if response_tone == "critical":
    render_alerts([("critical", f"Average ambulance response time is {avg_response} min — above the 15 min target. Review fleet deployment/routing.")])
elif response_tone == "warning":
    render_alerts([("warning", f"Average ambulance response time is {avg_response} min — trending high.")])

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Visual Charts — Unified Blue Theme
# ----------------------------------------------------------------------
col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Trip Volume", icon_name="trending")
    m = f.groupby("Month").size().reset_index(name="Trips").sort_values("Month")
    fig = px.area(m, x="Month", y="Trips")
    fig.update_traces(line_color=PRIMARY, fillcolor="rgba(11,95,255,0.12)")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Trips by Pickup Location (Top 10)", icon_name="package", note="Darker shade = higher volume")
    loc = f["Pickup_Location"].value_counts().head(10).reset_index()
    loc.columns = ["Location", "Trips"]
    fig = gradient_bar(loc, x="Location", y="Trips", orientation="h", scale="Blues")
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Diagnosis Category (Top 10)", icon_name="stethoscope", note="Darker shade = higher volume")
    diag = f["Diagnosis"].value_counts().head(10).reset_index()
    diag.columns = ["Diagnosis", "Count"]
    fig = gradient_bar(diag, x="Diagnosis", y="Count", scale="Blues")  # Updated: Teal -> Blues
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Driver Workload (Top 10)", icon_name="users", note="Darker shade = heavier workload")
    drv = f["Driver_Name"].value_counts().head(10).reset_index()
    drv.columns = ["Driver", "Trips"]
    fig = gradient_bar(drv, x="Driver", y="Trips", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with st.container(border=True):
    chart_title("Response vs Travel Time by Season", icon_name="clock")
    season_time = f.groupby("Season")[["Response_Time_Min", "Travel_Time_Min"]].mean().reset_index()
    season_melt = season_time.melt(id_vars="Season", var_name="Metric", value_name="Minutes")
    
    # Updated: Added corporate blue palette sequence
    fig = px.bar(
        season_melt, x="Season", y="Minutes", color="Metric", barmode="group",
        color_discrete_sequence=["#022C7A", "#60A5FA"]
    )
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

section_title("Raw Ambulance Records", icon_name="table")
st.dataframe(f.sort_values("Call_Date", ascending=False), width='stretch', height=350)