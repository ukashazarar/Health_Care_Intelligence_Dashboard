"""
Home.py
-------
Entry point: authentication gate + sidebar navigation for the
Medical Operation Intelligence Dashboard.
"""

import streamlit as st
from utils.styling import icon_svg

# 1. Page Config (must be called once, at the very top)
st.set_page_config(
    page_title="Hospital Management Portal",
    page_icon="logo.png",
    layout="wide"
)

# 2. Session state for login status
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# -------------------------------------------------------------------
# 🔒 LOGIN SCREEN
# -------------------------------------------------------------------
def show_login_screen():
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarNav"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
            header { visibility: hidden !important; }
            footer { visibility: hidden !important; }

            .stApp {
                background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)),
                           url('https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=2070&auto=format&fit=crop');
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }

            div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.96) !important;
                padding: 2.5rem 2rem 2rem 2rem !important;
                border-radius: 20px !important;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3) !important;
                border: 1px solid rgba(255, 255, 255, 0.4) !important;
                max-width: 420px !important;
                margin: 0 auto !important;
            }

            .stTextInput input {
                border-radius: 10px !important;
                border: 1px solid #cbd5e1 !important;
                padding: 0.6rem 0.8rem !important;
                font-size: 0.95rem !important;
            }
            .stTextInput input:focus {
                border-color: #0284c7 !important;
                box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2) !important;
            }

            div[data-testid="stForm"] button[type="submit"] {
                background-color: #0284c7 !important;
                border-color: #0284c7 !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                padding: 0.6rem 1rem !important;
                margin-top: 0.5rem !important;
                transition: all 0.2s ease-in-out !important;
            }
            div[data-testid="stForm"] button[type="submit"]:hover {
                background-color: #0369a1 !important;
                box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
            }

            .login-title {
                text-align: center;
                color: #ffffff;
                font-size: 1.8rem;
                font-weight: 700;
                letter-spacing: -0.5px;
                margin-bottom: 0.2rem;
            }
            .login-subtitle {
                text-align: center;
                color: #94a3b8;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
            }
            .security-badge {
                text-align: center;
                color: #cbd5e1;
                font-size: 0.78rem;
                margin-top: 1.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

    col_img1, col_img2, col_img3 = st.columns([1, 0.3, 1])
    with col_img2:
        st.image("logo.png", width='stretch')

    st.markdown("""
        <div class="login-title">Health Care Operation Portal</div>
        <div class="login-subtitle">Decision Support & Business Intelligence System</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown(
                f"<h4 style='text-align: center; color: #0f172a; margin-bottom: 1rem;'>"
                f"{icon_svg('lock', size=18, color='#0f172a')} Staff Sign-In</h4>",
                unsafe_allow_html=True,
            )

            username = st.text_input("Username", placeholder="e.g. admin or doctor")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            submit = st.form_submit_button("Sign In to Portal", width='stretch', type="primary")

            if submit:
                # Read credentials safely from Streamlit Secrets
                if "credentials" in st.secrets:
                    stored_credentials = dict(st.secrets["credentials"])
                    if username in stored_credentials and str(password) == str(stored_credentials[username]):
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")
                else:
                    st.error("Authentication configuration missing. Please add credentials to secrets.toml.")

    st.markdown(
        f"""
        <div class="security-badge">
            {icon_svg('shield', size=13, color='#cbd5e1')} Encrypted Enterprise Session &bull; Authorized Personnel Only
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# 🔀 MAIN ROUTER
# -------------------------------------------------------------------
if not st.session_state["authenticated"]:
    show_login_screen()

else:
    # -------------------------------------------------------------------
    # 🔓 DASHBOARD
    # -------------------------------------------------------------------
    # st.sidebar.image("logo.png", width='stretch')
    st.sidebar.markdown(
        f"{icon_svg('users', size=14, color='#0e5dc4')} **Logged in as:** `{st.session_state.get('username')}`",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Log Out", width='stretch', icon=":material/logout:"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.rerun()
    st.sidebar.divider()

    dashboard_pages = [
        st.Page("views/Overview.py", title="Overview & Intelligence", icon=":material/dashboard:", default=True),
        st.Page("views/Patient_Overview.py", title="Patient Overview", icon=":material/groups:"),
        st.Page("views/Ambulance.py", title="Ambulance", icon=":material/emergency:"),
        st.Page("views/Appointments.py", title="Appointments", icon=":material/event_available:"),
        st.Page("views/Emergency_Monitoring.py", title="Emergency Monitoring", icon=":material/monitor_heart:"),
        st.Page("views/Laboratory.py", title="Laboratory", icon=":material/science:"),
        st.Page("views/OT_Dashboard.py", title="OT Dashboard", icon=":material/medical_services:"),
        st.Page("views/Pharmacy.py", title="Pharmacy", icon=":material/medication:"),
        st.Page("views/Staff_Scheduling.py", title="Staff Scheduling", icon=":material/badge:"),
    ]

    pg = st.navigation(dashboard_pages)
    pg.run()
