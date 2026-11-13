{{ config(materialized='view') }}

SELECT
    hub_id,
    hub_name,
    hub_capacity,
    latitude,
    longitude,
    ingestion_batch_id,
    data_origin,
    stg_updated_at
FROM staging.stg_hubs
