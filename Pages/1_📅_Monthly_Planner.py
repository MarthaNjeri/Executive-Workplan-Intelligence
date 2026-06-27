import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")
st.title("📅 Dynamic Monthly Operational Planner")

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
    key="planner_month_selector"
)

if st.session_state.target_month != selected_month:
    st.session_state.target_month = selected_month
    st.rerun()

# Set current working scope
active_month = st.session_state.target_month
st.markdown(f"Current Planning Matrix Target Window: **{active_month}**")

# =========================================================
# 💾 DATABASE OPERATIONS & INTERACTIVE SYSTEM LAYER
# =========================================================
# Force look in root project folder next to app.py
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_file = os.path.join(base_dir, "institutional.db")

if os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    try:
        query = "SELECT rowid, * FROM operational_workplan WHERE UPPER(TRIM(MONTH_YEAR)) = ?"
        df = pd.read_sql_query(query, conn, params=(active_month.strip().upper(),))
    except Exception as e:
        st.error(f"Error loading planning rows: {str(e)}")
        df = pd.DataFrame()
    finally:
        conn.close()
    
    if not df.empty:
        df.columns = df.columns.str.strip().str.upper()
        
        status_option = "STATUS" if "STATUS" in df.columns else df.columns[1]
        priority_option = "PRIORITY" if "PRIORITY" in df.columns else df.columns[2]

        st.caption("💡 Executive Configuration: Edit statuses or priorities interactively below. Click the save button to commit changes.")
        
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=[c for c in df.columns if c not in ["STATUS", "PRIORITY"]],
            column_config={
                "ROWID": None,
                "STATUS": st.column_config.SelectboxColumn(
                    "STATUS",
                    options=["NOT STARTED", "IN PROGRESS", "COMPLETED", "DELAYED", "BLOCKED"],
                    required=True,
                ),
                "PRIORITY": st.column_config.SelectboxColumn(
                    "PRIORITY",
                    options=["LOW", "MEDIUM", "HIGH"],
                    required=True,
                )
            }
        )
        
        st.markdown("### 💾 Commit Operations")
        if st.button("Save Operational Changes to Database", type="primary"):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            try:
                for index, row in edited_df.iterrows():
                    cursor.execute(
                        f"UPDATE operational_workplan SET {status_option} = ?, {priority_option} = ? WHERE rowid = ?",
                        (row[status_option], row[priority_option], row["ROWID"])
                    )
                conn.commit()
                st.success(f"📊 Successfully updated records for {active_month}!")
                st.balloons()
            except Exception as write_err:
                conn.rollback()
                st.error(f"💥 Write failure: {str(write_err)}")
            finally:
                conn.close()
    else:
        st.warning(f"No planning rows found matching '{active_month}' in the database.")
else:
    st.error("Data repository layer unavailable.")