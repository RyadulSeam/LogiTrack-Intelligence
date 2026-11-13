{{ config(materialized='view') }}

SELECT
    order_id,
    order_date,
    actual_delivery_date,
    order_status,
    is_delayed,
    is_on_time,
    delay_reason,
    driver_id,
    driver_name_snapshot,
    hub_name,
    vehicle_code,
    vehicle_type,
    customer_satisfaction_score,
    delivery_time_hours,
    hub_processing_time_hours,
    ingestion_batch_id,
    data_origin,
    stg_updated_at
FROM staging.stg_orders
