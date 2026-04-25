from agents.base_agent import BaseAgent
from agents.emergency.tools import TOOLS, HANDLERS
from data.models import SensorEvent, AgentResponse


class EmergencyResponseAgent(BaseAgent):
    name = "emergency_response"
    model = "gemini-2.5-pro"
    max_tokens = 2048

    def __init__(self):
        super().__init__(tools=TOOLS, tool_handlers=HANDLERS)

    async def handle_incident(self, description: str, zone_id: str = None) -> AgentResponse:
        messages = [{"role": "user", "content": description}]
        return await self.invoke(messages=messages, system="")

    async def handle_sensor_alert(self, event: SensorEvent) -> AgentResponse:
        description = (
            f"SENSOR ALERT: {event.sensor_type} in zone '{event.zone_id}' "
            f"has reached {event.value} (severity: {event.severity})."
        )
        return await self.handle_incident(description, zone_id=event.zone_id)
