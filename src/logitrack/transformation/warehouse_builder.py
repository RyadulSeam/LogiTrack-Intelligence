"""
Enterprise Data Warehouse Builder
LogiTrack Intelligence — Phase 6

Transforms Silver (staging.*) records into Gold (warehouse.*) star schema models
in DuckDB and Neon PostgreSQL. Supports programmatic dbt execution.
"""

import subprocess
import sys
from pathlib import Path
from loguru import logger
from logitrack.storage.duckdb_manager import DuckDBManager


def build_warehouse_tables(db_path: str = "data/lake/logitrack.duckdb"):
    """
    Populates warehouse.* dimension and fact tables in DuckDB
    from staging.* and realtime.* schemas.
    """
    logger.info("Starting Gold layer warehouse transformation...")
    manager = DuckDBManager(db_path=db_path)

    # Clean existing data child-first to respect foreign key constraints
    logger.info("Clearing warehouse facts and dimensions in dependency order...")
    manager.conn.execute("DELETE FROM warehouse.fact_orders;")
    manager.conn.execute("DELETE FROM warehouse.fact_order_events;")
    manager.conn.execute("DELETE FROM warehouse.fact_vehicle_telemetry;")
    manager.conn.execute("DELETE FROM warehouse.fact_hub_hourly;")
    manager.conn.execute("DELETE FROM warehouse.dim_route;")
    manager.conn.execute("DELETE FROM warehouse.dim_vehicle;")
    manager.conn.execute("DELETE FROM warehouse.dim_driver;")
    manager.conn.execute("DELETE FROM warehouse.dim_hub;")
    manager.conn.execute("DELETE FROM warehouse.dim_date;")

    # 1. Populate dim_date (2023 to 2026)
    logger.info("Building warehouse.dim_date...")
    manager.conn.execute("""
        INSERT INTO warehouse.dim_date (
            date_key, full_date, day_of_week, day_name,
            day_of_month, month_number, month_name, quarter, year, is_weekend
        )
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
        FROM date_spine;
    """)

    # 2. Populate dim_hub
    logger.info("Building warehouse.dim_hub...")
    manager.conn.execute("""
        INSERT INTO warehouse.dim_hub (
            hub_key, hub_id, hub_name, city, state, daily_capacity, latitude, longitude, data_origin
        )
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
        FROM staging.stg_hubs;
    """)

    # 3. Populate dim_driver
    logger.info("Building warehouse.dim_driver...")
    manager.conn.execute("""
        INSERT INTO warehouse.dim_driver (
            driver_key, driver_id, driver_name, employment_type,
            hire_date, experience_years, performance_rating, data_origin
        )
        SELECT
            driver_id AS driver_key,
            driver_id,
            driver_name,
            employment_type,
            hire_date,
            experience_years,
            performance_rating,
            data_origin
        FROM staging.stg_drivers;
    """)

    # 4. Populate dim_vehicle
    logger.info("Building warehouse.dim_vehicle...")
    manager.conn.execute("""
        INSERT INTO warehouse.dim_vehicle (
            vehicle_key, vehicle_id, vehicle_code, vehicle_model,
            vehicle_type, current_status, lifetime_breakdowns,
            is_maintenance_alert, purchase_date, data_origin
        )
        SELECT
            vehicle_id AS vehicle_key,
            vehicle_id,
            vehicle_code,
            vehicle_model,
            CASE
                WHEN vehicle_model LIKE '%Freightliner%' THEN 'Truck'
                WHEN vehicle_model LIKE '%Isuzu%' THEN 'Box Truck'
                WHEN vehicle_model LIKE '%Silverado%' THEN 'Pickup'
                ELSE 'Van'
            END AS vehicle_type,
            vehicle_status AS current_status,
            breakdown_count AS lifetime_breakdowns,
            is_maintenance_alert,
            purchase_date,
            data_origin
        FROM staging.stg_vehicles;
    """)

    # 5. Populate dim_route
    logger.info("Building warehouse.dim_route...")
    manager.conn.execute("""
        INSERT INTO warehouse.dim_route (
            route_key, origin_hub_id, destination_hub_id,
            distance_km, typical_duration_hours, corridor_name
        )
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
            FROM staging.stg_hubs h1
            CROSS JOIN staging.stg_hubs h2
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
        FROM hub_pairs;
    """)

    # 6. Populate fact_orders
    logger.info("Building warehouse.fact_orders...")
    manager.conn.execute("""
        INSERT INTO warehouse.fact_orders (
            order_id, order_date_key, delivery_date_key,
            hub_key, driver_key, vehicle_key, order_status,
            is_delayed, is_on_time, delay_reason, package_weight_kg,
            delivery_priority, csat_score, delivery_time_hours,
            hub_processing_time_hours, data_origin, created_at
        )
        SELECT
            o.order_id,
            CAST(strftime(o.order_date, '%Y%m%d') AS INTEGER) AS order_date_key,
            CASE 
                WHEN o.actual_delivery_date IS NOT NULL 
                THEN CAST(strftime(o.actual_delivery_date, '%Y%m%d') AS INTEGER)
                ELSE NULL 
            END AS delivery_date_key,
            h.hub_key,
            d.driver_key,
            v.vehicle_key,
            o.order_status,
            o.is_delayed,
            o.is_on_time,
            o.delay_reason,
            NULL::DECIMAL(8, 2) AS package_weight_kg,
            'Standard' AS delivery_priority,
            o.customer_satisfaction_score AS csat_score,
            o.delivery_time_hours,
            o.hub_processing_time_hours,
            o.data_origin,
            CURRENT_TIMESTAMP AS created_at
        FROM staging.stg_orders o
        LEFT JOIN warehouse.dim_hub h ON o.hub_name = h.hub_name
        LEFT JOIN warehouse.dim_driver d ON o.driver_id = d.driver_id
        LEFT JOIN warehouse.dim_vehicle v ON o.vehicle_code = v.vehicle_code;
    """)

    # 7. Populate fact_order_events
    logger.info("Building warehouse.fact_order_events...")
    manager.conn.execute("""
        INSERT INTO warehouse.fact_order_events (
            event_id, order_id, event_type, event_timestamp,
            hub_key, driver_key, vehicle_key, data_origin
        )
        SELECT
            e.event_id,
            e.order_id,
            e.event_type,
            e.event_timestamp,
            h.hub_key,
            d.driver_key,
            v.vehicle_key,
            e.data_origin
        FROM realtime.order_events e
        LEFT JOIN warehouse.dim_hub h ON e.hub_name = h.hub_name
        LEFT JOIN warehouse.dim_driver d ON e.driver_id = d.driver_id
        LEFT JOIN warehouse.dim_vehicle v ON e.vehicle_code = v.vehicle_code;
    """)

    # 8. Populate fact_vehicle_telemetry
    logger.info("Building warehouse.fact_vehicle_telemetry...")
    manager.conn.execute("""
        INSERT INTO warehouse.fact_vehicle_telemetry (
            telemetry_id, vehicle_key, ping_timestamp, latitude,
            longitude, speed_kmh, heading_deg, fuel_level_pct,
            engine_temp_c, engine_status, data_origin
        )
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
        LEFT JOIN warehouse.dim_vehicle v ON t.vehicle_code = v.vehicle_code;
    """)

    # 9. Populate fact_hub_hourly
    logger.info("Building warehouse.fact_hub_hourly...")
    manager.conn.execute("""
        INSERT INTO warehouse.fact_hub_hourly (
            hub_hourly_id, hub_key, date_key, hour_of_day,
            orders_received, orders_dispatched, avg_processing_time_hours,
            backlog_volume, capacity_utilization_pct
        )
        WITH order_hourly AS (
            SELECT
                h.hub_key,
                CAST(strftime(o.order_date, '%Y%m%d') AS INTEGER) AS date_key,
                EXTRACT(HOUR FROM o.stg_updated_at)::SMALLINT AS hour_of_day,
                COUNT(o.order_id) AS orders_received,
                SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS orders_dispatched,
                ROUND(AVG(o.hub_processing_time_hours), 2) AS avg_processing_time_hours,
                SUM(CASE WHEN o.order_status != 'Delivered' THEN 1 ELSE 0 END) AS backlog_volume
            FROM staging.stg_orders o
            JOIN warehouse.dim_hub h ON o.hub_name = h.hub_name
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
        JOIN warehouse.dim_hub dh ON oh.hub_key = dh.hub_key;
    """)

    counts = {
        "dim_date": manager.query("SELECT COUNT(*) FROM warehouse.dim_date").iloc[0, 0],
        "dim_hub": manager.query("SELECT COUNT(*) FROM warehouse.dim_hub").iloc[0, 0],
        "dim_driver": manager.query("SELECT COUNT(*) FROM warehouse.dim_driver").iloc[0, 0],
        "dim_vehicle": manager.query("SELECT COUNT(*) FROM warehouse.dim_vehicle").iloc[0, 0],
        "dim_route": manager.query("SELECT COUNT(*) FROM warehouse.dim_route").iloc[0, 0],
        "fact_orders": manager.query("SELECT COUNT(*) FROM warehouse.fact_orders").iloc[0, 0],
        "fact_order_events": manager.query("SELECT COUNT(*) FROM warehouse.fact_order_events").iloc[0, 0],
        "fact_vehicle_telemetry": manager.query("SELECT COUNT(*) FROM warehouse.fact_vehicle_telemetry").iloc[0, 0],
        "fact_hub_hourly": manager.query("SELECT COUNT(*) FROM warehouse.fact_hub_hourly").iloc[0, 0],
    }
    manager.close()
    logger.success(f"Warehouse build complete! Rows: {counts}")
    return counts


def run_dbt_cli(command: str = "run"):
    """Runs dbt command against local DuckDB project."""
    dbt_dir = Path("dbt_project")
    venv_dbt = Path(".venv/Scripts/dbt.exe")
    dbt_cmd = str(venv_dbt) if venv_dbt.exists() else "dbt"

    logger.info(f"Running '{dbt_cmd} {command}' in {dbt_dir}...")
    result = subprocess.run(
        [dbt_cmd, command, "--profiles-dir", "."],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        logger.success(f"dbt {command} succeeded!")
    else:
        logger.warning(f"dbt {command} exited with code {result.returncode}:\n{result.stderr}")
    return result


if __name__ == "__main__":
    build_warehouse_tables()
