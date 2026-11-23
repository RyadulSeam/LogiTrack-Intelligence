-- ========================================================================================
-- LogiTrack Intelligence — Enterprise SQL Semantic Layer & Analytical Marts
-- Target Environments: DuckDB Analytical Lakehouse / PostgreSQL Enterprise Warehouse
-- Schema: warehouse
-- Purpose: Direct Query and Import Semantic Views for Power BI Desktop & Service
-- ========================================================================================

-- Ensure warehouse schema exists
CREATE SCHEMA IF NOT EXISTS warehouse;

-- ----------------------------------------------------------------------------------------
-- View 1: Executive Control Tower Order Fulfillment Mart
-- Grain: One record per operational delivery order (27,979 rows)
-- Primary Visuals: Executive KPI Cards, Monthly Fulfillment Trend, Hub SLA Scorecard
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_executive_control_tower AS
SELECT
    f.order_id,
    f.order_date_key,
    d_order.full_date                     AS order_date,
    d_order.year                          AS order_year,
    d_order.quarter_name                  AS order_quarter,
    d_order.month_name                    AS order_month,
    d_order.month_number                  AS order_month_number,
    f.delivery_date_key,
    d_deliv.full_date                     AS delivery_date,
    f.hub_key,
    h.hub_name                            AS origin_hub_name,
    h.city                                AS origin_hub_city,
    h.state                               AS origin_hub_state,
    h.daily_capacity                      AS hub_daily_capacity,
    f.driver_key,
    dr.driver_name,
    dr.employment_type                    AS driver_employment_type,
    dr.experience_years                   AS driver_experience_years,
    dr.performance_rating                 AS driver_performance_rating,
    f.vehicle_key,
    v.vehicle_code,
    v.vehicle_type,
    v.vehicle_model,
    v.current_status                      AS vehicle_status,
    f.order_status,
    CASE WHEN f.order_status = 'Delivered' THEN 1 ELSE 0 END AS is_delivered_flag,
    CASE WHEN f.order_status = 'Cancelled' THEN 1 ELSE 0 END AS is_cancelled_flag,
    f.is_on_time,
    f.is_delayed,
    f.delay_reason,
    COALESCE(f.delay_reason, 'On-Time / No Delay') AS delay_reason_label,
    f.delivery_time_hours,
    f.hub_processing_time_hours,
    ROUND(f.delivery_time_hours + f.hub_processing_time_hours, 2) AS total_fulfillment_hours,
    f.csat_score,
    f.data_origin
FROM warehouse.fact_orders f
LEFT JOIN warehouse.dim_date d_order  ON f.order_date_key = d_order.date_key
LEFT JOIN warehouse.dim_date d_deliv  ON f.delivery_date_key = d_deliv.date_key
LEFT JOIN warehouse.dim_hub h         ON f.hub_key = h.hub_key
LEFT JOIN warehouse.dim_driver dr     ON f.driver_key = dr.driver_key
LEFT JOIN warehouse.dim_vehicle v     ON f.vehicle_key = v.vehicle_key;


-- ----------------------------------------------------------------------------------------
-- View 2: Regional Hub Hourly Operations & Bottleneck Analytics
-- Grain: One record per Hub per Date per Hour
-- Primary Visuals: Capacity vs Volume Column Chart, 24-Hour Rhythm Line Chart, Hub Matrix
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_hub_hourly_operations AS
SELECT
    hh.hub_hourly_id,
    hh.hub_key,
    h.hub_name,
    h.city                                AS hub_city,
    h.daily_capacity                      AS designed_daily_capacity,
    hh.date_key,
    d.full_date                           AS operation_date,
    d.month_name                          AS operation_month,
    hh.hour_of_day,
    CASE 
        WHEN hh.hour_of_day < 6  THEN 'Night (00:00 - 06:00)'
        WHEN hh.hour_of_day < 12 THEN 'Morning (06:00 - 12:00)'
        WHEN hh.hour_of_day < 18 THEN 'Afternoon (12:00 - 18:00)'
        ELSE 'Evening (18:00 - 24:00)'
    END                                   AS time_of_day_band,
    hh.orders_received,
    hh.orders_dispatched,
    hh.backlog_volume,
    hh.avg_processing_time_hours,
    hh.capacity_utilization_pct,
    CASE 
        WHEN hh.capacity_utilization_pct >= 85.0 THEN 1 
        ELSE 0 
    END                                   AS is_bottleneck_alert
FROM warehouse.fact_hub_hourly hh
JOIN warehouse.dim_hub h ON hh.hub_key = h.hub_key
JOIN warehouse.dim_date d ON hh.date_key = d.date_key;


-- ----------------------------------------------------------------------------------------
-- View 3: Delivery Delay & Root-Cause Analytics Mart
-- Grain: One record per Delivered Order with Delay Diagnostics
-- Primary Visuals: Pareto Delay Reason Chart, Vehicle Delay Rate Bar Chart, Delay Incident Feed
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_delay_root_cause_analytics AS
SELECT
    f.order_id,
    d.full_date                           AS order_date,
    h.hub_name                            AS origin_hub,
    v.vehicle_code,
    v.vehicle_type,
    dr.driver_name,
    f.order_status,
    f.is_delayed,
    f.is_on_time,
    f.delay_reason,
    f.delivery_time_hours,
    f.hub_processing_time_hours,
    -- Benchmark variance: Difference from planned SLA (planned average: 24.0 hours)
    ROUND(f.delivery_time_hours - 24.0, 2) AS sla_duration_variance_hours,
    f.csat_score
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON f.order_date_key = d.date_key
JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
JOIN warehouse.dim_driver dr ON f.driver_key = dr.driver_key
JOIN warehouse.dim_vehicle v ON f.vehicle_key = v.vehicle_key
WHERE f.order_status = 'Delivered';


