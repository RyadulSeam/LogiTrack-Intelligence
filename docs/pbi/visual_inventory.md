| Page | Visual Name | Visual Type | Measure / Column References | Data Binding | Rendered | Functional |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Executive Control Tower | `p1_textbox_header_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Executive Control Tower | `p1_slicer_dimdate_year` | `slicer` | `Values:DimDate.year` | Yes | Yes | Yes |
| Executive Control Tower | `p1_slicer_dimhub_hub_name` | `slicer` | `Values:DimHub.hub_name` | Yes | Yes | Yes |
| Executive Control Tower | `p1_slicer_factorders_order_status` | `slicer` | `Values:FactOrders.order_status` | Yes | Yes | Yes |
| Executive Control Tower | `p1_card_total_orders` | `card` | `Values:_Measures.Total Orders` | Yes | Yes | Yes |
| Executive Control Tower | `p1_card_delivered_orders` | `card` | `Values:_Measures.Delivered Orders` | Yes | Yes | Yes |
| Executive Control Tower | `p1_card_on_time_delivery_rate_pct` | `card` | `Values:_Measures.On-Time Delivery Rate %` | Yes | Yes | Yes |
| Executive Control Tower | `p1_card_delay_rate_pct` | `card` | `Values:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Executive Control Tower | `p1_card_avg_delivery_duration_hours` | `card` | `Values:_Measures.Avg Delivery Duration (Hours)` | Yes | Yes | Yes |
| Executive Control Tower | `p1_card_fleet_availability_rate_pct` | `card` | `Values:_Measures.Fleet Availability Rate %` | Yes | Yes | Yes |
| Executive Control Tower | `p1_columnChart_monthly_volume_trajectory` | `columnChart` | `Category:DimDate.month_name, Y:_Measures.Total Orders, Y:_Measures.Delivered Orders` | Yes | Yes | Yes |
| Executive Control Tower | `p1_pieChart_fulfillment_ratio_donut` | `pieChart` | `Category:FactOrders.order_status, Y:_Measures.Total Orders` | Yes | Yes | Yes |
| Executive Control Tower | `p1_barChart_volume_by_hub` | `barChart` | `Category:DimHub.hub_name, Y:_Measures.Total Orders` | Yes | Yes | Yes |
| Executive Control Tower | `p1_table_hub_operational_summary` | `tableEx` | `Values:DimHub.hub_name, Values:DimHub.city, Values:_Measures.Total Orders, Values:_Measures.Delivered Orders, Values:_Measures.On-Time Delivery Rate %, Values:_Measures.Delay Rate %, Values:_Measures.Avg Delivery Duration (Hours)` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_textbox_header_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Regional Hub Operations | `p2_slicer_dimhub_hub_name` | `slicer` | `Values:DimHub.hub_name` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_slicer_dimdate_year` | `slicer` | `Values:DimDate.year` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_card_total_hubs` | `card` | `Values:_Measures.Total Hubs` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_card_network_daily_capacity` | `card` | `Values:_Measures.Network Daily Capacity` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_card_avg_hub_processing_time_hours` | `card` | `Values:_Measures.Avg Hub Processing Time (Hours)` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_card_total_orders_received_hub` | `card` | `Values:_Measures.Total Orders Received (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_card_total_orders_dispatched_hub` | `card` | `Values:_Measures.Total Orders Dispatched (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_card_total_backlog_volume` | `card` | `Values:_Measures.Total Backlog Volume` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_barChart_hub_throughput_ranking` | `barChart` | `Category:DimHub.hub_name, Y:_Measures.Total Orders Received (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_columnChart_hub_capacity_vs_volume` | `columnChart` | `Category:DimHub.hub_name, Y:_Measures.Network Daily Capacity, Y:_Measures.Total Orders` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_lineChart_hourly_network_flow` | `lineChart` | `Category:FactHubHourly.hour_of_day, Y:_Measures.Total Orders Received (Hub), Y:_Measures.Total Orders Dispatched (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `p2_table_hub_bottleneck_and_performance` | `tableEx` | `Values:DimHub.hub_name, Values:DimHub.city, Values:_Measures.Network Daily Capacity, Values:_Measures.Total Orders Received (Hub), Values:_Measures.Total Orders Dispatched (Hub), Values:_Measures.Total Backlog Volume, Values:_Measures.Avg Hub Processing Time (Hours)` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_textbox_header_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_slicer_factorders_delay_reason` | `slicer` | `Values:FactOrders.delay_reason` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_slicer_dimhub_hub_name` | `slicer` | `Values:DimHub.hub_name` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_card_total_orders` | `card` | `Values:_Measures.Total Orders` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_card_on_time_deliveries` | `card` | `Values:_Measures.On-Time Deliveries` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_card_delayed_deliveries` | `card` | `Values:_Measures.Delayed Deliveries` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_card_on_time_delivery_rate_pct` | `card` | `Values:_Measures.On-Time Delivery Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_card_delay_rate_pct` | `card` | `Values:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_card_avg_delayed_duration_hours` | `card` | `Values:_Measures.Avg Delayed Duration (Hours)` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_barChart_delay_reason_distribution` | `barChart` | `Category:FactOrders.delay_reason, Y:_Measures.Delay Incidents by Reason` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_columnChart_delay_rate_by_vehicle_type` | `columnChart` | `Category:DimVehicle.vehicle_type, Y:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_table_driver_performance_scorecard` | `tableEx` | `Values:DimDriver.driver_name, Values:DimDriver.employment_type, Values:DimDriver.experience_years, Values:DimDriver.performance_rating, Values:_Measures.Driver Completed Deliveries, Values:_Measures.On-Time Delivery Rate %, Values:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `p3_table_delay_incident_feed_and_sla` | `tableEx` | `Values:FactOrders.order_id, Values:DimHub.hub_name, Values:FactOrders.delay_reason, Values:_Measures.Avg Delivery Duration (Hours), Values:_Measures.Delivery SLA Variance (Hours)` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_textbox_header_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_slicer_dimvehicle_current_status` | `slicer` | `Values:DimVehicle.current_status` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_slicer_dimvehicle_vehicle_type` | `slicer` | `Values:DimVehicle.vehicle_type` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_card_total_fleet_vehicles` | `card` | `Values:_Measures.Total Fleet Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_card_active_vehicles` | `card` | `Values:_Measures.Active Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_card_vehicles_in_maintenance` | `card` | `Values:_Measures.Vehicles In Maintenance` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_card_maintenance_alert_vehicles` | `card` | `Values:_Measures.Maintenance Alert Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_card_total_maintenance_expense_usd` | `card` | `Values:_Measures.Total Maintenance Expense ($)` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_card_total_downtime_hours` | `card` | `Values:_Measures.Total Downtime Hours` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_pieChart_fleet_availability_breakdown` | `pieChart` | `Category:DimVehicle.current_status, Y:_Measures.Total Fleet Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_barChart_maintenance_expense_by_service` | `barChart` | `Category:FactMaintenance.service_type, Y:_Measures.Total Maintenance Expense ($)` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_columnChart_vehicle_fleet_distribution` | `columnChart` | `Category:DimVehicle.vehicle_code, Y:_Measures.Total Fleet Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `p4_table_high_risk_vehicle_watchlist` | `tableEx` | `Values:DimVehicle.vehicle_code, Values:DimVehicle.vehicle_model, Values:DimVehicle.vehicle_type, Values:DimVehicle.current_status, Values:DimVehicle.lifetime_breakdowns, Values:DimVehicle.is_maintenance_alert` | Yes | Yes | Yes |