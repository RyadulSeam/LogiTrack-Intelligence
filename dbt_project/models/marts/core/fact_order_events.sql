{{ config(materialized='table') }}

SELECT
    e.event_id,
    e.order_id,
    e.event_type,
    e.event_timestamp,
    h.hub_key,
    d.driver_key,
    v.vehicle_key,
    e.data_origin
FROM realtime.order_events e
LEFT JOIN {{ ref('dim_hub') }} h ON e.hub_name = h.hub_name
LEFT JOIN {{ ref('dim_driver') }} d ON e.driver_id = d.driver_id
LEFT JOIN {{ ref('dim_vehicle') }} v ON e.vehicle_code = v.vehicle_code
