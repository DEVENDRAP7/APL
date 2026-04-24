from fastapi import APIRouter
from data.models import SensorEvent, CameraFrame
from core.ingestion import ingest
from core.event_bus import event_bus

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/sensor")
async def receive_sensor_event(event: SensorEvent):
    await ingest(event)
    return {"status": "accepted", "event_id": event.event_id}


@router.post("/camera")
async def receive_camera_frame(frame: CameraFrame):
    if frame.anomaly_score >= 0.7:
        await event_bus.publish("alert.vision.anomaly", frame)
    return {"status": "accepted", "camera_id": frame.camera_id}
