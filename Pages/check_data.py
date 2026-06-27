import sqlite3
import pandas as pd

# FIXED: Points directly to the root directory database to bypass OneDrive path blocks
conn = sqlite3.connect("institutional.db")
try:
    # 1. Check what tables exist
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    print("📁 Tables found in database:")
    print(tables)
    print("-" * 50)
    
    # 2. Check the unique months stored in the data
    months = pd.read_sql_query("SELECT DISTINCT MONTH_YEAR FROM operational_workplan;", conn)
    print("🗓️ Unique months found in your data:")
    print(months)
    print("-" * 50)
    
    # 3. Look at the column names
    columns = pd.read_sql_query("PRAGMA table_info(operational_workplan);", conn)
    print("📋 Column headers found in your data:")
    print(columns[['name']])
    
except Exception as e:
    print(f"❌ Error reading database: {str(e)}")
finally:
    conn.close()