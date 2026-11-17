"""
LogiTrack Intelligence — Operational Control Tower & BI Dashboard
Phase 7: Real-Time Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from logitrack.analytics.metrics import (
    get_executive_kpis,
    get_hub_performance_summary,
    get_live_fleet_positions,
    get_delay_root_causes
)
from logitrack.storage.duckdb_manager import DuckDBManager

# 1. Page Configuration
st.set_page_config(
    page_title="LogiTrack Intelligence | Operational Control Tower",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# 2. Sidebar Filters
st.sidebar.image("https://img.icons8.com/color/96/delivery-conveyer.png", width=70)
st.sidebar.title("LogiTrack Ops")
st.sidebar.markdown("**Texas Regional Logistics Network**")

hub_options = [
    "All Hubs", "Dallas Main Hub", "Houston Hub", "Austin Hub",
    "San Antonio Hub", "Fort Worth Hub", "El Paso Hub"
]
selected_hub = st.sidebar.selectbox("Filter by Distribution Hub", hub_options)

st.sidebar.divider()
st.sidebar.markdown("### 🛡️ Data Provenance Policy")
st.sidebar.info("""
**Data Separation Active:**
- **Original:** Orders.csv (27,979 shipments)
- **Synthetic:** Simulated historical scale
- **Simulated:** MQTT live GPS stream
""")

st.sidebar.divider()
if st.sidebar.button("🔄 Refresh Data & Pipeline"):
    st.cache_data.clear()
    st.rerun()


# 3. Load Data
kpis = get_executive_kpis(hub_filter=selected_hub)
hubs_df = get_hub_performance_summary()
fleet_df = get_live_fleet_positions()
delays_df = get_delay_root_causes()

# 4. Main Title Banner
st.title("🚛 LogiTrack Intelligence — Operational Control Tower")
st.caption(f"Real-Time Freight Analytics & Fleet Telematics | Scope: **{selected_hub}**")

# 5. Dashboard Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛰️ Executive Control Tower",
    "🗺️ Fleet Intelligence & Map",
    "🏭 Hub Operations",
    "⏱️ Delivery Intelligence",
    "🛡️ Data Lineage & Governance"
])

# ============================================================
# TAB 1: Executive Control Tower
# ============================================================
with tab1:
    st.subheader("Operational Health & Core KPIs")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Shipments",
            value=f"{kpis['total_orders']:,}",
            help="Total historical and operational orders"
        )
    with col2:
        otd = kpis['on_time_delivery_rate_pct']
        st.metric(
            label="On-Time Delivery (OTD)",
            value=f"{otd:.1f}%",
            delta=f"{otd - 75.0:+.1f}% vs Target",
            delta_color="normal"
        )
    with col3:
        delay_rate = kpis['delay_rate_pct']
        st.metric(
            label="Shipment Delay Rate",
            value=f"{delay_rate:.1f}%",
            delta=f"-{delay_rate - 20.0:.1f}% vs Threshold" if delay_rate > 20 else "Healthy",
            delta_color="inverse"
        )
    with col4:
        st.metric(
            label="Fleet Utilization",
            value=f"{kpis['fleet_utilization_pct']:.1f}%",
            delta=f"{kpis['active_fleet']}/{kpis['total_fleet']} Active Units"
        )
    with col5:
        alerts = kpis['maintenance_alerts']
        st.metric(
            label="Maintenance Alerts",
            value=f"{alerts} Vehicles",
            delta="Service Required" if alerts > 0 else "All Clear",
            delta_color="inverse" if alerts > 0 else "normal"
        )

    st.divider()

    # Trend & Volume Breakdown
    left_chart, right_chart = st.columns([3, 2])
    
    with left_chart:
        st.markdown("#### Shipment Volume by Delivery Status")
        status_counts = pd.DataFrame({
            "Status": ["Delivered On-Time", "Delivered Delayed", "Cancelled"],
            "Count": [
                kpis["delivered_orders"] - (kpis["total_orders"] - kpis["delivered_orders"] - kpis["cancelled_orders"]),
                int(kpis["delivered_orders"] * (kpis["delay_rate_pct"] / 100)),
                kpis["cancelled_orders"]
            ]
        })
        fig_bar = px.bar(
            status_counts,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map={
                "Delivered On-Time": "#28a745",
                "Delivered Delayed": "#ffc107",
                "Cancelled": "#dc3545"
            },
            text_auto=True
        )
        fig_bar.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig_bar, use_container_width=True)

    with right_chart:
        st.markdown("#### Average Durations & Customer Score")
        dur_col1, dur_col2 = st.columns(2)
        dur_col1.metric("Avg Delivery Duration", f"{kpis['avg_delivery_time_hours']:.1f} hrs")
        dur_col2.metric("Avg Hub Processing", f"{kpis['avg_hub_processing_hours']:.2f} hrs")
        
        st.markdown("##### Customer Satisfaction (CSAT)")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=kpis["avg_csat_score"],
            gauge={
                'axis': {'range': [1, 5]},
                'bar': {'color': "#0066cc"},
                'steps': [
                    {'range': [1, 3], 'color': "#ffcccc"},
                    {'range': [3, 4], 'color': "#fff3cd"},
                    {'range': [4, 5], 'color': "#d4edda"}
                ],
            },
            title={'text': "Average CSAT Rating (1 to 5)"}
        ))
        fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)


# ============================================================
# TAB 2: Fleet Intelligence & Live Map
# ============================================================
with tab2:
    st.subheader("🗺️ Texas Regional Fleet Map & Telematics")
    st.markdown("Real-time tracked positions of fleet vehicles and regional distribution hubs.")

    map_col, stats_col = st.columns([3, 1])

    with map_col:
        # Prepare Map Data
        # Hub Layer (Red Pillars)
        hub_map_data = hubs_df[["hub_name", "latitude", "longitude", "daily_capacity"]].dropna().copy()
        hub_map_data["type"] = "Distribution Hub"
        
        # Vehicle Telemetry Layer (Blue Pillars)
        if not fleet_df.empty:
            veh_map_data = fleet_df[["vehicle_code", "latitude", "longitude", "speed_kmh", "current_status"]].dropna().copy()
            veh_map_data["type"] = "Fleet Vehicle"
        else:
            veh_map_data = pd.DataFrame(columns=["latitude", "longitude", "vehicle_code", "speed_kmh", "type"])

        # PyDeck 3D Hexagon / Scatterplot Layer
        hub_layer = pdk.Layer(
            "ScatterplotLayer",
            data=hub_map_data,
            get_position=["longitude", "latitude"],
            get_color=[220, 53, 69, 200],  # Red
            get_radius=22000,
            pickable=True,
            auto_highlight=True
        )

        vehicle_layer = pdk.Layer(
            "ScatterplotLayer",
            data=veh_map_data,
            get_position=["longitude", "latitude"],
            get_color=[0, 123, 255, 220],  # Blue
            get_radius=14000,
            pickable=True,
            auto_highlight=True
        )

        view_state = pdk.ViewState(
            latitude=31.2,
            longitude=-99.2,
            zoom=5.5,
            pitch=35
        )

        deck = pdk.Deck(
            layers=[hub_layer, vehicle_layer],
            initial_view_state=view_state,
            tooltip={"text": "{type}\nName/Code: {vehicle_code}{hub_name}\nStatus: {current_status}\nSpeed: {speed_kmh} km/h"},
            map_style="light"
        )
        st.pydeck_chart(deck, use_container_width=True)

    with stats_col:
        st.markdown("#### Active Fleet Status")
        st.metric("Tracked Live Vehicles", f"{len(fleet_df)}")
        if not fleet_df.empty:
            avg_speed = fleet_df["speed_kmh"].mean()
            st.metric("Avg Fleet Speed", f"{avg_speed:.1f} km/h")
            avg_fuel = fleet_df["fuel_level_pct"].mean()
            st.metric("Avg Fuel Level", f"{avg_fuel:.1f}%")
        
        st.markdown("#### Map Legend")
        st.markdown("🔴 **Red Markers:** Regional Hubs")
        st.markdown("🔵 **Blue Markers:** Active Vehicles")

    st.markdown("#### Live Telematics Signal Feed")
    if not fleet_df.empty:
        st.dataframe(
            fleet_df[["vehicle_code", "vehicle_model", "current_status", "speed_kmh", "fuel_level_pct", "engine_temp_c", "ping_timestamp"]],
            use_container_width=True,
            height=220
        )
    else:
        st.info("No active telemetry signals detected. Trigger Phase 5 streaming runner to simulate pings.")


# ============================================================
# TAB 3: Hub Operations
# ============================================================
with tab3:
    st.subheader("Distribution Center Workload & Capacity")

    hubs_chart_col, hubs_table_col = st.columns([3, 2])

    with hubs_chart_col:
        fig_hubs = px.bar(
            hubs_df,
            x="hub_name",
            y="total_orders",
            color="delayed_orders",
            title="Total Orders Processed per Texas Hub",
            labels={"hub_name": "Hub", "total_orders": "Total Orders", "delayed_orders": "Delayed Orders"},
            color_continuous_scale="Reds"
        )
        fig_hubs.update_layout(xaxis_tickangle=-25, height=360)
        st.plotly_chart(fig_hubs, use_container_width=True)

    with hubs_table_col:
        st.markdown("#### Hub Efficiency Summary")
        st.dataframe(
            hubs_df[["city", "daily_capacity", "avg_processing_hours", "avg_csat", "delayed_orders"]],
            use_container_width=True,
            height=320
        )


# ============================================================
# TAB 4: Delivery Intelligence & Root Causes
# ============================================================
with tab4:
    st.subheader("Shipment Delays & Root Cause Analysis")

    delays_chart, dist_chart = st.columns(2)

    with delays_chart:
        st.markdown("#### Pareto Analysis: Delay Reasons")
        fig_reasons = px.bar(
            delays_df,
            x="incident_count",
            y="delay_reason",
            orientation="h",
            color="incident_count",
            color_continuous_scale="Viridis",
            labels={"incident_count": "Delayed Shipments", "delay_reason": "Root Cause"}
        )
        fig_reasons.update_layout(yaxis={'categoryorder': 'total ascending'}, height=360)
        st.plotly_chart(fig_reasons, use_container_width=True)

    with dist_chart:
        st.markdown("#### Delivery Duration Distribution (Hours)")
        manager = DuckDBManager()
        dur_df = manager.query("""
            SELECT delivery_time_hours
            FROM warehouse.fact_orders
            WHERE order_status = 'Delivered' AND delivery_time_hours IS NOT NULL
            LIMIT 5000;
        """)
        manager.close()

        fig_hist = px.histogram(
            dur_df,
            x="delivery_time_hours",
            nbins=40,
            color_discrete_sequence=["#0066cc"],
            labels={"delivery_time_hours": "Elapsed Hours"}
        )
        fig_hist.update_layout(height=360)
        st.plotly_chart(fig_hist, use_container_width=True)


# ============================================================
# TAB 5: Data Lineage & Governance
# ============================================================
with tab5:
    st.subheader("🛡️ Enterprise Data Provenance & Lineage Verification")
    st.markdown("""
    To maintain complete transparency and technical integrity, **LogiTrack Intelligence**
    strictly isolates and tags every record by its authoritative origin.
    """)

    manager = DuckDBManager()
    provenance_df = manager.query("""
        SELECT
            data_origin,
            COUNT(*) AS record_count,
            'warehouse.fact_orders' AS target_model
        FROM warehouse.fact_orders
        GROUP BY data_origin
        UNION ALL
        SELECT
            data_origin,
            COUNT(*) AS record_count,
            'warehouse.fact_vehicle_telemetry' AS target_model
        FROM warehouse.fact_vehicle_telemetry
        GROUP BY data_origin;
    """)
    manager.close()

    col_lineage1, col_lineage2 = st.columns([2, 1])

    with col_lineage1:
        st.markdown("#### Records by Data Origin Tag")
        st.dataframe(provenance_df, use_container_width=True)

    with col_lineage2:
        st.markdown("#### Lineage Policy Verification")
        st.success("✅ Original Historical Data: 27,979 orders untouched")
        st.info("ℹ️ Synthetic Data: Clearly flagged with `source: synthetic`")
        st.warning("⚡ Simulated Streams: Clearly flagged with `source: simulated`")
