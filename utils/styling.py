"""
styling.py
----------
Shared visual design system so every page of the dashboard looks like one
cohesive, production-grade product: colors, typography, background, the
Plotly theme, a small line-icon set (no emoji), KPI cards, page headers,
insight-driven charts and alert banners.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# ----------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------
PRIMARY = "#0B5FFF"
PRIMARY_DARK = "#0842B0"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
CRITICAL = "#DC2626"
NEUTRAL = "#475569"
MUTED_BAR = "#CBD5E1"
BG_CARD = "#FFFFFF"

CHART_COLORWAY = ["#0B5FFF", "#16A34A", "#F59E0B", "#DC2626", "#7C3AED",
                   "#0891B2", "#DB2777", "#65A30D", "#EA580C", "#4338CA"]

TONE_COLOR = {"default": PRIMARY, "good": SUCCESS, "warning": WARNING, "critical": CRITICAL}

# ----------------------------------------------------------------------
# Minimal line-icon set (hand-built, stroke-based — no emoji, no external
# icon font/CDN dependency). Referenced by name across every page.
# ----------------------------------------------------------------------
_ICON_BODY = {
    "hospital": '<rect x="4" y="7" width="16" height="13" rx="1"></rect><path d="M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"></path><line x1="12" y1="11" x2="12" y2="16"></line><line x1="9.5" y1="13.5" x2="14.5" y2="13.5"></line>',
    "bed": '<path d="M3 18v-7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v7"></path><path d="M3 18v2"></path><path d="M21 18v2"></path><path d="M3 13h18"></path><circle cx="7" cy="10" r="1"></circle>',
    "clock": '<circle cx="12" cy="12" r="9"></circle><polyline points="12 7 12 12 15.5 14"></polyline>',
    "alert": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>',
    "repeat": '<polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path>',
    "smile": '<circle cx="12" cy="12" r="9"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line>',
    "calendar": '<rect x="3" y="4" width="18" height="17" rx="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>',
    "activity": '<polyline points="2 12 6 12 9 20 14 4 17 12 22 12"></polyline>',
    "money": '<circle cx="12" cy="12" r="9"></circle><path d="M9 8h6M9 11.5h6M10.5 8c2.8 0 2.8 3.5 0 3.5H10l4 4.5"></path>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"></path><circle cx="10" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M17 3.13a4 4 0 0 1 0 7.75"></path>',
    "pill": '<path d="M4.5 4.5a4.95 4.95 0 0 1 7 0l8 8a4.95 4.95 0 1 1-7 7l-8-8a4.95 4.95 0 0 1 0-7Z"></path><line x1="9" y1="9" x2="14.5" y2="14.5"></line>',
    "flask": '<path d="M9 2h6"></path><path d="M9 2v6L4 18a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3L15 8V2"></path><line x1="7" y1="15" x2="17" y2="15"></line>',
    "ambulance": '<rect x="1" y="9" width="14" height="9"></rect><path d="M15 12h3l3 3v3h-6z"></path><circle cx="6" cy="19" r="1.5"></circle><circle cx="17" cy="19" r="1.5"></circle><line x1="6" y1="12" x2="6" y2="16"></line><line x1="4" y1="14" x2="8" y2="14"></line>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path><line x1="2" y1="13" x2="22" y2="13"></line>',
    "trending": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline>',
    "package": '<path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"></path><polyline points="3 8 12 13 21 8"></polyline><line x1="12" y1="13" x2="12" y2="21"></line>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"></rect><line x1="2" y1="9" x2="22" y2="9"></line>',
    "stethoscope": '<path d="M4.5 3v6a4.5 4.5 0 0 0 9 0V3"></path><path d="M9 15a6 6 0 0 0 12 0v-2"></path><circle cx="21" cy="11" r="2"></circle>',
    "chart": '<line x1="4" y1="20" x2="20" y2="20"></line><rect x="6" y="12" width="3" height="6"></rect><rect x="11" y="8" width="3" height="10"></rect><rect x="16" y="4" width="3" height="14"></rect>',
    "shield": '<path d="M12 2 4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5z"></path>',
    "check-circle": '<circle cx="12" cy="12" r="9"></circle><polyline points="8 12 11 15 16 9"></polyline>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V7a4 4 0 0 1 8 0v4"></path>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line>',
    "table": '<rect x="3" y="4" width="18" height="16" rx="1"></rect><line x1="3" y1="10" x2="21" y2="10"></line><line x1="9" y1="4" x2="9" y2="20"></line>',
    "tune": '<line x1="4" y1="6" x2="20" y2="6"></line><circle cx="9" cy="6" r="2"></circle><line x1="4" y1="12" x2="20" y2="12"></line><circle cx="15" cy="12" r="2"></circle><line x1="4" y1="18" x2="20" y2="18"></line><circle cx="7" cy="18" r="2"></circle>',
    "dot": '<circle cx="12" cy="12" r="4"></circle>',
}


def icon_svg(name: str, size: int = 18, color: str = "currentColor", stroke_width: float = 2) -> str:
    """Return an inline <svg> string for a named icon (professional, stroke-based)."""
    body = _ICON_BODY.get(name, _ICON_BODY["dot"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-4px; display:inline-block;">{body}</svg>'
    )


# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
def apply_page_config(title: str, icon_name: str = "hospital"):
    st.set_page_config(page_title=f"{title} | Medical Operation Intelligence", page_icon="logo.png", layout="wide")
    _inject_css()
    _set_plotly_theme()


def _set_plotly_theme():
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif", size=13, color="#1E293B"),
        colorway=CHART_COLORWAY,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=50, l=10, r=10, b=10),
        xaxis=dict(gridcolor="#E2E8F0", zeroline=False),
        yaxis=dict(gridcolor="#E2E8F0", zeroline=False),
    )
    pio.templates["hospital"] = template
    pio.templates.default = "hospital"


# def _inject_css():
#     st.markdown(
#         """
#         <style>
#         @keyframes fadeInUp {
#             from { opacity: 0; transform: translateY(8px); }
#             to   { opacity: 1; transform: translateY(0); }
#         }

