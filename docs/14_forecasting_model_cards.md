# LogiTrack Intelligence — Forecasting Model Cards
**Document Reference:** `docs/14_forecasting_model_cards.md`  
**Phase:** Phase 9 — Forecasting Engineering  
**Version:** 1.0.0  
**Storage & Registry:** DuckDB `forecasting.model_registry`, `forecasting.model_evaluations`, `forecasting.demand_forecasts`, `forecasting.hub_workload_forecasts`, `forecasting.fleet_requirement_forecasts`  
**Artifact Directory:** `models/artifacts/*.joblib`  

---

## 1. Executive Summary

Phase 9 implements an enterprise-grade, resource-bounded time-series forecasting suite specifically engineered for regional supply chain and fulfillment operations in Texas. It delivers three dedicated predictive engines:

1. **Regional Demand Forecaster:** Multi-horizon (7-day and 30-day) order volume forecasting with dynamic point estimates and 95% Confidence Intervals via quantile regression.
2. **Hub Workload & Bottleneck Forecaster:** Physical capacity utilization modeling, throughput bounding, and proactive bottleneck alert classification.
3. **Fleet Requirement & Allocation Forecaster:** Vehicle asset requirement projections across 4 vehicle classes (Van, Truck, Pickup, Box Truck) with deficit/surplus gap analysis against active fleet supply.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Warehouse Gold Storage                            │
│           (warehouse.fact_orders, dim_date, dim_hub)                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
               Time-Series Feature Engineering Pipeline
                 (src/logitrack/forecasting/features.py)
          • Calendar & Cyclical (sin/cos DOW, Month, Quarter)
          • Lag Autoregressions (lag 1, 2, 3, 7, 14, 21, 28)
          • Rolling Windows (mean, std, min, max over 7, 14, 28 days)
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  Regional Demand     │ │  Hub Workload        │ │  Fleet Requirement   │
│  Forecaster          │ │  Forecaster          │ │  Forecaster          │
│  (Quantile GBDT)     │ │  (Capacity Flow)     │ │  (Payload & Supply)  │
└──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DuckDB Forecasting Registry                          │
│  • forecasting.model_registry                                          │
│  • forecasting.model_evaluations                                       │
│  • forecasting.demand_forecasts (30-day ahead per hub)                 │
│  • forecasting.hub_workload_forecasts (utilization & bottleneck alerts)│
│  • forecasting.fleet_requirement_forecasts (vehicle demand vs 33 fleet)│
│  • models/artifacts/*.joblib                                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Model Card 1: Regional Demand Forecaster (`regional_demand_forecaster`)

### 2.1 Model Details
- **Model Identifier:** `regional_demand_forecaster` (v1.0.0)
- **Algorithm:** Tri-Model Gradient Boosting Regressors (`sklearn.ensemble.GradientBoostingRegressor`)
  - **Point Model:** Least-squares loss (`squared_error`) for expected demand
  - **Lower Bound Model:** Quantile regression with $\alpha = 0.025$ (2.5th percentile)
  - **Upper Bound Model:** Quantile regression with $\alpha = 0.975$ (97.5th percentile)
- **Hyperparameters:** `n_estimators=150`, `max_depth=4`, `learning_rate=0.05`, `random_state=42`
- **Serialization Artifact:** `models/artifacts/demand_forecaster.joblib`

### 2.2 Feature Space
- **Calendar & Cyclical:** `day_of_week`, `day_of_month`, `month`, `quarter`, `is_weekend`, `day_of_year`, `sin_dow`, `cos_dow`, `sin_month`, `cos_month`.
- **Autoregressive Lags:** `lag_1`, `lag_2`, `lag_3`, `lag_7`, `lag_14`, `lag_21`, `lag_28`.
- **Rolling Aggregations:** `rolling_mean_7`, `rolling_std_7`, `rolling_min_7`, `rolling_max_7`, `rolling_mean_14`, `rolling_mean_28`, `rolling_std_28`, `expanding_mean`.

### 2.3 Chronological Non-Leaking Backtesting
- **Total Dataset:** 4,296 daily hub records across 6 Texas regional hubs.
- **Train Window:** `2023-01-29` to `2024-09-30` (3,586 records, ~20 months).
- **Test Window (Out-of-Time):** `2024-10-01` to `2024-12-31` (542 records, 92 days).
- **Evaluation Performance Metrics:**
  - **MAE (Mean Absolute Error):** **1.96 parcels/day**
  - **RMSE (Root Mean Squared Error):** **2.55 parcels/day**
  - **$R^2$ Score:** **0.5983**
  - **Empirical 95% Confidence Interval Coverage:** **97.05%** (target: $\ge 95\%$)

---

## 3. Model Card 2: Hub Workload & Capacity Forecaster (`hub_workload_forecaster`)

### 3.1 Model Details
- **Model Identifier:** `hub_workload_forecaster` (v1.0.0)
- **Algorithm:** Deterministic Capacity Flow & Bottleneck Classification Model
- **Serialization Artifact:** `models/artifacts/hub_workload_forecaster.joblib`
- **Parameters:** `bottleneck_threshold_pct=85.0%`

### 3.2 Formulation & Business Logic
$$\text{Capacity Utilization \%} = \frac{\text{Forecast Order Volume}}{\text{Designed Daily Capacity}} \times 100$$

$$\text{Projected Daily Backlog} = \max\left(0, \text{Forecast Order Volume} - \min(\text{Forecast Order Volume}, 0.98 \times \text{Daily Capacity})\right)$$

$$\text{Risk Classification} = \begin{cases} 
\text{CRITICAL\_OVERFLOW} & \text{if } \text{Utilization} \ge 100\% \\ 
\text{HIGH\_RISK} & \text{if } 85\% \le \text{Utilization} < 100\% \\ 
\text{NORMAL} & \text{otherwise} 
\end{cases}$$

### 3.3 Output Characteristics
- 180 daily workload forecasts across 6 Texas regional hubs (Dallas Main, Houston, Austin, San Antonio, Fort Worth, El Paso).
- Identifies peak delivery days with bottleneck risk flags so logistics dispatchers can pre-route volume to adjacent regional hubs.

---

## 4. Model Card 3: Fleet Requirement Forecaster (`fleet_requirement_forecaster`)

### 4.1 Model Details
- **Model Identifier:** `fleet_requirement_forecaster` (v1.0.0)
- **Algorithm:** Payload & Asset Allocation Constraint Model
- **Serialization Artifact:** `models/artifacts/fleet_requirement_forecaster.joblib`
- **Active Fleet Supply Baseline:** 33 active vehicles (22 Vans, 6 Trucks, 2 Pickups, 3 Box Trucks).

### 4.2 Fleet Configuration Matrix

| Vehicle Type | Order Share % | Daily Parcel Capacity / Vehicle | Active Fleet Supply Baseline |
|---|---|---|---|
| **Van** | 65.03% | 35 parcels/day | 22 |
| **Truck** | 19.29% | 25 parcels/day | 6 |
| **Pickup** | 10.31% | 40 parcels/day | 2 |
| **Box Truck** | 5.37% | 20 parcels/day | 3 |

### 4.3 Output Characteristics
- Generates 720 forward fleet requirement forecasts ($30 \text{ days} \times 6 \text{ hubs} \times 4 \text{ vehicle types}$).
- Computes vehicle demand, active fleet utilization, and surplus/deficit balance against available assets.

---

## 5. Compliance & Data Provenance Notice

> [!NOTE]
> **Synthetic / Simulation Notice:**  
> All future 7-day and 30-day forecast outputs are explicitly tagged with `is_synthetic_simulated = TRUE` in the DuckDB data lakehouse and must retain this provenance label when exposed to Power BI, Streamlit, or external REST API consumers. Historical observations are derived from verified warehouse facts (`warehouse.fact_orders`).
