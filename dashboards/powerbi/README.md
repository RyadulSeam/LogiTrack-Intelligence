# LogiTrack Intelligence — Enterprise Power BI Project
**Directory:** `dashboards/powerbi/`  
**Master Project File:** `dashboards/powerbi/LogiTrack_Analytics/LogiTrack_Analytics.pbip`  
**Theme File:** `dashboards/powerbi/LogiTrack_Corporate_Theme.json`  
**Data Export Directory:** `dashboards/powerbi/data_export/`  

---

## 1. Project Overview

This is the official **Enterprise Power BI Project (`.pbip`)** for **LogiTrack Intelligence**, built in strict compliance with the 21-section Master Development Prompt. It provides a production-grade, 4-page Business Intelligence reporting suite engineered for Executive Management, Operations Directors, and Logistics Analysts.

```
dashboards/powerbi/
├── LogiTrack_Analytics/                      # Modern Power BI Project (.pbip)
│   ├── LogiTrack_Analytics.pbip              # Double-click entry point for Power BI Desktop
│   ├── LogiTrack_Analytics.Report/           # Visual report definitions (report.json, definition.pbir)
│   └── LogiTrack_Analytics.Dataset/          # Tabular model schema (model.bim, definition.pbidataset)
├── LogiTrack_Corporate_Theme.json            # Master Corporate Theme JSON (exact HEX palette)
├── data_export/                              # Clean, verified data tables (Dim & Fact CSVs)
├── dax_measures.txt                          # DAX Reference File
└── semantic_views.sql                        # Semantic Layer SQL Views
```

---

## 2. The 4 Core Dashboard Pages

1. **Page 1: Executive Control Tower**
   - 6 KPI Cards: Total Orders, Fulfilled Orders, On-Time Rate (OTD %), Delay Rate %, Avg Delivery Duration, Fleet Availability %.
   - Monthly Order Volume & OTD Performance Trend (Combo Chart).
   - Fulfillment vs Cancellation Ratio (Donut Chart).
   - Regional Hub Delivery Volume (Horizontal Clustered Bar Chart).
   - Regional Hub Operational Summary & SLA Watchlist (Table).

2. **Page 2: Regional Hub Operations**
   - 6 KPI Cards: Active Texas Hubs, Network Daily Capacity, Avg Processing Time, Intake Volume, Dispatches, Backlog.
   - Texas Regional Hub Spatial Distribution & Volume (Geo-Map with Texas coordinates).
   - Designed Capacity vs Processed Volume (Clustered Column Chart).
   - 24-Hour Network Intake vs Dispatch Rhythm (Dual-series Line Chart).
   - Regional Hub Bottleneck & Processing Performance Matrix (Table).

3. **Page 3: Delay & Root-Cause Analytics**
   - 6 KPI Cards: Total Late Deliveries, Delay Rate %, Avg Late Duration, Delay SLA Variance, Total Incidents, Total Orders.
   - Delay Reason Pareto Distribution (10 Verified Categories with cumulative % line & 80% threshold).
   - Delivery Delay Rate % by Vehicle Type (Horizontal Bar Chart).
   - Driver Performance Matrix (Scatter: Experience in Years vs OTD Rate %).
   - Machine Learning Real-Time Risk Predictions Feed (XGBoostClassifier pilot batch).

4. **Page 4: Fleet Telematics & Predictive Maintenance**
   - 6 KPI Cards: Total Fleet Assets, Active Fleet, Vehicles in Depot, Critical Risk Alerts, Total Spend, Total Downtime.
   - Fleet Operational Availability Breakdown (Donut Chart: Active vs Maintenance).
   - Vehicle Age (Days) vs Lifetime Mechanical Breakdown Count (Scatter Plot).
   - Maintenance Expense ($) by Service Category (Horizontal Bar Chart - source: synthetic).
   - High-Risk Vehicle Fleet Maintenance Action Watchlist (Table with status flags).

---

## 3. How to Open in Microsoft Power BI Desktop

1. Ensure **Microsoft Power BI Desktop** is installed.
2. In Power BI Desktop, go to:
   **File -> Open report -> Browse reports**
3. Navigate to:
   ```
   F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics\
   ```
4. Select **`LogiTrack_Analytics.pbip`** and click **Open**.
5. Power BI Desktop reads the Tabular Model (`model.bim`) and Visual Layout (`report.json`), loads the data from `data_export/`, and opens all 4 pages immediately!
6. *(Optional)* To save as a standalone binary file: Go to **File -> Save As** and select **Power BI file (*.pbix)**.

---

## 4. How to Refresh Data

To refresh the report after new warehouse runs:
1. Run the automated data export script:
   ```bash
   .venv\Scripts\python.exe scripts/pbi_stage3_export_data.py
   ```
2. In Power BI Desktop, click the **Refresh** button on the Home ribbon.

---

## 5. Technical Documentation Index

All architectural stages, data audits, and independent verification reports are documented in `docs/pbi/`:
- [`docs/pbi/stage1_inspection_report.md`](../../docs/pbi/stage1_inspection_report.md): Data inventory, column audit & 8 data gaps.
- [`docs/pbi/stage2_kpi_dictionary.md`](../../docs/pbi/stage2_kpi_dictionary.md): 28 verified KPIs with business definitions and rules.
- [`docs/pbi/stage3_semantic_model.md`](../../docs/pbi/stage3_semantic_model.md): Star-schema relationships, grains, and surrogate masking.
- [`docs/pbi/stage4_dax_engineering.md`](../../docs/pbi/stage4_dax_engineering.md): 30 production DAX measures across 5 display folders.
- [`docs/pbi/stage5_corporate_theme.md`](../../docs/pbi/stage5_corporate_theme.md): Exact HEX corporate palettes and typography rules.
- [`docs/pbi/stage6_dashboard_pages.md`](../../docs/pbi/stage6_dashboard_pages.md): Visual grid layout specifications.
- [`docs/pbi/stage8_kpi_validation_report.md`](../../docs/pbi/stage8_kpi_validation_report.md): 100% mathematical validation report (SQL vs DAX).
