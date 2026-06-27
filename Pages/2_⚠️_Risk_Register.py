import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("⚠️ Institutional Risk & Bottleneck Register")

# =========================================================
# 🧭 UNIFIED GLOBAL SIDEBAR NAVIGATION CONTROLS
# =========================================================
st.sidebar.markdown("### 🗺️ System Controls")
if "target_month" not in st.session_state:
    st.session_state.target_month = "JUNE 2026"

available_months = ["FEB 2026", "MARCH 2026", "APRIL 2026", "MAY 2026", "JUNE 2026"]
try:
    default_index = available_months.index(st.session_state.target_month.upper())
except ValueError:
    default_index = 4

selected_month = st.sidebar.selectbox(
    "Select Target Operational Month Cycle:",
    available_months,
    index=default_index,
    key="risk_month_selector"
)

if st.session_state.target_month != selected_month:
    st.session_state.target_month = selected_month
    st.rerun()

active_month = st.session_state.target_month
st.markdown(f"Active Vulnerability Assessment Scope: **{active_month}**")

# =========================================================
# 📊 RISK & EXPOSURE ANALYSIS LAYER
# =========================================================
# Force look in root project folder next to app.py
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_file = os.path.join(base_dir, "institutional.db")

if os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    try:
        query = "SELECT * FROM operational_workplan WHERE UPPER(TRIM(MONTH_YEAR)) = ?"
        df = pd.read_sql_query(query, conn, params=(active_month.strip().upper(),))
    except Exception as e:
        st.error(f"SQL Read Failure: {str(e)}")
        df = pd.DataFrame()
    finally:
        conn.close()
    
    if not df.empty:
        df.columns = df.columns.str.strip().str.upper()
        
        df["STATUS"] = df["STATUS"].astype(str).str.strip().str.upper() if "STATUS" in df.columns else "NOT STARTED"
        df["PRIORITY"] = df["PRIORITY"].astype(str).str.strip().str.upper() if "PRIORITY" in df.columns else "MEDIUM"
        
        delayed_blocked = df[df["STATUS"].isin(["DELAYED", "BLOCKED"])]
        high_priority_open = df[(df["PRIORITY"] == "HIGH") & (df["STATUS"] != "COMPLETED")]
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### 🚨 Delayed & Blocked Items")
            if not delayed_blocked.empty:
                display_cols = [c for c in ["DATE", "KEY_RESPONSIBILITY", "KEY_TASK_TO_BE_UNDERTAKEN", "STATUS"] if c in df.columns]
                st.dataframe(delayed_blocked[display_cols], use_container_width=True, hide_index=True)
            else:
                st.success("Clear Pipeline: No workflows are flagged as delayed or blocked.")
                
        with col_right:
            st.markdown("### 🔥 High-Priority Open Exposures")
            if not high_priority_open.empty:
                display_cols = [c for c in ["DATE", "KEY_RESPONSIBILITY", "KEY_TASK_TO_BE_UNDERTAKEN", "PRIORITY"] if c in df.columns]
                st.dataframe(high_priority_open[display_cols], use_container_width=True, hide_index=True)
            else:
                st.success("Low Exposure: All high-priority items are tracking on schedule.")
    else:
        st.warning(f"No records available to analyze for '{active_month}'.")
else:
    st.error("Data repository layer unavailable.")