{{ config(materialized='table') }}

WITH order_hourly AS (
    SELECT
        h.hub_key,
        CAST(strftime(o.order_date, '%Y%m%d') AS INTEGER) AS date_key,
        EXTRACT(HOUR FROM o.stg_updated_at)::SMALLINT AS hour_of_day,
        COUNT(o.order_id) AS orders_received,
        SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS orders_dispatched,
        ROUND(AVG(o.hub_processing_time_hours), 2) AS avg_processing_time_hours,
        SUM(CASE WHEN o.order_status != 'Delivered' THEN 1 ELSE 0 END) AS backlog_volume
    FROM {{ ref('stg_orders') }} o
    JOIN {{ ref('dim_hub') }} h ON o.hub_name = h.hub_name
    GROUP BY h.hub_key, date_key, hour_of_day
)
SELECT
    MD5(CONCAT(oh.hub_key::VARCHAR, '_', oh.date_key::VARCHAR, '_', oh.hour_of_day::VARCHAR)) AS hub_hourly_id,
    oh.hub_key,
    oh.date_key,
    oh.hour_of_day,
    oh.orders_received,
    oh.orders_dispatched,
    oh.avg_processing_time_hours,
    oh.backlog_volume,
    ROUND((oh.orders_received::DECIMAL / NULLIF(dh.daily_capacity, 0)) * 100, 2) AS capacity_utilization_pct
FROM order_hourly oh
JOIN {{ ref('dim_hub') }} dh ON oh.hub_key = dh.hub_key
