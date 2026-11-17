{{ config(materialized='table') }}

SELECT
    hub_id AS hub_key,
    hub_id,
    hub_name,
    CASE 
        WHEN hub_name LIKE '%Dallas%' THEN 'Dallas'
        WHEN hub_name LIKE '%Houston%' THEN 'Houston'
        WHEN hub_name LIKE '%Austin%' THEN 'Austin'
        WHEN hub_name LIKE '%San Antonio%' THEN 'San Antonio'
        WHEN hub_name LIKE '%Fort Worth%' THEN 'Fort Worth'
        WHEN hub_name LIKE '%El Paso%' THEN 'El Paso'
        ELSE 'Texas'
    END AS city,
    'TX' AS state,
    hub_capacity AS daily_capacity,
    latitude,
    longitude,
    data_origin
FROM {{ ref('stg_hubs') }}
