from typing import Callable
from core.client import get_client
from data.models import AgentResponse

_MOCK_RESPONSES = {
    "attendee_experience": (
        "Welcome to the venue! Zone A and B have moderate crowd density right now. "
        "I recommend using Gate 3 for the quickest entry. Food stalls on Level 2 have shorter queues. "
        "Enjoy the event!"
    ),
    "emergency_response": (
        "Situation assessed. Recommend standard crowd flow protocol: activate secondary exits, "
        "deploy stewards to Zone C, monitor density sensors. No immediate evacuation required."
    ),
}


class BaseAgent:
    name: str = "base"
    model: str = "antigravity-fast"
    max_tokens: int = 1024

    def __init__(self, tools: list[dict], tool_handlers: dict[str, Callable]):
        self.client = get_client()
        self.tools = tools
        self.tool_handlers = tool_handlers

    async def invoke(
        self,
        messages: list[dict],
        system: list[dict] | str,
    ) -> AgentResponse:
        return AgentResponse(
            agent_name=self.name,
            response_text=_MOCK_RESPONSES.get(
                self.name,
                "System operating in demo mode.",
            ),
            tools_called=[],
            actions_taken=[],
        )
