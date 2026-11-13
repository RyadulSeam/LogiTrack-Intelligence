-- ============================================================
-- Migration: 001_create_schemas.sql
-- Description: Creates 5 logical schemas for Medallion Architecture
-- ============================================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS realtime;
CREATE SCHEMA IF NOT EXISTS ml;
