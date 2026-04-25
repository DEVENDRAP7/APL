from agents.base_agent import BaseAgent
from agents.attendee.tools import TOOLS, HANDLERS
from data.models import AttendeeSession, AgentResponse


class AttendeeExperienceAgent(BaseAgent):
    name = "attendee_experience"
    model = "gemini-2.5-flash"
    max_tokens = 1024

    def __init__(self):
        super().__init__(tools=TOOLS, tool_handlers=HANDLERS)

    async def chat(self, session: AttendeeSession, user_message: str) -> AgentResponse:
        session.conversation_history.append({"role": "user", "content": user_message})
        response = await self.invoke(
            messages=list(session.conversation_history),
            system="",
        )
        session.conversation_history.append({
            "role": "assistant",
            "content": response.response_text
        })
        return response

    async def chat_stream(self, session: AttendeeSession, user_message: str):
        session.conversation_history.append({"role": "user", "content": user_message})
        mock = (
            "I'm here to help! In demo mode I can tell you: Zone A is at 65% capacity, "
            "Gate 3 is your fastest entry, and food vendors on Level 2 have the shortest queues."
        )
        for word in mock.split(" "):
            yield word + " "
        session.conversation_history.append({"role": "assistant", "content": mock})
