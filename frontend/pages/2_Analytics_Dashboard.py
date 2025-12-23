# Path: frontend/pages/2_Analytics_Dashboard.py

import streamlit as st
import streamlit.components.v1 as components

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Analytics Dashboard",
    layout="wide"
)

# -------------------------------------------------
# ACCESS GUARD (IMPORTANT)
# -------------------------------------------------
if "db_loaded" not in st.session_state or not st.session_state["db_loaded"]:
    st.error("❌ Analytics not available yet.")
    st.info(
        "Please complete the following steps first:\n\n"
        "1️⃣ Upload Bank Statement\n"
        "2️⃣ Load Analytics\n\n"
        "Then return to this page."
    )

    # Optional: guide user back
    if st.button("⬅️ Go Back to Home"):
        st.switch_page("Home.py")

    st.stop()  # ⛔ HARD STOP (prevents iframe from loading)

# -------------------------------------------------
# DASHBOARD UI
# -------------------------------------------------
st.title("📊 Live Analytics Dashboard")
st.caption("← Use sidebar or browser back to return to Home")

components.html(
    """
    <iframe title="Dashboard_Finance_Analytics_Azure_Version"
     width="800" height="450" 
     src="https://app.powerbi.com/view?r=eyJrIjoiYjRhMjhmMGUtNjM3NC00OWRkLTg3MzgtYTc3N2MxNjIxOWY0IiwidCI6ImJlNmRiMjQyLTRmZTctNDJiMi1hZTE1LTZkODQ4NmNkNDc3ZiJ9" 
     frameborder="0" allowFullScreen="true">
     </iframe>
    """,
    height=700
)
st.balloons()