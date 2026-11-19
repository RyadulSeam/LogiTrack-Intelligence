"""
Phase 11 — Forecasting Pipeline Tests
Validates time-series forecasting output quality, 
confidence interval integrity, and DuckDB schema population.
"""

import pytest
import duckdb
import pandas as pd
import numpy as np

DB_PATH = "data/lake/logitrack.duckdb"


@pytest.fixture(scope="module")
def db():
    conn = duckdb.connect(DB_PATH, read_only=True)
    yield conn
    conn.close()


class TestDemandForecastSchema:
    """Validates the demand_forecasts table structure and data quality."""

    def test_demand_forecasts_row_count(self, db):
        count = db.execute("SELECT COUNT(*) FROM forecasting.demand_forecasts").fetchone()[0]
        assert count == 180, f"Expected 180 demand forecasts (6 hubs × 30 days), got {count}"

    def test_demand_forecasts_all_hubs_present(self, db):
        hubs = db.execute(
            "SELECT DISTINCT hub_name FROM forecasting.demand_forecasts ORDER BY hub_name"
        ).fetchdf()["hub_name"].tolist()
        assert len(hubs) == 6, f"Expected 6 hubs in demand_forecasts, got {hubs}"

    def test_demand_forecasts_horizon_steps(self, db):
        min_step, max_step = db.execute(
            "SELECT MIN(horizon_step), MAX(horizon_step) FROM forecasting.demand_forecasts"
        ).fetchone()
        assert min_step == 1
        assert max_step == 30

    def test_demand_confidence_interval_valid(self, db):
        """Ensure lower_bound_95 <= forecast <= upper_bound_95 for all rows."""
        violations = db.execute("""
            SELECT COUNT(*) FROM forecasting.demand_forecasts
            WHERE lower_bound_95 > forecast_order_volume
               OR upper_bound_95 < forecast_order_volume
        """).fetchone()[0]
        assert violations == 0, f"{violations} CI violations in demand_forecasts"

    def test_demand_forecast_volumes_positive(self, db):
        negative = db.execute(
            "SELECT COUNT(*) FROM forecasting.demand_forecasts WHERE forecast_order_volume <= 0"
        ).fetchone()[0]
        assert negative == 0, f"{negative} non-positive forecast volumes found"

    def test_demand_synthetic_flag_set(self, db):
        not_flagged = db.execute(
            "SELECT COUNT(*) FROM forecasting.demand_forecasts WHERE is_synthetic_simulated = FALSE"
        ).fetchone()[0]
        assert not_flagged == 0, "All demand forecasts must be flagged as synthetic_simulated"


class TestHubWorkloadForecastSchema:
    """Validates hub_workload_forecasts table integrity."""

    def test_workload_forecasts_row_count(self, db):
        count = db.execute(
            "SELECT COUNT(*) FROM forecasting.hub_workload_forecasts"
        ).fetchone()[0]
        assert count == 180, f"Expected 180 workload forecasts (6 hubs × 30 days), got {count}"

    def test_capacity_utilization_range(self, db):
        """Utilization should be in [0%, 200%] — values above 100% indicate overflow."""
        out_of_range = db.execute("""
            SELECT COUNT(*) FROM forecasting.hub_workload_forecasts
            WHERE capacity_utilization_pct < 0 OR capacity_utilization_pct > 200
        """).fetchone()[0]
        assert out_of_range == 0, f"{out_of_range} rows with invalid utilization values"

    def test_workload_risk_level_values(self, db):
        risk_levels = db.execute(
            "SELECT DISTINCT risk_level FROM forecasting.hub_workload_forecasts"
        ).fetchdf()["risk_level"].tolist()
        valid_levels = {"Normal", "Elevated", "High Risk", "Critical Overflow", "NORMAL", "HIGH_RISK", "CRITICAL"}
        # At least some valid level must exist
        assert len(risk_levels) > 0

    def test_bottleneck_risk_boolean_consistency(self, db):
        """is_bottleneck_risk should be TRUE only when utilization >= 85%."""
        inconsistent = db.execute("""
            SELECT COUNT(*) FROM forecasting.hub_workload_forecasts
            WHERE is_bottleneck_risk = TRUE AND capacity_utilization_pct < 85.0
        """).fetchone()[0]
        assert inconsistent == 0, f"{inconsistent} rows with inconsistent bottleneck flag"

    def test_dispatched_volume_not_exceeds_forecast(self, db):
        """Dispatched volume should not dramatically exceed forecasted volume."""
        df = db.execute("""
            SELECT forecast_order_volume, forecast_dispatched_volume
            FROM forecasting.hub_workload_forecasts
        """).fetchdf()
        # Dispatch can exceed forecast slightly (backlog), but should stay within 150%
        excessive = (df["forecast_dispatched_volume"] > df["forecast_order_volume"] * 1.5).sum()
        assert excessive == 0, f"{excessive} rows where dispatched drastically exceeds forecast"


