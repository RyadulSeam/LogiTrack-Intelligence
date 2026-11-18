# LogiTrack Intelligence — Power BI Project
# Stage 5: Corporate Design System & Theme Specification
**Document Reference:** `docs/pbi/stage5_corporate_theme.md`  
**Phase:** Phase 7 (Specialized) — Enterprise Power BI Analytics  
**Version:** 1.0.0  
**Artifact File:** `dashboards/powerbi/LogiTrack_Corporate_Theme.json`  

---

## 1. Master Corporate Color Palette & HEX Specifications

The LogiTrack Intelligence design system enforces a clean, executive-grade corporate aesthetic. All visual charts, backgrounds, text classes, and conditional formatting rules strictly employ the verified palette below:

### 1.1 Primary Corporate Colors

| Color Token | HEX Code | RGB | Role & Usage |
|---|---|---|---|
| **Deep Navy** | `#142B45` | `rgb(20, 43, 69)` | Main brand identifier, report titles, primary KPI values, table headers, and major navigation elements. |
| **Corporate Blue** | `#2F5D8A` | `rgb(47, 93, 138)` | Primary analytical data series, bar charts, trend lines, and comparative metrics. |
| **Slate** | `#64748B` | `rgb(100, 116, 139)` | Subtitles, KPI category labels, secondary chart series, axis labels, and supporting annotations. |
| **Light Background**| `#F4F6F8` | `rgb(244, 246, 248)` | Uniform report canvas background across all 4 pages. |
| **Surface White** | `#FFFFFF` | `rgb(255, 255, 255)` | KPI card surfaces, visual container backgrounds, and contrast headers. |

### 1.2 Semantic Status Colors (Strict Business Meaning)

| Status Token | HEX Code | RGB | Semantic Business Meaning |
|---|---|---|---|
| **Status Green** | `#2E7D5B` | `rgb(46, 125, 91)` | **Positive / Healthy / On-Time**: Deliveries on time, active vehicles, healthy SLA meeting targets. |
| **Status Amber** | `#C58B2A` | `rgb(197, 139, 42)` | **Warning / Moderate Concern / In-Shop**: Vehicles in maintenance, moderate backlog, attention required. |
| **Status Red** | `#C65353` | `rgb(198, 83, 83)` | **Critical / Adverse / Delayed**: Late deliveries, maintenance breakdown alerts, cancelled orders. |
| **Neutral Grey** | `#8793A1` | `rgb(135, 147, 161)` | **Neutral / Benchmark / Secondary**: Prior period comparisons, inactive elements, reference lines. |

---

## 2. Global Design Rules & Constraints

1. **Zero Rainbow Palettes:** No visual may introduce unapproved bright colors (yellows, purples, oranges). Every color must trace back to the master palette.
2. **Semantic Meaning Lock:** Red `#C65353` is strictly reserved for adverse conditions (delays, critical alerts). Green `#2E7D5B` is strictly reserved for positive fulfillment. They are never used decoratively.
3. **Card Consistency:** All KPI cards feature a clean `#FFFFFF` surface, `#142B45` bold callout values (24pt), `#64748B` category labels (9pt), and a subtle `#E2E8F0` border.
4. **Table Styling:** Dark navy headers (`#142B45`) with white text (`#FFFFFF`) and alternating white/light-slate rows (`#F8FAFC`).
5. **No Visual Clutter:** No drop shadows, no 3D charts, no heavy gradients, and no rounded borders exceeding 4px radius.

---

## 3. Page-Wise Color & Visual Architecture

### Page 1: Executive Control Tower
- **Visual Personality:** High-level, authoritative, clean, executive.
- **Header:** Deep Navy `#142B45`
- **Volume & Trend:** Corporate Blue `#2F5D8A` bars with Green `#2E7D5B` OTD trend line.
- **Status Donut:** Green `#2E7D5B` (Delivered) vs Red `#C65353` (Cancelled).
- **KPI Accents:** OTD Rate colored Green `#2E7D5B`; Delay Rate colored Red `#C65353`.

