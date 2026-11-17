{{ config(materialized='table') }}

SELECT
    vehicle_id AS vehicle_key,
    vehicle_id,
    vehicle_code,
    vehicle_model,
    CASE
        WHEN vehicle_model LIKE '%Freightliner%' THEN 'Truck'
        WHEN vehicle_model LIKE '%Isuzu%' THEN 'Box Truck'
        WHEN vehicle_model LIKE '%Silverado%' THEN 'Pickup'
        ELSE 'Van'
    END AS vehicle_type,
    vehicle_status AS current_status,
    breakdown_count AS lifetime_breakdowns,
    is_maintenance_alert,
    purchase_date,
    data_origin
FROM {{ ref('stg_vehicles') }}
