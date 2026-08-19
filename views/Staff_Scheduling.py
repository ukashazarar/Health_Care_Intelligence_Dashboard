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
apply_page_config("Staff Scheduling")

data = get_data_for_page()
staff = data["staff"].copy()

page_header("Staff Scheduling & Workforce", "Duty rosters, shifts, leaves, overtime and emergency coverage.", icon_name="briefcase")

depts = sorted(staff["Department"].dropna().unique().tolist())
roles = sorted(staff["Role"].dropna().unique().tolist())
min_d, max_d = staff["Date"].min().date(), staff["Date"].max().date()

bar = filter_bar()
fc1, fc2, fc3 = bar.columns([1.4, 1.4, 1.3])
with fc1:
    sel_dept = st.multiselect("Department", depts, default=depts)
with fc2:
    sel_role = st.multiselect("Role", roles, default=roles)
with fc3:
    dr = st.date_input("Schedule date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = staff[
    (staff["Department"].isin(sel_dept)) &
    (staff["Role"].isin(sel_role)) &
    (staff["Date"].dt.date >= start_d) &
    (staff["Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No staff scheduling records match the selected filters.")
    st.stop()

leave_rate = pct((f['Leave_Status'] == 'On Leave').sum(), len(f))
leave_tone = "critical" if leave_rate >= 20 else "warning" if leave_rate >= 12 else "good"

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Scheduled Shifts", "value": f"{len(f):,}", "icon": "briefcase", "hero": True,
     "sub": f"{f['Overtime_Hours'].sum():,} overtime hours"},
    {"label": "On Leave", "value": f"{leave_rate}%", "icon": "alert", "tone": leave_tone},
    {"label": "Week-Off", "value": f"{pct((f['Leave_Status']=='Week-Off').sum(), len(f))}%", "icon": "calendar"},
    {"label": "Total Overtime Hours", "value": f"{f['Overtime_Hours'].sum():,}", "icon": "clock"},
    {"label": "Appointments Postponed", "value": f"{pct((f['Appointment_Postponed']=='Yes').sum(), len(f))}%", "icon": "activity"},
]
render_kpi_cards(kpis, cols_per_row=5)

if leave_tone == "critical":
    render_alerts([("critical", f"{leave_rate}% of shifts show staff on leave — significant staffing shortage risk.")])
elif leave_tone == "warning":
    render_alerts([("warning", f"{leave_rate}% of shifts show staff on leave — monitor coverage closely.")])

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Leave Trend", icon_name="trending")
    m = f[f["Leave_Status"] == "On Leave"].groupby("Month").size().reset_index(name="On Leave").sort_values("Month")
    fig = px.line(m, x="Month", y="On Leave", markers=True)
    fig.update_traces(line_color="#0B5FFF")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Department-wise Staffing", icon_name="hospital", note="Darker shade = larger roster")
    dep = f.groupby("Department").size().reset_index(name="Shifts")
    fig = gradient_bar(dep, x="Department", y="Shifts", scale="Blues")
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Role Distribution", icon_name="users")
    role = f["Role"].value_counts().reset_index()
    role.columns = ["Role", "Count"]
    fig = px.pie(role, names="Role", values="Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Duty Type by Shift", icon_name="briefcase")
    dt_shift = f.groupby(["Shift", "Duty_Type"]).size().reset_index(name="Count")
    fig = px.bar(dt_shift, x="Shift", y="Count", color="Duty_Type", barmode="stack")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with st.container(border=True):
    chart_title("Emergency Contact Assignment vs Leave Status", icon_name="shield")
    ec = f.groupby(["Leave_Status", "Emergency_Contact_Assigned"]).size().reset_index(name="Count")
    fig = px.bar(ec, x="Leave_Status", y="Count", color="Emergency_Contact_Assigned", barmode="group")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

section_title("Raw Staff Scheduling Records", icon_name="table")
st.dataframe(f.sort_values("Date", ascending=False), width='stretch', height=350)
