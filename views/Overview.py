"""
views/Overview.py
-----------------
Health Care Operation Intelligence Dashboard — Main Overview page.
"""

from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_all_data, get_global_date_bounds, DEFAULT_DATA_PATH
from utils.kpi import overview_kpis, generate_alerts
from utils.styling import (
    apply_page_config, render_alerts, section_title, page_header,
    render_kpi_cards, gradient_bar, chart_title, icon_svg, filter_bar, PRIMARY,
)
from utils.pdf_generator import generate_pdf_report

apply_page_config("Overview")

# ----------------------------------------------------------------------
# Sidebar — Data Source & Reports
# ----------------------------------------------------------------------
st.sidebar.subheader("Data Source")
uploaded = st.sidebar.file_uploader("Upload hospital dataset (.xlsx)", type=["xlsx"])
if uploaded is not None:
    try:
        data = load_all_data(file_bytes=uploaded.getvalue())
        st.sidebar.success("Custom dataset loaded.")
    except Exception as e:
        st.sidebar.error(f"Could not read file: {e}")
        st.stop()
else:
    if not DEFAULT_DATA_PATH.exists():
        st.error(
            "No dataset found. Please upload the hospital Excel dataset from the "
            "sidebar, or place it at `data/Hospital_Dataset_Complete_Project.xlsx`."
        )
        st.stop()
    data = load_all_data(file_path=str(DEFAULT_DATA_PATH))

# Make loaded dataset available across session so every other page reuses it.
st.session_state["data"] = data

st.sidebar.divider()

# --- PDF Report Download Section in Sidebar ---
st.sidebar.subheader("Reports")
pdf_bytes = generate_pdf_report(st.session_state.get("kpi_data", None))
st.sidebar.download_button(
    label="Download Analysis PDF",
    data=pdf_bytes,
    file_name=f"Healthcare_Intelligence_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
    mime="application/pdf",
    use_container_width=True,
)

st.sidebar.divider()
st.sidebar.caption("Built with Python · Pandas · Plotly · Streamlit")

# ----------------------------------------------------------------------
# 1. Header Placeholder (Reserves space at the very top)
# ----------------------------------------------------------------------
header_placeholder = st.empty()

# ----------------------------------------------------------------------
# 2. Top Filter Bar Layout & Data Calculations
# ----------------------------------------------------------------------
min_date, max_date = get_global_date_bounds(data)
departments = sorted(data["visits"]["Department"].dropna().unique().tolist())

bar = filter_bar()
fc1, fc2 = bar.columns([1.3, 2])
with fc1:
    date_range = st.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
with fc2:
    selected_depts = st.multiselect("Department", departments, default=departments)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# ----------------------------------------------------------------------
# 3. Inject Header into Placeholder (Now variables exist safely!)
# ----------------------------------------------------------------------
with header_placeholder:
    page_header(
        "Health Care Operation Intelligence Dashboard",
        "Hospital-wide performance analytics & operational decision support",
        icon_name="hospital",
        badges=[
            f"{icon_svg('calendar', size=13, color='#e2e8f0')} {start_date.strftime('%d %b %Y')} \u2013 {end_date.strftime('%d %b %Y')}",
            f"{icon_svg('users', size=13, color='#e2e8f0')} {len(selected_depts)}/{len(departments)} departments selected",
            f"{icon_svg('check-circle', size=13, color='#4ADE80')} Live data",
        ],
    )

# ----------------------------------------------------------------------
# Apply Filters
# ----------------------------------------------------------------------
def _in_range(df, col, start, end):
    return df[(df[col].dt.date >= start) & (df[col].dt.date <= end)]

visits = _in_range(data["visits"], "Visit_Date", start_date, end_date)
if selected_depts:
    visits = visits[visits["Department"].isin(selected_depts)]

appointments = _in_range(data["appointments"], "Appointment_Date", start_date, end_date)
ot = _in_range(data["ot"], "OT_Date", start_date, end_date)
ambulance = _in_range(data["ambulance"], "Call_Date", start_date, end_date)
staff = _in_range(data["staff"], "Date", start_date, end_date)
pharmacy = _in_range(data["pharmacy"], "Prescription Date", start_date, end_date)
lab = _in_range(data["lab"], "Test Date", start_date, end_date)

if len(visits) == 0:
    st.warning("No data in the selected filters. Please widen the date range or department selection.")
    st.stop()

# ----------------------------------------------------------------------
# KPI Cards — curated to the 7 metrics that actually drive decisions
# ----------------------------------------------------------------------
k = overview_kpis(visits, ot, appointments, staff, pharmacy, lab)
st.session_state["kpi_data"] = k  # Session memory update for report

section_title("Executive KPIs", icon_name="chart")

bed_tone = "critical" if k["bed_occupancy"] >= 90 else "warning" if k["bed_occupancy"] >= 75 else "good"
wait_tone = "critical" if k["er_avg_wait"] >= 45 else "warning" if k["er_avg_wait"] >= 30 else "good"
readmit_tone = "critical" if k["readmission_rate"] >= 15 else "warning" if k["readmission_rate"] >= 10 else "good"
sat_tone = "critical" if k["avg_satisfaction"] < 3 else "warning" if k["avg_satisfaction"] < 3.8 else "good"

