{{ config(materialized='table') }}

SELECT
    o.order_id,
    CAST(strftime(o.order_date, '%Y%m%d') AS INTEGER) AS order_date_key,
    CASE 
        WHEN o.actual_delivery_date IS NOT NULL 
        THEN CAST(strftime(o.actual_delivery_date, '%Y%m%d') AS INTEGER)
        ELSE NULL 
    END AS delivery_date_key,
    h.hub_key,
    d.driver_key,
    v.vehicle_key,
    o.order_status,
    o.is_delayed,
    o.is_on_time,
    o.delay_reason,
    NULL::DECIMAL(8, 2) AS package_weight_kg,
    'Standard' AS delivery_priority,
    o.customer_satisfaction_score AS csat_score,
    o.delivery_time_hours,
    o.hub_processing_time_hours,
    o.data_origin,
    CURRENT_TIMESTAMP AS created_at
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_hub') }} h ON o.hub_name = h.hub_name
LEFT JOIN {{ ref('dim_driver') }} d ON o.driver_id = d.driver_id
LEFT JOIN {{ ref('dim_vehicle') }} v ON o.vehicle_code = v.vehicle_code
