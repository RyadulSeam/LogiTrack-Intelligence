"""
Order Lifecycle Event Generator Engine
LogiTrack Intelligence — Phase 2

Generates realistic granular state transition events for each order,
ensuring strict chronological monotonicity across state transitions.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any


LIFECYCLE_SEQUENCE = [
    "ORDER_CREATED",
    "HUB_RECEIVED",
    "PROCESSING_STARTED",
    "PROCESSING_COMPLETED",
    "DISPATCHED",
    "IN_TRANSIT",
    "OUT_FOR_DELIVERY",
    "DELIVERED"
]


class EventGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed

    def generate_order_events(self, order: Dict[str, Any]) -> List[Dict[str, Any]]:
        events = []
        order_id = order["order_id"]
        order_status = order["order_status"]
        order_dt = datetime.strptime(order["order_timestamp"], "%Y-%m-%d %H:%M:%S")

        current_dt = order_dt

        # Determine target sequence
        if order_status == "Processing":
            target_states = ["ORDER_CREATED", "HUB_RECEIVED", "PROCESSING_STARTED"]
        elif order_status == "In Transit":
            target_states = ["ORDER_CREATED", "HUB_RECEIVED", "PROCESSING_STARTED", "PROCESSING_COMPLETED", "DISPATCHED", "IN_TRANSIT"]
        elif order_status == "Out for Delivery":
            target_states = ["ORDER_CREATED", "HUB_RECEIVED", "PROCESSING_STARTED", "PROCESSING_COMPLETED", "DISPATCHED", "IN_TRANSIT", "OUT_FOR_DELIVERY"]
        elif order_status == "Cancelled":
            target_states = ["ORDER_CREATED", "HUB_RECEIVED", "CANCELLED"]
        else: # Delivered
            target_states = LIFECYCLE_SEQUENCE

        # If delivered and delivery timestamp is known, compute milestones relative to start and end
        actual_deliv_dt = None
        if order.get("actual_delivery_timestamp"):
            actual_deliv_dt = datetime.strptime(order["actual_delivery_timestamp"], "%Y-%m-%d %H:%M:%S")
            # Sanity check: must be after order_dt
            if actual_deliv_dt <= order_dt:
                actual_deliv_dt = order_dt + timedelta(hours=3)

        for i, state in enumerate(target_states):
            if state == "ORDER_CREATED":
                step_dt = order_dt
            elif state == "DELIVERED" and actual_deliv_dt:
                step_dt = actual_deliv_dt if actual_deliv_dt >= current_dt else current_dt + timedelta(minutes=10)
            elif state == "CANCELLED":
                step_dt = current_dt + timedelta(minutes=45)
            else:
                # Progressive increment
                increment_mins = {
                    "HUB_RECEIVED": 15,
                    "PROCESSING_STARTED": 20,
                    "PROCESSING_COMPLETED": int(max(0.5, order.get("hub_processing_time_hours", 1.0)) * 60),
                    "DISPATCHED": 15,
                    "IN_TRANSIT": 30,
                    "OUT_FOR_DELIVERY": 45,
                    "DELIVERED": 30
                }.get(state, 15)
                step_dt = current_dt + timedelta(minutes=increment_mins)

            # Strict monotonicity enforcement
            if step_dt < current_dt:
                step_dt = current_dt + timedelta(minutes=5)
            current_dt = step_dt

            event = {
                "event_id": f"evt-{uuid.uuid4().hex[:12]}",
                "order_id": order_id,
                "event_type": state,
                "event_timestamp": step_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "hub_name": order["origin_hub"],
                "driver_id": order["driver_id"],
                "vehicle_code": order["vehicle_code"],
                "data_origin": "source: synthetic",
                "generation_version": "1.0"
            }
            events.append(event)

        return events