kpis = [
    {  # Hero metric — the single most important "north star" number
        "label": "Total Revenue", "value": f"\u20b9{k['total_revenue']/1e7:,.2f} Cr", "icon": "money",
        "hero": True, "sub": f"{k['total_patients']:,} patients served",
    },
    {"label": "Bed Occupancy", "value": f"{k['bed_occupancy']}%", "icon": "bed", "tone": bed_tone,
     "sub": "Near capacity" if bed_tone == "critical" else ("Watch closely" if bed_tone == "warning" else "Healthy")},
    {"label": "ER Avg Wait", "value": f"{k['er_avg_wait']} min", "icon": "alert", "tone": wait_tone,
     "sub": "Overloaded" if wait_tone == "critical" else ("Trending high" if wait_tone == "warning" else "On target")},
    {"label": "Readmission Rate", "value": f"{k['readmission_rate']}%", "icon": "repeat", "tone": readmit_tone,
     "sub": "Review discharge process" if readmit_tone == "critical" else "Within range"},
    {"label": "Avg Satisfaction", "value": f"{k['avg_satisfaction']} / 5", "icon": "smile", "tone": sat_tone,
     "sub": "Needs attention" if sat_tone == "critical" else "Stable"},
    {"label": "Avg Length of Stay", "value": f"{k['avg_los']} days", "icon": "calendar", "tone": "default"},
    {"label": "OT Cases", "value": f"{k['ot_total']:,}", "icon": "stethoscope", "tone": "default",
     "sub": f"{k['ot_cancelled_rate']}% cancelled"},
]
render_kpi_cards(kpis, cols_per_row=4)

st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Alerts / Intelligence
# ----------------------------------------------------------------------
section_title("Intelligence & Alerts", icon_name="alert")
dept_load = (
    visits.groupby("Department").size().reset_index(name="Patients").sort_values("Patients", ascending=False)
)
alerts = generate_alerts(k, dept_load)
render_alerts(alerts)

st.divider()

# ----------------------------------------------------------------------
# Trends & Visuals
# ----------------------------------------------------------------------
section_title("Visual Analytics", icon_name="chart")

col_a, col_b = st.columns(2)

with col_a, st.container(border=True):
    chart_title("Patient Volume Trend", icon_name="trending")
    monthly = visits.groupby("Month").size().reset_index(name="Patients").sort_values("Month")
    fig = px.line(monthly, x="Month", y="Patients", markers=True)
    fig.update_traces(line_color=PRIMARY, fill="tozeroy", fillcolor="rgba(11,95,255,0.08)")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=320)
    st.plotly_chart(fig, width='stretch')

with col_b, st.container(border=True):
    chart_title("Patient Load by Department", icon_name="hospital", note="Darker shade = higher patient volume")
    fig = gradient_bar(dept_load, x="Department", y="Patients", scale="Blues")
    st.plotly_chart(fig, width='stretch')

col_c, col_d = st.columns(2)

with col_c, st.container(border=True):
    chart_title("Admission Type Split", icon_name="stethoscope")
    admit = visits["Admission_Type"].value_counts().reset_index()
    admit.columns = ["Admission_Type", "Count"]
    
    # Sort for smooth gradient shading (Higher count = Darker Blue)
    admit = admit.sort_values("Count", ascending=False)
    blue_palette = ["#003FB5", "#316AC4", "#5996E0", "#93C5FD", "#BFDBFE"]
    
    fig = px.pie(
        admit, names="Admission_Type", values="Count", hole=0.55,
        color_discrete_sequence=blue_palette
    )
    fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#ffffff", width=1.5)))
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=320, showlegend=False)
    st.plotly_chart(fig, width='stretch')

with col_d, st.container(border=True):
    chart_title("Revenue Composition", icon_name="money")
    revenue_mix = pd.DataFrame({
        "Source": ["Visits (Consult/Room)", "Pharmacy", "Laboratory"],
        "Revenue": [
            visits["Total_Bill"].sum(),
            pharmacy["Net Amount"].sum(),
            lab["Net Amount"].sum(),
        ],
    }).sort_values("Revenue", ascending=False)
    
    rev_palette = ["#003FB5", "#316AC4", "#5996E0"]
    
    fig = px.pie(
        revenue_mix, names="Source", values="Revenue", hole=0.55,
        color_discrete_sequence=rev_palette
    )
    fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#ffffff", width=1.5)))
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=320, showlegend=False)
    st.plotly_chart(fig, width='stretch')

col_e, col_f = st.columns(2)

with col_e, st.container(border=True):
    chart_title("Bed Status", icon_name="bed")
    bed = visits["Bed_Status"].value_counts().reset_index()
    bed.columns = ["Bed_Status", "Count"]
    
    # Highest bed share gets the primary dark blue, lower gets the lighter shade
    bed = bed.sort_values("Count", ascending=False)
    bed_palette = ["#003FB5", "#5996E0"]
    
    fig = px.pie(
        bed, names="Bed_Status", values="Count", hole=0.55,
        color_discrete_sequence=bed_palette
    )
    fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#ffffff", width=1.5)))
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=320, showlegend=False)
    st.plotly_chart(fig, width='stretch')

with col_f, st.container(border=True):
    chart_title("Patient Satisfaction Distribution", icon_name="smile", note="Color intensity tracks response volume")
    sat = visits["Satisfaction_Score"].value_counts().sort_index().reset_index()
    sat.columns = ["Score", "Count"]
    sat["Score"] = sat["Score"].astype(str)
    fig = gradient_bar(sat, x="Score", y="Count", scale="Blues")
    st.plotly_chart(fig, width='stretch')

st.caption(
    "Use the pages in the sidebar (Patient Overview, Laboratory, Pharmacy, Ambulance, "
    "Staff Scheduling, Appointments, OT Dashboard, Emergency Monitoring) for department-level detail."
)