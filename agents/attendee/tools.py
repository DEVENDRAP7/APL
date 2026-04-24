from core.state_store import state_store

TOOLS = [
    {
        "name": "lookup_seat",
        "description": "Look up seat location and walking directions from a gate or zone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "from_zone": {"type": "string", "description": "Current zone or gate of the attendee"}
            },
            "required": ["ticket_id"]
        }
    },
    {
        "name": "get_queue_wait",
        "description": "Get live queue wait time at a concession stand or restroom.",
        "input_schema": {
            "type": "object",
            "properties": {
                "zone_id": {"type": "string", "description": "Zone ID of the concession or restroom"}
            },
            "required": ["zone_id"]
        }
    },
    {
        "name": "find_nearest_amenity",
        "description": "Find the nearest amenity (restroom, food, ATM, first_aid) to the attendee's current location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amenity_type": {"type": "string", "enum": ["restroom", "food", "atm", "first_aid"]},
                "near_zone": {"type": "string"}
            },
            "required": ["amenity_type", "near_zone"]
        }
    },
    {
        "name": "place_food_order",
        "description": "Place a food/drink order for delivery or pickup at a concession stand.",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
                "delivery_zone": {"type": "string"},
                "stand_id": {"type": "string"}
            },
            "required": ["items", "delivery_zone"]
        }
    },
    {
        "name": "request_accessibility_help",
        "description": "Request wheelchair assistance or accessibility support for an attendee.",
        "input_schema": {
            "type": "object",
            "properties": {
                "zone_id": {"type": "string"},
                "need": {"type": "string", "description": "Describe the accessibility need"}
            },
            "required": ["zone_id", "need"]
        }
    },
]


# ── Tool handlers ────────────────────────────────────────────────────────────

async def lookup_seat(ticket_id: str, from_zone: str = "gate_north") -> dict:
    return {
        "seat": {"section": "110", "row": "G", "seat": "14", "gate": "Gate North"},
        "directions": f"From {from_zone}: Follow blue signs → Section 110 → Row G. ~3 min walk.",
        "accessible_route": "Elevator near Gate North → Level 2 → Section 110 wheelchair bay"
    }


async def get_queue_wait(zone_id: str) -> dict:
    zone = state_store.get_zone(zone_id)
    if zone:
        wait = zone.wait_time_minutes or zone.queue_depth * 0.8
        return {"zone": zone.name, "wait_minutes": round(wait, 1), "queue_depth": zone.queue_depth}
    return {"error": f"Zone {zone_id} not found"}


async def find_nearest_amenity(amenity_type: str, near_zone: str) -> dict:
    amenity_map = {
        "restroom": {"zone_id": "restroom_a", "name": "Restroom Block A", "walk_minutes": 2},
        "food":     {"zone_id": "food_north",  "name": "Food Court North",  "walk_minutes": 3},
        "atm":      {"zone_id": "gate_north",  "name": "ATM near Gate North", "walk_minutes": 4},
        "first_aid":{"zone_id": "first_aid",   "name": "First Aid Station",  "walk_minutes": 5},
    }
    result = amenity_map.get(amenity_type, {"error": "Unknown amenity type"})
    if "zone_id" in result:
        zone = state_store.get_zone(result["zone_id"])
        if zone:
            result["current_wait_minutes"] = round(zone.queue_depth * 0.8, 1)
    return result


async def place_food_order(items: list, delivery_zone: str, stand_id: str = "food_north") -> dict:
    import uuid
    return {
        "order_id": str(uuid.uuid4())[:8].upper(),
        "items": items,
        "stand": stand_id,
        "delivery_zone": delivery_zone,
        "estimated_ready_minutes": 8,
        "status": "confirmed"
    }


async def request_accessibility_help(zone_id: str, need: str) -> dict:
    return {
        "request_id": "ACC-001",
        "status": "dispatched",
        "message": f"Accessibility staff notified at {zone_id}. ETA 3–5 minutes.",
        "need": need
    }


HANDLERS = {
    "lookup_seat": lookup_seat,
    "get_queue_wait": get_queue_wait,
    "find_nearest_amenity": find_nearest_amenity,
    "place_food_order": place_food_order,
    "request_accessibility_help": request_accessibility_help,
}