-- ----------------------------------------------------------------------------------------
-- View 4: Fleet Telematics, Asset Health & Predictive Maintenance Mart
-- Grain: One record per commercial fleet vehicle (45 units)
-- Primary Visuals: Fleet Status Donut, Age vs Breakdowns Scatter, Maintenance Watchlist
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_fleet_telematics_maintenance AS
SELECT
    v.vehicle_key,
    v.vehicle_code,
    v.vehicle_type,
    v.vehicle_model,
    v.purchase_date,
    DATEDIFF('day', v.purchase_date, CAST('2026-11-18' AS DATE)) AS vehicle_age_days,
    v.current_status,
    v.lifetime_breakdowns,
    v.is_maintenance_alert,
    COUNT(DISTINCT f.order_id)           AS total_orders_completed,
    ROUND(AVG(f.delivery_time_hours), 2) AS avg_delivery_transit_hours,
    COUNT(DISTINCT m.maintenance_id)     AS total_maintenance_events,
    COALESCE(SUM(m.cost_usd), 0.0)       AS total_maintenance_cost_usd,
    COALESCE(SUM(m.downtime_hours), 0.0) AS total_downtime_hours,
    CASE
        WHEN v.is_maintenance_alert = TRUE OR v.lifetime_breakdowns >= 4 THEN 'Critical Action'
        WHEN v.current_status = 'Maintenance' THEN 'In Depot Service'
        ELSE 'Road Ready'
    END                                  AS operational_readiness_status
FROM warehouse.dim_vehicle v
LEFT JOIN warehouse.fact_orders f ON v.vehicle_key = f.vehicle_key AND f.order_status = 'Delivered'
LEFT JOIN warehouse.fact_maintenance m ON v.vehicle_key = m.vehicle_key
GROUP BY
    v.vehicle_key,
    v.vehicle_code,
    v.vehicle_type,
    v.vehicle_model,
    v.purchase_date,
    v.current_status,
    v.lifetime_breakdowns,
    v.is_maintenance_alert;


-- ----------------------------------------------------------------------------------------
-- View 5: Driver Performance & SLA Compliance Scorecard
-- Grain: One record per certified delivery driver (55 drivers)
-- Primary Visuals: Driver Experience vs OTD Scatter, Driver Ranking Table
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_driver_scorecard AS
SELECT
    dr.driver_key,
    dr.driver_name,
    dr.employment_type,
    dr.hire_date,
    dr.experience_years,
    dr.performance_rating,
    COUNT(f.order_id)                     AS total_assigned_orders,
    SUM(CASE WHEN f.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    SUM(CASE WHEN f.is_on_time = TRUE AND f.order_status = 'Delivered' THEN 1 ELSE 0 END) AS on_time_deliveries,
    SUM(CASE WHEN f.is_delayed = TRUE AND f.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delayed_deliveries,
    ROUND(
        DIVIDE(
            SUM(CASE WHEN f.is_on_time = TRUE AND f.order_status = 'Delivered' THEN 1.0 ELSE 0.0 END),
            NULLIF(SUM(CASE WHEN f.order_status = 'Delivered' THEN 1.0 ELSE 0.0 END), 0),
            0.0
        ) * 100.0,
        2
    )                                     AS on_time_delivery_rate_pct,
    ROUND(AVG(f.delivery_time_hours), 2)  AS avg_delivery_time_hours,
    ROUND(AVG(f.csat_score), 2)           AS avg_driver_csat_score
FROM warehouse.dim_driver dr
LEFT JOIN warehouse.fact_orders f ON dr.driver_key = f.driver_key
GROUP BY
    dr.driver_key,
    dr.driver_name,
    dr.employment_type,
    dr.hire_date,
    dr.experience_years,
    dr.performance_rating;


-- ----------------------------------------------------------------------------------------
-- View 6: Machine Learning Real-Time Risk Predictions Feed
-- Grain: One record per predicted order event
-- Primary Visuals: ML Delay Risk Prediction Feed Table
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_predictive_ml_feed AS
SELECT
    ml.prediction_id,
    ml.model_name,
    ml.order_id,
    f.order_status,
    f.is_delayed                          AS actual_is_delayed,
    ml.predicted_label,
    ml.predicted_score,
    -- Prediction accuracy verification
    CASE
        WHEN ml.predicted_label = 'DELAY_RISK' AND f.is_delayed = TRUE THEN 'True Positive'
        WHEN ml.predicted_label = 'ON_TIME' AND f.is_delayed = FALSE THEN 'True Negative'
        WHEN ml.predicted_label = 'DELAY_RISK' AND f.is_delayed = FALSE THEN 'False Positive'
        ELSE 'False Negative'
    END                                   AS ml_accuracy_classification,
    ml.prediction_timestamp
FROM warehouse.fact_ml_predictions ml
LEFT JOIN warehouse.fact_orders f ON ml.order_id = f.order_id;


-- ----------------------------------------------------------------------------------------
-- View 7: Enterprise Calendar & Date Dimension Mart
-- Grain: One record per calendar date
-- ----------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.vw_pbi_dim_date_calendar AS
SELECT
    date_key,
    full_date,
    day_of_month,
    month_number,
    month_name,
    quarter_number,
    quarter_name,
    year,
    day_of_week_number,
    day_of_week_name,
    is_weekend,
    is_holiday
FROM warehouse.dim_date;

-- ========================================================================================
-- End of LogiTrack Intelligence Power BI Semantic Layer Views
-- ========================================================================================
