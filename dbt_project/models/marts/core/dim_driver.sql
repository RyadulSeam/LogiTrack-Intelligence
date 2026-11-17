{{ config(materialized='table') }}

SELECT
    driver_id AS driver_key,
    driver_id,
    driver_name,
    employment_type,
    hire_date,
    experience_years,
    performance_rating,
    data_origin
FROM {{ ref('stg_drivers') }}
