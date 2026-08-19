import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import pct
from utils.styling import (
    apply_page_config, section_title, page_header, render_kpi_cards,
    gradient_bar, chart_title, render_alerts, filter_bar,
)
from utils.auth import require_login

require_login()
apply_page_config("Appointments")

data = get_data_for_page()
appt = data["appointments"].copy()

page_header("Appointments", "Booking volume, completion, cancellations, no-shows and peak hours.", icon_name="calendar")

depts = sorted(appt["Department"].dropna().unique().tolist())
types = sorted(appt["Appointment_Type"].dropna().unique().tolist())
min_d, max_d = appt["Appointment_Date"].min().date(), appt["Appointment_Date"].max().date()

bar = filter_bar()
fc1, fc2, fc3 = bar.columns([1.4, 1.4, 1.3])
with fc1:
    sel_dept = st.multiselect("Department", depts, default=depts)
with fc2:
    sel_type = st.multiselect("Appointment Type", types, default=types)
with fc3:
    dr = st.date_input("Appointment date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = appt[
    (appt["Department"].isin(sel_dept)) &
    (appt["Appointment_Type"].isin(sel_type)) &
    (appt["Appointment_Date"].dt.date >= start_d) &
    (appt["Appointment_Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No appointments match the selected filters.")
    st.stop()

noshow_rate = pct((f['Status'] == 'No-show').sum(), len(f))
noshow_tone = "critical" if noshow_rate >= 20 else "warning" if noshow_rate >= 15 else "good"

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Total Appointments", "value": f"{len(f):,}", "icon": "calendar", "hero": True,
     "sub": f"{pct((f['Status']=='Completed').sum(), len(f))}% completed"},
    {"label": "Completed", "value": f"{pct((f['Status']=='Completed').sum(), len(f))}%", "icon": "check-circle", "tone": "good"},
    {"label": "Cancelled", "value": f"{pct((f['Status']=='Cancelled').sum(), len(f))}%", "icon": "alert", "tone": "warning"},
    {"label": "No-show", "value": f"{noshow_rate}%", "icon": "alert", "tone": noshow_tone},
]
render_kpi_cards(kpis, cols_per_row=4)

if noshow_rate >= 15:
    render_alerts([("warning", f"No-show rate is {noshow_rate}% — consider automated reminders (SMS/call) to reduce missed appointments.")])

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Appointment Volume", icon_name="trending")
    m = f.groupby("Month").size().reset_index(name="Appointments").sort_values("Month")
    fig = px.area(m, x="Month", y="Appointments")
    fig.update_traces(line_color="#0B5FFF", fillcolor="rgba(11,95,255,0.10)")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Status Breakdown", icon_name="chart")
    s = f["Status"].value_counts().reset_index()
    s.columns = ["Status", "Count"]
    fig = px.pie(s, names="Status", values="Count", hole=0.55,
                 color="Status", color_discrete_map={"Completed": "#16A34A", "Cancelled": "#DC2626", "No-show": "#F59E0B"})
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Appointments by Department", icon_name="hospital", note="Darker shade = busier department")
    dep = f.groupby("Department").size().reset_index(name="Count").sort_values("Count", ascending=False)
    fig = gradient_bar(dep, x="Department", y="Count", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Online vs Walk-in", icon_name="users")
    t = f["Appointment_Type"].value_counts().reset_index()
    t.columns = ["Type", "Count"]
    fig = px.pie(t, names="Type", values="Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with st.container(border=True):
    chart_title("Peak Appointment Hours", icon_name="clock", note="Darker shade = higher booking volume")
    hourly = f.groupby("Appointment_Hour").size().reset_index(name="Count").sort_values("Appointment_Hour")
    fig = gradient_bar(hourly, x="Appointment_Hour", y="Count", scale="Teal")
    fig.update_xaxes(dtick=1, title="Hour of Day (24h)")
    st.plotly_chart(fig, width='stretch')

section_title("Raw Appointment Records", icon_name="table")
st.dataframe(f.sort_values("Appointment_Date", ascending=False), width='stretch', height=350)
