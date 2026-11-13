"""
Fleet Maintenance & Health Simulation Engine
LogiTrack Intelligence — Phase 2

Generates realistic vehicle maintenance logs, preventive service records,
and unexpected breakdown histories.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

SERVICE_TYPES = [
    "Routine Oil & Filter",
    "Brake System Inspection",
    "Transmission Service",
    "Tire Rotation & Replacement",
    "Engine Diagnostics",
    "Coolant Flush & Thermostat",
    "Electrical & Alternator Check",
    "Suspension & Steering"
]


class MaintenanceGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def generate_maintenance_logs(
        self,
        vehicle_codes: List[str],
        num_records: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        logs = []
        total_seconds = int((end_date - start_date).total_seconds())

        for _ in range(num_records):
            v_code = random.choice(vehicle_codes)
            service = random.choice(SERVICE_TYPES)
            
            event_sec = random.randint(0, total_seconds)
            sched_dt = start_date + timedelta(seconds=event_sec)
            
            status = random.choices(
                ["Completed", "In Progress", "Scheduled"],
                weights=[0.85, 0.08, 0.07],
                k=1
            )[0]

            if status == "Completed":
                downtime_hours = round(random.uniform(2.5, 36.0), 1)
                completed_dt = sched_dt + timedelta(hours=downtime_hours)
                cost_usd = round(random.uniform(150.0, 1850.0), 2)
            else:
                downtime_hours = None
                completed_dt = None
                cost_usd = round(random.uniform(120.0, 900.0), 2)

            log_entry = {
                "maintenance_id": f"maint-{uuid.uuid4().hex[:10]}",
                "vehicle_code": v_code,
                "service_type": service,
                "status": status,
                "scheduled_date": sched_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "completed_date": completed_dt.strftime("%Y-%m-%d %H:%M:%S") if completed_dt else None,
                "downtime_hours": downtime_hours,
                "cost_usd": cost_usd,
                "data_origin": "source: synthetic",
                "generation_version": "1.0"
            }
            logs.append(log_entry)

        return logs
