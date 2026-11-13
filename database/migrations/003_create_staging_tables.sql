-- ============================================================
-- Migration: 003_create_staging_tables.sql
-- Description: Staging (Silver) tables: standardized naming & explicit types
-- ============================================================

-- Staging Hubs
CREATE TABLE IF NOT EXISTS staging.stg_hubs (
    hub_id INTEGER PRIMARY KEY,
    hub_name VARCHAR(100) NOT NULL UNIQUE,
    hub_capacity INTEGER NOT NULL,
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    ingestion_batch_id VARCHAR(64),
    data_origin VARCHAR(50),
    stg_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging Drivers
CREATE TABLE IF NOT EXISTS staging.stg_drivers (
    driver_id INTEGER PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    employment_type VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    experience_years INTEGER NOT NULL,
    performance_rating INTEGER CHECK (performance_rating BETWEEN 1 AND 5),
    ingestion_batch_id VARCHAR(64),
    data_origin VARCHAR(50),
    stg_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging Vehicles
CREATE TABLE IF NOT EXISTS staging.stg_vehicles (
    vehicle_id INTEGER PRIMARY KEY,
    vehicle_code VARCHAR(20) NOT NULL UNIQUE,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_status VARCHAR(50) NOT NULL,
    breakdown_count INTEGER DEFAULT 0,
    is_maintenance_alert BOOLEAN NOT NULL,
    purchase_date DATE NOT NULL,
    ingestion_batch_id VARCHAR(64),
    data_origin VARCHAR(50),
    stg_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging Orders
CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id BIGINT PRIMARY KEY,
    order_date DATE NOT NULL,
    actual_delivery_date DATE,
    order_status VARCHAR(50) NOT NULL,
    is_delayed BOOLEAN NOT NULL,
    is_on_time BOOLEAN NOT NULL,
    delay_reason VARCHAR(255),
    driver_id INTEGER NOT NULL,
    driver_name_snapshot VARCHAR(100),
    hub_name VARCHAR(100) NOT NULL,
    vehicle_code VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    customer_satisfaction_score SMALLINT CHECK (customer_satisfaction_score BETWEEN 1 AND 5),
    delivery_time_hours DECIMAL(8, 2),
    hub_processing_time_hours DECIMAL(6, 2) NOT NULL,
    ingestion_batch_id VARCHAR(64),
    data_origin VARCHAR(50),
    stg_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
