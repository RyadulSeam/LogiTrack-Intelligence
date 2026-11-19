| Page | Visual Name | Visual Type | Measure / Column References | Data Binding | Rendered | Functional |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Executive Control Tower | `header_title_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Executive Control Tower | `slicer_DimDate_year` | `slicer` | `Values:DimDate.year` | Yes | Yes | Yes |
| Executive Control Tower | `slicer_DimHub_hub_name` | `slicer` | `Values:DimHub.hub_name` | Yes | Yes | Yes |
| Executive Control Tower | `slicer_FactOrders_order_status` | `slicer` | `Values:FactOrders.order_status` | Yes | Yes | Yes |
| Executive Control Tower | `card_Total_Orders` | `card` | `Values:_Measures.Total Orders` | Yes | Yes | Yes |
| Executive Control Tower | `card_Delivered_Orders` | `card` | `Values:_Measures.Delivered Orders` | Yes | Yes | Yes |
| Executive Control Tower | `card_On-Time_Delivery_Rate_Pct` | `card` | `Values:_Measures.On-Time Delivery Rate %` | Yes | Yes | Yes |
| Executive Control Tower | `card_Delay_Rate_Pct` | `card` | `Values:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Executive Control Tower | `card_Avg_Delivery_Duration_Hours` | `card` | `Values:_Measures.Avg Delivery Duration (Hours)` | Yes | Yes | Yes |
| Executive Control Tower | `card_Fleet_Availability_Rate_Pct` | `card` | `Values:_Measures.Fleet Availability Rate %` | Yes | Yes | Yes |
| Executive Control Tower | `chart_DimDate_month_name_columnChart` | `columnChart` | `Category:DimDate.month_name, Y:_Measures.Total Orders, Y:_Measures.Delivered Orders` | Yes | Yes | Yes |
| Executive Control Tower | `chart_FactOrders_order_status_pieChart` | `pieChart` | `Category:FactOrders.order_status, Y:_Measures.Total Orders` | Yes | Yes | Yes |
| Executive Control Tower | `chart_DimHub_hub_name_barChart` | `barChart` | `Category:DimHub.hub_name, Y:_Measures.Total Orders` | Yes | Yes | Yes |
| Executive Control Tower | `table_Regional_Hub_Operational_` | `tableEx` | `Values:DimHub.hub_name, Values:DimHub.city, Values:_Measures.Total Orders, Values:_Measures.Delivered Orders, Values:_Measures.On-Time Delivery Rate %, Values:_Measures.Delay Rate %, Values:_Measures.Avg Delivery Duration (Hours)` | Yes | Yes | Yes |
| Regional Hub Operations | `header_title_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Regional Hub Operations | `slicer_DimHub_hub_name` | `slicer` | `Values:DimHub.hub_name` | Yes | Yes | Yes |
| Regional Hub Operations | `slicer_DimDate_year` | `slicer` | `Values:DimDate.year` | Yes | Yes | Yes |
| Regional Hub Operations | `card_Total_Hubs` | `card` | `Values:_Measures.Total Hubs` | Yes | Yes | Yes |
| Regional Hub Operations | `card_Network_Daily_Capacity` | `card` | `Values:_Measures.Network Daily Capacity` | Yes | Yes | Yes |
| Regional Hub Operations | `card_Avg_Hub_Processing_Time_Hours` | `card` | `Values:_Measures.Avg Hub Processing Time (Hours)` | Yes | Yes | Yes |
| Regional Hub Operations | `card_Total_Orders_Received_Hub` | `card` | `Values:_Measures.Total Orders Received (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `card_Total_Orders_Dispatched_Hub` | `card` | `Values:_Measures.Total Orders Dispatched (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `card_Total_Backlog_Volume` | `card` | `Values:_Measures.Total Backlog Volume` | Yes | Yes | Yes |
| Regional Hub Operations | `chart_DimHub_hub_name_barChart` | `barChart` | `Category:DimHub.hub_name, Y:_Measures.Total Orders Received (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `chart_DimHub_hub_name_columnChart` | `columnChart` | `Category:DimHub.hub_name, Y:_Measures.Network Daily Capacity, Y:_Measures.Total Orders` | Yes | Yes | Yes |
| Regional Hub Operations | `chart_FactHubHourly_hour_of_day_lineChart` | `lineChart` | `Category:FactHubHourly.hour_of_day, Y:_Measures.Total Orders Received (Hub), Y:_Measures.Total Orders Dispatched (Hub)` | Yes | Yes | Yes |
| Regional Hub Operations | `table_Regional_Hub_Bottleneck_&` | `tableEx` | `Values:DimHub.hub_name, Values:DimHub.city, Values:_Measures.Network Daily Capacity, Values:_Measures.Total Orders Received (Hub), Values:_Measures.Total Orders Dispatched (Hub), Values:_Measures.Total Backlog Volume, Values:_Measures.Avg Hub Processing Time (Hours)` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `header_title_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Delay & Root-Cause Analytics | `slicer_FactOrders_delay_reason` | `slicer` | `Values:FactOrders.delay_reason` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `slicer_DimHub_hub_name` | `slicer` | `Values:DimHub.hub_name` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `card_Total_Orders` | `card` | `Values:_Measures.Total Orders` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `card_On-Time_Deliveries` | `card` | `Values:_Measures.On-Time Deliveries` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `card_Delayed_Deliveries` | `card` | `Values:_Measures.Delayed Deliveries` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `card_On-Time_Delivery_Rate_Pct` | `card` | `Values:_Measures.On-Time Delivery Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `card_Delay_Rate_Pct` | `card` | `Values:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `card_Avg_Delayed_Duration_Hours` | `card` | `Values:_Measures.Avg Delayed Duration (Hours)` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `chart_FactOrders_delay_reason_barChart` | `barChart` | `Category:FactOrders.delay_reason, Y:_Measures.Delay Incidents by Reason` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `chart_DimVehicle_vehicle_type_columnChart` | `columnChart` | `Category:DimVehicle.vehicle_type, Y:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `table_Driver_Performance_Scorec` | `tableEx` | `Values:DimDriver.driver_name, Values:DimDriver.employment_type, Values:DimDriver.experience_years, Values:DimDriver.performance_rating, Values:_Measures.Driver Completed Deliveries, Values:_Measures.On-Time Delivery Rate %, Values:_Measures.Delay Rate %` | Yes | Yes | Yes |
| Delay & Root-Cause Analytics | `table_Delay_Incident_Feed_&_SLA` | `tableEx` | `Values:FactOrders.order_id, Values:DimHub.hub_name, Values:FactOrders.delay_reason, Values:_Measures.Avg Delivery Duration (Hours), Values:_Measures.Delivery SLA Variance (Hours)` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `header_title_banner` | `textbox` | `Static UI (Header)` | N/A | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `slicer_DimVehicle_current_status` | `slicer` | `Values:DimVehicle.current_status` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `slicer_DimVehicle_vehicle_type` | `slicer` | `Values:DimVehicle.vehicle_type` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `card_Total_Fleet_Vehicles` | `card` | `Values:_Measures.Total Fleet Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `card_Active_Vehicles` | `card` | `Values:_Measures.Active Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `card_Vehicles_In_Maintenance` | `card` | `Values:_Measures.Vehicles In Maintenance` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `card_Maintenance_Alert_Vehicles` | `card` | `Values:_Measures.Maintenance Alert Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `card_Total_Maintenance_Expense_USD` | `card` | `Values:_Measures.Total Maintenance Expense ($)` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `card_Total_Downtime_Hours` | `card` | `Values:_Measures.Total Downtime Hours` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `chart_DimVehicle_current_status_pieChart` | `pieChart` | `Category:DimVehicle.current_status, Y:_Measures.Total Fleet Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `chart_FactMaintenance_service_type_barChart` | `barChart` | `Category:FactMaintenance.service_type, Y:_Measures.Total Maintenance Expense ($)` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `chart_DimVehicle_vehicle_code_columnChart` | `columnChart` | `Category:DimVehicle.vehicle_code, Y:_Measures.Total Fleet Vehicles` | Yes | Yes | Yes |
| Fleet Telematics & Predictive Maintenance | `table_High-Risk_Vehicle_Fleet_M` | `tableEx` | `Values:DimVehicle.vehicle_code, Values:DimVehicle.vehicle_model, Values:DimVehicle.vehicle_type, Values:DimVehicle.current_status, Values:DimVehicle.lifetime_breakdowns, Values:DimVehicle.is_maintenance_alert` | Yes | Yes | Yes |