#         /* ---- App background: subtle, professional, non-distracting ---- */
#         .stApp {
#             background:
#                 radial-gradient(circle at 15% 0%, rgba(11,95,255,0.05) 0%, rgba(11,95,255,0) 45%),
#                 radial-gradient(circle at 100% 20%, rgba(3,105,161,0.05) 0%, rgba(3,105,161,0) 40%),
#                 #F7F9FC;
#         }
#         .block-container {padding-top: 1.6rem; padding-bottom: 3rem;}

#         div[data-testid="stMetric"] {
#             background: #FFFFFF;
#             border: 1px solid #E2E8F0;
#             border-radius: 12px;
#             padding: 14px 18px 10px 18px;
#             box-shadow: 0 1px 2px rgba(0,0,0,0.04);
#         }
#         div[data-testid="stMetricLabel"] { font-weight: 600; color: #475569; }

#         /* ---- Alerts ---- */
#         .alert-box {
#             border-radius: 10px;
#             padding: 12px 16px;
#             margin-bottom: 8px;
#             font-size: 0.92rem;
#             border-left: 5px solid;
#             display: flex; align-items: center; gap: 10px;
#             animation: fadeInUp 0.35s ease both;
#         }
#         .alert-critical { background:#FEF2F2; border-color:#DC2626; color:#7F1D1D; }
#         .alert-warning  { background:#FFFBEB; border-color:#F59E0B; color:#78350F; }
#         .alert-good     { background:#F0FDF4; border-color:#16A34A; color:#14532D; }

#         .section-title {
#             font-size: 1.1rem; font-weight: 700; color:#0F172A;
#             margin-top: 0.6rem; margin-bottom: 0.7rem;
#             display:flex; align-items:center; gap:8px;
#             border-left: 4px solid #0B5FFF; padding-left: 10px;
#         }
#         .section-title svg { color:#0B5FFF; }

