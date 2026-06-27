import os
import pandas as pd
import sqlite3

def build_executive_database():
    # 1. Establish Absolute Paths to Bypass OneDrive Sync Conflicts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(base_dir, "data_history_2026.xlsx")
    db_dir = os.path.join(base_dir, "database")
    db_file = os.path.join(db_dir, "institutional.db")
    
    print("🚀 Initializing Executive Data Consolidation Engine...")
    print(f"📁 Target Project Directory: {base_dir}")

    # 2. Verification Guardrail: Excel Existence Check
    if not os.path.exists(excel_file):
        print(f"❌ Critical Error: Could not find '{os.path.basename(excel_file)}' in the root project folder.")
        print("💡 Please ensure your Excel file is named exactly: data_history_2026.xlsx")
        return
        
    # 3. Defensive Directory Creation
    try:
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"📁 Successfully created database directory: {db_dir}")
    except Exception as folder_err:
        print(f"⚠️ Directory creation skipped/restricted: {str(folder_err)}")
        print("🔄 Falling back: Writing database directly to root project folder.")
        db_file = os.path.join(base_dir, "institutional.db")

    # 4. Connect to Relational Database Engine
    try:
        conn = sqlite3.connect(db_file)
        print(f"🔌 Connected to SQLite database target: {db_file}")
    except sqlite3.OperationalError as db_err:
        print(f"💥 SQLite Connection Blocked: {str(db_err)}")
        print("🔄 Secondary Fallback: Enforcing local directory override...")
        db_file = os.path.join(base_dir, "institutional.db")
        conn = sqlite3.connect(db_file)

    # 5. Extract, Transform, and Load (ETL) Loop
    try:
        print(f"📖 Inspecting workbook layout structure...")
        # Get Excel sheet metadata first without loading full data matrices
        xl_file = pd.ExcelFile(excel_file)
        sheet_names = xl_file.sheet_names
        
        all_monthly_tables = []
        target_sheets = ["FEB", "MARCH", "APRIL", "MAY", "JUNE"]
        
        for sheet_name in sheet_names:
            sheet_clean = sheet_name.strip().upper()
            
            # Skip evaluation if the sheet name isn't part of our target operational horizon
            if not any(m in sheet_clean for m in target_sheets):
                print(f"⏭️ Skipping non-operational structural sheet: {sheet_name}")
                continue
                
            print(f"📦 Processing raw timeline grid: {sheet_clean}")
            
            # 🛠️ ADJUSTMENT: Skip the top stylized header banner line (Row 1)
            # This shifts the column index focus to Row 2, capturing genuine operational headers.
            df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=1)
            
            # Standardize column headers to uppercase to prevent mapping mismatches
            df.columns = df.columns.str.strip().str.upper()
            
            # Map raw names directly 
            df['MONTH_YEAR'] = sheet_clean
            
            # Fix Excel merged cell artifacts (handling sequential empty Date rows cleanly)
            if 'DATE' in df.columns:
                df['DATE'] = (
                    df['DATE']
                    .astype(str)
                    .str.strip()
                    .replace({"nan": None, "None": None, "": None})
                )
                df['DATE'] = df['DATE'].ffill()
            
            # Inject defensive fallbacks for critical analytical modules if missing
            if 'STATUS' not in df.columns:
                df['STATUS'] = 'Not Started'
            if 'PRIORITY' not in df.columns:
                df['PRIORITY'] = 'Medium'
                
            all_monthly_tables.append(df)
            
        if not all_monthly_tables:
            print("❌ Processing Aborted: No valid data matrices matching monthly criteria found.")
            return

        # 6. Structural Merge (Appending all 5 months together into 1 dataset)
        print("🔗 Appending operational rows into a unified relational schema...")
        unified_workplan_df = pd.concat(all_monthly_tables, ignore_index=True)
        
        # Clean any remaining empty rows that might be lingering at the bottom of sheets
        if 'KEY_TASK_TO_BE_UNDERTAKEN' in unified_workplan_df.columns:
            unified_workplan_df = unified_workplan_df.dropna(subset=['KEY_TASK_TO_BE_UNDERTAKEN'])
        
        # 7. Commit cleanly to the SQLite relational engine
        unified_workplan_df.to_sql(
            name="operational_workplan", 
            con=conn, 
            if_exists="replace", 
            index=False
        )
        
        print("\n" + "="*50)
        print("📊 DATA INGESTION PIPELINE EXECUTED SUCCESSFULLY!")
        print(f"💾 Active Table Formed: 'operational_workplan'")
        print(f"🔢 Total Core Analytical Rows Logged: {len(unified_workplan_df)}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"💥 Critical Failure during pipeline execution: {str(e)}")
    finally:
        conn.close()
        print("🔌 Database connection closed safely.")

if __name__ == "__main__":
    build_executive_database()