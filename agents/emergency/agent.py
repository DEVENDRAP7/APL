from agents.base_agent import BaseAgent
from agents.emergency.system_prompt import SYSTEM_PROMPT
from agents.emergency.tools import TOOLS, HANDLERS
from core.client import build_cached_system
from core.state_store import state_store
from data.models import SensorEvent, AgentResponse


class EmergencyResponseAgent(BaseAgent):
    name = "emergency_response"
    model = "claude-opus-4-7"
    max_tokens = 2048

    def __init__(self):
        super().__init__(tools=TOOLS, tool_handlers=HANDLERS)

    async def handle_incident(self, description: str, zone_id: str = None) -> AgentResponse:
        venue_state = state_store.get_state()
        dynamic = (
            f"\nCurrent venue mode: {venue_state.operational_mode}. "
            f"Alert level: {venue_state.overall_alert_level}. "
            f"Active incidents: {len(venue_state.active_incidents)}."
        )
        if zone_id:
            zone = state_store.get_zone(zone_id)
            if zone:
                dynamic += f" Incident zone '{zone_id}' occupancy: {zone.occupancy_pct:.0f}%."

        system = build_cached_system(SYSTEM_PROMPT, dynamic)
        messages = [{"role": "user", "content": description}]
        return await self.invoke(messages=messages, system=system)

    async def handle_sensor_alert(self, event: SensorEvent) -> AgentResponse:
        description = (
            f"SENSOR ALERT: {event.sensor_type} in zone '{event.zone_id}' "
            f"has reached {event.value} (severity: {event.severity}). "
            f"Assess the situation and recommend immediate actions."
        )
        return await self.handle_incident(description, zone_id=event.zone_id)
