import streamlit as st
import plotly.express as px

from utils.data_loader import get_data_for_page
from utils.kpi import safe_mean
from utils.styling import (
    apply_page_config, section_title, page_header, render_kpi_cards,
    chart_title, render_alerts, gradient_bar, filter_bar,
)
from utils.auth import require_login

require_login()
apply_page_config("Emergency Monitoring")

data = get_data_for_page()
er = data["er"].copy()
visits = data["visits"].copy()

page_header(
    "Emergency (ER) Monitoring",
    "Monthly emergency case load, category mix and admission-type split, "
    "plus live waiting-time signal from patient visits.",
    icon_name="alert",
)

seasons = sorted(er["Season"].dropna().unique().tolist())
cats = sorted(er["Case_Category"].dropna().unique().tolist())
months = sorted(er["YearMonth"].dropna().unique().tolist())

bar = filter_bar()
fc1, fc2, fc3 = bar.columns([1.4, 1.4, 1.6])
with fc1:
    sel_season = st.multiselect("Season", seasons, default=seasons)
with fc2:
    sel_cat = st.multiselect("Case Category", cats, default=cats)
with fc3:
    sel_months = st.select_slider("Month range", options=months, value=(months[0], months[-1]))

f = er[
    (er["Season"].isin(sel_season)) &
    (er["Case_Category"].isin(sel_cat)) &
    (er["YearMonth"] >= sel_months[0]) &
    (er["YearMonth"] <= sel_months[1])
]

if len(f) == 0:
    st.warning("No ER records match the selected filters.")
    st.stop()

er_visits = visits[visits["Admission_Type"] == "Emergency"]
er_wait = safe_mean(er_visits["Waiting_Time_Min"])
wait_tone = "critical" if er_wait >= 45 else "warning" if er_wait >= 30 else "good"

section_title("Key Metrics", icon_name="chart")
kpis = [
    {"label": "Total ER Cases (period)", "value": f"{int(f['Case_Count'].sum()):,}", "icon": "alert", "hero": True,
     "sub": f"{er_wait} min avg ER waiting time"},
    {"label": "Accident / Trauma", "value": f"{int(f[f['Case_Category']=='Accident/Trauma']['Case_Count'].sum()):,}", "icon": "activity"},
    {"label": "Natural / Illness", "value": f"{int(f[f['Case_Category']=='Natural/Illness']['Case_Count'].sum()):,}", "icon": "stethoscope"},
    {"label": "Avg ER Waiting Time", "value": f"{er_wait} min", "icon": "clock", "tone": wait_tone,
     "sub": "Overloaded" if wait_tone == "critical" else ("Trending high" if wait_tone == "warning" else "Within range")},
]
render_kpi_cards(kpis, cols_per_row=4)

if wait_tone == "critical":
    render_alerts([("critical", f"Average Emergency waiting time is {er_wait} min — department is overloaded. Deploy additional doctors/nurses immediately.")])
elif wait_tone == "warning":
    render_alerts([("warning", f"Average Emergency waiting time is {er_wait} min — trending high, keep monitoring.")])
else:
    render_alerts([("good", f"Average Emergency waiting time is {er_wait} min — within acceptable range.")])

st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1, st.container(border=True):
    chart_title("Monthly ER Case Volume", icon_name="trending")
    m = f.groupby("YearMonth")["Case_Count"].sum().reset_index().sort_values("YearMonth")
    fig = px.line(m, x="YearMonth", y="Case_Count", markers=True)
    fig.update_traces(line_color="#0B5FFF")
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col2, st.container(border=True):
    chart_title("Case Category Split", icon_name="chart")
    cat = f.groupby("Case_Category")["Case_Count"].sum().reset_index()
    fig = px.pie(cat, names="Case_Category", values="Case_Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

col3, col4 = st.columns(2)
with col3, st.container(border=True):
    chart_title("Admission Type Split (Emergency Cases)", icon_name="hospital")
    adm = f.groupby("Admission_Type")["Case_Count"].sum().reset_index()
    fig = px.pie(adm, names="Admission_Type", values="Case_Count", hole=0.55)
    fig.update_layout(height=320, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, width='stretch')

with col4, st.container(border=True):
    chart_title("Seasonal Case Load", icon_name="calendar", note="Darker shade = heavier case load")
    season = f.groupby("Season")["Case_Count"].sum().reset_index().sort_values("Case_Count", ascending=False)
    fig = gradient_bar(season, x="Season", y="Case_Count", scale="Blues")
    st.plotly_chart(fig, width='stretch')

# with st.container(border=True):
#     chart_title("Case Category vs Admission Type (by month)", icon_name="chart")
#     pivot = f.pivot_table(index="YearMonth", columns="Case_Category", values="Case_Count", aggfunc="sum").fillna(0)
#     fig = px.imshow(pivot.T, aspect="auto", color_continuous_scale="Blues",
#                      labels=dict(x="Month", y="Case Category", color="Cases"))
#     fig.update_layout(height=340, margin=dict(t=10, l=10, r=10, b=10))
#     st.plotly_chart(fig, width='stretch')

section_title("Raw ER Monitoring Summary", icon_name="table")
st.dataframe(f.sort_values("YearMonth", ascending=False), width='stretch', height=350)
