# Executive Workplan Intelligence System

An enterprise-grade, relational data orchestration pipeline and real-time analytical intelligence dashboard designed for the **Chief Finance Officer (CFO) Command Center**. 

This system automates the extraction, transformation, and loading (ETL) of multi-month operational spreadsheets into a transactional SQLite database engine, rendering a dynamic, high-performance executive dashboard via Streamlit.

---

## 🏗️ Architecture & Technical Core

The application is structured into an automated background backend pipeline and a modular multi-page frontend interface:

```text
├── App.py                            # Primary Executive Command Center Hub
├── pipeline.py                       # Automated multi-sheet ETL ingestion engine
├── institutional.db                  # Localized relational SQLite transactional layer
├── data_history_2026.xlsx            # Source workbook (Feb - June operational metrics)
└── Pages/                            # Specialized analytical view modules
    ├── 1_📊_Monthly_Planner.py       # Dynamic Monthly Operational Planner
    ├── 2_⚠️_Risk_Register.py          # Risk & Bottleneck Matrix Ledger
    └── 3_🎯_KPI_Monitor.py           # Strategic KPI & Performance Target Monitor