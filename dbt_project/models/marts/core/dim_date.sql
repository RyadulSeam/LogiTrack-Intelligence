{{ config(materialized='table') }}

WITH date_spine AS (
    SELECT UNNEST(generate_series(DATE '2023-01-01', DATE '2026-12-31', INTERVAL 1 DAY))::DATE AS full_date
)
SELECT
    CAST(strftime(full_date, '%Y%m%d') AS INTEGER) AS date_key,
    full_date,
    EXTRACT(DOW FROM full_date)::SMALLINT AS day_of_week,
    strftime(full_date, '%A') AS day_name,
    EXTRACT(DAY FROM full_date)::SMALLINT AS day_of_month,
    EXTRACT(MONTH FROM full_date)::SMALLINT AS month_number,
    strftime(full_date, '%B') AS month_name,
    EXTRACT(QUARTER FROM full_date)::SMALLINT AS quarter,
    EXTRACT(YEAR FROM full_date)::INTEGER AS year,
    CASE WHEN EXTRACT(DOW FROM full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM date_spine
