{{ config(materialized='view') }}

SELECT
    driver_id,
    driver_name,
    employment_type,
    hire_date,
    experience_years,
    performance_rating,
    ingestion_batch_id,
    data_origin,
    stg_updated_at
FROM staging.stg_drivers