#         /* ---- Page header banner ---- */
#         .dash-header {
#             background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0369a1 100%);
#             padding: 1.7rem 2rem; border-radius: 16px; color: white;
#             box-shadow: 0 10px 25px -5px rgba(0,0,0,0.25); margin-bottom: 1.6rem;
#             animation: fadeInUp 0.4s ease both;
#             position: relative; overflow: hidden;
#         }
#         .dash-header::after {
#             content: ""; position: absolute; inset: 0;
#             background: radial-gradient(circle at 90% -10%, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 55%);
#             pointer-events: none;
#         }
#         .dash-header h1 {
#             color:#fff !important; font-size:1.55rem !important; font-weight:700 !important;
#             margin-bottom:0.3rem !important; display:flex; align-items:center; gap:10px;
#         }
#         .dash-header p { color:#94a3b8 !important; font-size:0.92rem !important; margin-bottom:0 !important; }
#         .header-badge {
#             background: rgba(255,255,255,0.13); backdrop-filter: blur(8px);
#             padding:0.32rem 0.8rem; border-radius:20px; font-size:0.78rem; color:#e2e8f0;
#             border:1px solid rgba(255,255,255,0.18); display:inline-flex; align-items:center; gap:6px;
#             margin-top:0.7rem; margin-right:0.5rem;
#         }

#         /* ---- KPI cards ---- */
#         .kpi-card {
#             background:#fff; border:1px solid #e2e8f0; border-radius:14px;
#             padding:0.95rem 1.1rem; height:100%;
#             box-shadow:0 2px 4px rgba(0,0,0,0.04);
#             transition: transform .15s ease, box-shadow .15s ease;
#             animation: fadeInUp 0.35s ease both;
#         }
#         .kpi-card:hover { transform: translateY(-3px); box-shadow:0 10px 18px -6px rgba(15,23,42,0.14); }
#         .kpi-header { display:flex; align-items:center; justify-content:space-between;
#             color:#64748b; font-size:0.74rem; font-weight:700; text-transform:uppercase;
#             letter-spacing:0.4px; margin-bottom:0.5rem; }
#         .kpi-value { color:#0f172a; font-size:1.45rem; font-weight:800; line-height:1.15; }
#         .kpi-sub { margin-top:0.35rem; font-size:0.76rem; font-weight:600; }
#         .kpi-icon-wrap {
#             width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center;
#             flex-shrink: 0;
#         }
#         .kpi-hero { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); }
#         .kpi-hero .kpi-value { font-size:1.85rem; }

#         /* ---- Chart card wrapper (via st.container(border=True)) ---- */
#         div[data-testid="stVerticalBlockBorderWrapper"] {
#             border-radius: 14px !important;
#         }
#         div[data-testid="stVerticalBlockBorderWrapper"]:has(div.chart-card-tag) {
#             animation: fadeInUp 0.35s ease both;
#         }
#         .chart-title { font-weight:700; color:#0f172a; font-size:0.95rem; margin-bottom:0.3rem;
#             display:flex; align-items:center; gap:8px; }
#         .chart-title svg { color:#0B5FFF; }
#         .chart-note { color:#64748b; font-size:0.78rem; margin-bottom:0.4rem; }

#         /* ---- Sidebar polish ---- */
#         /* ---- Sidebar polish ---- */
#         section[data-testid="stSidebar"] {
#             background: linear-gradient(180deg, #0f172a 0%, #111827 100%) !important;
#         }
#         section[data-testid="stSidebar"] * { 
#             color: #e2e8f0 !important; 
#         }

#         /* Sidebar Buttons (Log Out Button Fix) */
#         section[data-testid="stSidebar"] button {
#             background-color: #1e293b !important;
#             color: #ffffff !important;
#             border: 1px solid #334155 !important;
#             border-radius: 8px !important;
#             font-weight: 500 !important;
#             transition: all 0.2s ease-in-out !important;
#         }
#         section[data-testid="stSidebar"] button:hover {
#             background-color: #334155 !important;
#             border-color: #38bdf8 !important;
#             color: #38bdf8 !important;
#         }

#         /* Sidebar File Upload Area Fix */
#         section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"] {
#             background-color: #1e293b !important;
#             border: 1px dashed #475569 !important;
#             border-radius: 10px !important;
#         }
#         section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"] * {
#             color: #94a3b8 !important;
#         }
#         section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"]:hover {
#             border-color: #38bdf8 !important;
#             background-color: #0f172a !important;
#         }

