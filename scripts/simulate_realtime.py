"""
Simulates a live venue sensor feed.
Publishes SensorEvents to the ingestion pipeline every 2 seconds.
Cycles through 4 scenarios: normal → crowd_surge → queue_buildup → post_game_exit
"""
import asyncio
import random
import uuid
from datetime import datetime
from data.models import SensorEvent
from core.ingestion import ingest

SCENARIOS = [
    # (scenario_name, zone_densities, queue_depths)
    ("normal",        {"gate_north": 0.45, "concourse_north": 0.50, "concourse_south": 0.48, "parking_a": 0.60}, {"food_north": 4, "food_south": 3, "restroom_a": 2}),
    ("crowd_surge",   {"gate_north": 0.88, "concourse_north": 0.91, "concourse_south": 0.72, "parking_a": 0.85}, {"food_north": 18, "food_south": 12, "restroom_a": 9}),
    ("queue_buildup", {"gate_north": 0.65, "concourse_north": 0.70, "concourse_south": 0.68, "parking_a": 0.75}, {"food_north": 22, "food_south": 26, "restroom_a": 14}),
    ("post_game_exit",{"gate_north": 0.92, "concourse_north": 0.89, "concourse_south": 0.94, "parking_a": 0.97}, {"food_north": 3,  "food_south": 2,  "restroom_a": 5}),
]

_scenario_idx = 0
_tick = 0
_SCENARIO_DURATION = 30  # ticks per scenario (~60s at 2s interval)


async def emit_sensor_events() -> None:
    global _scenario_idx, _tick

    name, densities, queues = SCENARIOS[_scenario_idx]

    # Crowd density events
    for zone_id, base_density in densities.items():
        jitter = random.uniform(-0.03, 0.03)
        value = max(0.0, min(1.0, base_density + jitter))
        await ingest(SensorEvent(
            event_id=str(uuid.uuid4()),
            sensor_id=f"sensor-density-{zone_id}",
            zone_id=zone_id,
            sensor_type="crowd_density",
            value=round(value, 3),
            unit="ratio",
        ))

    # Queue depth events
    for zone_id, base_depth in queues.items():
        jitter = random.randint(-2, 2)
        value = max(0, base_depth + jitter)
        await ingest(SensorEvent(
            event_id=str(uuid.uuid4()),
            sensor_id=f"sensor-queue-{zone_id}",
            zone_id=zone_id,
            sensor_type="queue_depth",
            value=float(value),
            unit="people",
        ))

    _tick += 1
    if _tick >= _SCENARIO_DURATION:
        _tick = 0
        _scenario_idx = (_scenario_idx + 1) % len(SCENARIOS)
        print(f"[Simulator] Scenario → {SCENARIOS[_scenario_idx][0]}")


async def run_simulator() -> None:
    print("[Simulator] Starting real-time venue sensor feed (2s interval)...")
    while True:
        await emit_sensor_events()
        await asyncio.sleep(2)
