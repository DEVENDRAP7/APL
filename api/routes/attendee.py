from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from agents.attendee.agent import AttendeeExperienceAgent
from data.models import AttendeeSession
import json

router = APIRouter(prefix="/ws", tags=["attendee"])
_agent = AttendeeExperienceAgent()
_sessions: dict[str, AttendeeSession] = {}


@router.websocket("/attendee/{attendee_id}")
async def attendee_chat(websocket: WebSocket, attendee_id: str):
    await websocket.accept()
    session = _sessions.setdefault(
        attendee_id,
        AttendeeSession(attendee_id=attendee_id, ticket_id=f"TKT-{attendee_id}")
    )
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(json.dumps({"type": "start"}))
            full = ""
            async for chunk in _agent.chat_stream(session, msg):
                full += chunk
                await websocket.send_text(json.dumps({"type": "delta", "text": chunk}))
            await websocket.send_text(json.dumps({"type": "done", "text": full}))
    except WebSocketDisconnect:
        _sessions.pop(attendee_id, None)
