import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import pct
from utils.styling import (
    apply_page_config, section_title, page_header, render_kpi_cards,
    gradient_bar, chart_title, filter_bar,
)
from utils.auth import require_login

require_login()
apply_page_config("Laboratory")

data = get_data_for_page()
lab = data["lab"].copy()

page_header("Laboratory Operations", "Test volumes, revenue, categories and insurance coverage across the lab.", icon_name="flask")

cats = sorted(lab["Test Category"].dropna().unique().tolist())
min_d, max_d = lab["Test Date"].min().date(), lab["Test Date"].max().date()

bar = filter_bar()
fc1, fc2 = bar.columns([2, 1.3])
with fc1:
    sel_cat = st.multiselect("Test Category", cats, default=cats)
with fc2:
    dr = st.date_input("Test date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = lab[
    (lab["Test Category"].isin(sel_cat)) &
    (lab["Test Date"].dt.date >= start_d) &
    (lab["Test Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No lab records match the selected filters.")
    st.stop()

insurance_rate = pct((f["Insurance Covered"] == "Yes").sum(), len(f))

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Total Tests", "value": f"{len(f):,}", "icon": "flask", "hero": True,
     "sub": f"\u20b9{f['Net Amount'].sum():,.0f} total revenue"},
    {"label": "Avg Test Cost", "value": f"\u20b9{f['Test Cost'].mean():,.0f}", "icon": "money"},
    {"label": "Avg Discount", "value": f"\u20b9{f['Discount Amount'].mean():,.0f}", "icon": "card"},
    {"label": "Insurance Covered", "value": f"{insurance_rate}%", "icon": "shield",
     "tone": "good" if insurance_rate >= 50 else "warning"},
    {"label": "Technicians Active", "value": f"{f['Lab Technician'].nunique()}", "icon": "users"},
]
render_kpi_cards(kpis, cols_per_row=5)

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Test Volume", icon_name="trending")
    m = f.groupby("Month").size().reset_index(name="Tests").sort_values("Month")
    fig = px.area(m, x="Month", y="Tests")
    fig.update_traces(line_color="#0B5FFF", fillcolor="rgba(11,95,255,0.10)")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Test Category Share", icon_name="flask")
    cat = f["Test Category"].value_counts().reset_index()
    cat.columns = ["Category", "Count"]
    fig = px.pie(cat, names="Category", values="Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Top 10 Tests by Volume", icon_name="package", note="Darker shade = higher volume")
    top_tests = f["Test Name"].value_counts().head(10).reset_index()
    top_tests.columns = ["Test Name", "Count"]
    fig = gradient_bar(top_tests, x="Test Name", y="Count", orientation="h", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Revenue by Test Category", icon_name="money", note="Darker shade = higher revenue")
    rev = f.groupby("Test Category")["Net Amount"].sum().reset_index().sort_values("Net Amount", ascending=False)
    fig = gradient_bar(rev, x="Test Category", y="Net Amount", scale="Teal")
    st.plotly_chart(fig, width='stretch')

with st.container(border=True):
    chart_title("Lab Technician Workload (Top 15)", icon_name="users", note="Darker shade = heavier workload")
    tech = f["Lab Technician"].value_counts().head(15).reset_index()
    tech.columns = ["Technician", "Tests Handled"]
    fig = gradient_bar(tech, x="Technician", y="Tests Handled", scale="Blues")
    st.plotly_chart(fig, width='stretch')

section_title("Raw Lab Records", icon_name="table")
st.dataframe(f.sort_values("Test Date", ascending=False), width='stretch', height=350)
