-- ============================================================
-- Migration: 002_create_raw_tables.sql
-- Description: Raw (Bronze) tables capturing exact source representations
-- ============================================================

-- Raw Hubs
CREATE TABLE IF NOT EXISTS raw.raw_hubs (
    hub_id VARCHAR(50),
    hub_name VARCHAR(100),
    hub_capacity VARCHAR(50),
    -- Lineage metadata
    ingestion_batch_id VARCHAR(64),
    source_file VARCHAR(255),
    data_origin VARCHAR(50) DEFAULT 'source: original',
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Drivers
CREATE TABLE IF NOT EXISTS raw.raw_drivers (
    driver_id VARCHAR(50),
    driver_name VARCHAR(100),
    employment_type VARCHAR(50),
    hire_date VARCHAR(50),
    experience_years VARCHAR(50),
    performance_rating VARCHAR(50),
    -- Lineage metadata
    ingestion_batch_id VARCHAR(64),
    source_file VARCHAR(255),
    data_origin VARCHAR(50) DEFAULT 'source: original',
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Vehicles
CREATE TABLE IF NOT EXISTS raw.raw_vehicles (
    purchase_date VARCHAR(50),
    vehicle_id VARCHAR(50),
    vehicle_model VARCHAR(100),
    vehicle_status VARCHAR(50),
    breakdown VARCHAR(50),
    maintenance_count_alert VARCHAR(50),
    vehicle_code VARCHAR(50),
    -- Lineage metadata
    ingestion_batch_id VARCHAR(64),
    source_file VARCHAR(255),
    data_origin VARCHAR(50) DEFAULT 'source: original',
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Orders
CREATE TABLE IF NOT EXISTS raw.raw_orders (
    order_id VARCHAR(50),
    actual_delivery_date VARCHAR(50),
    delay_reason VARCHAR(255),
    driver_id VARCHAR(50),
    driver_name VARCHAR(100),
    hub_name VARCHAR(100),
    is_delayed VARCHAR(50),
    is_on_time VARCHAR(50),
    order_date VARCHAR(50),
    order_status VARCHAR(50),
    vehicle_name VARCHAR(50),
    vehicle_type VARCHAR(50),
    customer_satisfaction_score VARCHAR(50),
    delivery_time_hours VARCHAR(50),
    hub_processing_time_hours VARCHAR(50),
    -- Lineage metadata
    ingestion_batch_id VARCHAR(64),
    source_file VARCHAR(255),
    data_origin VARCHAR(50) DEFAULT 'source: original',
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
