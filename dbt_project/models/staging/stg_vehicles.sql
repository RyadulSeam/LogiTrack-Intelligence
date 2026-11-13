{{ config(materialized='view') }}

SELECT
    vehicle_id,
    vehicle_code,
    vehicle_model,
    vehicle_status,
    breakdown_count,
    is_maintenance_alert,
    purchase_date,
    ingestion_batch_id,
    data_origin,
    stg_updated_at
FROM staging.stg_vehicles
