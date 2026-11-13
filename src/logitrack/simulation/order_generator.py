"""
Synthetic Orders Generation Engine
LogiTrack Intelligence — Phase 2

Generates realistic orders with Texas geographic routing, SLA thresholds,
package metrics, and state lifecycles with deterministic seed reproducibility.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from faker import Faker

from logitrack.simulation.geo_routes import TEXAS_HUBS, get_road_distance_km

DELAY_REASONS = [
    "Traffic Congestion",
    "Road Construction",
    "Severe Weather",
    "Vehicle Breakdown",
    "Package Sorting Error",
    "Multiple Delivery Stops",
    "Customer Not Home",
    "Incorrect Address",
    "Hub Processing Delay",
    "Driver Unavailable"
]


class OrderGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.faker = Faker()
        Faker.seed(seed)
        self.hubs = list(TEXAS_HUBS.keys())

    def generate_orders(
        self,
        num_orders: int,
        start_date: datetime,
        end_date: datetime,
        driver_ids: List[int],
        vehicle_codes: List[str]
    ) -> List[Dict[str, Any]]:
        orders = []
        total_seconds = int((end_date - start_date).total_seconds())

        for i in range(1, num_orders + 1):
            order_id = 100000 + i
            customer_id = f"CUST-{self.rng.randint(1000, 9999)}"
            
            origin = self.rng.choice(self.hubs)
            destination = self.rng.choice(self.hubs)
            distance_km = get_road_distance_km(origin, destination)
            
            priority = self.rng.choices(
                ["Standard", "Express", "Same-Day"],
                weights=[0.65, 0.25, 0.10],
                k=1
            )[0]
            
            if self.rng.random() < 0.85:
                package_weight_kg = round(self.rng.uniform(0.8, 18.0), 2)
            else:
                package_weight_kg = round(self.rng.uniform(20.0, 250.0), 2)

            order_sec = self.rng.randint(0, total_seconds)
            order_dt = start_date + timedelta(seconds=order_sec)
            
            if priority == "Same-Day":
                lead_hours = self.rng.uniform(4.0, 8.0)
            elif priority == "Express":
                lead_hours = self.rng.uniform(12.0, 24.0)
            else:
                lead_hours = self.rng.uniform(24.0, 72.0)
                
            promised_dt = order_dt + timedelta(hours=lead_hours)

            status_choice = self.rng.choices(
                ["Delivered", "In Transit", "Out for Delivery", "Processing", "Cancelled"],
                weights=[0.88, 0.05, 0.03, 0.02, 0.02],
                k=1
            )[0]

            hub_processing_hours = round(self.rng.uniform(0.5, 3.8), 2)
            
            actual_delivery_dt = None
            delivery_time_hours = None
            is_delayed = False
            is_on_time = False
            delay_reason = None
            csat = None

            if status_choice == "Cancelled":
                csat = 1
                is_delayed = False
                is_on_time = False
            elif status_choice == "Delivered":
                base_transit_hours = (distance_km / 65.0) + hub_processing_hours
                transit_variance = self.rng.uniform(0.85, 1.35)
                actual_duration = round(base_transit_hours * transit_variance, 2)
                
                actual_delivery_dt = order_dt + timedelta(hours=actual_duration)
                delivery_time_hours = actual_duration

                if actual_delivery_dt > promised_dt:
                    is_delayed = True
                    is_on_time = False
                    delay_reason = self.rng.choice(DELAY_REASONS)
                    csat = self.rng.choices([1, 2, 3, 4], weights=[0.25, 0.35, 0.30, 0.10], k=1)[0]
                else:
                    is_delayed = False
                    is_on_time = True
                    delay_reason = None
                    csat = self.rng.choices([3, 4, 5], weights=[0.10, 0.45, 0.45], k=1)[0]

            assigned_driver = self.rng.choice(driver_ids)
            assigned_vehicle = self.rng.choice(vehicle_codes)

            order_record = {
                "order_id": order_id,
                "customer_id": customer_id,
                "origin_hub": origin,
                "destination_hub": destination,
                "route_distance_km": distance_km,
                "package_weight_kg": package_weight_kg,
                "delivery_priority": priority,
                "driver_id": assigned_driver,
                "vehicle_code": assigned_vehicle,
                "order_status": status_choice,
                "is_delayed": is_delayed,
                "is_on_time": is_on_time,
                "delay_reason": delay_reason,
                "hub_processing_time_hours": hub_processing_hours,
                "delivery_time_hours": delivery_time_hours,
                "order_timestamp": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "promised_delivery_timestamp": promised_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_delivery_timestamp": actual_delivery_dt.strftime("%Y-%m-%d %H:%M:%S") if actual_delivery_dt else None,
                "customer_satisfaction_score": csat,
                "data_origin": "source: synthetic",
                "generation_version": "1.0"
            }
            orders.append(order_record)

        return orders
