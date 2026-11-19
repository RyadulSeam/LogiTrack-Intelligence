# Visual Diagnostic Audit Table (Phase 1)

Total visuals audited: **53** across **4** pages.

| # | Page | Visual Name | Type | Query | Projections | Model Refs | Safe ID | Status / Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Executive Control Tower | `p1_textbox_header_banner` | `textbox` | Yes | Yes | Valid | Yes | VALID |
| 2 | Executive Control Tower | `p1_slicer_dimdate_year` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 3 | Executive Control Tower | `p1_slicer_dimhub_hub_name` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 4 | Executive Control Tower | `p1_slicer_factorders_order_status` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 5 | Executive Control Tower | `p1_card_total_orders` | `card` | Yes | Yes | Valid | Yes | VALID |
| 6 | Executive Control Tower | `p1_card_delivered_orders` | `card` | Yes | Yes | Valid | Yes | VALID |
| 7 | Executive Control Tower | `p1_card_on_time_delivery_rate_pct` | `card` | Yes | Yes | Valid | Yes | VALID |
| 8 | Executive Control Tower | `p1_card_delay_rate_pct` | `card` | Yes | Yes | Valid | Yes | VALID |
| 9 | Executive Control Tower | `p1_card_avg_delivery_duration_hours` | `card` | Yes | Yes | Valid | Yes | VALID |
| 10 | Executive Control Tower | `p1_card_fleet_availability_rate_pct` | `card` | Yes | Yes | Valid | Yes | VALID |
| 11 | Executive Control Tower | `p1_columnChart_monthly_volume_trajectory` | `columnChart` | Yes | Yes | Valid | Yes | NEEDS_ATTENTION: Uses columnChart (stacked) instead of clusteredColumnChart |
| 12 | Executive Control Tower | `p1_pieChart_fulfillment_ratio_donut` | `pieChart` | Yes | Yes | Valid | Yes | VALID |
| 13 | Executive Control Tower | `p1_barChart_volume_by_hub` | `barChart` | Yes | Yes | Valid | Yes | VALID |
| 14 | Executive Control Tower | `p1_table_hub_operational_summary` | `tableEx` | Yes | Yes | Valid | Yes | VALID |
| 15 | Regional Hub Operations | `p2_textbox_header_banner` | `textbox` | Yes | Yes | Valid | Yes | VALID |
| 16 | Regional Hub Operations | `p2_slicer_dimhub_hub_name` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 17 | Regional Hub Operations | `p2_slicer_dimdate_year` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 18 | Regional Hub Operations | `p2_card_total_hubs` | `card` | Yes | Yes | Valid | Yes | VALID |
| 19 | Regional Hub Operations | `p2_card_network_daily_capacity` | `card` | Yes | Yes | Valid | Yes | VALID |
| 20 | Regional Hub Operations | `p2_card_avg_hub_processing_time_hours` | `card` | Yes | Yes | Valid | Yes | VALID |
| 21 | Regional Hub Operations | `p2_card_total_orders_received_hub` | `card` | Yes | Yes | Valid | Yes | VALID |
| 22 | Regional Hub Operations | `p2_card_total_orders_dispatched_hub` | `card` | Yes | Yes | Valid | Yes | VALID |
| 23 | Regional Hub Operations | `p2_card_total_backlog_volume` | `card` | Yes | Yes | Valid | Yes | VALID |
| 24 | Regional Hub Operations | `p2_barChart_hub_throughput_ranking` | `barChart` | Yes | Yes | Valid | Yes | VALID |
| 25 | Regional Hub Operations | `p2_columnChart_hub_capacity_vs_volume` | `columnChart` | Yes | Yes | Valid | Yes | NEEDS_ATTENTION: Uses columnChart (stacked) instead of clusteredColumnChart |
| 26 | Regional Hub Operations | `p2_lineChart_hourly_network_flow` | `lineChart` | Yes | Yes | Valid | Yes | VALID |
| 27 | Regional Hub Operations | `p2_table_hub_bottleneck_and_performance` | `tableEx` | Yes | Yes | Valid | Yes | VALID |
| 28 | Delay & Root-Cause Analytics | `p3_textbox_header_banner` | `textbox` | Yes | Yes | Valid | Yes | VALID |
| 29 | Delay & Root-Cause Analytics | `p3_slicer_factorders_delay_reason` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 30 | Delay & Root-Cause Analytics | `p3_slicer_dimhub_hub_name` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 31 | Delay & Root-Cause Analytics | `p3_card_total_orders` | `card` | Yes | Yes | Valid | Yes | VALID |
| 32 | Delay & Root-Cause Analytics | `p3_card_on_time_deliveries` | `card` | Yes | Yes | Valid | Yes | VALID |
| 33 | Delay & Root-Cause Analytics | `p3_card_delayed_deliveries` | `card` | Yes | Yes | Valid | Yes | VALID |
| 34 | Delay & Root-Cause Analytics | `p3_card_on_time_delivery_rate_pct` | `card` | Yes | Yes | Valid | Yes | VALID |
| 35 | Delay & Root-Cause Analytics | `p3_card_delay_rate_pct` | `card` | Yes | Yes | Valid | Yes | VALID |
| 36 | Delay & Root-Cause Analytics | `p3_card_avg_delayed_duration_hours` | `card` | Yes | Yes | Valid | Yes | VALID |
| 37 | Delay & Root-Cause Analytics | `p3_barChart_delay_reason_distribution` | `barChart` | Yes | Yes | Valid | Yes | VALID |
| 38 | Delay & Root-Cause Analytics | `p3_columnChart_delay_rate_by_vehicle_type` | `columnChart` | Yes | Yes | Valid | Yes | NEEDS_ATTENTION: Uses columnChart (stacked) instead of clusteredColumnChart |
| 39 | Delay & Root-Cause Analytics | `p3_table_driver_performance_scorecard` | `tableEx` | Yes | Yes | Valid | Yes | VALID |
| 40 | Delay & Root-Cause Analytics | `p3_table_delay_incident_feed_and_sla` | `tableEx` | Yes | Yes | Valid | Yes | VALID |
| 41 | Fleet Telematics & Predictive Maintenance | `p4_textbox_header_banner` | `textbox` | Yes | Yes | Valid | Yes | VALID |
| 42 | Fleet Telematics & Predictive Maintenance | `p4_slicer_dimvehicle_current_status` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 43 | Fleet Telematics & Predictive Maintenance | `p4_slicer_dimvehicle_vehicle_type` | `slicer` | Yes | Yes | Valid | Yes | VALID |
| 44 | Fleet Telematics & Predictive Maintenance | `p4_card_total_fleet_vehicles` | `card` | Yes | Yes | Valid | Yes | VALID |
| 45 | Fleet Telematics & Predictive Maintenance | `p4_card_active_vehicles` | `card` | Yes | Yes | Valid | Yes | VALID |
| 46 | Fleet Telematics & Predictive Maintenance | `p4_card_vehicles_in_maintenance` | `card` | Yes | Yes | Valid | Yes | VALID |
| 47 | Fleet Telematics & Predictive Maintenance | `p4_card_maintenance_alert_vehicles` | `card` | Yes | Yes | Valid | Yes | VALID |
| 48 | Fleet Telematics & Predictive Maintenance | `p4_card_total_maintenance_expense_usd` | `card` | Yes | Yes | Valid | Yes | VALID |
| 49 | Fleet Telematics & Predictive Maintenance | `p4_card_total_downtime_hours` | `card` | Yes | Yes | Valid | Yes | VALID |
| 50 | Fleet Telematics & Predictive Maintenance | `p4_pieChart_fleet_availability_breakdown` | `pieChart` | Yes | Yes | Valid | Yes | VALID |
| 51 | Fleet Telematics & Predictive Maintenance | `p4_barChart_maintenance_expense_by_service` | `barChart` | Yes | Yes | Valid | Yes | VALID |
| 52 | Fleet Telematics & Predictive Maintenance | `p4_columnChart_vehicle_fleet_distribution` | `columnChart` | Yes | Yes | Valid | Yes | NEEDS_ATTENTION: Uses columnChart (stacked) instead of clusteredColumnChart |
| 53 | Fleet Telematics & Predictive Maintenance | `p4_table_high_risk_vehicle_watchlist` | `tableEx` | Yes | Yes | Valid | Yes | VALID |
