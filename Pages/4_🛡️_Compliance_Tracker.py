import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("🛡️ Regulatory & Statutory Compliance Tracker")

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
    key="compliance_tracker_resilient"
)

if st.session_state.target_month != selected_month:
    st.session_state.target_month = selected_month
    st.rerun()

active_month = st.session_state.target_month
st.markdown(f"Statutory Risk & Governance Horizon: **{active_month}**")

st.markdown(
    """
    <style>
    .compliance-box { background-color: #FFFBEB; padding: 15px; border-left: 5px solid #D97706; border-radius: 4px; margin-bottom: 20px; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 🔍 RESILIENT ALL-COLUMN SEARCH ENGINE
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
        # Standardize column naming configurations
        df.columns = df.columns.str.strip().str.upper()
        
        # Expanded keywords to match your standard workflow entries
        compliance_keywords = ["TAX", "ITAX", "ETIMS", "KRA", "STATUTORY", "AUDIT", "FILING", "COMPLIANCE", "RECONCILIATION", "PAYMENT", "APPROVAL", "RETURNS"]
        regex_pattern = "|".join(compliance_keywords)
        
        # Global Search: Enforce text matching across ALL columns simultaneously
        # This bypasses strict column header tracking entirely
        match_mask = df.astype(str).apply(lambda row: row.str.upper().str.contains(regex_pattern).any(), axis=1)
        compliance_df = df[match_mask]
        
        if not compliance_df.empty:
            status_col = "STATUS" if "STATUS" in compliance_df.columns else None
            
            # Metric Math Calculation
            total_comp = len(compliance_df)
            if status_col:
                completed_comp = len(compliance_df[compliance_df[status_col].astype(str).str.upper().str.strip() == "COMPLETED"])
            else:
                completed_comp = 0
            pending_comp = total_comp - completed_comp
            
            st.markdown(
                f"""
                <div class="compliance-box">
                    <strong>🛡️ CFO Compliance Oversight Note:</strong><br>
                    Found <b>{total_comp}</b> core workflows matching regulatory deadlines, approval gates, or statutory requirements for this cycle.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Compliance Items", total_comp)
            m2.metric("Completed Deadlines", completed_comp)
            m3.metric("Outstanding Exposures", pending_comp, delta_color="inverse")
            
            st.markdown("### 📋 Filtered Statutory Ledger")
            # Present columns that actually exist in your data model layout
            expected_cols = ["DATE", "KEY_RESPONSIBILITY", "KEY_TASK_TO_BE_UNDERTAKEN", "EXPECTED_DELIVERABLES", "STATUS", "PRIORITY"]
            display_cols = [c for c in expected_cols if c in compliance_df.columns]
            if not display_cols:
                display_cols = compliance_df.columns.tolist()
                
            st.dataframe(compliance_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info(f"ℹ️ Broad scan completed: No explicit rows flagged with compliance keywords inside the '{active_month}' sequence.")
    else:
        st.warning(f"⚠️ No raw data records found in the database for '{active_month}'. Go to your main dashboard page to verify your database connection data.")
else:
    st.error("Data repository layer unavailable.")