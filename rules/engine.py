"""
Rule-based decisions. No AI needed here.
Called by the event bus whenever a sensor alert fires.
"""
from data.models import SensorEvent
from core.state_store import state_store


class RuleEngine:

    async def handle(self, event_type: str, event: SensorEvent) -> list[str]:
        """Returns list of action strings taken."""
        actions = []

        if event.sensor_type == "crowd_density":
            actions += self._crowd_rules(event)
        elif event.sensor_type == "queue_depth":
            actions += self._queue_rules(event)
        elif event.sensor_type == "parking_bay":
            actions += self._parking_rules(event)

        for action in actions:
            print(f"[RuleEngine] {action}")
        return actions

    def _crowd_rules(self, event: SensorEvent) -> list[str]:
        actions = []
        zone = state_store.get_zone(event.zone_id)
        if not zone:
            return actions
        occ = event.value

        if occ >= 0.95:
            actions.append(f"EMERGENCY: Close entry to {event.zone_id} — {occ:.0%} capacity")
            actions.append(f"SIGNAGE: {event.zone_id} → 'Zone Full — Use Alternate Route'")
            actions.append(f"STAFF: Deploy 4 ushers to {event.zone_id} for crowd control")
        elif occ >= 0.85:
            actions.append(f"CRITICAL: Open auxiliary gate adjacent to {event.zone_id}")
            actions.append(f"SIGNAGE: {event.zone_id} → 'Busy — Consider Alternate Entrance'")
            actions.append(f"STAFF: Deploy 2 ushers to {event.zone_id}")
        elif occ >= 0.70:
            actions.append(f"WARNING: Monitor {event.zone_id} — {occ:.0%} capacity")
            actions.append(f"SIGNAGE: {event.zone_id} → 'Moderate Crowds — Allow Extra Time'")

        return actions

    def _queue_rules(self, event: SensorEvent) -> list[str]:
        actions = []
        depth = int(event.value)

        if depth >= 25:
            actions.append(f"EMERGENCY: Open overflow counter at {event.zone_id} — queue={depth}")
            actions.append(f"STAFF: Redeploy 3 staff to {event.zone_id} immediately")
            actions.append(f"NOTIFY: Push alert to nearby attendees — suggest {event.zone_id} alternate")
        elif depth >= 15:
            actions.append(f"CRITICAL: Redeploy 2 staff to {event.zone_id} — queue={depth}")
            actions.append(f"DISPLAY: Update wait board at {event.zone_id} → '{depth * 1} min wait'")
        elif depth >= 8:
            actions.append(f"WARNING: Monitor {event.zone_id} queue — {depth} people waiting")

        return actions

    def _parking_rules(self, event: SensorEvent) -> list[str]:
        actions = []
        fill = event.value

        if fill >= 0.90:
            actions.append(f"CRITICAL: Open overflow lot for {event.zone_id}")
            actions.append(f"SIGNAGE: Redirect traffic away from {event.zone_id}")
            actions.append(f"TRANSIT: Dispatch 2 extra shuttle buses")
        elif fill >= 0.75:
            actions.append(f"WARNING: {event.zone_id} at {fill:.0%} — alert attendees of limited parking")

        return actions


# Singleton
rule_engine = RuleEngine()
