{{ config(materialized='table') }}

SELECT
    t.event_id AS telemetry_id,
    v.vehicle_key,
    t.event_timestamp AS ping_timestamp,
    t.latitude,
    t.longitude,
    t.speed_kmh,
    t.heading_deg,
    t.fuel_level_pct,
    t.engine_temp_c,
    t.engine_status,
    t.data_origin
FROM realtime.vehicle_events t
LEFT JOIN {{ ref('dim_vehicle') }} v ON t.vehicle_code = v.vehicle_code