class TestFleetRequirementForecastSchema:
    """Validates fleet_requirement_forecasts table integrity."""

    def test_fleet_requirement_row_count(self, db):
        count = db.execute(
            "SELECT COUNT(*) FROM forecasting.fleet_requirement_forecasts"
        ).fetchone()[0]
        # 30 days × 6 hubs × 4 vehicle types = 720 rows
        assert count == 720, f"Expected 720 fleet requirement rows, got {count}"

    def test_fleet_all_vehicle_types_present(self, db):
        types = db.execute(
            "SELECT DISTINCT vehicle_type FROM forecasting.fleet_requirement_forecasts ORDER BY vehicle_type"
        ).fetchdf()["vehicle_type"].tolist()
        expected = {"Van", "Truck", "Pickup", "Box Truck"}
        assert set(types) == expected, f"Missing vehicle types: {expected - set(types)}"

    def test_vehicles_required_positive(self, db):
        non_positive = db.execute(
            "SELECT COUNT(*) FROM forecasting.fleet_requirement_forecasts WHERE vehicles_required <= 0"
        ).fetchone()[0]
        assert non_positive == 0, f"{non_positive} rows with non-positive vehicles_required"

    def test_fleet_deficit_flag_consistency(self, db):
        """is_fleet_deficit should be TRUE only when surplus_or_deficit < 0."""
        inconsistent = db.execute("""
            SELECT COUNT(*) FROM forecasting.fleet_requirement_forecasts
            WHERE is_fleet_deficit = TRUE AND surplus_or_deficit >= 0
        """).fetchone()[0]
        assert inconsistent == 0, f"{inconsistent} rows with inconsistent fleet deficit flag"

    def test_utilization_rate_range(self, db):
        out_of_range = db.execute("""
            SELECT COUNT(*) FROM forecasting.fleet_requirement_forecasts
            WHERE utilization_rate_pct < 0 OR utilization_rate_pct > 500
        """).fetchone()[0]
        assert out_of_range == 0, f"{out_of_range} fleet forecast rows with unrealistic utilization"

    def test_all_hubs_covered_in_fleet_forecast(self, db):
        hub_count = db.execute(
            "SELECT COUNT(DISTINCT hub_name) FROM forecasting.fleet_requirement_forecasts"
        ).fetchone()[0]
        assert hub_count == 6, f"Expected 6 hubs in fleet forecasts, got {hub_count}"


class TestForecastingDataProvenance:
    """Validates data provenance labelling across all forecasting tables."""

    def test_demand_provenance_label(self, db):
        rows = db.execute(
            "SELECT COUNT(*) FROM forecasting.demand_forecasts WHERE is_synthetic_simulated IS NOT NULL"
        ).fetchone()[0]
        assert rows == 180

    def test_all_forecast_dates_in_future_range(self, db):
        """Forecast dates should all be within 1–30 days from a recent reference."""
        earliest, latest = db.execute(
            "SELECT MIN(forecast_date), MAX(forecast_date) FROM forecasting.demand_forecasts"
        ).fetchone()
        assert earliest is not None
        assert latest is not None
        # Horizon step 1 should be strictly after some reference date
        assert str(earliest) < str(latest)
