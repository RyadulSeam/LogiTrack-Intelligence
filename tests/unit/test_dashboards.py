"""
Dashboard & BI Metrics Unit Tests
LogiTrack Intelligence — Phase 7

Tests KPI calculation formulas, DuckDB analytical loader queries,
and data structure integrity for BI dashboards.
"""

import pytest
from logitrack.analytics.metrics import (
    calculate_otd_rate,
    calculate_delay_rate,
    get_executive_kpis,
    get_hub_performance_summary,
    get_delay_root_causes
)


def test_calculate_otd_rate_standard():
    rate = calculate_otd_rate(80, 100)
    assert rate == 80.0


def test_calculate_otd_rate_zero_division():
    assert calculate_otd_rate(0, 0) == 0.0
    assert calculate_otd_rate(5, -1) == 0.0


def test_calculate_delay_rate_standard():
    rate = calculate_delay_rate(20, 100)
    assert rate == 20.0


def test_executive_kpis_contract():
    kpis = get_executive_kpis()
    required_keys = [
        "total_orders", "delivered_orders", "on_time_delivery_rate_pct",
        "delay_rate_pct", "avg_delivery_time_hours", "fleet_utilization_pct",
        "maintenance_alerts"
    ]
    for key in required_keys:
        assert key in kpis, f"Missing key in executive KPIs: {key}"
        assert kpis[key] is not None

    assert kpis["total_orders"] == 27979
    assert 0 <= kpis["on_time_delivery_rate_pct"] <= 100.0
    assert 0 <= kpis["delay_rate_pct"] <= 100.0


def test_hub_performance_summary():
    df = get_hub_performance_summary()
    assert len(df) == 6
    assert "hub_name" in df.columns
    assert "total_orders" in df.columns
    assert df["total_orders"].sum() == 27979


def test_delay_root_causes_summary():
    df = get_delay_root_causes()
    assert len(df) > 0
    assert "delay_reason" in df.columns
    assert "incident_count" in df.columns
    assert df["incident_count"].sum() > 0
