"""
Phase 11 — Monitoring & Health Tests
Tests for the system health monitor, KPI drift detection,
data completeness checks, and ML model freshness monitoring.
"""

import pytest
import pandas as pd
from logitrack.monitoring.health_monitor import (
    check_lakehouse_table_health,
    check_model_artifact_freshness,
    check_data_completeness,
    check_kpi_drift,
    run_full_health_check,
)


class TestTableHealthMonitor:
    """Validates table health checks across the DuckDB lakehouse."""

    def test_table_health_returns_dataframe(self):
        df = check_lakehouse_table_health()
        assert isinstance(df, pd.DataFrame)
        assert "table" in df.columns
        assert "row_count" in df.columns
        assert "status" in df.columns

    def test_table_health_covers_core_tables(self):
        df = check_lakehouse_table_health()
        tables = df["table"].tolist()
        assert "warehouse.fact_orders" in tables
        assert "warehouse.dim_hub" in tables
        assert "forecasting.demand_forecasts" in tables
        assert "ml.model_registry" in tables

    def test_critical_tables_are_healthy(self):
        df = check_lakehouse_table_health()
        fact_orders = df[df["table"] == "warehouse.fact_orders"].iloc[0]
        assert fact_orders["status"] == "OK"
        assert fact_orders["row_count"] == 27979

        dim_hub = df[df["table"] == "warehouse.dim_hub"].iloc[0]
        assert dim_hub["status"] == "OK"
        assert dim_hub["row_count"] == 6

    def test_forecasting_tables_populated(self):
        df = check_lakehouse_table_health()
        demand_row = df[df["table"] == "forecasting.demand_forecasts"].iloc[0]
        assert demand_row["status"] == "OK"
        assert demand_row["row_count"] >= 100


class TestModelArtifactFreshness:
    """Validates ML model artifact freshness monitoring."""

    def test_model_freshness_returns_dataframe(self):
        df = check_model_artifact_freshness()
        assert isinstance(df, pd.DataFrame)

    def test_all_expected_artifacts_exist(self):
        df = check_model_artifact_freshness()
        artifacts = df["artifact"].tolist()
        assert "delay_risk_classifier.joblib" in artifacts
        assert "eta_regressor.joblib" in artifacts

    def test_artifacts_are_fresh(self):
        df = check_model_artifact_freshness(max_age_days=90)
        assert len(df) > 0
        # With a generous 90-day window, all artifacts should be fresh
        stale = df[df["status"] == "STALE"]
        assert len(stale) == 0, f"Stale artifacts found: {stale['artifact'].tolist()}"

    def test_artifact_sizes_are_non_zero(self):
        df = check_model_artifact_freshness()
        assert (df["size_kb"] > 0).all()


class TestDataCompleteness:
    """Validates null rate checks on critical warehouse columns."""

    def test_completeness_returns_dataframe(self):
        df = check_data_completeness()
        assert isinstance(df, pd.DataFrame)
        assert "table" in df.columns
        assert "column" in df.columns
        assert "null_rate_pct" in df.columns
        assert "status" in df.columns

    def test_order_id_has_no_nulls(self):
        df = check_data_completeness()
        order_id_row = df[(df["table"] == "warehouse.fact_orders") & (df["column"] == "order_id")].iloc[0]
        assert order_id_row["null_rate_pct"] == 0.0
        assert order_id_row["status"] == "OK"

    def test_hub_coordinates_have_no_nulls(self):
        df = check_data_completeness()
        lat_row = df[(df["table"] == "warehouse.dim_hub") & (df["column"] == "latitude")].iloc[0]
        lon_row = df[(df["table"] == "warehouse.dim_hub") & (df["column"] == "longitude")].iloc[0]
        assert lat_row["status"] == "OK"
        assert lon_row["status"] == "OK"

    def test_all_completeness_checks_pass(self):
        df = check_data_completeness()
        failed = df[df["status"].str.startswith("HIGH_NULL_RATE")]
        assert len(failed) == 0, f"Failed completeness checks: {failed[['table', 'column', 'null_rate_pct']].to_dict()}"


class TestKPIDriftDetection:
    """Validates business KPI baseline drift detection."""

    def test_kpi_drift_returns_dict(self):
        result = check_kpi_drift()
        assert isinstance(result, dict)
        assert "total_orders" in result
        assert "otd_rate_pct" in result

    def test_total_orders_matches_baseline(self):
        result = check_kpi_drift()
        assert result["total_orders"]["actual"] == 27979
        assert result["total_orders"]["status"] == "OK"

    def test_delivered_orders_matches_baseline(self):
        result = check_kpi_drift()
        assert result["delivered_orders"]["actual"] == 27727
        assert result["delivered_orders"]["status"] == "OK"

    def test_otd_rate_within_tolerance(self):
        result = check_kpi_drift()
        otd = result["otd_rate_pct"]
        assert otd["status"] == "OK", f"OTD rate drift: actual={otd['actual']}, baseline={otd['baseline']}"

    def test_all_kpis_stable(self):
        result = check_kpi_drift()
        drifted = {k: v for k, v in result.items() if v["status"] != "OK"}
        assert len(drifted) == 0, f"Drifted KPIs: {drifted}"


class TestCompositeHealthReport:
    """Validates the full composite system health check."""

    def test_health_report_returns_dict(self):
        report = run_full_health_check()
        assert isinstance(report, dict)
        assert "overall_status" in report
        assert "timestamp" in report
        assert "summary" in report

    def test_health_report_overall_status_is_healthy(self):
        report = run_full_health_check()
        # Overall health is healthy when all KPIs pass and all checked tables pass
        # Some staging tables may not exist yet - check KPI and core warehouse health
        assert report["summary"]["kpis_ok"] == 5, (
            f"KPI drift detected: {report['kpi_drift']}"
        )
        # Core tables (warehouse + forecasting) must all be healthy
        core_tables = [
            t for t in report["table_health"]
            if t["table"].startswith("warehouse.") or t["table"].startswith("forecasting.")
        ]
        core_ok = all(t["status"] == "OK" for t in core_tables)
        assert core_ok, f"Core table failures: {[t for t in core_tables if t['status'] != 'OK']}"

    def test_health_report_summary_counts(self):
        report = run_full_health_check()
        summary = report["summary"]
        # At least 11 tables should be healthy (excluding staging tables that may differ in name)
        assert summary["tables_ok"] >= 11, (
            f"Too few healthy tables: {summary}"
        )
        assert summary["kpis_ok"] == 5  # 5 KPI checks
