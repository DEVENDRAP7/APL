import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import events, attendee, ops
from core.event_bus import event_bus
from rules.engine import rule_engine
from agents.emergency.agent import EmergencyResponseAgent
from agents.vision_anomaly.agent import VisionAnomalyAgent
from scripts.simulate_realtime import run_simulator

_emergency_agent = EmergencyResponseAgent()
_vision_agent = VisionAnomalyAgent()


async def _on_alert(event_type: str, payload):
    if "critical" in event_type or "emergency" in event_type:
        print(f"\n[API] Critical alert — routing to EmergencyAgent: {event_type}")
        response = await _emergency_agent.handle_sensor_alert(payload)
        print(f"[EmergencyAgent] {response.response_text[:200]}")
    elif "vision.anomaly" in event_type:
        result = await _vision_agent.analyse(payload)
        print(f"[VisionAgent] {result}")
    else:
        await rule_engine.handle(event_type, payload)


@asynccontextmanager
async def lifespan(app: FastAPI):
    event_bus.subscribe_all(_on_alert)
    bus_task = asyncio.create_task(event_bus.run())
    sim_task = asyncio.create_task(run_simulator())
    yield
    bus_task.cancel()
    sim_task.cancel()


app = FastAPI(title="Venue Intelligence System", lifespan=lifespan)
app.include_router(events.router)
app.include_router(attendee.router)
app.include_router(ops.router)


@app.get("/")
async def root():
    return {"system": "Venue Intelligence System", "status": "running", "agents": 3}
