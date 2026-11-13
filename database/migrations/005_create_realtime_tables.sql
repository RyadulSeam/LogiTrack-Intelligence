-- ============================================================
-- Migration: 005_create_realtime_tables.sql
-- Description: Realtime streaming state & ingestion dead-letter store
-- ============================================================

-- Vehicle Telemetry Stream State
CREATE TABLE IF NOT EXISTS realtime.vehicle_events (
    event_id VARCHAR(64) PRIMARY KEY,
    vehicle_code VARCHAR(20) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    speed_kmh DECIMAL(6, 2) NOT NULL,
    heading_deg DECIMAL(5, 1),
    fuel_level_pct DECIMAL(5, 2),
    engine_temp_c DECIMAL(5, 1),
    engine_status VARCHAR(20),
    data_origin VARCHAR(50) DEFAULT 'source: simulated',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Lifecycle Stream State
CREATE TABLE IF NOT EXISTS realtime.order_events (
    event_id VARCHAR(64) PRIMARY KEY,
    order_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    hub_name VARCHAR(100),
    driver_id INTEGER,
    vehicle_code VARCHAR(20),
    data_origin VARCHAR(50) DEFAULT 'source: simulated',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Driver Activity Stream State
CREATE TABLE IF NOT EXISTS realtime.driver_events (
    event_id VARCHAR(64) PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- Shift Start, Break, Active Assignment, Shift End
    event_timestamp TIMESTAMP NOT NULL,
    vehicle_code VARCHAR(20),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hub Stream Events
CREATE TABLE IF NOT EXISTS realtime.hub_events (
    event_id VARCHAR(64) PRIMARY KEY,
    hub_name VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    active_backlog INTEGER,
    throughput_rate_per_hr DECIMAL(6, 2),
    congestion_alert BOOLEAN DEFAULT FALSE,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dead Letter Queue & Ingestion Errors Store
CREATE TABLE IF NOT EXISTS realtime.ingestion_errors (
    error_id VARCHAR(64) PRIMARY KEY,
    source_topic VARCHAR(100),
    failed_payload TEXT,
    error_reason VARCHAR(255),
    error_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
