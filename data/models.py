from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Sensor / Ingestion ───────────────────────────────────────────────────────

class SensorEvent(BaseModel):
    event_id: str
    sensor_id: str
    zone_id: str
    sensor_type: Literal[
        "crowd_density", "queue_depth", "turnstile_count",
        "temperature", "co2", "parking_bay", "structural_load"
    ]
    value: float
    unit: str = ""
    severity: Literal["info", "warning", "critical"] = "info"
    threshold_breached: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CameraFrame(BaseModel):
    camera_id: str
    zone_id: str
    frame_b64: str          # base64-encoded JPEG
    anomaly_score: float    # 0.0–1.0 from CV service
    cv_flags: dict = {}     # headcount, flow_direction, density_level
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Venue State ──────────────────────────────────────────────────────────────

class ZoneState(BaseModel):
    zone_id: str
    name: str
    occupancy_pct: float = 0.0
    queue_depth: int = 0
    wait_time_minutes: float = 0.0
    alert_level: Literal["normal", "elevated", "critical", "emergency"] = "normal"
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class VenueState(BaseModel):
    venue_id: str
    operational_mode: Literal[
        "pre_event", "gates_open", "in_event", "post_event", "emergency", "evacuation"
    ] = "in_event"
    overall_alert_level: Literal["normal", "elevated", "critical", "emergency"] = "normal"
    zones: dict[str, ZoneState] = {}
    active_incidents: list[Incident] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Incidents ────────────────────────────────────────────────────────────────

class Incident(BaseModel):
    incident_id: str
    incident_type: Literal[
        "medical", "security", "crowd_crush", "fire", "infrastructure", "weather"
    ]
    severity: Literal["minor", "moderate", "major", "critical"]
    zone_id: str
    description: str
    responding_staff: list[str] = []
    external_services_notified: list[str] = []
    status: Literal["reported", "responding", "contained", "resolved"] = "reported"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


# ── Attendee ─────────────────────────────────────────────────────────────────

class SeatLocation(BaseModel):
    section: str
    row: str
    seat: str
    gate: str
    zone_id: str


class AttendeeSession(BaseModel):
    attendee_id: str
    ticket_id: str
    seat: Optional[SeatLocation] = None
    accessibility_needs: list[str] = []
    language: str = "en"
    conversation_history: list[dict] = []   # message format


# ── Agent I/O ────────────────────────────────────────────────────────────────

class AgentResponse(BaseModel):
    agent_name: str
    response_text: str
    tools_called: list[str] = []
    actions_taken: list[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Fix forward ref
VenueState.model_rebuild()
