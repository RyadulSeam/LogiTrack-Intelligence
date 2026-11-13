"""
Live Streaming Simulation Runner
LogiTrack Intelligence — Phase 5

Runs a simulated live operational session, streaming vehicle telemetry, order transitions,
and hub events through the validation and idempotent consumer pipeline.
"""

import json
from loguru import logger
from logitrack.streaming.mqtt_producer import EventProducer
from logitrack.streaming.mqtt_consumer import EventConsumer
from logitrack.storage.duckdb_manager import DuckDBManager


def run_streaming_simulation(num_telemetry: int = 60, num_orders: int = 25):
    logger.info("=== Starting LogiTrack Real-Time Streaming Session ===")
    
    producer = EventProducer()
    consumer = EventConsumer()

    # 1. Stream Vehicle Telemetry
    logger.info(f"Streaming {num_telemetry} live vehicle GPS telemetry pings...")
    for i in range(num_telemetry):
        vehicle_code = f"FT-{((i % 41) + 1):03d}"
        event = producer.generate_telemetry_event(vehicle_code=vehicle_code)
        consumer.process_message("logitrack/vehicle/telemetry", json.dumps(event))

    # 2. Stream Order Lifecycle Transitions
    logger.info(f"Streaming {num_orders} live order lifecycle events...")
    for i in range(num_orders):
        order_event = producer.generate_order_event(order_id=100000 + i)
        consumer.process_message("logitrack/order/status", json.dumps(order_event))

    # 3. Test Ingestion Failure & Dead-Letter Routing (Corrupt payload)
    logger.info("Simulating corrupted event payload to test Dead-Letter Queue (DLQ)...")
    corrupt_payload = "{ 'malformed': True, missing_quotes }"
    consumer.process_message("logitrack/vehicle/telemetry", corrupt_payload)

    # 4. Flush any remaining telemetry buffer to Parquet
    consumer._flush_telemetry_to_parquet()
    consumer.close()

    # 5. Query verification
    manager = DuckDBManager()
    veh_count = manager.query("SELECT COUNT(*) as count FROM realtime.vehicle_events")["count"][0]
    ord_count = manager.query("SELECT COUNT(*) as count FROM realtime.order_events")["count"][0]
    dlq_count = manager.query("SELECT COUNT(*) as count FROM realtime.ingestion_errors")["count"][0]
    manager.close()

    print("\n" + "=" * 60)
    print("STREAMING SESSION VERIFICATION")
    print("=" * 60)
    print(f"[*] Realtime Vehicle Events in DB: {veh_count:,}")
    print(f"[*] Realtime Order Events in DB:   {ord_count:,}")
    print(f"[*] Dead-Letter Errors Logged:     {dlq_count:,}")
    print("=" * 60)
    logger.success("Real-time streaming simulation session completed successfully!")


if __name__ == "__main__":
    run_streaming_simulation()
