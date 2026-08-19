"""
auth.py
-------
Lightweight, defense-in-depth access guard for the detail pages.

Primary authentication happens in Home.py: the sidebar navigation is only
mounted after a successful sign-in, so unauthenticated users never see a
link to any detail page. require_login() is a second safety net in case a
page URL is ever opened directly (Streamlit multipage apps expose a direct
route per page) — it re-checks the same session flag Home.py sets and
blocks rendering if the session isn't authenticated.
"""

import streamlit as st
from utils.styling import icon_svg


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))


def require_login():
    if not is_authenticated():
        st.markdown('<style>[data-testid="stSidebar"] {display: none !important;}</style>', unsafe_allow_html=True)
        st.markdown(
            f"### {icon_svg('lock', size=22)} Access restricted",
            unsafe_allow_html=True,
        )
        st.info("Please sign in from the Home page to view this dashboard.")
        st.stop()
