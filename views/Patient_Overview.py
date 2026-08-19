import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import pct, safe_mean
from utils.styling import (
    apply_page_config, section_title, page_header, render_kpi_cards,
    gradient_bar, chart_title, filter_bar,
)
from utils.auth import require_login

require_login()
apply_page_config("Patient Overview")

data = get_data_for_page()
visits = data["visits"].copy()

page_header("Patient Overview — Hospital Visits", "Deep dive into patient visits, demographics, admissions, billing and satisfaction.", icon_name="users")

# ---------------------------------------------------------------
# Filters
# ---------------------------------------------------------------
depts = sorted(visits["Department"].dropna().unique().tolist())
admit_types = sorted(visits["Admission_Type"].dropna().unique().tolist())
min_d, max_d = visits["Visit_Date"].min().date(), visits["Visit_Date"].max().date()

bar = filter_bar()
fc1, fc2, fc3 = bar.columns([1.4, 1.4, 1.3])
with fc1:
    sel_dept = st.multiselect("Department", depts, default=depts)
with fc2:
    sel_admit = st.multiselect("Admission Type", admit_types, default=admit_types)
with fc3:
    dr = st.date_input("Visit date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = visits[
    (visits["Department"].isin(sel_dept)) &
    (visits["Admission_Type"].isin(sel_admit)) &
    (visits["Visit_Date"].dt.date >= start_d) &
    (visits["Visit_Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No visits match the selected filters.")
    st.stop()

# ---------------------------------------------------------------
# KPIs — curated to the 6 most decision-relevant metrics for a
# patient-level view (the remaining raw fields are still explorable
# in the charts and the records table below).
# ---------------------------------------------------------------
readmit_rate = pct((f['Readmission'] == 'Yes').sum(), len(f))
readmit_tone = "critical" if readmit_rate >= 15 else "warning" if readmit_rate >= 10 else "good"
satisfaction = safe_mean(f['Satisfaction_Score'])
sat_tone = "critical" if satisfaction < 3 else "warning" if satisfaction < 3.8 else "good"

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Patients", "value": f"{len(f):,}", "icon": "users", "hero": True,
     "sub": f"₹{f['Total_Bill'].mean():,.0f} avg bill"},
    {"label": "Avg Waiting Time", "value": f"{safe_mean(f['Waiting_Time_Min'])} min", "icon": "clock"},
    {"label": "Avg Length of Stay", "value": f"{safe_mean(f['Length_of_Stay'])} days", "icon": "calendar"},
    {"label": "Readmission Rate", "value": f"{readmit_rate}%", "icon": "repeat", "tone": readmit_tone},
    {"label": "Insurance Coverage", "value": f"{pct((f['Insurance']=='Yes').sum(), len(f))}%", "icon": "shield"},
    {"label": "Avg Satisfaction", "value": f"{satisfaction} / 5", "icon": "smile", "tone": sat_tone},
]
render_kpi_cards(kpis, cols_per_row=3)

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Patient Trend", icon_name="trending")
    m = f.groupby("Month").size().reset_index(name="Patients").sort_values("Month")
    fig = px.area(m, x="Month", y="Patients")
    fig.update_traces(line_color="#0B5FFF", fillcolor="rgba(11,95,255,0.10)")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Gender Distribution", icon_name="users")
    g = f["Gender"].value_counts().reset_index()
    g.columns = ["Gender", "Count"]
    fig = px.pie(g, names="Gender", values="Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Department vs Admission Type", icon_name="hospital")
    ct = f.groupby(["Department", "Admission_Type"]).size().reset_index(name="Count")
    fig = px.bar(ct, x="Department", y="Count", color="Admission_Type", barmode="stack")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Age Distribution", icon_name="chart")
    fig = px.histogram(f, x="Age", nbins=20)
    fig.update_traces(marker_color="#0B5FFF")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col5, col6 = st.columns(2)
with col5, st.container(border=True):
    chart_title("Discharge Status", icon_name="activity", note="Darker shade = more common outcome")
    ds = f["Discharge_Status"].value_counts().reset_index()
    ds.columns = ["Status", "Count"]
    fig = gradient_bar(ds, x="Status", y="Count", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with col6, st.container(border=True):
    chart_title("Payment Status by Insurance", icon_name="card")
    pv = f.groupby(["Insurance", "Payment_Status"]).size().reset_index(name="Count")
    fig = px.bar(pv, x="Insurance", y="Count", color="Payment_Status", barmode="group")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with st.container(border=True):
    chart_title("Billing Breakdown by Department", icon_name="money")
    bill = f.groupby("Department")[["Consultation_Fee", "Lab_Cost", "Pharmacy_Cost", "Room_Charges"]].sum().reset_index()
    bill_melt = bill.melt(id_vars="Department", var_name="Component", value_name="Amount")
    fig = px.bar(bill_melt, x="Department", y="Amount", color="Component", barmode="stack")
    fig.update_layout(height=340, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

section_title("Raw Visit Records", icon_name="table")
st.dataframe(f.sort_values("Visit_Date", ascending=False), width='stretch', height=350)
