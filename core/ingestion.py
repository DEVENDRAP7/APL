import yaml
from pathlib import Path
from data.models import SensorEvent
from core.state_store import state_store
from core.event_bus import event_bus


def _load_thresholds() -> dict:
    return yaml.safe_load(Path("config/thresholds.yaml").read_text())


_thresholds = _load_thresholds()


def _severity(sensor_type: str, value: float) -> tuple[str, bool]:
    rules = _thresholds.get(sensor_type, {})
    if not rules:
        return "info", False
    if value >= rules.get("emergency", float("inf")):
        return "critical", True
    if value >= rules.get("critical", float("inf")):
        return "critical", True
    if value >= rules.get("warning", float("inf")):
        return "warning", True
    return "info", False


async def ingest(event: SensorEvent) -> None:
    """Normalize, update state, threshold-check, publish to event bus."""
    sev, breached = _severity(event.sensor_type, event.value)
    event.severity = sev
    event.threshold_breached = breached

    # Update in-memory zone state
    zone = state_store.get_zone(event.zone_id)
    if zone:
        if event.sensor_type == "crowd_density":
            alert = "normal"
            if event.value >= _thresholds["crowd_density"]["emergency"]:
                alert = "emergency"
            elif event.value >= _thresholds["crowd_density"]["critical"]:
                alert = "critical"
            elif event.value >= _thresholds["crowd_density"]["warning"]:
                alert = "elevated"
            state_store.update_zone(event.zone_id, occupancy_pct=event.value * 100, alert_level=alert)

        elif event.sensor_type == "queue_depth":
            state_store.update_zone(event.zone_id, queue_depth=int(event.value))

    # Always publish to event bus
    topic = f"sensor.{event.sensor_type}"
    if breached:
        topic = f"alert.{sev}.{event.sensor_type}"
    await event_bus.publish(topic, event)
