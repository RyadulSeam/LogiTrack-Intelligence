"""
Pydantic API Request and Response Schemas
LogiTrack Intelligence — Phase 10: API & Application Layer
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Health Check
class HealthCheckResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "HEALTHY"})
    version: str = Field("1.0.0", json_schema_extra={"example": "1.0.0"})
    database: str = Field(..., json_schema_extra={"example": "CONNECTED"})
    environment: str = Field("production-ready", json_schema_extra={"example": "production-ready"})


# Executive KPIs
class ExecutiveKPIsResponse(BaseModel):
    total_orders: int
    delivered_orders: int
    cancelled_orders: int
    on_time_delivery_rate_pct: float
    delay_rate_pct: float
    avg_delivery_time_hours: float
    avg_hub_processing_hours: float
    avg_csat_score: float
    total_fleet: int
    active_fleet: int
    fleet_utilization_pct: float
    maintenance_alerts: int


# Hub Performance
class HubSummaryItem(BaseModel):
    hub_name: str
    city: str
    daily_capacity: int
    latitude: float
    longitude: float
    total_orders: int
    delayed_orders: int
    avg_delivery_hours: float
    avg_processing_hours: float
    avg_csat: float
    workload_ratio: float


class HubsResponse(BaseModel):
    total_hubs: int
    hubs: List[HubSummaryItem]


# Fleet Telematics
class FleetVehicleItem(BaseModel):
    vehicle_code: str
    vehicle_model: str
    vehicle_type: str
    current_status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    fuel_level_pct: Optional[float] = None
    engine_temp_c: Optional[float] = None
    engine_status: Optional[str] = None


class FleetResponse(BaseModel):
    total_fleet: int
    active_fleet: int
    vehicles: List[FleetVehicleItem]


# ML Inference
class DelayPredictionRequest(BaseModel):
    distance_km: float = Field(..., ge=1.0, le=2000.0, json_schema_extra={"example": 245.5})
    planned_duration_hours: float = Field(..., ge=0.5, le=120.0, json_schema_extra={"example": 36.0})
    package_weight_kg: float = Field(15.0, ge=0.1, le=500.0, json_schema_extra={"example": 18.5})
    delivery_priority: str = Field("Standard", json_schema_extra={"example": "High"})
    vehicle_type: str = Field("Van", json_schema_extra={"example": "Van"})
    driver_experience_years: int = Field(4, ge=0, le=40, json_schema_extra={"example": 5})
    driver_rating: float = Field(4.0, ge=1.0, le=5.0, json_schema_extra={"example": 4.5})
    is_weekend: bool = Field(False, json_schema_extra={"example": False})
    hub_id: str = Field("HUB-DAL-01", json_schema_extra={"example": "HUB-DAL-01"})


class DelayPredictionResponse(BaseModel):
    predicted_label: str = Field(..., json_schema_extra={"example": "DELAY_RISK"})
    delay_probability_pct: float = Field(..., json_schema_extra={"example": 78.5})
    risk_level: str = Field(..., json_schema_extra={"example": "HIGH"})
    explanation: str
    model_version: str = "1.0.0"


class ETAPredictionRequest(BaseModel):
    distance_km: float = Field(..., ge=1.0, le=2000.0, json_schema_extra={"example": 180.0})
    planned_duration_hours: float = Field(..., ge=0.5, le=120.0, json_schema_extra={"example": 24.0})
    package_weight_kg: float = Field(12.0, json_schema_extra={"example": 15.0})
    vehicle_type: str = Field("Van", json_schema_extra={"example": "Van"})
    delivery_priority: str = Field("Standard", json_schema_extra={"example": "Standard"})
    driver_experience_years: int = Field(3, json_schema_extra={"example": 3})


class ETAPredictionResponse(BaseModel):
    predicted_eta_hours: float
    confidence_interval_hours: Dict[str, float]
    model_version: str = "1.0.0"


# Forecasting
class DemandForecastItem(BaseModel):
    forecast_date: str
    horizon_step: int
    hub_id: str
    hub_name: str
    daily_capacity: int
    forecast_order_volume: float
    lower_bound_95: float
    upper_bound_95: float
    is_synthetic_simulated: bool = True


class DemandForecastResponse(BaseModel):
    horizon_days: int
    forecasts: List[DemandForecastItem]


class HubWorkloadForecastItem(BaseModel):
    forecast_date: str
    horizon_step: int
    hub_id: str
    hub_name: str
    forecast_order_volume: float
    forecast_dispatched_volume: float
    projected_daily_backlog: float
    capacity_utilization_pct: float
    is_bottleneck_risk: bool
    risk_level: str


class HubWorkloadForecastResponse(BaseModel):
    horizon_days: int
    workload_forecasts: List[HubWorkloadForecastItem]


class FleetRequirementForecastItem(BaseModel):
    forecast_date: str
    hub_name: str
    vehicle_type: str
    projected_parcels: float
    vehicles_required: int
    active_fleet_baseline: int
    surplus_or_deficit: int
    is_fleet_deficit: bool
    utilization_rate_pct: float


class FleetRequirementForecastResponse(BaseModel):
    horizon_days: int
    fleet_forecasts: List[FleetRequirementForecastItem]
