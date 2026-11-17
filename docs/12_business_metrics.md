# Business Metrics & KPI Dictionary
# LogiTrack Intelligence — Phase 7

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-12 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-17 |

---

## 1. Executive KPIs Matrix

| Metric Name | Business Definition | Target / Benchmark | Source Table(s) | Update Frequency |
|---|---|---|---|---|
| **On-Time Delivery Rate (OTD %)** | Percentage of delivered shipments arriving on or before SLA | **≥ 80.0%** | `warehouse.fact_orders` | Real-time / Daily |
| **Shipment Delay Rate (%)** | Percentage of delivered shipments experiencing delays | **≤ 20.0%** | `warehouse.fact_orders` | Real-time / Daily |
| **Fleet Utilization (%)** | Ratio of Active vehicles to Total registered fleet | **≥ 85.0%** | `warehouse.dim_vehicle` | Hourly |
| **Average Delivery Duration** | Mean elapsed transit duration from dispatch to delivery | **< 36.0 hrs** | `warehouse.fact_orders` | Daily |
| **Customer Satisfaction (CSAT)**| Average score rated by recipients (1 to 5 scale) | **≥ 4.0 / 5.0** | `warehouse.fact_orders` | Daily |
| **Hub Capacity Utilization** | Current active backlog relative to daily throughput limit | **≤ 85.0%** | `warehouse.fact_hub_hourly` | Hourly |

---

## 2. Mathematical & SQL Formulations

### 2.1 On-Time Delivery Rate (OTD %)
$$\text{OTD \%} = \left( \frac{\text{Delivered Orders where } is\_on\_time = \text{TRUE}}{\text{Total Delivered Orders}} \right) \times 100$$

**SQL Formula:**
```sql
SELECT 
    ROUND(
        (SUM(CASE WHEN is_on_time = TRUE AND order_status = 'Delivered' THEN 1 ELSE 0 END)::DECIMAL 
        / NULLIF(SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END), 0)) * 100, 2
    ) AS otd_rate_pct
FROM warehouse.fact_orders;
```

**DAX Formula:**
```dax
On-Time Delivery Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_on_time] = TRUE() && 'fact_orders'[order_status] = "Delivered"),
    CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[order_status] = "Delivered"),
    0
) * 100
```

---

### 2.2 Delay Rate (%)
$$\text{Delay Rate \%} = \left( \frac{\text{Delivered Orders where } is\_delayed = \text{TRUE}}{\text{Total Delivered Orders}} \right) \times 100$$

**SQL Formula:**
```sql
SELECT 
    ROUND(
        (SUM(CASE WHEN is_delayed = TRUE AND order_status = 'Delivered' THEN 1 ELSE 0 END)::DECIMAL 
        / NULLIF(SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END), 0)) * 100, 2
    ) AS delay_rate_pct
FROM warehouse.fact_orders;
```

---

### 2.3 Fleet Utilization Rate (%)
$$\text{Fleet Utilization \%} = \left( \frac{\text{Active Vehicles}}{\text{Total Fleet Assets}} \right) \times 100$$

**SQL Formula:**
```sql
SELECT 
    ROUND(
        (SUM(CASE WHEN current_status = 'Active' THEN 1 ELSE 0 END)::DECIMAL 
        / NULLIF(COUNT(*), 0)) * 100, 1
    ) AS fleet_utilization_pct
FROM warehouse.dim_vehicle;
```

---

## 3. Reporting Channels & Visualizations

| Layer | Primary Tool | Target Persona | Primary Views |
|---|---|---|---|
| **Operational Control Tower** | Streamlit | Dispatchers, Ops Leads | Live Texas Map, Delay alerts, Hub backlog gauges |
| **Management Reporting** | Power BI Desktop | Executives, Directors | Quarterly OTD trends, Route profitability, Fleet asset lifecycle |
| **Pipeline Health** | Grafana / Tests | Data Engineers, DevOps | Throughput pings/sec, Ingestion error rates (DLQ) |
