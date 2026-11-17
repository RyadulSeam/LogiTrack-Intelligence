{{ config(materialized='table') }}

WITH hub_pairs AS (
    SELECT
        h1.hub_id AS origin_hub_id,
        h2.hub_id AS destination_hub_id,
        h1.hub_name AS origin_name,
        h2.hub_name AS destination_name,
        h1.latitude AS lat1,
        h1.longitude AS lon1,
        h2.latitude AS lat2,
        h2.longitude AS lon2
    FROM {{ ref('stg_hubs') }} h1
    CROSS JOIN {{ ref('stg_hubs') }} h2
)
SELECT
    (origin_hub_id * 100 + destination_hub_id)::INTEGER AS route_key,
    origin_hub_id,
    destination_hub_id,
    CASE 
        WHEN origin_hub_id = destination_hub_id THEN 28.50
        ELSE ROUND(
            (6371 * 2 * ASIN(SQRT(
                POWER(SIN(RADIANS(lat2 - lat1) / 2), 2) +
                COS(RADIANS(lat1)) * COS(RADIANS(lat2)) *
                POWER(SIN(RADIANS(lon2 - lon1) / 2), 2)
            ))) * 1.18, 2
        )
    END AS distance_km,
    CASE
        WHEN origin_hub_id = destination_hub_id THEN 1.25
        ELSE ROUND(
            ((6371 * 2 * ASIN(SQRT(
                POWER(SIN(RADIANS(lat2 - lat1) / 2), 2) +
                COS(RADIANS(lat1)) * COS(RADIANS(lat2)) *
                POWER(SIN(RADIANS(lon2 - lon1) / 2), 2)
            ))) * 1.18) / 65.0, 2
        )
    END AS typical_duration_hours,
    CASE
        WHEN (origin_name LIKE '%Dallas%' AND destination_name LIKE '%Houston%') OR (origin_name LIKE '%Houston%' AND destination_name LIKE '%Dallas%') THEN 'I-45 Corridor'
        WHEN (origin_name LIKE '%Dallas%' AND destination_name LIKE '%Austin%') OR (origin_name LIKE '%Austin%' AND destination_name LIKE '%Dallas%') THEN 'I-35 Corridor'
        WHEN (origin_name LIKE '%Austin%' AND destination_name LIKE '%San Antonio%') OR (origin_name LIKE '%San Antonio%' AND destination_name LIKE '%Austin%') THEN 'I-35 South Corridor'
        WHEN (origin_name LIKE '%Houston%' AND destination_name LIKE '%San Antonio%') OR (origin_name LIKE '%San Antonio%' AND destination_name LIKE '%Houston%') THEN 'I-10 East Corridor'
        WHEN (origin_name LIKE '%San Antonio%' AND destination_name LIKE '%El Paso%') OR (origin_name LIKE '%El Paso%' AND destination_name LIKE '%San Antonio%') THEN 'I-10 West Corridor'
        WHEN origin_hub_id = destination_hub_id THEN 'Metro Intra-city Delivery'
        ELSE 'Regional Highway Freight'
    END AS corridor_name
FROM hub_pairs
