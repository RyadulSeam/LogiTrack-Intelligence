"""
Unit & Integration Tests for LogiTrack Intelligence FastAPI Endpoints
Phase 10: API & Application Layer
"""

import pytest
from fastapi.testclient import TestClient
from logitrack.api.main import app

client = TestClient(app)


def test_health_check():
    """Validates /health returns 200 and healthy lakehouse connection."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["database"] == "CONNECTED"
    assert data["version"] == "1.0.0"


def test_executive_kpis():
    """Validates /api/v1/kpis/executive returns accurate baseline metrics."""
    response = client.get("/api/v1/kpis/executive")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 27979
    assert data["delivered_orders"] == 27727
    assert data["cancelled_orders"] == 252
    assert abs(data["on_time_delivery_rate_pct"] - 79.6) <= 0.1
    assert abs(data["delay_rate_pct"] - 20.4) <= 0.1
    assert data["total_fleet"] == 45
    assert data["active_fleet"] == 33


def test_executive_kpis_filtered():
    """Validates /api/v1/kpis/executive with hub_name filter."""
    response = client.get("/api/v1/kpis/executive?hub_name=Dallas+Main+Hub")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] > 0
    assert data["delivered_orders"] > 0


def test_hubs_endpoint():
    """Validates /api/v1/hubs returns all 6 regional hubs."""
    response = client.get("/api/v1/hubs")
    assert response.status_code == 200
    data = response.json()
    assert data["total_hubs"] == 6
    hub_names = [h["hub_name"] for h in data["hubs"]]
    assert "Dallas Main Hub" in hub_names
    assert "Houston Hub" in hub_names
    assert "Austin Hub" in hub_names
    assert "San Antonio Hub" in hub_names
    assert "Fort Worth Hub" in hub_names
    assert "El Paso Hub" in hub_names
    for hub in data["hubs"]:
        assert hub["daily_capacity"] > 0
        assert hub["latitude"] > 0
        assert hub["longitude"] < 0


def test_fleet_endpoint():
    """Validates /api/v1/fleet returns telematics records for active fleet assets."""
    response = client.get("/api/v1/fleet")
    assert response.status_code == 200
    data = response.json()
    assert data["total_fleet"] == 41
    assert data["active_fleet"] == 30
    assert len(data["vehicles"]) == 41


def test_ml_predict_delay():
    """Validates POST /api/v1/ml/predict-delay returns inference scoring."""
    payload = {
        "distance_km": 120.5,
        "planned_duration_hours": 24.0,
        "package_weight_kg": 15.0,
        "delivery_priority": "High",
        "vehicle_type": "Van",
        "driver_experience_years": 4,
        "driver_rating": 4.8,
        "is_weekend": False,
        "hub_id": "HUB-DAL-01"
    }
    response = client.post("/api/v1/ml/predict-delay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data
    assert "delay_probability_pct" in data
    assert data["predicted_label"] in ["ON_TIME", "DELAY_RISK"]
    assert 0.0 <= data["delay_probability_pct"] <= 100.0


def test_ml_predict_eta():
    """Validates POST /api/v1/ml/predict-eta returns transit ETA."""
    payload = {
        "distance_km": 250.0,
        "planned_duration_hours": 24.0,
        "package_weight_kg": 12.0,
        "vehicle_type": "Van",
        "delivery_priority": "Standard",
        "driver_experience_years": 3
    }
    response = client.post("/api/v1/ml/predict-eta", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_eta_hours"] > 0
    assert "confidence_interval_hours" in data


def test_forecasting_demand():
    """Validates /api/v1/forecasting/demand returns 30-day forecast with intervals."""
    response = client.get("/api/v1/forecasting/demand?horizon_days=30")
    assert response.status_code == 200
    data = response.json()
    assert data["horizon_days"] == 30
    assert len(data["forecasts"]) == 180  # 6 hubs * 30 days
    sample = data["forecasts"][0]
    assert sample["is_synthetic_simulated"] is True
    assert sample["forecast_order_volume"] > 0
    assert sample["lower_bound_95"] <= sample["upper_bound_95"]


def test_forecasting_workload():
    """Validates /api/v1/forecasting/workload returns workload utilization."""
    response = client.get("/api/v1/forecasting/workload?horizon_days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["horizon_days"] == 7
    assert len(data["workload_forecasts"]) == 42  # 6 hubs * 7 days


def test_forecasting_fleet():
    """Validates /api/v1/forecasting/fleet returns vehicle requirements."""
    response = client.get("/api/v1/forecasting/fleet?horizon_days=30")
    assert response.status_code == 200
    data = response.json()
    assert len(data["fleet_forecasts"]) == 720  # 30 days * 6 hubs * 4 types
