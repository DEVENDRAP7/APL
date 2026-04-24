import json
from datetime import datetime
from pathlib import Path
from data.models import VenueState, ZoneState


class StateStore:
    """In-memory venue state. Drop-in replace with Redis later."""

    def __init__(self):
        self._state: VenueState = self._load_initial_state()

    def _load_initial_state(self) -> VenueState:
        layout_path = Path("config/venue_layout.json")
        layout = json.loads(layout_path.read_text())
        zones = {
            zone_id: ZoneState(zone_id=zone_id, name=info["name"])
            for zone_id, info in layout["zones"].items()
        }
        return VenueState(venue_id=layout["venue_id"], zones=zones)

    def get_state(self) -> VenueState:
        return self._state

    def get_zone(self, zone_id: str) -> ZoneState | None:
        return self._state.zones.get(zone_id)

    def update_zone(self, zone_id: str, **kwargs) -> None:
        if zone_id in self._state.zones:
            zone = self._state.zones[zone_id]
            for k, v in kwargs.items():
                setattr(zone, k, v)
            zone.last_updated = datetime.utcnow()
            self._state.timestamp = datetime.utcnow()

    def set_mode(self, mode: str) -> None:
        self._state.operational_mode = mode
        self._state.timestamp = datetime.utcnow()

    def add_incident(self, incident) -> None:
        self._state.active_incidents.append(incident)
        self._state.timestamp = datetime.utcnow()

    def resolve_incident(self, incident_id: str) -> None:
        for inc in self._state.active_incidents:
            if inc.incident_id == incident_id:
                inc.status = "resolved"
                inc.resolved_at = datetime.utcnow()


# Singleton
state_store = StateStore()