#         /* Input fields and dropdowns in sidebar */
#         section[data-testid="stSidebar"] input, 
#         section[data-testid="stSidebar"] textarea {
#             background-color: #1e293b !important;
#             color: #ffffff !important;
#             border: 1px solid #334155 !important;
#             border-radius: 6px !important;
#         }
#         """,
#         unsafe_allow_html=True,
#     )



def _inject_css():
    st.markdown(
        """
        <style>
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ---- App background ---- */
        .stApp {
            background:
                radial-gradient(circle at 15% 0%, rgba(11,95,255,0.05) 0%, rgba(11,95,255,0) 45%),
                radial-gradient(circle at 100% 20%, rgba(3,105,161,0.05) 0%, rgba(3,105,161,0) 40%),
                #F7F9FC;
        }
        .block-container {padding-top: 1.6rem; padding-bottom: 3rem;}

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 14px 18px 10px 18px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetricLabel"] { font-weight: 600; color: #475569; }

        /* ---- Alerts ---- */
        .alert-box {
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 8px;
            font-size: 0.92rem;
            border-left: 5px solid;
            display: flex; align-items: center; gap: 10px;
            animation: fadeInUp 0.35s ease both;
        }
        .alert-critical { background:#FEF2F2; border-color:#DC2626; color:#7F1D1D; }
        .alert-warning  { background:#FFFBEB; border-color:#F59E0B; color:#78350F; }
        .alert-good     { background:#F0FDF4; border-color:#16A34A; color:#14532D; }

        .section-title {
            font-size: 1.1rem; font-weight: 700; color:#0F172A;
            margin-top: 0.6rem; margin-bottom: 0.7rem;
            display:flex; align-items:center; gap:8px;
            border-left: 4px solid #0B5FFF; padding-left: 10px;
        }
        .section-title svg { color:#0B5FFF; }

        /* ---- Page header banner ---- */
        .dash-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0369a1 100%);
            padding: 1.7rem 2rem; border-radius: 16px; color: white;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.25); margin-bottom: 1.6rem;
            animation: fadeInUp 0.4s ease both;
            position: relative; overflow: hidden;
        }
        .dash-header::after {
            content: ""; position: absolute; inset: 0;
            background: radial-gradient(circle at 90% -10%, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 55%);
            pointer-events: none;
        }
        .dash-header h1 {
            color:#fff !important; font-size:1.55rem !important; font-weight:700 !important;
            margin-bottom:0.3rem !important; display:flex; align-items:center; gap:10px;
        }
        .dash-header p { color:#94a3b8 !important; font-size:0.92rem !important; margin-bottom:0 !important; }
        .header-badge {
            background: rgba(255,255,255,0.13); backdrop-filter: blur(8px);
            padding:0.32rem 0.8rem; border-radius:20px; font-size:0.78rem; color:#e2e8f0;
            border:1px solid rgba(255,255,255,0.18); display:inline-flex; align-items:center; gap:6px;
            margin-top:0.7rem; margin-right:0.5rem;
        }

        /* ---- KPI cards ---- */
        .kpi-card {
            background:#fff; border:1px solid #e2e8f0; border-radius:14px;
            padding:0.95rem 1.1rem; height:100%;
            box-shadow:0 2px 4px rgba(0,0,0,0.04);
            transition: transform .15s ease, box-shadow .15s ease;
            animation: fadeInUp 0.35s ease both;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow:0 10px 18px -6px rgba(15,23,42,0.14); }
        .kpi-header { display:flex; align-items:center; justify-content:space-between;
            color:#64748b; font-size:0.74rem; font-weight:700; text-transform:uppercase;
            letter-spacing:0.4px; margin-bottom:0.5rem; }
        .kpi-value { color:#0f172a; font-size:1.45rem; font-weight:800; line-height:1.15; }
        .kpi-sub { margin-top:0.35rem; font-size:0.76rem; font-weight:600; }
        .kpi-icon-wrap {
            width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center;
            flex-shrink: 0;
        }
        .kpi-hero { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); }
        .kpi-hero .kpi-value { font-size:1.85rem; }

        /* ---- Chart card wrapper ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.chart-card-tag) {
            animation: fadeInUp 0.35s ease both;
        }
        .chart-title { font-weight:700; color:#0f172a; font-size:0.95rem; margin-bottom:0.3rem;
            display:flex; align-items:center; gap:8px; }
        .chart-title svg { color:#0B5FFF; }
        .chart-note { color:#64748b; font-size:0.78rem; margin-bottom:0.4rem; }

        /* ---- Sidebar Deep Dark Theme Override ---- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%) !important;
        }
        section[data-testid="stSidebar"] * { 
            color: #f8fafc !important; 
        }

        /* 1. Admin Text / Badge Fix */
        section[data-testid="stSidebar"] code,
        section[data-testid="stSidebar"] span[data-testid="stBadge"] {
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            border: 1px solid #334155 !important;
            font-weight: 600 !important;
        }

        /* 2. Log Out Button Box Styling */
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            width: 100% !important;
            transition: all 0.2s ease-in-out !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: #334155 !important;
            border-color: #38bdf8 !important;
            color: #38bdf8 !important;
        }

        /* 3. Data Source / File Uploader Complete Dark Box */
        /* 3. Data Source / File Uploader Complete Dark Box */
        section[data-testid="stSidebar"] div[data-testid="stFileUploader"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 12px !important;
        }

        /* Target all child wrappers, dropzone, and inner sections to eliminate white background */
        section[data-testid="stSidebar"] div[data-testid="stFileUploader"] *,
        section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"],
        section[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] > div {
            background-color: #0f172a !important;
            color: #ffffff !important;
        }

        /* Custom style for the dropzone border */
        section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"] {
            border: 1px dashed #475569 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            border-radius: 6px !important;
        }

        /* Upload button inside the dropzone */
        section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"] button {
            background-color: #334155 !important;
            color: #ffffff !important;
            border: 1px solid #475569 !important;
            border-radius: 6px !important;
        }

        /* Hover effect for upload button */
        section[data-testid="stSidebar"] section[data-testid="stFileUploadDropzone"] button:hover {
            # background-color: #475569 !important;
            border-color: #38bdf8 !important;
            color: #38bdf8 !important;
        }

        /* Subtext / Small caption text */
        section[data-testid="stSidebar"] small {
            color: #94a3b8 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, badges=None, icon_name: str = "hospital"):
    """Gradient hero banner used at the top of every page."""
    badges_html = "".join(f'<span class="header-badge">{b}</span>' for b in (badges or []))
    st.markdown(
        f"""
        <div class="dash-header">
            <h1>{icon_svg(icon_name, size=24, color="#ffffff")} {title}</h1>
            <p>{subtitle}</p>
            <div>{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(items, cols_per_row: int = 4):
    """
    Render a clean, professional KPI grid.
    items: list of dicts, each with:
        label (str), value (str), icon (str, optional icon name),
        hero (bool, optional) -> visually emphasized "north star" metric,
        tone ("default"|"good"|"warning"|"critical", optional) -> accent color,
        sub (str, optional) -> small caption line (e.g. trend / context)
    Keep this list to 5-7 items: the most decision-relevant metrics only.
    """
    for row_start in range(0, len(items), cols_per_row):
        row = items[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, row):
            tone = item.get("tone", "default")
            accent = TONE_COLOR.get(tone, PRIMARY)
            hero = item.get("hero", False)
            card_class = "kpi-card kpi-hero" if hero else "kpi-card"
            sub_html = f'<div class="kpi-sub" style="color:{accent};">{item["sub"]}</div>' if item.get("sub") else ""
            icon_html = ""
            if item.get("icon"):
                icon_html = (
                    f'<span class="kpi-icon-wrap" style="background:{accent}1A;">'
                    f'{icon_svg(item["icon"], size=16, color=accent)}</span>'
                )
            with col:
                st.markdown(
                    f"""
                    <div class="{card_class}" style="border-top:4px solid {accent};">
                        <div class="kpi-header"><span>{item['label']}</span>{icon_html}</div>
                        <div class="kpi-value">{item['value']}</div>
                        {sub_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def gradient_bar(df: pd.DataFrame, x: str, y: str, orientation: str = "v",
                  scale: str = "Blues", height: int = 320, value_suffix: str = ""):
    """
    Build a bar chart where every bar is shaded along a smooth color gradient
    driven by its own value (darker/more saturated = higher) — so the trend
    is visible at a glance from color alone, not just bar length. Mirrors the
    'color=value, color_continuous_scale=...' pattern used elsewhere in the
    hospital's BI tooling, kept as the house style for ranking/volume charts.

    scale: any Plotly continuous scale name, e.g. "Blues", "Teal", "Purples",
           "Oranges", "Greens".
    """
    d = df.reset_index(drop=True)
    text_fmt = "%{text:,.0f}" + value_suffix

    if orientation == "h":
        fig = px.bar(
            d, x=y, y=x, orientation="h",
            color=y, color_continuous_scale=scale, text=y,
        )
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    else:
        fig = px.bar(
            d, x=x, y=y,
            color=y, color_continuous_scale=scale, text=y,
        )

    fig.update_traces(
        texttemplate=text_fmt, textposition="outside",
        marker_line_width=0, cliponaxis=False,
    )
    fig.update_layout(
        showlegend=False, coloraxis_showscale=False, height=height,
        margin=dict(t=25, l=10, r=10, b=10), uniformtext_minsize=10,
    )
    return fig


def insight_bar(df: pd.DataFrame, x: str, y: str, orientation: str = "v",
                 highlight: str = "max", height: int = 320, value_suffix: str = ""):
    """
    Build a bar chart that draws the eye to the single most important bar
    (the highest or lowest value) by coloring it with the brand accent and
    muting every other bar to grey — turns a "flat" bar chart into an
    at-a-glance insight instead of a wall of same-colored bars.

    highlight: "max" | "min" | None (None = brand-colored, no highlight)
    """
    d = df.reset_index(drop=True)
    colors = [MUTED_BAR] * len(d)
    if highlight in ("max", "min") and len(d) > 0:
        pos = d[y].idxmax() if highlight == "max" else d[y].idxmin()
        colors[pos] = PRIMARY
    elif highlight is None:
        colors = [PRIMARY] * len(d)

    text = [f"{v:,.0f}{value_suffix}" for v in d[y]]

    if orientation == "h":
        fig = go.Figure(go.Bar(
            x=d[y], y=d[x], orientation="h",
            marker_color=colors, text=text, textposition="outside",
        ))
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    else:
        fig = go.Figure(go.Bar(
            x=d[x], y=d[y],
            marker_color=colors, text=text, textposition="outside",
        ))

    fig.update_traces(marker_line_width=0, cliponaxis=False)
    fig.update_layout(
        showlegend=False, height=height,
        margin=dict(t=25, l=10, r=10, b=10),
        uniformtext_minsize=10,
    )
    return fig


def render_alerts(alerts):
    """alerts: list of (level, message) tuples."""
    icon_for_level = {"critical": ("alert", CRITICAL), "warning": ("alert", WARNING), "good": ("check-circle", SUCCESS)}
    for level, msg in alerts:
        name, color = icon_for_level.get(level, ("dot", NEUTRAL))
        st.markdown(
            f'<div class="alert-box alert-{level}">{icon_svg(name, size=16, color=color)} {msg}</div>',
            unsafe_allow_html=True,
        )


def section_title(text: str, icon_name: str = None):
    icon_html = icon_svg(icon_name, size=18) if icon_name else ""
    st.markdown(f'<div class="section-title">{icon_html}{text}</div>', unsafe_allow_html=True)


def chart_title(text: str, icon_name: str = None, note: str = None):
    """Small heading + optional note used inside a bordered chart container."""
    st.markdown('<span class="chart-card-tag" style="display:none;"></span>', unsafe_allow_html=True)
    icon_html = icon_svg(icon_name, size=16) if icon_name else ""
    st.markdown(f'<div class="chart-title">{icon_html}{text}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="chart-note">{note}</div>', unsafe_allow_html=True)


def filter_bar():
    """
    Open a bordered 'Filters' card at the top of the page (instead of the
    sidebar) and return a live st.container to place filter widgets in via
    st.columns(...). Usage:

        with filter_bar() as bar:
            c1, c2, c3 = bar.columns(3)
            with c1: dept = st.multiselect(...)
    """
    box = st.container(border=True)
    with box:
        chart_title("Filters", icon_name="tune")
    return box
