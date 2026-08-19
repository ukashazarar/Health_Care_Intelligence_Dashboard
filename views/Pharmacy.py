import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import pct
from utils.styling import (
    apply_page_config, section_title, render_alerts, page_header,
    render_kpi_cards, gradient_bar, chart_title, filter_bar,
)
from utils.auth import require_login

require_login()
apply_page_config("Pharmacy")

data = get_data_for_page()
pharmacy = data["pharmacy"].copy()

page_header("Pharmacy Operations", "Medicine dispensing, revenue, category and branch performance.", icon_name="pill")

branches = sorted(pharmacy["Pharmacy Branch"].dropna().unique().tolist())
cats = sorted(pharmacy["Medicine Category"].dropna().unique().tolist())
min_d, max_d = pharmacy["Prescription Date"].min().date(), pharmacy["Prescription Date"].max().date()

bar = filter_bar()
fc1, fc2, fc3 = bar.columns([1.4, 1.4, 1.3])
with fc1:
    sel_branch = st.multiselect("Branch", branches, default=branches)
with fc2:
    sel_cat = st.multiselect("Medicine Category", cats, default=cats)
with fc3:
    dr = st.date_input("Prescription date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(dr, tuple) and len(dr) == 2:
    start_d, end_d = dr
else:
    start_d, end_d = min_d, max_d

f = pharmacy[
    (pharmacy["Pharmacy Branch"].isin(sel_branch)) &
    (pharmacy["Medicine Category"].isin(sel_cat)) &
    (pharmacy["Prescription Date"].dt.date >= start_d) &
    (pharmacy["Prescription Date"].dt.date <= end_d)
]

if len(f) == 0:
    st.warning("No pharmacy records match the selected filters.")
    st.stop()

insurance_rate = pct((f["Insurance Covered"] == "Yes").sum(), len(f))

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Transactions", "value": f"{len(f):,}", "icon": "package", "hero": True,
     "sub": f"{f['Quantity Dispensed'].sum():,} units dispensed"},
    {"label": "Total Revenue", "value": f"\u20b9{f['Net Amount'].sum():,.0f}", "icon": "money"},
    {"label": "Avg Order Value", "value": f"\u20b9{f['Net Amount'].mean():,.0f}", "icon": "card"},
    {"label": "Insurance Covered", "value": f"{insurance_rate}%", "icon": "shield",
     "tone": "good" if insurance_rate >= 50 else "warning"},
    {"label": "Branches Active", "value": f"{f['Pharmacy Branch'].nunique()}", "icon": "briefcase"},
]
render_kpi_cards(kpis, cols_per_row=5)

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Demand intelligence — the dataset has no live stock-on-hand field,
# so we surface dispensing velocity (recent volume in the current
# filter) as a practical proxy for what to reorder soon.
# ---------------------------------------------------------------
section_title("Demand Intelligence", icon_name="alert")
st.caption(
    "This dataset does not include a live inventory column, so instead of a stock-level alert "
    "we surface the fastest-moving medicines by recent dispensing volume — a practical signal "
    "for what to reorder soon."
)
top_demand = f.groupby("Medicine Name")["Quantity Dispensed"].sum().reset_index().sort_values(
    "Quantity Dispensed", ascending=False
).head(10)
alerts = [
    ("warning", f"<b>{row['Medicine Name']}</b> \u2014 {int(row['Quantity Dispensed']):,} units dispensed in the selected period. High-demand item; verify stock levels.")
    for _, row in top_demand.head(3).iterrows()
]
render_alerts(alerts)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly Sales Trend", icon_name="trending")
    m = f.groupby("Month")["Net Amount"].sum().reset_index().sort_values("Month")
    fig = px.area(m, x="Month", y="Net Amount")
    fig.update_traces(line_color="#0B5FFF", fillcolor="rgba(11,95,255,0.10)")
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Medicine Category Share", icon_name="pill")
    cat = f.groupby("Medicine Category")["Net Amount"].sum().reset_index()
    fig = px.pie(cat, names="Medicine Category", values="Net Amount", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Top 10 Medicines by Volume", icon_name="package", note="Darker shade = higher volume")
    fig = gradient_bar(top_demand, x="Medicine Name", y="Quantity Dispensed", orientation="h", scale="Blues")
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Revenue by Branch", icon_name="briefcase", note="Darker shade = higher revenue")
    branch_rev = f.groupby("Pharmacy Branch")["Net Amount"].sum().reset_index().sort_values("Net Amount", ascending=False)
    fig = gradient_bar(branch_rev, x="Pharmacy Branch", y="Net Amount", scale="Teal")
    st.plotly_chart(fig, width='stretch')

with st.container(border=True):
    chart_title("Payment Mode Distribution", icon_name="card", note="Darker shade = more transactions")
    pm = f["Payment Mode"].value_counts().reset_index()
    pm.columns = ["Payment Mode", "Count"]
    fig = gradient_bar(pm, x="Payment Mode", y="Count", scale="Blues")
    st.plotly_chart(fig, width='stretch')

section_title("Raw Pharmacy Records", icon_name="table")
st.dataframe(f.sort_values("Prescription Date", ascending=False), width='stretch', height=350)
