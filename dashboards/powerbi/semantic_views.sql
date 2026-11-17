-- ============================================================
-- Power BI Semantic Layer Views & Direct Queries
-- LogiTrack Intelligence — Phase 7
-- ============================================================

-- View 1: Executive KPI Summary
CREATE OR REPLACE VIEW warehouse.vw_powerbi_executive_summary AS
SELECT
    f.order_id,
    d.full_date AS order_date,
    deliv_d.full_date AS delivery_date,
    h.hub_name,
    h.city AS hub_city,
    dr.driver_name,
    dr.employment_type AS driver_type,
    v.vehicle_code,
    v.vehicle_type,
    f.order_status,
    f.is_delayed,
    f.is_on_time,
    f.delay_reason,
    f.csat_score,
    f.delivery_time_hours,
    f.hub_processing_time_hours,
    f.data_origin
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON f.order_date_key = d.date_key
LEFT JOIN warehouse.dim_date deliv_d ON f.delivery_date_key = deliv_d.date_key
JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
JOIN warehouse.dim_driver dr ON f.driver_key = dr.driver_key
JOIN warehouse.dim_vehicle v ON f.vehicle_key = v.vehicle_key;

-- View 2: Fleet Telematics & Asset Utilization
CREATE OR REPLACE VIEW warehouse.vw_powerbi_fleet_performance AS
SELECT
    v.vehicle_code,
    v.vehicle_model,
    v.vehicle_type,
    v.current_status,
    v.lifetime_breakdowns,
    v.is_maintenance_alert,
    COUNT(f.order_id) AS total_orders_assigned,
    ROUND(AVG(f.delivery_time_hours), 2) AS avg_delivery_time_hours
FROM warehouse.dim_vehicle v
LEFT JOIN warehouse.fact_orders f ON v.vehicle_key = f.vehicle_key
GROUP BY
    v.vehicle_code, v.vehicle_model, v.vehicle_type,
    v.current_status, v.lifetime_breakdowns, v.is_maintenance_alert;
