import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import pct, safe_mean
from utils.styling import (
    apply_page_config, section_title, page_header, render_kpi_cards,
    gradient_bar, chart_title, render_alerts, filter_bar,
)
from utils.auth import require_login

require_login()
apply_page_config("OT Dashboard")

data = get_data_for_page()
ot = data["ot"].copy()

page_header("Operation Theatre (OT) Dashboard", "Surgery volume, status, duration and room-wise utilization.", icon_name="stethoscope")

depts = sorted(ot["Department"].dropna().unique().tolist())
rooms = sorted(ot["OT_Room_Number"].dropna().unique().tolist())
min_d, max_d = ot["OT_Date"].min().date(), ot["OT_Date"].max().date()

bar = filter_bar()
fc1, fc2, fc3 = bar.columns([1.4, 1.4, 1.3])
with fc1:
    sel_dept = st.multiselect("Department", depts, default=depts)
with fc2:
    sel_room = st.multiselect("OT Room", rooms, default=rooms)
with fc3:
    dr = st.date_input("Surgery date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = ot[
    (ot["Department"].isin(sel_dept)) &
    (ot["OT_Room_Number"].isin(sel_room)) &
    (ot["OT_Date"].dt.date >= start_d) &
    (ot["OT_Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No OT records match the selected filters.")
    st.stop()

cancel_rate = pct((f['Surgery_Status'] == 'Cancelled').sum(), len(f))
cancel_tone = "critical" if cancel_rate >= 15 else "warning" if cancel_rate >= 8 else "good"

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Total Surgeries", "value": f"{len(f):,}", "icon": "stethoscope", "hero": True,
     "sub": f"{safe_mean(f['Duration_Min'])} min avg duration"},
    {"label": "Completed", "value": f"{pct((f['Surgery_Status']=='Completed').sum(), len(f))}%", "icon": "check-circle", "tone": "good"},
    {"label": "Emergency Surgeries", "value": f"{pct((f['Surgery_Status']=='Emergency Surgery').sum(), len(f))}%", "icon": "alert"},
    {"label": "Cancelled", "value": f"{cancel_rate}%", "icon": "alert", "tone": cancel_tone},
    {"label": "Avg Duration", "value": f"{safe_mean(f['Duration_Min'])} min", "icon": "clock"},
]
render_kpi_cards(kpis, cols_per_row=5)

if cancel_tone == "critical":
    render_alerts([("critical", f"OT cancellation rate is {cancel_rate}% — investigate scheduling conflicts or resource shortages.")])
elif cancel_tone == "warning":
    render_alerts([("warning", f"OT cancellation rate is {cancel_rate}% — worth monitoring.")])

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Surgery Volume", icon_name="trending")
    m = f.groupby("Month").size().reset_index(name="Surgeries").sort_values("Month")
    fig = px.area(m, x="Month", y="Surgeries")
    fig.update_traces(line_color="#0B5FFF", fillcolor="rgba(11,95,255,0.10)")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Surgery Status Breakdown", icon_name="chart")
    s = f["Surgery_Status"].value_counts().reset_index()
    s.columns = ["Status", "Count"]
    fig = px.pie(s, names="Status", values="Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Surgeries by Department", icon_name="hospital", note="Darker shade = busier department")
    dep = f.groupby("Department").size().reset_index(name="Count").sort_values("Count", ascending=False)
    fig = gradient_bar(dep, x="Department", y="Count", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("OT Room Utilization", icon_name="activity", note="Darker shade = higher utilization")
    room = f.groupby("OT_Room_Number").size().reset_index(name="Surgeries").sort_values("Surgeries", ascending=False)
    fig = gradient_bar(room, x="OT_Room_Number", y="Surgeries", scale="Teal")
    st.plotly_chart(fig, width='stretch')

col5, col6 = st.columns(2)
with col5, st.container(border=True):
    chart_title("Surgeon Workload (Top 15)", icon_name="users", note="Darker shade = heavier caseload")
    surgeon = f["Surgeon_Name"].value_counts().head(15).reset_index()
    surgeon.columns = ["Surgeon", "Cases"]
    fig = gradient_bar(surgeon, x="Surgeon", y="Cases", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with col6, st.container(border=True):
    chart_title("Avg Surgery Duration by Department", icon_name="clock", note="Darker shade = longer average duration")
    dur = f.groupby("Department")["Duration_Min"].mean().reset_index().sort_values("Duration_Min", ascending=False)
    fig = gradient_bar(dur, x="Department", y="Duration_Min", scale="Blues", value_suffix=" min")
    st.plotly_chart(fig, width='stretch')

section_title("Raw OT Records", icon_name="table")
st.dataframe(f.sort_values("OT_Date", ascending=False), width='stretch', height=350)