### Page 2: Regional Hub Operations
- **Visual Personality:** Structured, operational, comparative, geographical.
- **Hub Map:** Clean corporate map canvas with Corporate Blue `#2F5D8A` hub bubbles.
- **Capacity vs Volume:** Corporate Blue `#2F5D8A` (Actual Orders) vs Slate `#64748B` (Daily Designed Capacity).
- **Hourly Flow:** Corporate Blue `#2F5D8A` (Intake) vs Slate `#64748B` (Dispatches).

### Page 3: Delay Root-Cause & SLA Diagnostics
- **Visual Personality:** Diagnostic, investigative, evidence-based, risk-oriented.
- **Pareto Bars:** Corporate Blue `#2F5D8A` for ranked delay cause counts.
- **Pareto Cumulative Line:** Slate `#64748B` / Dark Navy line with 80% benchmark reference line.
- **Vehicle Type Delay Bars:** Corporate Blue `#2F5D8A` with Red `#C65353` callout on highest delay tier.
- **Driver Scatter:** Corporate Blue `#2F5D8A` bubbles with Green/Amber/Red quadrant benchmarks.

### Page 4: Fleet Telematics & Predictive Maintenance
- **Visual Personality:** Technical, asset-focused, health-monitoring, alert-driven.
- **Fleet Status Donut:** Green `#2E7D5B` (Active) vs Amber `#C58B2A` (In Maintenance).
- **Maintenance Cost by Service:** Corporate Blue `#2F5D8A` bars with synthetic data banner.
- **Age vs Breakdown Scatter:** Corporate Blue `#2F5D8A` bubbles.
- **Urgent Watchlist Grid:** Conditional formatting highlighting Maintenance Alert flags in Red `#C65353`.

---

## 4. Cross-Page Semantic Consistency Matrix

| Entity / Status Condition | Required Color Token | Exact HEX | Consistent Meaning Across All 4 Pages |
|---|---|---|---|
| **On-Time Delivery** | Status Green | `#2E7D5B` | Fulfilled within target SLA window. |
| **Delayed Delivery** | Status Red | `#C65353` | Fulfilled past target delivery duration. |
| **Cancelled Order** | Status Red | `#C65353` | Lost/unfulfilled order. |
| **Active Fleet Vehicle** | Status Green | `#2E7D5B` | Road-ready asset available for dispatch. |
| **Vehicle In Maintenance** | Status Amber | `#C58B2A` | Asset currently in depot for servicing. |
| **Maintenance Alert Flag** | Status Red | `#C65353` | High breakdown risk vehicle requiring immediate inspection. |
| **Primary Order Series** | Corporate Blue | `#2F5D8A` | Main quantitative transactional volume. |
| **Designed Capacity Baseline** | Slate | `#64748B` | Reference engineering threshold. |
| **Prior Period Comparison** | Neutral Grey | `#8793A1` | Previous month/week benchmark. |

---

## 5. Typography Standards

| Role | Font Family | Size | Weight | Color |
|---|---|---|---|---|
| **Report Page Titles** | Segoe UI Semibold | 16pt | 600 | Deep Navy `#142B45` |
| **Section & Visual Titles** | Segoe UI Semibold | 12pt | 600 | Deep Navy `#142B45` |
| **KPI Callout Values** | Segoe UI Semibold | 24pt | 600 | Deep Navy `#142B45` / Status Color |
| **KPI Category Subtitles** | Segoe UI | 9pt | 400 | Slate `#64748B` |
| **Chart Axis & Data Labels** | Segoe UI | 8–9pt | 400 | Slate `#64748B` |
| **Table Column Headers** | Segoe UI Semibold | 10pt | 600 | Surface White `#FFFFFF` |
| **Table Row Data** | Segoe UI | 9pt | 400 | Deep Navy `#142B45` |

---

> **Stage 5 Complete. The Corporate Theme JSON and Page-wise Color Specifications are locked in. Ready to advance to Stage 6: Dashboard Page Development.**
