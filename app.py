import os
import sqlite3
import pandas as pd
import streamlit as st

# 1. PAGE SETUP & CORPORATE ACCENTS
st.set_page_config(
    page_title="Executive Workplan Intelligence", 
    page_icon="📊", 
    layout="wide"
)

# Custom Styling: Executive Corporate Navy Palette
st.markdown(
    """
    <style>
    .exec-header { font-size:30px !important; font-weight: bold; color: #1E3A8A; margin-bottom: 2px; }
    .exec-sub { font-size:14px !important; color: #555555; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px; }
    .metric-box { background-color: #F8FAFC; padding: 20px; border-radius: 6px; border-top: 4px solid #1E3A8A; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="exec-header">EXECUTIVE WORKPLAN INTELLIGENCE SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="exec-sub">Chief Finance Officer (CFO) Command Center | Unified Relational Engine</div>', unsafe_allow_html=True)

# 2. DATABASE READ LAYER
def load_active_workplan(month_filter):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for root location first since pipeline falls back here on OneDrive lockouts
    db_file = os.path.join(base_dir, "institutional.db")
    if not os.path.exists(db_file):
        db_file = os.path.join(base_dir, "database", "institutional.db")

    if not os.path.exists(db_file):
        st.error(f"❌ Database engine file not found at project path locations.")
        return pd.DataFrame()

    conn = sqlite3.connect(db_file)
    try:
        # Enforce case-insensitive comparison using SQL UPPER()
        query = "SELECT * FROM operational_workplan WHERE UPPER(TRIM(MONTH_YEAR)) = ?"
        df = pd.read_sql_query(query, conn, params=(month_filter.strip().upper(),))
    except Exception as e:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

# 3. SIDEBAR NAVIGATION CONTROLS & SHARED GLOBAL STATE
st.sidebar.markdown("### 🗺️ System Controls")

# Initialize state cleanly
if "target_month" not in st.session_state:
    st.session_state.target_month = "JUNE 2026"

available_months = ["FEB 2026", "MARCH 2026", "APRIL 2026", "MAY 2026", "JUNE 2026"]

try:
    default_index = available_months.index(st.session_state.target_month.upper())
except ValueError:
    default_index = 4

# Interactively monitor selector updates
selected_month = st.sidebar.selectbox(
    "Select Target Operational Month Cycle:",
    available_months,
    index=default_index,
    key="main_dashboard_month_selector"
)

# Force application state sync on modification
if st.session_state.target_month != selected_month:
    st.session_state.target_month = selected_month
    st.rerun()

st.sidebar.success(f"Connected Matrix: {st.session_state.target_month}")

# 4. DATA PROCESSING FOR METRIC TILES
df_tasks = load_active_workplan(st.session_state.target_month)

st.subheader(f"📆 Live Operational Cadence — {st.session_state.target_month}")

if not df_tasks.empty:
    # Safely match column identifiers even if casing is skewed
    df_tasks.columns = df_tasks.columns.str.strip().str.upper()
    
    status_col = "STATUS" if "STATUS" in df_tasks.columns else None
    priority_col = "PRIORITY" if "PRIORITY" in df_tasks.columns else None
    
    if status_col:
        df_tasks[status_col] = df_tasks[status_col].astype(str).str.strip().str.upper()
    if priority_col:
        df_tasks[priority_col] = df_tasks[priority_col].astype(str).str.strip().str.upper()

    # =========================================================
    # 🔍 RESILIENT TEXT PARSING LAYER
    # =========================================================
    total_tasks = len(df_tasks)
    
    # Check for text patterns matching completed variants (COMPLETED, DONE)
    if status_col:
        completed_tasks = len(df_tasks[df_tasks[status_col].str.contains("COMPLETED|DONE", na=False)])
        delayed_tasks = len(df_tasks[df_tasks[status_col].str.contains("DELAYED|BLOCKED|PENDING", na=False)])
    else:
        completed_tasks = 0
        delayed_tasks = 0
    
    # Check for text patterns matching high priority variants (HIGH, CRITICAL)
    if priority_col and status_col:
        high_priority_open = len(df_tasks[
            (df_tasks[priority_col].str.contains("HIGH|CRITICAL", na=False)) & 
            (~df_tasks[status_col].str.contains("COMPLETED|DONE", na=False))
        ])
    else:
        high_priority_open = 0
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    # Layout Execution Dashboard Metric Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Total Logged Tasks", value=total_tasks)
    with c2:
        st.metric(label="Completion Rate", value=f"{completion_rate:.1f}%", delta="Target Base: 85.0%")
    with c3:
        st.metric(label="Delayed Bottlenecks", value=delayed_tasks, delta_color="inverse")
    with c4:
        st.metric(label="High-Priority Open Items", value=high_priority_open)

    st.markdown("---")
    
    # Render Master Table View
    st.markdown("### 📋 Primary Operational Ledger")
    expected_cols = ["DATE", "KEY_RESPONSIBILITY", "KEY_TASK_TO_BE_UNDERTAKEN", "EXPECTED_DELIVERABLES", "STATUS", "PRIORITY"]
    display_cols = [c for c in expected_cols if c in df_tasks.columns]
    
    if not display_cols:
        display_cols = df_tasks.columns.tolist()
        
    st.dataframe(df_tasks[display_cols], use_container_width=True, hide_index=True)

else:
    st.warning(f"No operational workplan records found matching '{st.session_state.target_month}'. Please check your sidebar selection or ensure pipeline.py was run.")