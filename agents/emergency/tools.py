from core.state_store import state_store
import uuid

TOOLS = [
    {
        "name": "get_venue_state",
        "description": "Get current venue state including all zone occupancy and active incidents.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_evacuation_routes",
        "description": "Get current status and capacity of all emergency exits and evacuation routes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "zone_id": {"type": "string", "description": "Optionally filter to exits near a specific zone"}
            }
        }
    },
    {
        "name": "activate_pa_announcement",
        "description": "Broadcast a PA announcement to specified zones or the entire venue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "zones": {"type": "array", "items": {"type": "string"}, "description": "Use ['all'] for venue-wide"},
                "tone": {"type": "string", "enum": ["informational", "urgent", "emergency"]}
            },
            "required": ["message", "zones", "tone"]
        }
    },
    {
        "name": "contact_emergency_services",
        "description": "Contact external emergency services (EMS, police, fire).",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "enum": ["ems", "police", "fire"]},
                "incident_type": {"type": "string"},
                "location": {"type": "string"},
                "priority": {"type": "string", "enum": ["immediate", "urgent", "non_urgent"]}
            },
            "required": ["service", "incident_type", "location", "priority"]
        }
    },
    {
        "name": "trigger_zone_evacuation",
        "description": "Initiate evacuation of one or more zones. Check evacuation routes first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "zones": {"type": "array", "items": {"type": "string"}},
                "primary_exit": {"type": "string"},
                "reason": {"type": "string"}
            },
            "required": ["zones", "primary_exit", "reason"]
        }
    },
    {
        "name": "dispatch_medical_team",
        "description": "Dispatch a medical team and AED to a specific zone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "zone_id": {"type": "string"},
                "incident_description": {"type": "string"}
            },
            "required": ["zone_id", "incident_description"]
        }
    },
]


# ── Handlers ─────────────────────────────────────────────────────────────────

async def get_venue_state() -> dict:
    state = state_store.get_state()
    return {
        "mode": state.operational_mode,
        "alert_level": state.overall_alert_level,
        "zones": {
            zid: {"occupancy_pct": z.occupancy_pct, "alert_level": z.alert_level}
            for zid, z in state.zones.items()
        },
        "active_incidents": len(state.active_incidents),
    }


async def get_evacuation_routes(zone_id: str = None) -> dict:
    routes = {
        "gate_north": {"status": "clear", "capacity": 5000, "estimated_clear_time_min": 8},
        "gate_south": {"status": "clear", "capacity": 5000, "estimated_clear_time_min": 9},
        "gate_east":  {"status": "clear", "capacity": 3000, "estimated_clear_time_min": 6},
        "gate_west":  {"status": "clear", "capacity": 3000, "estimated_clear_time_min": 6},
    }
    if zone_id:
        return {k: v for k, v in routes.items() if "north" in k or "south" in k}
    return routes


async def activate_pa_announcement(message: str, zones: list, tone: str) -> dict:
    print(f"\n[PA SYSTEM — {tone.upper()}] Zones: {zones}\n  '{message}'\n")
    return {"status": "broadcast", "zones": zones, "tone": tone, "message": message}


async def contact_emergency_services(service: str, incident_type: str, location: str, priority: str) -> dict:
    print(f"[EMERGENCY SERVICES] Contacting {service.upper()} — {priority} — {incident_type} at {location}")
    return {"status": "notified", "service": service, "eta_minutes": 6 if priority == "immediate" else 12}


async def trigger_zone_evacuation(zones: list, primary_exit: str, reason: str) -> dict:
    print(f"[EVACUATION] Zones: {zones} → Exit: {primary_exit} | Reason: {reason}")
    return {"status": "initiated", "zones": zones, "primary_exit": primary_exit}


async def dispatch_medical_team(zone_id: str, incident_description: str) -> dict:
    print(f"[MEDICAL] Dispatching team to {zone_id}: {incident_description}")
    return {"status": "dispatched", "zone": zone_id, "eta_minutes": 3, "aed_included": True}


HANDLERS = {
    "get_venue_state": get_venue_state,
    "get_evacuation_routes": get_evacuation_routes,
    "activate_pa_announcement": activate_pa_announcement,
    "contact_emergency_services": contact_emergency_services,
    "trigger_zone_evacuation": trigger_zone_evacuation,
    "dispatch_medical_team": dispatch_medical_team,
}
