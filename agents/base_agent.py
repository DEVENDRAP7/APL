from typing import Callable
from core.client import get_client
from data.models import AgentResponse


class BaseAgent:
    name: str = "base"
    model: str = "claude-sonnet-4-6"
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
        tools_called = []
        actions_taken = []

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                tools=self.tools if self.tools else [],
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                text = "".join(
                    b.text for b in response.content if hasattr(b, "text")
                )
                return AgentResponse(
                    agent_name=self.name,
                    response_text=text,
                    tools_called=tools_called,
                    actions_taken=actions_taken,
                )

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tools_called.append(block.name)
                        handler = self.tool_handlers.get(block.name)
                        if handler:
                            result = await handler(**block.input)
                            actions_taken.append(f"{block.name}({block.input})")
                        else:
                            result = {"error": f"No handler for {block.name}"}
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
                messages.append({"role": "user", "content": tool_results})
                continue

            break

        return AgentResponse(agent_name=self.name, response_text="")
