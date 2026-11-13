-- ============================================================
-- Migration: 004_create_warehouse_tables.sql
-- Description: Warehouse (Gold) tables: Dimensions & Facts (Star Schema)
-- ============================================================

-- Date Dimension
CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key INTEGER PRIMARY KEY, -- YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    day_of_month SMALLINT NOT NULL,
    month_number SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter SMALLINT NOT NULL,
    year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Hub Dimension
CREATE TABLE IF NOT EXISTS warehouse.dim_hub (
    hub_key INTEGER PRIMARY KEY,
    hub_id INTEGER NOT NULL UNIQUE,
    hub_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(10) DEFAULT 'TX',
    daily_capacity INTEGER NOT NULL,
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    data_origin VARCHAR(50)
);

-- Driver Dimension
CREATE TABLE IF NOT EXISTS warehouse.dim_driver (
    driver_key INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL UNIQUE,
    driver_name VARCHAR(100) NOT NULL,
    employment_type VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    experience_years INTEGER NOT NULL,
    performance_rating INTEGER,
    data_origin VARCHAR(50)
);

-- Vehicle Dimension
CREATE TABLE IF NOT EXISTS warehouse.dim_vehicle (
    vehicle_key INTEGER PRIMARY KEY,
    vehicle_id INTEGER NOT NULL UNIQUE,
    vehicle_code VARCHAR(20) NOT NULL UNIQUE,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    current_status VARCHAR(50) NOT NULL,
    lifetime_breakdowns INTEGER DEFAULT 0,
    is_maintenance_alert BOOLEAN NOT NULL,
    purchase_date DATE NOT NULL,
    data_origin VARCHAR(50)
);

-- Route Dimension
CREATE TABLE IF NOT EXISTS warehouse.dim_route (
    route_key INTEGER PRIMARY KEY,
    origin_hub_id INTEGER NOT NULL,
    destination_hub_id INTEGER NOT NULL,
    distance_km DECIMAL(8, 2) NOT NULL,
    typical_duration_hours DECIMAL(6, 2),
    corridor_name VARCHAR(100)
);

-- Orders Fact Table
CREATE TABLE IF NOT EXISTS warehouse.fact_orders (
    order_id BIGINT PRIMARY KEY,
    order_date_key INTEGER REFERENCES warehouse.dim_date(date_key),
    delivery_date_key INTEGER REFERENCES warehouse.dim_date(date_key),
    hub_key INTEGER REFERENCES warehouse.dim_hub(hub_key),
    driver_key INTEGER REFERENCES warehouse.dim_driver(driver_key),
    vehicle_key INTEGER REFERENCES warehouse.dim_vehicle(vehicle_key),
    order_status VARCHAR(50) NOT NULL,
    is_delayed BOOLEAN NOT NULL,
    is_on_time BOOLEAN NOT NULL,
    delay_reason VARCHAR(255),
    package_weight_kg DECIMAL(8, 2),
    delivery_priority VARCHAR(30),
    csat_score SMALLINT,
    delivery_time_hours DECIMAL(8, 2),
    hub_processing_time_hours DECIMAL(6, 2) NOT NULL,
    data_origin VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Events Fact Table (Grain: 1 row per lifecycle state transition)
CREATE TABLE IF NOT EXISTS warehouse.fact_order_events (
    event_id VARCHAR(64) PRIMARY KEY,
    order_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    hub_key INTEGER REFERENCES warehouse.dim_hub(hub_key),
    driver_key INTEGER REFERENCES warehouse.dim_driver(driver_key),
    vehicle_key INTEGER REFERENCES warehouse.dim_vehicle(vehicle_key),
    data_origin VARCHAR(50) NOT NULL
);

-- Vehicle Telemetry Fact Table (Grain: 1 row per vehicle GPS ping)
CREATE TABLE IF NOT EXISTS warehouse.fact_vehicle_telemetry (
    telemetry_id VARCHAR(64) PRIMARY KEY,
    vehicle_key INTEGER REFERENCES warehouse.dim_vehicle(vehicle_key),
    ping_timestamp TIMESTAMP NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    speed_kmh DECIMAL(6, 2) NOT NULL,
    heading_deg DECIMAL(5, 1),
    fuel_level_pct DECIMAL(5, 2),
    engine_temp_c DECIMAL(5, 1),
    engine_status VARCHAR(20),
    data_origin VARCHAR(50) NOT NULL
);

-- Vehicle Maintenance Fact Table
CREATE TABLE IF NOT EXISTS warehouse.fact_maintenance (
    maintenance_id VARCHAR(64) PRIMARY KEY,
    vehicle_key INTEGER REFERENCES warehouse.dim_vehicle(vehicle_key),
    service_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    scheduled_timestamp TIMESTAMP NOT NULL,
    completed_timestamp TIMESTAMP,
    downtime_hours DECIMAL(6, 2),
    cost_usd DECIMAL(10, 2),
    data_origin VARCHAR(50) NOT NULL
);

-- Hourly Hub Aggregates Fact
CREATE TABLE IF NOT EXISTS warehouse.fact_hub_hourly (
    hub_hourly_id VARCHAR(64) PRIMARY KEY,
    hub_key INTEGER REFERENCES warehouse.dim_hub(hub_key),
    date_key INTEGER REFERENCES warehouse.dim_date(date_key),
    hour_of_day SMALLINT NOT NULL,
    orders_received INTEGER DEFAULT 0,
    orders_dispatched INTEGER DEFAULT 0,
    avg_processing_time_hours DECIMAL(6, 2),
    backlog_volume INTEGER DEFAULT 0,
    capacity_utilization_pct DECIMAL(5, 2)
);
