from agents.base_agent import BaseAgent
from agents.attendee.system_prompt import SYSTEM_PROMPT
from agents.attendee.tools import TOOLS, HANDLERS
from core.client import build_cached_system
from core.state_store import state_store
from data.models import AttendeeSession, AgentResponse
import anthropic


class AttendeeExperienceAgent(BaseAgent):
    name = "attendee_experience"
    model = "claude-sonnet-4-6"
    max_tokens = 1024

    def __init__(self):
        super().__init__(tools=TOOLS, tool_handlers=HANDLERS)

    async def chat(self, session: AttendeeSession, user_message: str) -> AgentResponse:
        session.conversation_history.append({"role": "user", "content": user_message})

        venue_state = state_store.get_state()
        dynamic = f"\nVenue mode: {venue_state.operational_mode}. Overall alert: {venue_state.overall_alert_level}."

        system = build_cached_system(SYSTEM_PROMPT, dynamic)
        response = await self.invoke(
            messages=list(session.conversation_history),
            system=system,
        )

        session.conversation_history.append({
            "role": "assistant",
            "content": response.response_text
        })
        return response

    async def chat_stream(self, session: AttendeeSession, user_message: str):
        """Yields text chunks for WebSocket streaming."""
        session.conversation_history.append({"role": "user", "content": user_message})
        venue_state = state_store.get_state()
        dynamic = f"\nVenue mode: {venue_state.operational_mode}."
        system = build_cached_system(SYSTEM_PROMPT, dynamic)

        full_text = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            tools=self.tools,
            messages=list(session.conversation_history),
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                yield text

        session.conversation_history.append({
            "role": "assistant", "content": full_text
        })
